# Stage 1 — Build Go binary
FROM golang:1.25-alpine AS go-builder
WORKDIR /build
COPY whatsmeow_server/ .
RUN go build -o wa_server .

# Stage 2 — Python runtime
FROM python:3.11-slim
WORKDIR /app

# System deps for Pillow + fonts for invoice images
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-dejavu-core \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy Go binary
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

EXPOSE 5000

CMD ["./start.sh"]
