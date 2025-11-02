# Placeholder Redundancy Analysis
**Date:** 2025-10-26
**Purpose:** Understand why TASK/CONTEXT/INSTRUCTION all resolve to same value

---

## The Problem

**User Question (!! Comment 3):**
> "Das ist mir unklar, wieso all diese aliases? Wieso ist 'Task' und 'Context' hier dasselbe??"

**Current Behavior (chunk_builder.py:93-97):**
```python
instruction_text = resolved_config.context or ''

replacement_context = {
    'INSTRUCTION': instruction_text,
    'INSTRUCTIONS': instruction_text,  # Alias
    'TASK': instruction_text,          # Alias
    'CONTEXT': instruction_text,       # Alias
    ...
}
```

**Result:** All four placeholders get the SAME value from `config.context`

---

## Who Uses What?

### Chunk Usage Analysis

| Chunk | Placeholders Used | Template Structure | Users |
|-------|-------------------|-------------------|-------|
| `manipulate.json` | `{{INSTRUCTIONS}}` + `{{CONTEXT}}` | Both on separate lines | 29 configs |
| `translate.json` | `{{INSTRUCTIONS}}` only | Single placeholder | 0 configs (unused?) |
| `prompt_interception.json` | `{{TASK}}` + `{{CONTEXT}}` | "Task:\n{{TASK}}\n\nContext:\n{{CONTEXT}}" | 1 config |
| `prompt_interception_lyrics` | ❌ BROKEN | Invalid structure | 0 |
| `prompt_interception_tags` | ❌ BROKEN | Invalid structure | 0 |

### Config Pipeline Usage

**Pipeline Usage Counts:**
- `simple_manipulation`: **29 configs** (uses `manipulate` chunk)
- `prompt_interception_single`: **1 config** (uses `prompt_interception` chunk)
- `music_generation`: **2 configs**
- `audio_generation`: **2 configs**

**Only config using prompt_interception:**
```bash
$ grep -l "prompt_interception_single" schemas/configs/*.json
schemas/configs/translation_en.json
```

---

## What Happens in Each Chunk?

### 1. manipulate.json Template

**Template:**
```
{{INSTRUCTIONS}}

{{CONTEXT}}

Text to manipulate:

{{PREVIOUS_OUTPUT}}
```

**With current resolver:**
```
[config.context]

[config.context]  ← DUPLICATE!

Text to manipulate:

[previous output]
```

**PROBLEM:** The instruction text appears TWICE because both placeholders resolve to same value!

**Why it "works":**
- LLM sees the instruction twice, probably ignores redundancy
- But wastes tokens and is confusing

---

### 2. prompt_interception.json Template

**Template:**
```
Task:
{{TASK}}

Context:
{{CONTEXT}}

Prompt:
{{INPUT_TEXT}}
```

**With current resolver:**
```
Task:
[config.context]

Context:
[config.context]  ← DUPLICATE AGAIN!

Prompt:
[user input]
```

**PROBLEM:** Again, same text appears twice under different headers!

**Original Intent (probably):**
- `TASK`: Generic instruction ("Transform this prompt...")
- `CONTEXT`: Specific artistic/cultural context ("You are a Dadaist artist...")

**Why it seems to work:**
- The duplicate text has semantic structure internally
- LLM probably ignores the redundant header

---

### 3. translate.json Template

**Template:**
```
{{INSTRUCTIONS}}

Text to translate:

{{INPUT_TEXT}}
```

**With current resolver:**
```
[config.context]

Text to translate:

[user input]
```

**NO PROBLEM HERE:** Only one placeholder, no duplication

**But:** This chunk is UNUSED (0 configs reference it)

---

## Why Was It Done This Way?

### Theory 1: Legacy Compatibility

Looking at the comment in chunk_builder.py:
```python
'TASK': instruction_text,  # For prompt_interception template
```

**Hypothesis:** After removing `instruction_types`, the code mapped everything to `config.context` to maintain compatibility with existing chunks.

**Evidence:**
- All chunks continued to work
- No errors thrown
- System didn't break

**But:** It creates semantic confusion and duplication

---

### Theory 2: Misunderstanding of Placeholder Semantics

**Original Design (probably):**
- `TASK` = What to do (generic operation)
- `CONTEXT` = Domain-specific knowledge/perspective
- `INSTRUCTION` = Complete combined instruction

**After instruction_types removal:**
- Everything merged into `config.context`
- Placeholders became pure aliases
- Semantic distinction lost

---

## What Should It Be?

### Option A: Single Placeholder (Recommended)

**Change all chunks to use ONE placeholder:**
```json
// manipulate.json
{
  "template": "{{INSTRUCTION}}\n\nText to manipulate:\n\n{{PREVIOUS_OUTPUT}}"
}

// translate.json
{
  "template": "{{INSTRUCTION}}\n\nText to translate:\n\n{{INPUT_TEXT}}"
}

// prompt_interception.json
{
  "template": "{{INSTRUCTION}}\n\nPrompt:\n{{INPUT_TEXT}}"
}
```

**Benefits:**
- No duplication
- Clear semantics
- Config.context contains COMPLETE instruction

**Downside:**
- Loses explicit "Task / Context" pedagogical framing in prompt_interception

---

### Option B: Split Config Structure (Breaking Change)

