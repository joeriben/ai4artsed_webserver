# Handover: LoRA Parsing & Integration

**Date:** 2026-01-11
**Status:** RESET COMPLETED (git reset --hard a077a6e)
**Previous Agent:** Claude (via Cline) - FAILED
**Cleanup Agent:** Claude (via Claude Code)

## Reset Summary

All parsing-related commits were removed via hard reset to commit `a077a6e`.
The LoRA Training Studio (commit `f21a56b`) was preserved - this feature works correctly.

**What was removed:**
- `parse_and_extract_loras()` function
- 4-tuple returns from `execute_stage1_gpt_oss_unified`
- All `triggers` handling in `schema_pipeline_routes.py`
- Test files (TEST_lora_parsing.py, TEST_lora_end_to_end.py)

**What was kept:**
- LoRA Training Studio (Frontend + Backend)
- All other DevServer functionality

## Context
The goal was to implement a "Dual-Parse" architecture for LoRA triggers:
1.  Parse `<lora:name:strength>` tags from User Input (Stage 1) -> Remove them so Safety checks see clean text.
2.  Parse tags from Stage 2 (LLM Optimization) output.
3.  Merge triggers and inject them into the ComfyUI workflow (Stage 4).

## The Failure
The previous implementation failed due to architectural inconsistencies:
1.  **Streaming Mode Missed:** The implementation only covered the synchronous `/pipeline/execute` route. The streaming route `/pipeline/execute_streaming` has a completely separate Stage 1 implementation which was ignored, leading to missing parsing in streaming mode.
2.  **Context Availability:** The plan relied on `PipelineContext` or `tracker.metadata` to pass triggers from Stage 1 to Stage 4.
    - `PipelineContext` is only created in Stage 4, so it cannot be used to store data in Stage 1.
    - `tracker.metadata` was used as a "quick fix" (modifying `NoOpTracker`), which was rejected as architecturally unclean.
3.  **Variable Naming:** `triggers_unified` was used, causing confusion with legacy "unified" models.

## The Solution (Architecture)
The correct approach identified (but not implemented before reset) is:
1.  **Local Variables:** In the manual orchestration functions (`execute_pipeline` and `execute_pipeline_streaming`), use local variables to capture triggers returned from Stage 1.
2.  **Pass Explicitly:** Pass these triggers down or merge them with Stage 2 triggers before creating the `PipelineContext` in Stage 4.
3.  **Streaming Parity:** Ensure `execute_pipeline_streaming` implements the same parsing logic as the synchronous route.

## Preserved Code Snippets
The parsing logic itself was correct and tested. Here is the function for reference:

```python
import re

def parse_and_extract_loras(text: str) -> tuple[str, list[dict]]:
    """
    Extracts <lora:name:strength> tags from text.
    Returns cleaned text and list of trigger dicts.
    Default strength is 1.0 if not specified.
    """
    lora_pattern = r'<lora:([^:>]+)(?::([0-9.]+))?>'
    triggers = []
    
    def replace_callback(match):
        name = match.group(1)
        strength = float(match.group(2)) if match.group(2) else 1.0
        triggers.append({'name': name, 'strength': strength})
        return ""

    cleaned_text = re.sub(lora_pattern, replace_callback, text, flags=re.IGNORECASE)
    # Clean up double spaces/newlines left behind
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    
    return cleaned_text, triggers
```

## Next Steps
1.  Re-implement `parse_and_extract_loras` in `stage_orchestrator.py`.
2.  Update `execute_stage1...` to return triggers (4-tuple).
3.  Update `schema_pipeline_routes.py`:
    - In `execute_pipeline` (Sync): Capture triggers from Stage 1 into a local variable.
    - In `execute_pipeline_streaming` (Async): Capture triggers from Stage 1 into a local variable.
4.  Implement Parse Point 2 (Stage 2 output parsing) in both routes.
5.  Merge triggers and pass to `PipelineContext` (via `custom_placeholders`) when initializing Stage 4.

## Lessons Learned (For Next Implementation)

### DO:
- Use simple local variables in the orchestration functions to pass triggers
- Keep the parsing function pure: input text, output (cleaned_text, triggers)
- Test BOTH `/pipeline/execute` AND `/pipeline/execute_streaming` routes
- Commit incrementally and verify each step works before proceeding

### DO NOT:
- Use `tracker.metadata` as storage (NoOpTracker should remain no-op)
- Use confusing variable names like `triggers_unified`
- Create "quick fixes" that violate architectural principles
- Skip streaming mode (it's not optional - both routes must work)

### Architecture Principle
The data flow is simple:
```
Stage 1 Input → parse_and_extract_loras() → cleaned_text + triggers (local var)
             ↓
Stage 2 runs on cleaned_text
             ↓
Stage 2 Output → parse_and_extract_loras() → final_text + more_triggers (local var)
             ↓
Merge triggers (local operation)
             ↓
Create PipelineContext with merged triggers in custom_placeholders
             ↓
Stage 4 uses context.custom_placeholders['loras']
```

No special storage, no tracker hacks, just local variables passed through function scope.
