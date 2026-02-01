#!/bin/bash
# AI4ArtsEd - Systemd Services Installation
# Makes backend and cloudflared start automatically on boot
#
# REQUIRES: sudo privileges
# RUN ONCE: After initial setup on production/remote servers
#
# Usage: sudo ./install_systemd_services.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}[✗]${NC} This script must be run with sudo"
    echo "    Usage: sudo ./install_systemd_services.sh"
    exit 1
fi

# Get the actual user (not root)
ACTUAL_USER="${SUDO_USER:-$USER}"
if [ "$ACTUAL_USER" = "root" ]; then
    echo -e "${RED}[✗]${NC} Cannot determine actual user. Don't run as root directly."
    echo "    Usage: sudo ./install_systemd_services.sh"
    exit 1
fi

# Get script directory (should be repo root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEVSERVER_DIR="$SCRIPT_DIR/devserver"

echo -e "${BLUE}=== AI4ArtsEd - Systemd Services Setup ===${NC}"
echo ""
echo "This will configure automatic startup on boot for:"
echo "  - Cloudflared tunnel (if config exists)"
echo "  - AI4ArtsEd backend"
echo ""
echo "Installation directory: $SCRIPT_DIR"
echo "Running as user: $ACTUAL_USER"
echo ""

# Verify devserver exists
if [ ! -f "$DEVSERVER_DIR/server.py" ]; then
    echo -e "${RED}[✗]${NC} server.py not found in $DEVSERVER_DIR"
    exit 1
fi

# Detect port from environment or default
BACKEND_PORT="${PORT:-17801}"
echo -e "${BLUE}[Info]${NC} Backend will run on port $BACKEND_PORT"
echo ""

# ============================================
# Step 1: Cloudflared Service
# ============================================
echo -e "${BLUE}[1/3]${NC} Checking Cloudflared..."

CLOUDFLARED_CONFIG="/etc/cloudflared/config.yml"

if [ -f "$CLOUDFLARED_CONFIG" ]; then
    echo -e "${GREEN}[✓]${NC} Cloudflared config found: $CLOUDFLARED_CONFIG"

    # Check if service file exists
    if [ -f "/etc/systemd/system/cloudflared.service" ]; then
        echo -e "${BLUE}[→]${NC} Cloudflared service already exists"
    else
        echo -e "${BLUE}[Creating]${NC} Cloudflared systemd service..."

        cat > /etc/systemd/system/cloudflared.service << EOF
[Unit]
Description=Cloudflared Tunnel
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$ACTUAL_USER
ExecStart=/usr/local/bin/cloudflared --config $CLOUDFLARED_CONFIG tunnel run
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
        echo -e "${GREEN}[✓]${NC} Cloudflared service created"
    fi

    # Enable cloudflared
    systemctl daemon-reload
    systemctl enable cloudflared
    echo -e "${GREEN}[✓]${NC} Cloudflared enabled for boot"

    CLOUDFLARED_ENABLED=true
else
    echo -e "${YELLOW}[⚠]${NC} No cloudflared config at $CLOUDFLARED_CONFIG"
    echo "    Skipping cloudflared setup. Configure manually if needed."
    CLOUDFLARED_ENABLED=false
fi

# ============================================
# Step 2: Backend Service
# ============================================
echo ""
echo -e "${BLUE}[2/3]${NC} Creating AI4ArtsEd backend service..."

# Determine dependencies
if [ "$CLOUDFLARED_ENABLED" = true ]; then
    AFTER_DEPS="After=network-online.target cloudflared.service"
    WANTS_DEPS="Wants=network-online.target cloudflared.service"
else
    AFTER_DEPS="After=network-online.target"
    WANTS_DEPS="Wants=network-online.target"
fi

cat > /etc/systemd/system/ai4artsed-backend.service << EOF
[Unit]
Description=AI4ArtsEd Backend Server
$AFTER_DEPS
$WANTS_DEPS

[Service]
Type=simple
User=$ACTUAL_USER
WorkingDirectory=$DEVSERVER_DIR
Environment=PORT=$BACKEND_PORT
Environment=DISABLE_API_CACHE=false
ExecStart=/usr/bin/python3 $DEVSERVER_DIR/server.py
Restart=always
RestartSec=5

# Give time for cleanup on stop
TimeoutStopSec=10

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}[✓]${NC} Backend service created"

# Enable backend
systemctl daemon-reload
systemctl enable ai4artsed-backend
echo -e "${GREEN}[✓]${NC} Backend enabled for boot"

# ============================================
# Step 3: Summary
# ============================================
echo ""
echo -e "${BLUE}[3/3]${NC} Installation complete!"
echo ""
echo -e "${GREEN}=== Summary ===${NC}"
echo ""

if [ "$CLOUDFLARED_ENABLED" = true ]; then
    echo "  Cloudflared:  enabled (starts on boot)"
    echo "                sudo systemctl start cloudflared"
    echo "                sudo systemctl status cloudflared"
else
    echo "  Cloudflared:  not configured"
fi

echo ""
echo "  Backend:      enabled (starts on boot, port $BACKEND_PORT)"
echo "                sudo systemctl start ai4artsed-backend"
echo "                sudo systemctl status ai4artsed-backend"
echo ""
echo -e "${YELLOW}Commands:${NC}"
echo "  Start now:    sudo systemctl start ai4artsed-backend"
echo "  Stop:         sudo systemctl stop ai4artsed-backend"
echo "  Logs:         sudo journalctl -u ai4artsed-backend -f"
echo "  Disable:      sudo systemctl disable ai4artsed-backend"
echo ""
echo -e "${GREEN}[✓]${NC} Server will now start automatically after reboot!"
echo ""
