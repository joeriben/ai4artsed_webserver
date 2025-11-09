# DevServer Architecture

**Part 18: Data Storage & Persistence**

> **Last Updated:** 2025-11-09
> **Status:** Current as of v2.0.0-alpha.1 (Sessions 21-22, 27, 29, 37, 39)

---

## Overview

**v2.0.0-alpha.1 Status:** As of Session 37, DevServer uses **two active data persistence systems**:

1. **Execution History** (Sessions 19-24) - Research data tracking [ACTIVE]
2. **LivePipelineRecorder** (Session 29, enhanced Session 37) - Real-time entity tracking + media storage [PRIMARY]
3. ~~**Unified Media Storage** (Session 27)~~ - **REMOVED in Session 37**

**Critical Architecture:** Both active systems use a **unified `run_id`** (Session 29 fix).

**Major Change (Session 37):** MediaStorage completely removed from pipeline execution. LivePipelineRecorder now handles ALL real-time tracking and media storage, eliminating redundancy.

---

## 1. Execution History System (Sessions 19-24)

### Purpose

Track complete pedagogical journey through 4-stage pipeline for research data export.

### Architecture

```
exports/pipeline_runs/
└── exec_20251104_212530_896e054c.json
```

**File naming:** `exec_{YYYYMMDD}_{HHMMSS}_{8_char_uuid}.json`

### Data Model

#### ExecutionRecord
```python
@dataclass
class ExecutionRecord:
    execution_id: str                    # exec_20251104_...
    config_name: str                     # "dada", "bauhaus", etc.
    execution_mode: str                  # "eco" or "fast"
    safety_level: str                    # "kids" or "youth"
    user_id: str                         # "DOE_J", "anonymous"
    session_id: str                      # "workshop_2025"
    timestamp: str                       # ISO 8601
    items: List[ExecutionItem]           # Chronological items
    total_execution_time: float          # Seconds
    taxonomy_version: str                # "1.0"
    used_seed: Optional[int]             # Random seed
```

#### ExecutionItem
```python
@dataclass
class ExecutionItem:
    sequence_number: int                 # 1, 2, 3, ...
    stage: int                           # 0-5 (5=pipeline_complete)
    item_type: str                       # See Item Type Taxonomy
    timestamp: str                       # ISO 8601
    content: Optional[str]               # Text content
    file_path: Optional[str]             # Media file reference
    model_used: Optional[str]            # "mistral-nemo:latest"
    backend_used: Optional[str]          # "ollama", "comfyui"
    execution_time: Optional[float]      # Seconds
    metadata: Optional[Dict]             # Additional data
    stage_iteration: Optional[int]       # For Stille Post (1-8)
    loop_iteration: Optional[int]        # For multi-output (1-N)
```

### Item Type Taxonomy (20+ Types)

**Stage 0 - System:**
- `pipeline_start` - Pipeline initialization
- `pipeline_complete` - Pipeline finished

**Stage 1 - Pre-Interception:**
- `user_input_text` - Original user input
- `translation_result` - Translated text
- `stage1_safety_check` - §86a safety check

**Stage 2 - Interception:**
- `interception_iteration` - Each Stille Post iteration (stage_iteration=1-8)
- `interception_final` - Final interception result

**Stage 3 - Pre-Output Safety:**
- `stage3_safety_check` - Content safety check (per output)

**Stage 4 - Media Generation:**
- `output_image` - Generated image
- `output_audio` - Generated audio
- `output_music` - Generated music
- `output_video` - Generated video (future)

See `docs/ITEM_TYPE_TAXONOMY.md` for complete taxonomy.

### Metadata Tracking

**Stage 1 Example:**
```json
{
  "model_used": "gpt-oss",
  "backend_used": "ollama",
  "execution_time": 0.0
}
```

**Stage 3 Example (LLM-based):**
```json
{
  "method": "llm_context_check",
  "model_used": "local/llama-guard3:1b",
  "backend_used": "ollama",
  "execution_time": 0.986
}
```

**Stage 4 Example:**
```json
{
  "model_used": "unknown",
  "backend_used": "comfyui",
  "execution_time": 0.035
}
```

### Integration

**File:** `devserver/execution_history/tracker.py`

