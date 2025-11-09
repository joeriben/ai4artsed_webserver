#!/usr/bin/env bash

#===============================================================================
# AI4ArtsEd Backend Only Startup Script
# Starts only the Python/Flask backend on port 17801
#===============================================================================

set -euo pipefail

# ANSI Color Codes
readonly GREEN='\033[0;32m'
readonly BLUE='\033[0;34m'
readonly RED='\033[0;31m'
readonly NC='\033[0m'

readonly PORT=17801

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}AI4ArtsEd Backend Server${NC}"
echo -e "${BLUE}========================================${NC}"

# Change to devserver directory
cd "$(dirname "$0")/devserver" || exit 1

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found${NC}"
    exit 1
fi

# Kill any existing process on port
if lsof -ti:$PORT > /dev/null 2>&1; then
    echo -e "${BLUE}Stopping existing server on port $PORT...${NC}"
    lsof -ti:$PORT | xargs kill -9 2>/dev/null || true
    sleep 1
fi

echo -e "${GREEN}✓ Starting backend server on port $PORT${NC}"
echo -e "${BLUE}Press Ctrl+C to stop${NC}"
echo ""

# Start server (foreground for direct output)
exec python3 server.py
