# Intellectual Property Documentation
## Cross-Modal Dimension Manipulation in Generative AI

**Status:** Defensive Publication — Establishes Prior Art
**Date:** 2026-02-17
**Author:** Prof. Dr. Benjamin Jörissen
**Organization:** UNESCO Chair in Digital Culture and Arts in Education, Friedrich-Alexander-Universität Erlangen-Nürnberg
**License:** UCDCAE AI Lab License v1.0
**Repository:** https://github.com/joeriben/ai4artsed_webserver

---

## I. Innovation Summary

### What

AI4ArtsEd implements **direct user manipulation of individual embedding dimensions across modalities** (image generation, audio synthesis, text generation) through interactive visual interfaces. Users control the internal representations of generative AI models geometrically rather than linguistically.

### Why Novel

**Existing paradigm:**
- Users control generative AI via text prompts
- Internal model representations remain opaque black boxes
- No direct access to embedding dimensions

**AI4ArtsEd innovation:**
- Users manipulate embeddings through vector operations (interpolation, extrapolation, dimension transfer)
- Embedding dimensions are exposed as interactive controls (sliders, spectral strips, bar charts)
- Same mathematical operations work uniformly across CLIP-L (768d), CLIP-G (1280d), T5-XXL (4096d), and Stable Audio T5-Base (768d) embeddings

### Technical Novelty

**Unified cross-modal framework:**

1. **Dimension-level control:** Users select specific dimensions (e.g., "transfer dimensions 42-108 from Prompt B to Prompt A")
2. **Diff-based sorting:** Dimensions ranked by discriminative power between two prompts
3. **Real-time feedback:** Every manipulation updates visual/audio output immediately
4. **Pedagogical transparency:** Every tool answers a research question explicitly

**Three integrated systems:**

| System | Modality | Embedding Space | UI Pattern | Scientific Basis |
|--------|----------|-----------------|------------|------------------|
| Latent Lab (Visual) | Image | CLIP-L (768d), T5 (4096d) | Bar charts, sliders | Mikolov 2013, Hertz 2022, Zou 2023 |
| Latent Audio Synth | Audio | T5-Base (768d) | Spectral strip (768 bars) | Kwon 2023, Stable Audio 2024 |
| Latent Text Lab | Text | LLM hidden states (variable) | Heatmaps, projections | Li 2024, Kornblith 2019, Bricken 2023 |

---

## II. Prior Art Establishment

### Publication Timeline

**Public Git Repository:** git@github.com:joeriben/ai4artsed_webserver.git

**Key Commits (Establishing Prior Art):**

| Date | Commit | Innovation |
|------|--------|------------|
| 2026-02-17 | `cbb9f96` | Wavetable synthesis as third playback mode (Crossmodal Lab) |
| 2026-02-17 | `297317b` | Dimension Explorer — spectral drawbar UI for T5 embeddings (768 bars) |
| 2026-02-16 | `06606d8` | ARCHITECTURE PART 30 — Latent Audio Synth documentation |
| 2026-02-15 | Session 178 | Latent Text Lab (RepEng, Model Comparison, Bias Archaeology) |
| 2026-02-08 | Session 162 | Hallucinator Diffusers backend (CLIP-L/T5 extrapolation) |
| 2025-12+ | Multiple | Feature Probing, Concept Algebra, Attention Cartography |

**Git Tag:** `v2.0.0-dimension-manipulation-ip-2026-02-17` (annotated, includes author + timestamp)

### Documentation

**Architecture Documentation:**
- **[PART 25](ARCHITECTURE%20PART%2025%20-%20Explorative-Vector-Based-Workflows.md):** Hallucinator (CLIP-L/T5 extrapolation)
- **[PART 28](ARCHITECTURE%20PART%2028%20-%20Latent-Lab.md):** Latent Lab (Visual + Text introspection tools)
- **[PART 30](ARCHITECTURE%20PART%2030%20-%20Latent-Audio-Synth.md):** Latent Audio Synth (768d T5 embedding space)

**Scientific Foundation:**
- **[LATENT_LAB_SCIENTIFIC_FOUNDATION.md](LATENT_LAB_SCIENTIFIC_FOUNDATION.md):** 15 peer-reviewed papers (2013-2024) mapped to implementations

