# Session 69: Surrealization Model Selection Issue - Handover

**Date**: 2025-11-24
**Status**: RESEARCH COMPLETED - NO FIXES APPLIED
**Critical**: Image generation fails with "Unbekanntes Modell-Format: task:advanced"

---

## Executive Summary

The **surrealization pipeline** fails at Stage 4 because chunks use **deprecated model selection syntax** (`task:advanced`) that was removed in **Session 55**. The system now uses **static model variables from config.py** instead of dynamic task-based selection.

---

## Problems Discovered

### 1. **Primary Issue**: Deprecated Model Selection in Surrealization Chunks

**Error Log**:
```
2025-11-24 18:07:53,206 - ERROR - Step step_1_optimize_t5_prompt failed:
Backend error: Unbekanntes Modell-Format: task:advanced
```

**Root Cause**:
- `devserver/schemas/chunks/optimize_t5_prompt.json` uses `"model": "task:advanced"`
- `devserver/schemas/chunks/optimize_clip_prompt.json` uses `"model": "task:fast"`
- Both are **deprecated** formats from pre-Session-55

**Current System (Session 55+)**:
- Models defined as **variables in `devserver/config.py`**
- Chunks reference variables like `"model": "STAGE2_OPTIMIZATION_MODEL"`
- `chunk_builder.py` (lines 180-182) loads these via `getattr(config, base_model)`

**Evidence**:
```python
# devserver/config.py (line 83)
# Chunks reference these variables by name (e.g., "model": "STAGE2_MODEL")

# Git history:
ba6e8bd refactor: Deprecate execution_mode parameter (Session 55)
ab77d8c refactor: Phase 4a - Remove execution_mode from chunk_builder
61c029a refactor: Replace execution_mode with per-stage model config
```

### 2. **Secondary Issue**: Frontend Duplicate Declarations in direct.vue

**File**: `public/ai4artsed-frontend/src/views/direct.vue`
**Lines**: 251-252 AND 354-355

```typescript
// Line 251-252
const pipelineStore = usePipelineExecutionStore()
const route = useRoute()

// Line 354-355 (DUPLICATE!)
const route = useRoute()
const pipelineStore = usePipelineExecutionStore()
```

**Impact**: TypeScript will fail with duplicate const declarations

**Origin**: Previous session restored variables but forgot to remove duplicates

### 3. **Confusion**: Multiple "task" Concepts

Three **different** "task" concepts exist:

| Concept | Location | Status | Purpose |
|---------|----------|--------|---------|
| `"task_type"` field | Chunk JSONs | **UNUSED** | Metadata only, never read by code |
| `"model": "task:*"` | Chunk JSONs | **DEPRECATED** | Old dynamic selection (Session 55-) |
| `task_categories` | `model_selector.py` | **DEPRECATED** | Supported old system, now unused |

