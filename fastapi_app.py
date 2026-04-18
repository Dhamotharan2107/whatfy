from fastapi import FastAPI, Request, Form, Body, UploadFile, File, BackgroundTasks
from fastapi.responses import RedirectResponse, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, Dict, Any
import sqlite3, hashlib, secrets, json, time, io, base64, threading, os, random
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from pathlib import Path
from datetime import datetime
import uvicorn

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_OK = True
except ImportError:
    PIL_OK = False

try:
    from openai import OpenAI as _OpenAI
    _ai = _OpenAI(
        api_key="4ed473e121c7480186f26d81a0464b41.O4F2MZtdY4xah84r",
        base_url="https://open.bigmodel.cn/api/paas/v4/",
        timeout=60.0,
    )
    AI_OK = True
except ImportError:
    AI_OK = False

# Per-sender last-reply timestamp — enforce minimum gap between AI replies
_sender_last: dict = {}
_sender_lock = threading.Lock()
_SENDER_MIN_GAP = 3.0  # seconds between replies per sender

def _is_network_err(e: Exception) -> bool:
    cls = type(e).__name__
    msg = str(e).lower()
    return any(k in cls+msg for k in ("connect","getaddrinfo","network","timeout","apiconnection"))

def _ai_call(messages: list, max_tokens: int = 400) -> str:
    """Call GLM with retry on 429 rate-limit (up to 3 attempts)."""
    for attempt in range(3):
        try:
            resp = _ai.chat.completions.create(
                model="glm-4.7-flash", messages=messages, max_tokens=max_tokens
            )
            return resp.choices[0].message.content
        except Exception as e:
            status = getattr(getattr(e, "response", None), "status_code", None)
            # openai SDK wraps HTTP errors; check for 429
            if status == 429 or "1302" in str(e) or "rate" in str(e).lower():
                wait = 4 ** attempt  # 1s, 4s, 16s
                print(f"[AI] 429 rate-limit, waiting {wait}s (attempt {attempt+1}/3)")
                time.sleep(wait)
                continue
            if "timed out" in str(e).lower() or "timeout" in str(e).lower():
                wait = 4 ** attempt
                print(f"[AI] timeout, retrying in {wait}s (attempt {attempt+1}/3)")
                time.sleep(wait)
                continue
            if _is_network_err(e):
                raise
            raise
    raise Exception("Rate limit — too many requests. Please wait a moment and try again.")

try:
    import qrcode as _qrlib
    QR_OK = True
except ImportError:
    QR_OK = False

app = FastAPI(title="Whatfy")
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
DB_PATH  = BASE_DIR / "platform.db"
API_BASE = os.environ.get("GO_SERVER_URL", "http://localhost:8080")

# ── Email config ──────────────────────────────────────────────────────────────
SMTP_HOST  = os.environ.get("SMTP_HOST",  "smtp.zoho.in")
SMTP_PORT  = int(os.environ.get("SMTP_PORT", "465"))   # 465=SSL, 587=STARTTLS
SMTP_USER  = os.environ.get("SMTP_USER",  "info@opendrap.website")
SMTP_PASS  = os.environ.get("SMTP_PASS",  "h0LBrxNA4u4G")
FROM_EMAIL = os.environ.get("FROM_EMAIL", "info@opendrap.website")
APP_URL    = os.environ.get("APP_URL",    "http://whatfy.opendrap.website")

# token -> {uid, wa_verified, code, code_sent}
_sessions: dict = {}

# ── DB ────────────────────────────────────────────────────────────────────────

def _db():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c

