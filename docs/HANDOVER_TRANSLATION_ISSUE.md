# HANDOVER: Stage 3 Translation Issue - Root Cause Analysis

**Date**: 2025-11-22
**Session**: 62 Part 3 (Continuation)
**Status**: ❌ CRITICAL BUG - Translation NOT working

---

## Executive Summary

**Problem**: German prompts are NOT being translated to English in Stage 3, resulting in German text being sent to SD3.5 for image generation.

**Root Cause**: The `translate` chunk (using model `gpt-OSS:20b`) is **EXPANDING German text instead of translating to English**.

**Impact**:
- SD3.5 receives German prompts instead of English
- Image quality may be affected
- Translation has been broken (user reports it worked 6 months ago)

---

## Detailed Flow Analysis

### Current Architecture (Stage 3 - Pre-Output)

```
Stage 2 Output (German)
    ↓
Stage 3: execute_stage3_safety()
    ↓
    ├─ Step 1: Translation (NEW CODE - Added in this session)
    │   └─ Config: 'pre_output/translation_en'
    │       └─ Chunk: 'translate'
    │           └─ Model: gpt-OSS:20b (STAGE3_MODEL)
    │           └─ Template: "TRANSLATE TO ENGLISH: ..."
    │           └─ ❌ RETURNS GERMAN EXPANDED TEXT
    │
    ├─ Step 2: Safety Check
    │   ├─ Fast-path (95% of requests)
    │   │   └─ Quick regex check (0.4ms)
    │   │   └─ Returns: positive_prompt = translated_prompt
    │   │
    │   └─ Slow-path (5% of requests)
    │       └─ LLM context verification
    │       └─ Returns: positive_prompt = translated_prompt
    │
    └─ Output: safety_result['positive_prompt']
        ↓
Stage 4: Media Generation
    ↓
prompt_for_media = safety_result.get('positive_prompt', ...)
    ↓
SwarmUI/ComfyUI (SD3.5)
```

### Evidence from Testing

**Test Input**: `"Ein Haus steht in einer Landschaft"`

**Test Output** (from direct function call):
```python
{
  'positive_prompt': 'Ein traditionelles Fachwerkhaus mit weißen Gefachen und dunklen Holzbalken erhebt sich inmitten einer sanft gewellten Hügellandschaft...',
  'execution_time': 12.075 seconds  # ← Translation DID execute!
}
```

**Analysis**:
- ✓ Translation WAS executed (12 seconds execution time)
- ✗ Output is GERMAN (not English)
- ✗ Output is EXPANDED (longer description, not translation)

### The Translate Chunk

**Location**: `/devserver/schemas/chunks/translate.json`

**Config**:
```json
{
  "name": "translate",
  "backend_type": "ollama",
  "model": "STAGE3_MODEL",  // → gpt-OSS:20b
  "template": "You are translating text for AI art/media generation.

TRANSLATE TO ENGLISH:
- Translate the text to English
- Preserve artistic intent and emotional tone
...

Text to translate:
{{INPUT_TEXT}}"
}
```

**Problem**: The model `gpt-OSS:20b` is NOT following the "TRANSLATE TO ENGLISH" instruction. Instead, it's treating the German text as a creative prompt and EXPANDING it in German.

---

## Changes Made in This Session

### 1. Modified Files

#### `devserver/schemas/engine/stage_orchestrator.py`
**Change**: Added translation execution BEFORE safety check in `execute_stage3_safety()`

**Before**:
```python
async def execute_stage3_safety(prompt, ...):
    # Fast-path: Quick regex check → return prompt (GERMAN!)
    # Slow-path: Execute text_safety_check_kids (translate + safety)
```

**After** (NEW):
```python
async def execute_stage3_safety(prompt, ...):
    # STEP 1: ALWAYS translate first
    translate_result = await pipeline_executor.execute_pipeline(
        'pre_output/translation_en',
        prompt,
        execution_mode
    )
    translated_prompt = translate_result.final_output

    # STEP 2: Safety check on translated_prompt
    # Fast-path or slow-path → return translated_prompt
```

