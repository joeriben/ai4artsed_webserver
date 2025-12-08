#!/bin/bash
# Start Flask backend in foreground (visible terminal output)
# PRODUCTION backend on port 17801 (for cloudflared tunnel)

BACKEND_PORT=17801

# Get directory where this script lives
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Safety check: Only run from 'production' directory
if [[ ! "$SCRIPT_DIR" =~ "production" ]]; then
    echo "❌ ERROR: This production script can only be run from a directory containing 'production' in its path."
    echo "   Current directory: $SCRIPT_DIR"
    echo "   Expected: Path must contain 'production' (e.g., ~/ai/ai4artsed_production)"
    exit 1
fi

echo "=== AI4ArtsEd Backend (Production) ==="
echo ""

# Check if port is in use and terminate any process using it
echo "Checking port ${BACKEND_PORT}..."
if lsof -ti:${BACKEND_PORT} > /dev/null 2>&1; then
    echo "Port ${BACKEND_PORT} is in use. Terminating existing process..."
    lsof -ti:${BACKEND_PORT} | xargs -r kill -9
    sleep 2
    echo "✅ Process terminated."
fi

# Move to devserver directory
cd "$SCRIPT_DIR/devserver"

# Clean Python cache
echo "Cleaning Python cache..."
rm -rf my_app/__pycache__ my_app/*/__pycache__ schemas/__pycache__ schemas/*/__pycache__

echo ""
echo "Starting Flask backend (PRODUCTION) on http://0.0.0.0:${BACKEND_PORT}"
echo "Working directory: $SCRIPT_DIR/devserver"
echo "Press Ctrl+C to stop"
echo ""

# Override PORT via environment variable
export PORT=17801
python3 server.py
