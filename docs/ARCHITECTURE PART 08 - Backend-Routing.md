# DevServer Architecture

**Part 8: Backend Routing**

---

## ⚠️ PARTIALLY DEPRECATED (Session 65 - 2025-11-23)

**The execution_mode system described in this document is OBSOLETE.**

**What changed:** The execution_mode parameter ('eco', 'fast', 'local', 'remote') has been REMOVED. Model selection is now centralized in `devserver/config.py`.

**Migration:** See `ARCHITECTURE PART 01 - Section 2: Model Selection Architecture` for current implementation.

**Backend routing patterns (Ollama, ComfyUI, OpenRouter) remain valid.**

---


### Backend Types

| Backend | Type | Use Cases | Authentication | DSGVO |
|---------|------|-----------|----------------|-------|
| **Ollama** | Local | Text transformation, translation | None (local) | ✅ Compliant |
| **ComfyUI** | Local | Image/Audio/Music/Video generation | None (local) | ✅ Compliant |
| **OpenRouter** | Cloud | Fast text/image tasks | API Key required | ❌ Non-compliant |
| **OpenAI** | Cloud | GPT-5 Image, Sora2 Video (future) | API Key required | ⚠️ Enterprise only |

---

### ~~Execution Mode System: eco vs fast~~ [DEPRECATED - Session 65]

**⚠️ THIS SECTION IS OBSOLETE:** The execution_mode parameter system was completely removed in Session 65 (2025-11-23). Model selection is now handled centrally via constants in `devserver/config.py` (STAGE1_MODEL, STAGE2_INTERCEPTION_MODEL, etc.). See ARCHITECTURE PART 01 - Section 2 for current implementation.

**Historical documentation (for reference only):**

The DevServer ~~implements~~ **implemented** a simple **two-mode execution system** that ~~determines~~ **determined** whether tasks run locally or remotely:

| Mode | Priority | Backends | Cost | Speed | DSGVO |
|------|----------|----------|------|-------|-------|
| **eco** | Local resources | Ollama, ComfyUI | Free | Slower | ✅ Compliant |
| **fast** | Cloud APIs | OpenRouter, OpenAI | Paid | Faster | ⚠️ Depends on provider |

**Mode Selection Logic:**
1. **User Switch (Frontend):** User can toggle eco/fast mode in UI
2. **Server Default (server.config.py):** Fallback if no user preference
3. **Config Override (optional):** Specific configs can force eco mode (e.g., DSGVO-sensitive tasks)

---

### Routing Logic Details

#### 1. Text Transformation (LLM Tasks)

**eco mode:**
```python
Backend: Ollama (local)
Models: mistral-nemo, llama3.2, gemma2, qwen2.5-translator
Cost: Free
DSGVO: Compliant (all data stays local)
```

**fast mode:**
```python
Backend: OpenRouter (cloud) - or configured alternative
Models: claude-3.5-haiku, gemini-2.5-pro, mistral-nemo (cloud)
Cost: ~$0.10-0.18 per 1M tokens
DSGVO: Depends on provider (OpenRouter: non-compliant)

Note: Cloud provider is configured in server.config.py
      Administrator decides which services to use based on DSGVO research
```

---

#### 2. Media Generation (Image/Audio/Music/Video)

**2a. Image Generation**

**eco mode:**
```python
Backend: ComfyUI (local)
Models:
  - Stable Diffusion 3.5 Large (default)
  - Flux1 Development
  - SD1.5 / SDXL (legacy)
Cost: Free (GPU usage)
Quality: High (full control over parameters)
Speed: ~20-60 seconds per image
DSGVO: Compliant
```

**fast mode:**
```python
Backend: OpenRouter (cloud)
Model: GPT-5 Image (via OpenRouter or direct OpenAI)
Cost: TBD (GPT-5 pricing not yet public)
Quality: TBD
Speed: ~5-15 seconds per image
DSGVO: Non-compliant (OpenRouter) or Enterprise-only (OpenAI direct)

Status: Planned, not yet implemented
```

---

**2b. Audio Generation (Sound Effects, Ambience)**

**eco mode:**
```python
Backend: ComfyUI (local)
Model: Stable Audio Open
Input: Single text prompt (e.g., "ocean waves crashing")
Output: Audio file (47 seconds, WAV)
Cost: Free
DSGVO: Compliant
```

**fast mode:**
```python
Backend: Not yet implemented
Model: TBD (no suitable OpenRouter audio model available)
Status: Placeholder for future implementation

Note: OpenRouter does not currently offer audio generation APIs
```

---

**2c. Music Generation (with Tags + Lyrics)**

