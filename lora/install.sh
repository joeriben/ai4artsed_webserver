#!/bin/bash
# ============================================================================
# LoRA Training Setup - Automated Installation Script
# ============================================================================
# Purpose: Upgrade Kohya-SS venv to PyTorch nightly for RTX 5090 support
# Safety:  Isolated venv - will NOT affect DevServer or system Python
# ============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# Configuration
# ============================================================================

# Auto-detect script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"
MIN_PYTORCH_VERSION="2.9.0"

# Kohya directory configuration
# Override with environment variable: KOHYA_DIR=/path/to/kohya ./install.sh
if [ -z "$KOHYA_DIR" ]; then
    # Try to auto-detect common locations
    POSSIBLE_LOCATIONS=(
        "$HOME/ai/kohya_ss_new"
        "$HOME/kohya_ss"
        "$HOME/kohya-ss"
        "$HOME/ai/kohya_ss"
        "$(dirname "$SCRIPT_DIR")/kohya_ss_new"
        "$(dirname "$SCRIPT_DIR")/kohya_ss"
    )

    for loc in "${POSSIBLE_LOCATIONS[@]}"; do
        if [ -d "$loc/venv" ]; then
            KOHYA_DIR="$loc"
            break
        fi
    done

    # If still not found, ask user
    if [ -z "$KOHYA_DIR" ] || [ ! -d "$KOHYA_DIR" ]; then
        echo -e "${YELLOW}Could not auto-detect Kohya-SS installation.${NC}"
        echo ""
        read -p "Enter path to Kohya-SS directory (e.g., /path/to/kohya_ss_new): " KOHYA_DIR
        echo ""
    fi
fi

VENV_PATH="$KOHYA_DIR/venv"

# ============================================================================
# Helper Functions
# ============================================================================

print_header() {
    echo -e "${BLUE}============================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# ============================================================================
# Pre-flight Checks
# ============================================================================

print_header "LoRA Training Setup - Pre-flight Checks"

# Check if running as root (should not be)
if [ "$EUID" -eq 0 ]; then
    print_error "Do not run this script as root!"
    print_info "Run as normal user: bash install.sh"
    exit 1
fi
print_success "Running as normal user"

# Check if Kohya directory exists
if [ ! -d "$KOHYA_DIR" ]; then
    print_error "Kohya directory not found: $KOHYA_DIR"
    print_info "Set KOHYA_DIR environment variable or install Kohya-SS first"
    print_info "Example: KOHYA_DIR=/path/to/kohya_ss ./install.sh"
    exit 1
fi
print_success "Kohya directory found: $KOHYA_DIR"

# Check if venv exists
if [ ! -d "$VENV_PATH" ]; then
    print_error "Kohya venv not found: $VENV_PATH"
    print_info "Please install Kohya-SS first"
    exit 1
fi
print_success "Kohya venv found: $VENV_PATH"

# Check if requirements.txt exists
if [ ! -f "$REQUIREMENTS_FILE" ]; then
    print_error "Requirements file not found: $REQUIREMENTS_FILE"
    exit 1
fi
print_success "Requirements file found"

# Check if nvidia-smi works (GPU detection)
if ! command -v nvidia-smi &> /dev/null; then
    print_warning "nvidia-smi not found - cannot verify GPU"
else
    GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -n 1)
    print_success "GPU detected: $GPU_NAME"

    if [[ ! "$GPU_NAME" == *"RTX 5090"* ]]; then
        print_warning "Expected RTX 5090, found: $GPU_NAME"
        print_info "PyTorch nightly installation will continue, but may not be necessary"
    fi
fi

echo ""
print_info "All pre-flight checks passed!"
echo ""

# ============================================================================
# Safety Confirmation
# ============================================================================

print_header "Safety Confirmation"