**License:**
- **[LICENSE.md](../LICENSE.md):** UCDCAE AI Lab License v1.0 (bilingual DE/EN, §1-§10)

### Scientific Foundation Papers

**Directly Implemented (15 Papers):**

1. Mikolov et al. (2013) — Vector arithmetic in word embeddings
2. Belinkov (2022) — Probing classifiers for representation analysis
3. Bau et al. (2020) — Network dissection and feature rewriting
4. Hertz et al. (2022) — Prompt-to-Prompt attention control
5. Tang et al. (2022) — DAAM (Diffusion Attention Attribution Maps)
6. Kwon et al. (2023) — Semantic latent space in diffusion models
7. Liu et al. (2022) — Composable Diffusion Models
8. Zou et al. (2023) — Representation Engineering
9. Li et al. (2024) — Inference-Time Intervention
10. Kornblith et al. (2019) — Centered Kernel Alignment (CKA)
11. Olsson et al. (2022) — In-Context Learning and Induction Heads
12. Bricken et al. (2023) — Monosemanticity via Dictionary Learning
13. Olah et al. (2017, 2020) — Feature Visualization, Circuits
14. Elhage et al. (2021) — Transformer Circuits Framework
15. Radford et al. (2021) — CLIP (OpenAI)

**See:** `LATENT_LAB_SCIENTIFIC_FOUNDATION.md` for detailed mapping of papers to implementations.

---

## III. Technical Implementation

### Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                     AI4ArtsEd DevServer                      │
│                   (Orchestration Layer)                      │
└────────────────────────┬─────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
  ┌──────────┐   ┌──────────┐   ┌──────────┐
  │  Image   │   │  Audio   │   │   Text   │
  │  (SD3.5) │   │ (Stable  │   │  (LLaMA, │
  │          │   │  Audio)  │   │  Mistral)│
  └──────────┘   └──────────┘   └──────────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
                         ▼
              ┌──────────────────┐
              │   GPU Service    │
              │  (Port 17803)    │
              │  PyTorch Tensor  │
              │   Operations     │
              └──────────────────┘
```

### Core Algorithms

#### 1. Dimension Difference Analysis (Feature Probing)

**File:** `devserver/my_app/services/embedding_analyzer.py:23-54`

```python
def compute_dimension_differences(embed_a, embed_b, encoder_name):
    """
    Compute per-dimension absolute difference between two embeddings.

    Args:
        embed_a: [1, seq_len, dim] (e.g., CLIP-L: [1, 77, 768])
        embed_b: [1, seq_len, dim]
        encoder_name: 'clip_l', 'clip_g', 't5', or 'all'

    Returns:
        diff_per_dim: [dim] — absolute difference averaged over tokens
        top_dims: [N] — dimensions sorted by magnitude (descending)
    """
    # Average over sequence dimension (collapse tokens)
    mean_a = torch.mean(embed_a, dim=1)  # [1, dim]
    mean_b = torch.mean(embed_b, dim=1)  # [1, dim]

    # Absolute difference per dimension
    diff_per_dim = torch.abs(mean_b - mean_a).squeeze(0)  # [dim]

    # Sort dimensions by discriminative power
    top_dims = torch.argsort(diff_per_dim, descending=True)

    return diff_per_dim, top_dims
```

**Innovation:** No classifier training (unlike Belinkov 2022); direct difference is the signal.

#### 2. Dimension Transfer (Feature Probing Phase 2)

**File:** `devserver/my_app/services/embedding_analyzer.py:56-82`

```python
def apply_dimension_transfer(embed_a, embed_b, transfer_dims):
    """
    Copy selected dimensions from embed_b into embed_a.

    Args:
        embed_a: [1, seq_len, dim] — base embedding
        embed_b: [1, seq_len, dim] — source embedding
        transfer_dims: List[int] — dimensions to transfer

    Returns:
        embed_result: [1, seq_len, dim] — modified embedding
    """
    embed_result = embed_a.clone()

    # Replace specified dimensions (across all token positions)
    for dim in transfer_dims:
        embed_result[:, :, dim] = embed_b[:, :, dim]

    return embed_result
