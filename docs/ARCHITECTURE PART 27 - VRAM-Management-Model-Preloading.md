# DevServer Architecture

**Part 27: VRAM Management & Model Preloading**

---

## Overview

The Diffusers backend manages GPU-accelerated image generation models (SD3.5 Large, FLUX.2 Dev) that each consume 24-28GB VRAM. In workshop scenarios, participants switch between models frequently. This architecture provides:

1. **Three-Tier Memory Hierarchy** — GPU VRAM (active) / CPU RAM (offloaded, ~1s reload) / Disk (cold, ~10s reload)
2. **Startup Preloading** — Default model loaded into VRAM on server start (background thread)
3. **CPU Offloading** — Evicted models move to system RAM instead of being deleted (inspired by ComfyUI)
4. **Reference Counting** — Models in active use are never evicted mid-inference

---

## Problem Statement

**Before:** Models are lazy-loaded on first request (~10s from disk). No eviction logic exists — loading a second large model alongside the first causes CUDA OOM. Each model switch in a workshop triggers a full disk reload.

**After:** Default model is pre-loaded at startup. Model switches offload the old model to CPU RAM (~1s) and load the new one. If the new model was previously offloaded to CPU, it reloads in ~1s instead of ~10s from disk.

---

## Three-Tier Memory Hierarchy

```
┌───────────────────────────────────┐
│         GPU VRAM (~32GB)          │  Active model — inference runs here
│         Speed: instant            │  Only 1 large model fits
└──────────────┬────────────────────┘
               │ pipe.to("cpu")  ~1s    ▲ pipe.to("cuda")  ~1s
               ▼                        │
┌───────────────────────────────────┐
│       CPU System RAM (128GB)      │  Offloaded models — fast reload
│       Speed: ~1s (PCIe 5.0)      │  Multiple models can coexist
└──────────────┬────────────────────┘
               │ del pipe  (last resort) ▲ from_pretrained()  ~10s
               ▼                         │
┌───────────────────────────────────┐
│       NVMe SSD / HF Cache         │  Cold storage — full reload from disk
│       Speed: ~10s                  │  Always available as fallback
└───────────────────────────────────┘
```

**Transfer speeds for a ~28GB model:**

| Transfer Path | Bandwidth | Time |
|---------------|-----------|------|
| NVMe SSD → GPU | ~7 GB/s | ~4-7s |
| CPU RAM → GPU (PCIe 4.0 x16) | ~32 GB/s | ~0.9s |
| CPU RAM → GPU (PCIe 5.0 x16) | ~64 GB/s | ~0.4s |
| GPU → CPU RAM | ~32-64 GB/s | ~0.4-0.9s |

**Design principle (from ComfyUI):** Never delete a model if system RAM can hold it. CPU RAM is 5-15x faster than disk for model reload.

---

## Architecture

### Component Diagram

```
                        Server Startup
                             │
                             ▼
                    ┌─────────────────┐
                    │  create_app()   │
                    │  (__init__.py)  │
                    └────────┬────────┘
                             │ daemon thread
                             ▼
┌────────────────────────────────────────────────────────────┐
│               DiffusersImageGenerator                       │
│                                                             │
│  State:                                                     │
│  ├── _pipelines: Dict[model_id → pipeline]    (GPU or CPU) │
│  ├── _model_device: Dict[model_id → "cuda"|"cpu"]          │
│  ├── _model_last_used: Dict[model_id → timestamp]          │
│  ├── _model_vram_mb: Dict[model_id → measured MB]          │
│  ├── _model_in_use: Dict[model_id → refcount]              │
│  └── _load_lock: threading.Lock                             │
│                                                             │
│  Methods:                                                   │
│  ├── warmup()                ← startup thread               │
│  ├── _load_model_sync()      ← all loading goes through    │
│  ├── _ensure_vram_available() ← offload to CPU, not delete  │
│  ├── _offload_to_cpu()       ← pipe.to("cpu") + cache clear│
│  ├── _move_to_gpu()          ← pipe.to("cuda") from CPU    │
│  ├── load_model()            ← async wrapper (existing API) │
│  ├── unload_model()          ← hard unload (existing API)   │
│  └── generate_image()        ← refcount guarded             │
└────────────────────────────────────────────────────────────┘
```

### Data Flow: Model Loading

