#!/bin/bash

# AI4ArtsEd DevServer Startup Script
# Starts both Backend (Python/Waitress) and Frontend (Vue/Vite)

echo "================================================"
echo "AI4ArtsEd DevServer - Starting..."
echo "================================================"

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Kill any existing servers
echo "🧹 Checking for running servers..."

# Check and kill Backend
if pgrep -f 'python3.*server.py' > /dev/null 2>&1; then
    echo "   Found existing Backend processes, stopping them..."
    pkill -f 'python3.*server.py'
    sleep 1
    echo "   ✓ Backend stopped"
else
    echo "   No existing Backend processes found"
fi

# Check and kill Frontend
if pgrep -f 'vite' > /dev/null 2>&1; then
    echo "   Found existing Vite processes, stopping them..."
    pkill -f 'vite'
    sleep 2
    echo "   ✓ Frontend stopped"
else
    echo "   No existing Vite processes found"
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

# Start Frontend Server (Vue/Vite)
echo ""
echo "🎨 Starting Frontend Server (Vue/Vite)..."
cd ../public/ai4artsed-frontend
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
    echo "   Stopping backend..."
    kill $BACKEND_PID
    exit 1
fi

# Success message
echo ""
echo "================================================"
echo "✅ DevServer started successfully!"
echo "================================================"
echo ""
echo "Backend:  http://localhost:17801 (PID: $BACKEND_PID)"
echo "Frontend: http://localhost:5173   (PID: $FRONTEND_PID)"
echo ""
echo "Logs:"
echo "  Backend:  tail -f /tmp/devserver_backend.log"
echo "  Frontend: tail -f /tmp/devserver_frontend.log"
echo ""
echo "To stop:"
echo "  Backend:  kill $BACKEND_PID"
echo "  Frontend: kill $FRONTEND_PID"
echo "  Both:     pkill -f 'python3 server.py' && pkill -f 'vite'"
echo ""
echo "Press Ctrl+C to stop monitoring (servers will keep running)"
echo "================================================"

# Monitor both logs
tail -f /tmp/devserver_backend.log /tmp/devserver_frontend.log
