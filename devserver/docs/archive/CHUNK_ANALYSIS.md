# Chunk Structure Analysis
**Date:** 2025-10-26
**Purpose:** Analyze inconsistencies in chunk architecture (!! Comment 1)

---

## Problem Statement

**User Question (!! Comment 1):**
> "Was ist der genaue Unterschied zwischen 'manipulate' und 'prompt_interception'? Das sollten doch die Configs regeln, ob es um Lyrik oder anderes geht? Gibt es einen Unterschied zwischen 'manipulate' und 'translate'?"

---

## Current Chunk Inventory

### Working Chunks (Proper Structure)

#### 1. manipulate.json ✅
```json
{
  "name": "manipulate",
  "template": "{{INSTRUCTIONS}}\n\n{{CONTEXT}}\n\nText to manipulate:\n\n{{PREVIOUS_OUTPUT}}",
  "backend_type": "ollama",
  "model": "gemma2:9b",
  "parameters": {"temperature": 0.7},
  "meta": {"chunk_type": "manipulation"}
}
```
**Purpose:** Text transformation with instructions
**Input:** Uses `{{PREVIOUS_OUTPUT}}` (for chaining)
**Observation:** Has both `{{INSTRUCTIONS}}` AND `{{CONTEXT}}` - redundant?

---

#### 2. translate.json ✅
```json
{
  "name": "translate",
  "template": "{{INSTRUCTIONS}}\n\nText to translate:\n\n{{INPUT_TEXT}}",
  "backend_type": "ollama",
  "model": "gemma2:9b",
  "parameters": {"temperature": 0.1},
  "meta": {"chunk_type": "translation"}
}
```
**Purpose:** Translation
**Input:** Uses `{{INPUT_TEXT}}` (for first-in-pipeline)
**Observation:** Only uses `{{INSTRUCTIONS}}`, no `{{CONTEXT}}`
**Question:** Is this functionally different from `manipulate` with translation context?

---

#### 3. prompt_interception.json ✅
```json
{
  "name": "prompt_interception",
  "template": "Task:\n{{TASK}}\n\nContext:\n{{CONTEXT}}\n\nPrompt:\n{{INPUT_TEXT}}",
  "backend_type": "ollama",
  "model": "gemma2:9b",
  "parameters": {"temperature": 0.7},
  "meta": {
    "chunk_type": "prompt_interception",
    "universal_interface": true
  }
}
```
**Purpose:** Universal prompt transformation with explicit Task/Context/Prompt structure
**Input:** Uses `{{INPUT_TEXT}}`
**Observation:** Uses BOTH `{{TASK}}` AND `{{CONTEXT}}` as separate sections
**Question:** What's the semantic difference between TASK and CONTEXT?

---

### BROKEN Chunks (Invalid Structure)

#### 4. prompt_interception_lyrics.json ❌
```json
{
  "backend_type": "ollama",
  "model": "{{MODEL}}",  // ❌ Placeholder, not actual value!
  "parameters": {
    "temperature": "{{TEMPERATURE}}",  // ❌ String, should be number
    "max_tokens": "{{MAX_TOKENS}}"
  },
  "task": "{{TASK}}",  // ❌ Not a template field
  "context": "{{CONTEXT}}",  // ❌ Not a template field
  "placeholders": {...}  // ❌ Invalid structure
}
```
**Status:** ❌ BROKEN - Not a valid chunk template
**Problem:** This is a meta-template or placeholder file, not an executable chunk
**Expected:** Should have same structure as other chunks with concrete template string

---

#### 5. prompt_interception_tags.json ❌
**Status:** ❌ BROKEN - Identical to lyrics, same problems

---

### ComfyUI Chunks

#### 6. comfyui_image_generation.json
**Status:** ⚠️ Not analyzed yet (ComfyUI integration)

#### 7. comfyui_audio_generation.json
**Status:** ⚠️ Not analyzed yet (ComfyUI integration)

---

## Functional Analysis

### Question 1: manipulate vs translate

**Current Difference:**
- `manipulate`: Uses `{{PREVIOUS_OUTPUT}}` (chaining), temp=0.7
- `translate`: Uses `{{INPUT_TEXT}}` (first step), temp=0.1

**Semantic Difference:**
- `translate`: Lower temperature for accuracy
- `manipulate`: Higher temperature for creativity

**User's Point:**
> "Ist 'translate' nicht einfach ein 'manipulate' mit Kontext 'Übersetze in Sprache / En ...'?"

**ANSWER:** YES! Translation is functionally a manipulation with specific instruction context.

**Recommendation:**
- Keep `translate` for semantic clarity
- Add `task_type` metadata to distinguish them
- OR: Merge into single `transform` chunk with task_type parameter

---

### Question 2: manipulate vs prompt_interception

**Current Difference:**
- `manipulate`: Generic instruction + context format
- `prompt_interception`: Explicit "Task / Context / Prompt" structure

**Semantic Difference:**
- `prompt_interception`: Original pedagogical concept - explicit structure shows LLM what it's doing
- `manipulate`: Generic transformation without pedagogical framing

**User's Point:**
> "Das sollten doch die Configs regeln ob es um Lyrik oder anderes geht?"

