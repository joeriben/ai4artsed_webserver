# SESSION 56 HANDOVER: Flow Consolidation Refactoring

**Date:** 2025-11-20
**Previous Session:** 55 (Config-based Model Selection)
**Next Task:** Major architecture refactoring - consolidate 4-stage flow into cleaner 2-stage flow

---

## 🎯 GOAL: Eliminate Stage 3, Make Stage 2 a Mega-Prompt

### Current Architecture (Slow, Redundant):
```
Stage 1: Translation + §86a Safety (GPT-OSS:20b local)
Stage 2: Prompt Interception (Claude 4.5 remote)
Stage 3: Pre-Output Safety Check (GPT-OSS:20b local) ← REDUNDANT!
Stage 4: Media Generation (ComfyUI/SwarmUI)
```

### Target Architecture (Fast, Clean):
```
Stage 1: Input Cleaning
  1. Typo correction (context-sensitive: kids/youth, art course) ✅ ALREADY IMPLEMENTED
  2. English translation
  3. §86a Safety check
  → USER CHOOSES MEDIUM HERE ← NEW!

Stage 2: Smart Transformation (ONE LLM call, concatenated prompt)
  1. Prompt Interception (artistic transformation with config context)
  2. Medium-specific optimization (SD3.5, FLUX, GPT-5, audio, etc.)
  3. Final safety assessment (kids/youth/adult/off)
  → Output: optimized prompt + negative_prompt

Stage 3: ELIMINATED ← 33% FASTER!

Stage 4: Media Generation (unchanged)
```

---

## 📋 IMPLEMENTATION PLAN

### Phase 1: Preparation (Metadata & Config)

#### 1.1 Add Media-Specific Optimization Instructions

**File:** Each output config in `devserver/schemas/configs/output/*.json`

**Add to meta:**
```json
{
  "meta": {
    "optimization_instruction": "Optimize for Stable Diffusion 3.5: Create detailed visual description with concrete nouns, specific materials, lighting, composition. Avoid abstract concepts. Include art historical references when relevant. Specify medium (oil painting, watercolor, digital art, etc.)."
  }
}
```

**Examples per medium:**
- **SD3.5/FLUX (image):** "Detailed visual description, concrete materials, lighting, composition, art medium"
- **GPT-5 Image:** "Narrative scene description, emotional atmosphere, symbolic elements, creative interpretation"
- **Stable Audio:** "Sonic textures, instruments, rhythm, mood, genre references, tempo, dynamics"
- **Music generation:** "Musical structure, instrumentation, harmony, melody patterns, genre fusion"

**Files to edit:**
- `devserver/schemas/configs/output/sd35_large.json`
- `devserver/schemas/configs/output/gpt5_image.json`
- `devserver/schemas/configs/output/flux_dev.json`
- All audio/music configs

#### 1.2 Define Safety-Level Filter Texts

**File:** `devserver/config.py`

**Add after STAGE*_MODEL section:**
```python
# ----------------------------------------------------------------------------
# 6. SAFETY FILTER TEXTS (for Stage 2 mega-prompt)
# ----------------------------------------------------------------------------
# These texts are concatenated into Stage 2 prompt for final safety assessment

SAFETY_FILTER_KIDS = """
Ensure the output is appropriate for children (ages 6-12):
- NO violence, gore, blood, death, weapons, fighting
- NO horror elements (scary, frightening, monsters, demons, zombies)
- NO sexual content (nude, naked, inappropriate)
- NO psychological distress (suicide, self-harm, depression)
- IF UNSAFE: Set "safe": false and explain why in "abort_reason"
"""

SAFETY_FILTER_YOUTH = """
Ensure the output is appropriate for youth (ages 13-17):
- NO explicit violence (torture, brutal, savage, mutilation)
- NO sexual content (pornographic, explicit, nsfw, genitals)
- NO self-harm content (suicide, cutting, self-injury)
- Mild scary/action themes acceptable if contextually appropriate
- IF UNSAFE: Set "safe": false and explain why in "abort_reason"
"""

SAFETY_FILTER_ADULT = """
Ensure the output complies with German law (18+):
- NO §86a StGB violations (Nazi symbols, terrorist organizations)
- Artistic nudity acceptable in appropriate context
- Mature themes acceptable (violence, horror, etc.)
- IF ILLEGAL: Set "safe": false and explain why in "abort_reason"
"""

SAFETY_FILTER_OFF = """
No content filtering (development/testing only).
- Still check for §86a StGB violations (legal requirement)
- IF ILLEGAL: Set "safe": false and explain why in "abort_reason"
"""
```

