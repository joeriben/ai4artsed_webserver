#!/bin/bash
# Start SwarmUI (required dependency for AI4ArtsEd)

# Get directory where this script lives (repo root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# SwarmUI is expected at ../SwarmUI relative to repo root
# (assuming structure: ai/ai4artsed_webserver/ and ai/SwarmUI/)
SWARMUI_DIR="$SCRIPT_DIR/../SwarmUI"

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

# Check if already running
if lsof -ti:7801 > /dev/null 2>&1; then
    echo "⚠️  SwarmUI appears to be already running on port 7801"
    echo "   To stop: lsof -ti:7801 | xargs kill -9"
    exit 1
fi

cd "$SWARMUI_DIR"
echo "Working directory: $SWARMUI_DIR"
echo "Activating venv and starting SwarmUI..."
echo "Press Ctrl+C to stop"
echo ""

source ./venv/bin/activate
./launch-linux.sh
