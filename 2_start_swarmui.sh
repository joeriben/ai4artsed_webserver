#!/bin/bash
# Start SwarmUI (required dependency for AI4ArtsEd)

# Keep window open on error
trap 'echo ""; echo "❌ Script failed! Press any key to close..."; read -n 1 -s -r' ERR

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
    echo "SwarmUI is HIGHLY recommended for AI4ArtsEd."
    echo "Please install SwarmUI or adjust the path in this script."
    exit 1
fi


cd "$SWARMUI_DIR"
echo "Working directory: $SWARMUI_DIR"
echo "Activating venv and starting SwarmUI..."
echo "Press Ctrl+C to stop"
echo ""

# === Output Cleanup ===
# DevServer exportiert nach /export, daher sind SwarmUI/ComfyUI Outputs redundant
echo "========================================"
echo "Cleaning up redundant output folders in dlbackend/ComfyUI..."
echo "========================================"

# ComfyUI Output
if [ -d "./dlbackend/ComfyUI/output" ] && [ "$(ls -A ./dlbackend/ComfyUI/output 2>/dev/null)" ]; then
    count_comfy=$(find ./dlbackend/ComfyUI/output -type f 2>/dev/null | wc -l)
    echo "ComfyUI Output: $count_comfy files"
    rm -rf ./dlbackend/ComfyUI/output/*
    echo "  -> Deleted"
else
    echo "ComfyUI Output: empty"
fi

echo "========================================"
echo ""

source ./venv/bin/activate

# Remove error trap - allow normal server exit without "Script failed" message
trap - ERR

# Start SwarmUI without opening browser (--launch_mode none)
./launch-linux.sh --launch_mode none