```
Request for model_id X
         │
         ▼
    _load_model_sync(X)
         │
    ┌────┴────┐
    │ Acquire │
    │  _load  │
    │  _lock  │
    └────┬────┘
         │
    X in _pipelines? ──yes──▶ On GPU? ──yes──▶ Update last_used, return
         │                        │
         │ no                     │ no (on CPU)
         │                        ▼
         │              _ensure_vram_available()
         │                        │
         │              _move_to_gpu(X)   ◄── pipe.to("cuda") ~1s
         │              Update last_used, return
         │
         ▼ (not in _pipelines at all — cold load from disk)
    _ensure_vram_available()
         │
    Measure VRAM (before)
         │
    PipelineClass.from_pretrained()   ◄── ~10s from disk
    pipe.to("cuda")
    enable_attention_slicing()
         │
    Measure VRAM (after)
    Store delta in _model_vram_mb[X]
         │
    _pipelines[X] = pipe
    _model_device[X] = "cuda"
    _model_last_used[X] = now
         │
    Release _load_lock
```

### Data Flow: VRAM Eviction (Offload to CPU)

```
_ensure_vram_available()
         │
    Free VRAM >= reserve? ──yes──▶ return (nothing to do)
         │ no
         ▼
    Find LRU model on GPU
    where _model_in_use[id] <= 0
         │
    ┌────┴────┐
    │ Found?  │──no──▶ Log warning, return (all in-use)
    └────┬────┘
         │ yes
         ▼
    _offload_to_cpu(model_id)
         │
    pipe.to("cpu")                ◄── weights move to system RAM
    torch.cuda.empty_cache()
    _model_device[id] = "cpu"
         │
    Log: [DIFFUSERS] Offloaded {id} to CPU ({freed}MB freed)
         │
    Repeat check (free VRAM >= reserve?)
```

### Data Flow: Image Generation (Refcount Guard)

```
generate_image(model_id=X)
         │
    Ensure model loaded (load_model)
         │
    _model_in_use[X] += 1   ◄── protects from eviction
         │
    try:
    │   pipe = _pipelines[X]
    │   _model_last_used[X] = now
    │   result = pipe(prompt, ...)
    │   return PNG bytes
    finally:
    │   _model_in_use[X] -= 1   ◄── releases protection
```

---

## Configuration

**File:** `devserver/config.py`

| Setting | Default | Description |
|---------|---------|-------------|
| `DIFFUSERS_PRELOAD_MODELS` | `[("stabilityai/stable-diffusion-3.5-large", "StableDiffusion3Pipeline")]` | Models to preload at startup, in priority order. |
| `DIFFUSERS_VRAM_RESERVE_MB` | `3072` | Minimum free VRAM (MB) to keep for inference overhead (latents, VAE, scheduler). |

**Empty preload list disables warmup:** `DIFFUSERS_PRELOAD_MODELS = []`

---

## Model VRAM Measurements

VRAM usage is measured empirically (delta of `torch.cuda.memory_allocated()` before and after loading), **not** from chunk metadata. Chunk metadata `gpu_vram_mb` values are unreliable (e.g. SD3.5 chunk claims 8GB, actual usage is ~28GB).

| Model | Pipeline Class | Measured VRAM (fp16) | CPU RAM when offloaded |
|-------|---------------|---------------------|----------------------|
| SD3.5 Large | StableDiffusion3Pipeline | ~28 GB | ~28 GB |
| FLUX.2 Dev | Flux2Pipeline | ~24 GB (bfloat16) | ~24 GB |

**RAM requirement:** Both models offloaded simultaneously = ~52GB system RAM. With 128GB, this leaves ample room for OS, Ollama models, and other services.

---

## Startup Preloading

### Sequence

```
Server startup
    │
    ├── create_app()                     ◄── Flask app ready
    │     ├── register blueprints
    │     ├── _run_startup_migration()
    │     └── Start daemon thread ──────────┐
    │                                        │
    ├── serve(app, ...)                      │ (parallel)
    │     Server accepting requests ◄────────┤
    │                                        │
    │                                   ┌────┴────┐
    │                                   │ warmup() │
    │                                   │ Load     │
    │                                   │ SD3.5... │
    │                                   │ (10-15s) │
    │                                   └────┬────┘
    │                                        │
    │                              [DIFFUSERS-WARMUP] SD3.5 ready
    │                              (12.3s, 28652MB VRAM)
    ▼
First image request → model already loaded → instant
```

---

## Workshop Scenario: Model Switching

```
Time  User     Action                     GPU VRAM              CPU RAM
─────────────────────────────────────────────────────────────────────────
0:00  Server   Startup + warmup           SD3.5 (28GB)          -
0:15  Alice    Generate (SD3.5)           SD3.5 (28GB)          -           instant
0:30  Bob      Generate (FLUX.2)          Loading...            SD3.5 (28GB)
                                                                             ▲ offload ~1s
0:31  Bob      ...                        FLUX.2 (24GB)         SD3.5 (28GB) ▼ disk load ~10s
0:45  Alice    Generate (SD3.5) again     Loading...            FLUX.2 (24GB)
                                                                             ▲ offload ~1s
0:46  Alice    ...                        SD3.5 (28GB)          FLUX.2 (24GB) ▼ CPU→GPU ~1s!
1:00  Charlie  Generate (SD3.5)           SD3.5 (28GB)          FLUX.2 (24GB) instant
```

