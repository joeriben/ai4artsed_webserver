# DevServer Architecture

**Part 18: Data Storage & Persistence**

> **Last Updated:** 2025-11-06
> **Status:** Current as of Sessions 21-22, 27, 29

---

## Overview

DevServer implements **three parallel data persistence systems**, each serving distinct purposes:

1. **Execution History** (Sessions 19-24) - Research data tracking
2. **Unified Media Storage** (Session 27) - Backend-agnostic media files
3. **LivePipelineRecorder** (Session 29) - Real-time entity tracking

**Critical Architecture:** All three systems use a **unified `run_id`** (Session 29 fix).

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

## 2. Unified Media Storage (Session 27)

### Purpose

Backend-agnostic media file persistence with complete run metadata.

### Problem Solved

**Before Session 27:**
- ❌ ComfyUI images displayed but NOT stored locally
- ❌ OpenRouter images stored as data strings (unusable)
- ❌ Export function failed (media not persisted)
- ❌ Research data incomplete

**After Session 27:**
- ✅ All media downloaded during pipeline execution
- ✅ Backend-agnostic (ComfyUI, OpenRouter, Replicate)
- ✅ Atomic research units (one folder = complete run)
- ✅ Export-ready

### Architecture

```
exports/json/
└── {run_id}/
    ├── metadata.json
    ├── input_text.txt
    ├── transformed_text.txt
    └── output_image.png
```

**Storage path:** `exports/json/{run_id}/` (migrated from `media_storage/runs/` in Session 31)

### Data Model

#### RunMetadata
```json
{
  "run_id": "812ccc30-5de8-416e-bfe7-10e913916672",
  "user_id": "DOE_J",
  "timestamp": "2025-11-04T21:15:30",
  "schema": "dada",
  "execution_mode": "eco",
  "safety_level": "kids",
  "input_text": "A surreal dream",
  "transformed_text": "Ein surrealistischer Traum in dadaistischer Ästhetik...",
  "outputs": [
    {
      "type": "image",
      "filename": "output_image.png",
      "backend": "comfyui",
      "config": "sd35_large",
      "file_size_bytes": 1048576,
      "format": "png",
      "width": 1024,
      "height": 1024,
      "created_at": "2025-11-04T21:15:45"
    }
  ]
}
```

### Design Decisions

#### Flat Structure (No Sessions)
> User: "I just think we do not have an entity 'session' yet, and I would not know how to discriminate sessions technically."

No hierarchical structure. UUID-based flat folders enable future queries via metadata.

#### "Run" Terminology (Not "Execution")
> User: "stop using 'execution'. this is also the word for killing humans."

German language sensitivity. "Run" is neutral, commonly used in programming.

#### Atomic Units
> User: "Our data management has to keep 'atomic' research events, such as one pipeline run, together."

One folder = one complete research event. No split data across locations.

#### UUID-Based for Concurrency
Supports workshop scenario: 15 kids executing pipelines simultaneously.

### Backend Detection Logic

**File:** `devserver/my_app/services/media_storage.py`

```python
# Auto-detect backend type
if output_value.startswith('http'):
    # API-based (OpenRouter) - Download from URL
    await media_storage.add_media_from_url(
        run_id=run_id,
        url=output_value,
        media_type="image"
    )
else:
    # ComfyUI - Fetch via prompt_id
    await media_storage.add_media_from_comfyui(
        run_id=run_id,
        prompt_id=output_value,
        media_type="image"
    )
```

### Integration

**File:** `devserver/my_app/routes/schema_pipeline_routes.py`

```python
# Create run at pipeline start
from my_app.services.media_storage import get_media_storage_service
media_storage = get_media_storage_service()

run_id = str(uuid.uuid4())  # Unified ID
media_storage.create_run(
    run_id=run_id,
    user_id=user_id,
    schema=schema_name,
    execution_mode=execution_mode,
    safety_level=safety_level,
    input_text=input_text
)

# After Stage 2: Save transformed text
media_storage.save_text(run_id, "transformed_text.txt", interception_output)

# After Stage 4: Auto-download media
if output_value.startswith('http'):
    await media_storage.add_media_from_url(run_id, output_value, "image")
else:
    await media_storage.add_media_from_comfyui(run_id, output_value, "image")
```

### API Endpoints

See **ARCHITECTURE PART 11 (API-Routes)** for complete API documentation:
- `GET /api/media/image/<run_id>` - Serve image file
- `GET /api/media/audio/<run_id>` - Serve audio file
- `GET /api/media/info/<run_id>` - Get metadata only
- `GET /api/media/run/<run_id>` - Complete run info

---

## 3. LivePipelineRecorder (Session 29)

### Purpose

Real-time entity tracking with sequential numbering for frontend polling.

