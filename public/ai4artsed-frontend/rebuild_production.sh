#!/bin/bash
# Rebuild and reload production frontend for lab.ai4artsed.org

set -e

echo "=== AI4ArtsEd Lab Frontend - Production Rebuild ==="
echo ""
echo "Working directory: $(pwd)"
echo "Time: $(date)"
echo ""

# Check if in correct directory
if [ ! -f "package.json" ]; then
    echo "ERROR: Not in frontend directory!"
    exit 1
fi

# Build
echo "[1/2] Building production version..."
npm run build

# Reload service
echo ""
echo "[2/2] Reloading lab-frontend service..."
sudo systemctl reload-or-restart lab-frontend

# Wait and check status
echo ""
echo "Waiting 3 seconds..."
sleep 3

echo ""
echo "=== Service Status ==="
sudo systemctl status lab-frontend --no-pager -l | head -20

echo ""
echo "=== Testing Port 5174 ==="
curl -I http://localhost:5174 2>&1 | head -5

echo ""
echo "=== Done ==="
echo "lab.ai4artsed.org should now serve the new build"
