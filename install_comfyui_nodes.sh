#!/bin/bash
# AI4ArtsEd - Automated ComfyUI Custom Nodes Installation
# Installs all required ComfyUI custom nodes for AI4ArtsEd

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Default SwarmUI path (can be overridden)
SWARMUI_PATH="${SWARMUI_PATH:-/opt/ai4artsed/SwarmUI}"

echo -e "${BLUE}=== AI4ArtsEd - ComfyUI Custom Nodes Installer ===${NC}"
echo ""
echo "SwarmUI Path: $SWARMUI_PATH"
echo ""

# Check if SwarmUI exists
if [ ! -d "$SWARMUI_PATH" ]; then
    echo -e "${RED}[✗]${NC} SwarmUI not found at: $SWARMUI_PATH"
    echo ""
    echo "Set SWARMUI_PATH environment variable or install SwarmUI first:"
    echo "  ${BLUE}export SWARMUI_PATH=/path/to/SwarmUI${NC}"
    exit 1
fi

CUSTOM_NODES_DIR="$SWARMUI_PATH/dlbackend/ComfyUI/custom_nodes"

if [ ! -d "$CUSTOM_NODES_DIR" ]; then
    echo -e "${RED}[✗]${NC} ComfyUI custom_nodes directory not found"
    echo "Expected: $CUSTOM_NODES_DIR"
    exit 1
fi

echo -e "${GREEN}[✓]${NC} ComfyUI custom_nodes directory found"
echo ""

cd "$CUSTOM_NODES_DIR"

# Activate SwarmUI venv
VENV_PATH="$SWARMUI_PATH/venv"
if [ -f "$VENV_PATH/bin/activate" ]; then
    echo -e "${BLUE}[Activating]${NC} SwarmUI virtual environment..."
    source "$VENV_PATH/bin/activate"
    echo -e "${GREEN}[✓]${NC} Virtual environment activated"
else
    echo -e "${YELLOW}[⚠]${NC} SwarmUI venv not found, using system Python"
fi

echo ""

# Install Node 1: ComfyUI-LTXVideo
echo -e "${BLUE}[1/3]${NC} Installing ComfyUI-LTXVideo (Video Generation)..."
if [ -d "ComfyUI-LTXVideo" ]; then
    echo -e "${YELLOW}[⚠]${NC} ComfyUI-LTXVideo already exists, updating..."
    cd ComfyUI-LTXVideo
    git pull
    cd ..
else
    git clone https://github.com/Lightricks/ComfyUI-LTXVideo.git
fi

cd ComfyUI-LTXVideo
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}[✓]${NC} ComfyUI-LTXVideo installed"
else
    echo -e "${YELLOW}[⚠]${NC} No requirements.txt found, skipping dependencies"
fi
cd ..

echo ""

# Install Node 2: ai4artsed_comfyui
echo -e "${BLUE}[2/3]${NC} Installing ai4artsed_comfyui (Pedagogical Nodes)..."
if [ -d "ai4artsed_comfyui" ]; then
    echo -e "${YELLOW}[⚠]${NC} ai4artsed_comfyui already exists, updating..."
    cd ai4artsed_comfyui
    git pull
    cd ..
else
    git clone https://github.com/joeriben/ai4artsed_comfyui_nodes.git ai4artsed_comfyui
fi

cd ai4artsed_comfyui
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}[✓]${NC} ai4artsed_comfyui installed"
else
    echo -e "${YELLOW}[⚠]${NC} No requirements.txt found, skipping dependencies"
fi
cd ..

echo ""

# Install Node 3: comfyui-sound-lab
echo -e "${BLUE}[3/3]${NC} Installing comfyui-sound-lab (Audio Generation)..."
if [ -d "comfyui-sound-lab" ]; then
    echo -e "${YELLOW}[⚠]${NC} comfyui-sound-lab already exists, updating..."
    cd comfyui-sound-lab
    git pull
    cd ..
else
    git clone https://github.com/MixLabPro/comfyui-sound-lab.git
fi

cd comfyui-sound-lab
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt || echo -e "${YELLOW}[⚠]${NC} Some dependencies failed (flash-attention is optional)"
    echo -e "${GREEN}[✓]${NC} comfyui-sound-lab installed"
else
    echo -e "${YELLOW}[⚠]${NC} No requirements.txt found, skipping dependencies"
fi
cd ..

# Deactivate venv if we activated it
if [ -f "$VENV_PATH/bin/activate" ]; then
    deactivate
fi

echo ""
echo -e "${GREEN}[✓]${NC} All custom nodes installed!"
echo ""
echo "Installed nodes:"
ls -1 "$CUSTOM_NODES_DIR" | grep -E "ComfyUI-LTXVideo|ai4artsed_comfyui|comfyui-sound-lab"
echo ""
echo "Next steps:"
echo "  1. Restart SwarmUI"
echo "  2. Check ComfyUI can load the nodes"
echo ""
