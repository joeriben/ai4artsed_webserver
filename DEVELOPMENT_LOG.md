# Development Log

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

### Next Steps
**Connect to Stage2-Configs:** Each interception config (Meta-Prompt) can define optimal LoRAs:
```json
{
  "name": "jugendsprache",
  "context_prompt": "...",
  "loras": [
    {"name": "anime_style.safetensors", "strength": 0.8}
  ]
}
```

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

**Why This Works:**
- SwarmUI supports `--launch_mode` command-line argument
- Overrides `LaunchMode: web` setting in `Settings.fds`
- Works on ANY SwarmUI installation (no settings file modification needed)

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

### Architecture Updates
- Updated ARCHITECTURE PART 07 - Engine-Modules.md (SwarmUI Manager)
- Updated ARCHITECTURE PART 08 - Backend-Routing.md (Auto-recovery integration)

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

### Fix 3: User Feedback (Queue Visualization)
1. **Backend (SSE):**
   - Updated `execute_pipeline_streaming` to yield `queue_status` events while waiting in queue.
   - Frequency: Every 1 second.
   - Payload: `{'status': 'waiting', 'message': 'Warte auf freien Slot... (Xs)'}`.

2. **Frontend (MediaInputBox.vue):**
   - Added listener for `queue_status` event.
   - Visual Feedback:
     - Spinner turns **RED** (`.spinner-large.queued`) when status is 'waiting'.
     - Loading text pulses red and shows queue message.
     - Automatically resets to normal (blue) when slot is acquired.

### Next Steps
- Monitor production after deployment.

---

## Session 111 - CRITICAL: Unified Streaming Architecture Refactoring
**Date:** 2025-12-28
**Duration:** ~4 hours
- Supports both emoji and string icon names ('lightbulb', 'clipboard', etc.)