### Problem Solved: Dual-ID Bug

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
media_storage.create_run(run_id)
pipeline_recorder = LivePipelineRecorder(run_id)
```

### Architecture

```
pipeline_runs/
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
# Media entity saved automatically by MediaStorage
```

### Media Polling Bug Fix (Critical Achievement)

**The Problem:**
ComfyUI generates images asynchronously. Calling `get_history(prompt_id)` immediately returns empty result.

**The Fix (Line 214 in media_storage.py):**
```python
# OLD (BROKEN):
# history = await client.get_history(prompt_id)

# NEW (FIXED):
history = await client.wait_for_completion(prompt_id)
```

**Why This Matters:**
- `wait_for_completion()` polls every 2 seconds until workflow finishes
- **OLD ExecutionTracker identified this issue but FAILED to fix it for months**
- **NEW LivePipelineRecorder SUCCEEDED on first implementation**

### API Endpoints

See **ARCHITECTURE PART 11 (API-Routes)** for complete API documentation:
- `GET /api/pipeline/<run_id>/status` - Real-time execution state
- `GET /api/pipeline/<run_id>/entities` - List available entities
- `GET /api/pipeline/<run_id>/entity/<type>` - Fetch specific entity

---

## Unified run_id Architecture

### Critical: Single ID Across All Systems

```python
# schema_pipeline_routes.py

# Generate ONCE at pipeline start
run_id = str(uuid.uuid4())

# Pass to ALL systems
execution_tracker = ExecutionTracker(
    execution_id=run_id,  # ← Same ID
    config_name=schema_name,
    execution_mode=execution_mode,
    safety_level=safety_level,
    user_id=user_id,
    session_id=session_id
)

media_storage.create_run(
    run_id=run_id,  # ← Same ID
    user_id=user_id,
    schema=schema_name,
    execution_mode=execution_mode,
    safety_level=safety_level,
    input_text=input_text
)

recorder = get_recorder(
    run_id=run_id,  # ← Same ID
    schema=schema_name,
    execution_mode=execution_mode,
    safety_level=safety_level,
    user_id=user_id
)
```

### Data Flow

```
1. Pipeline Start
   ↓
   run_id = uuid.uuid4()
   ↓
2. Initialize ALL systems with same run_id
   ├─→ ExecutionTracker(execution_id=run_id)
   ├─→ MediaStorage.create_run(run_id)
   └─→ LivePipelineRecorder(run_id)
   ↓
3. Execute Pipeline (Stages 1-4)
   ├─→ tracker.log_*()
   ├─→ media_storage.save_*()
   └─→ recorder.save_entity()
   ↓
4. Finalize
   ├─→ tracker.finalize() → exports/pipeline_runs/exec_*.json
   ├─→ media_storage → exports/json/{run_id}/
   └─→ recorder → pipeline_runs/{run_id}/
```

---

## Storage Locations Summary

```
Project Root
├── exports/
│   ├── json/                          # Unified Media Storage (Session 27)
│   │   └── {run_id}/
│   │       ├── metadata.json
│   │       ├── input_text.txt
│   │       ├── transformed_text.txt
│   │       └── output_image.png
│   │
│   └── pipeline_runs/                 # Execution History (Sessions 21-22)
│       └── exec_20251104_*.json
│
└── pipeline_runs/                     # LivePipelineRecorder (Session 29)
    └── {run_id}/
        ├── metadata.json
        ├── 01_input.txt
        ├── 02_translation.txt
        ├── 03_safety.json
        ├── 04_interception.txt
        ├── 05_safety_pre_output.json
        └── 06_output_image.png
```

---

## Key Design Decisions

### 1. Three Parallel Systems (By Design)

**Why not merge them?**
- Each serves distinct purpose
- ExecutionHistory: Complete pedagogical journey for research
- MediaStorage: Backend-agnostic file persistence
- LivePipelineRecorder: Real-time frontend tracking

**Overlap is intentional:**
- Redundancy ensures no data loss
- Different access patterns (research vs real-time)
- Gradual migration path (OLD → NEW)

### 2. Unified run_id (Session 29)

**Critical Fix:** Prevents Dual-ID desynchronization bug.

**Single source of truth:** Generated once, used everywhere.

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

---

## Related Documentation

- **API Endpoints:** ARCHITECTURE PART 11 (API-Routes)
- **4-Stage Pipeline:** ARCHITECTURE PART 01 (4-Stage Orchestration Flow)
- **Technical Details:**
  - `docs/EXECUTION_TRACKER_ARCHITECTURE.md` (1200+ lines)
  - `docs/ITEM_TYPE_TAXONOMY.md` (Item type taxonomy)
  - `docs/UNIFIED_MEDIA_STORAGE.md` (Media storage design)
  - `docs/LIVE_PIPELINE_RECORDER.md` (Live recorder design)
- **Decision History:**
  - `docs/DEVELOPMENT_DECISIONS.md` (Active Decision 7 & 8)
  - `docs/DEVELOPMENT_LOG.md` (Sessions 19-24, 27, 29)

---