def _init():
    db = _db()
    db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id                 INTEGER PRIMARY KEY AUTOINCREMENT,
            email              TEXT UNIQUE NOT NULL,
            password_hash      TEXT NOT NULL,
            name               TEXT DEFAULT '',
            email_verified     INTEGER DEFAULT 0,
            verification_token TEXT DEFAULT '',
            created_at         INTEGER DEFAULT (strftime('%s','now'))
        );
        CREATE TABLE IF NOT EXISTS grocery (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            name       TEXT NOT NULL,
            qty        REAL DEFAULT 0,
            unit       TEXT DEFAULT 'kg',
            low_thresh REAL DEFAULT 5,
            price      REAL DEFAULT 0,
            ordered    INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS invoices (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            inv_no     TEXT NOT NULL,
            cust_name  TEXT NOT NULL,
            cust_phone TEXT NOT NULL,
            items      TEXT DEFAULT '[]',
            total      REAL DEFAULT 0,
            status     TEXT DEFAULT 'draft',
            created_at INTEGER DEFAULT (strftime('%s','now')),
            sent_at    INTEGER DEFAULT NULL
        );
        CREATE TABLE IF NOT EXISTS shop_profile (
            user_id      INTEGER PRIMARY KEY,
            shop_name    TEXT DEFAULT '',
            shop_phone   TEXT DEFAULT '',
            shop_address TEXT DEFAULT '',
            shop_email   TEXT DEFAULT '',
            logo_data    TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS patients (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            name        TEXT NOT NULL,
            phone       TEXT NOT NULL,
            age         INTEGER DEFAULT 0,
            condition   TEXT DEFAULT '',
            medications TEXT DEFAULT '[]'
        );
        CREATE TABLE IF NOT EXISTS appointments (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id       INTEGER NOT NULL,
            patient_name  TEXT NOT NULL,
            patient_phone TEXT NOT NULL,
            doctor        TEXT DEFAULT '',
            appt_type     TEXT DEFAULT 'General',
            appt_date     TEXT NOT NULL,
            appt_time     TEXT NOT NULL,
            status        TEXT DEFAULT 'scheduled',
            notes         TEXT DEFAULT '',
            created_at    INTEGER DEFAULT (strftime('%s','now'))
        );
        CREATE TABLE IF NOT EXISTS agent_cfg (
            user_id   INTEGER NOT NULL,
            agent     TEXT NOT NULL,
            enabled   INTEGER DEFAULT 0,
            wa_number TEXT DEFAULT '',
            notes     TEXT DEFAULT '',
            PRIMARY KEY (user_id, agent)
        );
        CREATE TABLE IF NOT EXISTS sessions (
            token       TEXT PRIMARY KEY,
            uid         INTEGER NOT NULL,
            wa_verified INTEGER DEFAULT 0,
            created_at  INTEGER DEFAULT (strftime('%s','now'))
        );
        CREATE TABLE IF NOT EXISTS conversations (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            sender     TEXT NOT NULL,
            role       TEXT NOT NULL,
            content    TEXT NOT NULL,
            created_at INTEGER DEFAULT (strftime('%s','now'))
        );
        CREATE INDEX IF NOT EXISTS idx_conv_sender ON conversations(sender, created_at);
        CREATE TABLE IF NOT EXISTS campaigns (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            name        TEXT NOT NULL,
            message     TEXT NOT NULL,
            delay_secs  INTEGER DEFAULT 20,
            status      TEXT DEFAULT 'draft',
            total       INTEGER DEFAULT 0,
            sent        INTEGER DEFAULT 0,
            failed      INTEGER DEFAULT 0,
            created_at  INTEGER DEFAULT (strftime('%s','now')),
            started_at  INTEGER DEFAULT NULL,
            finished_at INTEGER DEFAULT NULL
        );
        CREATE TABLE IF NOT EXISTS campaign_contacts (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_id INTEGER NOT NULL,
            name        TEXT DEFAULT '',
            phone       TEXT NOT NULL,
            status      TEXT DEFAULT 'pending',
            sent_at     INTEGER DEFAULT NULL,
            error       TEXT DEFAULT ''
        );
        CREATE INDEX IF NOT EXISTS idx_cc_campaign ON campaign_contacts(campaign_id, status);
        CREATE INDEX IF NOT EXISTS idx_invoices_user ON invoices(user_id, created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_grocery_user ON grocery(user_id);
        CREATE INDEX IF NOT EXISTS idx_grocery_low ON grocery(user_id, qty, low_thresh, ordered);
        CREATE INDEX IF NOT EXISTS idx_patients_user ON patients(user_id);
        CREATE INDEX IF NOT EXISTS idx_appts_user ON appointments(user_id, appt_date);
        CREATE INDEX IF NOT EXISTS idx_appts_status ON appointments(user_id, status, appt_date);
        CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(user_id, status);
        CREATE INDEX IF NOT EXISTS idx_agent_cfg_user ON agent_cfg(user_id);
        CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(token);
    """)
    db.close()

_init()

# Migrate existing DB — add columns/tables if missing
def _migrate():
    db = _db()
    for stmt in [
        "ALTER TABLE users ADD COLUMN email_verified INTEGER DEFAULT 0",
        "ALTER TABLE users ADD COLUMN verification_token TEXT DEFAULT ''",
        # shop_profile table (added later — create if missing)
        """CREATE TABLE IF NOT EXISTS shop_profile (
            user_id      INTEGER PRIMARY KEY,
            shop_name    TEXT DEFAULT '',
            shop_phone   TEXT DEFAULT '',
            shop_address TEXT DEFAULT '',
            shop_email   TEXT DEFAULT '',
            logo_data    TEXT DEFAULT ''
        )""",
    ]:
        try: db.execute(stmt)
        except: pass
    db.commit()
    db.close()

_migrate()

# ── Campaign runtime ──────────────────────────────────────────────────────────
_campaign_threads: dict = {}   # cid -> Thread
_campaign_stop:    dict = {}   # cid -> bool  (True = stop requested)
_campaign_lock = threading.Lock()

def _parse_contacts(raw: str) -> list:
    """Parse contacts from textarea.
    Formats supported per line:
      name,phone   /   phone   /   +91xxxxxxxxxx
    Lines starting with # are ignored.
    """
    out = []
    for line in raw.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split(",")]
        if len(parts) >= 2:
            name, phone = parts[0], parts[1]
        else:
            name, phone = "", parts[0]
        phone = phone.replace(" ", "").replace("-", "").replace("+", "").replace("(", "").replace(")", "")
        if not phone.isdigit() or len(phone) < 7:
            continue
        out.append({"name": name, "phone": phone})
    return out

def _campaign_run(cid: int):
    """Background worker — sends one message every delay_secs seconds."""
    db = _db()
    try:
        db.execute("UPDATE campaigns SET status='running', started_at=? WHERE id=?",
                   (int(time.time()), cid))
        db.commit()

        while True:
            # Check stop flag
            if _campaign_stop.get(cid):
                db.execute("UPDATE campaigns SET status='paused' WHERE id=?", (cid,))
                db.commit()
                break

            # Fetch next pending contact
            row = db.execute(
                "SELECT * FROM campaign_contacts WHERE campaign_id=? AND status='pending' ORDER BY id LIMIT 1",
                (cid,)).fetchone()

            if not row:
                db.execute("UPDATE campaigns SET status='completed', finished_at=? WHERE id=?",
                           (int(time.time()), cid))
                db.commit()
                break

            row  = dict(row)
            camp = db.execute("SELECT message, delay_secs FROM campaigns WHERE id=?", (cid,)).fetchone()
            if not camp:
                break

            msg   = camp["message"]
            delay = random.randint(20, 60)   # random 20–60s — reduces spam detection
            name  = (row.get("name") or "").strip()
            if name:
                msg = msg.replace("{{name}}", name).replace("{name}", name)

            # Send
            try:
                result = _send_wa(row["phone"], msg)
                if result.get("error"):
                    db.execute(
                        "UPDATE campaign_contacts SET status='failed', error=?, sent_at=? WHERE id=?",
                        (str(result["error"])[:255], int(time.time()), row["id"]))
                    db.execute("UPDATE campaigns SET failed=failed+1 WHERE id=?", (cid,))
                else:
                    db.execute(
                        "UPDATE campaign_contacts SET status='sent', sent_at=? WHERE id=?",
                        (int(time.time()), row["id"]))
                    db.execute("UPDATE campaigns SET sent=sent+1 WHERE id=?", (cid,))
            except Exception as e:
                db.execute(
                    "UPDATE campaign_contacts SET status='failed', error=?, sent_at=? WHERE id=?",
                    (str(e)[:255], int(time.time()), row["id"]))
                db.execute("UPDATE campaigns SET failed=failed+1 WHERE id=?", (cid,))
            db.commit()

            # Interruptible sleep — check stop flag every second
            for _ in range(delay):
                if _campaign_stop.get(cid):
                    break
                time.sleep(1)

    except Exception as e:
        print(f"[CAMPAIGN {cid}] Error: {e}")
        try:
            db.execute("UPDATE campaigns SET status='failed' WHERE id=?", (cid,))
            db.commit()
        except Exception:
            pass
    finally:
        db.close()
        with _campaign_lock:
            _campaign_threads.pop(cid, None)
            _campaign_stop.pop(cid, None)

# ── Email ─────────────────────────────────────────────────────────────────────

def _build_msg(to_email: str, subject: str, html_body: str):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"Whatfy | Opendrap <{FROM_EMAIL}>"
    msg["To"]      = to_email
    msg.attach(MIMEText(html_body, "html"))
    return msg

def _send_email(to_email: str, subject: str, html_body: str) -> bool:
    if not SMTP_USER or not SMTP_PASS:
        print(f"[EMAIL] SMTP not configured — skipping email to {to_email}")
        return False

    msg = _build_msg(to_email, subject, html_body)
    raw = msg.as_string()

    # Try all Zoho-compatible connection methods in order
    attempts = [
        ("SSL-465",     lambda: _try_ssl(SMTP_HOST,      465, to_email, raw)),
        ("SSL-465-IN",  lambda: _try_ssl("smtp.zoho.in", 465, to_email, raw)),
        ("TLS-587",     lambda: _try_tls(SMTP_HOST,      587, to_email, raw)),
        ("TLS-587-IN",  lambda: _try_tls("smtp.zoho.in", 587, to_email, raw)),
    ]

    last_err = None
    for label, fn in attempts:
        try:
            print(f"[EMAIL] Trying {label} …")
            fn()
            print(f"[EMAIL] ✓ Sent via {label} → {to_email}")
            return True
        except smtplib.SMTPAuthenticationError as e:
            last_err = e
            print(f"[EMAIL] {label} — Auth failed: {e}")
            break            # wrong password — no point trying other ports/hosts
        except Exception as e:
            last_err = e
            print(f"[EMAIL] {label} — {type(e).__name__}: {e}")
            continue

    print(f"[EMAIL] All attempts failed. Last error: {last_err}")
    print("[EMAIL] ACTION REQUIRED: accounts.zoho.com → Security → App Passwords → generate one and update SMTP_PASS")
    return False

def _try_ssl(host: str, port: int, to_email: str, raw: str):
    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL(host, port, context=ctx, timeout=10) as s:
        s.ehlo()
        s.login(SMTP_USER, SMTP_PASS)
        s.sendmail(FROM_EMAIL, to_email, raw)

def _try_tls(host: str, port: int, to_email: str, raw: str):
    ctx = ssl.create_default_context()
    with smtplib.SMTP(host, port, timeout=10) as s:
        s.ehlo()
        s.starttls(context=ctx)
        s.ehlo()
        s.login(SMTP_USER, SMTP_PASS)
        s.sendmail(FROM_EMAIL, to_email, raw)

def _send_verification_email(name: str, to_email: str, token: str):
    link = f"{APP_URL}/auth/verify-email/{token}"
    html = f"""
    <!DOCTYPE html><html><body style="font-family:-apple-system,sans-serif;background:#f1f5f9;padding:40px 0">
    <div style="max-width:520px;margin:0 auto;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,.08)">
      <div style="background:linear-gradient(135deg,#0f172a,#0d2f1e);padding:36px 36px 28px;text-align:center">
        <div style="width:56px;height:56px;background:linear-gradient(135deg,#25D366,#128C7E);border-radius:14px;display:inline-flex;align-items:center;justify-content:center;font-size:28px;margin-bottom:16px">💬</div>
        <h1 style="color:#fff;font-size:22px;margin:0;font-weight:800">Verify your email</h1>
        <p style="color:rgba(255,255,255,.55);margin:8px 0 0;font-size:14px">One more step to activate your Whatfy account</p>
      </div>
      <div style="padding:36px">
        <p style="color:#374151;font-size:15px;margin-bottom:24px">Hi <strong>{name}</strong>,</p>
        <p style="color:#6b7280;font-size:14px;line-height:1.6;margin-bottom:28px">
          Thanks for signing up! Click the button below to verify your email address and start using Whatfy.
        </p>
        <div style="text-align:center;margin-bottom:28px">
          <a href="{link}" style="display:inline-block;background:linear-gradient(135deg,#25D366,#128C7E);color:#fff;text-decoration:none;padding:14px 36px;border-radius:10px;font-weight:700;font-size:15px">
            ✓ Verify Email Address
          </a>
        </div>
        <p style="color:#9ca3af;font-size:12px;text-align:center;line-height:1.6">
          Or copy this link:<br>
          <a href="{link}" style="color:#25D366;word-break:break-all">{link}</a>
        </p>
        <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0">
        <p style="color:#9ca3af;font-size:12px;text-align:center">
          This link expires in 24 hours. If you didn't create an account, you can safely ignore this email.
        </p>
      </div>
    </div>
    </body></html>
    """
    _send_email(to_email, "Verify your Whatfy account", html)

# ── Helpers ───────────────────────────────────────────────────────────────────

def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def _session(req: Request) -> Optional[dict]:
    t = req.cookies.get("st")
    if not t:
        return None
    # Fast path: already in memory
    if t in _sessions:
        return _sessions[t]
    # Fallback: load from DB (handles server restarts)
    db = _db()
    row = db.execute("SELECT * FROM sessions WHERE token=?", (t,)).fetchone()
    db.close()
    if row:
        s = {"uid": row["uid"], "wa_verified": bool(row["wa_verified"]),
             "code": None, "code_sent": None}
        _sessions[t] = s   # cache in memory
        return s
    return None

def _uid(req: Request) -> Optional[int]:
    s = _session(req); return s["uid"] if s else None

def _verified(req: Request) -> bool:
    s = _session(req); return bool(s and s.get("wa_verified"))

def _session_save(token: str, uid: int, wa_verified: bool = False):
    """Persist session to DB and memory."""
    s = {"uid": uid, "wa_verified": wa_verified, "code": None, "code_sent": None}
    _sessions[token] = s
    db = _db()
    db.execute("INSERT OR REPLACE INTO sessions (token,uid,wa_verified) VALUES (?,?,?)",
               (token, uid, 1 if wa_verified else 0))
    db.commit()
    db.close()
    return s

def _session_set_verified(req: Request):
    """Mark the current session as WA-verified in memory + DB."""
    t = req.cookies.get("st")
    s = _session(req)
    if s:
        s["wa_verified"] = True
    if t:
        db = _db()
        db.execute("UPDATE sessions SET wa_verified=1 WHERE token=?", (t,))
        db.commit()
        db.close()

def _session_delete(token: str):
    """Remove session from memory and DB."""
    _sessions.pop(token, None)
    db = _db()
    db.execute("DELETE FROM sessions WHERE token=?", (token,))
    db.commit()
    db.close()

def _auth():    return RedirectResponse("/auth",     status_code=302)
def _connect(): return RedirectResponse("/connect",  status_code=302)
def _verify():  return RedirectResponse("/verify",   status_code=302)
def _home():    return RedirectResponse("/dashboard", status_code=302)

_wa_cache: dict = {"connected": False, "phone": ""}

def _wa_status():
    """Instant read — always returns cached value, never blocks."""
    return _wa_cache["connected"], _wa_cache["phone"]

def _wa_poll():
    """Background thread: refreshes WA status every 20 s."""
    while True:
        try:
            r = requests.get(f"{API_BASE}/status", timeout=3)
            s = r.json()
            connected = bool(s.get("connected") and s.get("loggedIn"))
            phone = ""
            if connected:
                try:
                    u = requests.get(f"{API_BASE}/user", timeout=3).json()
                    phone = u.get("phone", "")
                except Exception:
                    pass
            _wa_cache.update({"connected": connected, "phone": phone})
        except Exception:
            _wa_cache.update({"connected": False, "phone": ""})
        time.sleep(20)

# Start background WA poller once
threading.Thread(target=_wa_poll, daemon=True).start()

def _send_wa(number: str, msg: str):
    return requests.post(f"{API_BASE}/send",
                         json={"number": number, "message": msg}, timeout=15).json()

# ── AI helpers ────────────────────────────────────────────────────────────────

def _ai_chat(prompt: str, system: str = "") -> str:
    if not AI_OK: return "AI unavailable."
    try:
        msgs = []
        if system: msgs.append({"role": "system", "content": system})
        msgs.append({"role": "user", "content": prompt})
        return _ai_call(msgs)
    except Exception as e:
        if _is_network_err(e):
            return "⚠️ Cannot reach AI service — check your internet connection and try again."
        return f"⚠️ AI error: {e}"

def _ai_vision(image_b64: str, prompt: str) -> str:
    if not AI_OK: return "AI unavailable."
    try:
        resp = _ai.chat.completions.create(
            model="glm-4.6v-flash",
            messages=[{"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}},
                {"type": "text", "text": prompt}
            ]}]
        )
        return resp.choices[0].message.content
    except Exception as e:
        if _is_network_err(e):
            return "⚠️ Cannot reach AI service — check your internet connection and try again."
        return f"⚠️ AI error: {e}"

# ── Invoice image ─────────────────────────────────────────────────────────────

def _invoice_image(inv_no, cust_name, cust_phone, items, total,
                   shop_name="", shop_address="", shop_phone="",
                   shop_email="", logo_data=""):
    # ── Fonts ──────────────────────────────────────────────────────────────────
    _font_pairs = [
        ("C:/Windows/Fonts/arialbd.ttf",  "C:/Windows/Fonts/arial.ttf"),
        ("C:/Windows/Fonts/calibrib.ttf", "C:/Windows/Fonts/calibri.ttf"),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        ("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
         "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),
    ]
    def _font(path, size):
        try: return ImageFont.truetype(path, size)
        except: return None

    f_title = f_hdr = f_reg = f_sm = f_xs = None
    for bold, reg in _font_pairs:
        f_title = _font(bold, 28)
        f_hdr   = _font(bold, 14)
        f_reg   = _font(reg,  14)
        f_sm    = _font(reg,  12)
        f_xs    = _font(reg,  11)
        if f_title: break
    if not f_title:
        d_ = ImageFont.load_default()
        f_title = f_hdr = f_reg = f_sm = f_xs = d_

    # ── Colours ────────────────────────────────────────────────────────────────
    C_BRAND   = (18, 140, 126)   # WhatsApp teal header
    C_ACCENT  = (37, 211, 102)   # green highlights
    C_TBL_HD  = (30, 55, 45)     # table header dark
    C_ROW_A   = (245, 250, 247)  # even row
    C_ROW_B   = (255, 255, 255)  # odd row
    C_TEXT    = (25,  25,  25)
    C_MUTED   = (100, 115, 108)
    C_WHITE   = (255, 255, 255)
    C_TOTAL   = (20,  90,  60)
    C_BORDER  = (210, 225, 218)
    C_BG      = (252, 254, 252)

    # ── Layout constants ───────────────────────────────────────────────────────
    W          = 720
    PAD        = 40
    ROW_H      = 36
    LOGO_SZ    = 80
    HDR_H      = 130       # header block height
    INFO_H     = 70        # invoice info + customer row
    COL_W      = [300, 60, 100, 120]  # Item | Qty | Rate | Amount
    TABLE_TOP  = HDR_H + INFO_H + 20
    n_rows     = len(items)
    H = TABLE_TOP + ROW_H + n_rows * ROW_H + ROW_H + 80  # tbl header+rows+total+footer

    img = Image.new("RGB", (W, H), C_BG)
    d   = ImageDraw.Draw(img)

    # ── HEADER BAR ─────────────────────────────────────────────────────────────
    d.rectangle([0, 0, W, HDR_H], fill=C_BRAND)
    # gradient-ish: lighter stripe
    d.rectangle([0, HDR_H - 8, W, HDR_H], fill=(22, 160, 145))

    logo_x_end = PAD  # where text starts (may shift right if logo present)

    # Shop logo (if provided)
    if logo_data:
        try:
            logo_bytes = base64.b64decode(logo_data.split(",")[-1])
            logo_img   = Image.open(io.BytesIO(logo_bytes)).convert("RGBA")
            logo_img.thumbnail((LOGO_SZ, LOGO_SZ), Image.LANCZOS)
            # white circle mask background
            mask = Image.new("L", (LOGO_SZ, LOGO_SZ), 0)
            from PIL import ImageDraw as _ID
            _ID.Draw(mask).ellipse([0, 0, LOGO_SZ, LOGO_SZ], fill=255)
            bg_circle = Image.new("RGB", (LOGO_SZ, LOGO_SZ), C_WHITE)
            bg_circle.paste(logo_img.resize((LOGO_SZ, LOGO_SZ)), mask=logo_img.split()[3] if logo_img.mode == "RGBA" else None)
            lx = PAD
            ly = (HDR_H - LOGO_SZ) // 2
            img.paste(bg_circle, (lx, ly))
            logo_x_end = PAD + LOGO_SZ + 16
        except:
            pass

    # Shop name & details on the header
    sn = shop_name or "Your Shop"
    d.text((logo_x_end, 24), sn, font=f_title, fill=C_WHITE)
    detail_y = 62
    for detail in [shop_phone, shop_address, shop_email]:
        if detail:
            d.text((logo_x_end, detail_y), detail, font=f_sm, fill=(200, 240, 220))
            detail_y += 18

    # "INVOICE" label — right side of header
    lbl = "INVOICE"
    bb  = d.textbbox((0, 0), lbl, font=f_title)
    lbl_w = bb[2] - bb[0]
    d.text((W - PAD - lbl_w, 24), lbl, font=f_title, fill=C_WHITE)
    # Sub-label: inv no + date
    sub_lines = [f"# {inv_no}", datetime.now().strftime("%d %b %Y")]
    sy = 62
    for sl in sub_lines:
        bb2 = d.textbbox((0, 0), sl, font=f_sm)
        d.text((W - PAD - (bb2[2] - bb2[0]), sy), sl, font=f_sm, fill=(200, 240, 220))
        sy += 18

    # ── BILL-TO / INVOICE INFO STRIP ──────────────────────────────────────────
    strip_y = HDR_H + 12
    d.rectangle([PAD, strip_y, W - PAD, strip_y + INFO_H - 4], fill=C_WHITE,
                outline=C_BORDER, width=1)
    # Bill To
    d.text((PAD + 12, strip_y + 10), "BILL TO", font=f_hdr, fill=C_MUTED)
    d.text((PAD + 12, strip_y + 28), cust_name, font=f_hdr, fill=C_TEXT)
    if cust_phone:
        d.text((PAD + 12, strip_y + 46), cust_phone, font=f_sm, fill=C_MUTED)

    # ── TABLE HEADER ──────────────────────────────────────────────────────────
    ty = TABLE_TOP
    x  = PAD
    headers = ["Item / Description", "Qty", "Rate (₹)", "Amount (₹)"]
    for hdr, cw in zip(headers, COL_W):
        d.rectangle([x, ty, x + cw, ty + ROW_H], fill=C_TBL_HD)
        d.text((x + 8, ty + 10), hdr, font=f_xs, fill=C_WHITE)
        x += cw

    # ── TABLE ROWS ────────────────────────────────────────────────────────────
    for ri, item in enumerate(items):
        ty += ROW_H
        x   = PAD
        bg  = C_ROW_A if ri % 2 == 0 else C_ROW_B
        amt = item.get("qty", 0) * item.get("price", 0)
        vals = [
            item.get("name", ""),
            str(item.get("qty", 0)),
            f"{item.get('price', 0):.2f}",
            f"{amt:.2f}",
        ]
        for v, cw in zip(vals, COL_W):
            d.rectangle([x, ty, x + cw, ty + ROW_H], fill=bg, outline=C_BORDER, width=1)
            d.text((x + 8, ty + 10), str(v), font=f_sm, fill=C_TEXT)
            x += cw

    # ── TOTAL ROW ─────────────────────────────────────────────────────────────
    ty += ROW_H
    x   = PAD
    d.rectangle([x, ty, x + sum(COL_W), ty + ROW_H], fill=C_TOTAL)
    d.text((x + 8, ty + 10), "TOTAL", font=f_hdr, fill=C_WHITE)
    total_str = f"Rs. {total:.2f}"
    bb3 = d.textbbox((0, 0), total_str, font=f_hdr)
    tw  = bb3[2] - bb3[0]
    d.text((x + sum(COL_W) - tw - 12, ty + 10), total_str, font=f_hdr, fill=C_ACCENT)

    # ── FOOTER ────────────────────────────────────────────────────────────────
    fy = ty + ROW_H + 16
    d.line([PAD, fy, W - PAD, fy], fill=C_BORDER, width=1)
    thank = "Thank you for your business!"
    bb4   = d.textbbox((0, 0), thank, font=f_sm)
    d.text(((W - (bb4[2] - bb4[0])) // 2, fy + 10), thank, font=f_sm, fill=C_MUTED)
    if shop_name:
        pw = d.textbbox((0, 0), shop_name, font=f_xs)
        d.text(((W - (pw[2] - pw[0])) // 2, fy + 30), shop_name, font=f_xs, fill=C_MUTED)

    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=95)
    return buf.getvalue()

# ── Auth ──────────────────────────────────────────────────────────────────────

@app.get("/")
def root(request: Request):
    if not _uid(request):
        return templates.TemplateResponse(request, "landing.html")
    return _home()

@app.get("/docs-api")
def docs_page(request: Request):
    return templates.TemplateResponse(request, "docs.html")

@app.get("/settings")
def settings_page(request: Request):
    uid, user = _page_guard(request)
    if not uid: return _auth()
    wa_ok, wa_phone = _wa_status()
    return templates.TemplateResponse(request, "settings.html", {
        "user": user, "wa_ok": wa_ok, "wa_phone": wa_phone,
        "active": "settings", "g_low": 0,
    })

@app.post("/api/settings/profile")
async def update_profile(request: Request):
    uid, user = _page_guard(request)
    if not uid: return JSONResponse({"error": "Unauthorized"}, 401)
    body = await request.json()
    name = (body.get("name") or "").strip()
    if not name:
        return JSONResponse({"error": "Name is required"})
    db = _db()
    db.execute("UPDATE users SET name=? WHERE id=?", (name, uid))
    db.commit(); db.close()
    return JSONResponse({"ok": True, "name": name})

@app.post("/api/settings/password")
async def change_password(request: Request):
    uid, user = _page_guard(request)
    if not uid: return JSONResponse({"error": "Unauthorized"}, 401)
    body = await request.json()
    current = body.get("current_password", "")
    new_pw  = body.get("new_password", "")
    if not current or not new_pw:
        return JSONResponse({"error": "Both fields required"})
    if len(new_pw) < 6:
        return JSONResponse({"error": "Password must be at least 6 characters"})
    import bcrypt
    db = _db()
    row = db.execute("SELECT password_hash FROM users WHERE id=?", (uid,)).fetchone()
    if not row or not bcrypt.checkpw(current.encode(), row["password_hash"].encode()):
        db.close(); return JSONResponse({"error": "Current password is incorrect"})
    new_hash = bcrypt.hashpw(new_pw.encode(), bcrypt.gensalt()).decode()
    db.execute("UPDATE users SET password_hash=? WHERE id=?", (new_hash, uid))
    db.commit(); db.close()
    return JSONResponse({"ok": True})

@app.get("/terms")
def terms_page(request: Request):
    return templates.TemplateResponse(request, "terms.html")

@app.get("/auth")
def auth_page(request: Request):
    if _uid(request): return _home()
    return templates.TemplateResponse(request, "auth.html")

@app.post("/auth/register")
def do_register(request: Request, name: str=Form(...), email: str=Form(...), password: str=Form(...)):
    email_clean = email.lower().strip()
    name_clean  = name.strip()
    vtoken = secrets.token_urlsafe(32)
    smtp_configured = bool(SMTP_USER and SMTP_PASS)
    verified_default = 1 if not smtp_configured else 0  # auto-verify if no SMTP
    db = _db()
    try:
        db.execute(
            "INSERT INTO users (email,password_hash,name,email_verified,verification_token) VALUES (?,?,?,?,?)",
            (email_clean, _hash(password), name_clean, verified_default, vtoken))
        db.commit()
        row = db.execute("SELECT id FROM users WHERE email=?", (email_clean,)).fetchone()
    except sqlite3.IntegrityError:
        db.close()
        return templates.TemplateResponse(request, "auth.html",
            {"error": "Email already registered.", "tab": "reg"})
    uid = row["id"]
    db.close()
    if smtp_configured:
        # Send verification email in background
        threading.Thread(target=_send_verification_email, args=(name_clean, email_clean, vtoken), daemon=True).start()
        return templates.TemplateResponse(request, "check_email.html", {"email": email_clean})
    else:
        # No SMTP — auto-verify and log straight in
        t = secrets.token_hex(32)
        _session_save(t, uid, wa_verified=True)
        r = _home(); r.set_cookie("st", t, httponly=True, max_age=86400*30)
        return r

@app.post("/auth/login")
def do_login(request: Request, email: str=Form(...), password: str=Form(...)):
    db = _db()
    row = db.execute("SELECT * FROM users WHERE email=? AND password_hash=?",
                     (email.lower().strip(), _hash(password))).fetchone()
    db.close()
    if not row:
        return templates.TemplateResponse(request, "auth.html",
            {"error": "Invalid email or password.", "tab": "login"})
    if not row["email_verified"]:
        return templates.TemplateResponse(request, "auth.html", {
            "error": "Please verify your email first. Check your inbox for the verification link.",
            "tab": "login", "unverified_email": row["email"]
        })
    t = secrets.token_hex(32)
    _session_save(t, row["id"], wa_verified=True)
    r = _home(); r.set_cookie("st", t, httponly=True, max_age=86400*30)
    return r

@app.get("/auth/verify-email/{token}")
def verify_email(token: str, request: Request):
    db = _db()
    row = db.execute("SELECT * FROM users WHERE verification_token=?", (token,)).fetchone()
    if not row:
        db.close()
        return templates.TemplateResponse(request, "auth.html",
            {"error": "Invalid or expired verification link.", "tab": "login"})
    db.execute("UPDATE users SET email_verified=1, verification_token='' WHERE id=?", (row["id"],))
    db.commit()
    db.close()
    t = secrets.token_hex(32)
    _session_save(t, row["id"], wa_verified=True)
    r = templates.TemplateResponse(request, "email_verified.html", {"name": row["name"] or row["email"]})
    r.set_cookie("st", t, httponly=True, max_age=86400*30)
    return r

@app.post("/auth/resend-verification")
def resend_verification(request: Request, email: str=Form(...)):
    db = _db()
    row = db.execute("SELECT * FROM users WHERE email=?", (email.lower().strip(),)).fetchone()
    db.close()
    if row and not row["email_verified"] and row["verification_token"]:
        threading.Thread(target=_send_verification_email,
            args=(row["name"] or row["email"], row["email"], row["verification_token"]), daemon=True).start()
    return templates.TemplateResponse(request, "check_email.html",
        {"email": email.lower().strip(), "resent": True})

@app.get("/auth/logout")
def do_logout(request: Request):
    t = request.cookies.get("st")
    if t: _session_delete(t)
    r = _auth(); r.delete_cookie("st"); return r

# ── Connect & Verify ──────────────────────────────────────────────────────────

@app.get("/connect")
def connect_page(request: Request):
    uid, user = _page_guard(request)
    if not uid: return _auth()
    wa_ok, wa_phone = _wa_status()
    return templates.TemplateResponse(request, "connect.html", {
        "user": user, "wa_ok": wa_ok, "wa_phone": wa_phone,
        "active": "connect", "g_low": 0,
    })

@app.get("/verify")
def verify_page(request: Request):
    if not _uid(request): return _auth()
    wa_ok, wa_phone = _wa_status()
    uid = _uid(request)
    db = _db()
    user = dict(db.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone())
    db.close()
    s = _session(request)
    code_sent = bool(s and s.get("code"))
    return templates.TemplateResponse(request, "verify.html", {
        "user": user, "wa_phone": wa_phone, "code_sent": code_sent
    })

@app.post("/api/wa/send-code")
def wa_send_code(request: Request):
    if not _uid(request): return JSONResponse({"error":"unauthorized"},401)
    wa_ok, wa_phone = _wa_status()
    if not wa_ok: return {"error": "WhatsApp not connected — go back and connect first"}
    if not wa_phone:
        return {"error": "Could not read your WhatsApp number — try reconnecting"}
    code = secrets.token_hex(3).upper()   # e.g. "A3F8C2"
    msg = (f"🔐 *Whatfy Verification Code*\n\n"
           f"Your login verification code is:\n\n"
           f"*{code}*\n\n"
           f"_Valid for 5 minutes. Do not share this code with anyone._\n\n"
           f"— Whatfy")
    result = _send_wa(wa_phone, msg)
    if result.get("error"):
        return {"error": f"Send failed: {result['error']}"}
    s = _session(request)
    if s:
        s["code"] = code
        s["code_sent"] = time.time()
    return {"status": "sent", "phone": wa_phone}

@app.post("/api/wa/verify-code")
def wa_verify_code(request: Request, payload: Dict[str,Any]=Body(...)):
    s = _session(request)
    if not s: return JSONResponse({"error":"unauthorized"},401)
    code = payload.get("code","").strip().upper()
    if not s.get("code"):
        return {"error": "No code sent — request a new one"}
    if time.time() - (s.get("code_sent") or 0) > 300:
        s["code"] = None
        return {"error": "Code expired — request a new one"}
    if code != s["code"]:
        return {"error": "Incorrect code — try again"}
    s["code"] = None
    _session_set_verified(request)   # persists to DB
    return {"status": "verified"}

# ── WA proxy ──────────────────────────────────────────────────────────────────

@app.get("/api/wa/status")
def wa_status_api(request: Request):
    if not _uid(request): return JSONResponse({"error":"unauthorized"},401)
    try: r = requests.get(f"{API_BASE}/status",timeout=3); return r.json()
    except Exception as e: return {"connected":False,"loggedIn":False,"error":str(e)}

@app.get("/api/wa/qr-image")
def wa_qr_image(request: Request):
    if not _uid(request): return JSONResponse({"error":"unauthorized"},401)
    try:
        r = requests.get(f"{API_BASE}/qr",timeout=25); data = r.json()
        raw = data.get("qr","")
        if not raw: return {"error": "No QR available — may already be connected"}
        if not QR_OK: return {"error": "qrcode package not installed"}
        q = _qrlib.QRCode(version=1,box_size=8,border=2,
                          error_correction=_qrlib.constants.ERROR_CORRECT_L)
        q.add_data(raw); q.make(fit=True)
        img = q.make_image(fill_color="black",back_color="white")
        buf = io.BytesIO(); img.save(buf,"PNG")
        b64 = base64.b64encode(buf.getvalue()).decode()
        return {"qr_image": f"data:image/png;base64,{b64}"}
    except Exception as e: return {"error":str(e)}

@app.post("/api/wa/pair")
def wa_pair(request: Request, payload: Dict[str,Any]=Body(default={})):
    if not _uid(request): return JSONResponse({"error":"unauthorized"},401)
    try:
        r = requests.get(f"{API_BASE}/pair",params={"number":payload.get("number")},timeout=15)
        return r.json()
    except Exception as e: return {"error":str(e)}

@app.get("/api/wa/logout")
def wa_logout(request: Request):
    if not _uid(request): return JSONResponse({"error":"unauthorized"},401)
    s = _session(request)
    if s: s["wa_verified"] = False
    # Reset all sessions' wa_verified so everyone must re-verify after reconnect
    db = _db()
    db.execute("UPDATE sessions SET wa_verified=0")
    db.commit()
    db.close()
    _sessions.clear()
    try: r = requests.get(f"{API_BASE}/logout",timeout=5); return r.json()
    except Exception as e: return {"error":str(e)}

# ── Pages ─────────────────────────────────────────────────────────────────────

def _page_guard(request: Request):
    """Returns (uid, user_dict) or (None, None) when unauthenticated."""
    uid = _uid(request)
    if not uid:
        return None, None
    db = _db()
    row = db.execute("SELECT id,email,name,email_verified FROM users WHERE id=?", (uid,)).fetchone()
    db.close()
    if not row:
        return None, None
    return uid, dict(row)

def _get_dashboard_stats(uid: int, db) -> dict:
    """Single-connection helper: returns all dashboard counters + agent config."""
    today = datetime.now().strftime("%Y-%m-%d")
    row = db.execute("""
        SELECT
            (SELECT COUNT(*) FROM grocery     WHERE user_id=? AND qty<=low_thresh AND ordered=0) AS g_low,
            (SELECT COUNT(*) FROM invoices    WHERE user_id=? AND status='draft')               AS inv_draft,
            (SELECT COUNT(*) FROM patients    WHERE user_id=?)                                  AS p_total,
            (SELECT COUNT(*) FROM appointments WHERE user_id=? AND appt_date=? AND status='scheduled') AS appt_today
    """, (uid, uid, uid, uid, today)).fetchone()
    agents = {r["agent"]: {"enabled": bool(r["enabled"]), "wa_number": r["wa_number"]}
              for r in db.execute("SELECT agent,enabled,wa_number FROM agent_cfg WHERE user_id=?", (uid,)).fetchall()}
    return {
        "g_low":      row["g_low"],
        "inv_draft":  row["inv_draft"],
        "p_total":    row["p_total"],
        "appt_today": row["appt_today"],
        "agents":     agents,
    }

@app.get("/dashboard")
def dashboard(request: Request):
    uid, user = _page_guard(request)
    if not uid: return _auth()
    db = _db()
    stats = _get_dashboard_stats(uid, db)
    db.close()
    wa_connected, wa_phone = _wa_status()
    return templates.TemplateResponse(request, "dashboard.html", {
        "user": user, "wa_phone": wa_phone, "wa_ok": wa_connected,
        **stats,
    })

@app.get("/shop")
def shop_page(request: Request):
    uid, user = _page_guard(request)
    if not uid: return _auth()
    db = _db()
    items = [dict(r) for r in db.execute(
        "SELECT id,name,qty,unit,low_thresh,price,ordered FROM grocery WHERE user_id=? ORDER BY name",(uid,)).fetchall()]
    cfg = db.execute("SELECT enabled,wa_number,notes FROM agent_cfg WHERE user_id=? AND agent='shop'",(uid,)).fetchone()
    cfg = dict(cfg) if cfg else {"enabled":0,"wa_number":"","notes":""}
    g_low = sum(1 for i in items if i["qty"] <= i["low_thresh"] and not i["ordered"])
    db.close()
    wa_connected, wa_phone = _wa_status()
    return templates.TemplateResponse(request, "shop.html", {
        "user": user, "items": items, "cfg": cfg, "g_low": g_low,
        "wa_ok": wa_connected, "wa_phone": wa_phone, "active": "shop"
    })

@app.get("/invoice")
def invoice_page(request: Request):
    uid, user = _page_guard(request)
    if not uid: return _auth()
    db = _db()
    # Only select the columns we actually render in the list — skip the heavy items JSON
    invs = [dict(r) for r in db.execute(
        "SELECT id,inv_no,cust_name,cust_phone,total,status,created_at FROM invoices "
        "WHERE user_id=? ORDER BY created_at DESC LIMIT 50", (uid,)).fetchall()]
    for inv in invs:
        inv["items"] = []   # items loaded on demand (preview/send)
        inv["date"] = datetime.fromtimestamp(inv["created_at"]).strftime("%d %b %Y")
    cfg = db.execute("SELECT enabled,wa_number,notes FROM agent_cfg WHERE user_id=? AND agent='invoice'",(uid,)).fetchone()
    cfg = dict(cfg) if cfg else {"enabled":0,"wa_number":"","notes":""}
    # Fetch profile WITHOUT logo_data — logo loads async via /api/invoice/logo
    try:
        profile = db.execute(
            "SELECT shop_name,shop_phone,shop_address,shop_email FROM shop_profile WHERE user_id=?",
            (uid,)).fetchone()
        profile = dict(profile) if profile else {}
        has_logo = bool(db.execute(
            "SELECT 1 FROM shop_profile WHERE user_id=? AND logo_data!=''", (uid,)).fetchone())
    except Exception:
        profile = {}
        has_logo = False
    db.close()
    wa_connected, wa_phone = _wa_status()
    return templates.TemplateResponse(request, "invoice.html", {
        "user": user, "invoices": invs, "cfg": cfg,
        "profile": {
            "shop_name":    profile.get("shop_name",""),
            "shop_phone":   profile.get("shop_phone",""),
            "shop_address": profile.get("shop_address",""),
            "shop_email":   profile.get("shop_email",""),
            "has_logo":     has_logo,
        },
        "wa_ok": wa_connected, "wa_phone": wa_phone, "active": "invoice", "g_low": 0
    })

@app.get("/health")
def health_page(request: Request):
    uid, user = _page_guard(request)
    if not uid: return _auth()
    db = _db()
    patients = [dict(r) for r in db.execute(
        "SELECT id,name,phone,age,condition,medications FROM patients WHERE user_id=? ORDER BY name LIMIT 200",(uid,)).fetchall()]
    for p in patients:
        try: p["medications"] = json.loads(p["medications"])
        except: p["medications"] = []
    cfg = db.execute("SELECT enabled,wa_number,notes FROM agent_cfg WHERE user_id=? AND agent='health'",(uid,)).fetchone()
    cfg = dict(cfg) if cfg else {"enabled":0,"wa_number":"","notes":""}
    g_low = db.execute("SELECT COUNT(*) c FROM grocery WHERE user_id=? AND qty<=low_thresh AND ordered=0",(uid,)).fetchone()["c"]
    db.close()
    wa_connected, wa_phone = _wa_status()
    return templates.TemplateResponse(request, "health.html", {
        "user": user, "patients": patients, "cfg": cfg, "g_low": g_low,
        "wa_ok": wa_connected, "wa_phone": wa_phone, "active": "health"
    })

@app.get("/appointment")
def appt_page(request: Request):
    uid, user = _page_guard(request)
    if not uid: return _auth()
    db = _db()
    appts = [dict(r) for r in db.execute(
        "SELECT id,patient_name,patient_phone,doctor,appt_type,appt_date,appt_time,status,notes "
        "FROM appointments WHERE user_id=? ORDER BY appt_date DESC,appt_time LIMIT 200",(uid,)).fetchall()]
    cfg = db.execute("SELECT enabled,wa_number,notes FROM agent_cfg WHERE user_id=? AND agent='appointment'",(uid,)).fetchone()
    cfg = dict(cfg) if cfg else {"enabled":0,"wa_number":"","notes":""}
    g_low = db.execute("SELECT COUNT(*) c FROM grocery WHERE user_id=? AND qty<=low_thresh AND ordered=0",(uid,)).fetchone()["c"]
    db.close()
    wa_connected, wa_phone = _wa_status()
    return templates.TemplateResponse(request, "appointment.html", {
        "user": user, "appointments": appts, "cfg": cfg, "g_low": g_low,
        "wa_ok": wa_connected, "wa_phone": wa_phone, "active": "appointment"
    })

# ── Grocery API ───────────────────────────────────────────────────────────────

@app.post("/api/grocery")
def grocery_add(request: Request, payload: Dict[str,Any]=Body(...)):
    uid = _uid(request)
    if not uid: return JSONResponse({"error":"unauthorized"},401)
    db = _db()
    db.execute("INSERT INTO grocery (user_id,name,qty,unit,low_thresh,price) VALUES (?,?,?,?,?,?)",
               (uid,payload["name"],float(payload.get("qty",0)),payload.get("unit","kg"),
                float(payload.get("low_thresh",5)),float(payload.get("price",0))))
    db.commit()
    rid = db.execute("SELECT last_insert_rowid() id").fetchone()["id"]
    row = dict(db.execute("SELECT * FROM grocery WHERE id=?",(rid,)).fetchone())
    db.close(); return row

@app.put("/api/grocery/{iid}")
def grocery_update(iid: int, request: Request, payload: Dict[str,Any]=Body(...)):
    uid = _uid(request)
    if not uid: return JSONResponse({"error":"unauthorized"},401)
    db = _db()
    db.execute("UPDATE grocery SET name=?,qty=?,unit=?,low_thresh=?,price=?,ordered=? WHERE id=? AND user_id=?",
               (payload["name"],float(payload.get("qty",0)),payload.get("unit","kg"),
                float(payload.get("low_thresh",5)),float(payload.get("price",0)),
                int(payload.get("ordered",0)),iid,uid))
    db.commit()
    row = dict(db.execute("SELECT * FROM grocery WHERE id=?",(iid,)).fetchone())
    db.close(); return row

@app.delete("/api/grocery/{iid}")
def grocery_delete(iid: int, request: Request):
    uid = _uid(request)
    if not uid: return JSONResponse({"error":"unauthorized"},401)
    db = _db(); db.execute("DELETE FROM grocery WHERE id=? AND user_id=?",(iid,uid))
    db.commit(); db.close(); return {"status":"deleted"}

@app.post("/api/grocery/alert")
def grocery_alert(request: Request):
    uid = _uid(request)
    if not uid: return JSONResponse({"error":"unauthorized"},401)
    db = _db()
    low = [dict(r) for r in db.execute(
        "SELECT * FROM grocery WHERE user_id=? AND qty<=low_thresh AND ordered=0 ORDER BY qty",(uid,)).fetchall()]
    cfg = db.execute("SELECT * FROM agent_cfg WHERE user_id=? AND agent='shop'",(uid,)).fetchone()
    db.close()
    if not low: return {"message":"All stock levels are fine!"}
    if not cfg or not cfg["wa_number"]: return {"error":"No WhatsApp number configured for Shop Agent"}
    lines=["⚠️ *Low Stock Alert*",""]
    for it in low: lines.append(f"• {it['name']}: {it['qty']} {it['unit']} (min {it['low_thresh']})")
    lines.append("\n_Please reorder these items._")
    return _send_wa(cfg["wa_number"], "\n".join(lines))

# ── Invoice API ───────────────────────────────────────────────────────────────

@app.post("/api/invoices")
def invoice_create(request: Request, payload: Dict[str,Any]=Body(...)):
    uid = _uid(request)
    if not uid: return JSONResponse({"error":"unauthorized"},401)
    items = payload.get("items",[]); total = sum(i.get("qty",0)*i.get("price",0) for i in items)
    inv_no = f"INV{int(time.time())}"
    db = _db()
    db.execute("INSERT INTO invoices (user_id,inv_no,cust_name,cust_phone,items,total) VALUES (?,?,?,?,?,?)",
               (uid,inv_no,payload["cust_name"],payload["cust_phone"],json.dumps(items),total))
    db.commit()
    rid = db.execute("SELECT last_insert_rowid() id").fetchone()["id"]
    row = dict(db.execute("SELECT * FROM invoices WHERE id=?",(rid,)).fetchone())
    db.close(); row["items"]=items; row["date"]=datetime.now().strftime("%d %b %Y")
    return row

@app.post("/api/invoices/{inv_id}/send")
def invoice_send(inv_id: int, request: Request):
    uid = _uid(request)
    if not uid: return JSONResponse({"error":"unauthorized"},401)
    db = _db()
    inv = db.execute("SELECT * FROM invoices WHERE id=? AND user_id=?",(inv_id,uid)).fetchone()
    if not inv: db.close(); return JSONResponse({"error":"not found"},404)
    inv = dict(inv); items = json.loads(inv["items"] or "[]")
    profile = db.execute("SELECT * FROM shop_profile WHERE user_id=?",(uid,)).fetchone()
    profile = dict(profile) if profile else {}
    if PIL_OK:
        img_b = _invoice_image(
            inv["inv_no"], inv["cust_name"], inv["cust_phone"], items, inv["total"],
            shop_name=profile.get("shop_name",""),
            shop_address=profile.get("shop_address",""),
            shop_phone=profile.get("shop_phone",""),
            shop_email=profile.get("shop_email",""),
            logo_data=profile.get("logo_data",""),
        )
        try:
            r = requests.post(f"{API_BASE}/send-media",
                files={"file":("invoice.jpg",img_b,"image/jpeg")},
                data={"number":inv["cust_phone"],"message":f"Invoice #{inv['inv_no']} — Rs.{inv['total']:.2f}"},
                timeout=30); result=r.json()
        except Exception as e: result={"error":str(e)}
    else:
        lines=[f"*Invoice #{inv['inv_no']}*",f"To: {inv['cust_name']}",""]
        for it in items: lines.append(f"• {it['name']} x{it['qty']} @ {it['price']} = {it['qty']*it['price']:.2f}")
        lines.append(f"\n*Total: Rs.{inv['total']:.2f}*")
        result = _send_wa(inv["cust_phone"], "\n".join(lines))
    if not result.get("error"):
        db.execute("UPDATE invoices SET status='sent',sent_at=? WHERE id=?",(int(time.time()),inv_id))
        db.commit()
    db.close(); return result

@app.delete("/api/invoices/{inv_id}")
def invoice_delete(inv_id: int, request: Request):
    uid = _uid(request)
    if not uid: return JSONResponse({"error":"unauthorized"},401)
    db = _db(); db.execute("DELETE FROM invoices WHERE id=? AND user_id=?",(inv_id,uid))
    db.commit(); db.close(); return {"status":"deleted"}

@app.get("/api/invoice/logo")
def get_logo(request: Request):
    """Return only the logo base64 — called async after page load."""
    uid = _uid(request)
    if not uid: return JSONResponse({"error":"unauthorized"},401)
    try:
        db = _db()
        row = db.execute("SELECT logo_data FROM shop_profile WHERE user_id=?",(uid,)).fetchone()
        db.close()
        return {"logo_data": row["logo_data"] if row and row["logo_data"] else ""}
    except Exception:
        return {"logo_data": ""}

@app.get("/api/invoice/shop-profile")
def get_shop_profile(request: Request):
    uid = _uid(request)
    if not uid: return JSONResponse({"error":"unauthorized"},401)
    try:
        db = _db()
        row = db.execute(
            "SELECT shop_name,shop_phone,shop_address,shop_email,logo_data FROM shop_profile WHERE user_id=?",
            (uid,)).fetchone()
        db.close()
    except Exception:
        return {"shop_name":"","shop_phone":"","shop_address":"","shop_email":"","has_logo":False}
    if row:
        p = dict(row)
        p["has_logo"] = bool(p.pop("logo_data",""))
        return p
    return {"shop_name":"","shop_phone":"","shop_address":"","shop_email":"","has_logo":False}

@app.post("/api/invoice/shop-profile")
def save_shop_profile(request: Request, payload: Dict[str,Any]=Body(...)):
    uid = _uid(request)
    if not uid: return JSONResponse({"error":"unauthorized"},401)
    db = _db()
    existing = db.execute("SELECT user_id FROM shop_profile WHERE user_id=?",(uid,)).fetchone()
    if existing:
        db.execute("""UPDATE shop_profile SET shop_name=?,shop_phone=?,shop_address=?,shop_email=?
                      WHERE user_id=?""",
                   (payload.get("shop_name",""), payload.get("shop_phone",""),
                    payload.get("shop_address",""), payload.get("shop_email",""), uid))
    else:
        db.execute("""INSERT INTO shop_profile (user_id,shop_name,shop_phone,shop_address,shop_email)
                      VALUES (?,?,?,?,?)""",
                   (uid, payload.get("shop_name",""), payload.get("shop_phone",""),
                    payload.get("shop_address",""), payload.get("shop_email","")))
    db.commit(); db.close()
    return {"status":"saved"}

@app.post("/api/invoice/logo")
async def upload_logo(request: Request, file: UploadFile = File(...)):
    uid = _uid(request)
    if not uid: return JSONResponse({"error":"unauthorized"},401)
    data = await file.read()
    if len(data) > 2 * 1024 * 1024:
        return JSONResponse({"error":"Image too large (max 2MB)"},400)
    # Resize to max 400x400 using Pillow if available
    if PIL_OK:
        try:
            img = Image.open(io.BytesIO(data)).convert("RGBA")
            img.thumbnail((400, 400), Image.LANCZOS)
            buf = io.BytesIO()
            img.save(buf, "PNG")
            data = buf.getvalue()
        except:
            pass
    b64 = "data:image/png;base64," + base64.b64encode(data).decode()
    db = _db()
    existing = db.execute("SELECT user_id FROM shop_profile WHERE user_id=?",(uid,)).fetchone()
    if existing:
        db.execute("UPDATE shop_profile SET logo_data=? WHERE user_id=?",(b64,uid))
    else:
        db.execute("INSERT INTO shop_profile (user_id,logo_data) VALUES (?,?)",(uid,b64))
    db.commit(); db.close()
    return {"status":"saved","preview":b64}

@app.delete("/api/invoice/logo")
def delete_logo(request: Request):
    uid = _uid(request)
    if not uid: return JSONResponse({"error":"unauthorized"},401)
    db = _db()
    db.execute("UPDATE shop_profile SET logo_data='' WHERE user_id=?",(uid,))
    db.commit(); db.close()
    return {"status":"deleted"}

@app.get("/api/invoice/preview/{inv_id}")
def invoice_preview(inv_id: int, request: Request):
    """Return the invoice as a JPEG image for in-browser preview."""
    uid = _uid(request)
    if not uid: return JSONResponse({"error":"unauthorized"},401)
    if not PIL_OK: return JSONResponse({"error":"PIL not installed"},500)
    db = _db()
    inv = db.execute("SELECT * FROM invoices WHERE id=? AND user_id=?",(inv_id,uid)).fetchone()
    if not inv: db.close(); return JSONResponse({"error":"not found"},404)
    inv = dict(inv); items = json.loads(inv["items"] or "[]")
    profile = db.execute("SELECT * FROM shop_profile WHERE user_id=?",(uid,)).fetchone()
    profile = dict(profile) if profile else {}
    db.close()
    img_b = _invoice_image(
        inv["inv_no"], inv["cust_name"], inv["cust_phone"], items, inv["total"],
        shop_name=profile.get("shop_name",""),
        shop_address=profile.get("shop_address",""),
        shop_phone=profile.get("shop_phone",""),
        shop_email=profile.get("shop_email",""),
        logo_data=profile.get("logo_data",""),
    )
    return StreamingResponse(io.BytesIO(img_b), media_type="image/jpeg",
                             headers={"Content-Disposition":f"inline; filename=invoice-{inv['inv_no']}.jpg"})

# ── Patient API ───────────────────────────────────────────────────────────────

@app.post("/api/patients")
def patient_add(request: Request, payload: Dict[str,Any]=Body(...)):
    uid = _uid(request)
    if not uid: return JSONResponse({"error":"unauthorized"},401)
    db = _db()
    db.execute("INSERT INTO patients (user_id,name,phone,age,condition,medications) VALUES (?,?,?,?,?,?)",
               (uid,payload["name"],payload["phone"],int(payload.get("age",0)),
                payload.get("condition",""),json.dumps(payload.get("medications",[]))))
    db.commit()
    rid = db.execute("SELECT last_insert_rowid() id").fetchone()["id"]
    row = dict(db.execute("SELECT * FROM patients WHERE id=?",(rid,)).fetchone())
    db.close()
    try: row["medications"]=json.loads(row["medications"])
    except: row["medications"]=[]
    return row

@app.put("/api/patients/{pid}")
def patient_update(pid: int, request: Request, payload: Dict[str,Any]=Body(...)):
    uid = _uid(request)
    if not uid: return JSONResponse({"error":"unauthorized"},401)
    db = _db()
    db.execute("UPDATE patients SET name=?,phone=?,age=?,condition=?,medications=? WHERE id=? AND user_id=?",
               (payload["name"],payload["phone"],int(payload.get("age",0)),
                payload.get("condition",""),json.dumps(payload.get("medications",[])),pid,uid))
    db.commit()
    row = dict(db.execute("SELECT * FROM patients WHERE id=?",(pid,)).fetchone())
    db.close()
    try: row["medications"]=json.loads(row["medications"])
    except: row["medications"]=[]
    return row

@app.delete("/api/patients/{pid}")
def patient_delete(pid: int, request: Request):
    uid = _uid(request)
    if not uid: return JSONResponse({"error":"unauthorized"},401)
    db = _db(); db.execute("DELETE FROM patients WHERE id=? AND user_id=?",(pid,uid))
    db.commit(); db.close(); return {"status":"deleted"}

@app.post("/api/patients/{pid}/remind")
def patient_remind(pid: int, request: Request):
    uid = _uid(request)
    if not uid: return JSONResponse({"error":"unauthorized"},401)
    db = _db()
    p = db.execute("SELECT * FROM patients WHERE id=? AND user_id=?",(pid,uid)).fetchone()
    db.close()
    if not p: return JSONResponse({"error":"not found"},404)
    p = dict(p)
    try: meds=json.loads(p["medications"])
    except: meds=[]
    if not meds: return {"error":"No medications configured"}
    lines=[f"💊 *Medication Reminder*",f"Hello {p['name']}! 👋",""]
    for m in meds: lines.append(f"• *{m.get('name','')}* — {m.get('dose','')} at {m.get('time','')}")
    lines.append("\n_Stay healthy! 🌿_")
    return _send_wa(p["phone"], "\n".join(lines))

# ── Appointment API ───────────────────────────────────────────────────────────

@app.post("/api/appointments")
def appt_create(request: Request, payload: Dict[str,Any]=Body(...)):
    uid = _uid(request)
    if not uid: return JSONResponse({"error":"unauthorized"},401)
    db = _db()
    db.execute("""INSERT INTO appointments
        (user_id,patient_name,patient_phone,doctor,appt_type,appt_date,appt_time,notes)
        VALUES (?,?,?,?,?,?,?,?)""",
        (uid,payload["patient_name"],payload["patient_phone"],payload.get("doctor",""),
         payload.get("appt_type","General"),payload["appt_date"],payload["appt_time"],
         payload.get("notes","")))
    db.commit()
    rid = db.execute("SELECT last_insert_rowid() id").fetchone()["id"]
    row = dict(db.execute("SELECT * FROM appointments WHERE id=?",(rid,)).fetchone())
    db.close(); return row

@app.put("/api/appointments/{aid}")
def appt_update(aid: int, request: Request, payload: Dict[str,Any]=Body(...)):
    uid = _uid(request)
    if not uid: return JSONResponse({"error":"unauthorized"},401)
    db = _db()
    db.execute("""UPDATE appointments SET patient_name=?,patient_phone=?,doctor=?,appt_type=?,
        appt_date=?,appt_time=?,status=?,notes=? WHERE id=? AND user_id=?""",
        (payload["patient_name"],payload["patient_phone"],payload.get("doctor",""),
         payload.get("appt_type","General"),payload["appt_date"],payload["appt_time"],
         payload.get("status","scheduled"),payload.get("notes",""),aid,uid))
    db.commit()
    row = dict(db.execute("SELECT * FROM appointments WHERE id=?",(aid,)).fetchone())
    db.close(); return row

@app.delete("/api/appointments/{aid}")
def appt_delete(aid: int, request: Request):
    uid = _uid(request)
    if not uid: return JSONResponse({"error":"unauthorized"},401)
    db = _db(); db.execute("DELETE FROM appointments WHERE id=? AND user_id=?",(aid,uid))
    db.commit(); db.close(); return {"status":"deleted"}

@app.post("/api/appointments/{aid}/remind")
def appt_remind(aid: int, request: Request):
    uid = _uid(request)
    if not uid: return JSONResponse({"error":"unauthorized"},401)
    db = _db()
    a = db.execute("SELECT * FROM appointments WHERE id=? AND user_id=?",(aid,uid)).fetchone()
    db.close()
    if not a: return JSONResponse({"error":"not found"},404)
    a = dict(a)
    msg = (f"🏥 *Appointment Reminder*\n\nHello {a['patient_name']}!\n\n"
           f"You have an appointment:\n"
           f"• *Doctor:* {a['doctor'] or 'TBD'}\n"
           f"• *Type:* {a['appt_type']}\n"
           f"• *Date:* {a['appt_date']}\n"
           f"• *Time:* {a['appt_time']}\n\n"
           f"{'Notes: ' + a['notes'] if a['notes'] else ''}\n\n"
           f"_Please arrive 15 minutes early._ 🙏")
    return _send_wa(a["patient_phone"], msg)

# ── WhatsApp incoming webhook (called by Go server) ──────────────────────────

def _conv_history(sender: str, limit: int = 10) -> list:
    """Fetch recent conversation history for a sender."""
    db = _db()
    rows = db.execute(
        "SELECT role, content FROM conversations WHERE sender=? ORDER BY created_at DESC LIMIT ?",
        (sender, limit)).fetchall()
    db.close()
    return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]

def _conv_save(sender: str, role: str, content: str):
    """Save a message to conversation history, keep last 20."""
    db = _db()
    db.execute("INSERT INTO conversations (sender,role,content) VALUES (?,?,?)", (sender, role, content))
    db.commit()
    # Prune old messages (keep 20 per sender)
    db.execute("""DELETE FROM conversations WHERE sender=? AND id NOT IN
        (SELECT id FROM conversations WHERE sender=? ORDER BY created_at DESC LIMIT 20)""",
        (sender, sender))
    db.commit()
    db.close()

def _parse_time(t: str) -> str:
    """Convert '6pm', '6:30 pm', '18:00' etc. to HH:MM."""
    t = t.strip().lower().replace(" ", "")
    import re
    m = re.match(r"(\d{1,2})(?::(\d{2}))?(am|pm)?$", t)
    if not m: return t
    h, mi, mer = int(m.group(1)), int(m.group(2) or 0), m.group(3)
    if mer == "pm" and h != 12: h += 12
    if mer == "am" and h == 12: h = 0
    return f"{h:02d}:{mi:02d}"

def _build_ai_reply(sender: str, text: str):
    """Build AI context from enabled agents, use history, book appointments. Runs in background."""
    try:
        db = _db()
        rows = db.execute("SELECT DISTINCT user_id FROM agent_cfg WHERE enabled=1").fetchall()
        if not rows:
            _send_wa(sender, "👋 Hi! I'm Whatfy.\n\nNo agents are active yet. Please enable an agent from the dashboard to get started! 🚀")
            db.close()
            return

        uid = rows[0]["user_id"]
        enabled_agents = {r["agent"] for r in db.execute(
            "SELECT agent FROM agent_cfg WHERE user_id=? AND enabled=1", (uid,)).fetchall()}

        context_parts = []
        if "shop" in enabled_agents:
            items = [dict(r) for r in db.execute("SELECT * FROM grocery WHERE user_id=? ORDER BY name",(uid,)).fetchall()]
            lines = [f"- {i['name']}: {i['qty']} {i['unit']} (low≤{i['low_thresh']}, ₹{i['price']})" for i in items]
            context_parts.append("📦 GROCERY:\n" + ("\n".join(lines) or "Empty."))
        if "invoice" in enabled_agents:
            recent = [dict(r) for r in db.execute("SELECT inv_no,cust_name,total,status FROM invoices WHERE user_id=? ORDER BY created_at DESC LIMIT 10",(uid,)).fetchall()]
            lines = [f"- {r['inv_no']} | {r['cust_name']} | ₹{r['total']:.2f} | {r['status']}" for r in recent]
            context_parts.append("🧾 INVOICES:\n" + ("\n".join(lines) or "None."))
        if "health" in enabled_agents:
            patients = [dict(r) for r in db.execute("SELECT * FROM patients WHERE user_id=?",(uid,)).fetchall()]
            lines = []
            for p in patients:
                try: meds = json.loads(p["medications"])
                except: meds = []
                med_str = "; ".join([f"{m.get('name','')} {m.get('dose','')} at {m.get('time','')}" for m in meds]) or "no meds"
                lines.append(f"- {p['name']} (age {p['age']}, {p['condition']}): {med_str}")
            context_parts.append("💊 PATIENTS:\n" + ("\n".join(lines) or "No patients."))
        if "appointment" in enabled_agents:
            appts = [dict(r) for r in db.execute("SELECT * FROM appointments WHERE user_id=? ORDER BY appt_date,appt_time",(uid,)).fetchall()]
            lines = [f"- {a['patient_name']} | Dr.{a['doctor'] or 'TBD'} | {a['appt_type']} | {a['appt_date']} {a['appt_time']} | {a['status']}" for a in appts]
            context_parts.append("🏥 APPOINTMENTS:\n" + ("\n".join(lines) or "None scheduled."))
        db.close()

        # Extract phone from sender JID
        sender_phone = sender.split("@")[0].split(":")[0]
        today_date = datetime.now().strftime("%Y-%m-%d")
        today_str  = datetime.now().strftime("%d %b %Y, %A")

        system = (
            f"You are Whatfy, a WhatsApp business assistant. Today is {today_str} ({today_date}).\n"
            f"Active agents: {', '.join(enabled_agents)}.\n\n"
            f"Business data:\n\n" + "\n\n".join(context_parts) + "\n\n"
            "IMPORTANT — When you have collected ALL required info for an appointment booking "
            "(patient name, date in YYYY-MM-DD, time in HH:MM 24h, reason/type), "
            "you MUST respond with EXACTLY this on the FIRST line:\n"
            "BOOK_APPOINTMENT:{\"patient_name\":\"...\",\"patient_phone\":\"...\","
            "\"appt_date\":\"YYYY-MM-DD\",\"appt_time\":\"HH:MM\","
            "\"appt_type\":\"...\",\"doctor\":\"\",\"notes\":\"...\"}\n"
            "Then on the next line write the confirmation message to send the user.\n\n"
            f"The user's WhatsApp number is: {sender_phone}\n"
            "Keep replies concise and WhatsApp-friendly. Don't re-introduce yourself in every message."
        )

        # Build messages with conversation history
        history = _conv_history(sender)
        msgs = [{"role": "system", "content": system}]
        msgs.extend(history)
        msgs.append({"role": "user", "content": text})

        # Save user message to history
        _conv_save(sender, "user", text)

        # Per-sender cooldown — drop duplicate rapid messages
        now = time.time()
        with _sender_lock:
            last = _sender_last.get(sender, 0)
            if now - last < _SENDER_MIN_GAP:
                print(f"[WA-IN] cooldown skip for {sender}")
                return
            _sender_last[sender] = now

        # Call AI
        if not AI_OK:
            reply = "⚠️ AI service not available."
        else:
            try:
                reply = _ai_call(msgs) or "I'm sorry, I couldn't generate a response. Please try again."
            except Exception as e:
                if _is_network_err(e):
                    reply = "⚠️ Cannot reach AI service — check internet connection."
                elif "rate" in str(e).lower() or "1302" in str(e):
                    reply = "⚠️ Too many messages — please wait a moment and try again."
                else:
                    reply = f"⚠️ AI error: {e}"

        print(f"[WA-IN] raw reply: {reply[:150]}")

        # Check if AI wants to book an appointment
        if reply.startswith("BOOK_APPOINTMENT:"):
            lines = reply.split("\n", 1)
            json_str = lines[0][len("BOOK_APPOINTMENT:"):].strip()
            human_msg = lines[1].strip() if len(lines) > 1 else ""
            try:
                appt = json.loads(json_str)
                db = _db()
                db.execute(
                    """INSERT INTO appointments
                    (user_id,patient_name,patient_phone,doctor,appt_type,appt_date,appt_time,notes)
                    VALUES (?,?,?,?,?,?,?,?)""",
                    (uid, appt.get("patient_name",""), appt.get("patient_phone", sender_phone),
                     appt.get("doctor",""), appt.get("appt_type","Consultation"),
                     appt.get("appt_date", today_date), appt.get("appt_time","09:00"),
                     appt.get("notes","")))
                db.commit()
                db.close()
                print(f"[WA-IN] Appointment created for {appt.get('patient_name')}")
                # If AI didn't write a confirmation, generate one
                if not human_msg:
                    human_msg = (
                        f"✅ Appointment booked!\n\n"
                        f"👤 Name: {appt.get('patient_name')}\n"
                        f"📅 Date: {appt.get('appt_date')}\n"
                        f"🕐 Time: {appt.get('appt_time')}\n"
                        f"🏥 Type: {appt.get('appt_type')}\n\n"
                        f"We'll send you a reminder. See you soon! 🙏"
                    )
                _conv_save(sender, "assistant", human_msg)
                _send_wa(sender, human_msg)
                return
            except Exception as e:
                print(f"[WA-IN] Booking parse error: {e}")
                # Fall through to send raw reply

        # Normal reply
        _conv_save(sender, "assistant", reply)
        _send_wa(sender, reply)

    except Exception as e:
        print(f"[WA-IN] ERROR: {e}")
        try: _send_wa(sender, "⚠️ Something went wrong. Please try again.")
        except: pass

@app.post("/wa/incoming")
async def wa_incoming(payload: Dict[str,Any]=Body(...), bg: BackgroundTasks = BackgroundTasks()):
    """Receives incoming WA messages — returns immediately, processes AI in background."""
    sender = payload.get("from", "").strip()
    text   = payload.get("message", "").strip()
    print(f"[WA-IN] from={sender!r} text={text!r}")
    # Skip empty, media, groups, and self-messages
    if not sender or not text or text.startswith("[") or sender.endswith("@g.us"):
        return {"ok": True}
    bg.add_task(_build_ai_reply, sender, text)
    return {"ok": True}  # Return immediately — Go webhook won't timeout

@app.get("/api/dashboard/stats")
def dashboard_stats(request: Request):
    uid = _uid(request)
    if not uid: return JSONResponse({"error":"unauthorized"}, 401)
    db = _db()
    stats = _get_dashboard_stats(uid, db)
    db.close()
    _, wa_phone = _wa_status()
    return {**stats, "wa_phone": wa_phone}

# ── Agent config ──────────────────────────────────────────────────────────────

@app.post("/api/agent/{agent_type}")
def agent_save(agent_type: str, request: Request, payload: Dict[str,Any]=Body(...)):
    uid = _uid(request)
    if not uid: return JSONResponse({"error":"unauthorized"},401)
    db = _db()
    db.execute("""INSERT INTO agent_cfg (user_id,agent,enabled,wa_number,notes) VALUES (?,?,?,?,?)
        ON CONFLICT(user_id,agent) DO UPDATE SET
        enabled=excluded.enabled,wa_number=excluded.wa_number,notes=excluded.notes""",
        (uid,agent_type,int(payload.get("enabled",0)),
         payload.get("wa_number",""),payload.get("notes","")))
    db.commit(); db.close()
    return {"status":"saved"}

# ── AI Chat endpoints ─────────────────────────────────────────────────────────

@app.post("/api/ai/shop")
def ai_shop(request: Request, payload: Dict[str,Any]=Body(...)):
    uid = _uid(request)
    if not uid: return JSONResponse({"error":"unauthorized"},401)
    db = _db()
    items = [dict(r) for r in db.execute("SELECT * FROM grocery WHERE user_id=? ORDER BY name",(uid,)).fetchall()]
    db.close()
    inv = "\n".join([f"- {i['name']}: {i['qty']} {i['unit']} (low at {i['low_thresh']}, ₹{i['price']}/unit)" for i in items]) or "Empty inventory."
    system = f"""You are a smart grocery shop assistant AI. Current inventory:\n{inv}\n
Help with stock queries, prices, low-stock warnings, reorder suggestions, and order management.
Be concise and use bullet points for lists."""
    return {"reply": _ai_chat(payload.get("message",""), system)}

@app.post("/api/ai/invoice")
def ai_invoice(request: Request, payload: Dict[str,Any]=Body(...)):
    uid = _uid(request)
    if not uid: return JSONResponse({"error":"unauthorized"},401)
    db = _db()
    recent = [dict(r) for r in db.execute(
        "SELECT inv_no,cust_name,total,status FROM invoices WHERE user_id=? ORDER BY created_at DESC LIMIT 10",(uid,)).fetchall()]
    db.close()
    inv_summary = "\n".join([f"- {r['inv_no']} | {r['cust_name']} | ₹{r['total']:.2f} | {r['status']}" for r in recent]) or "No invoices yet."
    system = f"""You are a billing and invoice assistant AI. Recent invoices:\n{inv_summary}\n
Help with invoice queries, total calculations, customer summaries, and billing advice.
Be professional and concise."""
    return {"reply": _ai_chat(payload.get("message",""), system)}

@app.post("/api/ai/health")
def ai_health(request: Request, payload: Dict[str,Any]=Body(...)):
    uid = _uid(request)
    if not uid: return JSONResponse({"error":"unauthorized"},401)
    db = _db()
    pts = [dict(r) for r in db.execute("SELECT name,age,condition,medications FROM patients WHERE user_id=?",(uid,)).fetchall()]
    db.close()
    pt_summary = "\n".join([f"- {p['name']} (age {p['age']}, {p['condition']})" for p in pts]) or "No patients registered."
    system = f"""You are a compassionate health assistant AI. Registered patients:\n{pt_summary}\n
Help with medication queries, health advice, reminder scheduling, and patient management.
Always recommend consulting a doctor for medical decisions. Be empathetic and clear."""
    return {"reply": _ai_chat(payload.get("message",""), system)}

@app.post("/api/ai/health/analyze")
async def ai_health_analyze(request: Request, file: UploadFile=File(...),
                             prompt: str=Form(default="Analyze this medical image and provide detailed observations about what you see.")):
    if not _uid(request): return JSONResponse({"error":"unauthorized"},401)
    img_bytes = await file.read()
    b64 = base64.b64encode(img_bytes).decode()
    return {"analysis": _ai_vision(b64, prompt)}

@app.post("/api/ai/appointment")
def ai_appointment(request: Request, payload: Dict[str,Any]=Body(...)):
    uid = _uid(request)
    if not uid: return JSONResponse({"error":"unauthorized"},401)
    db = _db()
    appts = [dict(r) for r in db.execute(
        "SELECT patient_name,doctor,appt_type,appt_date,appt_time,status FROM appointments WHERE user_id=? ORDER BY appt_date",(uid,)).fetchall()]
    db.close()
    appt_text = "\n".join([f"- {a['patient_name']} with Dr.{a['doctor']} on {a['appt_date']} {a['appt_time']} ({a['status']})" for a in appts]) or "No appointments."
    system = f"""You are a medical appointment scheduling assistant AI. Current appointments:\n{appt_text}\n
Help with scheduling, rescheduling, cancellations, reminders, and appointment queries.
Be professional, empathetic, and organised."""
    return {"reply": _ai_chat(payload.get("message",""), system)}

# ── Campaign page ─────────────────────────────────────────────────────────────

@app.get("/campaign")
def campaign_page(request: Request):
    uid, user = _page_guard(request)
    if not uid: return _auth()
    db = _db()
    camps = [dict(r) for r in db.execute(
        "SELECT id,name,message,status,total,sent,failed,created_at FROM campaigns "
        "WHERE user_id=? ORDER BY created_at DESC LIMIT 100", (uid,)).fetchall()]
    db.close()
    for c in camps:
        c["running"] = c["id"] in _campaign_threads
        c["date"] = datetime.fromtimestamp(c["created_at"]).strftime("%d %b %Y, %H:%M")
    wa_connected, wa_phone = _wa_status()
    return templates.TemplateResponse(request, "campaign.html", {
        "user": user, "wa_phone": wa_phone, "wa_ok": wa_connected, "active": "campaign",
        "campaigns": camps, "g_low": 0,
    })

# ── Campaign API ──────────────────────────────────────────────────────────────

@app.post("/api/campaigns")
def campaign_create(request: Request, payload: Dict[str, Any] = Body(...)):
    uid = _uid(request)
    if not uid: return JSONResponse({"error": "unauthorized"}, 401)
    name    = payload.get("name", "").strip()
    message = payload.get("message", "").strip()
    delay   = int(payload.get("delay_secs", 20))
    raw     = payload.get("contacts", "")
    if not name or not message or not raw:
        return JSONResponse({"error": "name, message and contacts are required"}, 400)
    contacts = _parse_contacts(raw)
    if not contacts:
        return JSONResponse({"error": "No valid contacts found. Use format: name,phone  or just phone"}, 400)
    db = _db()
    db.execute(
        "INSERT INTO campaigns (user_id,name,message,delay_secs,total) VALUES (?,?,?,?,?)",
        (uid, name, message, max(5, delay), len(contacts)))
    db.commit()
    cid = db.execute("SELECT last_insert_rowid() id").fetchone()["id"]
    db.executemany(
        "INSERT INTO campaign_contacts (campaign_id,name,phone) VALUES (?,?,?)",
        [(cid, c["name"], c["phone"]) for c in contacts])
    db.commit()
    row = dict(db.execute("SELECT * FROM campaigns WHERE id=?", (cid,)).fetchone())
    db.close()
    row["date"] = datetime.fromtimestamp(row["created_at"]).strftime("%d %b %Y, %H:%M")
    return row

@app.get("/api/campaigns")
def campaign_list(request: Request):
    uid = _uid(request)
    if not uid: return JSONResponse({"error": "unauthorized"}, 401)
    db = _db()
    camps = [dict(r) for r in db.execute(
        "SELECT * FROM campaigns WHERE user_id=? ORDER BY created_at DESC", (uid,)).fetchall()]
    db.close()
    for c in camps:
        c["running"] = c["id"] in _campaign_threads
        c["date"] = datetime.fromtimestamp(c["created_at"]).strftime("%d %b %Y, %H:%M")
    return {"campaigns": camps}

@app.get("/api/campaigns/{cid}")
def campaign_get(cid: int, request: Request):
    uid = _uid(request)
    if not uid: return JSONResponse({"error": "unauthorized"}, 401)
    db = _db()
    camp = db.execute("SELECT * FROM campaigns WHERE id=? AND user_id=?", (cid, uid)).fetchone()
    if not camp: db.close(); return JSONResponse({"error": "not found"}, 404)
    camp = dict(camp)
    contacts = [dict(r) for r in db.execute(
        "SELECT * FROM campaign_contacts WHERE campaign_id=? ORDER BY id", (cid,)).fetchall()]
    db.close()
    camp["running"]  = cid in _campaign_threads
    camp["contacts"] = contacts
    camp["date"] = datetime.fromtimestamp(camp["created_at"]).strftime("%d %b %Y, %H:%M")
    return camp

@app.delete("/api/campaigns/{cid}")
def campaign_delete(cid: int, request: Request):
    uid = _uid(request)
    if not uid: return JSONResponse({"error": "unauthorized"}, 401)
    # Stop if running
    with _campaign_lock:
        if cid in _campaign_threads:
            _campaign_stop[cid] = True
    db = _db()
    db.execute("DELETE FROM campaign_contacts WHERE campaign_id=?", (cid,))
    db.execute("DELETE FROM campaigns WHERE id=? AND user_id=?", (cid, uid))
    db.commit()
    db.close()
    return {"status": "deleted"}

@app.post("/api/campaigns/{cid}/start")
def campaign_start(cid: int, request: Request):
    uid = _uid(request)
    if not uid: return JSONResponse({"error": "unauthorized"}, 401)
    with _campaign_lock:
        if cid in _campaign_threads:
            return {"status": "already_running"}
        db = _db()
        camp = db.execute("SELECT * FROM campaigns WHERE id=? AND user_id=?", (cid, uid)).fetchone()
        db.close()
        if not camp: return JSONResponse({"error": "not found"}, 404)
        if camp["status"] == "completed":
            return JSONResponse({"error": "Campaign already completed"}, 400)
        _campaign_stop[cid] = False
        t = threading.Thread(target=_campaign_run, args=(cid,), daemon=True)
        _campaign_threads[cid] = t
        t.start()
    return {"status": "started"}

@app.post("/api/campaigns/{cid}/pause")
def campaign_pause(cid: int, request: Request):
    uid = _uid(request)
    if not uid: return JSONResponse({"error": "unauthorized"}, 401)
    with _campaign_lock:
        if cid not in _campaign_threads:
            return {"status": "not_running"}
        _campaign_stop[cid] = True
    return {"status": "pausing"}

@app.get("/api/campaigns/{cid}/stats")
def campaign_stats(cid: int, request: Request):
    uid = _uid(request)
    if not uid: return JSONResponse({"error": "unauthorized"}, 401)
    db = _db()
    camp = db.execute("SELECT * FROM campaigns WHERE id=? AND user_id=?", (cid, uid)).fetchone()
    if not camp: db.close(); return JSONResponse({"error": "not found"}, 404)
    camp = dict(camp)
    # Get live counts direct from contacts table
    row = db.execute(
        "SELECT SUM(status='sent') sent, SUM(status='failed') failed, SUM(status='pending') pending "
        "FROM campaign_contacts WHERE campaign_id=?", (cid,)).fetchone()
    db.close()
    camp["running"]  = cid in _campaign_threads
    camp["live_sent"]    = row[0] or 0
    camp["live_failed"]  = row[1] or 0
    camp["live_pending"] = row[2] or 0
    return camp

# ── Dev: test email ───────────────────────────────────────────────────────────

@app.get("/api/test-email")
def test_email(request: Request):
    """Diagnose SMTP — tries all connection methods and reports which one works."""

    results = []
    configs = [
        ("smtp.zoho.com",  465, "SSL"),
        ("smtp.zoho.in",   465, "SSL"),
        ("smtp.zoho.com",  587, "STARTTLS"),
        ("smtp.zoho.in",   587, "STARTTLS"),
    ]
    msg = _build_msg(FROM_EMAIL, "Whatfy SMTP Test", "<p>Test OK</p>")
    raw = msg.as_string()

    for host, port, mode in configs:
        label = f"{host}:{port} ({mode})"
        try:
            if mode == "SSL":
                _try_ssl(host, port, FROM_EMAIL, raw)
            else:
                _try_tls(host, port, FROM_EMAIL, raw)
            results.append({"config": label, "status": "✓ SUCCESS"})
            break   # stop on first success
        except smtplib.SMTPAuthenticationError as e:
            results.append({"config": label, "status": f"✗ AUTH FAILED: {e}"})
        except Exception as e:
            results.append({"config": label, "status": f"✗ {type(e).__name__}: {e}"})

    success = any("SUCCESS" in r["status"] for r in results)
    return {
        "user":    SMTP_USER,
        "host":    SMTP_HOST,
        "port":    SMTP_PORT,
        "results": results,
        "fix": None if success else (
            "Auth failed — go to accounts.zoho.com → Security → App Passwords → "
            "generate a password for 'Mail' and update SMTP_PASS in fastapi_app.py"
        )
    }

# ── Chat page ─────────────────────────────────────────────────────────────────

@app.get("/chat")
def chat_page(request: Request):
    uid, user = _page_guard(request)
    if not uid: return _auth()
    wa_connected, wa_phone = _wa_status()
    return templates.TemplateResponse(request, "chat.html", {
        "user": user, "wa_phone": wa_phone, "wa_ok": wa_connected, "active": "chat",
        "api_base": API_BASE, "g_low": 0,
    })

# ── WA message proxy (chat UI) ────────────────────────────────────────────────

@app.get("/api/messages")
def api_messages(request: Request):
    if not _uid(request): return JSONResponse({"error":"unauthorized"},401)
    try:
        r = requests.get(f"{API_BASE}/messages", timeout=5)
        return JSONResponse(r.json())
    except Exception as e:
        return JSONResponse({"messages":[], "error": str(e)})

@app.post("/api/send")
async def api_send(request: Request, payload: Dict[str,Any]=Body(...)):
    if not _uid(request): return JSONResponse({"error":"unauthorized"},401)
    try:
        r = requests.post(f"{API_BASE}/send", json=payload, timeout=15)
        return JSONResponse(r.json())
    except Exception as e:
        return JSONResponse({"error": str(e)})

@app.post("/api/send-media")
async def api_send_media(request: Request):
    if not _uid(request): return JSONResponse({"error":"unauthorized"},401)
    try:
        form = await request.form()
        files = {}
        data  = {}
        for key, val in form.items():
            if hasattr(val, "read"):
                content = await val.read()
                files[key] = (val.filename, content, val.content_type)
            else:
                data[key] = val
        r = requests.post(f"{API_BASE}/send-media", files=files, data=data, timeout=30)
        return JSONResponse(r.json())
    except Exception as e:
        return JSONResponse({"error": str(e)})

@app.get("/api/events")
async def api_events_proxy(request: Request):
    """Proxy SSE events from Go server so chat.html can use relative URL."""
    if not _uid(request): return JSONResponse({"error":"unauthorized"},401)
    try:
        def event_generator():
            with requests.get(f"{API_BASE}/events", stream=True, timeout=None) as r:
                for chunk in r.iter_content(chunk_size=None):
                    if chunk:
                        yield chunk
        return StreamingResponse(event_generator(), media_type="text/event-stream",
                                  headers={"Cache-Control":"no-cache","X-Accel-Buffering":"no"})
    except Exception as e:
        return JSONResponse({"error": str(e)})

@app.get("/api/media/{path:path}")
def api_media_proxy(path: str, request: Request):
    """Proxy media files from Go server."""
    if not _uid(request): return JSONResponse({"error":"unauthorized"},401)
    try:
        r = requests.get(f"{API_BASE}/{path}", stream=True, timeout=15)
        return StreamingResponse(r.iter_content(chunk_size=8192),
                                  media_type=r.headers.get("content-type","application/octet-stream"))
    except Exception as e:
        return JSONResponse({"error": str(e)})

if __name__ == "__main__":
    uvicorn.run("fastapi_app:app", host="0.0.0.0", port=5000, reload=True)
