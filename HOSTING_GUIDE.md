# Whatfy — Alwaysdata Hosting Guide (2 Accounts)

---

## Architecture

```
WhatsApp User
     │
     ▼
Account 2 — Go WhatsMeow          Account 1 — FastAPI
  (alwaysdata account B)    ←──►   (alwaysdata account A)
  your-go-domain.alwaysdata.net    your-api-domain.alwaysdata.net
```

**How they talk:**

```
User sends WhatsApp message
        ↓
Go (Account 2) receives it
        ↓
Go POSTs to → https://your-api-domain.alwaysdata.net/wa/incoming
        ↓
FastAPI runs AI, sends reply
        ↓
FastAPI calls → https://your-go-domain.alwaysdata.net/send
        ↓
Go sends WhatsApp message back
```

---

## What Was Changed in Your Code

### fastapi_app.py — line 69

Before (hardcoded localhost):
```python
API_BASE = "http://localhost:8080"
```

After (reads from environment variable):
```python
API_BASE = os.environ.get("GO_SERVER_URL", "http://localhost:8080")
```

### whatsmeow_server/main.go — line 37

Before (hardcoded localhost):
```go
const webhookURL = "http://localhost:5000/wa/incoming"
```

After (reads from environment variable):
```go
var webhookURL = func() string {
    if v := os.Getenv("FASTAPI_URL"); v != "" {
        return v + "/wa/incoming"
    }
    return "http://localhost:5000/wa/incoming"
}()
```

---

## Account 1 — FastAPI Setup (Alwaysdata)

### Environment variable to set in Alwaysdata panel:
```
GO_SERVER_URL = https://your-go-domain.alwaysdata.net
```

### Alwaysdata Site config:
- **Type:** Python ASGI  (or Custom process)
- **Command:** `uvicorn fastapi_app:app --host 0.0.0.0 --port 8080 --workers 1`
- **Working directory:** your FastAPI folder

### requirements.txt (clean version — remove unused):
```
fastapi
uvicorn[standard]
requests
pillow
qrcode[pil]
openai
```

---

## Account 2 — Go WhatsMeow Setup (Alwaysdata)

### Environment variable to set in Alwaysdata panel:
```
FASTAPI_URL = https://your-api-domain.alwaysdata.net
```

### Alwaysdata Site/Process config:
- **Type:** Custom process
- **Command:** `./wa_server`  (compile first: `go build -o wa_server .`)
- **Working directory:** your whatsmeow_server folder

### Build the Go binary on the server:
```bash
cd whatsmeow_server
go build -o wa_server .
```

---

## How to Set Environment Variables in Alwaysdata

1. Login to Alwaysdata panel
2. Go to **Advanced → Environment variables**
3. Add:

| Account | Variable | Value |
|---------|----------|-------|
| Account 1 (FastAPI) | `GO_SERVER_URL` | `https://your-go-domain.alwaysdata.net` |
| Account 2 (Go) | `FASTAPI_URL` | `https://your-api-domain.alwaysdata.net` |

---

## What You CANNOT Do (Alwaysdata limits)

| Thing | Status |
|-------|--------|
| Share RAM between accounts | ❌ |
| Share CPU between accounts | ❌ |
| Share disk/files between accounts | ❌ |
| Talk via localhost | ❌ (different servers) |
| Talk via HTTP API | ✅ This is what you now use |
| Talk via Webhooks | ✅ `/wa/incoming` is your webhook |

---

## Local Dev (still works — no changes needed)

When running locally both services still default to localhost:
```
FastAPI → GO_SERVER_URL not set → uses http://localhost:8080  ✅
Go     → FASTAPI_URL not set   → uses http://localhost:5000   ✅
```