**Result**: ❌ Translation executes but returns German text

#### `devserver/schemas/engine/pipeline_executor.py`
**Change**: Added chunk output logging

```python
logger.info(f"[CHUNK-OUTPUT] {step.chunk_name}: {output[:200]}...")
```

**Purpose**: Debug logging to trace chunk outputs

#### Created New Configs

- `devserver/schemas/configs/pre_output/safety_only_check_kids.json`
- `devserver/schemas/configs/pre_output/safety_only_check_youth.json`

**Purpose**: Safety check configs WITHOUT translation (to avoid double-translation in slow-path)

### 2. Issues with Changes

**Problem 1**: The translation chunk doesn't actually translate
- The model `gpt-OSS:20b` ignores the "TRANSLATE TO ENGLISH" instruction
- It treats the German prompt as a creative writing task
- It expands the German text instead of translating

**Problem 2**: No logging visibility
- The `[STAGE3-TRANSLATION]` log line should show translation result
- In actual runs, this log line is MISSING
- Suggests the code path may not be executed in production

**Problem 3**: Module reloading
- Backend was restarted multiple times
- Python cache was cleared
- But changes may not have taken effect properly

---

## Historical Context

**User Statement**: "Translation has been working for 6 months"

**Old System** (before changes):
- Stage 3 used `text_safety_check_kids` config
- Config had chunks: `["translate", "safety_check_kids"]`
- Translation ONLY happened in slow-path (5% of requests)
- Fast-path (95%) returned UNTRANSLATED German text

**Hypothesis**: The translation NEVER worked properly for fast-path cases, but the issue went unnoticed because:
1. Slow-path cases (with problematic terms) DID get translated
2. SD3.5 may handle German text reasonably well
3. The issue became visible when explicitly testing with simple German prompts (which trigger fast-path)

---

## The Real Problem

### Why Translation Fails

The `translate` chunk uses `gpt-OSS:20b` (a local Ollama model) which:

1. **Doesn't follow strict instructions well**
   - Template says "TRANSLATE TO ENGLISH"
   - Model interprets this as "expand this creative prompt"

2. **Treats German as valid creative input**
   - German text is valid input for a creative writing task
   - Model expands it artistically rather than translating

3. **No language detection/forcing**
   - No mechanism to FORCE English output
   - No validation that output is actually English

### What SHOULD Happen

```
Input:  "Ein Haus steht in einer Landschaft"
         ↓
translate chunk with proper model/prompt
         ↓
Output: "A house stands in a landscape"
```

### What ACTUALLY Happens

```
Input:  "Ein Haus steht in einer Landschaft"
         ↓
translate chunk with gpt-OSS:20b
         ↓
Model thinks: "Oh, a creative prompt in German! Let me expand it artistically!"
         ↓
Output: "Ein traditionelles Fachwerkhaus mit weißen Gefachen und
         dunklen Holzbalken erhebt sich inmitten einer sanft
         gewellten Hügellandschaft..." (STILL GERMAN, just longer)
```

---

## Solution Options

### Option 1: Fix the Translate Chunk Model
**Change**: Use a better model for translation (e.g., Claude via OpenRouter)

```json
{
  "name": "translate",
  "backend_type": "openrouter",
  "model": "anthropic/claude-sonnet-4.5",
  ...
}
```

**Pros**: Claude follows instructions precisely, will actually translate
**Cons**: Costs money, slower, requires API key

### Option 2: Fix the Translation Prompt
**Change**: Make the prompt more explicit and defensive

```
SYSTEM: You are a translation API. Output ONLY English text, nothing else.

INPUT: {{INPUT_TEXT}}

OUTPUT FORMAT: English translation only, no explanations, no German text.

IMPORTANT:
- If input is German → translate to English
- If input is English → return unchanged
- NEVER output German text
- NEVER add explanations or comments
```

**Pros**: Free, local
**Cons**: May still not work with gpt-OSS:20b

### Option 3: Use Dedicated Translation Model
**Change**: Use a model specifically trained for translation

