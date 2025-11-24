# DevServer Architecture

**Part 11: API Routes**

> **Last Updated:** 2025-11-09
> **Status:** Current as of v2.0.0-alpha.1 (Sessions 27, 29, 31, 37, 39)

---

## Overview

DevServer provides REST API endpoints across four main areas:
1. **Pipeline Execution** - Main workflow endpoints
2. **Real-Time Tracking** - Live pipeline status and entities
3. **Media Serving** - Backend-agnostic media delivery
4. **Execution History** - Research data export and querying

---

## 1. Pipeline Execution API

### Primary Endpoint: `/api/schema/pipeline/execute`

**Purpose:** Execute a config-based 4-stage pipeline

**Request:**
```json
{
  "schema": "dada",
  "input_text": "A surreal dream",
  "execution_mode": "eco",  // [DEPRECATED - Session 65] Ignored by backend
  "safety_level": "kids"     // or "youth"
}
```

**⚠️ DEPRECATION NOTICE:** The `execution_mode` parameter was removed in Session 65 (2025-11-23). Model selection is now centralized in `devserver/config.py`. This parameter is still accepted for backward compatibility but has no effect.

**Response:**
```json
{
  "status": "success",
  "run_id": "812ccc30-5de8-416e-bfe7-10e913916672",
  "schema": "dada",
  "config_name": "dada",
  "input_text": "A surreal dream",
  "final_output": "Ein surrealistischer Traum in dadaistischer Ästhetik...",
  "execution_mode": "eco",  // [DEPRECATED - Session 65] Echo of input, no longer affects execution
  "safety_level": "kids",
  "execution_time": 12.5,
  "outputs_generated": 1,
  "backend_info": [
    {
      "stage": 1,
      "backend": "ollama",
      "model": "mistral-nemo:latest"
    },
    {
      "stage": 4,
      "backend": "comfyui",
      "model": "unknown"
    }
  ]
}
```

**Key Features:**
- Unified `run_id` for all tracking systems (Sessions 27, 29)
- 4-Stage orchestration (Stage 1-4)
- Automatic media download and storage
- Backend-agnostic execution

**Media-Specific Optimization (Session 64):**

Stage 2 execution can dynamically extend pipeline context with output-specific optimization instructions:

```python
# If output config declares OUTPUT_CHUNK parameter
# DevServer loads chunk metadata and extracts optimization_instruction
# Example: SD3.5 Large Dual CLIP optimization (980 chars)

optimization_instruction = output_chunk['meta'].get('optimization_instruction')
if optimization_instruction:
    # Extend context using dataclasses.replace()
    from dataclasses import replace
    stage2_config = replace(
        config,
        context=config.context + "\n\n" + optimization_instruction,
        meta={**config.meta, 'optimization_added': True}
    )
    # Execute with overridden config
    result = await pipeline_executor.execute_pipeline(
        config_override=stage2_config
    )
```

**Use Case:** SD3.5 requires Dual CLIP prompt optimization (clip_g + t5xxl architecture)
**Design:** Single LLM call combines interception + optimization (pedagogical constraint: max 2 LLM calls)

See ARCHITECTURE PART 01 (4-Stage Orchestration) for detailed implementation pattern.

---

### ⚠️ CRITICAL: Schema Parameter Must Be Config ID, Not Pipeline Name

**Common Pitfall:** The `schema` parameter in ALL pipeline endpoints expects the **config ID**, not the pipeline name.

**Config Structure:**
```json
{
  "id": "bauhaus",                      // ← Use this for 'schema' parameter
  "pipeline": "text_transformation",    // ← NEVER use this for 'schema'
  "version": "1.0",
  "category": "artistic"
}
```

**Example - Frontend API Call:**
```typescript
// User selects "bauhaus" config
// Config: { id: "bauhaus", pipeline: "text_transformation" }

// ✅ CORRECT:
schema: pipelineStore.selectedConfig?.id  // Sends "bauhaus"

// ❌ WRONG:
schema: pipelineStore.selectedConfig?.pipeline  // Sends "text_transformation" → 404 ERROR
```

