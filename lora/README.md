# LoRA Training Setup for AI4ArtsEd DevServer

**Purpose:** Enable SD 3.5 Large LoRA training for advanced students using Kohya-SS with RTX 5090 support.

**Status:** Standalone training tool (not integrated with DevServer orchestration)

**Last Updated:** 2025-11-07

---

## Path Placeholders

This documentation uses the following placeholders for paths. Replace them with your actual installation locations:

| Placeholder | Meaning | Example |
|------------|---------|---------|
| `$KOHYA_DIR` | Your Kohya-SS installation directory | `~/ai/kohya_ss_new` or `~/kohya-ss` |
| `$SWARMUI_DIR` | Your SwarmUI installation directory | `~/SwarmUI` or `~/ai/SwarmUI` |
| `$DEVSERVER_DIR` | AI4ArtsEd DevServer directory | `~/ai4artsed_webserver` |
| `$TRAINING_DATA` | Your training datasets location | `~/trainingdata` or `~/datasets` |

**Note:** The automated `install.sh` script will auto-detect these paths for you.

---

## Table of Contents

1. [Overview](#overview)
2. [System Safety](#system-safety)
3. [Prerequisites](#prerequisites)
4. [Installation](#installation)
5. [SD 3.5 Training Workflow](#sd-35-training-workflow)
6. [DevServer Integration](#devserver-integration)
7. [Troubleshooting](#troubleshooting)
8. [Technical Details](#technical-details)

---

## Overview

This setup enables training custom LoRAs (Low-Rank Adaptations) for **Stable Diffusion 3.5 Large**, which can then be used with DevServer's `sd35_large` output configuration.

### What is LoRA?

LoRA (Low-Rank Adaptation) is a parameter-efficient fine-tuning technique that allows you to:
- Train custom artistic styles with only 10-100 images
- Create culturally-specific visual models (e.g., YorubaHeritage LoRA)
- Customize SD 3.5's output without retraining the entire model
- Use 10-20x less VRAM than full fine-tuning

### Pedagogical Context

**For Advanced Students:** LoRA training is a tool for exploring the intersection of:
- Cultural representation in generative AI
- Limits of pre-trained models with regard to cultural knowledge
- Active participation in shaping AI outputs (counter-hegemonic pedagogy)

**Example Workflow:**
1. Student uses DevServer's YorubaHeritage interception config (Stage 2)
2. Generates culturally-informed prompts
3. Trains a YorubaHeritage LoRA on authentic cultural imagery
4. Combines intercepted prompts + trained LoRA for culturally-grounded outputs

---

## System Safety

### Environment Isolation: SAFE TO INSTALL

**Your DevServer productivity system will NOT be affected by this installation.**

#### Why it's safe:

**Three Isolated Virtual Environments:**
1. **DevServer venv** (Python 3.13.9, PyTorch 2.7.1)
   - Location: `$DEVSERVER_DIR/venv/`
   - Status: Unaffected (doesn't even use PyTorch)

2. **Kohya venv** (Python 3.11.14, PyTorch 2.7.0 → 2.9.0 nightly)
   - Location: `$KOHYA_DIR/venv/`
   - Status: **Upgrade target** (isolated, safe)

3. **ComfyUI venv** (Python 3.11.14, PyTorch 2.9.0 nightly)
   - Location: `$SWARMUI_DIR/dlbackend/ComfyUI/venv/`
   - Status: **Already running nightly** (proof of safety)

**Proof:** ComfyUI already uses PyTorch nightly without affecting DevServer!

#### What We're Upgrading:

Only the Kohya venv gets upgraded. DevServer continues using its own isolated environment.

```
┌─────────────────────────────────────────────┐
│ System: Each box is completely isolated     │
├─────────────────────────────────────────────┤
│ DevServer venv  │ PyTorch 2.7.1   │ ✓ Safe │
│ Kohya venv      │ PyTorch 2.9.0dev│ ← HERE │
│ ComfyUI venv    │ PyTorch 2.9.0dev│ ✓ Safe │
└─────────────────────────────────────────────┘
```

---

## Prerequisites

### Hardware Requirements

**GPU:** RTX 5090 (22GB VRAM)
- **Blackwell SM_120 architecture**
- **Requires PyTorch 2.9.0+ nightly** (standard PyTorch doesn't support SM_120)

**VRAM Requirements by Model:**
- SD 1.5 LoRA: 8-12GB (fast, 30-60 min)
- SDXL LoRA: 16-20GB (quality, 1-2 hours)
- **SD 3.5 Large LoRA: 18-22GB** (best quality, 1-3 hours)

**Storage:**
- Training dataset: 10MB - 1GB (10-1000 images)
- Trained LoRA output: 100-500MB per LoRA

### Software Requirements

**Already Installed:**
- ✅ Kohya-SS: `$KOHYA_DIR/`
- ✅ SD 3.5 Large model: `$SWARMUI_DIR/Models/Stable-Diffusion/OfficialStableDiffusion/sd3.5_large.safetensors` (16GB)
- ✅ Text encoders: `clip_g.safetensors`, `clip_l.safetensors`, `t5xxl_fp8_e4m3fn.safetensors`

**Needs Upgrade:**
- ⚠️ PyTorch 2.7.0 → 2.9.0+ nightly (for RTX 5090 support)
- ⚠️ Kohya-SS dependencies (SD 3.5 branch compatible)

---

## Installation

### Option 1: Automated Installation (Recommended)

Run the provided installation script:

```bash
cd $DEVSERVER_DIR/lora
bash install.sh
```

The script will:
1. Verify Kohya venv exists
2. Activate Kohya venv
3. Upgrade PyTorch to nightly (cu128)
4. Install/upgrade all dependencies
5. Verify CUDA compatibility
6. Test torch import

### Option 2: Manual Installation

If you prefer manual control:

```bash
# 1. Navigate to Kohya directory
cd $KOHYA_DIR

# 2. Activate Kohya venv
source venv/bin/activate

# 3. Verify you're in the correct environment
which python
# Should show: $KOHYA_DIR/venv/bin/python

# 4. Upgrade PyTorch to nightly
pip install --pre torch torchvision --index-url https://download.pytorch.org/whl/nightly/cu128

# 5. Install LoRA training dependencies
pip install -r $DEVSERVER_DIR/lora/requirements.txt

# 6. Verify installation
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0)}')"

# Expected output:
# PyTorch: 2.9.0.dev20250807+cu128 (or later)
# CUDA: True
# GPU: NVIDIA GeForce RTX 5090

# 7. Deactivate when done
deactivate
```

### Verification

After installation, verify RTX 5090 support:

```bash
cd $KOHYA_DIR
source venv/bin/activate
python -c "import torch; print(torch.cuda.get_device_capability())"
# Should output: (9, 12)  ← SM_120 (Blackwell)
deactivate
```

---

## SD 3.5 Training Workflow

### Architecture Overview

**SD 3.5 Large vs SDXL:**
- SD 3.5: **MMDiT architecture** (8B parameters, 3 text encoders)
- SDXL: **UNet architecture** (2.6B parameters, 2 text encoders)
- **LoRAs are NOT cross-compatible** between architectures

**SD 3.5 Text Encoders:**
1. CLIP-ViT-L (OpenAI CLIP) - 123M params
2. OpenCLIP-ViT-G (OpenCLIP bigG) - 354M params
3. T5-XXL (Google's T5) - 4.7B params

**Result:** Better text understanding, higher quality images, but longer training time.

### Training Methods

#### Method A: Kohya-SS GUI (Easiest)

**Status:** SD 3.5 support in GUI is limited (missing some settings)

**Workaround:** Use GUI for dataset prep, switch to CLI for training.

```bash
cd $KOHYA_DIR
bash gui.sh
# GUI opens at http://localhost:7860
```

**Steps:**
1. LoRA → Training → Model → Select `sd3.5_large.safetensors`
2. Folders → Training images → Select your dataset folder
3. Parameters → Adjust learning rate, epochs, batch size
4. ⚠️ **GUI may not show SD 3.5 specific options** (CLIP-L, T5 settings)
5. Save config, train via CLI instead (see below)

#### Method B: Kohya-SS CLI (Recommended for SD 3.5)

**Why CLI:** SD 3.5 training requires settings not yet in GUI.

**Basic Training Command:**

```bash
cd $KOHYA_DIR
source venv/bin/activate

python sd3_train.py \
  --pretrained_model_name_or_path="$SWARMUI_DIR/Models/Stable-Diffusion/OfficialStableDiffusion/sd3.5_large.safetensors" \
  --train_data_dir="$TRAINING_DATA/yorubaheritage/images" \
  --output_dir="$SWARMUI_DIR/Models/Lora/" \
  --output_name="yorubaheritage_sd35" \
  --resolution="1024,1024" \
  --train_batch_size=1 \
  --gradient_accumulation_steps=4 \
  --learning_rate=1e-4 \
  --lr_scheduler="cosine" \
  --max_train_epochs=10 \
  --save_every_n_epochs=2 \
  --mixed_precision="bf16" \
  --save_precision="bf16" \
  --cache_latents \
  --optimizer_type="AdamW8bit" \
  --network_module="networks.lora" \
  --network_dim=32 \
  --network_alpha=16 \
  --clip_skip=2

deactivate
```

**Key Parameters:**

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `resolution` | `1024,1024` | SD 3.5 native resolution |
| `train_batch_size` | `1` | VRAM constraint (22GB) |
| `gradient_accumulation_steps` | `4` | Simulate batch size of 4 |
| `learning_rate` | `1e-4` | Standard LoRA learning rate |
| `network_dim` | `32` | LoRA rank (higher = more capacity, slower) |
| `network_alpha` | `16` | LoRA alpha (typically dim/2) |
| `mixed_precision` | `bf16` | BFloat16 for stability + speed |
| `optimizer_type` | `AdamW8bit` | Memory-efficient optimizer |

**Advanced Optimizations:**

```bash
# Add memory optimization flags
--xformers \                          # Flash Attention (faster)
--gradient_checkpointing \            # Reduce VRAM (slower)
--enable_bucket \                     # Variable image sizes
--min_bucket_reso=512 \
--max_bucket_reso=2048 \
--bucket_reso_steps=64
```

#### Method C: Config File (Best for Reproducibility)

Create `$TRAINING_DATA/yorubaheritage/train_config.toml`:

```toml
[model_arguments]
pretrained_model_name_or_path = "$SWARMUI_DIR/Models/Stable-Diffusion/OfficialStableDiffusion/sd3.5_large.safetensors"
vae = ""  # SD 3.5 has built-in VAE

[dataset_arguments]
train_data_dir = "$TRAINING_DATA/yorubaheritage/images"
resolution = [1024, 1024]
batch_size = 1
enable_bucket = true
min_bucket_reso = 512
max_bucket_reso = 2048

[training_arguments]
output_dir = "$SWARMUI_DIR/Models/Lora/"
output_name = "yorubaheritage_sd35"
max_train_epochs = 10
save_every_n_epochs = 2
learning_rate = 1e-4
lr_scheduler = "cosine"
optimizer_type = "AdamW8bit"
mixed_precision = "bf16"
save_precision = "bf16"

[network_arguments]
network_module = "networks.lora"
network_dim = 32
network_alpha = 16

[optimization_arguments]
xformers = true
gradient_checkpointing = true
gradient_accumulation_steps = 4
```

Train with:

```bash
cd $KOHYA_DIR
source venv/bin/activate
python sd3_train.py --config_file $TRAINING_DATA/yorubaheritage/train_config.toml
deactivate
```

### Dataset Preparation

**Image Requirements:**
- **Quantity:** 10-100 images (more = better, but diminishing returns after 50)
- **Resolution:** 1024x1024 minimum (SD 3.5 native)
- **Format:** JPG or PNG
- **Content:** Consistent subject/style (e.g., Yoruba traditional attire, ceremonies)

**Folder Structure:**

```
$TRAINING_DATA/yorubaheritage/
├── images/
│   ├── 10_yoruba_ceremony.jpg        # Prefix = repeat count
│   ├── 10_yoruba_traditional_attire.jpg
│   ├── 10_yoruba_beadwork.jpg
│   └── ...
└── train_config.toml
```

**Repeat Count (Prefix):**
- `10_` = Image used 10 times per epoch
- Higher repeats for rare/important concepts
- Lower repeats for common elements

**Captioning (Optional but Recommended):**

Create `.txt` files with same name as images:

```
10_yoruba_ceremony.jpg
10_yoruba_ceremony.txt  ← "Yoruba traditional ceremony with dancers in aso oke fabric"
```

Better captions = better LoRA quality.

**Existing Dataset:**

You have 16 prepared images in:
```
$DEVSERVER_DIR/archive/lora_experiment/lora_training_images/
```
- lora_001.jpg through lora_016.jpg (768x768 JPG format)
- These can be used for testing, but you may want to prepare a new culturally-specific dataset

### Training Time Estimates

**RTX 5090 (22GB VRAM):**
- 10 images, 10 epochs: ~30-45 minutes
- 50 images, 10 epochs: ~1-2 hours
- 100 images, 20 epochs: ~3-4 hours

**Monitoring Training:**

```bash
# Terminal output shows:
# - Epoch progress
# - Loss values (lower = better, should decrease)
# - Time per step
# - ETA

# Optional: TensorBoard monitoring
tensorboard --logdir=$SWARMUI_DIR/Models/Lora/logs
# Open http://localhost:6006 to see loss curves
```

---

## DevServer Integration

### Loading Trained LoRAs in DevServer

**Trained LoRA Location:**
```
$SWARMUI_DIR/Models/Lora/yorubaheritage_sd35.safetensors
```

**ComfyUI Auto-Detection:**
- ComfyUI scans `Models/Lora/` directory
- LoRAs appear in "Load LoRA" nodes automatically
- No manual registration needed

### Method 1: Manual ComfyUI Workflow (Current)

**Edit the ComfyUI workflow JSON:**

Location: `$DEVSERVER_DIR/devserver/schemas/chunks/output_image_sd35_large.json`

**Add LoRA loader node** (you'll need to modify the workflow to include a LoRA loader before the model):

```json
{
  "10": {
    "class_type": "LoraLoader",
    "inputs": {
      "model": ["4", 0],
      "clip": ["6", 1],
      "lora_name": "yorubaheritage_sd35.safetensors",
      "strength_model": 1.0,
      "strength_clip": 1.0
    }
  }
}
```

**Note:** Modifying ComfyUI workflows requires understanding node IDs and connections. Consider this advanced usage.

### Method 2: SwarmUI Interface (Easier)

**For testing before DevServer integration:**

1. Open SwarmUI: `http://localhost:7801`
2. Generate tab → LoRAs section
3. Click "+" → Select `yorubaheritage_sd35.safetensors`
4. Set strength: 0.7-1.0
5. Enter prompt → Generate
6. Compare output with/without LoRA

### Method 3: Future Integration (Not Implemented)

**Potential DevServer enhancement:**

```json
// devserver/schemas/configs/output/sd35_large_yoruba.json
{
  "name": "sd35_large_yoruba",
  "type": "output_config",
  "description": "SD 3.5 Large with YorubaHeritage LoRA",
  "pipeline": "single_text_media_generation",
  "chunks": ["output_image_sd35_large"],
  "lora": {
    "name": "yorubaheritage_sd35.safetensors",
    "strength_model": 0.85,
    "strength_clip": 0.85
  }
}
```

This would require:
1. New LoRA support in `output_image_sd35_large.json` chunk
2. Config loader modifications to pass LoRA parameters
3. Testing with DevServer orchestration flow

**Pedagogical Workflow (Full Integration):**

```
Stage 1: Translation + Safety
  ↓
Stage 2: YorubaHeritage Interception (prompt transformation)
  ↓
Stage 3: Pre-Output Safety
  ↓
Stage 4: SD 3.5 Large + YorubaHeritage LoRA
  ↓
Output: Culturally-informed prompt + culturally-trained visual model
```

---

## Troubleshooting

### Issue: "CUDA error: no kernel image is available"

**Cause:** PyTorch doesn't support RTX 5090's SM_120 architecture.

**Solution:**
```bash
cd $KOHYA_DIR
source venv/bin/activate
pip install --pre torch torchvision --index-url https://download.pytorch.org/whl/nightly/cu128
deactivate
```

**Verify:**
```bash
python -c "import torch; print(torch.__version__)"
# Must show: 2.9.0.dev or later
```

### Issue: "torch.cuda.OutOfMemoryError: CUDA out of memory"

**Cause:** Training exceeds 22GB VRAM.

**Solutions:**

1. **Reduce batch size:**
   ```bash
   --train_batch_size=1
   ```

2. **Enable gradient checkpointing:**
   ```bash
   --gradient_checkpointing
   ```

3. **Use FP8 text encoders** (smaller memory):
   ```bash
   # Replace t5xxl.safetensors with:
   # t5xxl_fp8_e4m3fn.safetensors (already in SwarmUI)
   ```

4. **Lower resolution:**
   ```bash
   --resolution="768,768"  # Instead of 1024,1024
   ```

5. **Unload ComfyUI before training:**
   ```bash
   # Stop SwarmUI/ComfyUI to free VRAM:
   pkill -f "SwarmUI"
   pkill -f "ComfyUI"
   ```

### Issue: "wrong venv - installing to system Python"

**Cause:** Forgot to activate Kohya venv.

**Solution:**
```bash
which python
# If NOT showing $KOHYA_DIR/venv/bin/python, STOP!

# Activate correct venv:
cd $KOHYA_DIR
source venv/bin/activate

# Now install:
pip install -r requirements.txt
```

### Issue: Training loss not decreasing

**Possible causes:**

1. **Learning rate too low:**
   - Try: `--learning_rate=2e-4` (double it)

2. **Learning rate too high:**
   - Loss jumps around, try: `--learning_rate=5e-5` (half it)

3. **Dataset too small:**
   - Need 20+ images minimum for stable training
   - Add more images or increase `max_train_epochs`

4. **Dataset too diverse:**
   - LoRA works best with consistent subject/style
   - Narrow focus (e.g., only Yoruba ceremonies, not all Nigerian culture)

5. **Insufficient training:**
   - Increase epochs: `--max_train_epochs=20`
   - Monitor loss curve in TensorBoard

### Issue: LoRA doesn't affect output

**Possible causes:**

1. **LoRA strength too low:**
   - In ComfyUI LoRA loader, increase strength to 0.9-1.0

2. **LoRA not loaded:**
   - Check ComfyUI console for LoRA loading messages
   - Verify file exists in `$SWARMUI_DIR/Models/Lora/`

3. **Incompatible architecture:**
   - Verify LoRA was trained on SD 3.5 Large (not SDXL!)
   - SDXL LoRAs won't work with SD 3.5

4. **Prompt doesn't trigger LoRA:**
   - Use trigger words from training captions
   - E.g., "yoruba traditional ceremony" if that was in captions

---

## Technical Details

### SD 3.5 Architecture (MMDiT)

**Multimodal Diffusion Transformer:**
- 8 billion parameters (vs SDXL's 2.6B)
- 38 transformer blocks with Query-Key Normalization
- Joint attention mechanism (image + text)
- Native 1024x1024 resolution

**Text Encoding Pipeline:**
```
User Prompt
  → CLIP-ViT-L (123M) → CLIP embeddings
  → OpenCLIP-ViT-G (354M) → OpenCLIP embeddings
  → T5-XXL (4.7B) → T5 embeddings
  → Concatenated → Joint attention with image latents
```

**LoRA Training Targets:**
- Transformer blocks (attention layers)
- Optionally: Text encoder projection layers
- Not trained: VAE, final output layers

### LoRA Mathematics

**Standard Fine-Tuning:**
```
W_new = W_pretrained + ΔW
# ΔW has same dimensions as W (millions of parameters)
```

**LoRA (Low-Rank Adaptation):**
```
W_new = W_pretrained + A × B
# A: (d × r), B: (r × k)
# r = rank (typically 4-128, default 32)
# r << d,k → Much fewer parameters to train
```

**Example:**
- Full layer: 1024 × 1024 = 1,048,576 parameters
- LoRA (r=32): (1024 × 32) + (32 × 1024) = 65,536 parameters
- **16x fewer parameters, 10x less VRAM, 5x faster training**

### File Formats

**SafeTensors (Recommended):**
- `.safetensors` extension
- Fast loading (memory-mapped)
- Security: No arbitrary code execution
- Standard for Hugging Face, ComfyUI

**Legacy Checkpoint:**
- `.ckpt` or `.pt` extension
- Uses Python pickle (security risk)
- Slower loading
- Not recommended for sharing

### VRAM Budget (RTX 5090, 22GB)

**SD 3.5 Large Training:**
```
Base Model (FP16):          16 GB
Optimizer States:           3-4 GB
Gradients:                  1-2 GB
Batch (1 img @ 1024x1024): 1 GB
LoRA Adapter:              <0.5 GB
-----------------------------------------
Total:                     ~21-23 GB
```

**Optimization Strategies:**
- FP8 text encoders: Save 2-3 GB
- Gradient checkpointing: Trade compute for memory (-2 GB)
- Batch size 1: Minimum memory usage
- Gradient accumulation: Simulate larger batches without more VRAM

### Training Hyperparameters (Explained)

| Parameter | Default | Explanation |
|-----------|---------|-------------|
| `learning_rate` | `1e-4` | Step size for weight updates. Too high = unstable, too low = slow |
| `network_dim` (rank) | `32` | LoRA capacity. Higher = more expressive, but overfits easier |
| `network_alpha` | `16` | Scaling factor. Typically `dim/2`. Affects effective learning rate |
| `max_train_epochs` | `10` | Full passes through dataset. More epochs = better fit (up to a point) |
| `train_batch_size` | `1` | Images per step. Limited by VRAM (22GB → batch 1) |
| `gradient_accumulation_steps` | `4` | Simulate batch size 4 by accumulating gradients |
| `lr_scheduler` | `"cosine"` | Learning rate decay. Cosine = smooth decay, good for LoRA |
| `optimizer_type` | `"AdamW8bit"` | 8-bit Adam optimizer. Saves VRAM with minimal quality loss |
| `mixed_precision` | `"bf16"` | BFloat16 training. Faster + less VRAM than FP32, stable |

**Advanced:**
- `clip_skip=2`: Skip last CLIP layer (sometimes better for anime/artistic styles)
- `noise_offset=0.05`: Add slight noise to improve dark/light handling
- `min_snr_gamma=5`: Min-SNR weighting (stabilizes training)

---

## Additional Resources

### Kohya-SS Documentation
- GitHub: https://github.com/kohya-ss/sd-scripts
- SD 3.5 Support PR: https://github.com/kohya-ss/sd-scripts/pull/1719
- Training Guide: https://github.com/kohya-ss/sd-scripts/wiki

### SD 3.5 Resources
- Stability AI: https://stability.ai/news/stable-diffusion-3-5
- Model Card: https://huggingface.co/stabilityai/stable-diffusion-3.5-large
- Technical Report: https://stability.ai/research/sd3-technical-report.pdf

### LoRA Theory
- Original Paper: https://arxiv.org/abs/2106.09685
- Hugging Face PEFT: https://huggingface.co/docs/peft/main/en/index

### Community
- Civitai (LoRA sharing): https://civitai.com
- r/StableDiffusion: https://reddit.com/r/StableDiffusion
- Kohya Discord: (check GitHub for invite)

---

## Changelog

### 2025-11-07: Initial Setup
- Created requirements.txt for SD 3.5 + RTX 5090
- Documented installation and training workflow
- Verified environment isolation (DevServer safety)
- Prepared for YorubaHeritage LoRA training

---

## Contact

**For DevServer-specific questions:**
- See: `docs/ARCHITECTURE.md`, `docs/DEVELOPMENT_LOG.md`

**For LoRA training issues:**
- Check: Troubleshooting section above
- Kohya-SS GitHub Issues: https://github.com/kohya-ss/sd-scripts/issues

**Pedagogical context:**
- See: `docs/LEGACY_SERVER_ARCHITECTURE.md` (Section 2.1: Prompt Interception)
- See: `docs/readme.md` (Counter-hegemonic pedagogy)