**eco mode:**
```python
Backend: ComfyUI (local)
Model: AceStep (ace_step_v1_3.5b.safetensors)
Input:
  - Prompt 1 (Tags): "upbeat, electronic, 120bpm"
  - Prompt 2 (Lyrics): "Dancing through the night..."
Output: Music file (47 seconds, WAV)
Cost: Free
DSGVO: Compliant
```

**fast mode:**
```python
Backend: Not yet implemented
Model: TBD (Suno AI? Udio? via OpenRouter or direct API)
Status: Placeholder for future implementation

Note: Music generation with lyrics is rare in cloud APIs
```

---

**2d. Video Generation (Future)**

**eco mode:**
```python
Backend: ComfyUI (local)
Model: TBD (AnimateDiff? Stable Video Diffusion?)
Cost: Free (but GPU-intensive)
Speed: Very slow (minutes per video)
DSGVO: Compliant
Status: Not yet implemented
```

**fast mode:**
```python
Backend: OpenAI (direct API)
Model: Sora2
Cost: Per-second pricing (e.g., $0.10-0.50 per second of video)
Speed: Fast (seconds to low-resolution, minutes to high-res)
DSGVO: Enterprise-only
Status: Planned, not yet implemented
```

---

### ~~Backend Selection Algorithm~~ [DEPRECATED - Session 65]

**⚠️ THIS ALGORITHM IS OBSOLETE:** The execution_mode-based routing described below was removed in Session 65. Model selection is now centralized in `devserver/config.py`. Backend routing still exists but is determined by model constants, not execution_mode parameter.

**Historical documentation (for reference only):**

**Step 1: Determine Task Type**
```python
if pipeline == "text_transformation":
    task_category = "LLM"
elif pipeline in ["single_text_media_generation", "dual_text_media_generation"]:
    task_category = "MEDIA_GENERATION"
    media_type = config.media_preferences.default_output  # "image", "audio", "music", "video"
```

**Step 2: Check Execution Mode**
```python
# Priority order:
execution_mode = (
    user_preference_from_frontend  # User toggled eco/fast switch
    or config.meta.get("force_eco")  # Config forces eco mode (DSGVO)
    or server_config.DEFAULT_EXECUTION_MODE  # Server default (usually "eco")
)
```

**Step 3: Route to Backend**
```python
if task_category == "LLM":
    if execution_mode == "eco":
        backend = "ollama"
        model = model_selector.get_local_model(task_type)
    elif execution_mode == "fast":
        # Use cloud service configured in server.config.py
        backend = server_config.LLM_SERVICES["cloud"]["provider"]  # "openrouter"
        model = model_selector.get_cloud_model(task_type)

elif task_category == "MEDIA_GENERATION":
    if execution_mode == "eco":
        backend = "comfyui"
        workflow = get_comfyui_workflow(media_type, config.meta.model)
    elif execution_mode == "fast":
        # Check if remote service is configured for this media type
        remote_service = server_config.REMOTE_SERVICES.get(media_type)

        if remote_service and remote_service["provider"]:
            backend = remote_service["provider"]
            model = remote_service["model"]
        else:
            # Fallback to local if no remote service configured
            backend = "comfyui"
            workflow = get_comfyui_workflow(media_type, config.meta.model)
```

**Step 4: Execute**
```python
result = backend_router.execute(
    backend=backend,
    model=model,
    workflow=workflow,
    input_data=processed_input,
    config_params=config.parameters
)
```

---

### ~~Remote Service Configuration (server.config.py)~~ [DEPRECATED - Session 65]

**⚠️ THIS CONFIGURATION PATTERN IS OBSOLETE:** The execution_mode-based service selection was removed in Session 65. Model/service selection is now handled via constants in `devserver/config.py`, not via execution_mode switching.

**Historical documentation (for reference only):**

The server ~~maintains~~ **maintained** centralized configuration for remote services:

```python
# server.config.py

# Default execution mode (eco = local, fast = cloud) [DEPRECATED]
DEFAULT_EXECUTION_MODE = "eco"

# Remote service endpoints (used when execution_mode == "fast") [DEPRECATED]
REMOTE_SERVICES = {
    "image": {
        "provider": "openrouter",  # or "openai" for direct GPT-5 access
        "model": "gpt-5-image",  # Placeholder - not yet available
        "api_key": os.getenv("OPENROUTER_API_KEY"),
        "fallback_to_local": True  # Use ComfyUI if API fails
    },
    "audio": {
        "provider": None,  # No cloud provider yet
        "fallback_to_local": True
    },
    "music": {
        "provider": None,  # No cloud provider yet (Suno? Udio?)
        "fallback_to_local": True
    },
    "video": {
        "provider": "openai",  # Sora2 via OpenAI direct API
        "model": "sora-2",  # Placeholder
        "api_key": os.getenv("OPENAI_API_KEY"),
        "cost_per_second": 0.20,  # Estimated
        "fallback_to_local": False  # No local video generation yet
    }
}

# LLM Services
LLM_SERVICES = {
    "local": {
        "provider": "ollama",
        "base_url": "http://localhost:11434"
    },
    "cloud": {
        "provider": "openrouter",
        "api_key": os.getenv("OPENROUTER_API_KEY"),
        "base_url": "https://openrouter.ai/api/v1"
    }
}
```

