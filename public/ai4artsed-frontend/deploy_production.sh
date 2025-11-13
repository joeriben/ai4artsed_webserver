#!/bin/bash
#
# Production Deployment Script for ai4artsed-frontend
#
# This script rebuilds the Vue.js frontend and restarts the Flask backend
# to serve the updated production build through Cloudflare Tunnel.
#
# Usage: ./deploy_production.sh
#

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "======================================"
echo "  ai4artsed Frontend Deployment"
echo "======================================"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Step 1: Build production bundle
echo -e "${YELLOW}[1/3]${NC} Building production bundle..."
npm run build

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Build completed successfully"
else
    echo -e "${RED}✗${NC} Build failed"
    exit 1
fi

# Check build output
if [ ! -d "dist" ] || [ ! -f "dist/index.html" ]; then
    echo -e "${RED}✗${NC} Build output not found"
    exit 1
fi

echo ""

# Step 2: Restart Flask backend
echo -e "${YELLOW}[2/3]${NC} Restarting Flask backend..."

# Find Flask backend process
BACKEND_PID=$(lsof -ti:17801 2>/dev/null || true)

if [ ! -z "$BACKEND_PID" ]; then
    echo "  → Stopping old backend (PID: $BACKEND_PID)..."
    kill $BACKEND_PID
    sleep 2
fi

# Start new backend
echo "  → Starting new backend..."
cd ../../devserver
python3 server.py > /tmp/backend_production.log 2>&1 &
NEW_PID=$!

# Wait for backend to start
sleep 3

# Verify backend is running
if lsof -ti:17801 > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Backend restarted (PID: $NEW_PID)"
else
    echo -e "${RED}✗${NC} Backend failed to start"
    echo "  Check logs: tail -f /tmp/backend_production.log"
    exit 1
fi

echo ""

# Step 3: Verify deployment
echo -e "${YELLOW}[3/3]${NC} Verifying deployment..."

# Test local access
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:17801/ 2>/dev/null || echo "000")

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓${NC} Local access: OK (HTTP $HTTP_CODE)"
else
    echo -e "${RED}✗${NC} Local access: FAILED (HTTP $HTTP_CODE)"
fi

# Test MIME type for JS files
MIME_TYPE=$(curl -s -I http://localhost:17801/assets/index-Bprq4S1F.js 2>/dev/null | grep -i "content-type" | cut -d' ' -f2 | tr -d '\r')

if [[ "$MIME_TYPE" == *"javascript"* ]]; then
    echo -e "${GREEN}✓${NC} MIME types: OK ($MIME_TYPE)"
else
    echo -e "${YELLOW}!${NC} MIME type: $MIME_TYPE (expected: text/javascript)"
fi

echo ""
echo "======================================"
echo -e "${GREEN}✓ Deployment Complete${NC}"
echo "======================================"
echo ""
echo "Frontend is now live at:"
echo "  • Local:  http://localhost:17801"
echo "  • Tunnel: https://lab.ai4artsed.org"
echo ""
echo "Backend logs: tail -f /tmp/backend_production.log"
echo ""
