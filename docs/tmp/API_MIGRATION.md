# API Migration: workflow_routes → schema_pipeline_routes

**Status:** In Progress
**Date:** 2025-10-28
**Priority:** High

---

## Executive Summary

We have **two API endpoints** that do almost the same thing:

1. **`/run_workflow`** (workflow_routes.py) - **LEGACY / DEPRECATED**
2. **`/api/schema/pipeline/execute`** (schema_pipeline_routes.py) - **NEW / RECOMMENDED**

Both implement Auto-Media orchestration (Interception → Output), but use different backends.

**Decision:** Deprecate `/run_workflow` and migrate to `/api/schema/pipeline/execute`

---

## Current State

### workflow_routes.py (LEGACY)
- **File:** `my_app/routes/workflow_routes.py` (41 KB)
- **Endpoint:** `/run_workflow`
- **Used by:** Frontend (currently in production)
- **Backend:** Old services (workflow_logic_service, ollama_service, comfyui_service)
- **Features:**
  - Auto-Media orchestration ✓
  - Hidden commands (#image#, #audio#) ✓
  - Legacy workflow_generator ✓
  - Inpainting support ✓
  - Export management ✓
- **Issues:**
  - Large, complex, hard to maintain
  - Mixes concerns (validation, export, orchestration)
  - Uses deprecated workflow_generator
  - Confusing "workflow" terminology

### schema_pipeline_routes.py (NEW)
- **File:** `my_app/routes/schema_pipeline_routes.py` (11 KB)
- **Endpoint:** `/api/schema/pipeline/execute`
- **Used by:** API tests, future frontend
- **Backend:** New engine (pipeline_executor, config_loader, backend_router)
- **Features:**
  - Auto-Media orchestration ✓
  - Clean separation of concerns ✓
  - Proxy-Chunk system ✓
  - Execution mode support (eco/fast) ✓
- **Advantages:**
  - Small, focused, maintainable
  - Uses new architecture (Chunks/Pipelines/Configs)
  - Clear terminology
  - Better error handling

---

## Why Migrate?

### Technical Reasons
1. **Cleaner Architecture:** New engine separates concerns properly
2. **Easier Maintenance:** 11 KB vs 41 KB of code
3. **Future-Proof:** Built for Chunks/Pipelines/Configs system
4. **Better Testing:** Isolated components are easier to test
5. **Clear Semantics:** "schema/pipeline" is clearer than "workflow"

### Business Reasons
1. **All Interception-Configs Run Locally:** HUGE milestone achieved!
2. **Auto-Media Working:** Text → Media generation fully functional
3. **No More "Workflows":** Legacy terminology removed
4. **Consistency:** One source of truth for pipeline execution

---

## Migration Plan

### Phase 1: Preparation (DONE ✓)
- [x] Implement Auto-Media in schema_pipeline_routes.py
- [x] Fix prompt_id extraction in both routes
- [x] Test Auto-Media with dada config (eco mode)
- [x] Document current state

### Phase 2: Deprecation (IN PROGRESS)
- [ ] Mark workflow_routes.py as deprecated in code
- [ ] Add deprecation warnings to /run_workflow endpoint
- [ ] Update ARCHITECTURE.md with new API structure
- [ ] Create this migration guide

### Phase 3: Frontend Migration (TODO)
- [ ] Update frontend to use /api/schema/pipeline/execute
- [ ] Add backward compatibility layer if needed
- [ ] Test all frontend workflows with new endpoint
- [ ] Monitor for issues

### Phase 4: Cleanup (TODO)
- [ ] Remove /run_workflow endpoint
- [ ] Move workflow_routes.py to workflow_routes.py.obsolete
- [ ] Clean up unused legacy services
- [ ] Remove workflow_generator references

---

## API Comparison

### Old API: `/run_workflow`

**Request:**
```json
{
  "workflow": "dada",
  "prompt": "A red bicycle",
  "mode": "eco"
}
```

**Response:**
```json
{
  "status": "success",
  "prompt_id": "uuid-here",
  "media_type": "image",
  "final_output": "transformed text..."
}
```

### New API: `/api/schema/pipeline/execute`

**Request:**
```json
{
  "schema": "dada",
  "input_text": "A red bicycle",
  "execution_mode": "eco"
}
```

**Response:**
```json
{
  "status": "success",
  "schema": "dada",
  "final_output": "transformed text...",
  "media_output": {
    "config": "sd35_large",
    "media_type": "image",
    "output": "uuid-here",
    "execution_time": 0.13,
    "metadata": {...}
  }
}
```

**Key Differences:**
- More structured response (separates text and media)
- Clearer parameter names ("schema" vs "workflow")
- Better metadata (execution times, config info)
- Consistent error format

---

## Breaking Changes

### Parameter Names
- `workflow` → `schema` (semantically clearer)
- `prompt` → `input_text` (consistent with architecture)
- `mode` → `execution_mode` (explicit)

### Response Structure
- Flat response → Nested with `media_output` key
- Single output → Separate text and media outputs
- Better error information

### Frontend Changes Required
```javascript
// OLD
const response = await fetch('/run_workflow', {
  method: 'POST',
  body: JSON.stringify({
    workflow: 'dada',
    prompt: userInput,
    mode: 'eco'
  })
});

// NEW
const response = await fetch('/api/schema/pipeline/execute', {
  method: 'POST',
  body: JSON.stringify({
    schema: 'dada',
    input_text: userInput,
    execution_mode: 'eco'
  })
});

// Response handling
const data = await response.json();
// OLD: data.final_output, data.prompt_id
// NEW: data.final_output (text), data.media_output.output (media)
```

---

## Backward Compatibility

**Option A: Keep /run_workflow as thin wrapper (RECOMMENDED)**
```python
@workflow_bp.route('/run_workflow', methods=['POST'])
def execute_workflow_deprecated():
    """DEPRECATED: Use /api/schema/pipeline/execute instead"""
    logger.warning("DEPRECATED: /run_workflow is deprecated, use /api/schema/pipeline/execute")

    # Translate old params to new format
    data = request.json
    new_request = {
        'schema': data.get('workflow'),
        'input_text': data.get('prompt'),
        'execution_mode': data.get('mode', 'eco')
    }

    # Call new endpoint internally
    # ... forward and translate response
```

**Option B: Direct cutover**
- Update frontend all at once
- Remove old endpoint completely
- Higher risk, but cleaner

---

## Testing Strategy

### Unit Tests
- [ ] Test new API with all Interception-Configs
- [ ] Test new API with all Output-Configs
- [ ] Test error handling
- [ ] Test execution_mode switching

### Integration Tests
- [ ] Test Auto-Media flow (Interception → Output)
- [ ] Test with ComfyUI (eco mode)
- [ ] Test with OpenRouter (fast mode)
- [ ] Test media_preferences detection

### Frontend Tests
- [ ] Test all UI workflows
- [ ] Test error messages
- [ ] Test loading states
- [ ] Test media display

---

## Success Criteria

- [ ] All frontend features work with new API
- [ ] No performance regression
- [ ] Better error messages for users
- [ ] Code is cleaner and more maintainable
- [ ] Documentation is complete

---

## Timeline

**Week 1 (Current):**
- ✅ Auto-Media implementation
- ✅ Testing and fixes
- ✅ Documentation

**Week 2:**
- [ ] Frontend migration preparation
- [ ] Backward compatibility layer
- [ ] Testing

**Week 3:**
- [ ] Frontend cutover
- [ ] Monitoring
- [ ] Bug fixes

**Week 4:**
- [ ] Cleanup
- [ ] Remove legacy code
- [ ] Final documentation

---

## Risks & Mitigations

### Risk: Frontend breaks during migration
**Mitigation:** Implement backward compatibility wrapper, test thoroughly

### Risk: Performance issues with new API
**Mitigation:** Already tested, performance is better (cleaner code path)

### Risk: Missing features from old API
**Mitigation:** Feature audit completed, all features present or planned

### Risk: User confusion from API changes
**Mitigation:** Clear error messages, migration guide for API users

---

## Open Questions

1. **Hidden commands (#image#, #audio#):** Migrate to new API or deprecate?
   - Recommendation: Keep for backward compatibility, document as legacy

2. **Export functionality:** Keep in workflow_routes or move to separate route?
   - Recommendation: Move to export_routes.py (cleaner separation)

3. **Inpainting:** Migrate or keep separate?
   - Recommendation: Keep separate route, it's specialized

4. **Validation pipeline:** Still needed?
   - Recommendation: Review usage, possibly deprecate

---

## Related Documents

- [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture
- [RULES.md](../RULES.md) - Development rules
- [DEVELOPMENT_DECISIONS.md](./DEVELOPMENT_DECISIONS.md) - Why decisions were made
- [devserver_todos.md](./devserver_todos.md) - Current tasks

---

**Last Updated:** 2025-10-28
**Next Review:** When frontend migration starts
