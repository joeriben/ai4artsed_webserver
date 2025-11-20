#!/bin/bash
# Start Flask backend in foreground (visible terminal output)

cd /home/joerissen/ai/ai4artsed_webserver/devserver
rm -rf my_app/__pycache__ my_app/*/__pycache__

echo "Starting Flask backend on http://0.0.0.0:17801"
echo "Press Ctrl+C to stop"
echo ""

python3 server.py
