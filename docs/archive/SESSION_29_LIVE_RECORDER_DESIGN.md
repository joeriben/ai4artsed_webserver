# Session 29 - Live Pipeline Recorder Design

**Date:** 2025-11-04
**Status:** 🔧 NEW ARCHITECTURE - Replacing ExecutionTracker + MediaStorage

---

## Problem Statement

Sessions 19-27 created TWO separate systems that never synchronized:
1. **ExecutionTracker** - In-memory collection, writes at end, generates own ID
2. **MediaStorage** - Retroactive downloads, generates different ID

**Result:** Broken system where nothing gets stored and exports fail.

---

## User's Core Insight

> "If we recognize that every pipeline, no matter how complex, essentially produces one or more media entities (text, image, ...) that ALWAYS appear one after the other as a linear appearance of entities, THEN devserver should save them one by one as they appear."

Key requirements:
1. **Write immediately** - Save to disk AS entities appear (not retroactively)
2. **Know current state** - Server can tell frontend "what's happening now"
3. **Self-describing** - Tell frontend what outputs to expect upfront
4. **One folder** - All files for one run together
5. **Simple structure** - Numbered files show order

---

## Solution: LivePipelineRecorder

**One system that:**
- Writes files immediately (like tape recorder)
- Maintains state (knows current stage/step)
- Self-describes (tells frontend structure upfront)

### File Structure

```
pipeline_runs/
└── {run_id}/
    ├── 01_input.txt              (Stage 1: user input)
    ├── 02_translation.txt         (Stage 1: translation result)
    ├── 03_safety.json             (Stage 1: safety check)
    ├── 04_interception.txt        (Stage 2: transformed text)
    ├── 05_safety_pre_output.json  (Stage 3: pre-output safety)
    ├── 06_output_image.png        (Stage 4: generated image)
    └── metadata.json              (Self-describing metadata)
```

### Metadata Structure

```json
{
  "run_id": "uuid-here",
  "timestamp": "2025-11-04T19:00:00",
  "config_name": "dada",
  "execution_mode": "eco",
  "safety_level": "kids",

  "expected_outputs": [
    "input",
    "translation",
    "safety",
    "interception",
    "safety_pre_output",
    "output_image"
  ],

  "current_state": {
    "stage": 4,
    "step": "image_generation_running",
    "progress": "5/6"
  },

  "entities": [
    {
      "sequence": 1,
      "type": "input",
      "filename": "01_input.txt",
      "timestamp": "2025-11-04T19:00:01",
      "metadata": {}
    },
    {
      "sequence": 6,
      "type": "output_image",
      "filename": "06_output_image.png",
      "timestamp": "2025-11-04T19:00:15",
      "metadata": {
        "seed": 12345,
        "cfg_scale": 7.0,
        "steps": 28,
        "model": "sd35_large"
      }
    }
  ]
}
```

---

## API Design

### For DevServer (Writing)

```python
# Create recorder at pipeline start
recorder = LivePipelineRecorder(run_id, config_name, execution_mode)

# Stage 1: Input
recorder.set_state(1, "input_received")
recorder.save_entity("input", user_input)

# Stage 1: Translation
recorder.set_state(1, "translation_running")
translated = await translate(user_input)
recorder.save_entity("translation", translated,
                     metadata={"from_lang": "de", "to_lang": "en"})

# Stage 2: Interception
recorder.set_state(2, "interception_running")
transformed = await run_interception(translated)
recorder.save_entity("interception", transformed,
                     metadata={"config": "dada", "model": "mistral-nemo"})

# Stage 4: Media generation
recorder.set_state(4, "image_generation_running")
image_bytes = await generate_image(transformed)
recorder.save_entity("output_image", image_bytes,
                     metadata={"seed": 12345, "cfg": 7.0})

recorder.set_state(5, "complete")
```

### For Frontend (Reading)

```javascript
// Get current status (poll every 1 second)
const status = await fetch(`/api/pipeline/${runId}/status`).then(r => r.json())

// Response:
{
  "run_id": "uuid...",
  "current_state": {
    "stage": 4,
    "step": "image_generation_running",
    "progress": "5/6"
  },
  "expected_outputs": ["input", "translation", "safety", ...],
  "completed_outputs": ["input", "translation", "safety", "interception"],
  "next_expected": "output_image",
  "entities": [...]
}

// Fetch completed entities
const imageUrl = `/api/pipeline/${runId}/entity/output_image`
```

---

## Implementation Plan

### Phase 1: Core Recorder (Priority 1)
- [x] Design document (this file)
- [ ] Implement LivePipelineRecorder class
- [ ] File writing utilities (text, json, binary)
- [ ] Metadata management (immediate writes)
- [ ] State tracking

### Phase 2: Integration (Priority 2)
- [ ] Update schema_pipeline_routes.py to use recorder
- [ ] Remove ExecutionTracker initialization
- [ ] Remove MediaStorage initialization
- [ ] Add recorder.save_entity() calls at each stage