```

**Innovation:** Transfer operates on frozen encoder outputs, not learned latent codes (unlike IRCAM RAVE).

#### 3. Concept Algebra (A - B + C)

**File:** `devserver/my_app/services/embedding_analyzer.py:114-148`

```python
def apply_concept_algebra(embed_a, embed_b, embed_c,
                         pooled_a, pooled_b, pooled_c,
                         scale_sub=1.0, scale_add=1.0):
    """
    Apply vector arithmetic: result = A - scale_sub*B + scale_add*C

    Implements Mikolov (2013) algebra on multi-token diffusion embeddings.

    Args:
        embed_*: [1, seq_len, 4096] — SD3.5 joint embeddings
        pooled_*: [1, 2048] — Global semantic vectors
        scale_sub: Subtraction intensity
        scale_add: Addition intensity

    Returns:
        embed_result: [1, seq_len, 4096]
        pooled_result: [1, 2048]
        distance: L2 distance from embed_a
    """
    # Arithmetic on sequence embeddings
    embed_result = embed_a - (scale_sub * embed_b) + (scale_add * embed_c)

    # Same operation on pooled
    pooled_result = pooled_a - (scale_sub * pooled_b) + (scale_add * pooled_c)

    # Measure displacement
    distance = torch.norm(embed_result - embed_a).item()

    return embed_result, pooled_result, distance
```

**Innovation:** Pre-diffusion embedding arithmetic (simpler than Liu 2022's during-diffusion score combination).

#### 4. CLIP-L/T5 Extrapolation (Hallucinator)

**File:** `devserver/my_app/services/diffusers_backend.py:1843-1917`

```python
def _fuse_prompt(self, text: str, alpha: float):
    """
    Token-level LERP between CLIP-L (768d) and T5-XXL (4096d).

    Formula (first 77 tokens):
        fused = (1 - alpha) * CLIP-L_padded + alpha * T5

    Remaining tokens (78-512): pure T5 (semantic anchor)

    Args:
        text: Prompt string
        alpha: Extrapolation factor (-75 to +75)

    Returns:
        fused_embeds: [1, 512, 4096]
        pooled: [1, 2048] (CLIP-L pooled + zeros)
    """
    # 1. Encode with CLIP-L only (NO CLIP-G)
    clip_l_embeds, clip_l_pooled = self.sd3_pipeline._get_clip_prompt_embeds(
        text, clip_model_index=0  # CLIP-L
    )  # [1, 77, 768]

    # 2. Encode with T5-XXL
    t5_embeds = self.sd3_pipeline._get_t5_prompt_embeds(
        text, max_sequence_length=512
    )  # [1, 512, 4096]

    # 3. Zero-pad CLIP-L to 4096d
    clip_padded = F.pad(clip_l_embeds, (0, 4096 - 768))  # [1, 77, 4096]

    # 4. LERP first 77 tokens (THE CORE FORMULA)
    interp_len = 77
    fused_part = (1.0 - alpha) * clip_padded[:, :interp_len, :] + \
                  alpha * t5_embeds[:, :interp_len, :]

    # 5. Append T5 remainder unchanged (semantic anchor)
    t5_remainder = t5_embeds[:, interp_len:, :]
    fused_embeds = torch.cat([fused_part, t5_remainder], dim=1)  # [1, 512, 4096]

    # 6. Pooled: CLIP-L (768d) + zeros (1280d) = [1, 2048]
    pooled = F.pad(clip_l_pooled, (0, 1280))

    return fused_embeds, pooled
