#!/bin/bash
# AI4ArtsEd DevServer - Model Download Script
# Downloads all required AI models from HuggingFace
# Idempotent: Safe to re-run, skips existing files

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Default SwarmUI path
SWARMUI_PATH="${SWARMUI_PATH:-/opt/ai4artsed/SwarmUI}"

echo -e "${BLUE}=== AI4ArtsEd Model Downloader ===${NC}"
echo ""
echo "SwarmUI Path: $SWARMUI_PATH"
echo "Total download: ~48GB"
echo "Estimated time: 30-60 minutes (100Mbps)"
echo ""

# Check if SwarmUI path exists
if [ ! -d "$SWARMUI_PATH" ]; then
    echo -e "${RED}Error: SwarmUI not found at $SWARMUI_PATH${NC}"
    echo ""
    echo "Set SWARMUI_PATH environment variable or install SwarmUI first:"
    echo "  ${BLUE}export SWARMUI_PATH=/path/to/SwarmUI${NC}"
    echo "  ${BLUE}cd /opt/ai4artsed && git clone https://github.com/mcmonkeyprojects/SwarmUI.git${NC}"
    exit 1
fi

# Check if wget or aria2c is available
DOWNLOADER="wget"
if command -v aria2c >/dev/null 2>&1; then
    echo -e "${GREEN}Using aria2c for faster downloads${NC}"
    DOWNLOADER="aria2c"
fi

# Download function
download_file() {
    local url="$1"
    local output="$2"

    if [ -f "$output" ]; then
        echo -e "${GREEN}✓${NC} Already exists, skipping: $(basename $output)"
        return 0
    fi

    echo "Downloading: $(basename $output)"

    if [ "$DOWNLOADER" = "aria2c" ]; then
        aria2c -x 16 -s 16 -d "$(dirname $output)" -o "$(basename $output)" "$url"
    else
        wget -c "$url" -O "$output"
    fi

    if [ -f "$output" ]; then
        SIZE=$(du -h "$output" | cut -f1)
        echo -e "${GREEN}✓${NC} Downloaded: $(basename $output) ($SIZE)"
    else
        echo -e "${RED}✗${NC} Failed to download: $(basename $output)"
        return 1
    fi
}

# Create directories
echo -e "${BLUE}[1/5]${NC} Creating directories..."
mkdir -p "${SWARMUI_PATH}/Models/Stable-Diffusion/OfficialStableDiffusion"
mkdir -p "${SWARMUI_PATH}/dlbackend/ComfyUI/models/clip"
mkdir -p "${SWARMUI_PATH}/dlbackend/ComfyUI/models/checkpoints"
echo -e "${GREEN}✓${NC} Directories ready"
echo ""

# Download SD3.5 Large
echo -e "${BLUE}[2/5]${NC} Downloading SD3.5 Large (16GB)..."
cd "${SWARMUI_PATH}/Models/Stable-Diffusion/OfficialStableDiffusion"
download_file \
    "https://huggingface.co/stabilityai/stable-diffusion-3.5-large/resolve/main/sd3.5_large.safetensors" \
    "sd3.5_large.safetensors"
echo ""

# Download CLIP encoders
echo -e "${BLUE}[3/5]${NC} Downloading CLIP encoders (6GB)..."
cd "${SWARMUI_PATH}/dlbackend/ComfyUI/models/clip"

download_file \
    "https://huggingface.co/stabilityai/stable-diffusion-3.5-large/resolve/main/clip_g.safetensors" \
    "clip_g.safetensors"

download_file \
    "https://huggingface.co/stabilityai/stable-diffusion-3.5-large/resolve/main/t5xxl_enconly.safetensors" \
    "t5xxl_enconly.safetensors"

download_file \
    "https://huggingface.co/mcmonkey/google_t5-v1_1-xxl_encoderonly/resolve/main/t5xxl_fp16.safetensors" \
    "t5xxl_fp16.safetensors"
echo ""

# Download LTX-Video
echo -e "${BLUE}[4/5]${NC} Downloading LTX-Video (15GB)..."
cd "${SWARMUI_PATH}/dlbackend/ComfyUI/models/checkpoints"
download_file \
    "https://huggingface.co/Lightricks/LTX-Video/resolve/main/ltxv-13b-0.9.7-distilled-fp8.safetensors" \
    "ltxv-13b-0.9.7-distilled-fp8.safetensors"
echo ""

# Create symlink
echo -e "${BLUE}[5/5]${NC} Creating symlink..."
cd "${SWARMUI_PATH}/dlbackend/ComfyUI/models/checkpoints"
if [ ! -L "OfficialStableDiffusion" ]; then
    ln -sf ../../../Models/Stable-Diffusion/OfficialStableDiffusion OfficialStableDiffusion
    echo -e "${GREEN}✓${NC} Symlink created"
else
    echo -e "${GREEN}✓${NC} Symlink already exists"
fi
echo ""

# Verification
echo "==================================="
echo -e "${BLUE}Verification:${NC}"
echo "==================================="

# Check all models
MODELS_OK=true

check_model() {
    local path="$1"
    local name="$2"

    if [ -f "$path" ]; then
        SIZE=$(du -h "$path" | cut -f1)
        echo -e "${GREEN}✓${NC} $name ($SIZE)"
    else
        echo -e "${RED}✗${NC} $name (missing)"
        MODELS_OK=false
    fi
}

check_model "${SWARMUI_PATH}/Models/Stable-Diffusion/OfficialStableDiffusion/sd3.5_large.safetensors" "SD3.5 Large"
check_model "${SWARMUI_PATH}/dlbackend/ComfyUI/models/clip/clip_g.safetensors" "CLIP-G"
check_model "${SWARMUI_PATH}/dlbackend/ComfyUI/models/clip/t5xxl_enconly.safetensors" "T5-XXL (SD3.5)"
check_model "${SWARMUI_PATH}/dlbackend/ComfyUI/models/clip/t5xxl_fp16.safetensors" "T5-XXL (Video)"
check_model "${SWARMUI_PATH}/dlbackend/ComfyUI/models/checkpoints/ltxv-13b-0.9.7-distilled-fp8.safetensors" "LTX-Video"

# Check symlink
if [ -L "${SWARMUI_PATH}/dlbackend/ComfyUI/models/checkpoints/OfficialStableDiffusion" ]; then
    echo -e "${GREEN}✓${NC} Symlink (OfficialStableDiffusion)"
else
    echo -e "${RED}✗${NC} Symlink missing"
    MODELS_OK=false
fi

echo ""

if $MODELS_OK; then
    echo -e "${GREEN}=== Download Complete! ===${NC}"
    echo ""
    echo "All models downloaded successfully."
    echo ""
    echo "Total size on disk:"
    du -sh "${SWARMUI_PATH}/Models" "${SWARMUI_PATH}/dlbackend/ComfyUI/models"
    echo ""
    echo "Next steps:"
    echo "  1. Start SwarmUI: cd $SWARMUI_PATH && ./launch-linux.sh"
    echo "  2. Continue with AI4ArtsEd installation"
    echo ""
else
    echo -e "${RED}=== Download Failed ===${NC}"
    echo ""
    echo "Some models failed to download. Please check errors above."
    echo "You can re-run this script to resume downloads."
    echo ""
    exit 1
fi
