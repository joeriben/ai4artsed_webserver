#!/bin/bash

# AI4ArtsEd Frontend Server Startup Script

echo "================================================"
echo "AI4ArtsEd Frontend Server - Starting..."
echo "================================================"

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Kill any process using port 5173
echo "🧹 Checking for processes using port 5173..."
PORT_PID=$(lsof -ti :5173)
if [ ! -z "$PORT_PID" ]; then
    echo "   Found process on port 5173 (PID: $PORT_PID), killing it..."
    kill -9 $PORT_PID
    sleep 2
    echo "   ✓ Port 5173 freed"
else
    echo "   Port 5173 is free"
fi

# Double-check: Kill any remaining Vite processes
if pgrep -f 'vite' > /dev/null 2>&1; then
    echo "   Cleaning up remaining Vite processes..."
    pkill -9 -f 'vite'
    sleep 1
fi

# Start Frontend Server
echo ""
echo "🎨 Starting Frontend Server (Vue/Vite)..."
npm run dev > /tmp/devserver_frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"
echo "   Frontend URL: http://localhost:5173"
echo "   Frontend Log: /tmp/devserver_frontend.log"

# Wait for frontend to start
sleep 3

# Check if frontend started successfully
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo "❌ Frontend failed to start! Check log: tail -f /tmp/devserver_frontend.log"
    exit 1
fi

# Success message
echo ""
echo "================================================"
echo "✅ Frontend Server started successfully!"
echo "================================================"
echo ""
echo "Frontend: http://localhost:5173 (PID: $FRONTEND_PID)"
echo ""
echo "Log: tail -f /tmp/devserver_frontend.log"
echo ""
echo "To stop: kill $FRONTEND_PID"
echo "================================================"

# Monitor log
tail -f /tmp/devserver_frontend.log