```python
# Initialize tracker with unified run_id
tracker = ExecutionTracker(
    execution_id=run_id,  # Same as LivePipelineRecorder & MediaStorage
    config_name=schema_name,
    execution_mode=execution_mode,
    safety_level=safety_level,
    user_id=user_id,
    session_id=session_id
)

# Log items throughout pipeline
tracker.log_user_input(input_text)
tracker.log_translation_result(translation, backend_used="ollama")
tracker.log_stage1_safety_check(result, model_used, backend_used, execution_time)
tracker.log_interception_iteration(iteration_result, iteration_number)
tracker.log_stage3_safety_check(result, model_used, backend_used, execution_time)
tracker.log_output_image(output_data, execution_time)

# Finalize and save to disk
tracker.finalize(total_duration, outputs_generated)
```

### API Endpoints

See **ARCHITECTURE PART 11 (API-Routes)** for complete API documentation:
- `GET /api/runs/stats` - Storage statistics
- `GET /api/runs` - List executions with filtering
- `GET /api/runs/<execution_id>` - Single execution record
- `GET /api/runs/<execution_id>/export/<format>` - Export (JSON implemented)

---

## 2. ~~Unified Media Storage (Session 27)~~ **DEPRECATED - REMOVED Session 37**

### Historical Purpose (Session 27-36)

Backend-agnostic media file persistence with complete run metadata.

### Why It Was Removed (Session 37)

**Problem:** Dual-system redundancy between MediaStorage and LivePipelineRecorder:
- Both systems downloaded media from ComfyUI
- Both systems saved metadata
- LivePipelineRecorder had to copy from MediaStorage
- Complex coordination, duplicate code paths

**Solution:** Merge functionality into LivePipelineRecorder as single source of truth.

**Migration:** All MediaStorage functionality moved to LivePipelineRecorder in Session 37.

### Legacy Architecture (Sessions 27-36)

```
exports/json/
└── {run_id}/
    ├── metadata.json
    ├── input_text.txt
    ├── transformed_text.txt
    └── output_image.png
```

**Note:** This storage location is now used by LivePipelineRecorder (Session 37+).

### Migration to LivePipelineRecorder (Session 37)

All MediaStorage functionality was moved to LivePipelineRecorder:
- Backend detection logic → LivePipelineRecorder
- Media download from ComfyUI → LivePipelineRecorder
- Metadata management → LivePipelineRecorder
- API endpoints → Now served by LivePipelineRecorder

**See Section 3 (LivePipelineRecorder)** for current implementation details.

---

## 3. LivePipelineRecorder (Session 29, Enhanced Session 37)

### Purpose

Real-time entity tracking with sequential numbering for frontend polling + media storage (Session 37+).

**v2.0.0-alpha.1 Status:** PRIMARY system for all real-time data and media storage.

### Problem Solved: Dual-ID Bug (Session 29) + Redundancy (Session 37)

**Before Session 29:**
```python
# OLD ExecutionTracker generated:
execution_id = f"exec_{timestamp}_{uuid8}"

# OLD MediaStorage generated:
run_id = str(uuid.uuid4())

# Result: Complete desynchronization!
```

**After Session 29:**
```python
# Generate ONCE at pipeline start:
run_id = str(uuid.uuid4())

# Pass to ALL systems:
execution_tracker = ExecutionTracker(execution_id=run_id)
media_storage.create_run(run_id)  # REMOVED Session 37
pipeline_recorder = LivePipelineRecorder(run_id)
```

**After Session 37:**
```python
# Generate ONCE at pipeline start:
run_id = str(uuid.uuid4())

# Pass to ACTIVE systems:
execution_tracker = ExecutionTracker(execution_id=run_id)  # Still exists for research data
pipeline_recorder = LivePipelineRecorder(run_id)  # PRIMARY - handles media + tracking
# MediaStorage completely removed
```

### Architecture

**Session 37+ Storage Location:**
```
exports/json/              # PRIMARY LOCATION (Session 37+)
└── {run_id}/
    ├── metadata.json
    ├── 01_input.txt
    ├── 02_translation.txt
    ├── 03_safety.json
    ├── 04_interception.txt
    ├── 05_safety_pre_output.json
    └── 06_output_image.png
```

**Sequential entity tracking:** 01 → 06 for easy frontend access.

**Note:** Storage path migrated from `pipeline_runs/{run_id}/` to `exports/json/{run_id}/` in Session 37 to unify with legacy MediaStorage location.

### Data Model

