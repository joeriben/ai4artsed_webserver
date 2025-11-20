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
    echo "To stop it, run: pkill -f 'cloudflared.*${CONFIG_FILE}'"
    exit 1
fi

# Check 2: Does our tunnel show active connections?
echo "Checking tunnel status for ${TUNNEL_NAME}..."
TUNNEL_INFO=$(cloudflared tunnel info ${TUNNEL_NAME} 2>&1)
if echo "$TUNNEL_INFO" | grep -q "active connection"; then
    echo "❌ ERROR: Tunnel ${TUNNEL_NAME} already has active connections!"
    echo ""
    echo "$TUNNEL_INFO"
    echo ""
    echo "Another process might be running this tunnel."
    echo "To find it: ps aux | grep cloudflared"
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
