# DevServer Architecture

**Part 28: Latent Lab — Deconstructive Model Introspection**

---

## Overview

The Latent Lab (`/latent-lab`) consolidates all deconstructive, vector-space-based operations into a single tab-based research mode. Unlike the productive generation modes (Text/Image/Music Transformation), the Latent Lab does not create finished artworks — it exposes the internal mechanics of generative AI models for exploration and education.

**Key Principle:** "What happens inside the model?" — every Latent Lab tool makes invisible model internals visible.

**Safety Level:** Requires `adult` or `research` (see Part 28a: Research-Level Gating below).

---

## Architecture

### Frontend: Tab Container

**File:** `public/ai4artsed-frontend/src/views/latent_lab.vue`

The Latent Lab is a lightweight shell that renders child components based on the active tab:

| Tab | Component | Status | Purpose |
|-----|-----------|--------|---------|
| Attention Cartography | `latent_lab/attention_cartography.vue` | Implemented | Token→Region attention heatmaps |
| Feature Probing | `latent_lab/feature_probing.vue` | Implemented | Embedding dimension analysis + transfer |
| Concept Algebra | — | Planned | Vector arithmetic (A - B + C) |
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
| `stores/safetyLevel.ts` | Safety level store (feature gating) |
| `components/ResearchComplianceDialog.vue` | Research compliance modal |
| `views/LandingView.vue` | Feature card gating |
| `router/index.ts` | Advanced-mode navigation guard |

### Backend
| File | Purpose |
|------|---------|
| `services/diffusers_backend.py` | `generate_image_with_attention()`, `generate_image_with_probing()` |
| `services/attention_processors_sd3.py` | Custom attention capture |
| `services/embedding_analyzer.py` | Dimension difference + transfer |
| `routes/settings_routes.py` | `/api/settings/safety-level` endpoint |
| `config.py` | `DEFAULT_SAFETY_LEVEL`, `SAFETY_FILTERS` |

### Configs
| File | Purpose |
|------|---------|
| `schemas/pipelines/latent_lab.json` | Passthrough pipeline (skip Stage 2) |
| `schemas/configs/interception/latent_lab.json` | UI metadata (icon, category) |
| `schemas/configs/output/attention_cartography_diffusers.json` | Attention Cartography output config |
| `schemas/configs/output/feature_probing_diffusers.json` | Feature Probing output config |

---

**Document Status:** Active (2026-02-11)
**Maintainer:** AI4ArtsEd Development Team
**Last Updated:** Session 165 (Research-level gating, architecture documentation)