#### Metadata.json
```json
{
  "run_id": "812ccc30-5de8-416e-bfe7-10e913916672",
  "schema": "dada",
  "execution_mode": "eco",
  "safety_level": "kids",
  "user_id": "DOE_J",
  "start_time": "2025-11-04T21:15:30",
  "status": "completed",
  "current_stage": 5,
  "current_step": "pipeline_complete",
  "progress": "6/6",
  "entities": {
    "01_input": {"type": "text", "available": true},
    "02_translation": {"type": "text", "available": true},
    "03_safety": {"type": "json", "available": true},
    "04_interception": {"type": "text", "available": true},
    "05_safety_pre_output": {"type": "json", "available": true},
    "06_output_image": {"type": "image", "available": true, "mime_type": "image/png"}
  }
}
```

### Entity Types

**Text Entities:**
- `01_input.txt` - Original user input
- `02_translation.txt` - Translated text
- `04_interception.txt` - Transformed prompt

**JSON Entities:**
- `03_safety.json` - Stage 1 safety check results
- `05_safety_pre_output.json` - Stage 3 safety check results

**Media Entities:**
- `06_output_image.png` - Generated image
- `06_output_audio.mp3` - Generated audio
- `06_output_video.mp4` - Generated video (future)

### Real-Time State Tracking

```python
# Update state throughout pipeline
recorder.update_state(
    stage=1,
    step='translation_and_safety',
    progress='1/6'
)

recorder.update_state(
    stage=2,
    step='interception',
    progress='3/6'
)

recorder.update_state(
    stage=4,
    step='media_generation',
    progress='5/6'
)
```

### Integration

**File:** `devserver/my_app/services/pipeline_recorder.py`

```python
from my_app.services.pipeline_recorder import get_recorder

# Initialize with unified run_id
recorder = get_recorder(
    run_id=run_id,  # Same as ExecutionTracker & MediaStorage
    schema=schema_name,
    execution_mode=execution_mode,
    safety_level=safety_level,
    user_id=user_id
)

# Save entities throughout pipeline
recorder.save_entity('input', input_text, metadata={...})
recorder.save_entity('translation', translation_output)
recorder.save_entity('safety', safety_result)
recorder.save_entity('interception', interception_output)
recorder.save_entity('safety_pre_output', safety_result)
# Session 37+: Media downloaded and saved by LivePipelineRecorder directly
await recorder.download_and_save_media(prompt_id, media_type='image')
```

### Media Polling Bug Fix (Critical Achievement)

**The Problem:**
ComfyUI generates images asynchronously. Calling `get_history(prompt_id)` immediately returns empty result.

**The Fix (Session 37 in pipeline_recorder.py):**
```python
# OLD (BROKEN in MediaStorage):
# history = await client.get_history(prompt_id)

# NEW (FIXED in LivePipelineRecorder):
history = await client.wait_for_completion(prompt_id)
```

**Why This Matters:**
- `wait_for_completion()` polls every 2 seconds until workflow finishes
- **OLD ExecutionTracker identified this issue but FAILED to fix it for months**
- **Session 37 LivePipelineRecorder integration finally fixed it properly**
- **Session 39 media_type bugfix completed the stability**

### API Endpoints

See **ARCHITECTURE PART 11 (API-Routes)** for complete API documentation:
- `GET /api/pipeline/<run_id>/status` - Real-time execution state
- `GET /api/pipeline/<run_id>/entities` - List available entities
- `GET /api/pipeline/<run_id>/entity/<type>` - Fetch specific entity

---

## Unified run_id Architecture

### Critical: Single ID Across All Systems (Session 29+)

**v2.0.0-alpha.1 Implementation:**
```python
# schema_pipeline_routes.py (Session 37+)

# Generate ONCE at pipeline start
run_id = str(uuid.uuid4())

# Pass to ACTIVE systems
execution_tracker = ExecutionTracker(
    execution_id=run_id,  # ← Same ID
    config_name=schema_name,
    execution_mode=execution_mode,
    safety_level=safety_level,
    user_id=user_id,
    session_id=session_id
)

# MediaStorage REMOVED Session 37 - no longer used
# media_storage.create_run(...)  # DEPRECATED

recorder = get_recorder(
    run_id=run_id,  # ← Same ID (PRIMARY system)
    schema=schema_name,
    execution_mode=execution_mode,
    safety_level=safety_level,
    user_id=user_id
)
```

