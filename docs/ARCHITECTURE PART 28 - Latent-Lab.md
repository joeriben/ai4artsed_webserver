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

**Document Status:** Active (2026-02-12)
**Maintainer:** AI4ArtsEd Development Team
**Last Updated:** Session 168 (Concept Algebra, Scientific Foundation)
