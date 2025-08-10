#!/usr/bin/env bash

# AI Services Stop Script - Direkte Version
# Beendet alle AI Services zuverlässig

# Farben für die Ausgabe
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${RED}=== Stopping AI Services ===${NC}"

# 1. SwarmUI beenden
echo -e "${YELLOW}Stopping SwarmUI...${NC}"
# Finde alle SwarmUI Prozesse und beende sie
pkill -f "SwarmUI/launch-linux.sh"
pkill -f "SwarmUI.*dotnet"
pkill -f "SwarmUI"

# 2. Werkraum-Tunnel beenden
echo -e "${YELLOW}Stopping Werkraum-Tunnel...${NC}"
pkill -f "werkraum-tunnel"

# 3. Webserver beenden (Port 5000)
echo -e "${YELLOW}Stopping Webserver...${NC}"
# Finde PID auf Port 5000 und beende
if command -v lsof &> /dev/null; then
    PID=$(lsof -ti:5000)
    if [ -n "$PID" ]; then
        kill -9 $PID 2>/dev/null
    fi
fi
# Zusätzlich nach Python Flask Prozessen suchen
pkill -f "python.*server.py"
pkill -f "flask run"
pkill -f "start_webserver.sh"

# 4. ComfyUI beenden (Port 7801)
echo -e "${YELLOW}Stopping ComfyUI...${NC}"
# Finde PID auf Port 7801 und beende
if command -v lsof &> /dev/null; then
    PID=$(lsof -ti:7801)
    if [ -n "$PID" ]; then
        kill -9 $PID 2>/dev/null
    fi
fi
# Zusätzlich nach ComfyUI Prozessen suchen
pkill -f "ComfyUI.*main.py"
pkill -f "comfyui"
pkill -f "python.*--port.*7801"

# Kurz warten
sleep 2

# Verifiziere dass alles beendet wurde
echo -e "\n${YELLOW}Verifying...${NC}"
STILL_RUNNING=false

# Check SwarmUI
if pgrep -f "SwarmUI" > /dev/null; then
    echo -e "${RED}SwarmUI still running!${NC}"
    STILL_RUNNING=true
else
    echo -e "${GREEN}SwarmUI stopped${NC}"
fi

# Check Werkraum-Tunnel
if pgrep -f "werkraum-tunnel" > /dev/null; then
    echo -e "${RED}Werkraum-Tunnel still running!${NC}"
    STILL_RUNNING=true
else
    echo -e "${GREEN}Werkraum-Tunnel stopped${NC}"
fi

# Check Port 5000
if command -v lsof &> /dev/null && lsof -ti:5000 > /dev/null; then
    echo -e "${RED}Port 5000 still in use!${NC}"
    STILL_RUNNING=true
else
    echo -e "${GREEN}Port 5000 free${NC}"
fi

# Check Port 7801 (ComfyUI)
if command -v lsof &> /dev/null && lsof -ti:7801 > /dev/null; then
    echo -e "${RED}Port 7801 still in use!${NC}"
    STILL_RUNNING=true
else
    echo -e "${GREEN}Port 7801 free${NC}"
fi

if [ "$STILL_RUNNING" = true ]; then
    echo -e "\n${RED}Some services still running. Force killing...${NC}"
    pkill -9 -f "SwarmUI"
    pkill -9 -f "werkraum-tunnel"
    pkill -9 -f "ComfyUI"
    pkill -9 -f "comfyui"
    [ -n "$(lsof -ti:5000 2>/dev/null)" ] && kill -9 $(lsof -ti:5000)
    [ -n "$(lsof -ti:7801 2>/dev/null)" ] && kill -9 $(lsof -ti:7801)
fi

echo -e "\n${GREEN}All AI services stopped!${NC}"
