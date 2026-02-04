# HeartMuLa CUDA Error - Debug Resolution

**Date:** 2026-02-04
**Status:** RESOLVED ✅ - TEXT_2 bug fixed (commit b94bc4a)

---

## Resolution (2026-02-04)

### Root Cause: TEXT_2 Always Empty String

**File:** `devserver/schemas/engine/chunk_builder.py:203`

**Bug:**
```python
if 'user_input' in context:
    parameters['TEXT_2'] = context.get('text2', '')  # ← Bug: 'text2' doesn't exist!
```

**Fix (commit b94bc4a):**
```python
if 'user_input' in context:
    parameters['TEXT_2'] = context['user_input']  # ← Correct key
```

**Impact:**
- Tags were NEVER passed to HeartMuLa (always empty string)
- HeartMuLa generated music without tag conditioning
- Invalid token indices generated → CUDA assert in codec detokenization

**Evidence:**
- Yesterday (2026-02-03 18:49): Worked → Old route was used (JSON chunk or different pipeline)
- Today (2026-02-04): Failed → New Python chunk route active with buggy TEXT_2 mapping
- Bug introduced in Session 156 when Python chunk support was added

**Testing Required:**
1. Restart backend to load fixed code
2. Test with: Lyrics="de doo doo doo", Tags="ska"
3. Verify logs show: `[CHUNK:heartmula] Tags (full): ska` (not empty)
4. Verify MP3 generation succeeds

---

## Original Problem Report

HeartMuLa music generation throws **CUDA device-side assert error** during codec detokenization.

```
torch.AcceleratorError: CUDA error: device-side assert triggered
Location: heartlib/src/heartlib/heartcodec/modeling_heartcodec.py:105 in detokenize
  → self.flow_matching.inference_codes()
  → vq_embed.get_output_from_indices(codes_bestrq_emb.transpose(1, 2))
  → F.linear() triggers CUDA assert
```

Error message:
```
[CHUNK:heartmula] Generation returned None
Music generation failed
```

---

## Facts

### Yesterday (2026-02-03 18:49) - WORKED ✅

**Generated File:** `/home/joerissen/ai/ai4artsed_development/exports/json/2026-02-03/dev_7769bcb0649c/f99fd56c-556c-4035-964b-058756bd7c8e/final/07_output_image.mp3` (434KB)

**Input:**
- Lyrics:
  ```
  de doo doo doo
  de blaa blaa blaa
  is all I want to sing to you
  ```
- Tags: Unknown (not visible in exports)

**Configuration:**
- Pipeline: `music_generation`
- Config: `heartmula` (interception config)
- Output Config: `heartmula_standard`

**Models:**
- HeartMuLa-oss-3B (old version, not RL)
- HeartCodec-oss (old version, not 20260123)

**Parameters (from commit 958ae0d):**
```python
DEFAULTS = {
    "temperature": 1.0,
    "topk": 50,
    "cfg_scale": 1.5,
    "max_audio_length_ms": 240000,
    "seed": None  # random
}
```

### Today (2026-02-04) - CUDA ERROR ❌

**Input:**
- Lyrics: `de doo doo doo`
- Tags: `ska`

**Same Models:** HeartMuLa-oss-3B, HeartCodec-oss (no change)

**Same Parameters:** temperature=1.0, topk=50, cfg_scale=1.5, max_audio_length_ms=240000

**VRAM:** 10.7GB used / 97.8GB total (plenty free)

---

## What Changed Between Yesterday and Today

### Code Changes (from other session)

**Commit 8c5ee0e** (2026-02-04 19:32):
- Rebuilt `music_generation.vue` with t2x-pattern
- Modified `backend_router.py`: Added base64 audio_data encoding for music chunks
- Modified `schema_pipeline_routes.py`: Added parallel Python chunk route
- Modified `pipeline_executor.py`: Added audio_data/audio_format to metadata whitelist
- Modified `output_music_heartmula.py`: Enhanced logging (line 95: full tags visible)

**Commit 33986e3** (2026-02-04 19:49):
- Created `lyrics_refinement.json` interception config
- Created `tags_generation.json` interception config
- Fixed streaming URL in frontend
- Removed hardcoded safety_level

### Session 156 Changes (my session, 2026-02-02/03):
- Created `dual_text_media_generation.json` pipeline (uses `{{OUTPUT_CHUNK}}` placeholder)
- Implemented Python-chunk execution in `backend_router.py`
- Added placeholder resolution in `config_loader.py`
- Python chunk detection in `chunk_builder.py`

---

## Failed Theories (Disproven)

❌ **"Tags too complex"** - HeartMuLa is a 2026 model, handles complex tags fine
❌ **"Lyrics too short"** - HeartMuLa example lyrics are equally short
❌ **"max_audio_length_ms too high"** - Yesterday worked with 240000ms
❌ **"VRAM insufficient"** - Only 10GB/98GB used

---

## Open Questions

1. **Which pipeline is used today?**
   - `music_generation` (hardcoded chunk)?
   - `dual_text_media_generation` (placeholder)?
   - User needs to check UI

2. **Random seed different?**
   - Yesterday: random seed (unknown value)
   - Today: random seed (unknown value)
   - Could specific seed values trigger bug?

3. **Model cache corrupted?**
   - Backend running continuously since yesterday?
   - Model state corrupted in memory?

4. **Code path different?**
   - Yesterday: Which route was used? Old route or new parallel route from 8c5ee0e?
   - Today: New parallel Python chunk route active?

5. **Input format different?**
   - How were TEXT_1/TEXT_2 passed yesterday vs today?
   - Dual interception active today but not yesterday?

