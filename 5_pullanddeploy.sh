#!/bin/bash
# Pull latest code from main branch and deploy in production
# Automates Steps 4 & 5 from DEPLOYMENT.md

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
if [ $? -ne 0 ]; then
    echo "❌ ERROR: Failed to checkout main branch"
    exit 1
fi

git pull origin main
if [ $? -ne 0 ]; then
    echo "❌ ERROR: Failed to pull from origin main"
    exit 1
fi
echo "✅ Code updated successfully"
echo ""

# Step 5: Build frontend and restart backend
echo "🔨 Step 5a: Building frontend..."
cd "$SCRIPT_DIR/public/ai4artsed-frontend"
npm run build
if [ $? -ne 0 ]; then
    echo "❌ ERROR: Frontend build failed"
    exit 1
fi
echo "✅ Frontend built successfully"
echo ""

echo "🚀 Step 5b: Restarting production backend..."
cd "$SCRIPT_DIR"

# Check if backend is already running and kill it
BACKEND_PORT=17801
if lsof -ti:${BACKEND_PORT} > /dev/null 2>&1; then
    echo "Stopping existing backend on port ${BACKEND_PORT}..."
    lsof -ti:${BACKEND_PORT} | xargs -r kill -9
    sleep 2
    echo "✅ Existing backend stopped"
fi

echo ""
echo "✅ Deployment completed successfully!"
echo "🌐 Starting production backend..."
echo "   Verify at: https://lab.ai4artsed.org/"
echo ""
echo "Press Ctrl+C to stop the backend"
echo ""

# Start production backend (runs in foreground)
./5_start_backend_prod.sh