#### 1.3 Create Safety Filter Lookup

**File:** `devserver/config.py`

```python
# Safety filter lookup dict
SAFETY_FILTERS = {
    'kids': SAFETY_FILTER_KIDS,
    'youth': SAFETY_FILTER_YOUTH,
    'adult': SAFETY_FILTER_ADULT,
    'off': SAFETY_FILTER_OFF
}
```

---

### Phase 2: Stage 2 Mega-Prompt Template

#### 2.1 Create New Chunk: `smart_transform.json`

**File:** `devserver/schemas/chunks/smart_transform.json`

```json
{
  "name": "smart_transform",
  "description": "Stage 2: Three-step smart transformation (Interception + Optimization + Safety)",
  "template": "You are an AI assistant helping children and youth (ages 6-17) in arts education courses.\n\nYou will perform THREE steps in sequence:\n\n---\n### STEP 1: ARTISTIC TRANSFORMATION\n\n{{INTERCEPTION_CONTEXT}}\n\nTransform this prompt:\n{{INPUT_TEXT}}\n\nFollow the artistic rules/context above. Create a rich, detailed transformation that embodies the artistic attitude.\n\n---\n### STEP 2: MEDIUM-SPECIFIC OPTIMIZATION\n\n{{OPTIMIZATION_INSTRUCTION}}\n\nOptimize the transformed prompt for the target medium. Make it concrete, detailed, and ready for generation.\n\n---\n### STEP 3: SAFETY ASSESSMENT\n\n{{SAFETY_FILTER}}\n\nCheck the optimized prompt for age-appropriate content.\n\n---\n### OUTPUT FORMAT (JSON only, no markdown):\n\n```json\n{\n  \"safe\": true,\n  \"positive_prompt\": \"<final optimized prompt from Step 2>\",\n  \"negative_prompt\": \"<comma-separated terms to avoid, based on safety level>\",\n  \"abort_reason\": \"\"\n}\n```\n\nOR if unsafe:\n\n```json\n{\n  \"safe\": false,\n  \"positive_prompt\": \"\",\n  \"negative_prompt\": \"\",\n  \"abort_reason\": \"<explanation why content is inappropriate>\"\n}\n```\n\nReturn ONLY the JSON object. No other text.",
  "backend_type": "openrouter",
  "model": "STAGE2_MODEL",
  "parameters": {
    "temperature": 0.7,
    "top_p": 0.9,
    "stream": false
  },
  "meta": {
    "chunk_type": "smart_transformation",
    "output_format": "json",
    "estimated_duration": "medium",
    "stage": 2,
    "required_placeholders": [
      "INTERCEPTION_CONTEXT",
      "INPUT_TEXT",
      "OPTIMIZATION_INSTRUCTION",
      "SAFETY_FILTER"
    ]
  }
}
```

#### 2.2 Create Stage 2 Config (or modify existing)

**File:** `devserver/schemas/configs/interception/user_defined.json`

**Update to use smart_transform chunk:**
```json
{
  "pipeline": "text_transformation",
  "chunks": ["smart_transform"],
  ...
}
```

---

### Phase 3: Routes Integration

#### 3.1 Modify schema_pipeline_routes.py

**File:** `devserver/my_app/routes/schema_pipeline_routes.py`

**Changes needed:**

1. **Move media selection to Stage 1:**
   - Frontend sends `media_type` parameter in Stage 1 request
   - After Stage 1 success, frontend shows media choice
   - Stage 2 request includes `output_config` parameter

2. **Build Stage 2 context with mega-prompt placeholders:**

```python
# After Stage 1, before Stage 2
output_config_name = data.get('output_config', 'sd35_large')
output_config = config_loader.get_config(output_config_name)

