#!/bin/bash
# Start Cloudflared tunnel for lab.ai4artsed.org in foreground (visible terminal output)

TUNNEL_NAME="werkraum-tunnel"
TUNNEL_HOSTNAME="lab.ai4artsed.org"
CONFIG_FILE="/etc/cloudflared/config.yml"

echo "=== Cloudflared Tunnel Startup Check ==="
echo ""

# Check 1: Is our specific config already running?
if pgrep -f "cloudflared.*${CONFIG_FILE}" > /dev/null; then
    echo "❌ ERROR: Cloudflared with config ${CONFIG_FILE} is already running!"
    echo "   PID: $(pgrep -f "cloudflared.*${CONFIG_FILE}")"
    echo ""
    echo "To switch modes, first stop the running tunnel:"
    echo "   ./6_stop_cloudflared.sh"
    echo ""
    echo "Then start this script again."
    exit 1
fi

# Check 2: Is the other script running (different config file)?
if pgrep -f "cloudflared.*tunnel run" > /dev/null; then
    echo "❌ ERROR: Another cloudflared tunnel is running (probably 6_start_cloudflared_both.sh)!"
    echo ""
    ps aux | grep "cloudflared.*tunnel run" | grep -v grep
    echo ""
    echo "To switch modes, first stop the running tunnel:"
    echo "   ./6_stop_cloudflared.sh"
    echo ""
    echo "Then start this script again."
    exit 1
fi

echo "✅ No conflicting tunnel processes found"
echo ""
echo "Starting Cloudflared tunnel for ${TUNNEL_HOSTNAME}"
echo "Tunnel: ${TUNNEL_NAME}"
echo "Config: ${CONFIG_FILE}"
echo ""
echo "Press Ctrl+C to stop"
echo ""

cloudflared --config ${CONFIG_FILE} tunnel run
