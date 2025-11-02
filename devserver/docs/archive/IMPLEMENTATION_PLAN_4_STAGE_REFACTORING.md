# Implementation Plan: 4-Stage Architecture Refactoring

**Date:** 2025-11-01
**Status:** Planning Phase
**Goal:** Refactor from "Stage 1-3 in PipelineExecutor" to "Stage 1-3 in DevServer Orchestrator"

---

## Executive Summary

**Problem:**
- Stage 1-3 logic embedded in `pipeline_executor.py` (lines 308-499)
- Causes redundant translation/safety when AUTO-MEDIA calls output configs
- Breaks architectural principle: PipelineExecutor should be DUMB, DevServer should be SMART

**Solution:**
- Move Stage 1-3 logic from `pipeline_executor.py` to `schema_pipeline_routes.py`
- PipelineExecutor becomes dumb engine (just executes chunks)
- DevServer orchestrates all 4 stages with non-redundant safety rules

**Strategy:**
- Incremental refactoring with feature flag (NOT big bang)
- Test at each step
- Rollback-able

---

## Part I: Big Picture Architecture

### Current (WRONG) Architecture

```
User Request
    ↓
schema_pipeline_routes.py
    ↓
    execute_pipeline(config='overdrive')
        ↓
        pipeline_executor.py execute_pipeline()
        ├─ Stage 1: Translation + Safety (EMBEDDED)
        ├─ Stage 2: Execute chunks
        └─ Stage 3: Pre-output safety (EMBEDDED)
            ↓
            Returns result with media_output
    ↓
AUTO-MEDIA: execute_pipeline(config='gpt5_image')
    ↓
    pipeline_executor.py execute_pipeline()
    ├─ Stage 1: Translation + Safety (REDUNDANT!)
    ├─ Stage 2: Execute chunks
    └─ Stage 3: Pre-output safety (REDUNDANT!)
        ↓
        Returns image

❌ Stage 1-3 run TWICE (once for overdrive, once for gpt5_image)
```

### Target (CORRECT) Architecture

```
User Request
    ↓
schema_pipeline_routes.py (SMART ORCHESTRATOR)
    ↓
    [Stage 1: Pre-Interception]
    │   Read: overdrive.pipeline.input_requirements = {texts: 1}
    │   → execute_pipeline('translation', text)        [DUMB]
    │   → run_hybrid_safety_check(text, 'stage1')     [DUMB]
    ↓
    [Stage 2: Interception]
    │   → execute_pipeline('overdrive', prepared_text) [DUMB]
    │   Returns: {
    │     final_output: "transformed text",
    │     output_requests: [{type: "image", prompt: "..."}]
    │   }
    ↓
    [Stage 3-4: For EACH output request]
    │   FOR request in output_requests:
    │       [Stage 3: Pre-Output Safety]
    │       → run_hybrid_safety_check(request.prompt, 'kids') [DUMB]
    │
    │       [Stage 4: Media Generation]
    │       → execute_pipeline('gpt5_image', request.prompt)  [DUMB]
    │       Returns: prompt_id
    ↓
    Return: {
        final_output: "transformed text",
        media_output: [{type: "image", prompt_id: "abc123"}]
    }

✅ Stage 1-3 run ONCE (no redundant calls)
✅ PipelineExecutor is DUMB (just executes chunks)
✅ DevServer is SMART (orchestrates flow)
```

---

## Part II: Implementation Strategy

### Strategy: Incremental Refactoring (SAFE)

**NOT Big Bang:**
- ❌ Delete 400 lines from pipeline_executor.py → Everything breaks
- ❌ Rewrite schema_pipeline_routes.py → Untested, risky

**YES Incremental:**
- ✅ Build new path parallel to old
- ✅ Feature flag to toggle between old/new
- ✅ Test thoroughly before switching
- ✅ Rollback if issues

### Feature Flag Approach

```python
# config.py or schema_pipeline_routes.py
USE_NEW_4_STAGE_ARCHITECTURE = False  # Start with False

# In schema_pipeline_routes.py
if USE_NEW_4_STAGE_ARCHITECTURE:
    result = await execute_4_stage_flow(...)  # New path
else:
    result = await pipeline_executor.execute_pipeline(...)  # Old path
```