# Get optimization instruction from output config metadata
optimization_instruction = output_config.meta.get(
    'optimization_instruction',
    'Optimize for the target medium with detailed, concrete descriptions.'
)

# Get safety filter text based on safety level
from config import SAFETY_FILTERS
safety_filter_text = SAFETY_FILTERS.get(safety_level, SAFETY_FILTERS['kids'])

# Build Stage 2 context
stage2_context = {
    'INTERCEPTION_CONTEXT': user_defined_config.context,  # Artistic rules
    'INPUT_TEXT': translated_text,  # From Stage 1
    'OPTIMIZATION_INSTRUCTION': optimization_instruction,  # From output config
    'SAFETY_FILTER': safety_filter_text  # From safety level
}

# Execute Stage 2 (mega-prompt)
result = await pipeline_executor.execute_pipeline(
    config_name='user_defined',  # or whatever interception config
    input_text=translated_text,
    execution_mode='eco',
    safety_level=safety_level,
    tracker=tracker,
    context_override=stage2_context  # Custom context!
)

# Parse JSON response
stage2_output = json.loads(result.final_output)

if not stage2_output['safe']:
    # Abort: unsafe content
    return jsonify({
        'success': False,
        'error': stage2_output['abort_reason']
    })

# SKIP STAGE 3 ENTIRELY!

