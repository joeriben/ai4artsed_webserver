# Session 176: Latent Text Lab Vue Frontend

## Context

Session 175 implemented the backend for Latent Text Lab - dekonstruktive LLM operations in the GPU Service. The backend is complete and tested:

- `gpu_service/services/text_backend.py` - LLM operations with VRAM coordination
- `gpu_service/routes/text_routes.py` - REST + SSE endpoints
- `devserver/my_app/services/text_client.py` - HTTP client for DevServer

## Task

Build the Vue frontend for Latent Text Lab as a Stage 4 dekonstruktive tool (like Attention Cartography, Feature Probing, Denoising Archaeology).

## API Endpoints (Port 17803)

```
POST /api/text/load          - Load model (auto-quantization)
POST /api/text/unload        - Unload model
GET  /api/text/models        - List loaded models
GET  /api/text/presets       - Available model presets

POST /api/text/embedding     - Get prompt embedding stats
POST /api/text/interpolate   - Interpolate between two prompts
POST /api/text/attention     - Get attention maps (tokens × tokens matrix)
POST /api/text/generate      - Generate with token surgery (boost/suppress)
POST /api/text/generate/stream - SSE streaming generation
POST /api/text/variations    - Generate seed variations
POST /api/text/layers        - Layer-by-layer activation analysis
```

## Requirements

1. **Stage 4 Chunk**: Create `output_text_latent_lab.py` (py before json rule)
2. **Vue Component**: `latent_text_lab.vue` following naming convention
3. **Visualizations**:
   - Attention heatmap (tokens × tokens)
   - Layer activation chart (mean/std/sparsity per layer)
   - Embedding interpolation visualization
   - Token surgery controls (boost/suppress lists)
4. **Model Management**: Load/unload, show VRAM usage, quantization level
5. **SSE Streaming**: Real-time token output for generation

## Design Notes

- Black background (`#0a0a0a`) - no colored gradients
- Consistent with other Latent Lab tools
- No Stage 1-3 processing - direct LLM access

## Files to Create

- `devserver/my_app/config/output_configs/text_latent_lab.json` (if needed)
- `devserver/schemas/chunks/output_text_latent_lab.py`
- `public/ai4artsed-frontend/src/components/latent_text_lab.vue`
- Router integration in `router/index.ts`
