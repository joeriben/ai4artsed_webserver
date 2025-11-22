# DevServer Architecture

**Part 15: Key Design Decisions**

---


### 1. Input-Type-Based Pipelines ✅

**Decision:** Pipelines categorized by INPUT structure, not output medium or backend

**Rationale:**
- Same input structure = same pipeline logic
- Output medium determined by config, not pipeline
- Backend determined by config, not pipeline
- Scalable (easy to add new media types without new pipelines)

**Example:**
- `single_text_media_generation` can output Image (SD3.5), Audio (Stable Audio), or Music
- Pipeline doesn't care about output type

---

### 2. Chunk Consolidation ✅

**Decision:** One universal `manipulate` chunk instead of multiple redundant chunks

**Removed:**
- translate.json (redundant with manipulate + translation context)
- prompt_interception.json (redundant with manipulate + different placeholder names)
- prompt_interception_lyrics.json (broken, invalid structure)
- prompt_interception_tags.json (broken, invalid structure)

**Rationale:**
- Content belongs in configs, not chunk names
- Reduces duplication (instruction appeared twice in rendered prompts)
- Cleaner architecture (3 chunks instead of 7)

---

### 3. Task-Based Model Selection ✅

**Decision:** Chunks declare `task_type`, model_selector.py maps to optimal LLM

**Implementation:**
```json
{
  "model": "task:translation",
  "meta": {"task_type": "translation"}
}
```

**Rationale:**
- Decouple chunk logic from specific model names
- Easy to upgrade models (change model_selector.py, not all chunks)
- Supports eco/fast mode switching
- DSGVO compliance (security/vision always local)

---

### 4. Backend Transparency ✅

**Decision:** Backend determined by config.meta.backend, not by pipeline or chunk

**Rationale:**
- Same pipeline can use ComfyUI (local) or OpenRouter (cloud)
- Easy to add new backends without changing pipelines
- Config controls everything (structure + content + backend)

---

### 5. No Fourth Layer ✅

**Decision:** No external registries or instruction_types system

**Rationale:**
- Instruction text belongs in configs (content layer)
- External indirection creates ambiguity and redundancy
- Three layers sufficient: Chunks (structure) → Pipelines (flow) → Configs (content)

---

### 6. Config Override Pattern for Runtime Optimization ✅

**Decision:** Use `dataclasses.replace()` for dynamic config modification, store optimization instructions in output chunk metadata

**Implementation:**
```python
from dataclasses import replace

# Load optimization instruction from output chunk
optimization_instruction = output_chunk['meta'].get('optimization_instruction')

# Create modified config with extended context
stage2_config = replace(
    config,
    context=config.context + "\n\n" + optimization_instruction,
    meta={**config.meta, 'optimization_added': True}
)

# Pass override to pipeline executor
result = await pipeline_executor.execute_pipeline(
    config_override=stage2_config
)
```

**Rationale:**
- **Pedagogical Constraint:** Max 2 LLM calls per workflow (single call for interception + optimization)
- **Storage Location:** Optimization instructions belong with model config (output chunk metadata)
- **Runtime Flexibility:** Same interception config works with different output configs
- **Dataclass Pattern:** Config is a dataclass, not Pydantic - use `dataclasses.replace()`, NOT `Config.from_dict()`

**Critical Implementation Rules:**
- ⚠️ MUST use `dataclasses.replace()` for config modification
- ⚠️ MUST load chunks directly from filesystem (ConfigLoader doesn't have `get_chunk()`)
- ⚠️ MUST use `await` for async pipeline execution (can't nest `asyncio.run()`)

**Bug History:** Session 64 Part 3 (2025-11-22) - Fixed 3 critical bugs violating these patterns

**Example Use Case:** SD3.5 Large Dual CLIP optimization (980 char instruction for clip_g + t5xxl architecture)

---