**Why This Matters:**

1. **Backend file loading:** Backend uses `schema` parameter to load config file from `schemas/configs/{schema}.json`
2. **Pipeline names have no config files:** Sending "text_transformation" looks for `text_transformation.json` which doesn't exist
3. **Result:** HTTP 404 "Not Found" error
4. **Silent failure:** Backend logs show nothing because request never reaches route handler (FastAPI returns 404 before route execution)

**Debugging Clue:** If you see 404 errors in browser console but backend logs show no errors, suspect wrong `schema` parameter value.

**Bug History:** Session 64 Part 4 (2025-11-23) - Youth Flow sent `config.pipeline` instead of `config.id`, causing production-breaking 404 errors. Nearly forced complete revert of Session 64 refactoring work.

**Affected Endpoints:**
- `/pipeline/stage2` (Stage 1+2 execution)
- `/pipeline/execute` (Stage 1-4 execution)
- `/pipeline/stage3-4` (Stage 3+4 execution)
- `/pipeline/transform` (deprecated)

---

**Pre-Translation Logic:**
```python
# Check for #notranslate# marker
if "#notranslate#" in input_text:
    translated_text = input_text.replace("#notranslate#", "")
elif should_translate:
    translated_text = await translator_service.translate(input_text, "de")
else:
    translated_text = input_text
```

**Supporting Endpoints:**
```
GET /api/schema/list
→ Returns list of available schemas

GET /api/schema/<name>
→ Returns schema configuration details
```

---

## 2. Real-Time Tracking API (Session 29)

### LivePipelineRecorder Endpoints

**Purpose:** Real-time pipeline status for frontend polling

### GET `/api/pipeline/<run_id>/status`

**Response:**
```json
{
  "run_id": "812ccc30-5de8-416e-bfe7-10e913916672",
  "status": "in_progress",  // or "completed", "failed"
  "current_stage": 3,
  "current_step": "pre_output_safety",
  "progress": "4/6",
  "start_time": "2025-11-04T21:15:30",
  "elapsed_time": 8.5
}
```

**Use Case:** Frontend progress bars, status polling

### GET `/api/pipeline/<run_id>/entities`

**Response:**
```json
{
  "run_id": "812ccc30-5de8-416e-bfe7-10e913916672",
  "entities": [
    {
      "sequence": "01",
      "type": "input",
      "filename": "01_input.txt",
      "available": true
    },
    {
      "sequence": "02",
      "type": "translation",
      "filename": "02_translation.txt",
      "available": true
    },
    {
      "sequence": "06",
      "type": "output_image",
      "filename": "06_output_image.png",
      "available": true,
      "mime_type": "image/png"
    }
  ]
}
```

**Use Case:** Track which pipeline outputs are ready

### GET `/api/pipeline/<run_id>/entity/<entity_type>`

**Parameters:**
- `entity_type`: input, translation, safety, interception, safety_pre_output, output_image, etc.

**Response:** Binary file with appropriate MIME type
- Text entities: `text/plain; charset=utf-8`
- JSON entities: `application/json`
- Image entities: `image/png`, `image/jpeg`
- Audio entities: `audio/mpeg`, `audio/wav`

**Use Case:** Fetch individual pipeline entities for display

---

## 3. Media Serving API (Session 27)

### Unified Media Storage Endpoints

**Purpose:** Backend-agnostic media file serving

### GET `/api/media/image/<run_id>`

**Response:** Image file (PNG/JPEG)
**Headers:**
```
Content-Type: image/png
Content-Disposition: inline; filename="output_image.png"
```

**Use Case:** Display generated images

### GET `/api/media/audio/<run_id>`

**Response:** Audio file (MP3/WAV)
**Headers:**
```
Content-Type: audio/mpeg
Content-Disposition: inline; filename="output_audio.mp3"
```