**Testing Phases:**
1. Implement new path, flag=False (old path runs)
2. Test new path with flag=True (compare results)
3. If tests pass, set flag=True permanently
4. Remove old code from pipeline_executor.py

---

## Part III: Detailed Implementation Steps

### Phase 1: Preparation (No Code Changes Yet)

**Step 1.1: Add input_requirements to pipelines**

**Files to modify:**
- `schemas/pipelines/text_transformation.json`
- `schemas/pipelines/single_prompt_generation.json`
- `schemas/pipelines/dual_prompt_generation.json`

**Example:**
```json
// text_transformation.json
{
  "name": "text_transformation",
  "input_requirements": {
    "texts": 1
  },
  "chunks": ["manipulate"]
}
```

**Test:** ConfigLoader reads input_requirements correctly

**Step 1.2: Add output_config flag to output configs**

**Files to modify:**
- `schemas/configs/gpt5_image.json`
- `schemas/configs/sd35_large.json`
- (any other output configs)

**Example:**
```json
// gpt5_image.json
{
  "meta": {
    "output_config": true,  // NEW FLAG
    "skip_pre_stages": true  // NEW FLAG
    // ... existing meta ...
  }
}
```

**Test:** ConfigLoader reads flags correctly

---

### Phase 2: Extract Helper Functions

**Step 2.1: Extract Stage 1 logic into standalone functions**

**Create new file:** `schemas/engine/stage_orchestrator.py`

**Functions to extract:**
```python
async def execute_stage1_translation(text: str, execution_mode: str) -> str:
    """
    Execute Stage 1a: Translation
    DUMB: Just calls translation pipeline, returns result
    """
    result = await pipeline_executor.execute_pipeline(
        'pre_interception/correction_translation_de_en',
        text,
        execution_mode=execution_mode,
        skip_stages=True  # NEW: Don't run Stage 1-3 inside
    )
    return result.final_output

async def execute_stage1_safety(text: str, execution_mode: str) -> tuple[bool, list]:
    """
    Execute Stage 1b: Hybrid Safety Check
    Returns: (is_safe, error_codes)
    """
    # Hybrid approach
    has_terms, found_terms = fast_filter_check(text, 'stage1')

    if not has_terms:
        return (True, [])

    # LLM verification
    result = await pipeline_executor.execute_pipeline(
        'pre_interception/safety_llamaguard',
        text,
        execution_mode=execution_mode,
        skip_stages=True
    )

    is_safe, codes = parse_llamaguard_output(result.final_output)
    return (is_safe, codes)

async def execute_stage3_safety(prompt: str, safety_level: str, execution_mode: str) -> dict:
    """
    Execute Stage 3: Pre-Output Safety Check
    Returns: {safe, abort_reason, positive_prompt, negative_prompt}
    """
    # Hybrid approach
    has_terms, found_terms = fast_filter_check(prompt, safety_level)

    if not has_terms:
        return {"safe": True, "method": "fast_filter"}

    # LLM verification
    safety_config = f"text_safety_check_{safety_level}"
    result = await pipeline_executor.execute_pipeline(
        safety_config,
        prompt,
        execution_mode=execution_mode,
        skip_stages=True
    )

    return parse_preoutput_json(result.final_output)
```

**Test:** Each helper function works independently

---

### Phase 3: Implement New Orchestrator

**Step 3.1: Create execute_4_stage_flow() in schema_pipeline_routes.py**

