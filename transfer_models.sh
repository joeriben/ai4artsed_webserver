#!/bin/bash
# AI4ArtsEd DevServer - Model Transfer Script
# Transfers AI models from source server (e.g., fedora) to target server (e.g., corsair)
# Faster than downloading from HuggingFace (LAN transfer)

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Default paths
DEFAULT_SWARMUI_PATH="/opt/ai4artsed/SwarmUI"
SOURCE_SERVER=""
DRY_RUN=false

# Usage
usage() {
    cat << EOF
AI4ArtsEd Model Transfer Script

Usage: $0 --source USER@HOST [OPTIONS]

Required:
  --source USER@HOST    Source server to transfer from (e.g., ai4artsed@fedora)

Options:
  --swarmui PATH        SwarmUI installation path (default: /opt/ai4artsed/SwarmUI)
  --dry-run             Show what would be transferred without actually doing it
  --help                Show this help message

Examples:
  # Transfer from fedora to current machine
  $0 --source ai4artsed@fedora

  # Custom SwarmUI path
  $0 --source ai4artsed@fedora --swarmui /custom/path/SwarmUI

  # Dry run to see what will be transferred
  $0 --source ai4artsed@fedora --dry-run

Requirements:
  - SSH access to source server (key-based auth recommended)
  - rsync installed on both machines
  - SwarmUI directory structure exists on target

EOF
    exit 1
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --source)
            SOURCE_SERVER="$2"
            shift 2
            ;;
        --swarmui)
            DEFAULT_SWARMUI_PATH="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --help)
            usage
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            usage
            ;;
    esac
done

# Validate arguments
if [ -z "$SOURCE_SERVER" ]; then
    echo -e "${RED}Error: --source is required${NC}"
    echo ""
    usage
fi

echo -e "${BLUE}=== AI4ArtsEd Model Transfer ===${NC}"
echo ""
echo "Source: $SOURCE_SERVER"
echo "Target: $(hostname)"
echo "SwarmUI Path: $DEFAULT_SWARMUI_PATH"
if $DRY_RUN; then
    echo -e "${YELLOW}Mode: DRY RUN (no actual transfer)${NC}"
fi
echo ""

# Check if SSH works
echo -e "${BLUE}[Check]${NC} Testing SSH connection..."
if ssh -o BatchMode=yes -o ConnectTimeout=5 "$SOURCE_SERVER" "echo 'SSH OK'" >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} SSH connection successful"
else
    echo -e "${RED}✗${NC} SSH connection failed"
    echo ""
    echo "Please ensure:"
    echo "  1. Source server is reachable"
    echo "  2. SSH key-based authentication is set up:"
    echo "     ${BLUE}ssh-keygen -t ed25519${NC}"
    echo "     ${BLUE}ssh-copy-id $SOURCE_SERVER${NC}"
    echo ""
    exit 1
fi

# Check if rsync is available
echo -e "${BLUE}[Check]${NC} Checking rsync..."
if ! command -v rsync >/dev/null 2>&1; then
    echo -e "${RED}✗${NC} rsync not found. Please install:"
    echo "  Ubuntu/Debian: ${BLUE}sudo apt install rsync${NC}"
    echo "  Fedora: ${BLUE}sudo dnf install rsync${NC}"
    echo "  Arch: ${BLUE}sudo pacman -S rsync${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} rsync available"

# Check source paths exist
echo -e "${BLUE}[Check]${NC} Verifying source paths..."
SOURCE_SWARMUI="${SOURCE_SERVER}:${DEFAULT_SWARMUI_PATH}"

if ! ssh "$SOURCE_SERVER" "test -d $DEFAULT_SWARMUI_PATH" 2>/dev/null; then
    echo -e "${RED}✗${NC} SwarmUI not found on source at $DEFAULT_SWARMUI_PATH"
    exit 1
fi
echo -e "${GREEN}✓${NC} Source paths verified"

