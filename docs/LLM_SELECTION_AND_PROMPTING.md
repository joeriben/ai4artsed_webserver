# LLM Selection and Prompting Strategy
**AI4ArtsEd DevServer - Model Selection and Prompt Optimization**

> **Last Updated:** 2026-01-23 (Session 132)
> **Status:** Active Architecture Decision

---

## 1. Task Requirements: SD3.5 CLIP Prompt Optimization

### What the Task Demands

| Requirement | Complexity | Why |
|-------------|------------|-----|
| **Multilingual I/O** | HIGH | Must respond in input language (DE, BG, Yoruba...) |
| **Scene-to-2D Transformation** | HIGH | Convert narrative to frozen visual frame |
| **Photographic Techniques** | HIGH | Domain knowledge required |
| **Atmosphere → Visible Elements** | HIGH | Semantic transformation |
| **Cultural Neutrality** | HIGH | No artist names, no art-historical terms |
| **Token Prioritization** | MEDIUM | CLIP weights early tokens |
| **Structured Output** | MEDIUM | Comma-separated, JSON format |

### Critical Insight: Not a Simple Instruction-Following Task

This is NOT pattern matching. The model must:
1. **Understand** semantic meaning in any language
2. **Transform** narrative descriptions to visual specifications
3. **Maintain** language consistency (no mid-response language switching)
4. **Apply** domain knowledge (photography, visual arts)
5. **Follow** complex multi-rule instructions

---

## 2. Model Evaluation (January 2026)

### Local Models Available (96GB VRAM)

| Model | VRAM | Architecture | Multilingual | Low-Resource Languages |
|-------|------|--------------|--------------|------------------------|
| **llama4:scout** | 67GB | 109B MoE (17B active) | 200 languages, 10x more data | ✅ Explicit support |
| **Mistral Large 3** | ~80GB | 675B MoE (41B active) | 40+ languages | ⚠️ No data for African |
| **gpt-OSS:120b** | 65GB | 117B MoE (5.1B active) | Good | ⚠️ No data |
| **Qwen3-next** | 50GB | 235B MoE (22B active) | 119 languages | ❌ Yoruba "unoptimized" |

### Cloud Models

| Model | Multilingual | Low-Resource | Instruction Following | Cost |
|-------|--------------|--------------|----------------------|------|
| **Claude 4.5 Sonnet** | Excellent | ✅ Best coverage | Excellent | $3/$15 per M tokens |
| **Claude 4.5 Haiku** | Excellent | ✅ Good | 90% of Sonnet | $1/$5 per M tokens |
| **GPT-4o** | Good | Good | Good | ~$5/$15 per M tokens |

### Benchmark Data

#### General Performance
| Model | MMLU | Instruction Following | Notes |
|-------|------|----------------------|-------|
| gpt-OSS:120b | 90% | Top-tier | OpenAI training style |
| Qwen3-235B | 85.7% | 73.0 MultiIF | Excludes Yoruba |
| llama4:scout | 79.6% | Good (architecture-improved) | 200 languages |
| Mistral Large 3 | ~85% | Top-tier | Best non-EN/CN |

#### Low-Resource Language Performance (MMLU-ProX)
| Language | Qwen3-235B | Status |
|----------|------------|--------|
| English | 80.7% | High-resource |
| German | ~80% | High-resource |
| Bulgarian | ~70% | Medium-resource |
| Yoruba | **3.9-57%** | ❌ Explicitly excluded |
| Wolof | 0.6-58.6% | Very low-resource |

---

## 3. Practical Experience (User Feedback)

| Model | Experience | Likely Cause |
|-------|------------|--------------|
| **Claude Sonnet** | Top | Optimized for instruction following |
| **gpt-OSS:120b** | Quite usable | OpenAI training = Claude-similar |
| **llama4:scout** | So-so | Needs different prompt structure |
| **Mistral** | Unusable | Very sensitive to prompt format |

### Key Insight: Prompt Format Sensitivity

Different model families respond to different prompt structures:

| Model Family | Preferred Style |
|--------------|-----------------|
| **Claude/OpenAI** | Structured with `===`, Markdown, clear sections |
| **Llama 4** | Flatter, more examples, shorter rule blocks |
| **Mistral** | Very precise, short instructions, minimal nesting |

---

## 4. Recommendation

### Primary Strategy: llama4:scout with Adapted Prompts

**Rationale:**
1. Only model with explicit low-resource language support (200 languages, 10x multilingual data)
2. Avoids constant VRAM swapping
3. Meta-prompts can be adapted to Llama's preferred style

### Model-Specific Prompt Variants

Three variants of each optimization prompt:

