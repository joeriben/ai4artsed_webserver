# Task-Based Model Selection Guide

## Overview

The devserver now supports **task-based model selection** in addition to concrete model names. Instead of specifying a particular model (which may become outdated), you can specify the **type of task** and let the system choose the optimal model.

## Quick Start

### Old Way (Concrete Models)
```json
{
  "model": "local/gemma2:9b"
}
```

### New Way (Task-Based)
```json
{
  "model": "task:standard"
}
```

The system will automatically select:
- **ECO mode**: `local/mistral-nemo`
- **FAST mode**: `openrouter/mistralai/mistral-nemo`

## Available Task Categories

### 1. `task:security`
**Use for:** Content moderation, safety checks, filtering
**Models:**
- ECO: `local/llama-guard-3-8b`
- FAST: `local/llama-guard-3-8b` ⚠️ **Always local for security**

**Example:**
```json
{
  "class_type": "ai4artsed_prompt_interception",
  "inputs": {
    "model": "task:security",
    "filter_level": "kids"
  }
}
```

---

### 2. `task:vision`
**Use for:** Image analysis, visual description
**Models:**
- ECO: `local/llava:13b`
- FAST: `local/llava:13b` ⚠️ **Always local for DSGVO privacy**

**Example:**
```json
{
  "class_type": "ai4artsed_image_analysis",
  "inputs": {
    "model": "task:vision",
    "system_prompt": "Describe the image..."
  }
}
```

---

### 3. `task:translation`
**Use for:** Language translation, multilingual tasks
**Models:**
- ECO: `local/qwen2.5-translator`
- FAST: `openrouter/google/gemma-3-27b-it`

**Example:**
```json
{
  "class_type": "ai4artsed_prompt_interception",
  "inputs": {
    "model": "task:translation",
    "input_prompt": "Translate this German text to English"
  }
}
```

---

### 4. `task:standard`
**Use for:** Standard creative prompts, general artistic tasks (MOST COMMON)
**Models:**
- ECO: `local/mistral-nemo`
- FAST: `openrouter/mistralai/mistral-nemo`

**Example:**
```json
{
  "class_type": "ai4artsed_prompt_interception",
  "inputs": {
    "model": "task:standard",
    "style_prompt": "Create a dadaist poem",
    "input_prompt": "Ein Kamel in der Wüste"
  }
}
```

**💡 Tip:** If unsure which task to use, `task:standard` covers 80% of creative use cases.

---

### 5. `task:advanced`
**Use for:** Complex cultural/ethical contexts, advanced semantics
**Models:**
- ECO: `local/mistral-small:24b`
- FAST: `openrouter/google/gemini-2.5-pro` 🌟 **Best for complex reasoning**

**Example:**
```json
{
  "class_type": "ai4artsed_prompt_interception",
  "inputs": {
    "model": "task:advanced",
    "style_prompt": "Analyze the ethical implications of this artwork in Yoruba cultural context",
    "input_prompt": "..."
  }
}
```

**When to use `advanced` instead of `standard`:**
- Cultural heritage workflows
- Ethical/philosophical analysis
- Complex semantic transformations
- Art historical interpretations requiring deep cultural knowledge

---

### 6. `task:data_extraction`
**Use for:** Extract numbers, booleans, structured data from text
**Models:**
- ECO: `local/gemma3:4b`
- FAST: `openrouter/google/gemma-3-4b-it`

**Example:**
```json
{
  "class_type": "ai4artsed_prompt_interception",
  "inputs": {
    "model": "task:data_extraction",
    "input_prompt": "Extract the year from this text: The artwork was created in 1923"
  }
}
```

## Migration Guide

### Updating Existing Workflows

**Before:**
```json
{
  "model": "local/mistral-nemo:latest"
}
```

**After (Recommended):**
```json
{
  "model": "task:standard"
}
```

**Benefits:**
- ✅ Future-proof (models can be updated centrally)
- ✅ Semantic clarity (shows intent, not implementation)
- ✅ Automatic optimization (system picks best model for task)
- ✅ Consistent across workflows

### Backward Compatibility

**Concrete models still work!** You can continue using specific models:
```json
{
  "model": "local/gemma2:9b"
}
```

This gives you full control when needed, but task-based is recommended for most cases.

## Schema Templates

In schema templates (`devserver/schemas/chunks/*.json`), use task-based selection:

```json
{
  "name": "prompt_interception",
  "backend_type": "ollama",
  "model": "task:standard",
  "template": "Task:\n{{TASK}}\n\nContext:\n{{CONTEXT}}\nPrompt:\n{{INPUT_TEXT}}",
  "parameters": {
    "temperature": 0.7
  }
}
```

The `model` field will be automatically converted based on the user's execution mode (eco/fast).

## Python API

### Direct Selection
```python
from schemas.engine.model_selector import model_selector

# Task-based
model = model_selector.select_model_for_mode("task:advanced", "fast")
# → "openrouter/google/gemini-2.5-pro"

# Concrete (still works)
model = model_selector.select_model_for_mode("gemma2:9b", "eco")
# → "local/gemma2:9b"
```