# Create target directories
echo -e "${BLUE}[Prepare]${NC} Creating target directories..."

RSYNC_OPTS="-avz --progress"
if $DRY_RUN; then
    RSYNC_OPTS="$RSYNC_OPTS --dry-run"
fi

mkdir -p "$DEFAULT_SWARMUI_PATH/Models/Stable-Diffusion/OfficialStableDiffusion"
mkdir -p "$DEFAULT_SWARMUI_PATH/dlbackend/ComfyUI/models/clip"
mkdir -p "$DEFAULT_SWARMUI_PATH/dlbackend/ComfyUI/models/checkpoints"

echo -e "${GREEN}✓${NC} Target directories ready"
echo ""

# Transfer SD3.5 Large model
echo -e "${BLUE}[1/4]${NC} Transferring SD3.5 Large model (~16GB)..."
rsync $RSYNC_OPTS \
    "${SOURCE_SERVER}:${DEFAULT_SWARMUI_PATH}/Models/Stable-Diffusion/OfficialStableDiffusion/sd3.5_large.safetensors" \
    "$DEFAULT_SWARMUI_PATH/Models/Stable-Diffusion/OfficialStableDiffusion/" \
    2>&1 || echo -e "${YELLOW}⚠${NC} sd3.5_large.safetensors not found on source (might already be on target)"

echo ""

# Transfer CLIP encoders
echo -e "${BLUE}[2/4]${NC} Transferring CLIP encoders (~6GB)..."
rsync $RSYNC_OPTS \
    "${SOURCE_SERVER}:${DEFAULT_SWARMUI_PATH}/dlbackend/ComfyUI/models/clip/clip_g.safetensors" \
    "${SOURCE_SERVER}:${DEFAULT_SWARMUI_PATH}/dlbackend/ComfyUI/models/clip/t5xxl_enconly.safetensors" \
    "$DEFAULT_SWARMUI_PATH/dlbackend/ComfyUI/models/clip/" \
    2>&1 || echo -e "${YELLOW}⚠${NC} Some CLIP models not found on source"

echo ""

# Transfer T5 encoder for video
echo -e "${BLUE}[3/4]${NC} Transferring T5 encoder for video (~11GB)..."
rsync $RSYNC_OPTS \
    "${SOURCE_SERVER}:${DEFAULT_SWARMUI_PATH}/dlbackend/ComfyUI/models/clip/t5xxl_fp16.safetensors" \
    "$DEFAULT_SWARMUI_PATH/dlbackend/ComfyUI/models/clip/" \
    2>&1 || echo -e "${YELLOW}⚠${NC} t5xxl_fp16.safetensors not found on source"

echo ""

# Transfer LTX-Video model
echo -e "${BLUE}[4/4]${NC} Transferring LTX-Video model (~15GB)..."
rsync $RSYNC_OPTS \
    "${SOURCE_SERVER}:${DEFAULT_SWARMUI_PATH}/dlbackend/ComfyUI/models/checkpoints/ltxv-13b-0.9.7-distilled-fp8.safetensors" \
    "$DEFAULT_SWARMUI_PATH/dlbackend/ComfyUI/models/checkpoints/" \
    2>&1 || echo -e "${YELLOW}⚠${NC} LTX-Video model not found on source"

echo ""

# Create symlink if not in dry-run mode
if ! $DRY_RUN; then
    echo -e "${BLUE}[Symlink]${NC} Creating symlink for SD3.5 access..."
    cd "$DEFAULT_SWARMUI_PATH/dlbackend/ComfyUI/models/checkpoints"
    if [ ! -L "OfficialStableDiffusion" ]; then
        ln -sf ../../../Models/Stable-Diffusion/OfficialStableDiffusion OfficialStableDiffusion
        echo -e "${GREEN}✓${NC} Symlink created"
    else
        echo -e "${GREEN}✓${NC} Symlink already exists"
    fi
