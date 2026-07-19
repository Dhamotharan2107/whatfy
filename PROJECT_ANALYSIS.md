# Whatfy Project Analysis

## What is This Project?

**Whatfy** is a WhatsApp automation platform that integrates with OpenAI's GLM-4.7 Flash model for intelligent AI responses. It's a dual-stack architecture application that combines Go's efficiency for WhatsApp connections with FastAPI's speed for AI processing and web functionality.

### Key Features
- WhatsApp messaging automation via Go WhatsMeow library
- AI-powered chat responses using OpenAI GLM-4.7 Flash
- Business management tools (grocery tracking, invoices, appointments)
- Multi-user support with session management
- Campaign management for bulk WhatsApp messaging
- Dashboard with real-time statistics
- Docker containerization for deployment

## What This Project Uses

### Backend Technologies
- **FastAPI** - Python web framework for API endpoints, AI chat interface, and business tools
- **Go + WhatsMeow** - WhatsApp library for handling WhatsApp connections, receiving messages, and sending replies
- **SQLite** - Embedded database for users, sessions, conversations, campaigns, and business data
- **OpenAI GLM-4.7 Flash** - AI model for generating intelligent responses to WhatsApp messages
- **Pillow (PIL)** - Image processing for invoice generation and QR code creation
- **Requests** - HTTP client for webhook communication between Go and FastAPI services

### Frontend Technologies
- **Jinja2 Templates** - Server-side templating for dynamic HTML pages
- **Static HTML Pages** - Multiple templates for different sections:
  - Landing page (index.html)
  - Authentication pages (auth.html, verify.html)
  - Dashboard (dashboard.html)
  - Shop management (shop.html)
  - Invoice management (invoice.html)
  - Campaign management (campaign.html)
  - Chat interface (chat.html)
  - Documentation (docs.html)
  - Terms and conditions (terms.html)

### Development & Deployment
- **Docker** - Containerization with multi-stage builds (Go builder + Python runtime)
- **Shell Scripts** - start.sh for container startup, build_push.sh for Docker Hub deployment
- **Git** - Version control with .gitignore file

## How This Project Was Created

### Architecture Overview
Whatfy uses a dual-service architecture with two main components:

```
User sends WhatsApp message
    ↓
Go WhatsMeow Server (port 8080) receives message
    ↓
Go POSTs to FastAPI webhook at /wa/incoming
    ↓
FastAPI processes message, calls OpenAI AI
    ↓
FastAPI calls Go API to send WhatsApp reply
    ↓
User receives AI response
```

### Development Process

#### 1. Core Components Created

**Go WhatsApp Server (whatsmeow_server/)**
- Built using Go 1.25.0 with whatsmeow library
- Manages WhatsApp connections and authentication
- Receives incoming messages via webhook
- Forwards messages to FastAPI
- Sends WhatsApp messages using OpenAI AI responses
- Uses SQLite database (store.db) for session management
- Exposes local service on port 8080

**FastAPI Application (fastapi_app.py)**
- Python 3.11 application using FastAPI framework
- Manages user authentication and sessions
- Processes WhatsApp messages via webhook endpoint
- Integrates with OpenAI GLM-4.7 Flash for AI responses
- Handles business features (grocery, invoices, appointments, campaigns)
- Provides web interface with Jinja2 templates
- Runs on port 5000 with Uvicorn server

**Database Schema**
- Users table with email, password, verification
- Grocery items with low stock tracking
- Invoices with customer management
- Patient records and appointments
- Agent configuration for WhatsApp integration
- Campaign management for bulk messaging
- Conversation history for AI context

#### 2. Implementation Details

**AI Integration**
```python
from openai import OpenAI as _OpenAI
_ai = _OpenAI(
    api_key="4ed473e121c7480186f26d81a0464b41...",
    base_url="https://open.bigmodel.cn/api/paas/v4/",
    timeout=60.0,
)
```

**WhatsApp Integration**
- Uses Go's whatsmeow library (v0.0.0-20260227112304-c9652e4448a2)
- Handles QR code authentication flow
- Processes text, image, video, and document messages
- Manages conversations and sessions

**Webhook Communication**
- Go server sends messages to FastAPI's `/wa/incoming` endpoint
- FastAPI processes and returns AI responses
- FastAPI calls Go's `/send` endpoint to send WhatsApp messages

