#!/usr/bin/env bash

#===============================================================================
# AI4ArtsEd Frontend Only Startup Script
# Starts only the Vue.js development server
#===============================================================================

set -euo pipefail

# ANSI Color Codes
readonly GREEN='\033[0;32m'
readonly BLUE='\033[0;34m'
readonly RED='\033[0;31m'
readonly NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}AI4ArtsEd Frontend (Vue.js)${NC}"
echo -e "${BLUE}========================================${NC}"

# Change to frontend directory
cd "$(dirname "$0")/public/ai4artsed-frontend" || exit 1

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}✗ Node.js not found${NC}"
    exit 1
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${BLUE}Installing dependencies...${NC}"
    npm install
fi

echo -e "${GREEN}✓ Starting Vue.js dev server${NC}"
echo -e "${BLUE}Press Ctrl+C to stop${NC}"
echo ""

# Start dev server (foreground for direct output)
exec npm run dev