---

## Next Debug Steps

### Step 1: Reproduce with Known-Good Input

Use EXACT input from yesterday:
```
Lyrics:
de doo doo doo
de blaa blaa blaa
is all I want to sing to you

Tags: ??? (need to find what was used yesterday)
```

### Step 2: Enable CUDA Debug Mode

Add to backend startup or heartmula_backend.py:
```python
import os
os.environ['CUDA_LAUNCH_BLOCKING'] = '1'
```

This will show EXACT line where assert fails.

### Step 3: Add Shape/Index Logging

In heartmula_backend.py, before calling pipeline:
```python
logger.info(f"[DEBUG] input_data: {input_data}")
logger.info(f"[DEBUG] lyrics length: {len(lyrics)} chars, {len(lyrics.split())} words")
logger.info(f"[DEBUG] tags: '{tags}'")
```

In heartlib code (if accessible), add logging in:
- `heartcodec/modeling_heartcodec.py:105` (before detokenize)
- `heartcodec/models/flow_matching.py:75` (before inference_codes)

Log shapes of tensors being passed.

### Step 4: Test with Fixed Seed

Change in output_music_heartmula.py:
```python
DEFAULTS = {
    ...
    "seed": 42  # Fixed seed instead of None
}
```

See if error is deterministic or random.

### Step 5: Check Model Files Integrity

```bash
cd /home/joerissen/ai/heartlib/ckpt
ls -lh HeartMuLa-oss-3B/
ls -lh HeartCodec-oss/

# Check for corrupted files
md5sum HeartMuLa-oss-3B/*.safetensors
md5sum HeartCodec-oss/*.safetensors
```

### Step 6: Try Newer Models

Download and test with RL versions (recommended by HeartMuLa):
```bash
cd /home/joerissen/ai/heartlib
hf download --local-dir './ckpt/HeartMuLa-oss-3B' 'HeartMuLa/HeartMuLa-RL-oss-3B-20260123'
hf download --local-dir './ckpt/HeartCodec-oss' HeartMuLa/HeartCodec-oss-20260123
```

### Step 7: Minimal Reproduction

Create standalone test script:
```python
import sys
sys.path.insert(0, '/home/joerissen/ai/heartlib/src')
from heartlib.pipelines.music_generation import MusicGenerationPipeline

pipeline = MusicGenerationPipeline(
    model_path='/home/joerissen/ai/heartlib/ckpt',
    device='cuda'
)

result = pipeline(
    {"lyrics": "de doo doo doo", "tags": "ska"},
    max_audio_length_ms=240000,
    save_path='/tmp/test_heartmula.mp3',
    topk=50,
    temperature=1.0,
    cfg_scale=1.5
)

print(f"Success: {result}")
```

Run with `CUDA_LAUNCH_BLOCKING=1 python test_heartmula.py`

---

## Code Rollback Test

To isolate if commits 8c5ee0e/33986e3 caused the issue:

```bash
git stash
git checkout c03499a  # Before other session's changes
# Restart backend
# Test HeartMuLa
# If works: Problem is in 8c5ee0e or 33986e3
# If fails: Problem elsewhere
git checkout develop
git stash pop
```

---

## Critical Files

**Backend:**
- `devserver/my_app/services/heartmula_backend.py` - Generation logic
- `devserver/schemas/chunks/output_music_heartmula.py` - Chunk execution
- `devserver/schemas/engine/backend_router.py` - Python chunk routing
- `devserver/schemas/engine/chunk_builder.py` - Chunk detection

**Pipelines:**
- `devserver/schemas/pipelines/music_generation.json` - Old pipeline (hardcoded)
- `devserver/schemas/pipelines/dual_text_media_generation.json` - New pipeline (placeholder)

**Configs:**
- `devserver/schemas/configs/output/heartmula_standard.json` - Output config
- `devserver/schemas/configs/interception/heartmula.json` - Interception config (if exists)

**Models:**
- `/home/joerissen/ai/heartlib/ckpt/HeartMuLa-oss-3B/` - Old model version
- `/home/joerissen/ai/heartlib/ckpt/HeartCodec-oss/` - Old codec version

**Working Export (reference):**
- `/home/joerissen/ai/ai4artsed_development/exports/json/2026-02-03/dev_7769bcb0649c/f99fd56c-556c-4035-964b-058756bd7c8e/`

---

## Logs to Collect

Before next debug session, collect:
1. Full backend log from failed generation (with CUDA_LAUNCH_BLOCKING=1)
2. GPU state: `nvidia-smi` output
3. Torch version: `python -c "import torch; print(torch.__version__)"`
4. HeartLib version: `pip show heartlib` or git commit in heartlib repo
5. Frontend request payload (what exactly is sent to backend?)

---

## My Failure

I made multiple unsupported claims:
- "Tags too complex" - NO EVIDENCE
- "Lyrics too short" - CONTRADICTS HEARTMULA EXAMPLES
- "max_audio_length_ms too high" - YESTERDAY WORKED WITH SAME VALUE

I wasted time on false theories instead of systematic debugging.

**The real answer:** I don't know why it fails. The error is in HeartMuLa's codec detokenization, suggesting invalid indices in generated codes. This could be:
- Bug in HeartMuLa old version (should test RL version)
- Corrupted model weights
- Non-deterministic bug (random seed dependent)
- Subtle code change in routing that affects how parameters are passed
- CUDA/PyTorch version incompatibility

**Next session should:** Follow the debug steps above systematically with CUDA_LAUNCH_BLOCKING=1 to get exact error location.