| Variant | Target | Characteristics |
|---------|--------|-----------------|
| `default` | Claude/OpenAI | Structured sections, `===` markers, detailed rules |
| `llama` | Llama 4 | Flat structure, more examples, shorter rules |
| `mistral` | Mistral | Minimal, precise, no nesting |

---

## 5. Prompt Variant Specifications

### 5.1 Claude/OpenAI Style (Default)

**Characteristics:**
- Structured with `===` section markers
- Detailed rule explanations
- Hierarchical organization
- Works well with long, complex instructions

**Example Structure:**
```
=== SECTION NAME ===
Detailed explanation of the concept.

RULES:
1. First rule with explanation
2. Second rule with explanation

=== NEXT SECTION ===
...
```

### 5.2 Llama Style

**Characteristics:**
- Flat structure, minimal nesting
- Heavy use of examples (Llama learns from examples)
- Short, direct rules (loses context with long instructions)
- System prompt utilized (unlike DeepSeek-R1)

**Example Structure:**
```
You transform scenic descriptions into 2D image specifications.

RULES:
- Remove temporal words
- Convert actions to poses
- Use neutral visual descriptors

EXAMPLES:
Input: "A mysterious forest..."
Output: "ancient forest, gnarled trees, twilight, mist..."

Input: "The scientist discovered..."
Output: "scientist, lab coat, glowing tube, laboratory..."
```

### 5.3 Mistral Style

**Characteristics:**
- Extremely concise
- No section markers
- Direct imperatives
- Minimal examples (only if necessary)

**Example Structure:**
```
Transform narrative text to 2D image tokens.
Remove: temporal words, causality, narrative voice.
Convert: actions→poses, atmosphere→visible elements.
Format: comma-separated, max 75 tokens.
Forbidden: artist names, art-historical terms.
Output: JSON {"clip_prompt": "..."}
```

---

## 6. Implementation Strategy

### Dynamic Prompt Selection

```python
# In prompt loading logic
def get_prompt_variant(model_name: str) -> str:
    if "llama" in model_name.lower():
        return "llama"
    elif "mistral" in model_name.lower():
        return "mistral"
    else:
        return "default"  # Claude/OpenAI style
```

### File Structure

```
devserver/schemas/chunks/
├── output_image_sd35_large.json          # Contains optimization_instruction
├── optimize_clip_prompt.json             # Default (Claude/OpenAI)
├── optimize_clip_prompt_llama.json       # Llama variant
├── optimize_clip_prompt_mistral.json     # Mistral variant
├── optimize_t5_prompt.json               # Default (Claude/OpenAI)
├── optimize_t5_prompt_llama.json         # Llama variant
└── optimize_t5_prompt_mistral.json       # Mistral variant
```

### Alternative: Single File with Variants

```json
{
  "name": "optimize_clip_prompt",
  "variants": {
    "default": { "prompt": "..." },
    "llama": { "prompt": "..." },
    "mistral": { "prompt": "..." }
  }
}
```

---

## 7. References

### Sources (January 2026)

- [Qwen3 Technical Report](https://arxiv.org/pdf/2505.09388) - Multilingual limitations
- [Llama 4 Official](https://www.llama.com/models/llama-4/) - 200 language support
- [Mistral 3 Announcement](https://mistral.ai/news/mistral-3) - Best non-EN/CN
- [gpt-OSS Model Card](https://cdn.openai.com/pdf/419b6906-9da6-406c-a19d-1bb078ac7637/oai_gpt-oss_model_card.pdf)
- [Claude 4.5 Haiku](https://www.anthropic.com/news/claude-haiku-4-5) - Instruction following
- [MMLU-ProX Multilingual](https://arxiv.org/pdf/2503.10497) - African language benchmarks
- [State of LLMs for African Languages](https://arxiv.org/html/2506.02280v3)

### Related Documentation

- `DEVELOPMENT_DECISIONS.md` - Design decision record
- `ARCHITECTURE PART 09 - Model-Selection.md` - Model configuration
- `devserver/config.py` - Model constants

---

## 8. Decision Record

**Date:** 2026-01-23
**Decision:** Use llama4:scout as primary local model with model-specific prompt variants
**Reasoning:**
1. Only model with documented low-resource language support
2. Aligns with platform's global diversity goals
3. 96GB VRAM allows single-model strategy (no swapping)
4. Meta-prompts can be adapted per model family

**Affected Files:**
- `devserver/schemas/chunks/optimize_clip_prompt.json`
- `devserver/schemas/chunks/optimize_t5_prompt.json`
- `devserver/schemas/chunks/output_image_sd35_large.json`
- `devserver/config.py` (model selection)
