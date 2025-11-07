# LoRA Training Functionality Test Plan

**Date:** 2025-11-07
**Purpose:** Verify LoRA training works before frontend implementation
**Status:** In Progress

---

## Test Objectives

1. ✅ Verify Kohya-SS installation state
2. ⏳ Test PyTorch nightly upgrade (isolated)
3. ⏳ Run minimal SD 3.5 LoRA training
4. ⏳ Verify output LoRA file integrity
5. ⏳ Test LoRA loading in ComfyUI
6. ⏳ Document results and recommendations

---

## Test Environment

**Hardware:**
- GPU: RTX 5090 (22GB VRAM)
- CUDA: 12.8 (cu128)

**Software:**
- Kohya-SS: `/home/joerissen/ai/kohya_ss_new`
- Python: 3.11.14 (Kohya venv)
- Current PyTorch: 2.7.0+cu128
- Target PyTorch: 2.9.0+ nightly

**Test Dataset:**
- Location: `/home/joerissen/ai/ai4artsed_webserver/archive/lora_experiment/lora_training_images/`
- Images: 16 JPG files (768x768)
- Prepared: Yes (lora_001.jpg through lora_016.jpg)

---

## Test 1: Environment Verification

### Commands:
```bash
# Check Kohya installation
ls -la /home/joerissen/ai/kohya_ss_new/venv

# Check current PyTorch
cd /home/joerissen/ai/kohya_ss_new
source venv/bin/activate
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA: {torch.cuda.is_available()}')"
deactivate
```

### Expected Results:
- Kohya venv exists
- PyTorch 2.7.0+cu128 installed
- CUDA available: True

### Actual Results:
_To be filled during test execution_

---

## Test 2: PyTorch Nightly Upgrade

