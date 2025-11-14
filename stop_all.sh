#!/bin/bash
# Stop all backend and cloudflared processes

echo "Stopping all backend processes on port 17801..."
lsof -ti:17801 | xargs -r kill -9

echo "Stopping cloudflared systemd service..."
sudo systemctl stop cloudflared

echo "Checking for any remaining cloudflared processes..."
pkill -9 cloudflared

echo ""
echo "All processes stopped."
echo "To start again:"
echo "  Terminal 1: ./devserver/start_backend_fg.sh"
echo "  Terminal 2: ./start_cloudflared_fg.sh"