### Data Flow (v2.0.0-alpha.1)

```
1. Pipeline Start
   ↓
   run_id = uuid.uuid4()
   ↓
2. Initialize ACTIVE systems with same run_id (Session 37+)
   ├─→ ExecutionTracker(execution_id=run_id)  # Research data
   └─→ LivePipelineRecorder(run_id)           # PRIMARY - media + tracking
   ↓
3. Execute Pipeline (Stages 1-4)
   ├─→ tracker.log_*()                        # Research data logging
   └─→ recorder.save_entity()                 # Real-time entity + media
   ↓
4. Finalize
   ├─→ tracker.finalize() → exports/pipeline_runs/exec_*.json
   └─→ recorder → exports/json/{run_id}/      # PRIMARY storage location
```

---

## Storage Locations Summary (v2.0.0-alpha.1)

```
Project Root
├── exports/
│   ├── json/                          # LivePipelineRecorder (Session 37+)
│   │   └── {run_id}/                  # PRIMARY STORAGE LOCATION
│   │       ├── metadata.json
│   │       ├── 01_input.txt
│   │       ├── 02_translation.txt
│   │       ├── 03_safety.json
│   │       ├── 04_interception.txt
│   │       ├── 05_safety_pre_output.json
│   │       └── 06_output_image.png
│   │
│   └── pipeline_runs/                 # Execution History (Sessions 21-22)
│       └── exec_20251104_*.json      # Research data export format
│
└── # DEPRECATED locations (Session 37):
    # pipeline_runs/{run_id}/ - REMOVED
    # MediaStorage system - REMOVED
```

---

## Key Design Decisions

### 1. Two Active Systems (v2.0.0-alpha.1)

**Session 37 Simplification:**
- ~~Three parallel systems~~ → **Two active systems**
- MediaStorage removed → LivePipelineRecorder handles all real-time data
- ExecutionHistory: Complete pedagogical journey for research
- LivePipelineRecorder: Real-time frontend tracking + media storage (PRIMARY)

**Why Two Systems Remain:**
- Different data models (sequential entities vs. research taxonomy)
- Different access patterns (real-time polling vs. export queries)
- ExecutionHistory proven valuable for research (Sessions 21-24)
- LivePipelineRecorder optimized for frontend needs (Session 29+)

### 2. Unified run_id (Session 29)

**Critical Fix:** Prevents Dual-ID desynchronization bug.

**Single source of truth:** Generated once, used everywhere.

**Session 37 Benefit:** Unified ID made MediaStorage removal clean and safe.

### 3. Flat Structures

**No hierarchical sessions:**
- Session entity doesn't exist yet technically
- UUID-based enables future queries via metadata
- Simpler than complex hierarchies

### 4. Atomic Research Units

**One folder = complete run:**
- All files for one pipeline execution in one location
- No split data across multiple directories
- Export-ready (zip one folder = complete data)

### 5. MediaStorage Removal (Session 37)

**Why removed:**
- Duplicate functionality with LivePipelineRecorder
- Complex coordination between systems
- Redundant media downloads
- LivePipelineRecorder proved more reliable

**Result:** Cleaner architecture, single source of truth for real-time data

---

## Related Documentation

- **API Endpoints:** ARCHITECTURE PART 11 (API-Routes)
- **4-Stage Pipeline:** ARCHITECTURE PART 01 (4-Stage Orchestration Flow)
- **Technical Details:**
  - `docs/EXECUTION_TRACKER_ARCHITECTURE.md` (1200+ lines, Sessions 19-24)
  - `docs/ITEM_TYPE_TAXONOMY.md` (Item type taxonomy)
  - `docs/LIVE_PIPELINE_RECORDER.md` (Live recorder design, Session 37+ PRIMARY)
  - ~~`docs/UNIFIED_MEDIA_STORAGE.md`~~ (DEPRECATED Session 37, historical reference only)
- **Decision History:**
  - `docs/DEVELOPMENT_DECISIONS.md` (Sessions 27, 29, 37, 39)
  - `docs/DEVELOPMENT_LOG.md` (Sessions 19-24, 27, 29, 37, 39)

**v2.0.0-alpha.1 Migration Notes:**
- MediaStorage functionality fully migrated to LivePipelineRecorder (Session 37)
- Unified run_id architecture proven stable (Session 29+)
- stage4_only feature operational (Session 39)

---