# Go directly to Stage 4 with optimized prompts
positive_prompt = stage2_output['positive_prompt']
negative_prompt = stage2_output['negative_prompt']
```

3. **Remove Stage 3 calls:**
   - Delete `execute_stage3_safety()` calls
   - Remove Stage 3 loop entirely

---

### Phase 4: Testing Strategy

#### 4.1 Test Cases

**Test 1: Simple prompt (kids safety)**
- Input: "katze auf der matratze"
- Rules: "alles muss grün-rosa-kariert sein!"
- Medium: SD3.5
- Safety: kids
- Expected: Green-pink-checkered cat description, appropriate for children

**Test 2: Edge case (youth safety)**
- Input: "dark cyberpunk street"
- Rules: "film noir style"
- Medium: FLUX
- Safety: youth
- Expected: Noir atmosphere acceptable, no explicit violence

**Test 3: Safety rejection (kids)**
- Input: "scary demon with blood"
- Rules: "horror style"
- Medium: SD3.5
- Safety: kids
- Expected: BLOCKED with appropriate abort_reason

#### 4.2 Performance Benchmarks

**Current (4-stage):**
- Stage 1: ~2s (GPT-OSS:20b)
- Stage 2: ~5s (Claude 4.5)
- Stage 3: ~2s (GPT-OSS:20b)
- Stage 4: ~10s (ComfyUI)
- **Total: ~19s**

**Target (3-stage):**
- Stage 1: ~2s (GPT-OSS:20b)
- Stage 2: ~6s (Claude 4.5 mega-prompt, slightly longer)
- Stage 3: ELIMINATED
- Stage 4: ~10s (ComfyUI)
- **Total: ~18s (5-10% faster, but cleaner!)**

---

## 📂 FILES TO MODIFY

### Create New:
- [ ] `devserver/schemas/chunks/smart_transform.json`

### Modify:
- [ ] `devserver/config.py` (add SAFETY_FILTER_* constants)
- [ ] All output configs in `devserver/schemas/configs/output/*.json` (add optimization_instruction)
- [ ] `devserver/schemas/configs/interception/user_defined.json` (use smart_transform chunk)
- [ ] `devserver/my_app/routes/schema_pipeline_routes.py` (mega-prompt context, remove Stage 3)

### Optional Cleanup:
- [ ] Remove old Stage 3 functions from `devserver/schemas/engine/stage_orchestrator.py`
- [ ] Archive old safety check configs in `devserver/schemas/configs/pre_output/` (or delete)

---

## 🚨 IMPORTANT NOTES

### 1. Frontend Changes Required

**Current flow:**
```
User input → Stage 1 → Stage 2 → Media choice → Stage 3 → Stage 4
```

**New flow:**
```
User input → Stage 1 → Media choice → Stage 2 (with media context) → Stage 4
```

Frontend needs to:
- Show media choice AFTER Stage 1 (not after Stage 2)
- Pass `output_config` parameter to Stage 2 request
- Handle simplified response (no Stage 3 data)

### 2. Backward Compatibility

- Keep old configs as fallback during migration
- Add feature flag if needed: `USE_CONSOLIDATED_FLOW = True`
- Test extensively before removing old code

### 3. Prompt Engineering Quality

The mega-prompt quality is CRITICAL. Test thoroughly:
- Does Claude 4.5 follow all 3 steps correctly?
- Is JSON output consistent?
- Are safety checks effective?
- Is optimization appropriate per medium?

---

## 🔗 RELATED SESSION WORK

**Session 55 Accomplishments:**
- ✅ Replaced execution_mode (eco/fast) with per-stage config variables
- ✅ Created translate_safety.json chunk for Stage 1
- ✅ manipulate.json uses STAGE2_MODEL (Claude 4.5)
- ✅ Fixed USER_INPUT placeholder for user rules
- ✅ Separated Stage 1/2 chunks cleanly

**Session 55 Issues:**
- ⚠️ Stage 3 still uses old override pattern (model_override hardcoded)
- ⚠️ User rules weren't reaching Claude (FIXED: use USER_INPUT placeholder)
- ⚠️ Ollama overload issue (unrelated to our changes)

**🚨 CRITICAL UNRESOLVED ISSUE: Rules Still Not Followed**

**Problem:** Even after fixing USER_INPUT placeholder, test output still ignored "alles muss grün-rosa-kariert sein!" rules.

**Output was:** Generic cat on mattress description (no green, pink, or checkered mentioned)

**Suspected Root Cause:** Back-translation issue
- User rules in German: "alles muss grün-rosa-kariert sein!"
- Stage 1 translates to English for processing
- BUT: Rules might be translated too literally or lose cultural/semantic meaning
- OR: Rules are not being passed through translation properly

**What to check in Session 56:**
1. Does Stage 1 translate BOTH the prompt AND the rules?
2. Are the rules reaching Stage 2 in English or German?
3. Does the translation preserve the imperative/rule nature of the text?
4. Test: Pass rules in English directly to isolate translation issue

**Possible fixes:**
- Don't translate rules (keep them in original language)
- Add explicit instruction: "These are RULES that MUST be followed"
- Use clearer template structure to separate "content" from "constraints"

**This WILL come up again - needs investigation!**

---

## ✅ SESSION 56 SUCCESS CRITERIA

1. [ ] Stage 2 mega-prompt works correctly with all 3 steps
2. [ ] Stage 3 is completely eliminated
3. [ ] Safety filtering effective in Stage 2 final step
4. [ ] Medium-specific optimization produces quality prompts
5. [ ] Performance improved or at least maintained
6. [ ] Tests pass: kids/youth/adult safety levels
7. [ ] "grün-rosa-kariert" example works perfectly end-to-end

---

## 🎯 NEXT SESSION START COMMAND

```bash
cd /home/joerissen/ai/ai4artsed_webserver
git status  # Should be clean
git log -3 --oneline  # Check Session 55 commits
```

**Read first:**
- This handover document
- `docs/ARCHITECTURE PART 01 - 4-Stage Orchestration Flow.md` (will be outdated after refactoring)
- `devserver/config.py` (understand STAGE*_MODEL variables)

**Then start with Phase 1.1:** Add optimization_instruction to output configs

---

**Good luck! This is a big one but will make the system much cleaner. 🚀**