**Use Case:** Play generated audio/music

### GET `/api/media/video/<run_id>`

**Response:** Video file (MP4/MOV)

**Use Case:** Display generated videos (future)

### GET `/api/media/info/<run_id>`

**Response:**
```json
{
  "run_id": "812ccc30-5de8-416e-bfe7-10e913916672",
  "outputs": [
    {
      "type": "image",
      "filename": "output_image.png",
      "file_size_bytes": 1048576,
      "format": "png",
      "width": 1024,
      "height": 1024,
      "backend": "comfyui",
      "config": "sd35_large"
    }
  ]
}
```

**Use Case:** Get media metadata without downloading file

### GET `/api/media/run/<run_id>`

**Response:**
```json
{
  "run_id": "812ccc30-5de8-416e-bfe7-10e913916672",
  "user_id": "DOE_J",
  "timestamp": "2025-11-04T21:15:30",
  "schema": "dada",
  "execution_mode": "eco",  // [DEPRECATED - Session 65] Historical data only
  "safety_level": "kids",
  "input_text": "A surreal dream",
  "transformed_text": "Ein surrealistischer Traum...",
  "outputs": [...]
}
```

**Use Case:** Complete run information including input/output text

---

## 4. Execution History API (Sessions 21-22)

### Research Data Export Endpoints

**Purpose:** Query and export pipeline execution records

### GET `/api/runs/stats`

**Response:**
```json
{
  "total_records": 42,
  "total_size_bytes": 125829120,
  "total_size_mb": 120.0,
  "storage_dir": "/path/to/exports/pipeline_runs"
}
```

**Use Case:** Storage statistics, system monitoring

### GET `/api/runs`

**Query Parameters:**
- `limit` (default: 20, max: 100) - Max results to return
- `offset` (default: 0) - Pagination offset
- `config` - Filter by config name (e.g., "dada")
- `date` - Filter by date (YYYY-MM-DD)
- `user_id` - Filter by user
- `session_id` - Filter by session

**Response:**
```json
{
  "executions": [
    {
      "execution_id": "exec_20251104_212530_896e054c",
      "config_name": "dada",
      "timestamp": "2025-11-04T21:25:30",
      "execution_mode": "eco",  // [DEPRECATED - Session 65] Historical data only
      "safety_level": "kids",
      "total_execution_time": 12.5,
      "items_count": 7,
      "user_id": "DOE_J",
      "session_id": "workshop_2025"
    }
  ],
  "total": 42,
  "limit": 20,
  "offset": 0,
  "returned": 1,
  "filters": {
    "config": "dada",
    "date": "2025-11-04",
    "user_id": null,
    "session_id": null
  }
}
```

**Use Case:** Browse execution history, filter by criteria

### GET `/api/runs/<execution_id>`

**Response:**
```json
{
  "execution_id": "exec_20251104_212530_896e054c",
  "config_name": "dada",
  "timestamp": "2025-11-04T21:25:30",
  "execution_mode": "eco",  // [DEPRECATED - Session 65] Historical data only
  "safety_level": "kids",
  "user_id": "DOE_J",
  "session_id": "workshop_2025",
  "total_execution_time": 12.5,
  "items": [
    {
      "sequence_number": 1,
      "stage": 0,
      "item_type": "pipeline_start",
      "timestamp": "2025-11-04T21:25:30"
    },
    {
      "sequence_number": 2,
      "stage": 1,
      "item_type": "user_input_text",
      "content": "A surreal dream"
    },
    ...
  ],
  "taxonomy_version": "1.0"
}
```

**Use Case:** Detailed execution record with complete pedagogical journey

### GET `/api/runs/<execution_id>/export/<format>`

**Supported Formats:**
- `json` - ✅ Implemented (raw JSON)
- `xml` - ⏳ Planned (research data format)
- `pdf` - ⏳ Planned (report format)
- `docx` - ⏳ Planned (legacy compatibility)

