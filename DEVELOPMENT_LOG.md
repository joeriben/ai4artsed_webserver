# Development Log

## Session 125 - Watermarking & Content Credentials Integration
**Date:** 2026-01-20
**Duration:** ~1.5 hours
**Focus:** Add invisible watermarks and C2PA Content Credentials to generated images
**Status:** SUCCESS (Watermark active, C2PA ready for production certificates)

### Background
Research into provenance tracking for AI-generated images:
- [Content Credentials](https://contentcredentials.org/) - C2PA standard for cryptographic provenance
- [invisible-watermark](https://github.com/ShieldMnt/invisible-watermark) - DWT-DCT invisible watermarking

### Implementation

**Invisible Watermark (ACTIVE):**
- Embeds "AI4ArtsEd" text invisibly into all generated images
- Uses DWT-DCT method (fastest, ~300ms for 1080p)
- Survives JPEG compression, noise, brightness changes
- Integrated into `pipeline_recorder.py` - automatic for all image outputs

**C2PA Content Credentials (READY, disabled):**
- Full service implementation complete
- Requires CA-issued certificates (self-signed not allowed by spec)
- Will add: Creator, timestamp, AI-training prohibition assertions
- Verifiable at: https://verify.contentcredentials.org/

### Key Finding
C2PA standard explicitly prohibits self-signed certificates for security reasons. Production deployment requires certificates from a C2PA-recognized Certificate Authority.

### Files Created
- ✨ `my_app/services/watermark_service.py` - Watermark embedding/extraction
- ✨ `my_app/services/c2pa_service.py` - C2PA manifest signing
- 📁 `devserver/certs/` - Certificate directory (key in .gitignore)

### Files Modified
- 📦 `requirements.txt` - Added invisible-watermark, c2pa-python, opencv-python
- ⚙️ `devserver/config.py` - ENABLE_WATERMARK, WATERMARK_TEXT, C2PA settings
- 🔧 `my_app/services/pipeline_recorder.py` - Integration into image save flow

### Configuration
```python
ENABLE_WATERMARK = True          # Active
WATERMARK_TEXT = "AI4ArtsEd"     # Embedded text
ENABLE_C2PA = False              # Needs CA certificates
```

### Verification
```python
from my_app.services.watermark_service import WatermarkService
service = WatermarkService("AI4ArtsEd")
extracted = service.extract_watermark(image_bytes)
# Returns "AI4ArtsEd" if watermark present
```

---

## Session 124 - LoRA Epoch & Strength Fine-Tuning
**Date:** 2026-01-18
**Duration:** ~45 minutes
**Focus:** Optimize LoRA training epoch and strength parameters
**Status:** SUCCESS - Reduced overfitting, improved prompt adherence

### Problem
LoRA-enhanced generations (e.g., "Cooked Negatives" style) were showing overfitting artifacts:
- Epoch 6 weights showed too strong stylistic dominance
- Strength 0.6 still caused prompt content to be ignored in some cases

### Investigation
Tested different epoch checkpoints and strength combinations:
- **Epoch 6 @ 0.6:** Overfitting visible, prompt partially ignored
- **Epoch 4 @ 0.6:** Better balance, style present without overwhelming
- **Epoch 4 @ 0.75:** Good for stronger styles (tested with cooked_negatives)

### Solution
1. **Use Earlier Epoch (4 instead of 6):**
   - Earlier checkpoints capture style essence without memorizing training data
   - Reduces overfitting artifacts

2. **Calibrate Strength Per LoRA:**
   - cooked_negatives: 0.75 (stronger film artifact effect desired)
   - Other LoRAs: 0.6 as baseline

### Key Insight
**LoRA Training Best Practices:**
- Don't always use final epoch - test intermediate checkpoints
- Epoch 4-5 often better than epoch 6+ for style transfer
- Strength and epoch interact: earlier epoch may need higher strength

### Files Changed
- 📝 `devserver/schemas/configs/interception/cooked_negatives.json` (epoch: 6 → 4, strength: 0.6 → 0.75)

### Commits
- `c015937` - fix(lora): Use earlier epoch (4) to reduce overfitting
- `f1d0f55` - feat(lora): Tune strength to 0.6 and document findings
- `09ffe7a` - fix(lora): Reduce cooked_negatives strength to 0.75

---

## Session 123 - Legacy View Migration & LoRA Badge Display
**Date:** 2026-01-17
**Duration:** ~1.5 hours
**Focus:** Migrate legacy views to /legacy endpoint, add LoRA indicators
**Status:** SUCCESS - Clean separation, visual LoRA feedback

### Legacy View Migration

**Problem:**
Legacy views (Surrealizer, Split&Combine, Partial Elimination) were mixed with new Lab-paradigm views, causing routing confusion.

**Solution:**
Created dedicated `/legacy` endpoint grouping:
- `/legacy/surrealizer`
- `/legacy/split-and-combine`
- `/legacy/partial-elimination`

**Benefits:**
- Clear separation between Lab (new) and Legacy workflows
- Easier maintenance and eventual deprecation
- Consistent routing patterns

### LoRA Badge Display

**Feature:**
Visual indicator when interception configs have associated LoRAs.

**Implementation:**
- Badge appears on config tiles with LoRA-enhanced styles
- Shows LoRA icon when `meta.loras` array is present in config
- Helps users understand which styles use custom models

### Files Changed
- 🔧 `devserver/my_app/routes/schema_pipeline_routes.py` (legacy endpoint grouping)
- ✨ `public/ai4artsed-frontend/src/components/ConfigTile.vue` (LoRA badge)
- 📝 Router configuration updates

### Commits
- `d0e85f6` - refactor: migrate legacy views to /legacy endpoint
- `1c41dc9` - feat(lora): Add LoRA badge display for interception configs

---

## Session 122 - Unified Export System & Partial Elimination Improvements
**Date:** 2026-01-17
**Duration:** ~3 hours
**Focus:** Fix broken export, enhance partial elimination workflow
**Status:** SUCCESS - Export working across all backends

### Unified Export Fix

**Critical Problem:**
Export function was BROKEN - entities scattered across multiple folders:
- `/interception` created `run_xxx/` with input, safety, interception
- `/generation` created `run_yyy/` with output_image
- Result: Incomplete exports, no unified research data

**Solution:**
Frontend passes `run_id` from `/interception` to `/generation`:
- Backend loads existing Recorder via `load_recorder()`
- All entities saved to ONE unified folder
- Complete research units for export

**Multi-Backend Image Saving:**
All backends now properly save images:
- SD3.5: Via SwarmUI API (unchanged)
- QWEN/FLUX2: Read from `filesystem_path`
- Gemini/GPT-Image: Decode from base64

### Partial Elimination Improvements

**Dual-Handle Slider:**
- New range slider for dimension selection
- Users can select min/max range with two handles
- More intuitive than separate min/max inputs

**Encoder Selector:**
- Added dropdown to choose encoding method
- Options: CLIP, T5, Combined
- Affects how prompts are processed for image generation

### Files Changed
- 🔧 `devserver/my_app/routes/schema_pipeline_routes.py` (unified export logic)
- ✨ `public/ai4artsed-frontend/src/views/partial_elimination.vue` (dual slider, encoder)
- 📝 `devserver/schemas/workflows/partial_elimination.json` (encoder support)

### Commits
- `7f07197` - fix(export): Unified run_id and fix image saving for all backends
- `5c9e792` - feat(partial-elimination): Dual-handle slider for dimension range selection
- `5e4139e` - feat(partial-elimination): Encoder selector and workflow improvements

---

## Session 121 - VRAM Management & Config Path Consolidation
**Date:** 2026-01-13
**Duration:** ~2 hours
**Focus:** Automatic VRAM management for training, consolidate hardcoded paths
**Status:** SUCCESS - Training more reliable, paths centralized

### VRAM Management for LoRA Training

**Problem:**
LoRA training would fail when SD3.5 model was loaded in VRAM:
- Training requires ~18GB VRAM
- SD3.5 Large uses ~12GB VRAM
- Combined exceeds typical 24GB GPU limit

**Solution:**
Automatic VRAM cleanup before training:
1. Check available VRAM before training starts
2. Unload SD3.5 model from SwarmUI if needed
3. Proceed with training
4. Model reloads automatically on next generation

**Implementation:**
```python
async def ensure_vram_available(required_gb: int = 18):
    """Unload models if VRAM insufficient for training."""
    if get_available_vram() < required_gb:
        await unload_swarmui_models()
```

### Config Path Consolidation

**Problem:**
Hardcoded paths scattered throughout codebase:
- LoRA output paths in multiple files
- Training dataset paths inconsistent
- Workflow paths duplicated

**Solution:**
Centralized all paths in `config.py`:
```python
LORA_OUTPUT_DIR = "/home/joerissen/ai/SwarmUI/Models/Lora"
TRAINING_DATASET_DIR = "/home/joerissen/ai/ai4artsed_development/training_data"
COMFYUI_WORKFLOWS_DIR = "/home/joerissen/ai/SwarmUI/ComfyUI/custom_nodes/ai4artsed_comfyui_workflows"
```

### Files Changed
- 📝 `devserver/config.py` (centralized paths, VRAM config)
- 🔧 `devserver/my_app/services/training_service.py` (VRAM management)
- 🔧 Various files (path references updated)

### Commits
- `f373530` - feat(training): Add VRAM management and WiFi-reliable uploads
- `22105e3` - fix(training): Move hardcoded paths to config.py
- `ca31581` - fix(training): Correct LoRA output path to /loras

---

## Session 120 - LoRA Injection Architecture & SwarmUI Auto-Recovery
**Date:** 2026-01-11
**Duration:** ~4 hours
**Focus:** Config-based LoRA injection, automatic SwarmUI lifecycle management
**Status:** SUCCESS - LoRA system complete, auto-recovery working

### Config-Based LoRA Injection

**Evolution from Session 114:**
Instead of hardcoded LoRA list, now reads from interception configs:
```json
{
  "name": "cooked_negatives",
  "meta": {
    "loras": [
      {"name": "sd3.5-large_cooked_negatives.safetensors", "strength": 1.0}
    ]
  }
}
```

**Benefits:**
- Each style can have optimal LoRA(s)
- No code changes needed for new LoRAs
- Strength configurable per style

### SwarmUI Auto-Recovery

See Session 113 for full details. This session completed the integration:
- All backend routes now call `ensure_swarmui_available()`
- Handles both initial startup and runtime crashes
- Browser tab prevention implemented

### Files Changed
- 📝 `devserver/schemas/configs/interception/*.json` (LoRA metadata)
- 🔧 `devserver/schemas/engine/backend_router.py` (config-based injection)
- ✨ `devserver/my_app/services/swarmui_manager.py` (auto-recovery)

### Commits
- `e2d247b` - feat: Implement LoRA injection for Stage 4 workflows
- `a69d2cb` - feat(lora): Implement config-based LoRA injection for Stage 4
- `bbe04d8` - feat(swarmui): Add auto-recovery with SwarmUI Manager service

---

## Session 119 - LoRA Training Studio
**Date:** 2026-01-09
**Duration:** ~5 hours
**Focus:** Build LoRA training UI and backend integration
**Status:** SUCCESS - Complete training pipeline from UI to output

### Feature Overview
New "Training Studio" section in the application:
- Upload training images directly in browser
- Configure training parameters (steps, learning rate, etc.)
- Start training from UI
- Monitor progress via SSE events
- Automatic LoRA file placement in SwarmUI Models folder

### Architecture

**Frontend (`LoraTrainingStudio.vue`):**
- Multi-image upload with drag & drop
- Training parameter form (caption, steps, epochs)
- Progress indicator during training
- Support for multiple comma-separated trigger words

**Backend (`training_service.py`):**
- Kohya-ss based training pipeline
- SD3.5 Large as base model
- Configurable output directory
- SSE progress streaming

**Training Configuration:**
```python
TRAINING_CONFIG = {
    "base_model": "sd3.5-large",
    "steps_per_image": 100,
    "learning_rate": 1e-4,
    "epochs": 6,
    "resolution": 1024
}
```

### Workflow
1. User uploads 5-20 training images
2. Sets trigger word(s) and caption template
3. Clicks "Start Training"
4. Backend prepares dataset, runs training
5. Progress streamed to frontend
6. LoRA file automatically placed in SwarmUI/Models/Lora/

### Files Created
- ✨ `public/ai4artsed-frontend/src/views/LoraTrainingStudio.vue` (Frontend UI)
- ✨ `devserver/my_app/services/training_service.py` (Training backend)
- ✨ `devserver/my_app/routes/training_routes.py` (API endpoints)

### Files Modified
- 📝 `devserver/config.py` (training configuration)
- 📝 Router registration

### Commit
- `f21a56b` - Feat: Add LoRA Training Studio (Backend + Frontend)

---

## Session 118 - SSE Queue Feedback System
**Date:** 2026-01-08
**Duration:** ~2 hours
**Focus:** Visual feedback when requests are queued
**Status:** SUCCESS - Users see queue status in UI

### Problem
With the request queueing system from Session 112, users had no indication their request was waiting. The UI just showed "loading" with no context.

### Solution: SSE Queue Events

**Backend Enhancement:**
New SSE event type `queue_status`:
```python
yield f"event: queue_status\ndata: {json.dumps({
    'status': 'waiting',
    'message': 'Warte auf freien Slot... (5s)'
})}\n\n"
```

**Frontend Visualization:**
- Spinner changes color: Blue (processing) → Red (queued)
- Loading text shows queue message
- Automatic color reset when slot acquired

### Implementation Details

**Backend (`schema_pipeline_routes.py`):**
- Queue wait loop yields status every 1 second
- Includes wait time in message
- Seamlessly transitions to normal processing

**Frontend (`MediaInputBox.vue`):**
- Added `queue_status` event listener
- CSS class `.spinner-large.queued` for red state
- Loading text pulses while queued

### User Experience
**Before:**
```
[Spinner spinning]
"Transformiere..."
(no indication of queue)
```

**After:**
```
[RED Spinner spinning]
"Warte auf freien Slot... (12s)"
(clear queue feedback)
```

### Files Changed
- 🔧 `devserver/my_app/routes/schema_pipeline_routes.py` (SSE events)
- 🔧 `public/ai4artsed-frontend/src/components/MediaInputBox.vue` (visual feedback)
- 📝 CSS additions for queued state

### Commits
- `76308cb` - feat: Add SSE Queue Feedback loop to backend
- `96ef55b` - feat: Add Frontend Queue Feedback (red spinner)
- `9399c16` - feat: Implement request queueing for Ollama

---

## Session 117 - LoRA Strength Tuning for Interception Configs
**Date:** 2026-01-17
**Duration:** ~30 minutes
**Focus:** Finding optimal LoRA strength for prompt/style balance
**Status:** SUCCESS - Strength calibrated

### Problem
LoRA injection was working (since Session 114/116), but at strength 1.0 the LoRA effect completely overrode the user's prompt content. Generated images showed only the LoRA style (e.g., film artifacts for Cooked Negatives) with no relevance to the actual prompt.

### Investigation
Compared generations with "Cooked Negatives" interception config:
- **Strength 1.0:** Full film artifact effect, but prompt completely ignored
- **Strength 0.5:** Effect barely visible
- **Strength 0.6:** Good balance - film artifacts visible AND prompt content preserved

### Solution
Adjusted LoRA strength in interception config:
```json
{
  "meta": {
    "loras": [
      {"name": "sd3.5-large_cooked_negatives.safetensors", "strength": 0.6}
    ]
  }
}
```

### Key Insight
**LoRA Strength Trade-off:**
- High strength (0.8-1.0): Style dominates, prompt ignored
- Low strength (0.3-0.5): Style barely visible
- Sweet spot (0.5-0.7): Balance between style and prompt adherence

This varies per LoRA - some are stronger than others. Each interception config should test and calibrate its LoRA strength individually.

### Files Changed
- 📝 `devserver/schemas/configs/interception/cooked_negatives.json` (strength: 1.0 → 0.6)

---

## Session 116 - Config-Based LoRA System Design
**Date:** 2026-01-10
**Duration:** ~1 hour
**Focus:** Design config schema for LoRA associations
**Status:** SUCCESS - Schema designed, documented

### Design Decision
Each interception config can optionally define LoRAs in a `meta` object:

```json
{
  "name": "cooked_negatives",
  "context_prompt": "...",
  "meta": {
    "loras": [
      {"name": "sd3.5-large_cooked_negatives.safetensors", "strength": 1.0}
    ],
    "recommended_models": ["sd35_large"],
    "style_tags": ["film", "vintage", "analog"]
  }
}
```

### Schema Benefits
- **Extensible:** `meta` object can hold any config-specific metadata
- **Optional:** Configs without LoRAs work exactly as before
- **Multi-LoRA:** Array supports stacking multiple LoRAs
- **Per-Config Strength:** Each config tunes its own LoRA strength

### Documentation
- Updated DEVELOPMENT_DECISIONS.md with LoRA schema rationale
- Added architecture docs for LoRA Training Studio

### Commits
- `a81e7cf` - docs: Add LoRA Training Studio architecture and design decisions

---

## Session 115 - Complete Icon System Migration to Material Design
**Date:** 2026-01-08
**Duration:** ~3 hours
**Focus:** Replace all emoji icons with Google Material Design SVGs
**Status:** SUCCESS - Complete icon system overhaul

### Problem Identified

**Emoji Icons Throughout UI**
- Emoji icons (lightbulb, clipboard, image, etc.) used inconsistently across the entire frontend
- Visually dominant and distracting from content
- Inconsistent rendering across browsers/OS
- Limited customization options (size, color transitions)

**Config Bubbles Rendering as Ellipses**
- CSS class name collision between PropertyCanvas and ConfigTile
- Both used `.config-bubble` with conflicting styles

### Solution Implemented

**Phase 1: Property Icons**
Replaced 8 property quadrant icons with Material Design SVGs:
- technical_imaging: photo_camera
- arts: museum
- attitudes: sentiment_content
- critical_analysis: diversity_2
- semantics: comic_bubble
- research: smart_toy
- aesthetics: wand_stars
- freestyle: stylus_note

**Phase 2: MediaInputBox Header Icons**
Added conditional SVG rendering for 6 icon types:
- lightbulb → emoji_objects
- clipboard → format_list_numbered
- arrow → line_end_arrow_notch
- stars → robot_2
- image → imagesmode
- plus → add_photo_alternate

**Phase 3: Image Icons Inside MediaBoxes**
- ImageUploadWidget: Replaced image emoji with SVG
- Category bubbles: image, video, sound icons

**Phase 4: CSS Collision Fix**
Renamed `.config-bubble` → `.property-config-bubble` in PropertyCanvas.vue

### Files Modified
- 14 new SVG icon assets
- 5 Vue components updated
- 8 interception configs renamed/updated

### Commits
- `fdc231d` through `6f1c0b3` - Icon migration series

---

## Session 114 - LoRA Injection for Stage 4 Workflows
**Date:** 2026-01-11
**Duration:** ~2 hours
**Focus:** Dynamic LoRA injection into ComfyUI workflows
**Status:** SUCCESS - LoRA injection working

### Goal
Enable LoRA models (e.g., face LoRAs, style LoRAs) to be automatically injected into Stage 4 image generation workflows.

### Background
Previous Cline session attempted "Dual-Parse" architecture (parsing `<lora:name:strength>` tags from prompts) but failed due to architectural issues. This session took a simpler approach: implement the injection mechanism first, decide WHERE the LoRA list comes from later.

### Solution: Workflow-Based LoRA Injection

**Key Insight:** Separate the injection mechanism from the data source.
1. Define LoRA list in `config.py` (temporary hardcoded)
2. Inject LoRALoader nodes into workflow at runtime
3. Later: connect to Stage2-Configs (Meta-Prompt + optimal LoRAs)

### Implementation

#### 1. Config (`config.py`)
```python
LORA_TRIGGERS = [
    {"name": "SD3.5-Large-Anime-LoRA.safetensors", "strength": 1.0},
    {"name": "bejo_face.safetensors", "strength": 1.0},
]
```

#### 2. Injection Logic (`backend_router.py`)
New method `_inject_lora_nodes()`:
- Finds CheckpointLoaderSimple node (model source)
- Finds model consumers (KSampler)
- Inserts LoRALoader nodes in chain: Checkpoint → LoRA1 → LoRA2 → KSampler
- Updates node connections automatically

#### 3. Routing Change
When `LORA_TRIGGERS` is configured, images use workflow mode instead of simple SwarmUI API:
```python
if LORA_TRIGGERS:
    return await self._process_workflow_chunk(...)
else:
    return await self._process_image_chunk_simple(...)
```

### Log Output (Success)
```
[LORA] Using workflow mode for image generation (LoRAs configured)
[LORA] Injected LoraLoader node 12: SD3.5-Large-Anime-LoRA.safetensors
[LORA] Injected LoraLoader node 13: bejo_face.safetensors
[LORA] Updated node 8 to receive model from LoRA chain
```

### Test Results
- ✅ Face LoRA (bejo_face) visible in output - works WITHOUT trigger word
- ✅ Multiple LoRAs chain correctly
- ✅ Workflow submission successful
- ⚠️ Style LoRA may need trigger word in prompt for visible effect

### Files Changed
- 📝 `devserver/config.py` (+10 lines - LORA_TRIGGERS config)
- 🔧 `devserver/schemas/engine/backend_router.py` (+80 lines - injection logic)

---

## Session 113 - SwarmUI Auto-Recovery System
**Date:** 2026-01-11
**Duration:** ~2 hours
**Focus:** Automatic SwarmUI lifecycle management
**Status:** SUCCESS - Full auto-recovery implemented

### Problem
DevServer crashed when SwarmUI was not running:
```
ClientConnectorError: Cannot connect to host 127.0.0.1:7821
```
**User Requirement:** DevServer should automatically detect and start SwarmUI when needed.

### Solution: SwarmUI Manager Service
Created new singleton service `swarmui_manager.py` for lifecycle management:

**Architecture Pattern:** Lazy Recovery (On-Demand)
- SwarmUI starts **only when needed** (not at DevServer startup)
- Handles both startup scenarios AND runtime crashes
- Faster DevServer startup
- Race-condition safe with `asyncio.Lock`

### Implementation

#### 1. SwarmUI Manager Service (`devserver/my_app/services/swarmui_manager.py`)
**Core Methods:**
- `ensure_swarmui_available()` - Main entry point, guarantees SwarmUI is running
- `is_healthy()` - Checks both ports (7801 REST API + 7821 ComfyUI backend)
- `_start_swarmui()` - Executes `2_start_swarmui.sh` via subprocess.Popen
- `_wait_for_ready()` - Polls health endpoints until ready or timeout (120s)

**Concurrency Safety:**
- `asyncio.Lock` prevents multiple threads from starting SwarmUI simultaneously
- Double-check pattern after acquiring lock

#### 2. Integration Points (5 locations)
**LegacyWorkflowService** (`legacy_workflow_service.py:95`):
- `ensure_swarmui_available()` before workflow submission

**BackendRouter** (`backend_router.py`):
- Line 150: Manager initialization in constructor
- Line 550: Before SwarmUI Text2Image generation
- Line 684: Before SwarmUI workflow submission
- Line 893: Before single image upload
- Line 941: Before multi-image upload

#### 3. Configuration (`config.py`)
```python
SWARMUI_AUTO_START = os.environ.get("SWARMUI_AUTO_START", "true").lower() == "true"
SWARMUI_STARTUP_TIMEOUT = int(os.environ.get("SWARMUI_STARTUP_TIMEOUT", "120"))  # seconds
SWARMUI_HEALTH_CHECK_INTERVAL = float(os.environ.get("SWARMUI_HEALTH_CHECK_INTERVAL", "2.0"))  # seconds
```

#### 4. Browser Tab Prevention
**Problem:** SwarmUI opened browser tab on startup, hiding the frontend.

**Solution:** Command-line override in `2_start_swarmui.sh`:
```bash
./launch-linux.sh --launch_mode none
```

### Expected Behavior
**Before:**
```
[ERROR] Cannot connect to host 127.0.0.1:7821
[ERROR] Workflow execution failed
```

**After:**
```
[SWARMUI-TEXT2IMAGE] Ensuring SwarmUI is available...
[SWARMUI-MANAGER] SwarmUI not available, starting...
[SWARMUI-MANAGER] Starting SwarmUI via: /path/to/2_start_swarmui.sh
[SWARMUI-MANAGER] SwarmUI process started (PID: 12345)
[SWARMUI-MANAGER] Waiting for SwarmUI (timeout: 120s)...
[SWARMUI-MANAGER] ✓ SwarmUI ready! (took 45.2s)
[SWARMUI] ✓ Generated 1 image(s)
```

### Benefits
- ✅ DevServer starts independently of SwarmUI
- ✅ Automatic crash recovery at runtime
- ✅ No manual intervention needed
- ✅ Frontend stays in focus (no SwarmUI UI popup)
- ✅ Works with any SwarmUI installation
- ✅ Configurable via environment variables

### Files Changed
- ✨ `devserver/my_app/services/swarmui_manager.py` (NEW - 247 lines)
- 📝 `devserver/config.py` (+7 lines - Auto-recovery configuration)
- 🔧 `devserver/my_app/services/legacy_workflow_service.py` (+9 lines - Manager integration)
- 🔧 `devserver/schemas/engine/backend_router.py` (+41 lines - Manager integration)
- 🚀 `2_start_swarmui.sh` (+3 lines - `--launch_mode none`)

**Commit:** `bbe04d8` - feat(swarmui): Add auto-recovery with SwarmUI Manager service

---

## Session 112 - CRITICAL: Fix Streaming Connection Leak (CLOSE_WAIT) & Queue Implementation
**Date:** 2026-01-08
**Duration:** ~2 hours
**Focus:** Fix connection leak and concurrent request overload (Ollama)
**Status:** SUCCESS - Connection cleanup implemented, Queue implemented

### Problem 1: Connection Leak (CLOSE_WAIT)
Production system (lab.ai4artsed.org) experiencing streaming failures:
- Cloudflared tunnel logs: "stream X canceled by remote with error code 0"
- Backend accumulating connections in CLOSE_WAIT state
- Eventually all streaming requests failing

### Fix 1: Streaming Cleanup
Implemented `GeneratorExit` handling and explicit `response.close()` in streaming generators:
1. `/devserver/schemas/engine/prompt_interception_engine.py:381`
2. `/devserver/my_app/services/ollama_service.py:366`
3. `/devserver/my_app/routes/schema_pipeline_routes.py:1278`

Result: CLOSE_WAIT connections now clear properly (tested with load test).

### Problem 2: Ollama Overload (Timeouts)
Under load (e.g. 10 parallel requests), Ollama (120b model) gets overloaded.
- Requests time out after 90s (default `OLLAMA_TIMEOUT`)
- Model execution takes 100-260s
- Parallel requests cause congestion and failures

### Fix 2: Request Queueing & Timeouts
1. **Request Queue:**
   - Implemented `threading.Semaphore(3)` in `schema_pipeline_routes.py`.
   - Limits concurrent heavy model executions to 3 (others wait).
   - Applied to Stage 1 safety checks in `execute_pipeline_streaming`, `execute_pipeline` (POST), and `execute_stage2`.

2. **Timeout Increase:**
   - Increased `OLLAMA_TIMEOUT` in `config.py` from 90s to 300s.

3. **Bug Fix:**
   - Fixed `SyntaxError` in `streaming_response.py` (f-string syntax) that prevented backend startup.

### Test Results
**Load Test (10 concurrent requests):**
- Backend: Running on port 17802 (Dev script)
- Queue Logic: Verified in logs
  ```
  [OLLAMA-QUEUE] Initialized with max concurrent requests: 3
  [OLLAMA-QUEUE] Stream ...: Waiting for queue slot...
  [OLLAMA-QUEUE] Stream ...: Acquired slot...
  [OLLAMA-QUEUE] Stream ...: Released slot
  ```
- All requests queued and processed sequentially without timeout errors.

### Files Changed
- 🔧 `devserver/schemas/engine/prompt_interception_engine.py` (cleanup)
- 🔧 `devserver/my_app/services/ollama_service.py` (cleanup)
- 🔧 `devserver/my_app/routes/schema_pipeline_routes.py` (queue, cleanup)
- 📝 `devserver/config.py` (timeout increase)

---

## Session 111 - CRITICAL: Unified Streaming Architecture Refactoring
**Date:** 2025-12-28
**Duration:** ~4 hours
**Focus:** Complete streaming architecture overhaul
**Status:** SUCCESS - SSE streaming unified across all endpoints

### Problem
Multiple streaming implementations with inconsistent behavior:
- Different SSE formats between endpoints
- Some endpoints missing streaming support
- Frontend handling varied per endpoint type

### Solution
Unified all streaming to consistent SSE format:
- All endpoints use same event types: `chunk`, `complete`, `error`
- Consistent JSON payload structure
- Frontend uses single handler for all streaming

### Implementation
Refactored 5 streaming endpoints to unified pattern.

### Files Changed
- Multiple route and service files updated for streaming consistency

---

*Earlier sessions documented in `docs/archive/DEVELOPMENT_LOG_Sessions_1-110.md`*