echo -e "${YELLOW}This script will upgrade PyTorch in Kohya venv ONLY.${NC}"
echo ""
echo "What will be modified:"
echo "  → $VENV_PATH/lib/python*/site-packages/"
echo ""
echo "What will NOT be affected:"
echo "  ✓ DevServer venv (if present)"
echo "  ✓ ComfyUI venv (if present)"
echo "  ✓ System Python (/usr/bin/python3)"
echo "  ✓ Other virtual environments"
echo ""
echo "Actions:"
echo "  1. Activate Kohya venv"
echo "  2. Upgrade PyTorch to 2.9.0+ nightly (cu128)"
echo "  3. Install/upgrade dependencies from requirements.txt"
echo "  4. Verify CUDA compatibility"
echo ""

read -p "Continue with installation? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_info "Installation cancelled by user"
    exit 0
fi

echo ""

# ============================================================================
# Activate Venv
# ============================================================================

print_header "Step 1: Activating Kohya Virtual Environment"

# Source the venv
source "$VENV_PATH/bin/activate"

# Verify activation
ACTIVE_PYTHON=$(which python)
EXPECTED_PYTHON="$VENV_PATH/bin/python"

if [[ "$ACTIVE_PYTHON" != "$EXPECTED_PYTHON" ]]; then
    print_error "Failed to activate correct venv!"
    print_error "Active Python: $ACTIVE_PYTHON"
    print_error "Expected: $EXPECTED_PYTHON"
    exit 1
fi

print_success "Activated: $ACTIVE_PYTHON"

# Show current Python version
PYTHON_VERSION=$(python --version 2>&1)
print_info "Python version: $PYTHON_VERSION"

# Show current PyTorch version (if installed)
if python -c "import torch" 2>/dev/null; then
    CURRENT_TORCH=$(python -c "import torch; print(torch.__version__)" 2>/dev/null)
    print_info "Current PyTorch: $CURRENT_TORCH"
else
    print_warning "PyTorch not currently installed"
    CURRENT_TORCH="not installed"
fi

echo ""

# ============================================================================
# Backup Current State
# ============================================================================

print_header "Step 2: Backing Up Current Environment"

BACKUP_FILE="$KOHYA_DIR/venv_backup_$(date +%Y%m%d_%H%M%S).txt"
pip list > "$BACKUP_FILE" 2>/dev/null || true

if [ -f "$BACKUP_FILE" ]; then
    print_success "Package list backed up to: $BACKUP_FILE"
else
    print_warning "Could not create backup (non-critical)"
fi

echo ""

# ============================================================================
# Upgrade PyTorch to Nightly
# ============================================================================

print_header "Step 3: Upgrading PyTorch to Nightly (RTX 5090 Support)"

print_info "This may take 5-10 minutes depending on internet speed..."
echo ""

# Upgrade PyTorch and torchvision to nightly
if pip install --pre torch torchvision --index-url https://download.pytorch.org/whl/nightly/cu128 --upgrade; then
    print_success "PyTorch nightly installed successfully"
else
    print_error "Failed to install PyTorch nightly"
    print_info "Check your internet connection and try again"
    exit 1
fi

# Verify new version
NEW_TORCH=$(python -c "import torch; print(torch.__version__)" 2>/dev/null)
print_success "New PyTorch version: $NEW_TORCH"

# Check if version is sufficient
if [[ "$NEW_TORCH" < "$MIN_PYTORCH_VERSION" ]]; then
    print_error "PyTorch version too old: $NEW_TORCH (need $MIN_PYTORCH_VERSION+)"
    print_info "This should not happen. Please report this issue."
    exit 1
fi

echo ""

# ============================================================================
# Install Dependencies
# ============================================================================

print_header "Step 4: Installing LoRA Training Dependencies"

print_info "Installing from: $REQUIREMENTS_FILE"
print_info "This may take 5-15 minutes..."
echo ""

if pip install -r "$REQUIREMENTS_FILE"; then
    print_success "Dependencies installed successfully"
else
    print_error "Failed to install some dependencies"
    print_warning "Some packages may have failed, but installation may still work"
    print_info "Check the output above for details"
fi

echo ""

# ============================================================================
# Verify Installation
# ============================================================================

print_header "Step 5: Verifying Installation"

# Test torch import
print_info "Testing torch import..."
if python -c "import torch" 2>/dev/null; then
    print_success "torch imports successfully"
else
    print_error "Failed to import torch"
    exit 1
fi