**Key insight:** After the first cold load from disk, subsequent switches are ~1s (CPU↔GPU) instead of ~10s (disk→GPU).

---

## Failsafe Analysis

| Scenario | Risk | Mitigation |
|----------|------|------------|
| **Warmup thread crashes** | Server starts without preloaded model | `try/except` in warmup + daemon thread. Fallback: lazy-load on first request. |
| **Eviction during active generation** | Model offloaded mid-inference → crash | `_model_in_use` refcount. Offloading skips models with refcount > 0. |
| **All models in-use, need VRAM for new model** | Cannot offload, cannot load | Load attempt proceeds (may OOM). Exception caught, returns error. Active generations continue. |
| **Request arrives during warmup** | Thread contention on lock | Blocks on `_load_lock`. When released, model already loaded → instant return. |
| **Concurrent requests for different models** | Race condition | `_load_lock` serializes all load/offload operations. |
| **CUDA OOM during loading** | GPU state corruption | Caught in `_load_model_sync()`. `empty_cache()` in error path. Returns `False`. |
| **System RAM full (too many offloaded models)** | Swap thrashing | Monitor: if offloading to CPU fails or RAM < threshold, hard-unload (del) instead. |
| **Server shutdown during warmup** | Orphaned thread | Daemon thread dies automatically with main process. |
| **Model not downloaded yet (first run)** | Warmup downloads from HuggingFace | `from_pretrained()` handles download. May take minutes but thread is non-blocking. |

### Concurrency Invariants

1. **Loading is serialized**: `_load_lock` ensures exactly one load/offload operation at a time
2. **Offloading is safe**: A model with `_model_in_use[id] > 0` is never offloaded
3. **Refcount is balanced**: `try/finally` ensures decrement even on generation errors
4. **No deadlock**: `_load_lock` is the only lock. `generate_image()` never acquires it.

---

## Files

| File | Change | Purpose |
|------|--------|---------|
| `devserver/config.py` | Add settings | `DIFFUSERS_PRELOAD_MODELS`, `DIFFUSERS_VRAM_RESERVE_MB` |
| `devserver/my_app/services/diffusers_backend.py` | Core changes | Three-tier memory, CPU offloading, refcount, `warmup()` |
| `devserver/my_app/__init__.py` | Launch thread | Start warmup daemon thread after `_run_startup_migration()` |

---

## Relationship to Other Components

- **ComfyUI Model Management**: Inspiration for the CPU-offloading approach. ComfyUI uses the same three-tier pattern (VRAM → CPU RAM → Disk) with `partially_unload()` and `VRAMState` enum. Our implementation is simpler (whole-model offload, not layer-by-layer) since we manage 2-3 large models, not dozens of components.
- **Backend Registry** (Part 8): VRAM management is internal to `DiffusersImageGenerator`. The registry's `min_vram_gb` gate is a coarse check; the VRAM manager provides fine-grained runtime control.
- **SwarmUI Manager** (Part 8): Orthogonal. SwarmUI manages ComfyUI process lifecycle; VRAM manager handles Diffusers pipeline objects.
- **LoRA Training** (Part 23): Training requires ~50GB VRAM. Offloaded CPU-resident models should also be hard-unloaded before training to avoid RAM pressure during weight computation.

---

## Design Rationale

**Why CPU offloading instead of hard unload?**
CPU RAM → GPU transfer is 5-15x faster than NVMe → GPU. In workshops with frequent model switching, this reduces switch time from ~10s to ~1s. The trade-off (system RAM usage) is acceptable with 128GB RAM.

**Why whole-model offload, not layer-by-layer like ComfyUI?**
ComfyUI manages many small components (CLIP, VAE, UNet, LoRAs) and benefits from granular offloading. We manage 2-3 monolithic pipelines where whole-model `.to("cpu")` / `.to("cuda")` is simpler and sufficient.

**Why measure VRAM empirically?**
Chunk metadata `gpu_vram_mb` values are inaccurate (SD3.5: claims 8GB, uses 28GB). Only `torch.cuda.memory_allocated()` deltas are reliable.

**Why `threading.Lock` instead of `asyncio.Lock`?**
`_load_model_sync()` runs via `asyncio.to_thread()` — real OS threads. `asyncio.Lock` doesn't work across threads.

---
