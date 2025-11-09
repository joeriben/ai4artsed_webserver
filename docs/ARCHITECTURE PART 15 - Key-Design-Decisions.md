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