```python
async def execute_4_stage_flow(
    config_name: str,
    input_text: str,
    execution_mode: str = 'eco',
    safety_level: str = 'kids'
):
    """
    NEW: 4-Stage orchestration (DevServer as smart orchestrator)

    Returns same structure as old execute_pipeline() for compatibility
    """

    # Load config
    config = config_loader.get_config(config_name)
    pipeline = config_loader.get_pipeline(config.pipeline_name)

    # Check if this is an output config (skip Stage 1-3)
    is_output_config = config.meta.get('output_config', False)

    if is_output_config:
        # Output configs skip Stage 1-3 (already done by main pipeline)
        result = await pipeline_executor.execute_pipeline(
            config_name,
            input_text,
            execution_mode=execution_mode,
            skip_stages=True  # NEW FLAG
        )
        return result

    # ================================================================
    # STAGE 1: Pre-Interception
    # ================================================================
    input_requirements = pipeline.get('input_requirements', {'texts': 1})
    num_texts = input_requirements.get('texts', 1)

    prepared_texts = []
    for i in range(num_texts):
        text = input_text if i == 0 else None  # TODO: Multi-input support

        # Stage 1a: Translation
        translated = await execute_stage1_translation(text, execution_mode)

        # Stage 1b: Safety
        is_safe, codes = await execute_stage1_safety(translated, execution_mode)
        if not is_safe:
            error_msg = build_safety_message(codes, lang='de')
            return PipelineResult(
                config_name=config_name,
                status=PipelineStatus.FAILED,
                error=error_msg,
                metadata={"safety_codes": codes, "stage": "pre_interception"}
            )

        prepared_texts.append(translated)

    # ================================================================
    # STAGE 2: Interception (Main Pipeline)
    # ================================================================
    result = await pipeline_executor.execute_pipeline(
        config_name,
        prepared_texts[0],  # TODO: Multi-input support
        execution_mode=execution_mode,
        skip_stages=True  # NEW: Don't run Stage 1-3 inside
    )

    if not result.success:
        return result

    # ================================================================
    # STAGE 3-4: For EACH output request
    # ================================================================

    # Check if config requests media output
    media_preferences = config.media_preferences
    default_output = media_preferences.get('default_output') if media_preferences else None

    if not default_output or default_output == 'text':
        # Text-only, no Stage 3-4
        return result

    # Build output request from config
    output_request = {
        "type": default_output,
        "prompt": result.final_output,
        "params": {}
    }

    # Stage 3: Pre-Output Safety
    stage3_result = await execute_stage3_safety(
        output_request['prompt'],
        safety_level,
        execution_mode
    )

    if not stage3_result['safe']:
        # Blocked: Return text alternative
        error_msg = f"🛡️ Sicherheitsfilter ({safety_level.upper()}):\n\n{stage3_result['abort_reason']}"
        result.final_output += f"\n\n---\n\n{error_msg}"
        result.metadata['stage_3_blocked'] = True
        return result

    # Stage 4: Media Generation
    output_config_name = lookup_output_config(default_output, execution_mode)

    output_result = await pipeline_executor.execute_pipeline(
        output_config_name,
        stage3_result.get('positive_prompt', output_request['prompt']),
        execution_mode=execution_mode,
        skip_stages=True  # IMPORTANT: Don't run Stage 1-3 again!
    )

    # Attach media output to result
    result.metadata['media_output'] = {
        'type': default_output,
        'prompt_id': output_result.final_output,
        'config': output_config_name
    }

    return result
```

**Test:** New flow works with feature flag

---

### Phase 4: Update PipelineExecutor

**Step 4.1: Add skip_stages parameter**

```python
# pipeline_executor.py

async def execute_pipeline(
    self,
    config_name: str,
    input_text: str,
    user_input: str = None,
    execution_mode: str = 'eco',
    safety_level: str = 'kids',
    skip_stages: bool = False  # NEW PARAMETER
):
    """
    Execute pipeline with optional stage skipping

    When skip_stages=True:
    - Skip Stage 1 (translation + safety)
    - Skip Stage 3 (pre-output safety)
    - Just execute chunks (DUMB mode)
    """

    # Load config
    config = self.config_loader.get_config(config_name)

    # Check if we should skip stages
    is_system_pipeline = config.meta.get('system_pipeline', False)
    is_output_config = config.meta.get('output_config', False)

    should_skip_stages = skip_stages or is_system_pipeline or is_output_config

    if should_skip_stages:
        # DUMB MODE: Just execute chunks
        logger.info(f"[DUMB-MODE] Executing {config_name} without Stage 1-3")
        context = PipelineContext(input_text=input_text, user_input=user_input)
        steps = self._plan_pipeline_steps(config)
        result = await self._execute_pipeline_steps(config_name, steps, context, execution_mode)
        return result

    # OLD PATH: Stage 1-3 logic (will be removed after migration)
    # Lines 308-499 stay here for now
    # ...
```

