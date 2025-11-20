#!/bin/bash

# AI4ArtsEd Backend Server Startup Script

echo "================================================"
echo "AI4ArtsEd Backend Server - Starting..."
echo "================================================"

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if server already running
if lsof -Pi :17801 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  Backend server already running on port 17801"
    echo "   Kill it first: pkill -f 'python3 server.py'"
    exit 1
fi

# Clear Python cache for fresh start
echo "🧹 Clearing Python bytecode cache..."
find . -type f -name "*.pyc" -delete 2>/dev/null
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# Start Backend Server
echo ""
echo "🚀 Starting Backend Server (Python/Waitress)..."
python3 -B server.py > /tmp/devserver_backend.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"
echo "   Backend URL: http://localhost:17801"
echo "   Backend Log: /tmp/devserver_backend.log"

# Wait for backend to start
sleep 2

# Check if backend started successfully
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "❌ Backend failed to start! Check log: tail -f /tmp/devserver_backend.log"
    exit 1
fi

# Success message
echo ""
echo "================================================"
echo "✅ Backend Server started successfully!"
echo "================================================"
echo ""
echo "Backend: http://localhost:17801 (PID: $BACKEND_PID)"
echo ""
echo "Log: tail -f /tmp/devserver_backend.log"
echo ""
echo "To stop: kill $BACKEND_PID"
echo "================================================"

# Monitor log
tail -f /tmp/devserver_backend.log
