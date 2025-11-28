#!/bin/bash
# Start Cloudflared tunnel with BOTH lab + werkraum (legacy) services
# Temporary config for testing legacy werkraum service on port 5000

TUNNEL_NAME="werkraum-tunnel"
TEMP_CONFIG="/tmp/cloudflared-with-legacy.yml"
CREDENTIALS_FILE="/home/joerissen/.cloudflared/b614ccb7-c8f3-4831-bfbb-d4674a0e2749.json"

echo "=== Cloudflared Tunnel Startup Check (Lab + Legacy Werkraum) ==="
echo ""

# Check: Is any cloudflared already running?
if pgrep -f "cloudflared.*tunnel run" > /dev/null; then
    echo "❌ ERROR: Cloudflared is already running (probably 6_start_cloudflared_lab.sh)!"
    echo "   PID: $(pgrep -f "cloudflared.*tunnel run")"
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

# Create temporary config with both services
echo "Creating temporary config: ${TEMP_CONFIG}"
cat > ${TEMP_CONFIG} << 'EOF'
tunnel: werkraum-tunnel
credentials-file: /home/joerissen/.cloudflared/b614ccb7-c8f3-4831-bfbb-d4674a0e2749.json

ingress:
  # Current DevServer (port 17801)
  - hostname: lab.ai4artsed.org
    service: http://127.0.0.1:17801
    originRequest:
      httpHostHeader: lab.ai4artsed.org
      connectTimeout: 60s
      tcpKeepAlive: 30s
      noHappyEyeballs: false
      keepAliveConnections: 100
      keepAliveTimeout: 90s
      disableChunkedEncoding: false

  # Legacy Werkraum Service (port 5000)
  - hostname: werkraum.ai4artsed.org
    service: http://127.0.0.1:5000
    originRequest:
      httpHostHeader: werkraum.ai4artsed.org
      connectTimeout: 60s
      tcpKeepAlive: 30s
      noHappyEyeballs: false
      keepAliveConnections: 100
      keepAliveTimeout: 90s
      disableChunkedEncoding: false

  # SSH Access
  - hostname: ssh-fedora.ai4artsed.org
    service: ssh://localhost:22

  # Catch-all (must be last)
  - service: http_status:404
EOF

echo "✅ Temporary config created"
echo ""

# Validate config
echo "Validating configuration..."
if ! cloudflared tunnel ingress validate --config ${TEMP_CONFIG}; then
    echo "❌ ERROR: Config validation failed!"
    exit 1
fi

echo "✅ Configuration is valid"
echo ""

# Show ingress rules
echo "=== Ingress Rules ==="
cloudflared tunnel ingress rule https://lab.ai4artsed.org --config ${TEMP_CONFIG}
cloudflared tunnel ingress rule https://werkraum.ai4artsed.org --config ${TEMP_CONFIG}
echo ""

echo "Starting Cloudflared tunnel with BOTH services:"
echo "  - lab.ai4artsed.org → http://127.0.0.1:17801"
echo "  - werkraum.ai4artsed.org → http://127.0.0.1:5000"
echo ""
echo "Config: ${TEMP_CONFIG}"
echo "Press Ctrl+C to stop"
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo "Cleaning up temporary config..."
    rm -f ${TEMP_CONFIG}
    echo "✅ Cleanup complete"
}

trap cleanup EXIT

cloudflared --config ${TEMP_CONFIG} tunnel run