---

### DSGVO Considerations

**Current Status:**
- ✅ **eco mode:** Fully DSGVO-compliant (all data stays local)
- ❌ **fast mode (OpenRouter):** Non-compliant (data routed through US/UK servers)

**Administrator Responsibilities:**
- Research and select DSGVO-compliant cloud providers for fast mode
- Update `server.config.py` with compliant services
- Potential EU-based alternatives:
  - Mistral AI (direct API, France-based)
  - DeepL (for translation, Germany-based)
  - OpenAI Enterprise (with DSGVO BAA, expensive)
  - Self-hosted Ollama on EU servers (slower than cloud, compliant)

**Implementation Options:**
1. **Default eco mode:** Keep all educational workshops on local processing
2. **Dual configuration:** Separate server.config.py for research vs workshop environments
3. **Config-level override:** Add `meta.force_eco = true` for sensitive workflows

**Current Default:**
- eco mode for all operations
- fast mode available but requires explicit activation + DSGVO review

---

### SwarmUI/ComfyUI Auto-Recovery

**Added:** Session 113 (2026-01-11)

**Problem:** DevServer crashed when SwarmUI/ComfyUI backend was not running, displaying connection errors to users.

**Solution:** Automatic lifecycle management via SwarmUI Manager service.

#### Architecture

**Service:** `devserver/my_app/services/swarmui_manager.py`
**Pattern:** Singleton with lazy initialization (on-demand)

**Key Features:**
1. **Automatic Detection:** Health checks on ports 7801 (SwarmUI REST API) and 7821 (ComfyUI backend)
2. **On-Demand Startup:** Only starts SwarmUI when actually needed (lazy initialization)
3. **Crash Recovery:** Handles both startup scenarios AND runtime crashes
4. **Race-Condition Safe:** asyncio.Lock with double-check pattern prevents duplicate startups
5. **Configurable:** Environment variables for timeout, polling interval, enable/disable

#### Integration Points

**BackendRouter** (`backend_router.py`):
- Constructor: Initializes SwarmUI Manager singleton (line 150)
- Text2Image: Auto-start before generation (line 550)
- Workflow Submission: Auto-start before workflow (line 684)
- Image Upload (single): Auto-start before upload (line 893)
- Image Upload (multi): Auto-start before batch upload (line 941)

**LegacyWorkflowService** (`legacy_workflow_service.py`):
- Workflow Execution: Auto-start before submission (line 95)

#### Configuration

**File:** `devserver/config.py`

```python
SWARMUI_AUTO_START = os.environ.get("SWARMUI_AUTO_START", "true").lower() == "true"
SWARMUI_STARTUP_TIMEOUT = int(os.environ.get("SWARMUI_STARTUP_TIMEOUT", "120"))  # seconds
SWARMUI_HEALTH_CHECK_INTERVAL = float(os.environ.get("SWARMUI_HEALTH_CHECK_INTERVAL", "2.0"))  # seconds
```

**Environment Overrides:**
```bash
export SWARMUI_AUTO_START=false          # Disable for testing
export SWARMUI_STARTUP_TIMEOUT=180       # Increase timeout
export SWARMUI_HEALTH_CHECK_INTERVAL=1.0 # Poll more frequently
```

#### Startup Behavior

**Typical Sequence:**
1. User triggers image generation (e.g., sd35_large config)
2. BackendRouter calls `swarmui_manager.ensure_swarmui_available()`
3. Manager detects SwarmUI is not running (health check fails)
4. Manager executes `2_start_swarmui.sh` via subprocess
5. Manager polls health endpoints every 2 seconds
6. After ~45 seconds: SwarmUI is ready
7. Image generation proceeds normally

**Startup Time:** 30-60 seconds (depends on hardware)
**User Experience:** Frontend shows "processing" spinner during auto-start

#### Browser Tab Prevention

**Problem:** SwarmUI opens browser tab on startup, hiding the frontend.

**Solution:** Command-line override in startup script:
```bash
./launch-linux.sh --launch_mode none
```

