#!/bin/bash
# Start Cloudflared tunnel in foreground (visible terminal output)

echo "Starting Cloudflared tunnel for lab.ai4artsed.org"
echo "Press Ctrl+C to stop"
echo ""

cloudflared --config /etc/cloudflared/config.yml tunnel run
