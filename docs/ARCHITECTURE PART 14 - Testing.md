# DevServer Architecture

**Part 14: Testing**

---


### Test Files

**1. test_refactored_system.py**
- Tests architecture components
- Config loading (34 configs)
- Pipeline loading (4 pipelines)
- Backward compatibility
- No execution, just validation

**2. test_pipeline_execution.py**
- Tests actual pipeline execution
- Requires Ollama running
- Tests with real configs (dada, overdrive)
- End-to-end validation

### Running Tests

```bash
# Architecture tests (fast, no dependencies)
python3 test_refactored_system.py

# Execution tests (requires Ollama)
python3 test_pipeline_execution.py
```

### Test Coverage

**Current Coverage:**
- ✅ Config loading (34 configs)
- ✅ Pipeline loading (4 pipelines)
- ✅ Chunk building
- ✅ Placeholder replacement
- ✅ Backend routing
- ✅ Task-based model selection
- ✅ Execution modes (eco/fast)

**TODO:**
- [ ] #notranslate# marker logic
- [ ] Output generation pipelines
- [ ] ComfyUI workflow generation
- [ ] Multi-step text→media chains

---