fi

# Verification
if ! $DRY_RUN; then
    echo ""
    echo -e "${BLUE}[Verify]${NC} Checking transferred models..."

    MODELS_OK=true

    # Check each model
    if [ -f "$DEFAULT_SWARMUI_PATH/Models/Stable-Diffusion/OfficialStableDiffusion/sd3.5_large.safetensors" ]; then
        SIZE=$(du -h "$DEFAULT_SWARMUI_PATH/Models/Stable-Diffusion/OfficialStableDiffusion/sd3.5_large.safetensors" | cut -f1)
        echo -e "${GREEN}✓${NC} sd3.5_large.safetensors ($SIZE)"
    else
        echo -e "${RED}✗${NC} sd3.5_large.safetensors missing"
        MODELS_OK=false
    fi

    if [ -f "$DEFAULT_SWARMUI_PATH/dlbackend/ComfyUI/models/clip/clip_g.safetensors" ]; then
        SIZE=$(du -h "$DEFAULT_SWARMUI_PATH/dlbackend/ComfyUI/models/clip/clip_g.safetensors" | cut -f1)
        echo -e "${GREEN}✓${NC} clip_g.safetensors ($SIZE)"
    else
        echo -e "${RED}✗${NC} clip_g.safetensors missing"
        MODELS_OK=false
    fi

    if [ -f "$DEFAULT_SWARMUI_PATH/dlbackend/ComfyUI/models/clip/t5xxl_enconly.safetensors" ]; then
        SIZE=$(du -h "$DEFAULT_SWARMUI_PATH/dlbackend/ComfyUI/models/clip/t5xxl_enconly.safetensors" | cut -f1)
        echo -e "${GREEN}✓${NC} t5xxl_enconly.safetensors ($SIZE)"
    else
        echo -e "${RED}✗${NC} t5xxl_enconly.safetensors missing"
        MODELS_OK=false
    fi

    if [ -f "$DEFAULT_SWARMUI_PATH/dlbackend/ComfyUI/models/clip/t5xxl_fp16.safetensors" ]; then
        SIZE=$(du -h "$DEFAULT_SWARMUI_PATH/dlbackend/ComfyUI/models/clip/t5xxl_fp16.safetensors" | cut -f1)
        echo -e "${GREEN}✓${NC} t5xxl_fp16.safetensors ($SIZE)"
    else
        echo -e "${YELLOW}⚠${NC} t5xxl_fp16.safetensors missing (optional for video)"
    fi

    if [ -f "$DEFAULT_SWARMUI_PATH/dlbackend/ComfyUI/models/checkpoints/ltxv-13b-0.9.7-distilled-fp8.safetensors" ]; then
        SIZE=$(du -h "$DEFAULT_SWARMUI_PATH/dlbackend/ComfyUI/models/checkpoints/ltxv-13b-0.9.7-distilled-fp8.safetensors" | cut -f1)
        echo -e "${GREEN}✓${NC} ltxv-13b-0.9.7-distilled-fp8.safetensors ($SIZE)"
    else
        echo -e "${YELLOW}⚠${NC} LTX-Video model missing (optional for video)"
    fi

    echo ""

    if $MODELS_OK; then
        echo -e "${GREEN}✓ Model transfer complete!${NC}"
        echo ""
        echo "All essential models transferred successfully."
        echo "SwarmUI can now be started with these models."
    else
        echo -e "${YELLOW}⚠ Transfer completed with warnings${NC}"
        echo ""
        echo "Some models could not be transferred."
        echo "You may need to download them manually using download_models.sh"
    fi
else
    echo -e "${YELLOW}Dry run completed. No files were transferred.${NC}"
fi

echo ""
echo "Next steps:"
echo "  1. Start SwarmUI: cd $DEFAULT_SWARMUI_PATH && ./launch-linux.sh"
echo "  2. Continue with AI4ArtsEd installation"
echo ""
