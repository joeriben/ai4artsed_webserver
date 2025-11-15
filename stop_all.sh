#!/bin/bash
# Stop all backend and cloudflared processes

echo "Stopping all backend processes..."

# Method 1: Kill by port 17801
echo "  - Killing processes on port 17801..."
lsof -ti:17801 | xargs -r kill -9

# Method 2: Kill all python3 server.py processes
echo "  - Killing python3 server.py processes..."
pkill -9 -f "python3.*server.py"

# Method 3: Double-check and kill any remaining
sleep 1
REMAINING=$(ps aux | grep "python3.*server.py" | grep -v grep | wc -l)
if [ $REMAINING -gt 0 ]; then
    echo "  - Found $REMAINING remaining backend processes, force killing..."
    ps aux | grep "python3.*server.py" | grep -v grep | awk '{print $2}' | xargs -r kill -9
fi

echo "Stopping cloudflared systemd service..."
sudo systemctl stop cloudflared 2>/dev/null || true

echo "Checking for any remaining cloudflared processes..."
pkill -9 cloudflared 2>/dev/null || true

echo ""
echo "✅ All processes stopped."
echo ""
echo "To start again:"
echo "  Terminal 1: cd devserver && ./start_backend_fg.sh"
echo "  Terminal 2: ./start_cloudflared_fg.sh"