**Add separate fields to Config:**
```json
// Config structure
{
  "task": "Transform this prompt according to the given context",
  "context": "You are an artist working in the spirit of Dadaism...",
  ...
}
```

**chunk_builder.py resolution:**
```python
replacement_context = {
    'TASK': resolved_config.task or '',
    'CONTEXT': resolved_config.context or '',
    'INSTRUCTION': f"{resolved_config.task}\n\n{resolved_config.context}"
}
```

**Benefits:**
- Semantic separation maintained
- Prompt_interception keeps pedagogical structure
- No duplication

**Downside:**
- Breaking change for all 34 configs
- More complex config structure

---

### Option C: Hybrid (Backward Compatible)

**Keep config.context as is, but smart splitting:**

```python
# In chunk_builder.py
def _split_instruction(instruction_text: str) -> tuple:
    """Split instruction into task and context if possible"""
    # Try to detect task/context structure
    if '\n\n' in instruction_text:
        parts = instruction_text.split('\n\n', 1)
        return parts[0], parts[1]
    return instruction_text, ''

task, context = _split_instruction(resolved_config.context)

replacement_context = {
    'TASK': task,
    'CONTEXT': context if context else task,  # Fallback
    'INSTRUCTION': resolved_config.context,
    'INSTRUCTIONS': resolved_config.context
}
```

**Benefits:**
- Backward compatible
- Attempts semantic separation
- No config changes needed

**Downside:**
- Heuristic/fragile
- May misinterpret some instructions

---

## Impact Analysis

### If We Fix manipulate.json (Remove {{CONTEXT}})

**Current:**
```
{{INSTRUCTIONS}}

{{CONTEXT}}

Text to manipulate:
{{PREVIOUS_OUTPUT}}
```

**Proposed:**
```
{{INSTRUCTION}}

Text to manipulate:
{{PREVIOUS_OUTPUT}}
```

**Impact:**
- 29 configs use simple_manipulation pipeline
- All would get cleaner, non-duplicated prompts
- Functionally identical (LLM sees same info once instead of twice)
- **Should improve token efficiency**

**Risk:** NONE - This is purely removing redundancy

---

### If We Fix prompt_interception.json

**Current:**
```
Task:
{{TASK}}

Context:
{{CONTEXT}}

Prompt:
{{INPUT_TEXT}}
```

**Proposed Option A (Simple):**
```
{{INSTRUCTION}}

Prompt:
{{INPUT_TEXT}}
```

**Proposed Option B (Keep structure):**
```
{{INSTRUCTION}}

Prompt:
{{INPUT_TEXT}}
```
(Config.context contains the full "Task + Context" text with structure)

**Impact:**
- Only 1 config uses this (translation_en.json)
- Pedagogical "Task / Context" headers would be lost
- But duplication removed

**Risk:** LOW - Only affects 1 config, easy to adjust

---

## Recommendations

### Immediate (No Breaking Changes)

1. ✅ **Fix manipulate.json**
   ```json
   {
     "template": "{{INSTRUCTION}}\n\nText to manipulate:\n\n{{PREVIOUS_OUTPUT}}"
   }
   ```
   - Removes duplication
   - 29 configs benefit
   - No semantic change

2. ✅ **Fix prompt_interception.json**
   ```json
   {
     "template": "{{INSTRUCTION}}\n\nPrompt:\n{{INPUT_TEXT}}"
   }
   ```
   - Removes duplication
   - 1 config affected (easy to verify)

3. ✅ **Keep only INSTRUCTION and INSTRUCTIONS aliases**
   ```python
   replacement_context = {
       'INSTRUCTION': instruction_text,
       'INSTRUCTIONS': instruction_text,  # Keep for backward compat
       'INPUT_TEXT': ...,
       'PREVIOUS_OUTPUT': ...,
       ...
   }
   ```
   - Remove TASK and CONTEXT aliases (they create confusion)

4. ✅ **Update configs if they rely on structure**
   - Check translation_en.json
   - Ensure config.context has appropriate formatting

---

### Future (If Needed)

**IF semantic Task/Context split is needed:**
- Add optional `task` field to Config schema
- Fall back to `context` if `task` not provided
- Update chunk_builder to use both

**But:** Current system works fine with single `context` field containing complete instruction

---

## Test Plan

1. ✅ **Test with dada.json (uses simple_manipulation)**
   - Before: Instruction appears twice
   - After: Instruction appears once
   - Verify output quality same/better

2. ✅ **Test with translation_en.json (uses prompt_interception_single)**
   - Verify translation still works
   - Check if pedagogical framing still effective

3. ✅ **Run full test suite**
   - Ensure 34 configs still load
   - No errors in chunk building

---

## Conclusion

**Why redundancy exists:**
- Legacy from instruction_types removal
- Quick fix to maintain compatibility
- Never cleaned up

**Why it "works":**
- LLMs ignore redundancy
- Semantic structure in config.context sufficient

**Why it should be fixed:**
- Token waste
- Confusion (your !! comment proves this!)
- Unclear placeholder semantics

**Recommended Action:**
- Fix templates to use single INSTRUCTION placeholder
- Remove TASK/CONTEXT aliases
- Document that config.context = complete instruction

---

**Created:** 2025-10-26
**Status:** Analysis complete
**Next:** Implement fixes (await user approval)