**ANSWER:** YES! The content (Dadaism, Youth Slang, Lyrics) belongs in Config.context, NOT in separate chunks.

**Current Problem:**
We have `prompt_interception_lyrics` and `prompt_interception_tags` as separate chunks.
These should just be configs that reference the generic `prompt_interception` chunk!

**Recommendation:**
- Keep ONE `prompt_interception` chunk
- Delete `prompt_interception_lyrics` and `prompt_interception_tags`
- Create configs that use `prompt_interception` with appropriate context

---

### Question 3: TASK vs CONTEXT vs INSTRUCTION

**Current Usage:**
- `prompt_interception`: Uses `{{TASK}}` and `{{CONTEXT}}` as SEPARATE placeholders
- `manipulate`: Uses `{{INSTRUCTIONS}}` and `{{CONTEXT}}` (redundant?)
- `translate`: Uses only `{{INSTRUCTIONS}}`

**chunk_builder.py Resolution:**
```python
replacement_context = {
    'INSTRUCTION': instruction_text,
    'INSTRUCTIONS': instruction_text,  # Alias
    'TASK': instruction_text,          # Alias
    'CONTEXT': instruction_text,       # Alias
    ...
}
```

**PROBLEM FOUND:** All four placeholders resolve to the SAME value (config.context)!

**User's Question (!! Comment 3):**
> "Wieso ist 'Task' und 'Context' hier dasselbe??"

**ANSWER:** It's a mistake! In `prompt_interception.json`, TASK and CONTEXT should be distinct:
- `TASK`: "Transform this prompt according to..."
- `CONTEXT`: "You are an artist working in Dadaism..." (the actual artistic/cultural context)

**Recommendation:**
1. `config.context` should be the COMPLETE instruction (Task + Context merged)
2. OR: Split config into `task` and `context` fields (breaking change)
3. OR: Keep as-is but fix template to not use both

---

## Architectural Recommendations

### Option A: Minimal Chunks (Recommended)

**Keep only 3 core chunks:**
1. `transform` (merges manipulate + translate + prompt_interception)
   - Template: Configurable via chunk parameter
   - Uses: `{{INSTRUCTION}}` + `{{INPUT_TEXT}}` or `{{PREVIOUS_OUTPUT}}`
   - Metadata: `task_type` (translation, manipulation, interception)

2. `comfyui_image_generation`
3. `comfyui_audio_generation`

**Benefits:**
- Maximum flexibility
- No redundancy
- Configs control ALL content
- Chunks are truly primitive operations

**Downside:**
- Loses explicit pedagogical framing of prompt_interception

---

### Option B: Keep Semantic Chunks

**Keep current working chunks:**
1. `manipulate` - Generic transformation
2. `translate` - Translation-specific (low temp)
3. `prompt_interception` - Pedagogical explicit structure
4. `comfyui_*` - Media generation

**Fix:**
- Delete `prompt_interception_lyrics` and `prompt_interception_tags`
- Fix placeholder resolution (TASK ≠ CONTEXT semantically)
- Add `task_type` metadata to all chunks

**Benefits:**
- Semantic clarity
- Preserves pedagogical concept
- Easier to understand

**Downside:**
- Some functional overlap remains

---

### Option C: Task-Type Based Chunks

**Restructure around task types from model_selector.py:**
1. `transform.json` - General transformation (task_type: standard/advanced)
2. `translate.json` - Translation (task_type: translation)
3. `analyze.json` - Analysis tasks (task_type: vision/data_extraction)
4. `comfyui_*` - Media generation

**Each chunk declares:**
```json
{
  "name": "transform",
  "task_type": "standard",  // Links to model_selector task categories
  "model": "task:standard",  // Uses task-based model selection
  ...
}
```

**Benefits:**
- Clean integration with LLM selection system
- Clear functional boundaries
- Scalable

---

## Immediate Issues to Fix

### 1. CRITICAL: Delete or Fix Broken Chunks
- `prompt_interception_lyrics.json` ❌ Invalid structure
- `prompt_interception_tags.json` ❌ Invalid structure

**Action:** Delete these files, replace with configs that use `prompt_interception`

---

### 2. HIGH: Fix Placeholder Ambiguity
- `{{TASK}}` and `{{CONTEXT}}` should NOT resolve to same value
- Either merge them into one, or split config structure

**Action:** Decide on placeholder semantics and document

---

### 3. MEDIUM: Add task_type Metadata
All chunks need `task_type` in metadata for LLM selection

**Action:** Add to all chunk JSON files

---

## Next Steps

1. **User Decision Required:**
   - Option A (minimal chunks)?
   - Option B (semantic chunks)?
   - Option C (task-type chunks)?

2. **Fix Broken Chunks:**
   - Delete/rewrite prompt_interception_lyrics and _tags

3. **Implement task_type System:**
   - Add metadata to chunks
   - Integrate with model_selector

4. **Update Documentation:**
   - Clarify chunk semantics
   - Document placeholder usage

---

**Created:** 2025-10-26
**Status:** Analysis complete, awaiting user decision
**Next:** User chooses architectural direction
