#!/bin/bash
# Start SwarmUI (required dependency for AI4ArtsEd)

BACKEND_PORT=7801

# Get directory where this script lives (repo root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# SwarmUI is expected at ../SwarmUI relative to repo root
# (assuming structure: ai/ai4artsed_webserver/ and ai/SwarmUI/)
SWARMUI_DIR="$SCRIPT_DIR/../SwarmUI"


# Check if port is in use and terminate any process using it
echo "Checking port ${BACKEND_PORT}..."
if lsof -ti:${BACKEND_PORT} > /dev/null 2>&1; then
    echo "Port ${BACKEND_PORT} is in use. Terminating existing process..."
    lsof -ti:${BACKEND_PORT} | xargs -r kill -9
    sleep 2
    echo "✅ Process terminated."
fi

echo "=== Starting SwarmUI ==="
echo ""

# Check if SwarmUI directory exists
if [ ! -d "$SWARMUI_DIR" ]; then
    echo "❌ ERROR: SwarmUI not found at: $SWARMUI_DIR"
    echo ""
    echo "SwarmUI is required for AI4ArtsEd to function."
    echo "Please install SwarmUI or adjust the path in this script."
    exit 1
fi


cd "$SWARMUI_DIR"
echo "Working directory: $SWARMUI_DIR"
echo "Activating venv and starting SwarmUI..."
echo "Press Ctrl+C to stop"
echo ""

source ./venv/bin/activate
./launch-linux.sh
