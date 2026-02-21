# DevServer Architecture

**Part 28: Latent Lab — Deconstructive Model Introspection**

---

## Overview

The Latent Lab (`/latent-lab`) consolidates all deconstructive, vector-space-based operations into a single tab-based research mode. Unlike the productive generation modes (Text/Image/Music Transformation), the Latent Lab does not create finished artworks — it exposes the internal mechanics of generative AI models for exploration and education.

**Key Principle:** "What happens inside the model?" — every Latent Lab tool makes invisible model internals visible.

**Safety Level:** Requires `adult` or `research` (see Part 28a: Research-Level Gating below).

---

## Scientific Foundation

The Latent Lab tools are grounded in six lines of research:

### Vector Arithmetic in Embedding Spaces
- **Mikolov, T. et al. (2013).** "Distributed Representations of Words and Phrases and their Compositionality." NeurIPS.
  DOI: [10.48550/arXiv.1310.4546](https://doi.org/10.48550/arXiv.1310.4546)
  — The foundational paper establishing vector arithmetic for word embeddings ("King − Man + Woman = Queen"). Demonstrates that learned embedding spaces encode semantic relationships as linear directions, enabling algebraic concept manipulation. **Basis for: Concept Algebra tab.**

### Representation Engineering
- **Zou, A. et al. (2023).** "Representation Engineering: A Top-Down Approach to AI Transparency." arXiv.
  DOI: [10.48550/arXiv.2310.01405](https://doi.org/10.48550/arXiv.2310.01405)
  — Reading and steering model behavior through manipulation of internal representations. Establishes that neural network activations encode interpretable, manipulable concepts. **Basis for: Feature Probing tab (dimension transfer).**

### Probing / Feature Attribution
- **Belinkov, Y. (2022).** "Probing Classifiers: Promises, Shortcomings, and Advances." Computational Linguistics (MIT Press).
  DOI: [10.1162/coli_a_00422](https://doi.org/10.1162/coli_a_00422)
  — Systematic survey of probing methods for understanding what information neural representations encode. **Basis for: Feature Probing tab (analysis phase).**

- **Bau, D. et al. (2020).** "Rewriting a Deep Generative Model." ECCV 2020 (Springer).
  DOI: [10.1007/978-3-030-58452-8_21](https://doi.org/10.1007/978-3-030-58452-8_21)
  — Targeted rewriting of individual features in generative models. Shows that single directions in representation space control specific visual concepts. **Basis for: Feature Probing tab (targeted dimension transfer).**

### Attention in Diffusion Models
- **Hertz, A. et al. (2022).** "Prompt-to-Prompt Image Editing with Cross Attention Control." ICLR 2023.
  DOI: [10.48550/arXiv.2208.01626](https://doi.org/10.48550/arXiv.2208.01626)
  — The key paper for attention manipulation in diffusion models. Shows that cross-attention layers control the spatial relationship between prompt tokens and image regions. **Basis for: Attention Cartography tab.**

### Latent Space Semantics in Diffusion
- **Kwon, M. et al. (2023).** "Diffusion Models Already Have a Semantic Latent Space." ICLR 2023.
  DOI: [10.48550/arXiv.2210.10960](https://doi.org/10.48550/arXiv.2210.10960)
  — Demonstrates that intermediate activations (h-space) in diffusion models carry semantic meaning. Early steps establish composition, middle steps form semantics, late steps refine detail. **Basis for: Denoising Archaeology tab.**

### Compositional Concept Algebra in Diffusion
- **Liu, N. et al. (2022).** "Compositional Visual Generation with Composable Diffusion Models." ECCV 2022 (Springer).
  DOI: [10.1007/978-3-031-19803-8_12](https://doi.org/10.1007/978-3-031-19803-8_12)
  — Mathematical composition of concepts in diffusion models. Demonstrates that score functions (and by extension, conditioning embeddings) can be algebraically combined. **Basis for: Concept Algebra tab.**

### Mapping: Paper → Latent Lab Tab

| Paper | Tab | Operation |
|-------|-----|-----------|
| Mikolov 2013 | Concept Algebra | A - B + C embedding arithmetic |
| Liu 2022 | Concept Algebra | Composable concept diffusion |
| Zou 2023 | Feature Probing | Representation reading + steering |
| Belinkov 2022 | Feature Probing | Probing what embeddings encode |
| Bau 2020 | Feature Probing | Rewriting specific features |
| Hertz 2022 | Attention Cartography | Cross-attention map analysis |
| Kwon 2023 | Denoising Archaeology | Semantic phases in denoising |

---

## Architecture

### Frontend: Tab Container

**File:** `public/ai4artsed-frontend/src/views/latent_lab.vue`

The Latent Lab is a lightweight shell that renders child components based on the active tab:

| Tab | Component | Status | Purpose |
|-----|-----------|--------|---------|
| Attention Cartography | `latent_lab/attention_cartography.vue` | Implemented | Token→Region attention heatmaps |
| Feature Probing | `latent_lab/feature_probing.vue` | Implemented | Embedding dimension analysis + transfer |
| Concept Algebra | `latent_lab/concept_algebra.vue` | Implemented | Vector arithmetic (A - B + C) |
| Encoder Fusion | — | Planned | Cross-encoder interpolation |
| Denoising Archaeology | — | Planned | Step-by-step denoising visualization |

Active tab persists in `localStorage`.

### Backend: Diffusers-Based Introspection

All Latent Lab operations use the Diffusers backend (`diffusers_backend.py`) for direct tensor access. The pipeline definition (`latent_lab.json`) is type `passthrough` with `skip_stage2: true` — preserving the raw prompt for model analysis.

**Why Diffusers, not ComfyUI:**

| Aspect | ComfyUI | Diffusers |
|--------|---------|-----------|
| Text encoders | Accessed via workflow nodes, outputs opaque | Direct method calls (`_get_clip_prompt_embeds()`) |
| Attention maps | Not exposed between nodes | Custom processors (`AttentionCaptureProcessor`) hot-swappable at runtime |
| Embedding manipulation | Requires custom nodes for each operation | Standard PyTorch tensor ops |
| Denoising introspection | Hidden inside KSampler node | Programmable step-by-step loop |

ComfyUI is ideal for node-graph-based generation workflows. Diffusers provides the programmatic access required for model introspection.

---

## Implemented Tools

### 1. Attention Cartography

**Question:** "Which prompt tokens influence which image regions?"

**Backend:** `DiffusersImageGenerator.generate_image_with_attention()` (diffusers_backend.py:560-752)

**Mechanism:**
1. Custom `AttentionCaptureProcessor` replaces SD3.5's efficient SDPA with manual softmax attention
2. During generation, captures text→image cross-attention submatrix `[image_tokens, text_tokens]` at configurable layers (default: 3, 9, 17) and timesteps
3. Attention maps averaged across heads, truncated to actual word token columns
4. Pre-tokenizes prompt with CLIP-L tokenizer to group sub-tokens into words

**Key Files:**
- `devserver/my_app/services/attention_processors_sd3.py` — `AttentionMapStore`, `AttentionCaptureProcessor`, `install_attention_capture()`, `restore_attention_processors()`
- `devserver/schemas/configs/output/attention_cartography_diffusers.json`

**Frontend:** Interactive canvas overlay with token selection chips, timestep slider, layer toggle, heatmap opacity control.

**Data Volume Optimization:** Token column truncation + head averaging reduces attention data from ~300MB to ~10MB per generation.

### 2. Feature Probing

**Question:** "Which embedding dimensions encode which semantic differences?"

**Backend:** `DiffusersImageGenerator.generate_image_with_probing()` (diffusers_backend.py:753-1048)

**Two-Phase Architecture:**

**Phase 1 — Analysis** (`transfer_dims=None`):
1. Encode prompts A and B with selected text encoder (CLIP-L/CLIP-G/T5-XXL/All)
2. Compute per-dimension absolute difference (averaged across token positions)
3. Sort all dimensions by magnitude (no arbitrary cutoff)
4. Generate reference image with embed_a
5. Return image + probing analysis (diff_per_dim, top_dims, L2 distance)

**Phase 2 — Transfer** (`transfer_dims` provided):
1. Copy selected dimensions from embed_b into embed_a
2. Compose full SD3.5 embedding for modified generation
3. Generate image with same seed for side-by-side comparison

**Key Files:**
- `devserver/my_app/services/embedding_analyzer.py` — `compute_dimension_differences()`, `apply_dimension_transfer()`
- `devserver/schemas/configs/output/feature_probing_diffusers.json`

**Frontend:** Two-prompt input, encoder selector, interactive dimension bar chart with threshold slider, multi-range slider for dimension selection, side-by-side comparison.

---

## Legacy Vector Workflows (ComfyUI, not in Latent Lab UI)

These existed before the Latent Lab and use ComfyUI custom nodes:

- **Split & Combine** (`split_and_combine_legacy.json`) — Semantic vector fusion of two prompts. Produces 4 images: A, B, fused, interpolated. Combination types: linear, spherical.
- **Partial Elimination** (`partial_elimination_legacy.json`) — Dimension elimination. Produces 3 images: reference, inner eliminated, outer eliminated. Modes: average, random, invert, zero_out.

These are candidates for future migration to Diffusers and integration into Latent Lab tabs (Concept Algebra, Encoder Fusion).

---

## Relationship to Hallucinator

The Hallucinator (`/surrealizer`) is architecturally related but remains a **separate feature**:

| Aspect | Hallucinator | Latent Lab |
|--------|-------------|------------|
| Purpose | Creative tool (produce surreal images) | Research tool (understand model internals) |
| User experience | Single slider (alpha), quick iteration | Multi-step analysis, data visualization |
| Output | Finished images for artistic use | Visualizations, charts, heatmaps |
| Route | `/surrealizer` (standalone) | `/latent-lab` (tabbed container) |

Both share the same Diffusers backend and bypass Stage 2. Future consolidation is planned but not prioritized.

See: `ARCHITECTURE PART 25 — Explorative Vector-Based Workflows` for Hallucinator technical details.

---

## Part 28a: Research-Level Gating

Canvas and Latent Lab bypass the standard 4-Stage Safety pipeline (Stage 2 skipped, Stage 1/3 optional). Rather than retrofitting full safety into every experimental endpoint — which would compromise their deconstructive character — access is gated by safety level.

### Safety Level Hierarchy

```
kids  <  youth  <  adult  <  research
```

| Level | Canvas & Latent Lab | Compliance Dialog |
|-------|--------------------|--------------------|
| `kids` | Locked (visible, opacity 0.4, lock icon) | — |
| `youth` | Locked | — |
| `adult` | Accessible (§86a + DSGVO still active) | No |
| `research` | Accessible (no filters) | Yes (per session) |

### Implementation

**Backend:** `GET /api/settings/safety-level` (public, no auth) returns `{"safety_level": "youth"}`.

**Frontend Store:** `stores/safetyLevel.ts` — Pinia store fetched at app startup:
- `isAdvancedMode` — `true` for `adult` or `research`
- `isResearchMode` — `true` for `research` only
- `researchConfirmed` — `ref` (resets on page reload, not persisted)

**Landing Page:** Feature cards with `requiresAdvanced: true` flag. Three states:
1. **Locked** (`!isAdvancedMode`): `.locked` class, pointer-events disabled, lock overlay with hint
2. **Normal** (`isAdvancedMode && !isResearchMode`): standard click → navigate
3. **Compliance** (`isResearchMode && !researchConfirmed`): click → `ResearchComplianceDialog` → on confirm → navigate

**Router Guard:** `meta: { requiresAdvanced: true }` on `/canvas` and `/latent-lab` routes. Prevents direct URL access at `kids`/`youth` by redirecting to landing page.

---

## File Reference

### Frontend
| File | Purpose |
|------|---------|
| `views/latent_lab.vue` | Tab container |
| `views/latent_lab/attention_cartography.vue` | Attention heatmaps |
| `views/latent_lab/feature_probing.vue` | Dimension analysis + transfer |
| `views/latent_lab/concept_algebra.vue` | Vector arithmetic (A - B + C) |
| `stores/safetyLevel.ts` | Safety level store (feature gating) |
| `components/ResearchComplianceDialog.vue` | Research compliance modal |
| `views/LandingView.vue` | Feature card gating |
| `router/index.ts` | Advanced-mode navigation guard |

### Backend
| File | Purpose |
|------|---------|
| `services/diffusers_backend.py` | `generate_image_with_attention()`, `generate_image_with_probing()`, `generate_image_with_algebra()` |
| `services/attention_processors_sd3.py` | Custom attention capture |
| `services/embedding_analyzer.py` | Dimension difference + transfer + concept algebra |
| `routes/settings_routes.py` | `/api/settings/safety-level` endpoint |
| `config.py` | `DEFAULT_SAFETY_LEVEL`, `SAFETY_FILTERS` |

### Configs
| File | Purpose |
|------|---------|
| `schemas/pipelines/latent_lab.json` | Passthrough pipeline (skip Stage 2) |
| `schemas/configs/interception/latent_lab.json` | UI metadata (icon, category) |
| `schemas/configs/output/attention_cartography_diffusers.json` | Attention Cartography output config |
| `schemas/configs/output/feature_probing_diffusers.json` | Feature Probing output config |
| `schemas/configs/output/concept_algebra_diffusers.json` | Concept Algebra output config |
| `schemas/configs/output/denoising_archaeology_diffusers.json` | Denoising Archaeology output config |
| `schemas/chunks/output_image_concept_algebra_diffusers.py` | Concept Algebra Python chunk |

---

## 3. Denoising Archaeology

### 3. Denoising Archaeology

**Question:** "How does noise become an image? What emerges at which step?"

**Scientific Foundation:** Kwon, M. et al. (2023). "Diffusion Models Already Have a Semantic
Latent Space." ICLR 2023. DOI: 10.48550/arXiv.2210.10960
— Shows that intermediate activations (h-space) in diffusion models carry semantic meaning.
Early steps establish composition, middle steps form semantics, late steps refine detail.

**Backend:** Python chunk `output_image_denoising_archaeology_diffusers.py` →
`DiffusersImageGenerator.generate_image_with_archaeology()` (diffusers_backend.py)

**Mechanism:**
1. Standard SD3.5 generation with `callback_on_step_end` at every step
2. At each callback: VAE-decode current latents to 512×512 JPEG (quality 70) thumbnail
3. After generation: collect all step thumbnails + full-resolution final PNG
4. Return as structured dict via Python chunk's `execute()` → dict return path

**Three Educational Phases:**
| Phase | Steps (of 25) | Description | Color |
|-------|---------------|-------------|-------|
| Composition | 1–8 | Global structure, color distribution, layout | #FF9800 (orange) |
| Semantics | 9–17 | Objects become recognizable, shapes crystallize | #00BCD4 (cyan) |
| Detail | 18–25 | Textures, edges, fine patterns | #4CAF50 (green) |

**Key Files:**
- `devserver/schemas/chunks/output_image_denoising_archaeology_diffusers.py` — Python chunk
- `devserver/schemas/configs/output/denoising_archaeology_diffusers.json` — Output config
- `devserver/my_app/services/diffusers_backend.py` — `generate_image_with_archaeology()`
- `public/ai4artsed-frontend/src/views/latent_lab/denoising_archaeology.vue` — Frontend

**Frontend:** Prompt input → Generate → Filmstrip of 25 step thumbnails + timeline slider +
full-size viewer with phase indicator badge. Phase markers (Composition/Semantics/Detail)
along the slider.

**Performance:** 25 VAE decodes × ~50ms = +1.25s overhead. 25 thumbnails × ~80KB +
final PNG ~1.5MB = ~3.5MB total response.

## 4. Concept Algebra

**Question:** "What happens when you apply word2vec-style vector arithmetic to image generation embeddings?"

**Scientific Foundation:** Mikolov, T. et al. (2013). "Distributed Representations of Words and Phrases and their Compositionality." NeurIPS. DOI: 10.48550/arXiv.1310.4546
— Demonstrated that embedding spaces encode semantic relationships as linear directions: vec("King") − vec("Man") + vec("Woman") ≈ vec("Queen").

Liu, N. et al. (2022). "Compositional Visual Generation with Composable Diffusion Models." ECCV. DOI: 10.1007/978-3-031-19803-8_12
— Extended algebraic composition to diffusion model conditioning.

**Backend:** `DiffusersImageGenerator.generate_image_with_algebra()` (diffusers_backend.py)

**Mechanism:**
1. Encode three prompts (A, B, C) with selected text encoder(s)
2. Compute: embed_result = embed_A − scale_sub × embed_B + scale_add × embed_C
3. Same arithmetic on pooled embeddings
4. Generate reference image with embed_A (same seed)
5. Generate result image with embed_result

**Key Files:**
- `devserver/schemas/chunks/output_image_concept_algebra_diffusers.py` — Python chunk
- `devserver/schemas/configs/output/concept_algebra_diffusers.json` — Output config
- `devserver/my_app/services/diffusers_backend.py` — `generate_image_with_algebra()`
- `devserver/my_app/services/embedding_analyzer.py` — `apply_concept_algebra()`
- `public/ai4artsed-frontend/src/views/latent_lab/concept_algebra.vue` — Frontend

**Frontend:** Three-prompt input (A = base, B = subtract, C = add), encoder selector (All/CLIP-L/CLIP-G/T5), formula visualization (A − B + C = ?), side-by-side comparison (reference vs. result), L2 distance display, scale controls for subtraction/addition intensity.

---

## Python Chunk Dict-Return Extension (Generic)

**Motivation:** `_execute_python_chunk()` (backend_router.py) originally only supported
`bytes` returns from `execute()`. The router guessed the media type from the chunk's
filename prefix (`output_music_*` → audio, else → raw bytes). This doesn't scale for
chunks that return structured data (multiple images, analysis results, metadata).

**Extension:** If `execute()` returns a `dict`, the router uses it directly:
- `dict['content_marker']` → `BackendResponse.content` (route dispatch key)
- Remaining dict entries → spread into `BackendResponse.metadata`
- `chunk_type: "python"` added automatically

**Backwards compatible:** Chunks returning `bytes` work unchanged.

**Location:** `devserver/schemas/engine/backend_router.py`, method `_execute_python_chunk()`,
after `result = await module.execute(**parameters)`.

**Example (Denoising Archaeology):**
```python
# In chunk execute():
return {
    'content_marker': 'diffusers_archaeology_generated',
    'image_data': base64_png,
    'archaeology_data': {'step_images': [...], 'total_steps': 25, 'seed': 42}
}
# Router creates: BackendResponse(content='diffusers_archaeology_generated', metadata={...})
```

**Future benefit:** Any Python chunk can return structured output. HeartMuLa could
eventually migrate from name-based detection to dict returns.

---

## Latent Text Lab — Dekonstruktive LLM-Introspektion

### Overview

The Latent Text Lab (`textlab` tab inside `/latent-lab`) extends the deconstructive paradigm from image models to large language models. Where the image-side tools (Attention Cartography, Feature Probing, etc.) expose the internals of Stable Diffusion 3.5, the Text Lab exposes the internals of decoder-only LLMs (LLaMA, GPT-2, Falcon, etc.).

**Key Question:** "What biases, directions, and structures are encoded in a language model's weights?"

The Text Lab does not produce finished text outputs — it runs controlled experiments that make invisible model behavior visible.

### Scientific Foundation (Text-Side)

Three additional research lines complement the image-side foundation:

#### Representation Engineering (Text Domain)
- **Zou, A. et al. (2023).** "Representation Engineering: A Top-Down Approach to AI Transparency." arXiv.
  DOI: [10.48550/arXiv.2310.01405](https://doi.org/10.48550/arXiv.2310.01405)
  — Concept directions in activation space via contrast pairs + PCA. Forward-hook manipulation steers generation without retraining. **Basis for: Tab 1 (Representation Engineering).**

- **Li, K. et al. (2024).** "Inference-Time Intervention: Eliciting Truthful Answers from a Language Model." NeurIPS 2023.
  DOI: [10.48550/arXiv.2306.03341](https://doi.org/10.48550/arXiv.2306.03341)
  — Runtime injection of concept directions into decoder layers via forward hooks. **Basis for: Tab 1 (manipulation phase).**

#### Probing & Comparative Archaeology
- **Belinkov, Y. (2022).** "Probing Classifiers: Promises, Shortcomings, and Advances." Computational Linguistics (MIT Press).
  DOI: [10.1162/coli_a_00422](https://doi.org/10.1162/coli_a_00422)
  — Layer-wise probing of what information neural representations encode. **Basis for: Tab 2 (Comparative Model Archaeology).**

- **Olsson, C. et al. (2022).** "In-Context Learning and Induction Heads." Anthropic Research.
  DOI: [10.48550/arXiv.2209.11895](https://doi.org/10.48550/arXiv.2209.11895)
  — Induction heads and mechanistic interpretability across model scales. **Basis for: Tab 2 (CKA comparison, attention analysis).**

#### Bias and Monosemanticity
- **Bricken, T. et al. (2023).** "Towards Monosemanticity: Decomposing Language Models With Dictionary Learning." Anthropic Research.
  — Individual neurons can encode interpretable features; systematic probing reveals latent biases. **Basis for: Tab 3 (Bias Archaeology).**

#### Mapping: Paper → Text Lab Tab

| Paper | Tab | Operation |
|-------|-----|-----------|
| Zou 2023 | Representation Engineering | Concept direction extraction via contrast pairs |
| Li 2024 | Representation Engineering | Forward-hook manipulation of generation |
| Belinkov 2022 | Comparative Model Archaeology | Layer-wise representation probing |
| Olsson 2022 | Comparative Model Archaeology | CKA similarity, attention pattern analysis |
| Bricken 2023 | Bias Archaeology | Systematic bias detection via token manipulation |

### Architecture

#### Data Flow

```
Frontend (latent_text_lab.vue)
    │
    │ POST /api/text/*
    ▼
DevServer text_routes.py (stateless proxy)
    │
    │ HTTP POST via TextClient
    ▼
GPU Service text_routes.py (port 17803)
    │
    ▼
TextBackend (text_backend.py)
    ├── Model management (load/unload/quantize)
    ├── VRAM coordination (VRAMCoordinator protocol)
    └── Dekonstruktive operations (PyTorch hooks, logit surgery)
```

**Key Design Principle:** DevServer is a stateless proxy. All model state (loaded models, VRAM tracking, LRU caches) lives exclusively in the GPU Service. This mirrors the architecture of the image-side Latent Lab tools, where Diffusers runs in the GPU Service.

**Why not the 4-Stage Pipeline?** The Text Lab bypasses the standard orchestration pipeline (Stages 1–4) entirely. Like all Latent Lab tools, it requires unmanipulated access to model internals. Safety interception (Stage 2) or prompt translation (Stage 1) would destroy the experimental controls.

#### Model Management

Auto-quantization based on available VRAM:

| Priority | Quantization | VRAM Multiplier | Quality |
|----------|-------------|-----------------|---------|
| 1 | bf16 | 1.0× | Best |
| 2 | int8 | 0.5× | Good |
| 3 | int4 | 0.3× | Acceptable |

VRAM coordination via `VRAMBackend` protocol: before loading a model, the TextBackend requests VRAM from the shared `VRAMCoordinator`, which may trigger cross-backend eviction (e.g., evict a Diffusers model to make space for an LLM).

### Endpoints

All endpoints are defined twice — once in DevServer (`devserver/my_app/routes/text_routes.py`) as proxy, once in GPU Service (`gpu_service/routes/text_routes.py`) as implementation.

| Endpoint | Method | Purpose | Backend Method |
|----------|--------|---------|----------------|
| `/api/text/models` | GET | List loaded models | `get_loaded_models()` |
| `/api/text/presets` | GET | Available model presets | `get_presets()` |
| `/api/text/load` | POST | Load model (auto-quant) | `load_model()` |
| `/api/text/unload` | POST | Unload model | `unload_model()` |
| `/api/text/embedding` | POST | Hidden state statistics | `get_prompt_embedding()` |
| `/api/text/interpolate` | POST | Embedding interpolation | `interpolate_prompts()` |
| `/api/text/attention` | POST | Attention map extraction | `get_attention_map()` |
| `/api/text/rep-engineering` | POST | Representation Engineering | `rep_engineering()` |
| `/api/text/compare` | POST | CKA model comparison | `compare_models()` |
| `/api/text/bias-probe` | POST | Bias Archaeology | `bias_probe()` |
| `/api/text/generate` | POST | Token-level logit surgery | `generate_with_token_surgery()` |
| `/api/text/generate/stream` | POST/SSE | Streaming generation | `generate_streaming()` |
| `/api/text/variations` | POST | Deterministic seed variations | `generate_variations()` |
| `/api/text/layers` | POST | Layer-by-layer stats | `compare_layer_outputs()` |
| `/api/text/interpret` | POST | LLM result interpretation | `call_chat_helper()` (DevServer only) |

**Note:** `/api/text/interpret` is the only endpoint that does NOT proxy to the GPU Service. It calls the DevServer's `call_chat_helper()` (multi-provider LLM dispatch) to generate pedagogical interpretations of experiment results.

### Tab 1: Representation Engineering (Zou 2023 + Li 2024)

**Question:** "Can we find interpretable concept directions in activation space and use them to steer generation?"

**Mechanism:**

1. **Direction Finding** — User defines contrast pairs (e.g., "Paris is the capital of France" vs. "Paris is the capital of Germany"). For each pair:
   - Extract hidden states at target layer (default: last)
   - Compute difference vector: `pos_hidden - neg_hidden`
   - PCA on all difference vectors → first principal component = concept direction
   - Return: explained variance, per-pair projections, embedding dimensionality

2. **Manipulation** — User enters a test prompt and alpha (manipulation strength):
   - Register forward hook on target decoder layer
   - Hook adds `alpha * direction` to the residual stream
   - Generate baseline (no hook) + manipulated (with hook) using same seed
   - Return both texts for comparison

**Architecture-Aware Layer Access:**
`_get_decoder_layers(model)` handles different LLM architectures:
- LLaMA/Mistral: `model.model.layers`
- GPT-2: `model.transformer.h`
- Falcon: `model.transformer.h`

**Bug Fix (Session 177):** Hidden states have N+1 entries (including input embedding) but decoder layers have N entries. Hook index must use `layer_idx - 1`.

### Tab 2: Comparative Model Archaeology (Belinkov 2022 + Olsson 2022)

**Question:** "How do two different models represent the same information internally?"

**Mechanism:**

1. Load two models simultaneously (Model A = primary, Model B = loaded separately)
2. Feed same prompt through both
3. Compute **Linear CKA** (Centered Kernel Alignment) similarity matrix between all layer pairs:
   - Subsample to max 32 layers per model for tractability
   - CKA measures representational similarity independent of dimensionality
4. Extract attention patterns and layer-wise statistics (L2 norm, mean, std) from both
5. Generate text from both with shared seed for behavioral comparison

**Frontend:** CKA heatmap rendered on `<canvas>` with interactive tooltip (hover shows exact CKA value per layer pair). Side-by-side generation comparison.

### Tab 3: Bias Archaeology (Zou 2023 + Bricken 2023)

**Question:** "What happens when we systematically suppress or boost specific token categories?"

**Preset Experiments:**

| Type | Manipulation | What It Reveals |
|------|-------------|-----------------|
| Gender | Suppress all gendered pronouns (he/she/his/her/him/herself/himself) | Model's default gender assumptions |
| Sentiment | Boost positive OR negative words separately | Strength of sentiment encoding |
| Domain | Boost scientific OR poetic vocabulary | Register shift patterns |
| Custom | User-defined boost/suppress token lists | Open-ended bias probing |

**Mechanism:**

1. Generate baseline samples (no manipulation, multiple seeds)
2. For each group: resolve token IDs (bare + space-prefixed + capitalized variants via `_resolve_token_ids()`)
3. Apply additive logit manipulation during generation:
   - Boost: `logits[:, token_id] += factor`
   - Suppress: `logits[:, token_id] = -inf`
4. Generate manipulated samples with same seeds as baseline
5. Return structured result: `{baseline: [...], groups: [{group_name, mode, tokens, samples}]}`

**Bug Fix (Session 177):** Multiplicative boost (`logits *= factor`) caused softmax collapse → switched to additive (`logits += factor`).

**Token Resolution:** BPE tokenizers encode `" he"` and `"he"` as different token IDs. `_resolve_token_ids()` resolves bare, space-prefixed (`" he"`), and capitalized (`"He"`, `" He"`) variants to ensure complete coverage.

### LLM Interpretation (Session 178)

**Question:** "The raw results show identical text for baseline and masculine-suppression — but why?"

**Problem:** Bias Archaeology produces structured experiment results, but users (especially the 13–17 target audience) often cannot interpret why certain manipulations had no effect, or what patterns emerge across groups.

**Solution:** After displaying bias results, the frontend automatically calls `POST /api/text/interpret` with the full result data. The DevServer formats the results into a structured prompt and calls `call_chat_helper()` (the multi-provider LLM dispatch used by the chat system) with a pedagogical system prompt:

```
System: "Du analysierst Ergebnisse eines KI-Bias-Experiments für Jugendliche (13-17 Jahre).
Erkläre die beobachteten Muster sachlich und verständlich. 3-5 Sätze.
Keine Wertungen, keine Vereinfachungen — nur präzise Beobachtungen.
Antworte in der Sprache der Eingabe."
```

The `_build_interpretation_prompt()` function formats the experiment data (baseline samples, manipulation groups with tokens and modes, generated texts) into a structured text that the LLM can analyze. Supports `bias`, `repeng`, and `compare` experiment types.

**Fail-Open:** If the interpretation call fails (LLM unavailable, timeout, error), the experiment results remain fully visible — only the interpretation box shows an error message. The experiment itself is never blocked.

**Architecture Decision:** Interpretation runs on the DevServer, NOT the GPU Service. The chat helper model (e.g., Mistral Large via Ollama) is a DevServer concern (pedagogical layer), not a GPU inference concern. This keeps the GPU Service focused on tensor operations.

### Frontend: `latent_text_lab.vue`

**Location:** `public/ai4artsed-frontend/src/views/latent_lab/latent_text_lab.vue`

**Tab Container Integration:**
`latent_lab.vue` renders `LatentTextLab` when `activeTab === 'textlab'`. Active tab persists in `localStorage('latent_lab_tab')`.

**Shared Model Panel:**
All three tabs share a single model management panel (top of page). Loading a model makes it available across tabs. Model B (for comparison) is loaded separately within Tab 2.

**Tab Structure:**

| Tab | Component Section | Key Refs |
|-----|------------------|----------|
| Representation Engineering | `activeTab === 'repeng'` | `contrastPairs`, `repResult`, `repGenResult` |
| Model Comparison | `activeTab === 'compare'` | `cmpResult`, `loadedModelB`, `ckaCanvas` |
| Bias Archaeology | `activeTab === 'bias'` | `biasResult`, `biasInterpretation`, `biasInterpreting` |

**CKA Heatmap:** Rendered directly on `<canvas>` via `drawCkaHeatmap()`. Cell color intensity = CKA value^0.7. Interactive tooltip on mousemove shows exact layer pair + CKA value.

**Interpretation Box:** Automatically triggered after bias results arrive (`interpretBiasResults()` called in `runBiasProbe()`). Shows loading spinner → interpretation text → or error. Styled with subtle blue border to distinguish from raw results.

---

## Updated File Reference

### Frontend — Image-Side Latent Lab
| File | Purpose |
|------|---------|
| `views/latent_lab.vue` | Tab container (7 tabs) |
| `views/latent_lab/attention_cartography.vue` | Attention heatmaps |
| `views/latent_lab/feature_probing.vue` | Dimension analysis + transfer |
| `views/latent_lab/concept_algebra.vue` | Vector arithmetic (A - B + C) |
| `views/latent_lab/denoising_archaeology.vue` | Step-by-step denoising |
| `stores/safetyLevel.ts` | Safety level store (feature gating) |
| `components/ResearchComplianceDialog.vue` | Research compliance modal |
| `views/LandingView.vue` | Feature card gating |
| `router/index.ts` | Advanced-mode navigation guard |

### Frontend — Latent Text Lab
| File | Purpose |
|------|---------|
| `views/latent_lab/latent_text_lab.vue` | All 3 tabs + model management + CKA heatmap |

### Backend — Image-Side Latent Lab
| File | Purpose |
|------|---------|
| `devserver/my_app/services/diffusers_backend.py` | `generate_image_with_attention()`, `generate_image_with_probing()`, `generate_image_with_algebra()`, `generate_image_with_archaeology()` |
| `devserver/my_app/services/attention_processors_sd3.py` | Custom attention capture |
| `devserver/my_app/services/embedding_analyzer.py` | Dimension difference + transfer + concept algebra |

### Backend — Latent Text Lab (DevServer proxy layer)
| File | Purpose |
|------|---------|
| `devserver/my_app/routes/text_routes.py` | REST proxy + `/interpret` endpoint |
| `devserver/my_app/services/text_client.py` | HTTP client to GPU Service |

### Backend — Latent Text Lab (GPU Service execution)
| File | Purpose |
|------|---------|
| `gpu_service/services/text_backend.py` | Core: model management, RepEng, CKA, bias probing, token surgery, VRAM coordination |
| `gpu_service/routes/text_routes.py` | REST + SSE endpoints wrapping TextBackend |

### Configs
| File | Purpose |
|------|---------|
| `schemas/pipelines/latent_lab.json` | Passthrough pipeline (skip Stage 2) |
| `schemas/configs/interception/latent_lab.json` | UI metadata (icon, category) |
| `schemas/configs/output/attention_cartography_diffusers.json` | Attention Cartography output config |
| `schemas/configs/output/feature_probing_diffusers.json` | Feature Probing output config |
| `schemas/configs/output/concept_algebra_diffusers.json` | Concept Algebra output config |
| `schemas/configs/output/denoising_archaeology_diffusers.json` | Denoising Archaeology output config |
| `schemas/chunks/output_image_concept_algebra_diffusers.py` | Concept Algebra Python chunk |

---

## Research Data Export (LatentLabRecorder)

### Problem

Canvas records research data via `CanvasRecorder` / `LivePipelineRecorder` because it runs through the 4-Stage Orchestrator — natural recording chokepoints exist. The Latent Lab bypasses this flow entirely: 11 tool types across 3 backend services with direct API calls. There is no backend chokepoint for a recorder.

### Solution: Frontend-Primary Hybrid

The frontend knows the full context (parameters, tab, tool type). After each generation, it POSTs to a lightweight backend endpoint which writes to disk.

**Phase 1** (current): Write to `exports/json/` — same folder structure as Canvas, always active.
**Phase 2** (future): QDA-compatible research format in `exports/research/` for analysis software.

### Architecture

```
┌─────────────────────────────────────┐
│  Vue Component (e.g. denoising)     │
│  useLatentLabRecorder('tool_name')  │
│                                     │
│  onMounted → isRecording = true     │
│  generate() → record({params, ...}) │  ←── Lazy start: backend run
│  onUnmounted → endRun()            │      created on first record()
└─────────────┬───────────────────────┘
              │ POST /api/latent-lab/record/{start,save,end}
              ▼
┌─────────────────────────────────────┐
│  LatentLabRecorder (Python)         │
│  - Creates run folder on start      │
│  - Writes params → prompting_process│
│  - Writes outputs → final/          │
│  - Writes steps → prompting_process │
│  - metadata.json compatible with    │
│    LivePipelineRecorder/Canvas      │
└─────────────────────────────────────┘
              │
              ▼
exports/json/YYYY-MM-DD/device_id/
  run_<timestamp>_<hash>/
    metadata.json
    final/
      01_output_image.png
    prompting_process/
      001_parameters.json
      002_step_01.jpg  (denoising steps)
      002_step_02.jpg
```

### Lazy Start

Run folders are only created when the first `record()` call happens. Navigating between Latent Lab tabs without generating creates no empty folders.

### metadata.json

```json
{
  "run_id": "run_1771664748800_abc123",
  "timestamp": "2026-02-21T10:05:48",
  "type": "latent_lab",
  "latent_lab_tool": "denoising_archaeology",
  "device_id": "38db259e-...",
  "user_id": "anonymous",
  "entities": [
    { "sequence": 1, "type": "latent_lab_params", "filename": "prompting_process/001_parameters.json" },
    { "sequence": 2, "type": "output_image", "filename": "01_output_image.png" }
  ]
}
```

Compatible with `SessionExportView.vue` — Latent Lab runs appear alongside Canvas runs.

### Integration per Tool

| Tool | Generation Functions | Recorded Data |
|------|---------------------|---------------|
| Denoising Archaeology | `generate()` | params + final PNG + all step JPGs |
| Concept Algebra | `compute()` | params + reference + result images |
| Feature Probing | `analyze()`, `transfer()` | params + original/modified images |
| Attention Cartography | `generate()` | params + output image |
| Crossmodal Lab | `runSynth()`, `runMMAudio()`, `runGuidance()` | params + audio WAV |
| Latent Text Lab | `findDirection()`, `runRepGeneration()`, `runComparison()`, `runBiasProbe()` | params + result metadata |
| Surrealizer | `executeWorkflow()` | params only (image in pipeline recorder) |

### Files

| File | Purpose |
|------|---------|
| `devserver/my_app/services/latent_lab_recorder.py` | LatentLabRecorder class + registry |
| `devserver/my_app/routes/latent_lab_recorder_routes.py` | 3 Flask endpoints (start/save/end) |
| `public/.../composables/useLatentLabRecorder.ts` | Vue composable with lazy lifecycle |

---

**Document Status:** Active (2026-02-22)
**Maintainer:** AI4ArtsEd Development Team
**Last Updated:** Session 192 (LatentLabRecorder research data export)
