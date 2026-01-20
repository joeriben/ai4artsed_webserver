# What's New - January 2026

**AI4ArtsEd DevServer Changelog**
**Version:** January 2026 Release
**Sessions:** 111-124

---

## Highlights

### LoRA Training Studio
**Train your own artistic styles directly in the app!**

Upload 5-20 example images, set a trigger word, and train a custom LoRA model that captures your unique style. The trained model is automatically available for image generation.

- Drag & drop image upload
- Configurable training parameters
- Real-time progress feedback
- Automatic VRAM management

### Multi-Image Transformation
**Combine up to 3 images with QWEN-2511!**

The new multi-image workflow lets you upload multiple images and describe how they should be combined or transformed.

### SSE Text Streaming
**See AI responses appear character by character!**

Real-time streaming brings the AI's thought process to life with a typewriter effect, making the transformation visible and engaging.

### SwarmUI Auto-Recovery
**Rock-solid stability!**

The system now automatically detects when SwarmUI needs to start and manages its lifecycle. No more manual restarts or connection errors.

---

## New Features

### LoRA Training Studio (Session 119)
- **Full training pipeline** from browser to model file
- **Kohya-ss based** training for SD3.5 Large
- **Smart VRAM management** - automatically unloads SD3.5 before training
- **Multiple trigger words** - support comma-separated triggers
- **Progress streaming** - real-time training status via SSE

### LoRA Injection System (Sessions 114-124)
- **Config-based LoRAs** - each interception style can have associated LoRAs
- **Automatic injection** - LoRAs added to workflow at runtime
- **Strength tuning** - per-config strength optimization
- **LoRA badges** - visual indicators on config tiles

### SwarmUI Auto-Recovery (Session 113)
- **Lazy startup** - SwarmUI starts only when needed
- **Crash recovery** - automatic restart on failures
- **Health monitoring** - checks both REST and ComfyUI endpoints
- **No browser popups** - frontend stays in focus

### SSE Queue Feedback (Session 118)
- **Visual queue status** - spinner turns red when waiting
- **Wait time display** - shows seconds in queue
- **Automatic reset** - returns to normal when slot acquired

---

## UI Improvements

### Material Design Icons (Session 115)
Complete icon system overhaul:
- All emoji icons replaced with Material Design SVGs
- Consistent sizing and colors across components
- Better accessibility and cross-browser rendering

Affected areas:
- Property quadrant icons
- MediaInputBox header icons
- Category bubbles (image/video/sound)
- Action buttons

### Partial Elimination Enhancements (Session 122)
- **Dual-handle slider** - intuitive range selection
- **Encoder selector** - choose between CLIP, T5, or Combined

### Legacy View Migration (Session 123)
- Clean `/legacy/` endpoint grouping
- Surrealizer, Split&Combine, Partial Elimination now under `/legacy/`

---

## Backend Improvements

### Unified Export System (Session 122)
- **Single run folder** - all entities in one place
- **Multi-backend support** - SD3.5, QWEN, FLUX2, Gemini, GPT all save correctly
- **Complete research units** - input, transformation, and output together

### Connection Stability (Session 112)
- **Fixed CLOSE_WAIT leak** - proper connection cleanup
- **Request queueing** - prevents Ollama overload
- **Extended timeouts** - 300s for large model requests

### Centralized Configuration (Session 121)
- All paths now in `config.py`
- VRAM management for training
- Environment variable overrides

---

## Technical Details

### Sessions Overview

| Session | Date | Focus |
|---------|------|-------|
| 124 | 2026-01-18 | LoRA Epoch/Strength Fine-Tuning |
| 123 | 2026-01-17 | Legacy Migration + LoRA Badges |
| 122 | 2026-01-17 | Unified Export + Partial Elimination |
| 121 | 2026-01-13 | VRAM Management + Config Paths |
| 120 | 2026-01-11 | Config-Based LoRA + Auto-Recovery |
| 119 | 2026-01-09 | LoRA Training Studio |
| 118 | 2026-01-08 | SSE Queue Feedback |
| 117 | 2026-01-17 | LoRA Strength Tuning |
| 116 | 2026-01-10 | LoRA Schema Design |
| 115 | 2026-01-08 | Material Design Icons |
| 114 | 2026-01-11 | LoRA Injection Mechanism |
| 113 | 2026-01-11 | SwarmUI Auto-Recovery |
| 112 | 2026-01-08 | Connection Leak Fix + Queue |
| 111 | 2025-12-28 | Unified Streaming Architecture |

### Key Commits

```
c015937 fix(lora): Use earlier epoch (4) to reduce overfitting
f1d0f55 feat(lora): Tune strength to 0.6 and document findings
d0e85f6 refactor: migrate legacy views to /legacy endpoint
7f07197 fix(export): Unified run_id and fix image saving
f21a56b Feat: Add LoRA Training Studio
bbe04d8 feat(swarmui): Add auto-recovery with SwarmUI Manager
fdc231d feat(icons): Replace emoji icons with Material Design SVGs
```

---

## Known Issues

### Open Bugs
- Stage 3 negative prompts not passed to Stage 4
- Prompt optimization may use wrong input

### Incomplete Features
- Partial Elimination composite image creation
- Vector Fusion (deactivated)

---

## Coming Soon

- Complete user documentation in DokumentationModal
- Dynamic config loading for model selection
- Video tutorial integration

---

*For detailed session information, see DEVELOPMENT_LOG.md*

---

<sub>📝 *This documentation was automatically generated by Claude Code during the Documentation Marathon (Session 126, January 2026).*</sub>
