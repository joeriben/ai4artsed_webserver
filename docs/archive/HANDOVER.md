# Phase 5 Handover: Integration Testing

**Date:** 2025-11-01
**Status:** Ready to start Phase 5
**Branch:** `feature/schema-architecture-v2`
**Estimated Time:** 2-3 hours

---

## ⚠️ IMPORTANT: Read Before Starting

**This document assumes you have read:**
- ✅ `docs/README_FIRST.md` (mandatory reading - 85 min)
- ✅ `/tmp/session9_summary.md` (Phase 3 completion summary)
- ✅ `docs/ARCHITECTURE.md` Section 1 (4-Stage Flow - AUTHORITATIVE)

**Current Progress:**
- ✅ Phase 1 Complete (metadata added to 49 JSON files)
- ✅ Phase 2 Complete (helper functions in stage_orchestrator.py)
- ✅ Phase 3 Complete (DevServer orchestration implemented)
- ⏭️ **Phase 5: YOU ARE HERE** - Integration testing

**Note:** Phase 4 (skip_stages parameter) is now OPTIONAL - architecture already clean after Phase 3.

---

## 📋 Phase 5 Goal

**Test 4-stage orchestration with comprehensive test coverage**

**Key Principle:** Verify DevServer orchestrates correctly, PipelineExecutor executes correctly, no redundancy.

**Strategy:**
1. Create automated test suite (`test_phase5_integration.py`)
2. Test multiple config types with various scenarios
3. Verify logs show clean execution (no redundant stages)
4. Document any issues found
5. Create report for Phase 6 cleanup

---

## 🎯 What Phase 5 Tests

### Test Categories

**1. Text Transformation Configs (Stage 1-2-3-4)**
- dada, bauhaus, overdrive, etc.
- Input: German text → Translation → Safety → Transform → Pre-Output → Media
- Expected: All 4 stages execute once each

**2. Output Configs (Skip Stage 1-3)**
- sd35_large, gpt5_image, flux1_dev
- Input: English prompt → Direct execution → Media
- Expected: Stage 1-3 skipped, Stage 4 executes

**3. System Pipelines (Skip Stage 1-3)**
- pre_interception/correction_translation_de_en
- pre_interception/safety_llamaguard
- Input: Direct text → Process → Return
- Expected: Stage 1-3 skipped, direct execution

**4. Safety Scenarios**
- Safe input → All stages pass
- Unsafe input (Stage 1) → Block at translation/safety
- Unsafe input (Stage 3) → Block before media generation
- safety_level='off' → Skip all safety checks

**5. Edge Cases**
- media_preferences=None → Text-only output (no Stage 3-4)
- Multiple output requests → Stage 3-4 loop
- Failed pipelines → Error handling
- English input → Translation pass-through

---

## 🔧 Implementation Guide

### Step 1: Create Test Suite

**File:** `test_phase5_integration.py`

```python
"""
Phase 5 Integration Tests: 4-Stage Orchestration
Tests complete flow from input to output for various config types
"""
import asyncio
import pytest
from schemas.engine.pipeline_executor import PipelineExecutor
from schemas.engine.config_loader import config_loader

# Test fixtures
@pytest.fixture
def pipeline_executor():
    executor = PipelineExecutor('schemas')
    return executor

# Test 1: Text transformation config (full 4-stage flow)
async def test_text_transformation_full_flow(pipeline_executor):
    """Test dada config: Stage 1 (translation+safety) → Stage 2 (transform) → Stage 3 (safety) → Stage 4 (media)"""
    # Implement test
    pass

# Test 2: Output config (skip Stage 1-3)
async def test_output_config_direct(pipeline_executor):
    """Test sd35_large: Should skip Stage 1-3, execute directly"""
    # Implement test
    pass

# Test 3: System pipeline (skip Stage 1-3)
async def test_system_pipeline_direct(pipeline_executor):
    """Test translation pipeline: Should skip Stage 1-3"""
    # Implement test
    pass

# Test 4: Unsafe input blocking (Stage 1)
async def test_unsafe_input_stage1(pipeline_executor):
    """Test input with unsafe terms: Should block at Stage 1"""
    # Implement test
    pass

# Test 5: Unsafe output blocking (Stage 3)
async def test_unsafe_output_stage3(pipeline_executor):
    """Test output with unsafe terms: Should block at Stage 3"""
    # Implement test
    pass

# Test 6: Safety level 'off'
async def test_safety_off(pipeline_executor):
    """Test with safety_level='off': Should skip all safety checks"""
    # Implement test
    pass

# Test 7: Text-only output
async def test_text_only_output(pipeline_executor):
    """Test config with no media_preferences: Should skip Stage 3-4"""
    # Implement test
    pass

# Run tests
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
```

