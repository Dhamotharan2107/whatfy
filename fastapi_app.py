from fastapi import FastAPI, Request, Form, Body, UploadFile, File, BackgroundTasks
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, Dict, Any
import sqlite3, hashlib, secrets, json, time, io, base64, threading, os
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
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            email         TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name          TEXT DEFAULT '',
            created_at    INTEGER DEFAULT (strftime('%s','now'))
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
    """)
    db.close()

_init()

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

def _wa_status():
    try:
        r = requests.get(f"{API_BASE}/status", timeout=2)
        s = r.json()
        connected = bool(s.get("connected") and s.get("loggedIn"))
        phone = ""
        if connected:
            try:
                u = requests.get(f"{API_BASE}/user", timeout=2).json()
                # /user returns {"phone": "919876543210", "jid": "...", "name": "..."}
                phone = u.get("phone", "")
            except:
                pass
        return connected, phone
    except:
        return False, ""

def _send_wa(number: str, msg: str):
    return requests.post(f"{API_BASE}/send",
                         json={"number": number, "message": msg}, timeout=15).json()

# ── AI helpers ────────────────────────────────────────────────────────────────

def _is_network_err(e: Exception) -> bool:
    cls = type(e).__name__
    msg = str(e).lower()
    return any(k in cls+msg for k in ("connect","getaddrinfo","network","timeout","apiconnection"))

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

def _invoice_image(inv_no, cust_name, items, total):
    _fonts = [
        ("C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/arial.ttf"),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    fb = fr = fs = None
    for bold, reg in _fonts:
        try:
            fb = ImageFont.truetype(bold, 22)
            fr = ImageFont.truetype(reg, 18)
            fs = ImageFont.truetype(reg, 14)
            break
        except:
            continue
    if fb is None:
        fb = fr = fs = ImageFont.load_default()
    pad=40; col=[280,70,100,110]; rh=42
    W=sum(col)+2*pad; H=180+(len(items)+3)*rh+60
    img=Image.new("RGB",(W,H),(255,255,255)); d=ImageDraw.Draw(img)
    d.rectangle([0,0,W,160],fill=(37,211,102))
    d.text((pad,18),"INVOICE",font=fb,fill=(255,255,255))
    d.text((pad,52),f"#{inv_no}",font=fr,fill=(255,255,255))
    d.text((pad,82),f"To: {cust_name}",font=fr,fill=(255,255,255))
    d.text((pad,112),datetime.now().strftime("%d %b %Y"),font=fs,fill=(210,255,210))
    y=160+pad; x=pad
    for h,cw in zip(["Item","Qty","Rate","Amt"],col):
        d.rectangle([x,y,x+cw,y+rh],fill=(20,160,80))
        d.text((x+8,y+12),h,font=fs,fill=(255,255,255)); x+=cw
    for ri,item in enumerate(items):
        y+=rh; x=pad; bg=(248,252,248) if ri%2==0 else (255,255,255)
        amt=item.get("qty",0)*item.get("price",0)
        for v,cw in zip([item.get("name",""),str(item.get("qty",0)),
                         f"{item.get('price',0):.2f}",f"{amt:.2f}"],col):
            d.rectangle([x,y,x+cw,y+rh],fill=bg)
            d.text((x+8,y+12),str(v),font=fs,fill=(30,30,30)); x+=cw
    y+=rh; x=pad
    d.rectangle([x,y,x+sum(col),y+rh],fill=(37,211,102))
    d.text((x+8,y+12),"TOTAL",font=fb,fill=(255,255,255))
    d.text((x+sum(col[:3])+8,y+12),f"Rs. {total:.2f}",font=fb,fill=(255,255,255))
    buf=io.BytesIO(); img.save(buf,"JPEG",quality=95)
    return buf.getvalue()

# ── Auth ──────────────────────────────────────────────────────────────────────

@app.get("/")
def root(request: Request):
    if not _uid(request): return _auth()
    return _home()

@app.get("/auth")
def auth_page(request: Request):
    if _uid(request): return _home()
    return templates.TemplateResponse(request, "auth.html")

@app.post("/auth/register")
def do_register(request: Request, name: str=Form(...), email: str=Form(...), password: str=Form(...)):
    db = _db()
    try:
        db.execute("INSERT INTO users (email,password_hash,name) VALUES (?,?,?)",
                   (email.lower().strip(), _hash(password), name.strip()))
        db.commit()
        row = db.execute("SELECT id FROM users WHERE email=?", (email.lower().strip(),)).fetchone()
    except sqlite3.IntegrityError:
        db.close()
        return templates.TemplateResponse(request, "auth.html",
            {"error": "Email already registered.", "tab": "reg"})
    db.close()
    t = secrets.token_hex(32)
    _session_save(t, row["id"], wa_verified=True)
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
    t = secrets.token_hex(32)
    _session_save(t, row["id"], wa_verified=True)
    r = _home(); r.set_cookie("st", t, httponly=True, max_age=86400*30)
    return r

@app.get("/auth/logout")
def do_logout(request: Request):
    t = request.cookies.get("st")
    if t: _session_delete(t)
    r = _auth(); r.delete_cookie("st"); return r

# ── Connect & Verify ──────────────────────────────────────────────────────────

@app.get("/connect")
def connect_page(request: Request):
    if not _uid(request): return _auth()
    wa_ok, wa_phone = _wa_status()
    uid = _uid(request)
    db = _db()
    user = dict(db.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone())
    db.close()
    return templates.TemplateResponse(request, "connect.html", {
        "user": user, "wa_ok": wa_ok, "wa_phone": wa_phone
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
    """Returns (uid, user_dict) or raises redirect to login."""
    uid = _uid(request)
    if not uid: raise _auth()
    db = _db()
    user = dict(db.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone())
    db.close()
    return uid, user

@app.get("/dashboard")
def dashboard(request: Request):
    try: uid, user = _page_guard(request)
    except Exception as redir: return redir
    db = _db()
    g_low = db.execute("SELECT COUNT(*) c FROM grocery WHERE user_id=? AND qty<=low_thresh AND ordered=0",(uid,)).fetchone()["c"]
    inv_draft = db.execute("SELECT COUNT(*) c FROM invoices WHERE user_id=? AND status='draft'",(uid,)).fetchone()["c"]
    p_total = db.execute("SELECT COUNT(*) c FROM patients WHERE user_id=?",(uid,)).fetchone()["c"]
    appt_today = db.execute("SELECT COUNT(*) c FROM appointments WHERE user_id=? AND appt_date=? AND status='scheduled'",
                             (uid,datetime.now().strftime("%Y-%m-%d"))).fetchone()["c"]
    agents = {r["agent"]:dict(r) for r in db.execute("SELECT * FROM agent_cfg WHERE user_id=?",(uid,)).fetchall()}
    db.close()
    _, wa_phone = _wa_status()
    return templates.TemplateResponse(request, "dashboard.html", {
        "user": user, "wa_phone": wa_phone, "wa_ok": True,
        "g_low": g_low, "inv_draft": inv_draft, "p_total": p_total,
        "appt_today": appt_today, "agents": agents,
    })

@app.get("/shop")
def shop_page(request: Request):
    try: uid, user = _page_guard(request)
    except Exception as r: return r
    db = _db()
    items = [dict(r) for r in db.execute("SELECT * FROM grocery WHERE user_id=? ORDER BY name",(uid,)).fetchall()]
    cfg = db.execute("SELECT * FROM agent_cfg WHERE user_id=? AND agent='shop'",(uid,)).fetchone()
    cfg = dict(cfg) if cfg else {"enabled":0,"wa_number":"","notes":""}
    db.close()
    _, wa_phone = _wa_status()
    return templates.TemplateResponse(request, "shop.html", {
        "user": user, "items": items, "cfg": cfg,
        "wa_ok": True, "wa_phone": wa_phone, "active": "shop"
    })

@app.get("/invoice")
def invoice_page(request: Request):
    try: uid, user = _page_guard(request)
    except Exception as r: return r
    db = _db()
    invs = [dict(r) for r in db.execute(
        "SELECT * FROM invoices WHERE user_id=? ORDER BY created_at DESC LIMIT 50",(uid,)).fetchall()]
    for inv in invs:
        try: inv["items"] = json.loads(inv["items"])
        except: inv["items"] = []
        inv["date"] = datetime.fromtimestamp(inv["created_at"]).strftime("%d %b %Y")
    cfg = db.execute("SELECT * FROM agent_cfg WHERE user_id=? AND agent='invoice'",(uid,)).fetchone()
    cfg = dict(cfg) if cfg else {"enabled":0,"wa_number":"","notes":""}
    db.close()
    _, wa_phone = _wa_status()
    return templates.TemplateResponse(request, "invoice.html", {
        "user": user, "invoices": invs, "cfg": cfg,
        "wa_ok": True, "wa_phone": wa_phone, "active": "invoice"
    })

@app.get("/health")
def health_page(request: Request):
    try: uid, user = _page_guard(request)
    except Exception as r: return r
    db = _db()
    patients = [dict(r) for r in db.execute("SELECT * FROM patients WHERE user_id=?",(uid,)).fetchall()]
    for p in patients:
        try: p["medications"] = json.loads(p["medications"])
        except: p["medications"] = []
    cfg = db.execute("SELECT * FROM agent_cfg WHERE user_id=? AND agent='health'",(uid,)).fetchone()
    cfg = dict(cfg) if cfg else {"enabled":0,"wa_number":"","notes":""}
    db.close()
    _, wa_phone = _wa_status()
    return templates.TemplateResponse(request, "health.html", {
        "user": user, "patients": patients, "cfg": cfg,
        "wa_ok": True, "wa_phone": wa_phone, "active": "health"
    })

@app.get("/appointment")
def appt_page(request: Request):
    try: uid, user = _page_guard(request)
    except Exception as r: return r
    db = _db()
    appts = [dict(r) for r in db.execute(
        "SELECT * FROM appointments WHERE user_id=? ORDER BY appt_date,appt_time",(uid,)).fetchall()]
    cfg = db.execute("SELECT * FROM agent_cfg WHERE user_id=? AND agent='appointment'",(uid,)).fetchone()
    cfg = dict(cfg) if cfg else {"enabled":0,"wa_number":"","notes":""}
    db.close()
    _, wa_phone = _wa_status()
    return templates.TemplateResponse(request, "appointment.html", {
        "user": user, "appointments": appts, "cfg": cfg,
        "wa_ok": True, "wa_phone": wa_phone, "active": "appointment"
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
    if PIL_OK:
        img_b = _invoice_image(inv["inv_no"],inv["cust_name"],items,inv["total"])
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
    today = datetime.now().strftime("%Y-%m-%d")
    g_low     = db.execute("SELECT COUNT(*) c FROM grocery WHERE user_id=? AND qty<=low_thresh AND ordered=0",(uid,)).fetchone()["c"]
    inv_draft = db.execute("SELECT COUNT(*) c FROM invoices WHERE user_id=? AND status='draft'",(uid,)).fetchone()["c"]
    p_total   = db.execute("SELECT COUNT(*) c FROM patients WHERE user_id=?",(uid,)).fetchone()["c"]
    appt_today= db.execute("SELECT COUNT(*) c FROM appointments WHERE user_id=? AND appt_date=? AND status='scheduled'",(uid,today)).fetchone()["c"]
    agents    = {r["agent"]: {"enabled": bool(r["enabled"])} for r in db.execute("SELECT agent,enabled FROM agent_cfg WHERE user_id=?",(uid,)).fetchall()}
    db.close()
    _, wa_phone = _wa_status()
    return {"g_low": g_low, "inv_draft": inv_draft, "p_total": p_total,
            "appt_today": appt_today, "agents": agents, "wa_phone": wa_phone}

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

if __name__ == "__main__":
    uvicorn.run("fastapi_app:app", host="0.0.0.0", port=5000, reload=True)
