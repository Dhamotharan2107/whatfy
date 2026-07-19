#!/bin/bash
set -e

echo "Building Go WhatsMeow Server..."

cd "$(dirname "$0")"

if [ ! -f "main.go" ]; then
    echo "main.go not found"
    exit 1
fi

echo "Building Go binary..."
go build -o wa_server .

echo "Build complete: whatsmeow_server/wa_server"
echo ""
echo "Server details:"
echo "  - Binary: wa_server"
echo "  - Size: $(du -h wa_server | cut -f1)"
echo "  - Mode: Single-session WhatsMeow transport with enriched inbox metadata"