#### 3. Containerization (Docker)

**Multi-stage Docker Build**
1. **Go Builder Stage** - Builds Go binary from source code
2. **Python Runtime Stage** - Copies Go binary, Python app, templates
3. **Dependencies** - Installs Python packages from requirements.txt
4. **Configuration** - Copies start script, sets up volume mounts

**Docker Compose/Container Setup**
- Exposes FastAPI on port 5000
- Exposes Go server internally on port 8080
- Mounts volumes for SQLite database and media files
- Uses start.sh to launch both services

#### 4. Deployment Pipeline

**Docker Hub Deployment**
- Image name: `tertwer/whatfy`
- Automated build and push via build_push.sh script
- Multi-arch support (implied from Alpine base)

**Hosting Guide**
- Deployed on Alwaysdata (2 accounts for separation)
- Account 1: FastAPI service
- Account 2: Go WhatsMeow service
- Apache reverse proxy configuration
- Environment variables for URL configuration

## What's Similar to FastAPI in This Project

### FastAPI as the Core Framework

The project heavily relies on FastAPI for the main application layer:

1. **Web Application Layer**
   - FastAPI serves the entire web interface
   - All business tools (dashboard, shop, invoice, etc.) are FastAPI routes
   - Templates are rendered using FastAPI's Jinja2 integration

2. **API Endpoints**
   - All RESTful API endpoints use FastAPI decorators (@app.get, @app.post)
   - Route handlers for authentication, data management, and WhatsApp integration

3. **WebSocket Support**
   - Real-time updates using server-sent events (SSE) via FastAPI
   - Background tasks for campaign processing

4. **Middleware & Utilities**
   - Session management with FastAPI's request handling
   - Authentication guards and page protection
   - Rate limiting for AI responses

### FastAPI's Role Compared to Go Component

| Component | Role | Technology |
|-----------|------|------------|
| **WhatsApp Connection** | Direct WhatsApp API management | Go + WhatsMeow |
| **Message Reception** | Listen for incoming messages | Go HTTP server on port 8080 |
| **Message Sending** | Send WhatsApp messages | Go HTTP client /api/send |
| **AI Processing** | Generate intelligent responses | FastAPI + OpenAI GLM-4.7 |
| **Web Interface** | User dashboard and tools | FastAPI + Jinja2 templates |
| **API Layer** | REST endpoints and business logic | FastAPI |
| **Database Access** | CRUD operations | SQLite via FastAPI functions |
| **User Authentication** | Login, sessions, verification | FastAPI + SQLite |

### Why This Dual Architecture?

1. **Performance**: Go excels at network I/O and handling concurrent connections (WhatsApp messages)
2. **WhatsApp Library Support**: WhatsMeow has better Go integration than Python
3. **AI Integration**: FastAPI has excellent Python AI library support (OpenAI SDK)
4. **Development**: Python easier for rapid development of AI features and business logic
5. **Scalability**: Each service can be deployed and scaled independently

### Communication Flow

```
[WhatsApp]
    ↓
[Go Server: port 8080]
    ↓ (webhook POST)
[FastAPI: port 5000]
    ↓ (OpenAI API call)
[AI Response]
    ↓ (HTTP POST to Go)
[Go Server: port 8080]
    ↓
[WhatsApp]
```

### Key FastAPI Files

- **fastapi_app.py** (94KB) - Main application with all routes and business logic
- **templates/** - 30+ Jinja2 template files for the frontend
- **requirements.txt** - Python dependencies (FastAPI, OpenAI, Pillow, etc.)

### Key Go Files

- **whatsmeow_server/main.go** (34KB) - WhatsApp server implementation
- **whatsmeow_server/go.mod** - Go module dependencies
- **whatsmeow_server/wa_server** (29MB) - Compiled Go binary

## Summary

Whatfy is a sophisticated WhatsApp automation platform built using **FastAPI as its primary application framework** with a **Go microservice** for WhatsApp connectivity. The architecture leverages FastAPI's strengths in AI integration and web development while using Go for the heavy network I/O of WhatsApp messaging. This combination provides a powerful, scalable solution for automated WhatsApp communications with AI assistance.