```json
{
  "name": "translate",
  "backend_type": "ollama",
  "model": "local/llama-translate",  // Or another translation-specific model
  ...
}
```

**Pros**: Purpose-built, reliable
**Cons**: Need to install/test translation model

### Option 4: Remove Translation, Use English Inputs Only
**Change**: Require users to input English prompts, remove translation entirely

**Pros**: Simplest, no translation bugs
**Cons**: Bad UX for German-speaking users (target audience!)

---

## Recommended Fix

**IMMEDIATE**: Option 1 - Use Claude for translation

1. Change `translate.json` to use `openrouter/anthropic/claude-sonnet-4.5`
2. Test with German prompts
3. Verify English output

**File to change**: `/devserver/schemas/chunks/translate.json`

```json
{
  "name": "translate",
  "description": "Translation to English for Stage 3",
  "template": "You are translating text for AI art/media generation.\n\nTRANSLATE TO ENGLISH:\n...",
  "backend_type": "openrouter",  // ← CHANGE THIS
  "model": "anthropic/claude-sonnet-4.5",  // ← CHANGE THIS
  "parameters": {
    "temperature": 0.2,
    "top_p": 0.9,
    "stream": false
  }
}
```

**LONG-TERM**: Find or train a local translation model that works reliably

---

## Testing Checklist

After implementing fix:

- [ ] Test with simple German prompt: "Ein Haus in der Landschaft"
- [ ] Verify `[STAGE3-TRANSLATION]` log shows English output
- [ ] Verify `[STAGE3-TRANSLATED]` log shows English prompt
- [ ] Verify SwarmUI receives English prompt
- [ ] Test with complex German prompt (slow-path trigger)
- [ ] Test with English prompt (should pass through unchanged)
- [ ] Check execution time (should be ~1-2s with Claude)

---

## Files Modified in This Session

```
M  devserver/schemas/engine/stage_orchestrator.py  (✓ Fixed fast-path, but translation still broken)
M  devserver/schemas/engine/pipeline_executor.py  (✓ Added logging)
M  devserver/my_app/routes/schema_pipeline_routes.py  (✓ Already had logging)
A  devserver/schemas/configs/pre_output/safety_only_check_kids.json  (✓ New config)
A  devserver/schemas/configs/pre_output/safety_only_check_youth.json  (✓ New config)
```

---

## Apology and Learnings

**What went wrong**:
1. I assumed the translation chunk itself was working correctly
2. I focused on the FLOW (when translation happens) not the CONTENT (what translation returns)
3. I didn't test the translate chunk in isolation first
4. I made changes without fully understanding the existing system
5. I created complexity (new configs, modified orchestrator) without solving the root issue

**What I learned**:
- ALWAYS test individual components before modifying the flow
- Translation != Text transformation
- Local LLMs may not follow instructions as precisely as needed
- The fast-path was a real issue, but the deeper issue is the translate chunk itself

**Status**: The translate chunk is not being executed. Despite correct configuration:
- ✓ New "translation" pipeline created
- ✓ translate.json changed to use OpenRouter/Claude
- ✓ translation_en.json config uses new pipeline
- ✗ No OpenRouter/Claude logs appear when translate chunk should execute
- ✗ Output equals input (passthrough behavior)

**Next Step**: Use devserver-architecture-expert agent to trace why the translate chunk bypasses LLM execution.

---

## Quick Test Command

```bash
python3 -c "
import sys, asyncio
sys.path.insert(0, '/home/joerissen/ai/ai4artsed_webserver/devserver')
from schemas.engine.pipeline_executor import executor
from pathlib import Path

executor.initialize()

result = asyncio.run(executor.execute_pipeline(
    'pre_output/translation_en',
    'Ein Haus steht in einer Landschaft',
    execution_mode='eco'
))

print('Input:  Ein Haus steht in einer Landschaft')
print('Output:', result.final_output[:200])
print('Is English?', not any(word in result.final_output.lower() for word in ['haus', 'landschaft', 'ein']))
"
```

Expected: `Is English? True`
Actual: `Is English? False`

---

**End of Handover**