**Test:** skip_stages=True bypasses Stage 1-3

---

### Phase 5: Enable Feature Flag & Test

**Step 5.1: Set feature flag to True**

```python
# schema_pipeline_routes.py
USE_NEW_4_STAGE_ARCHITECTURE = True  # ENABLE NEW PATH
```

**Step 5.2: Comprehensive testing**

**Test Cases:**
1. Simple flow: overdrive → gpt5_image (eco)
2. Simple flow: overdrive → gpt5_image (fast)
3. Text-only: overdrive (no image)
4. Unsafe input: Stage 1 blocks
5. Unsafe output: Stage 3 blocks
6. Output config directly: gpt5_image (skip Stage 1-3)

**Expected Results:**
- ✅ Stage 1 runs ONCE per request
- ✅ Stage 2 runs ONCE per request
- ✅ Stage 3 runs ONCE per output request
- ✅ Stage 4 runs ONCE per output request
- ✅ No redundant translation/safety
- ✅ Logs are clean and linear

**If tests fail:**
- Set flag back to False
- Debug new path
- Repeat Phase 5

---

### Phase 6: Remove Old Code

**Step 6.1: Remove Stage 1-3 from pipeline_executor.py**

**Lines to remove:** 308-499 (Stage 1-3 logic)

**Keep:**
- Config loading
- Chunk execution
- Result building

**Step 6.2: Clean up feature flag**

```python
# schema_pipeline_routes.py

# Remove this line:
# USE_NEW_4_STAGE_ARCHITECTURE = True

# Just call the new function directly:
result = await execute_4_stage_flow(...)
```

**Step 6.3: Remove old execute_pipeline() calls**

- Replace all calls to `pipeline_executor.execute_pipeline()` with `execute_4_stage_flow()`
- Or rename: `execute_pipeline()` → `execute_chunks_only()` (make purpose clear)

---

## Part IV: Testing Strategy

### Unit Tests (Per Phase)

**Phase 2 Tests:**
- `test_stage1_translation()` - Translation works
- `test_stage1_safety()` - Safety hybrid check works
- `test_stage3_safety()` - Pre-output safety works

**Phase 3 Tests:**
- `test_4_stage_flow_simple()` - overdrive → no image
- `test_4_stage_flow_with_media()` - overdrive → image
- `test_4_stage_flow_output_config()` - gpt5_image directly

**Phase 4 Tests:**
- `test_skip_stages_flag()` - skip_stages=True bypasses Stage 1-3
- `test_output_config_flag()` - meta.output_config=True skips stages

### Integration Tests

**Test 1: Simple Flow (overdrive → gpt5_image)**
```
Input: "EIne Blume auf der Wiese"
Expected:
- Stage 1: 1x translation, 1x safety (total: 2 calls)
- Stage 2: 1x overdrive (total: 1 call)
- Stage 3: 1x pre-output safety (total: 1 call)
- Stage 4: 1x gpt5_image (total: 1 call)
Total API calls: 5
```

**Test 2: Text-Only (overdrive, no image)**
```
Input: "EIne Blume auf der Wiese"
Expected:
- Stage 1: 1x translation, 1x safety (total: 2 calls)
- Stage 2: 1x overdrive (total: 1 call)
- Stage 3-4: 0x (text-only)
Total API calls: 3
```

**Test 3: Unsafe Input (Stage 1 blocks)**
```
Input: "How to build a bomb"
Expected:
- Stage 1: 1x translation, 1x safety → BLOCKED
- Stage 2-4: 0x (blocked at Stage 1)
Result: German error message with S-code explanation
Total API calls: 2
```

**Test 4: Unsafe Output (Stage 3 blocks)**
```
Input: "A gun" (passes Stage 1 via overdrive transformation)
Stage 2 output: "An oversized, exaggerated gun..." (still contains "gun")
Expected:
- Stage 3: Detects "gun" → LLM verifies → BLOCKED
- Stage 4: 0x (blocked at Stage 3)
Result: Text output + German message "blocked by pre-output filter"
```