### Step 2: Manual Testing via Server

**Start Server:**
```bash
cd /home/joerissen/ai/ai4artsed_webserver/devserver
python3 server.py

# Logs: tail -f /tmp/devserver.log | grep -E "\[4-STAGE\]|Stage"
```

**Test 1: Text Transformation (dada)**
```bash
curl -X POST http://localhost:17801/api/schema/pipeline/execute \
  -H "Content-Type: application/json" \
  -d '{
    "schema": "dada",
    "input_text": "Eine Blume auf der Wiese",
    "execution_mode": "eco",
    "safety_level": "kids"
  }'

# Expected in logs:
# [4-STAGE] Stage 1: Pre-Interception for 'dada'
# [STAGE1-SAFETY] PASSED (fast-path, 0.2ms)
# [4-STAGE] Stage 2: Interception (Main Pipeline) for 'dada'
# [4-STAGE] Stage 3: Pre-Output Safety for image (level: kids)
# [STAGE3-SAFETY] PASSED (fast-path, 0.1ms)
# [AUTO-MEDIA] Starting Output-Pipeline: sd35_large
```

**Test 2: Output Config (sd35_large)**
```bash
curl -X POST http://localhost:17801/api/schema/pipeline/execute \
  -H "Content-Type: application/json" \
  -d '{
    "schema": "sd35_large",
    "input_text": "A beautiful flower on a meadow",
    "execution_mode": "eco",
    "safety_level": "kids"
  }'

# Expected in logs:
# NO [4-STAGE] Stage 1 (should be skipped)
# NO [4-STAGE] Stage 3 (should be skipped)
# Pipeline for config 'sd35_large' completed
```

**Test 3: Unsafe Input (Stage 1)**
```bash
curl -X POST http://localhost:17801/api/schema/pipeline/execute \
  -H "Content-Type: application/json" \
  -d '{
    "schema": "dada",
    "input_text": "violent content with weapons and blood",
    "execution_mode": "eco",
    "safety_level": "kids"
  }'

# Expected: HTTP 403, error message with safety codes
```

**Test 4: Safety Off**
```bash
curl -X POST http://localhost:17801/api/schema/pipeline/execute \
  -H "Content-Type: application/json" \
  -d '{
    "schema": "dada",
    "input_text": "Eine Blume",
    "execution_mode": "eco",
    "safety_level": "off"
  }'

# Expected: Stage 1 safety skipped, Stage 3 skipped
```

### Step 3: Log Analysis

**Check for Redundancy:**
```bash
# Count Stage 1 executions (should be 1 or 0)
grep -c "\[4-STAGE\] Stage 1:" /tmp/devserver.log

# Check no recursive Stage 1-3 in output configs
grep "sd35_large" /tmp/devserver.log | grep -c "\[4-STAGE\] Stage 1"
# Should be 0

# Verify clean flow
grep "dada" /tmp/devserver.log | grep "\[4-STAGE\]"
# Should show: Stage 1 → Stage 2 → Stage 3 (no duplicates)
```

### Step 4: Create Test Report

**File:** `docs/PHASE5_TEST_REPORT.md`

```markdown
# Phase 5 Test Report

**Date:** [Date]
**Tester:** [Name/Session]
**Branch:** feature/schema-architecture-v2

## Test Results

### Text Transformation Configs
- [ ] dada: ✅/❌
- [ ] bauhaus: ✅/❌
- [ ] overdrive: ✅/❌
- [ ] stillepost: ✅/❌

### Output Configs
- [ ] sd35_large: ✅/❌
- [ ] gpt5_image: ✅/❌
- [ ] flux1_dev: ✅/❌

### System Pipelines
- [ ] translation: ✅/❌
- [ ] safety_llamaguard: ✅/❌

### Safety Scenarios
- [ ] Safe input (kids): ✅/❌
- [ ] Safe input (youth): ✅/❌
- [ ] Unsafe Stage 1: ✅/❌
- [ ] Unsafe Stage 3: ✅/❌
- [ ] Safety off: ✅/❌

### Edge Cases
- [ ] Text-only output: ✅/❌
- [ ] English input: ✅/❌
- [ ] German input: ✅/❌

## Issues Found

[List any issues discovered]

## Performance Observations

[Note any performance issues]

## Recommendations for Phase 6

[Cleanup tasks needed]
```

---

## ✅ Success Criteria

