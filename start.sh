#!/bin/sh
set -e

# Create dirs for SQLite and media
mkdir -p /app/whatsmeow_server

# Start Go whatsmeow server in background (localhost:8080)
cd /app/whatsmeow_server
/app/wa_server &
GO_PID=$!

# Wait for Go server to be ready
echo "Waiting for Go server..."
sleep 2

# Start FastAPI in foreground (0.0.0.0:5000)
cd /app
echo "Starting FastAPI..."
uvicorn fastapi_app:app --host 0.0.0.0 --port 5000 --workers 1

# If FastAPI exits, kill Go too
kill $GO_PID