# Check CUDA availability
print_info "Checking CUDA availability..."
CUDA_AVAILABLE=$(python -c "import torch; print(torch.cuda.is_available())" 2>/dev/null)
if [ "$CUDA_AVAILABLE" == "True" ]; then
    print_success "CUDA is available"
else
    print_error "CUDA is NOT available - training will not work!"
    print_info "Check your CUDA installation and NVIDIA drivers"
    exit 1
fi

# Get GPU name
GPU_NAME_TORCH=$(python -c "import torch; print(torch.cuda.get_device_name(0))" 2>/dev/null)
print_success "GPU detected by PyTorch: $GPU_NAME_TORCH"

# Get compute capability (SM version)
COMPUTE_CAP=$(python -c "import torch; cap = torch.cuda.get_device_capability(0); print(f'{cap[0]}.{cap[1]}')" 2>/dev/null)
print_success "Compute capability: SM_${COMPUTE_CAP/./}"

# Check if SM_120 (RTX 5090 Blackwell)
if [[ "$COMPUTE_CAP" == "9.12" ]]; then
    print_success "RTX 5090 (Blackwell SM_120) fully supported!"
else
    print_warning "Compute capability is $COMPUTE_CAP, not 9.12 (SM_120)"
    print_info "Expected for RTX 5090. If you have a different GPU, this is normal."
fi

# Check key dependencies
print_info "Verifying key dependencies..."

check_package() {
    if python -c "import $1" 2>/dev/null; then
        VERSION=$(python -c "import $1; print($1.__version__)" 2>/dev/null || echo "unknown")
        print_success "$1 ($VERSION)"
    else
        print_error "$1 not installed"
        return 1
    fi
}

check_package "torch"
check_package "torchvision"
check_package "diffusers"
check_package "transformers"
check_package "accelerate"
check_package "peft"
check_package "bitsandbytes" || print_warning "bitsandbytes failed (try 'pip install bitsandbytes --force-reinstall')"
check_package "xformers" || print_warning "xformers failed (optional, improves speed)"

echo ""

# ============================================================================
# Test Training Capability
# ============================================================================

print_header "Step 6: Testing Training Capability"

print_info "Running quick tensor operation test..."

TEST_RESULT=$(python -c "
import torch
try:
    # Test basic GPU operation
    x = torch.randn(100, 100).cuda()
    y = torch.matmul(x, x)
    print('SUCCESS')
except Exception as e:
    print(f'FAILED: {e}')
" 2>&1)

if [[ "$TEST_RESULT" == "SUCCESS" ]]; then
    print_success "GPU tensor operations working!"
else
    print_error "GPU test failed: $TEST_RESULT"
    print_warning "Training may not work properly"
fi

echo ""

# ============================================================================
# Summary
# ============================================================================

print_header "Installation Complete!"

echo ""
echo "Summary:"
echo "  ✓ Kohya venv upgraded successfully"
echo "  ✓ PyTorch version: $NEW_TORCH"
echo "  ✓ CUDA: Available"
echo "  ✓ GPU: $GPU_NAME_TORCH"
echo "  ✓ Compute Capability: SM_${COMPUTE_CAP/./}"
echo ""
echo "What's Next:"
echo "  1. Read the README:"
echo "     less $SCRIPT_DIR/README.md"
echo ""
echo "  2. Prepare your training dataset:"
echo "     mkdir -p ~/trainingdata/yourproject/images"
echo ""
echo "  3. Train your first LoRA:"
echo "     cd $KOHYA_DIR"
echo "     source venv/bin/activate"
echo "     python sd3_train.py --config_file /path/to/config.toml"
echo ""
echo "  4. Test the trained LoRA:"
echo "     - Place .safetensors in your ComfyUI/SwarmUI Models/Lora/ folder"
echo "     - Load in ComfyUI or SwarmUI"
echo "     - Test with DevServer's sd35_large output config (if using DevServer)"
echo ""

print_info "Backup of previous environment: $BACKUP_FILE"
print_warning "DevServer and other systems were NOT affected (isolated venvs)"

echo ""
print_success "Installation complete! Happy training!"
echo ""

# Deactivate venv
deactivate
