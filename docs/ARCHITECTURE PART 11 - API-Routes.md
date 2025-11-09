# DevServer Architecture

**Part 11: API Routes**

> **Last Updated:** 2025-11-06
> **Status:** Current as of Sessions 27, 29, 31

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
  "execution_mode": "eco",  // or "fast"
  "safety_level": "kids"     // or "youth"
}
```

**Response:**
```json
{
  "status": "success",
  "run_id": "812ccc30-5de8-416e-bfe7-10e913916672",
  "schema": "dada",
  "config_name": "dada",
  "input_text": "A surreal dream",
  "final_output": "Ein surrealistischer Traum in dadaistischer Ästhetik...",
  "execution_mode": "eco",
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
  "execution_mode": "eco",
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
      "execution_mode": "eco",
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
  "execution_mode": "eco",
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

**Critical:** All three tracking systems use the SAME `run_id`:
```python
# Generated ONCE at pipeline start
run_id = str(uuid.uuid4())

# Passed to ALL systems
execution_tracker = ExecutionTracker(execution_id=run_id)
media_storage.create_run(run_id)
pipeline_recorder = LivePipelineRecorder(run_id)
```

**Why:** Fixes Dual-ID Bug (Session 29) - prevents desynchronization between ExecutionHistory and MediaStorage

### Storage Locations

```
exports/
├── json/                    # Unified Media Storage (Session 27)
│   └── {run_id}/
│       ├── metadata.json
│       ├── input_text.txt
│       ├── transformed_text.txt
│       └── output_image.png
│
└── pipeline_runs/           # Execution History (Sessions 21-22)
    └── exec_*.json

pipeline_runs/               # LivePipelineRecorder (Session 29)
└── {run_id}/
    ├── metadata.json
    ├── 01_input.txt
    ├── 02_translation.txt
    ├── 03_safety.json
    ├── 04_interception.txt
    ├── 05_safety_pre_output.json
    └── 06_output_image.png
```

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
- **Execution Tracker:** `docs/EXECUTION_TRACKER_ARCHITECTURE.md`
- **Media Storage:** `docs/UNIFIED_MEDIA_STORAGE.md`
- **Pipeline Recorder:** `docs/LIVE_PIPELINE_RECORDER.md`

---