**Why This Works:**
- SwarmUI supports `--launch_mode` command-line argument (Program.cs)
- Overrides `LaunchMode: web` setting in SwarmUI's Settings.fds
- Works on ANY SwarmUI installation (no settings file modification needed)
- Portable solution for third-party installations

#### Benefits

1. **Independence:** DevServer starts without requiring SwarmUI to be running
2. **Resilience:** Automatic recovery from SwarmUI crashes during operation
3. **User Experience:** No manual intervention needed, no hidden browser tabs
4. **Performance:** Lazy initialization - only starts when media generation requested
5. **Safety:** Race-condition proof via double-check locking pattern
6. **Flexibility:** Configurable timeout and polling intervals
7. **Portability:** Works with any SwarmUI installation

#### Error Handling

**Script Not Found:**
```
[SWARMUI-MANAGER] Startup script not found: /path/to/2_start_swarmui.sh
[SWARMUI-MANAGER] Please start SwarmUI manually
```

**Timeout (120s):**
```
[SWARMUI-MANAGER] Timeout after 120s
[SWARMUI-MANAGER] Check SwarmUI logs for startup issues
```

**Auto-Start Disabled:**
```
[SWARMUI-MANAGER] Auto-start disabled, SwarmUI not available
```

#### Design Rationale

**Why Lazy (On-Demand) vs. Eager (Startup)?**
- ✅ Faster DevServer startup (no 60s SwarmUI wait)
- ✅ Handles runtime crashes (not just startup)
- ✅ Only loads when needed (user might not use media generation)
- ✅ Better separation of concerns

**Why Not Check at DevServer Startup?**
- User might not need media generation in this session
- SwarmUI could crash during operation (eager check doesn't help)
- Adds unnecessary 60-second delay to every DevServer restart
- Lazy approach handles all scenarios with better UX

#### Documentation

**Detailed Architecture:** See `ARCHITECTURE PART 07 - Engine-Modules.md` Section 12
**Development Log:** Session 113 (2026-01-11)
**Commit:** `bbe04d8` - feat(swarmui): Add auto-recovery with SwarmUI Manager service

---

### LoRA Injection for Image Generation

**Added:** Session 114 (2026-01-11)

**Purpose:** Automatically inject LoRA (Low-Rank Adaptation) models into ComfyUI workflows for personalized image generation (e.g., face LoRAs, style LoRAs).

#### Architecture

**Location:** `devserver/schemas/engine/backend_router.py`
**Method:** `_inject_lora_nodes(workflow, loras)`

**Key Features:**
1. **Dynamic Injection:** LoRA nodes inserted at runtime, no workflow template changes needed
2. **Chaining:** Multiple LoRAs chain in sequence: Checkpoint → LoRA1 → LoRA2 → KSampler
3. **Auto-Connection:** Finds CheckpointLoader and model consumers, updates connections automatically
4. **SD3.5 Support:** Handles DualCLIPLoader for SD3.5 workflows

#### Data Flow

```
Stage 4 Request
     ↓
_process_output_chunk()
     ↓
if LORA_TRIGGERS:  → Use workflow mode (not simple API)
     ↓
_process_workflow_chunk()
     ↓
workflow = chunk.get('workflow')
     ↓
if LORA_TRIGGERS:
    workflow = _inject_lora_nodes(workflow, LORA_TRIGGERS)
     ↓
Submit to SwarmUI/ComfyUI
```

#### Configuration

**Current:** Temporary hardcoded in `config.py`

```python
LORA_TRIGGERS = [
    {"name": "SD3.5-Large-Anime-LoRA.safetensors", "strength": 1.0},
    {"name": "bejo_face.safetensors", "strength": 1.0},
]
```

**Future:** Connected to Stage2-Configs (Meta-Prompt + optimal LoRAs):
```json
{
  "name": "jugendsprache",
  "context_prompt": "...",
  "loras": [
    {"name": "anime_style.safetensors", "strength": 0.8}
  ]
}
```

#### Workflow Modification

**Before Injection:**
```
Node 5 (CheckpointLoaderSimple) → Node 8 (KSampler)
```

**After Injection:**
```
Node 5 (CheckpointLoaderSimple)
     ↓
Node 12 (LoraLoader: anime_style)
     ↓
Node 13 (LoraLoader: bejo_face)
     ↓
Node 8 (KSampler)
```

#### Routing Behavior

When `LORA_TRIGGERS` is configured:
- Images use **workflow mode** (not SwarmUI Text2Image API)
- Enables full ComfyUI node manipulation
- Slightly slower but supports advanced features

```python
if LORA_TRIGGERS:
    return await self._process_workflow_chunk(...)
else:
    return await self._process_image_chunk_simple(...)
```

#### Documentation

**Development Log:** Session 114 (2026-01-11)

---

