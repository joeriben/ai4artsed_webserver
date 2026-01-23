# Handover: Session 132 - LLM Model-Specific Prompting

**Date:** 2026-01-23
**Session:** 132
**Status:** IMPLEMENTED (Core) + TODOs remaining

---

## Summary

Implemented model-specific prompt variants for SD3.5 CLIP/T5 optimization to handle different LLM families (Llama, Mistral, Claude/OpenAI) with their preferred prompting styles.

---

## Commits This Session

| Commit | Description |
|--------|-------------|
| `3213bf0` | SD3.5 CLIP meta-prompt with scene-to-2D transformation |
| `0a3394d` | T5 optimization prompt consistency update |
| `a778f6b` | Model-specific variants + LLM documentation |
| `39b0ffe` | Dynamic prompt selection in ChunkBuilder |

---

## What Was Implemented

### 1. Core Meta-Prompt Improvements

**Files modified:**
- `devserver/schemas/chunks/output_image_sd35_large.json` (optimization_instruction)
- `devserver/schemas/chunks/optimize_clip_prompt.json`
- `devserver/schemas/chunks/optimize_t5_prompt.json`

**Key changes:**
- Scene-to-2D transformation rules (frozen moment principle)
- Token architecture for triple CLIP (clip_g, clip_L, T5)
- CLIP syntax guide (keyword weighting, blending)
- Culturally neutral descriptors (NO artist names, NO art-historical terms)

### 2. Model-Specific Variants Created

```
devserver/schemas/chunks/
├── optimize_clip_prompt.json          # Default (Claude/OpenAI)
├── optimize_clip_prompt_llama.json    # Llama: example-heavy, flat
├── optimize_clip_prompt_mistral.json  # Mistral: minimal, precise
├── optimize_t5_prompt.json            # Default (Claude/OpenAI)
├── optimize_t5_prompt_llama.json      # Llama variant
└── optimize_t5_prompt_mistral.json    # Mistral variant
```

### 3. Dynamic Selection Logic

**File:** `devserver/schemas/engine/chunk_builder.py`

```python
def get_model_family(model_name: str) -> str:
    """Returns 'llama' | 'mistral' | 'default'"""

def _get_template_with_variant(self, chunk_name, model_name=None):
    """Auto-selects variant based on configured model"""
```

**Flow:**
```
config.STAGE2_OPTIMIZATION_MODEL = "local/llama4:scout"
                    ↓
get_model_family() → "llama"
                    ↓
_get_template_with_variant("optimize_clip_prompt")
                    ↓
Returns: optimize_clip_prompt_llama template
```

### 4. Documentation Created

- `docs/LLM_SELECTION_AND_PROMPTING.md` - Full LLM analysis
- `docs/DEVELOPMENT_DECISIONS.md` - Design decision added

---

## TODO: Missing Model-Specific Variants

The following prompts also need model-specific variants:

### 1. Interception Instruction (Stage 2)

**Current location:** `devserver/schemas/chunks/manipulate.json`

**What it does:** 3-part prompt interception (TASK_INSTRUCTION + CONTEXT + INPUT_TEXT)

**TODO:**
```
devserver/schemas/chunks/
├── manipulate.json              # Default (exists)
├── manipulate_llama.json        # TODO: Create
└── manipulate_mistral.json      # TODO: Create
```

### 2. Translation Instruction (Stage 3)

**Current location:** Likely in `schema_pipeline_routes.py` or a separate chunk

**TODO:** Find translation prompt location and create variants:
```
├── translate.json               # Default
├── translate_llama.json         # TODO
└── translate_mistral.json       # TODO
```

### 3. Safety Check Prompts (Stage 1 & 3)

**Locations to check:**
- `devserver/schemas/chunks/` - safety-related chunks
- `devserver/my_app/routes/schema_pipeline_routes.py` - inline prompts

---

## Key Files Reference

### Configuration
- `devserver/config.py` - Model constants (STAGE2_OPTIMIZATION_MODEL, etc.)

### Prompt Chunks
- `devserver/schemas/chunks/` - All prompt templates

### Selection Logic
- `devserver/schemas/engine/chunk_builder.py` - `get_model_family()`, `_get_template_with_variant()`

### Documentation
- `docs/LLM_SELECTION_AND_PROMPTING.md` - Full analysis with benchmarks
- `docs/DEVELOPMENT_DECISIONS.md` - Design decision

---

## Model Family Detection

```python
# From chunk_builder.py
def get_model_family(model_name: str) -> str:
    model_lower = model_name.lower()

    if any(x in model_lower for x in ["llama", "meta-llama"]):
        return "llama"

    if any(x in model_lower for x in ["mistral", "mixtral", "ministral", "magistral"]):
        return "mistral"

    return "default"  # Claude, OpenAI, Qwen, DeepSeek, etc.
```

---

## Prompting Style Summary

| Family | Characteristics | Example |
|--------|----------------|---------|
| **Default** (Claude/OpenAI) | Structured `===` sections, detailed rules, hierarchical | Current prompts |
| **Llama** | Flat, example-heavy, short rules, system prompt used | See `*_llama.json` |
| **Mistral** | Minimal, precise, no nesting, imperatives only | See `*_mistral.json` |

---

## Testing Command

```bash
cd /home/joerissen/ai/ai4artsed_development/devserver
python3 -c "
from schemas.engine.chunk_builder import ChunkBuilder, get_model_family
from pathlib import Path

builder = ChunkBuilder(Path('schemas'))

# Test variant selection
import config
config.STAGE2_OPTIMIZATION_MODEL = 'local/llama4:scout'
template = builder._get_template_with_variant('optimize_clip_prompt')
print(f'llama4 -> {template.name}')

config.STAGE2_OPTIMIZATION_MODEL = 'mistral/mistral-large-latest'
template = builder._get_template_with_variant('optimize_clip_prompt')
print(f'mistral -> {template.name}')
"
```

---

## LLM Recommendation (from analysis)

| Priority | Model | Use Case |
|----------|-------|----------|
| **1. Local** | llama4:scout (67GB) | Best low-resource language support (200 languages) |
| **2. Local** | Mistral Large 3 (~80GB) | Best for European languages |
| **3. Cloud** | Claude 4.5 Sonnet | Best overall, best low-resource |
| **4. Fallback** | gpt-OSS:120b (65GB) | Solid all-round |

**NOT recommended:** Qwen3 (Yoruba explicitly "unoptimized")

---

## Next Session Tasks

1. [ ] Create `manipulate_llama.json` and `manipulate_mistral.json`
2. [ ] Find and create translation prompt variants
3. [ ] Review safety check prompts for variant needs
4. [ ] Test with real prompts in German, Bulgarian, Yoruba
5. [ ] Update `config.py` to use `llama4:scout` as default

---

## Platform Principles (CRITICAL)

- **NO artist names** - "style of [artist]" is FORBIDDEN
- **NO art-historical technique terms** from any tradition (anti-Eurocentric)
- **Culturally neutral descriptors only**: light, texture, space, color
- **Multilingual I/O**: Response must be in input language

See `docs/LLM_SELECTION_AND_PROMPTING.md` for full details.