### Safety Checks:
- ✅ Kohya venv is isolated (won't affect DevServer)
- ✅ Backup created before upgrade
- ✅ Can roll back if needed

### Commands:
```bash
cd /home/joerissen/ai/kohya_ss_new
source venv/bin/activate

# Backup current environment
pip list > venv_backup_before_test_$(date +%Y%m%d_%H%M%S).txt

# Upgrade to nightly
pip install --pre torch torchvision --index-url https://download.pytorch.org/whl/nightly/cu128 --upgrade

# Verify
python -c "import torch; print(f'PyTorch: {torch.__version__}'); cap = torch.cuda.get_device_capability(0); print(f'Compute Cap: SM_{cap[0]}{cap[1]}')"

deactivate
```

### Expected Results:
- PyTorch version: 2.9.0.dev or later
- CUDA available: True
- Compute capability: SM_912 (RTX 5090 Blackwell)

### Rollback Plan:
```bash
pip install torch==2.7.0+cu128 torchvision==0.22.0+cu128 --index-url https://download.pytorch.org/whl/cu128
```

### Actual Results:
_To be filled during test execution_

---

## Test 3: Dependencies Installation

### Commands:
```bash
cd /home/joerissen/ai/kohya_ss_new
source venv/bin/activate

# Install minimal dependencies for testing
pip install diffusers>=0.31.0 transformers>=4.45.0 accelerate>=0.34.0 peft>=0.13.0 safetensors>=0.4.5

# Verify imports
python -c "import diffusers, transformers, accelerate, peft, safetensors; print('All imports OK')"

deactivate
```

### Expected Results:
- All packages install without errors
- All imports successful

### Actual Results:
_To be filled during test execution_

---

## Test 4: Minimal Training Run

### Test Configuration:
- **Model:** SD 3.5 Large (`sd3.5_large.safetensors`)
- **Dataset:** 16 test images
- **Epochs:** 2 (minimal test)
- **Rank:** 16 (smaller for speed)
- **Resolution:** 768x768 (smaller for speed)
- **Batch Size:** 1
- **Learning Rate:** 1e-4
- **Output:** `test_lora_minimal.safetensors`

### Commands:
```bash
cd /home/joerissen/ai/kohya_ss_new
source venv/bin/activate

# Create test output directory
mkdir -p /tmp/lora_test_output

# Training command (minimal test)
python sd3_train.py \
  --pretrained_model_name_or_path="/home/joerissen/ai/SwarmUI/Models/Stable-Diffusion/OfficialStableDiffusion/sd3.5_large.safetensors" \
  --train_data_dir="/home/joerissen/ai/ai4artsed_webserver/archive/lora_experiment/lora_training_images" \
  --output_dir="/tmp/lora_test_output" \
  --output_name="test_lora_minimal" \
  --resolution="768,768" \
  --train_batch_size=1 \
  --learning_rate=1e-4 \
  --lr_scheduler="constant" \
  --max_train_epochs=2 \
  --save_every_n_epochs=1 \
  --mixed_precision="bf16" \
  --save_precision="bf16" \
  --network_module="networks.lora" \
  --network_dim=16 \
  --network_alpha=8 \
  --optimizer_type="AdamW8bit"

deactivate
```

### Expected Results:
- Training starts without errors
- Progress logs show epoch/step updates
- Loss values decrease
- Output file created: `/tmp/lora_test_output/test_lora_minimal.safetensors`
- File size: ~50-150 MB (rank 16)
- Training time: ~10-20 minutes

### Success Criteria:
- [ ] Training completes both epochs
- [ ] No CUDA OOM errors
- [ ] Output .safetensors file exists
- [ ] File size reasonable (>10 MB, <500 MB)
- [ ] No Python exceptions

### Actual Results:
_To be filled during test execution_

---

## Test 5: LoRA File Integrity Check

### Commands:
```bash
cd /home/joerissen/ai/kohya_ss_new
source venv/bin/activate

# Inspect LoRA file
python -c "
from safetensors import safe_open
import os

lora_path = '/tmp/lora_test_output/test_lora_minimal.safetensors'

if not os.path.exists(lora_path):
    print('ERROR: LoRA file not found')
    exit(1)

file_size = os.path.getsize(lora_path) / (1024 * 1024)
print(f'File size: {file_size:.2f} MB')

with safe_open(lora_path, framework='pt', device='cpu') as f:
    keys = f.keys()
    print(f'Number of tensors: {len(keys)}')
    print(f'Sample keys: {list(keys)[:5]}')

print('✓ LoRA file is valid')
"

deactivate
```

### Expected Results:
- File exists
- File size: 50-150 MB
- Contains LoRA tensors (lora_up, lora_down, alpha)
- Valid safetensors format
- No corruption

### Actual Results:
_To be filled during test execution_

---

## Test 6: ComfyUI LoRA Loading Test

### Commands:
```bash
# Copy LoRA to ComfyUI directory
cp /tmp/lora_test_output/test_lora_minimal.safetensors /home/joerissen/ai/SwarmUI/Models/Lora/

# Check if ComfyUI can detect it
ls -lh /home/joerissen/ai/SwarmUI/Models/Lora/test_lora_minimal.safetensors

# Verify SwarmUI can list it (if running)
# Manual check: Open SwarmUI → LoRAs section → Should appear in list
```

### Manual Verification Steps:
1. Start SwarmUI (if not running): `cd /home/joerissen/ai/SwarmUI && bash launch-linux.sh`
2. Open http://localhost:7801
3. Navigate to LoRAs section
4. Look for `test_lora_minimal.safetensors` in the list
5. Try loading it (should not error)
6. (Optional) Generate a test image with LoRA strength 0.5

### Expected Results:
- LoRA appears in SwarmUI LoRA list
- Can be loaded without errors
- No warnings about incompatible format
- (Optional) Test generation succeeds

### Actual Results:
_To be filled during test execution_

---

## Test 7: DevServer Integration Check

### Commands:
```bash
# Check if DevServer's sd35_large config can reference LoRAs
cat /home/joerissen/ai/ai4artsed_webserver/devserver/schemas/chunks/output_image_sd35_large.json | head -50

# Check ComfyUI workflow structure
# Look for LoraLoader node compatibility
```

### Expected Results:
- ComfyUI workflow is JSON-based
- Can be modified to include LoraLoader node
- LoRA path: `Models/Lora/test_lora_minimal.safetensors`

### Actual Results:
_To be filled during test execution_

---

## Test 8: Cleanup & Rollback Verification

### Commands:
```bash
# Verify we can restore previous PyTorch if needed
cd /home/joerissen/ai/kohya_ss_new
source venv/bin/activate

pip list | grep torch

# If rollback needed:
# pip install torch==2.7.0+cu128 torchvision==0.22.0+cu128 --index-url https://download.pytorch.org/whl/cu128

deactivate

# Clean up test files
# rm /tmp/lora_test_output/test_lora_minimal.safetensors
# rm /home/joerissen/ai/SwarmUI/Models/Lora/test_lora_minimal.safetensors
```

### Expected Results:
- Can list installed packages
- Rollback command available if needed
- Test files can be removed

### Actual Results:
_To be filled during test execution_

---

## Risk Assessment

### Low Risk:
- ✅ Kohya venv is isolated (won't affect DevServer)
- ✅ ComfyUI already uses PyTorch nightly
- ✅ Test output goes to /tmp (temporary)
- ✅ Can roll back PyTorch upgrade

### Medium Risk:
- ⚠️ Training may fail due to missing Kohya dependencies
- ⚠️ CUDA OOM possible (but unlikely with batch_size=1, low rank)
- ⚠️ SD 3.5 support in Kohya may have issues

### Mitigation:
- Keep backup of current venv state
- Use minimal test config (2 epochs, rank 16)
- Monitor GPU memory during training
- Document all errors for troubleshooting

---

## Success Criteria (Overall)

**Minimum (Pass):**
- [ ] PyTorch nightly installs successfully
- [ ] Training starts and runs for at least 1 epoch
- [ ] Output LoRA file is created
- [ ] File is valid safetensors format

**Full Success:**
- [ ] Training completes 2 epochs without errors
- [ ] LoRA loads in ComfyUI/SwarmUI
- [ ] File size and structure are correct
- [ ] No GPU memory issues
- [ ] Can generate test image with LoRA (optional)

**Failure Conditions:**
- ❌ PyTorch upgrade breaks Kohya
- ❌ CUDA OOM during training
- ❌ SD 3.5 training not supported
- ❌ Output file corrupted or unusable
- ❌ LoRA won't load in ComfyUI

---

## Timeline

**Estimated Time:** 1-2 hours
- Environment check: 5 min
- PyTorch upgrade: 10 min
- Dependencies install: 10 min
- Training run: 15-30 min (2 epochs)
- Verification: 10 min
- Documentation: 10 min

---

## Notes

_Space for observations during testing_

---

## Final Recommendation

_To be filled after test completion_

**Options:**
1. ✅ **Proceed with frontend** - All tests passed
2. ⚠️ **Proceed with caution** - Some issues but workable
3. ❌ **Do not proceed** - Critical issues found

**Reasoning:**
_To be filled_

---

**Test Execution Log:**

_Timestamp entries to be added during execution_