**Response (JSON):**
- Same as `GET /api/runs/<execution_id>`
- Includes `Content-Disposition: attachment` header for download

**Response (XML/PDF/DOCX):**
```json
{
  "error": "XML export not yet implemented",
  "status": "planned",
  "details": "This format will be available in a future release"
}
```

**Use Case:** Export research data for analysis

---

## Architecture Notes

### Unified run_id System

**Critical:** All tracking systems use the SAME `run_id`:
```python
# Generated ONCE at pipeline start
run_id = str(uuid.uuid4())

# Passed to ALL systems
execution_tracker = ExecutionTracker(execution_id=run_id)  # Still exists for compatibility
pipeline_recorder = LivePipelineRecorder(run_id)  # Primary system (Session 37+)
```

**Note:** MediaStorage was removed in Session 37 - LivePipelineRecorder is now the single source of truth for real-time tracking and media storage.

**Why Unified ID:** Fixes Dual-ID Bug (Session 29) - prevents desynchronization between systems

### Storage Locations

```
exports/
├── json/                    # LivePipelineRecorder (Session 37+)
│   └── {run_id}/            # Primary storage location
│       ├── metadata.json
│       ├── 01_input.txt
│       ├── 02_translation.txt
│       ├── 03_safety.json
│       ├── 04_interception.txt
│       ├── 05_safety_pre_output.json
│       └── 06_output_image.png
│
└── pipeline_runs/           # Execution History (Sessions 21-22)
    └── exec_*.json          # Research data export format

# DEPRECATED (Session 37): MediaStorage system removed
# DEPRECATED (Session 37): pipeline_runs/{run_id}/ location
```

**Note:** As of Session 37, LivePipelineRecorder handles ALL real-time tracking and media storage. MediaStorage has been completely removed from the pipeline execution flow.

### API Evolution

**OLD API (deprecated):**
```
POST /api/workflow/execute
GET  /api/media/image/{prompt_id}
```

**NEW API (current):**
```
POST /api/schema/pipeline/execute
GET  /api/media/image/{run_id}
GET  /api/pipeline/{run_id}/status
GET  /api/runs/{execution_id}
```

**Key Changes:**
- `prompt_id` → `run_id` (unified identifier)
- `/workflow/` → `/schema/pipeline/` (clearer naming)
- Added real-time tracking endpoints
- Added execution history endpoints

---

## Error Handling

### Standard Error Response

```json
{
  "error": "Error description",
  "status": "error_type",
  "details": "Additional context"
}
```

### Common Status Codes

- `200 OK` - Success
- `400 Bad Request` - Invalid parameters
- `404 Not Found` - run_id or execution_id not found
- `500 Internal Server Error` - Pipeline execution failure
- `501 Not Implemented` - Feature planned but not yet available

### Example Error Responses

**404 - Run Not Found:**
```json
{
  "error": "Run not found",
  "run_id": "invalid-uuid",
  "status": "not_found"
}
```

**400 - Invalid Format:**
```json
{
  "error": "Invalid export format",
  "format": "txt",
  "supported_formats": ["json", "xml", "pdf", "docx"],
  "available_now": ["json"]
}
```

---

## Related Documentation

- **Pipeline Execution:** ARCHITECTURE PART 01 (4-Stage Orchestration)
- **Data Storage:** ARCHITECTURE PART 18 (Data Storage & Persistence)
- **Backend Routing:** ARCHITECTURE PART 08 (Backend-Routing)
- **Execution Tracker:** `docs/EXECUTION_TRACKER_ARCHITECTURE.md` (Sessions 19-24, still active)
- **Pipeline Recorder:** `docs/LIVE_PIPELINE_RECORDER.md` (Session 37+, primary system)
- **Media Storage:** `docs/UNIFIED_MEDIA_STORAGE.md` (DEPRECATED Session 37)

---
