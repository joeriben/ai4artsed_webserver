# DevServer Architecture

**Part 8: Backend Routing**

---


### Backend Types

| Backend | Type | Use Cases | Authentication | DSGVO |
|---------|------|-----------|----------------|-------|
| **Ollama** | Local | Text transformation, translation | None (local) | ✅ Compliant |
| **ComfyUI** | Local | Image/Audio/Music/Video generation | None (local) | ✅ Compliant |
| **OpenRouter** | Cloud | Fast text/image tasks | API Key required | ❌ Non-compliant |
| **OpenAI** | Cloud | GPT-5 Image, Sora2 Video (future) | API Key required | ⚠️ Enterprise only |

---

### Execution Mode System: eco vs fast

The DevServer implements a simple **two-mode execution system** that determines whether tasks run locally or remotely:

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

### Backend Selection Algorithm

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

### Remote Service Configuration (server.config.py)

The server maintains centralized configuration for remote services:

```python
# server.config.py

# Default execution mode (eco = local, fast = cloud)
DEFAULT_EXECUTION_MODE = "eco"

# Remote service endpoints (used when execution_mode == "fast")
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

