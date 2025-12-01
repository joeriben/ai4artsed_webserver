# Session 85: QWEN Image Edit (img2img) Implementation

**Date**: 2025-12-01
**Status**: 🟡 Partially Complete - Models downloaded, configs created, but architecture questions remain

---

## 🎯 Goal

Implement proper img2img functionality for AI4ArtsEd using QWEN Image Edit (Lightning 4-step), replacing the non-functional SD3.5 img2img attempt.

---

## ✅ What Was Completed

### 1. **Model Downloads** (All Complete)

Downloaded to `/home/joerissen/ai/SwarmUI/Models/`:

- ✅ `diffusion_models/qwen_image_edit_fp8_e4m3fn.safetensors` (20 GB)
- ✅ `loras/Qwen-Image-Edit-Lightning-4steps-V1.0-bf16.safetensors` (811 MB)
- ✅ `VAE/qwen_image_vae.safetensors` (already present)
- ✅ `clip/qwen_2.5_vl_7b_fp8_scaled.safetensors` (already present)

**Sources:**
- [Comfy-Org/Qwen-Image-Edit_ComfyUI](https://huggingface.co/Comfy-Org/Qwen-Image-Edit_ComfyUI)
- [lightx2v/Qwen-Image-Lightning](https://huggingface.co/lightx2v/Qwen-Image-Lightning)

### 2. **Backend Configuration Files Created**

#### `/devserver/schemas/chunks/output_image_qwen_img2img.json`
- Complete ComfyUI workflow for QWEN Image Edit
- Key nodes:
  - Node 78: LoadImage (input)
  - Node 93: ImageScaleToTotalPixels (1 megapixel)
  - Node 76/77: TextEncodeQwenImageEdit (positive/negative)
  - Node 88: VAEEncode
  - Node 3: KSampler (4 steps, CFG=1, denoise=1.0)
  - Node 8: VAEDecode
  - Node 60: SaveImage

#### `/devserver/schemas/configs/output/qwen_img2img.json`
- Output config for QWEN img2img
- Display name: "QWEN Image Edit (4-step Lightning)"
- Parameters: 4 steps, CFG=1, denoise=1.0, 1 megapixel
- Lightning-optimized settings

### 3. **Existing Infrastructure (Already Present)**

- ✅ `/devserver/schemas/pipelines/image_transformation.json` (Pipeline)
- ✅ `/public/ai4artsed-frontend/src/views/image_transformation.vue` (Vue view)
- ✅ Router entry: `/image-transformation`
- ✅ Upload endpoint: `POST /api/media/upload/image`

---

## ❌ Critical Discovery: SD3.5 is NOT img2img-capable

**Problem:** The previous Session 80 implementation used SD3.5 Large for img2img, but **SD3.5 does not natively support img2img**. QWEN Image Edit is the correct model for this task.

**Impact:** The `sd35_large_img2img` config should be deprecated/disabled.

---

## 🔴 Errors Made During This Session

### 1. **Created `image_transformation.json` in Wrong Location**

**What happened:**
- Created `/devserver/schemas/configs/image_transformation.json` (top-level)
- This should have been in `/devserver/schemas/configs/interception/` (Stage2 configs)
- OR not created at all (see Architecture Issue below)

**Impact:**
- Hijacked an existing category in Phase 1
- Reduced visible categories from 7 to 6
- Made the "Bild" (🖼️) category disappear or malfunction

**Fix Applied:**
- Deleted the misplaced `image_transformation.json`

**Status:** 🟡 Partially fixed - file deleted, but category may still be broken

### 2. **Misunderstood Architecture**

**What happened:**
- Treated img2img as a separate Stage2-config (like "Kunstgeschichte", "Surrealismus")
- img2img is actually a **MODE** (like t2i/i2i), not a config

**Correct Understanding:**
- **Modes** = Header toggle (Text→Image vs Image→Image)
- **Stage2 Configs** = Pedagogical transformations (Kunstgeschichte, Surrealismus, etc.)
- **Stage4 Configs** = Output models (sd35_large, gpt_image_1, qwen_img2img, etc.)
- **All Stage2 configs should work for BOTH modes**

---

## 🤔 Open Architecture Questions

### **Q1: How should i2i mode be implemented?**

**Option A:** Separate routes
- `/text-transformation` (current, works)
- `/image-transformation` (exists, but orphaned)

**Option B:** Mode toggle in header
- Single route with mode switcher
- Same Stage2 configs for both modes
- Pipeline determined by mode

**Option C:** Graceful fallback
- All t2i configs also work for i2i
- Backend detects `input_image` parameter
- Automatically uses i2i pipeline if image present

**Status:** 🔴 Not decided - needs user input

### **Q2: Where does `input_image` parameter come from?**

**Likely answer:** Stage1 (Translation)
- User uploads image → Stage1 stores path
- Stage2 (Interception) runs same way as t2i
- Stage3/4 execute with `input_image` parameter
- Pipeline switches to i2i workflow

**Status:** 🟡 Needs confirmation

### **Q3: What about the "Bild-Transformation" config?**

**Answer:** It should NOT exist as a Stage2 config
- It was a mistake
- Modes ≠ Configs
- Deleted and should stay deleted

---

## 🧪 Testing Status

### ❌ Not Tested Yet:
- QWEN img2img workflow execution
- Image upload → context → QWEN generation
- Output image display
- Retry with different seed
- Fullscreen modal

### Why Not Tested:
- Architecture unclear (how to trigger i2i mode?)
- Category issue not resolved
- No clear path to test without breaking existing system

---

## 📂 File Structure Summary

```
devserver/
├── schemas/
│   ├── chunks/
│   │   └── output_image_qwen_img2img.json ← NEW (QWEN workflow)
│   ├── configs/
│   │   ├── output/
│   │   │   ├── qwen_img2img.json ← NEW (output config)
│   │   │   └── sd35_large_img2img.json ← OLD (deprecated, SD3.5 not img2img-capable)
│   │   └── interception/ (Stage2 configs - untouched)
│   └── pipelines/
│       └── image_transformation.json ← EXISTS (pipeline definition)
│
public/ai4artsed-frontend/src/
├── views/
│   └── image_transformation.vue ← EXISTS (Vue view)
└── router/
    └── index.ts ← EXISTS (route: /image-transformation)
```

---

## 🔧 What Needs to Happen Next

### **Priority 1: Architectural Decision**
**Decision needed:** How should t2i/i2i modes work?
- Separate routes vs. mode toggle vs. automatic detection?
- User must decide before implementation continues

### **Priority 2: Fix Category Issue**
**Problem:** Phase 1 shows 6 categories instead of 7
- One category was destroyed/hidden by the misplaced config
- Even after deletion, may need frontend/backend restart
- Needs investigation: which category is missing?

### **Priority 3: Update Frontend**
**Current state:** `image_transformation.vue` has:
```typescript
configsByCategory = {
  image: [
    { id: 'sd35_large_img2img', disabled: false },  // ← Should be disabled (not img2img-capable)
    { id: 'qwen_img2img', disabled: true }          // ← Should be enabled
  ]
}
```
**Needed:** Enable QWEN, disable SD3.5

### **Priority 4: Test QWEN Workflow**
**Requirements:**
1. Clarify mode architecture
2. Fix category issue
3. Update frontend
4. Test end-to-end

---

## 💡 Key Learnings

### **1. Always Ask About Architecture First**
- Don't create configs without understanding the system
- Stage2 ≠ Stage4 ≠ Modes
- Placement matters: `configs/` vs `configs/interception/` vs `configs/output/`

### **2. SD3.5 is NOT img2img-capable**
- Previous Session 80 implementation was flawed
- QWEN Image Edit is the correct choice
- Lightning 4-step version = ultra-fast (5-10 seconds)

### **3. Modes vs Configs**
- **Modes** determine workflow type (t2i/i2i/i2v)
- **Configs** determine pedagogical transformation (Stage2) or output model (Stage4)
- They are orthogonal concepts

### **4. Context Matters**
- The "Bild" category in frontend = Stage4 output configs (image models)
- NOT the same as Stage2 "Kunstgeschichte" category
- Different layers of the system

---

## 🚀 Recommended Next Steps

1. **User Decision:** Choose i2i mode architecture (Option A/B/C above)
2. **Investigate:** Which category is missing? (7→6 issue)
3. **Restart Services:** Backend + Frontend (may fix category issue)
4. **Update Frontend:** Enable qwen_img2img, disable sd35_large_img2img
5. **Test:** Full workflow with uploaded image
6. **Document:** Final architecture decision in ARCHITECTURE.md

---

## 📦 Model Specifications

### QWEN Image Edit Lightning

**Model Type:** Diffusion (UNET-based)
**Speed:** 4-step Lightning (5-10 seconds)
**VRAM:** ~10 GB
**Resolution:** Auto-scales to 1 megapixel (~1024x1024)
**Denoise:** 1.0 (full transformation)
**CFG:** 1.0 (Lightning-optimized)

**Special Features:**
- Text-guided editing (add/remove/transform objects)
- Fast inference (4 steps vs typical 25-50)
- Natural language instructions
- Maintains image structure better than t2i

**Example Prompts:**
- "Remove the UI elements from the image"
- "Change the water to lava"
- "Add a rainbow in the sky"
- "Make it look like a watercolor painting"

---

## 🐛 Known Issues

1. **Category Missing:** One Stage2 category disappeared (7→6)
2. **SD3.5 img2img:** Should be disabled (not natively supported)
3. **Mode Architecture:** Not yet defined (how to switch t2i↔i2i?)
4. **Untested:** QWEN workflow never executed
5. **Frontend Mismatch:** qwen_img2img disabled, sd35_large_img2img enabled (backwards)

---

## 📚 References

- Session 80 Handover: `/docs/SESSION_80_IMG2IMG_HANDOVER.md` (SD3.5 attempt)
- Session 82 Handover: `/docs/SESSION_82_chat_overlay_implementation.md` (Träshy chat)
- ComfyUI QWEN Docs: https://docs.comfy.org/tutorials/image/qwen/qwen-image-edit
- QWEN Image Edit Paper: https://huggingface.co/Qwen/Qwen-Image-Edit

---

**Session End Time:** 2025-12-01 ~17:50 UTC
**Models Downloaded:** ✅ 20.8 GB total
**Files Created:** 2 (chunk + config)
**Files Deleted:** 1 (misplaced config)
**Architecture Questions:** 3 open
**Status:** Ready for architectural decision + testing