```

**Innovation:** Exploits dimensional asymmetry (768d vs. 4096d) as feature, not bug. Negative alpha inverts T5 attention patterns.

#### 5. Diff-Based Dimension Sorting (Latent Audio Synth)

**File:** `gpu_service/services/cross_aesthetic_backend.py:175-210`

```python
def _compute_stats(self, result_emb, emb_a, emb_b=None):
    """
    Compute embedding statistics with diff-based dimension sorting.

    If two prompts: sort by discriminative power (which dims differ most?)
    If one prompt: sort by activation magnitude

    Args:
        result_emb: [1, seq, 768] — manipulated embedding
        emb_a: [1, seq, 768] — prompt A embedding
        emb_b: [1, seq, 768] or None — prompt B embedding

    Returns:
        {
            'mean': float,
            'std': float,
            'all_activations': [{'dim': int, 'value': float}, ...],  # All 768
            'sort_mode': 'diff' | 'magnitude'
        }
    """
    # Mean over sequence dimension
    mean_result = result_emb.mean(dim=1).squeeze(0).cpu().numpy()  # [768]

    if emb_b is not None:
        # Diff-based sorting: which dimensions distinguish A from B?
        mean_a = emb_a.mean(dim=1).squeeze(0).cpu().numpy()
        mean_b = emb_b.mean(dim=1).squeeze(0).cpu().numpy()
        diff = np.abs(mean_a - mean_b)  # [768]
        sort_order = np.argsort(-diff)  # Descending
        sort_mode = 'diff'
    else:
        # Magnitude sorting: which dimensions are most active?
        sort_order = np.argsort(-np.abs(mean_result))
        sort_mode = 'magnitude'

    # Return all 768 dimensions, sorted
    all_activations = [
        {'dim': int(sort_order[i]), 'value': float(mean_result[sort_order[i]])}
        for i in range(768)
    ]

    return {
        'mean': float(mean_result.mean()),
        'std': float(mean_result.std()),
        'all_activations': all_activations,
        'sort_mode': sort_mode
    }