Phase 5 is complete when:

1. ✅ Automated test suite created and passing
2. ✅ Manual tests completed for all categories
3. ✅ Logs verified (no redundant Stage 1-3 calls)
4. ✅ All configs work end-to-end
5. ✅ Safety filters work correctly
6. ✅ Error handling works
7. ✅ Test report created
8. ✅ Documentation updated

**Test Coverage Required:**
- Minimum 10 different configs tested
- All 5 test categories covered
- Safe + unsafe scenarios tested
- Edge cases verified

---

## 🚨 Common Issues to Watch For

### Issue 1: Redundant Stage Calls
**Symptom:** Logs show Stage 1 or 3 running multiple times
**Check:** `grep -c "\[4-STAGE\] Stage 1:" /tmp/devserver.log`
**Fix:** Verify is_output_config and is_system_pipeline checks

### Issue 2: Output Configs Run Stage 1-3
**Symptom:** sd35_large shows "[4-STAGE] Stage 1"
**Check:** Config has `"stage": "output"` in meta?
**Fix:** Add missing metadata or fix check logic

### Issue 3: System Pipelines Recurse
**Symptom:** Translation pipeline triggers itself
**Check:** Config has `"system_pipeline": true` in meta?
**Fix:** Add missing metadata

### Issue 4: Safety Not Blocking
**Symptom:** Unsafe content passes through
**Check:** Filter terms loaded? Safety level correct?
**Fix:** Verify filter JSON files exist and are loaded

### Issue 5: Media Generation Fails
**Symptom:** Stage 4 errors
**Check:** ComfyUI running? Output config exists?
**Fix:** Start ComfyUI, verify config name

---

## 📊 Testing Strategy

### Automated Tests (pytest)
- Fast unit-style tests
- Mock external services (Ollama, ComfyUI)
- Focus on orchestration logic
- Run with: `pytest test_phase5_integration.py -v`

### Manual Tests (curl + server)
- Full integration tests
- Real Ollama + ComfyUI
- Verify complete flow
- Check logs for clean execution

### Log Analysis
- Grep for Stage patterns
- Count executions
- Verify no redundancy
- Check timing

---

## 📝 Documentation Updates Required

After Phase 5, update:

1. **`docs/DEVELOPMENT_LOG.md`**
   - Add Session 10 entry (or continue Session 9)
   - Document test results
   - Note any issues found

2. **`docs/devserver_todos.md`**
   - Mark Phase 5 complete
   - Add Phase 6 tasks based on findings

3. **`docs/PHASE5_TEST_REPORT.md`**
   - Create test report
   - List all tested configs
   - Document issues

4. **`docs/ARCHITECTURE.md` (if needed)**
   - Update if any issues found in design

---

## 🔗 Key References

**Must Read:**
- `docs/ARCHITECTURE.md` Section 1 (4-Stage Flow)
- `/tmp/session9_summary.md` (Phase 3 completion)
- `docs/IMPLEMENTATION_PLAN_4_STAGE_REFACTORING.md` Phase 5

**Implementation Files:**
- `my_app/routes/schema_pipeline_routes.py` (DevServer orchestration)
- `schemas/engine/stage_orchestrator.py` (Stage helpers)
- `schemas/engine/pipeline_executor.py` (DUMB executor)

**Test Examples:**
- `/tmp/test_request.json` (Dada test)
- `/tmp/devserver.log` (Server logs with [4-STAGE] markers)

---

## ⏭️ After Phase 5: Phase 6

**Phase 6: Final Cleanup & Documentation (1 hour)**

Based on Phase 5 findings:
- Fix any issues discovered
- Remove obsolete code (if any)
- Update documentation
- Create final test suite
- Prepare for merge to main

---

## 🎯 Quick Start Commands

```bash
# Navigate to devserver
cd /home/joerissen/ai/ai4artsed_webserver/devserver

# Read this handover
cat docs/HANDOVER.md

# Check Phase 3 implementation
grep -n "4-STAGE" my_app/routes/schema_pipeline_routes.py | head -10

# Start server for testing
python3 server.py &
tail -f /tmp/devserver.log | grep "\[4-STAGE\]"

# Create test suite
touch test_phase5_integration.py
# (Implement tests from Step 1 above)

# Run manual tests
curl -X POST http://localhost:17801/api/schema/pipeline/execute \
  -H "Content-Type: application/json" \
  -d @/tmp/test_request.json
```

---

**Status:** Ready to start Phase 5
**Estimated Time:** 2-3 hours
**Complexity:** Medium (testing + validation)

Good luck! 🚀
