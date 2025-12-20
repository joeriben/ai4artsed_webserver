#!/bin/bash
# Pull latest code from main branch and deploy in production
# Automates Steps 4 & 5 from DEPLOYMENT.md

# Ensure script runs in a terminal window
if [ ! -t 0 ]; then
    # Not running in terminal, launch in one
    gnome-terminal -- bash -c "$0; exec bash" || xterm -e "$0; exec bash" || konsole -e "$0; exec bash"
    exit 0
fi

# Error handler - pause on any error
trap 'echo ""; echo "❌ ERROR: Command failed! (exit code: $?)"; echo ""; read -n 1 -s -r -p "Press any key to close..."; exit 1' ERR
set -e  # Exit on error

# Get directory where this script lives
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Safety check: Only run from 'production' directory
if [[ ! "$SCRIPT_DIR" =~ "production" ]]; then
    echo "❌ ERROR: This production deployment script can only be run from a directory containing 'production' in its path."
    echo "   Current directory: $SCRIPT_DIR"
    echo "   Expected: Path must contain 'production' (e.g., ~/ai/ai4artsed_production)"
    exit 1
fi

echo "=== AI4ArtsEd Production Deployment ==="
echo ""

# Step 4: Pull latest code from main
echo "📥 Step 4: Pulling latest code from main branch..."
git checkout main
git pull origin main
echo "✅ Code updated successfully"
echo ""

# Step 5: Build frontend
echo "🔨 Step 5a: Building frontend..."
cd "$SCRIPT_DIR/public/ai4artsed-frontend"

# Check if 'install' script exists in package.json, run it only if present
if npm run | grep -q "^\s*install$"; then
    echo "Running custom install script..."
    npm run install
fi

# Always run build
npm run build
echo "✅ Frontend built successfully"
echo ""

# Step 6: Restart backend
read -p "Restart Backend? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Aborted by user"
    echo "In order to use the new deployment, manually restart the backend from the _production folder using 5_start_backend_prod.sh"
    exit 1
fi

./5_start_backend_prod.sh

echo ""
echo "✅ Deployment completed!"
echo ""
echo "================================================"
read -n 1 -s -r -p "Press any key to close this window..."
echo ""
exec bash
