#!/bin/bash
# Stop any running cloudflared tunnel (for switching between modes)

echo "=== Stopping Cloudflared Tunnel ==="
echo ""

# Check if any cloudflared is running
if ! pgrep -f "cloudflared.*tunnel run" > /dev/null; then
    echo "✅ No cloudflared tunnel is running"
    exit 0
fi

# Show which process is running
echo "Found running cloudflared process:"
ps aux | grep "cloudflared.*tunnel run" | grep -v grep
echo ""

# Kill it
echo "Stopping cloudflared..."
pkill -f "cloudflared.*tunnel run"

# Wait a moment
sleep 1

# Verify it stopped
if pgrep -f "cloudflared.*tunnel run" > /dev/null; then
    echo "❌ Failed to stop cloudflared"
    echo "   Try manually: pkill -9 -f 'cloudflared.*tunnel run'"
    exit 1
else
    echo "✅ Cloudflared stopped successfully"
fi