### List Available Tasks
```python
tasks = model_selector.list_task_types()
# → ['advanced', 'data_extraction', 'security', 'standard', 'translation', 'vision']

for task in tasks:
    desc = model_selector.get_task_description(task)
    print(f"{task}: {desc}")
```

## Best Practices

### DO ✅
- Use `task:standard` for most creative prompts
- Use `task:advanced` for cultural/ethical complexity
- Use `task:security` for content moderation
- Use `task:vision` for image analysis
- Let execution mode (eco/fast) choose the backend

### DON'T ❌
- Don't hardcode specific model versions (they change)
- Don't use cloud models for security/vision (privacy!)
- Don't use `task:advanced` when `task:standard` suffices (costs more)

## Decision Tree

```
Need to analyze an image?
  → task:vision (always local for privacy)

Need content moderation?
  → task:security (always local for security)

Need language translation?
  → task:translation

Need to extract data (numbers/booleans)?
  → task:data_extraction

Need creative prompt processing?
  ├─ Simple/general → task:standard
  └─ Complex cultural/ethical → task:advanced
```

## Testing

Test your workflow with both modes:

```bash
# ECO mode (local/Ollama)
curl -X POST http://localhost:17801/api/run_workflow \
  -H "Content-Type: application/json" \
  -d '{"workflow": "dev/your_schema", "mode": "eco", "prompt": "test"}'

# FAST mode (cloud/OpenRouter)
curl -X POST http://localhost:17801/api/run_workflow \
  -H "Content-Type: application/json" \
  -d '{"workflow": "dev/your_schema", "mode": "fast", "prompt": "test"}'
```

Check logs for:
```
[TASK-BASED] Task 'standard' → local/mistral-nemo (mode: eco)
[TASK-BASED] Task 'advanced' → openrouter/google/gemini-2.5-pro (mode: fast)
```

## FAQ

**Q: Can I still use specific models like `gemma2:9b`?**
A: Yes! Concrete models still work for backward compatibility.

**Q: What if I request FAST mode for `task:security`?**
A: It stays local. Security and vision tasks ignore execution mode for privacy/security.

**Q: Which task should I use for most workflows?**
A: `task:standard` covers 80% of creative use cases. Use `task:advanced` only when dealing with complex cultural/ethical contexts.

**Q: Can I add new task categories?**
A: Yes, edit `devserver/schemas/engine/model_selector.py` and add to `_define_task_categories()`.

**Q: How do I know which model is actually being used?**
A: Check the server logs - they show the selected model for each request.

## Troubleshooting

### OpenRouter API Key Not Found

**Problem:** FAST mode fails with "OpenRouter API Key not found"

**Solution:** Create `devserver/openrouter.key` file:
```bash
# File: devserver/openrouter.key
# You can add comments like this
# The actual key should start with "sk-"

sk-or-v1-abc123...your-actual-key-here
```

**Note:** The key loader automatically skips:
- Empty lines
- Lines starting with `#`
- Lines starting with `//`

### Backend Not Switching in FAST Mode

**Problem:** FAST mode still uses Ollama instead of OpenRouter

**Symptoms:**
- Logs show `🏠 Ollama Request` even when FAST mode selected
- Template has `"backend_type": "ollama"` hardcoded

**Solution:** The system now detects backend from model prefix automatically:
- `local/model` → Ollama
- `openrouter/model` → OpenRouter

The template's `backend_type` is only used as fallback if no prefix exists.

### Recursion Error

**Problem:** "maximum recursion depth exceeded" when using FAST mode

**Cause:** This was a bug in backend detection (fixed in current version)

**Solution:** Update to latest code - the backend_router now properly detects backends from model prefixes without recursion.

### Model Not Available

**Problem:** Request fails with "model not available"

**For Ollama (ECO mode):**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Pull the model if missing
ollama pull mistral-nemo
```

**For OpenRouter (FAST mode):**
- Check if API key is valid
- Verify model name is correct (check OpenRouter docs)
- System will attempt fallback to similar models automatically

### Different Output Between ECO and FAST

**Expected Behavior:** Different models produce different outputs

**ECO mode** (Ollama): Local models, may vary in style/quality  
**FAST mode** (OpenRouter): Cloud models, often more sophisticated

This is normal - the models are different. For consistent results, use the same model in both modes or use task-based selection which picks similar-capability models.

## Common Questions

**Q: Why do security/vision tasks ignore FAST mode?**  
A: Privacy and DSGVO compliance. These tasks handle sensitive data and must stay local.

**Q: Can I force a specific model even with task-based selection?**  
A: Yes, use concrete model names instead of `task:` prefix.

**Q: How do I know which model was actually used?**  
A: Check server logs for `[BACKEND]` messages showing the exact model used.

**Q: Can I add my own task categories?**  
A: Yes, edit `model_selector.py` and add to `_define_task_categories()`.

## Summary

Task-based selection makes workflows:
- **Future-proof** - Models can be updated centrally
- **Semantic** - Shows intent clearly
- **Optimized** - System picks best model for each task
- **Consistent** - Same logic across all workflows

**Recommended migration path:**
1. New workflows → Use task-based from start
2. Existing workflows → Migrate gradually (both work)
3. Special cases → Keep concrete models when needed
