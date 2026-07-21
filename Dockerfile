# Stage 1 — Build Go binary (Multi-Session WhatsApp Server)
FROM golang:1.24-alpine AS go-builder
WORKDIR /build
COPY whatsmeow_server/ .
RUN CGO_ENABLED=0 go build -mod=vendor -o wa_server .

# Stage 2 — Python runtime (FastAPI + Multi-Tenancy)
FROM python:3.11-slim
WORKDIR /app

# System deps for Pillow + fonts for invoice images
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    fonts-dejavu-core \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy Go binary from stage 1
COPY --from=go-builder /build/wa_server .

# Copy Python app
COPY fastapi_app.py .
COPY requirements.txt .
COPY templates/ templates/

# Install Python deps
RUN pip install --no-cache-dir -r requirements.txt

# Copy start script
COPY start.sh .
RUN chmod +x start.sh

# media/ and db files persist via volume
VOLUME ["/app/whatsmeow_server"]

# Environment variables
# ENV API_BASE="http://localhost:8080"
# ENV SMTP_HOST="smtp.zoho.in"
# ENV SMTP_PORT="465"
# ENV SMTP_USER="info@opendrap.website"
# ENV SMTP_PASS="h0LBrxNA4u4G"
# ENV FROM_EMAIL="info@opendrap.website"
# ENV APP_URL="http://whatfy.opendrap.website"

# Expose FastAPI port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

CMD ["./start.sh"]