```

**Innovation:** Dimension sorting reveals discriminative power — not present in IRCAM's VAE latent space navigation.

### File Locations (Code References)

| Component | File | Lines | Purpose |
|-----------|------|-------|---------|
| **Feature Probing** | `devserver/my_app/services/embedding_analyzer.py` | 23-112 | Dimension difference + transfer |
| **Concept Algebra** | `devserver/my_app/services/embedding_analyzer.py` | 114-148 | A - B + C vector arithmetic |
| **Hallucinator** | `devserver/my_app/services/diffusers_backend.py` | 1843-1950 | CLIP-L/T5 extrapolation |
| **Attention Cartography** | `devserver/my_app/services/diffusers_backend.py` | 560-752 | Cross-attention extraction |
| **Denoising Archaeology** | `devserver/my_app/services/diffusers_backend.py` | 1674-1842 | Step-by-step VAE decoding |
| **Dimension Explorer** | `gpu_service/services/cross_aesthetic_backend.py` | 55-250 | T5 embedding manipulation |
| **RepEng (Text Lab)** | `gpu_service/services/text_backend.py` | 245-380 | PCA concept directions |
| **Model Comparison** | `gpu_service/services/text_backend.py` | 382-510 | CKA similarity |
| **Bias Archaeology** | `gpu_service/services/text_backend.py` | 512-698 | Token surgery |
| **UI (Feature Probing)** | `public/ai4artsed-frontend/src/views/latent_lab/feature_probing.vue` | 1-650 | Bar chart + multi-range slider |
| **UI (Dimension Explorer)** | `public/ai4artsed-frontend/src/views/latent_lab/crossmodal_lab.vue` | 400-850 | Canvas spectral strip (768 bars) |
| **UI (Latent Text Lab)** | `public/ai4artsed-frontend/src/views/latent_lab/latent_text_lab.vue` | 1-1100 | RepEng + CKA + Bias tabs |

### Performance Characteristics

| Operation | Latency | VRAM |
|-----------|---------|------|
| T5 Encoding (512 tokens) | ~50-100ms | ~200MB |
| CLIP-L Encoding (77 tokens) | ~30-50ms | ~100MB |
| Embedding Manipulation (dimension transfer, algebra) | <1ms | Negligible |
| SD3.5 Generation (25 steps) | ~3-5s | ~6GB |
| Stable Audio Generation (20 steps, 1s audio) | ~1.2-1.5s | ~2.6GB |
| Canvas Redraw (768 bars) | ~2-5ms | Client-side |
| CKA Matrix (32×32 layers) | ~500ms-2s | ~1GB |

---

## IV. Use Cases & Embodiments

### 1. Educational Use Case

**Target:** Cultural education for ages 13-17

**Scenario:** "How does a text-to-image model represent color?"

**Workflow:**
1. Student enters two prompts: "red house" and "blue house"
2. Feature Probing shows bar chart of 4096 dimensions
3. Dimensions are sorted by difference magnitude (diff-based sorting)
4. Student observes: hundreds of dimensions change, not just one "color dimension"
5. Student selects top 100 dimensions → transfers to "red house" → house becomes partially blue
6. **Learning outcome:** Color is distributed across dimensions, not localized

**Pedagogical value:** Falsifies naive understanding ("Dimension 42 = color") through interactive experimentation.

### 2. Artistic Use Case

**Target:** Digital artists exploring AI-generated aesthetics

**Scenario:** "Create surreal variations by extrapolating beyond CLIP and T5"

**Workflow:**
1. Artist enters prompt: "forest landscape"
2. Hallucinator alpha slider set to 25 (high extrapolation)
3. System generates hallucinatory image with dreamlike morphology
4. Artist iterates alpha -10 → 0 → 10 → 25 → 50 to explore aesthetic range
5. **Artistic outcome:** Non-photographic, conceptually coherent AI hallucinations

**Creative value:** Access to out-of-distribution regions of embedding space enables novel aesthetics.

### 3. Research Use Case

**Target:** AI researchers studying model biases

**Scenario:** "Does this LLM associate 'doctor' with masculine pronouns?"

**Workflow:**
1. Researcher enters prompt: "The doctor explained to the nurse"
2. Bias Archaeology suppresses feminine pronouns ("she", "her", "herself")
3. System generates baseline + manipulated samples with same seeds
4. Baseline: "...that she should..." → Feminine default for "nurse"
5. Manipulated: "...that they should..." → Switches to neutral
6. **Research outcome:** Quantifiable gender bias detection

**Scientific value:** Systematic bias probing without training diagnostic classifiers.

---

## V. Defensive Publication Strategy

### Purpose

This document serves as **defensive publication** to establish **prior art** for the innovations described herein. By making this work publicly accessible before any third-party patent applications, we prevent the patenting of these ideas by others.

### Legal Mechanism

Under patent law, an invention is not patentable if it has been publicly disclosed before the patent application date. This document, combined with:

1. **Public Git repository** (git@github.com:joeriben/ai4artsed_webserver.git)
2. **Timestamped Git tag** (v2.0.0-dimension-manipulation-ip-2026-02-17)
3. **Architecture documentation** (PART 25, 28, 30)
4. **Scientific report** (LATENT_LAB_SCIENTIFIC_FOUNDATION.md)

...constitutes a complete, dated, and publicly accessible disclosure.

### Publication Details

- **Date:** 2026-02-17
- **Medium:** GitHub (public repository)
- **License:** UCDCAE AI Lab License v1.0 (open for non-commercial educational use)
- **Accessibility:** Worldwide, no registration required
- **Archiving:** Git history provides immutable timestamped record

### What This Protects

**Prevents third parties from patenting:**

1. Direct manipulation of embedding dimensions across modalities (image/audio/text)
2. Diff-based dimension sorting for discriminative power ranking
3. Per-dimension offset control in spectral strip UI
4. CLIP-L/T5 extrapolation with dimensional asymmetry exploitation
5. Interactive dimension transfer with multi-range selection
6. Real-time embedding manipulation with immediate visual/audio feedback

**Does NOT prevent:**

- Legitimate independent inventions (developed before this disclosure)
- Derivative works under different licenses (subject to UCDCAE AI Lab License terms)
- Commercial use with proper licensing agreement (see LICENSE.md §3(c))

### Future Reinforcement

**Planned:**
- arXiv preprint submission (academic indexing)
- Conference paper submission (peer review + publication)
- Workshop presentations (dissemination to research community)

---

## VI. Scientific Foundation & Cross-Modal Relationships

**Reference:** `docs/LATENT_LAB_SCIENTIFIC_FOUNDATION.md`

### Key Academic Foundations

#### 1. Vector Arithmetic in Embedding Spaces (Mikolov 2013)

**Paper:** "Distributed Representations of Words and Phrases and their Compositionality"
**DOI:** [10.48550/arXiv.1310.4546](https://doi.org/10.48550/arXiv.1310.4546)

**Principle:** vec("King") - vec("Man") + vec("Woman") ≈ vec("Queen")

**Implemented across modalities:**
- **Image:** Concept Algebra (A - B + C on SD3.5 embeddings)
- **Audio:** Latent Audio Synth (interpolation/extrapolation)
- **Text:** RepEng (concept direction arithmetic)

**Innovation:** Applies word2vec algebra to multi-token, multi-encoder diffusion embeddings (not just word vectors).

#### 2. Representation Engineering (Zou 2023)

**Paper:** "Representation Engineering: A Top-Down Approach to AI Transparency"
**DOI:** [10.48550/arXiv.2310.01405](https://doi.org/10.48550/arXiv.2310.01405)

**Principle:** Reading and steering model behavior via activation manipulation

**Implemented:**
- **Image:** Feature Probing (dimension transfer)
- **Text:** RepEng (PCA concept directions + forward hooks)

**Innovation:** Per-dimension offset control in real-time (not just concept direction injection).

#### 3. Attention Attribution (Hertz 2022, Tang 2022)

**Papers:**
- Hertz et al. "Prompt-to-Prompt Image Editing with Cross Attention Control" ([10.48550/arXiv.2208.01626](https://doi.org/10.48550/arXiv.2208.01626))
- Tang et al. "What the DAAM: Interpreting Stable Diffusion Using Cross Attention" ([10.48550/arXiv.2210.04885](https://doi.org/10.48550/arXiv.2210.04885))

**Principle:** Cross-attention maps show token→region attribution

**Implemented:** Attention Cartography (multi-layer, multi-timestep visualization)

**Innovation:** Interactive token selection + BPE token grouping + 25 timesteps × 3 layers = 75 maps.

#### 4. Semantic Latent Space (Kwon 2023)

**Paper:** "Diffusion Models Already Have a Semantic Latent Space"
**DOI:** [10.48550/arXiv.2210.10960](https://doi.org/10.48550/arXiv.2210.10960)

**Principle:** Three phases of diffusion — Composition (steps 1-8) → Semantics (9-17) → Detail (18-25)

**Implemented:** Denoising Archaeology (step-by-step VAE decoding)

**Innovation:** All 25 steps visualized as filmstrip timeline with phase annotations.

#### 5. Centered Kernel Alignment (Kornblith 2019)

**Paper:** "Similarity of Neural Network Representations Revisited"
**DOI:** [10.48550/arXiv.1905.00414](https://doi.org/10.48550/arXiv.1905.00414)

**Principle:** Dimensionality-invariant representation similarity via kernel alignment

**Implemented:** Comparative Model Archaeology (CKA heatmaps for LLM layer comparison)

**Innovation:** Interactive canvas-based heatmap with layer-pair tooltips.

#### 6. Monosemanticity & Bias Detection (Bricken 2023)

**Paper:** "Towards Monosemanticity: Decomposing Language Models With Dictionary Learning" (Anthropic)

**Principle:** Sparse features reveal interpretable model biases

**Implemented:** Bias Archaeology (systematic token suppression/boosting)

**Innovation:** Automatic LLM interpretation of bias patterns (meta-LLM explains experiment results).

### Novel Cross-Modal Contribution

**The innovation lies not in individual techniques** (all grounded in published research), **but in their unified application across modalities:**

1. **Same mathematical operations** (interpolation, extrapolation, dimension transfer) work on:
   - CLIP-L (768d), CLIP-G (1280d), T5-XXL (4096d) for image generation
   - T5-Base (768d) for audio synthesis
   - LLM hidden states (variable dimensions) for text generation

2. **Diff-based dimension sorting** reveals discriminative power uniformly across encoders

3. **Pedagogical framework:** "Show, don't simplify" — complex ML concepts made experiential without mathematical reduction

**15 Scientific Papers (2013-2024)** implemented as interactive tools accessible to ages 13-17.

---

## VII. Critical Differentiation from IRCAM Research

### IRCAM's Latent Space Work (Relevant Context)

IRCAM (Institut de Recherche et Coordination Acoustique/Musique) has developed several tools for latent space control in audio:

1. **[RAVE](https://acids-ircam.github.io/RAVE/)** (Realtime Audio Variational autoEncoder)
   - VAE-based neural audio synthesis with 128 latent dimensions
   - Control of learned latent space via dimensionality reduction
   - Target: Professional musicians, Max/MSP integration

2. **[Latent Terrain](https://forum.ircam.fr/article/detail/latent-terrain-dissecting-the-latent-space-of-neural-audio-autoencoder-by-shuoyang-jasper-zheng/)** (Zheng 2024)
   - 2D projection of neural audio autoencoder latent spaces
   - Algorithmic dissection for creative interactive systems

3. **[Embodied Latent Exploration](https://ircam-ismm.github.io/embodied-latent-exploration/)** (MOCO'24)
   - Dance-music performance via latent space navigation
   - Embodied interaction with generative audio models

4. **[Weaving Memory Matter](https://forum.ircam.fr/article/detail/weaving-memory-matter-steering-latent-audio-models-through-interactive-machine-learning/)** (Vigliensoni)
   - Interactive ML for steering latent audio models
   - Creative control through machine learning

### Fundamental Differences (AI4ArtsEd vs. IRCAM)

| Dimension | IRCAM Approach | AI4ArtsEd Innovation |
|-----------|----------------|---------------------|
| **Latent Space Type** | VAE-learned latent space (audio synthesis via training) | Pre-trained encoder embeddings (CLIP, T5, Stable Audio) — frozen, no training |
| **Control Paradigm** | Learned representations via model training | Direct dimension manipulation of frozen encoders |
| **Modality** | Audio-centric (RAVE, Latent Terrain, Max/MSP) | Cross-modal (image + audio + text unified framework) |
| **Target Audience** | Professional composers, performers, researchers (adults) | Youth (ages 13-17), cultural education contexts |
| **Cultural Theory** | **Production-oriented** — create new music/art through AI | **Reflection-oriented** — critique/understand AI mechanisms |
| **Pedagogical Goal** | Instrument/tool for creative practice (composition) | Deconstructive introspection for critical AI literacy |
| **Technical Focus** | VAE architecture, perceptual loss functions, timbre space | Embedding arithmetic, representation engineering, attention analysis |
| **Integration** | Max/MSP, Ableton Live (professional production environments) | Standalone web platform (zero prerequisites, educational access) |
| **Scientific Method** | Generative model training + evaluation (research ML) | Probing/manipulation of existing models (interpretability) |

### Cultural-Theoretical Differentiation

#### IRCAM (Productive Aesthetics)

- **Tradition:** Electroacoustic music (Pierre Schaeffer, musique concrète)
- **Goal:** Empower composers to shape sound via machine learning tools
- **Epistemology:** Technology as creative extension (cyborg aesthetics, human-AI collaboration)
- **Reference:** Magnusson's "Sonic Writing" — instruments shape musical thought

**Focus:** "What new sounds can I create with this AI?"

#### AI4ArtsEd (Critical Pedagogy)

- **Tradition:** Cultural education (Kulturelle Bildung), critical AI literacy
- **Goal:** Demystify AI through hands-on deconstruction (Cultural Resilience paradigm)
- **Epistemology:** Technology as object of critical inquiry (postdigital dissensus, media competence)
- **Reference:** Jörissen & Klepacki 2025 ("Cultural Resilience and Planetary Dissensus")

**Focus:** "How does the AI internally construct meaning?"

### Pedagogical Differentiation

#### IRCAM Educational Programs

- **Prerequisites:** Advanced training for practitioners (Max/MSP fluency assumed, music production knowledge)
- **Content:** "How to use RAVE for composition" — tool mastery
- **Age:** Adult professionals, university-level students
- **Outcome:** Compositional skills with neural synthesis

#### AI4ArtsEd Latent Lab

- **Prerequisites:** Zero (web-based, no coding/DAW/music theory required)
- **Content:** "How does the model internally represent concepts?" — model understanding
- **Age:** 13-17 (suitable for secondary school contexts)
- **Outcome:** Critical AI literacy (understanding model limitations, biases, mechanisms)

### Novel Contribution (Not Present in IRCAM Work)

1. **Unified Cross-Modal Framework:**
   - IRCAM: Audio-only (RAVE, Latent Terrain)
   - AI4ArtsEd: Same operations (interpolation, dimension transfer) across image/audio/text

2. **Diff-Based Dimension Sorting:**
   - IRCAM: VAE latent space navigation via dimensionality reduction (PCA, t-SNE)
   - AI4ArtsEd: Dimensions ranked by discriminative power between two prompts

3. **Pedagogical Transparency:**
   - IRCAM: Creative affordances (what can I do with this?)
   - AI4ArtsEd: Research questions (what does this dimension encode?)

4. **No Training Required:**
   - IRCAM: Trained VAEs (hours of training, large datasets)
   - AI4ArtsEd: Frozen encoders (instant, zero computational barrier)

### Complementarity, Not Competition

IRCAM and AI4ArtsEd serve different **cultural functions**:

- **IRCAM** → **Kunstproduktion** (art production in electroacoustic tradition)
- **AI4ArtsEd** → **Kunstpädagogik** (arts education as critical cultural practice)

Both manipulate latent spaces, but with fundamentally different **teleologies**:

- **IRCAM:** "What new sounds can I create?" (productive)
- **AI4ArtsEd:** "How does the AI construct meaning?" (analytical)

**No IP conflict:** Different domains, different audiences, different goals.

---

## VIII. References

### Architecture Documentation

- **[PART 25](ARCHITECTURE%20PART%2025%20-%20Explorative-Vector-Based-Workflows.md):** Hallucinator (CLIP-L/T5 extrapolation), geometric deep-dive
- **[PART 28](ARCHITECTURE%20PART%2028%20-%20Latent-Lab.md):** Latent Lab (Visual + Text introspection tools), scientific foundation
- **[PART 30](ARCHITECTURE%20PART%2030%20-%20Latent-Audio-Synth.md):** Latent Audio Synth (768d T5 embedding space), diff-based sorting

### Scientific Foundation

- **[LATENT_LAB_SCIENTIFIC_FOUNDATION.md](LATENT_LAB_SCIENTIFIC_FOUNDATION.md):** Complete mapping of 15 papers to implementations

### License

- **[LICENSE.md](../LICENSE.md):** UCDCAE AI Lab License v1.0 (bilingual DE/EN)

### Git Repository

- **Repository:** git@github.com:joeriben/ai4artsed_webserver.git
- **Tag:** v2.0.0-dimension-manipulation-ip-2026-02-17
- **Commit History:** Public, timestamped, immutable

### Scientific Papers (15 Primary Sources)

See `LATENT_LAB_SCIENTIFIC_FOUNDATION.md` Section 9 for complete bibliography.

Key papers:
- Mikolov et al. (2013) — Word2Vec algebra
- Zou et al. (2023) — Representation Engineering
- Hertz et al. (2022) — Prompt-to-Prompt attention control
- Kwon et al. (2023) — Semantic latent space in diffusion
- Kornblith et al. (2019) — Centered Kernel Alignment (CKA)
- Bricken et al. (2023) — Monosemanticity

### IRCAM Research (Context for Differentiation)

- **RAVE:** https://acids-ircam.github.io/RAVE/
- **Latent Terrain:** https://forum.ircam.fr/article/detail/latent-terrain-dissecting-the-latent-space-of-neural-audio-autoencoder-by-shuoyang-jasper-zheng/
- **Embodied Latent Exploration:** https://ircam-ismm.github.io/embodied-latent-exploration/
- **Weaving Memory Matter:** https://forum.ircam.fr/article/detail/weaving-memory-matter-steering-latent-audio-models-through-interactive-machine-learning/

---

## IX. Declaration

This document constitutes a **public disclosure** of the innovations described herein, effective as of the date of publication (2026-02-17). By publishing this work under the UCDCAE AI Lab License v1.0, we make it freely available for non-commercial educational use while establishing clear prior art to prevent third-party patent claims.

**Author:** Prof. Dr. Benjamin Jörissen
**Organization:** UNESCO Chair in Digital Culture and Arts in Education
**Institution:** Friedrich-Alexander-Universität Erlangen-Nürnberg
**Email:** benjamin.joerissen@fau.de

---

**Document Status:** Active — Defensive Publication
**Version:** 1.0
**Date:** 2026-02-17
**License:** CC BY-SA 4.0 (this documentation)
**Software License:** UCDCAE AI Lab License v1.0