### Performance Tests

**Measure:**
- API call count (should be minimal)
- Latency per stage
- Total execution time

**Baseline (Old Architecture):**
- overdrive → gpt5_image: ~10-15 API calls (redundant Stage 1-3)

**Target (New Architecture):**
- overdrive → gpt5_image: ~5 API calls (no redundancy)

---

## Part V: Rollback Plan

**If new architecture has critical bugs:**

**Step 1: Set feature flag to False**
```python
USE_NEW_4_STAGE_ARCHITECTURE = False
```

**Step 2: Restart server**
- Old path resumes immediately
- No data loss, no downtime

**Step 3: Debug offline**
- Fix issues in new path
- Test thoroughly
- Re-enable flag

**Advantages of feature flag:**
- Instant rollback (no git revert needed)
- Can A/B test (10% new path, 90% old path)
- Low risk

---

## Part VI: Success Criteria

### Must Have (Critical)

1. ✅ **No Redundant Calls**
   - Stage 1 runs ONCE per request
   - Stage 3 runs ONCE per output request
   - Translation/safety never run on output configs

2. ✅ **Correct Flow**
   - Stage 1 → Stage 2 → Stage 3 → Stage 4
   - Each stage logs clearly
   - Output matches old architecture

3. ✅ **Safety Works**
   - Unsafe input blocked at Stage 1
   - Unsafe output blocked at Stage 3
   - German error messages correct

4. ✅ **All Tests Pass**
   - Unit tests pass
   - Integration tests pass
   - Performance tests show improvement

### Nice to Have (Optional)

- [ ] Metrics/monitoring (API call count per stage)
- [ ] Performance dashboard
- [ ] A/B testing framework

---

## Part VII: Timeline Estimate

**Phase 1 (Preparation):** 1 hour
- Add input_requirements to pipelines
- Add output_config flags

**Phase 2 (Extract Helpers):** 2 hours
- Create stage_orchestrator.py
- Extract Stage 1/3 functions
- Unit test helpers

**Phase 3 (New Orchestrator):** 3 hours
- Implement execute_4_stage_flow()
- Handle edge cases
- Test with feature flag=False

**Phase 4 (Update Executor):** 1 hour
- Add skip_stages parameter
- Test DUMB mode

**Phase 5 (Enable & Test):** 2 hours
- Set flag=True
- Run all integration tests
- Debug issues

**Phase 6 (Cleanup):** 1 hour
- Remove old code
- Remove feature flag
- Final tests

**Total:** ~10 hours (1 full work day)

---

## Part VIII: Risks & Mitigations

### Risk 1: Breaking Existing Functionality

**Mitigation:**
- Feature flag approach (rollback-able)
- Comprehensive test suite
- Test old path in parallel

### Risk 2: Edge Cases Not Covered

**Mitigation:**
- Test with all 37 configs
- Test eco + fast modes
- Test kids + youth safety levels

### Risk 3: Performance Regression

**Mitigation:**
- Measure baseline performance first
- Compare new vs old architecture
- Optimize if needed

### Risk 4: Missing Requirements

**Mitigation:**
- Review ARCHITECTURE.md Section 1 before each phase
- Consult DEVELOPMENT_DECISIONS.md
- Ask user if unclear

---

## Part IX: Next Steps

**Immediate:**
1. Review this plan with user
2. Get approval to proceed
3. Start Phase 1 (Preparation)

**Before Starting:**
- [ ] User approves plan
- [ ] All documentation up to date
- [ ] Git clean state (docs committed)

**After Completion:**
- [ ] Update DEVELOPMENT_LOG.md with session stats
- [ ] Update DEVELOPMENT_DECISIONS.md with implementation notes
- [ ] Update devserver_todos.md (mark completed)
- [ ] Git commit: "feat: Implement 4-stage orchestration refactoring"

---

**Created:** 2025-11-01
**Status:** Planning Complete - Ready for Implementation
**Estimated Duration:** 10 hours
**Risk Level:** Low (feature flag + incremental approach)