**Valid task categories** (if system were active):
- `security`, `vision`, `translation`, `standard`, `advanced`, `data_extraction`
- **NOT** `fast` (doesn't exist!)

---

## What Was Changed (Then Reverted)

### Initial Incorrect Approach
1. ✗ Added `execution_mode` parameter to `chunk_builder.build_chunk()`
2. ✗ Added ModelSelector to resolve `task:advanced` dynamically
3. ✗ Changed `task:fast` → `task:standard`
4. ✗ Removed duplicate declarations in `direct.vue`

### Why This Was Wrong
- Reintroduced **deprecated Session 55 system**
- Ignored new **config.py-based** model selection
- Would break architectural consistency

### Files Modified Then Reverted
- `devserver/schemas/engine/pipeline_executor.py`
- `devserver/schemas/engine/chunk_builder.py`
- `devserver/schemas/chunks/optimize_clip_prompt.json`
- `public/ai4artsed-frontend/src/views/direct.vue`

**Current Status**: All changes reverted, back to broken state

---

## Correct Solution

### Fix 1: Migrate Surrealization Chunks to Config.py Model Variables

**File**: `devserver/schemas/chunks/optimize_t5_prompt.json`
```diff
- "model": "task:advanced",
+ "model": "REMOTE_ADVANCED_MODEL",
```

**File**: `devserver/schemas/chunks/optimize_clip_prompt.json`
```diff
- "model": "task:fast",
+ "model": "STAGE2_OPTIMIZATION_MODEL",
```

**Rationale**:
- `REMOTE_ADVANCED_MODEL` = `"openrouter/anthropic/claude-sonnet-4.5"` (config.py line 93)
- `STAGE2_OPTIMIZATION_MODEL` = `REMOTE_FAST_MODEL` (config.py line 100)
- Both have proper `openrouter/` prefix, work with existing system

**Alternative Variables from config.py**:
```python
# Line 87-94: Available model variables
LOCAL_DEFAULT_MODEL = "gpt-OSS:20b"
REMOTE_FAST_MODEL = "openrouter/anthropic/claude-haiku-4.5"
REMOTE_ADVANCED_MODEL = "openrouter/anthropic/claude-sonnet-4.5"
REMOTE_EXTREME_MODEL = "openrouter/anthropic/claude-opus-4.1"

# Line 97-101: Stage-specific assignments
STAGE2_INTERCEPTION_MODEL = REMOTE_FAST_MODEL
STAGE2_OPTIMIZATION_MODEL = REMOTE_FAST_MODEL
```

### Fix 2: Remove Duplicate Declarations in direct.vue

**File**: `public/ai4artsed-frontend/src/views/direct.vue`
**Action**: Delete lines 354-355

```diff
  const areModelBubblesEnabled = computed(() => {
    return interceptionResult.value.trim().length > 0
  })

- // ============================================================================
- // Route handling & Store
- // ============================================================================
-
- const route = useRoute()
- const pipelineStore = usePipelineExecutionStore()
-
  // ============================================================================
  // Lifecycle
  // ============================================================================
```

**Rationale**: Already declared at lines 251-252

### Optional Cleanup: Remove Unused "task_type" Fields

**Files**: All chunks with `"task_type"` field
**Action**: Remove field entirely (it's never read)

```diff
  {
    "name": "optimize_t5_prompt",
    "type": "processing_chunk",
    "backend_type": "ollama",
-   "task_type": "advanced",
    "description": "...",
    "model": "REMOTE_ADVANCED_MODEL",
```

**Rationale**: Code never reads this field, pure metadata

---

## Testing Plan

### Test 1: Surrealization Pipeline
1. Start devserver + frontend
2. Navigate to `/direct` route
3. Enter test prompt: "Ein Haus in einer Landschaft"
4. Click "Start" → wait for T5/CLIP prompts
5. Click "Bild mit Dual-Encoder erstellen"
6. **Expected**: Image generates successfully
7. **Check logs**: Should show `[BACKEND] Using model: openrouter/anthropic/...`

### Test 2: Frontend No Errors
1. Run `npm run type-check` in frontend
2. **Expected**: No TypeScript errors about duplicate declarations

### Test 3: Other Pipelines Unaffected
1. Test standard interception pipeline (e.g., overdrive)
2. **Expected**: Works normally, uses correct models from config.py

---

## Architecture Notes

### Model Selection Flow (Session 55+)

```
┌─────────────────────────────────────────────────────┐
│ 1. Chunk JSON defines model variable name          │
│    "model": "STAGE2_OPTIMIZATION_MODEL"            │
└────────────────┬────────────────────────────────────┘
                 │
                 v
┌─────────────────────────────────────────────────────┐
│ 2. chunk_builder.py checks if it's a config var    │
│    if hasattr(config, base_model):                 │
│        final_model = getattr(config, base_model)   │
└────────────────┬────────────────────────────────────┘
                 │
                 v
┌─────────────────────────────────────────────────────┐
│ 3. Load value from devserver/config.py             │
│    STAGE2_OPTIMIZATION_MODEL = REMOTE_FAST_MODEL   │
│    = "openrouter/anthropic/claude-haiku-4.5"       │
└────────────────┬────────────────────────────────────┘
                 │
                 v
┌─────────────────────────────────────────────────────┐
│ 4. backend_router detects prefix                   │
│    "openrouter/" → route to OpenRouter backend     │
└────────────────┬────────────────────────────────────┘
                 │
                 v
┌─────────────────────────────────────────────────────┐
│ 5. prompt_interception_engine.py executes          │
│    Validates openrouter/ or local/ prefix          │
└─────────────────────────────────────────────────────┘
```

### Why Session 55 Deprecated execution_mode

**Old System** (Pre-Session 55):
- Chunks had `"model": "task:advanced"`
- `execution_mode` parameter (`eco` or `fast`) passed through pipeline
- ModelSelector dynamically resolved: `task:advanced` + `eco` → `local/mistral-small:24b`

**Problems**:
- Complex dynamic resolution at runtime
- Hard to reason about which model actually runs
- execution_mode had to be threaded through entire pipeline

**New System** (Session 55+):
- All models statically defined in `config.py`
- Change models by editing **one file** (config.py)
- Clear, explicit model assignments per stage
- No runtime resolution needed

**Evidence**:
```python
# devserver/schemas/engine/pipeline_executor.py (line 100)
execution_mode: str = 'eco',  # DEPRECATED (Session 55): Ignored. Model selection via config.py
```

---

## Related Files

### Core Files
- `devserver/config.py` - Model variable definitions
- `devserver/schemas/engine/chunk_builder.py` - Loads models from config (lines 180-186)
- `devserver/schemas/engine/prompt_interception_engine.py` - Validates model format (line 103-110)
- `devserver/schemas/engine/backend_router.py` - Routes based on model prefix

### Surrealization Files
- `devserver/schemas/pipelines/dual_encoder_fusion.json` - Pipeline definition
- `devserver/schemas/chunks/optimize_t5_prompt.json` - **NEEDS FIX**
- `devserver/schemas/chunks/optimize_clip_prompt.json` - **NEEDS FIX**
- `devserver/schemas/chunks/dual_encoder_fusion_image.json` - ComfyUI output chunk
- `devserver/schemas/configs/output/surrealization_output.json` - Output config

### Frontend
- `public/ai4artsed-frontend/src/views/direct.vue` - **NEEDS FIX** (duplicates)

---

## Critical Rules for Next Session

1. **COMMIT BEFORE STARTING** - User explicitly requires this
2. **NO WORKAROUNDS** - Fix root problems, not symptoms
3. **DON'T REINTRODUCE DEPRECATED SYSTEMS** - Respect Session 55 architecture
4. **TEST WITH LOGS** - Verify model names in backend logs
5. **CHECK OTHER CHUNKS** - Ensure no other chunks use `task:*` format

---

## Questions for User

Before implementing fixes:

1. Should T5 optimization use `REMOTE_ADVANCED_MODEL` (Sonnet 4.5) or `REMOTE_FAST_MODEL` (Haiku 4.5)?
   - Advanced = better quality, higher cost
   - Fast = faster, cheaper

2. Should CLIP optimization use same model as T5 or can be different?

3. Should unused `"task_type"` metadata fields be removed for cleaner schemas?

---

## Git State

**Branch**: develop
**Uncommitted Changes**:
- `src/views/direct.vue` - Modified (duplicate declarations)
- `docs/SESSION_GPT5_CONTINUATION_HANDOVER.md` - Untracked

**Important**: Create commit of current broken state BEFORE applying fixes, so fixes can be cleanly reverted if needed.

---

## Next Session Checklist

- [ ] User confirms choice of models (Advanced vs Fast)
- [ ] Create commit of current state
- [ ] Fix `optimize_t5_prompt.json` model
- [ ] Fix `optimize_clip_prompt.json` model
- [ ] Remove duplicates in `direct.vue`
- [ ] Run `npm run type-check` (frontend)
- [ ] Test surrealization pipeline end-to-end
- [ ] Check logs for correct model usage
- [ ] Search codebase for other `task:*` usage
- [ ] Commit fixes with clear message
- [ ] Update DEVELOPMENT_LOG.md

---

**Session Status**: Research complete, ready for implementation