### Phase 3: API Endpoints (Priority 3)
- [ ] GET /api/pipeline/{run_id}/status
- [ ] GET /api/pipeline/{run_id}/entity/{entity_type}
- [ ] Remove old /api/media/* endpoints (or deprecate)

### Phase 4: Testing (Priority 4)
- [ ] Test complete pipeline execution
- [ ] Verify files written to disk
- [ ] Test status endpoint polling
- [ ] Test entity serving

### Phase 5: Cleanup (Priority 5)
- [ ] Mark ExecutionTracker as obsolete
- [ ] Mark MediaStorage as obsolete
- [ ] Update documentation
- [ ] Update frontend (if needed)

---

## Key Design Decisions

### Decision 1: Write Immediately

**Why:** Current system fails because it tries to download media retroactively after generation completes. But by then, ComfyUI history might be cleared or API URLs expired.

**Solution:** Write every entity to disk THE MOMENT it's generated.

### Decision 2: Numbered Filenames

**Why:** Makes order visually obvious. Scientist can see "01, 02, 03..." and understand flow.

**Alternative considered:** Timestamps - rejected because harder to sort visually.

### Decision 3: Single metadata.json

**Why:** All metadata in one file makes it easy to query current state without reading all files.

**Format:** Updated after each entity (append-only safe).

### Decision 4: Self-Describing Structure

**Why:** Frontend needs to know "What outputs should I expect?" before they appear, so it can show placeholders/spinners.

**Solution:** Parse config at start to determine expected_outputs.

### Decision 5: One ID, One System

**Why:** Two separate systems with different IDs caused the original bug.

**Solution:** Generate ONE run_id, use for everything.

---

## Benefits Over Old System

| Old System (Sessions 19-27) | New System (LiveRecorder) |
|-----------------------------|---------------------------|
| Two IDs (tracker + storage) | One ID |
| In-memory + retroactive | Write immediately |
| No state awareness | Live state tracking |
| Frontend guesses structure | Self-describing upfront |
| ~900 lines across 2 systems | ~300 lines one system |
| Media downloads fail silently | Direct writes, obvious failures |
| Export uses wrong IDs | Export uses correct run_id |

---

## Migration Strategy

### Backward Compatibility

**Existing data:**
- Old `/exports/pipeline_runs/*.json` files - Keep for historical research
- Old `/media_storage/runs/` folders - Keep (but empty, so not useful)

**New data:**
- New `/pipeline_runs/` structure starting from Session 29

### Frontend Changes

Minimal changes needed:
1. Poll `/api/pipeline/{run_id}/status` instead of `/api/media/info/{prompt_id}`
2. Fetch entities via `/api/pipeline/{run_id}/entity/{type}`
3. Display status messages based on `current_state.step`

---

## Example: Complete Run

### Initial State (Pipeline Start)

```
pipeline_runs/abc123/
└── metadata.json  (expected_outputs listed, current_state = stage 1)
```

### After Stage 1 (Translation + Safety)

```
pipeline_runs/abc123/
├── 01_input.txt
├── 02_translation.txt
├── 03_safety.json
└── metadata.json  (entities: 3, current_state = stage 2)
```

### After Stage 2 (Interception)

```
pipeline_runs/abc123/
├── 01_input.txt
├── 02_translation.txt
├── 03_safety.json
├── 04_interception.txt
└── metadata.json  (entities: 4, current_state = stage 3)
```

### After Stage 4 (Complete)

```
pipeline_runs/abc123/
├── 01_input.txt
├── 02_translation.txt
├── 03_safety.json
├── 04_interception.txt
├── 05_safety_pre_output.json
├── 06_output_image.png
└── metadata.json  (entities: 6, current_state = complete)
```

---

## Error Handling

### If Stage Fails

Still write error entity:

```json
{
  "sequence": 5,
  "type": "error",
  "filename": "05_error.json",
  "timestamp": "...",
  "metadata": {
    "stage": 3,
    "error_type": "safety_blocked",
    "message": "Content violates §86a",
    "codes": ["§86a"]
  }
}
```

### If Server Crashes

Metadata.json shows last completed step. On restart, can resume or mark as incomplete.

---

## Testing Checklist

- [ ] Create recorder, verify folder created
- [ ] Save text entity, verify file exists
- [ ] Save JSON entity, verify parseable
- [ ] Save binary (image) entity, verify readable
- [ ] Update state, verify metadata.json updated
- [ ] Query status, verify current_state correct
- [ ] Complete pipeline end-to-end
- [ ] Verify all 6+ entities written
- [ ] Test concurrent runs (multiple users)
- [ ] Test error cases (blocked content)

---

## Documentation Updates Needed

After implementation:
- [ ] Update SESSION_27_SUMMARY.md (mark as obsolete approach)
- [ ] Update SESSION_28_ERRORS.md (explain why it failed)
- [ ] Create SESSION_29_IMPLEMENTATION.md (this design + results)
- [ ] Update ARCHITECTURE.md (new data flow)
- [ ] Update devserver_todos.md (remove old tasks, add new)

---

**Created:** 2025-11-04 Session 29
**Status:** Design approved, implementation next
**Replaces:** ExecutionTracker (Sessions 19-24) + MediaStorage (Session 27)
