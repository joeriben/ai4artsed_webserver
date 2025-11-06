# LivePipelineRecorder - Unified Pipeline Execution Tracking

**Status:** ✅ Implemented (Session 29)
**Version:** 1.0
**Date:** 2025-11-04

## Overview

The LivePipelineRecorder is a unified system for tracking pipeline execution in real-time. It replaces the previous dual-ID architecture (ExecutionTracker + MediaStorage) with a single, coherent system that writes entity files immediately as they are created during pipeline execution.

## Why This System Exists

### The Problem: Dual ID Bug

The previous architecture had a critical synchronization bug:

```
ExecutionTracker:  execution_id = uuid.uuid4()  # Generated one ID
MediaStorage:      run_id = uuid.uuid4()        # Generated different ID
```

This caused **complete desynchronization**:
- Execution history referenced run IDs that didn't exist in `exports/json/`
- Media files were stored under one UUID, but execution records pointed to another
- Frontend couldn't reliably query run status or retrieve media

**Evidence:** Found in `exec_20251104_185608_b2d140b6.json` where file paths referenced UUIDs that didn't exist on disk.

### The Solution: Unified Run ID

```python
# ONE unified run_id generated upfront
run_id = str(uuid.uuid4())

# Passed to ALL systems
tracker = ExecutionTracker(execution_id=run_id)
media_storage.create_run(run_id=run_id)
recorder = LivePipelineRecorder(run_id=run_id)
```

Now all systems use the **same UUID** for complete synchronization.

## Architecture

### File Structure

Each pipeline run creates a folder in `pipeline_runs/{run_id}/`:

```
pipeline_runs/528e5af9-59b3-4551-b101-27e13dd6e43e/
├── metadata.json          # Complete run metadata + state tracking
├── 01_input.txt          # User's original input
├── 02_translation.txt    # Translated text (if applicable)
├── 03_safety.json        # Safety check results
├── 04_interception.txt   # Main pipeline output
├── 05_safety_pre_output.json  # Pre-output safety check
└── 06_output_image.png   # Generated media (if applicable)
```

### Key Design Principles

1. **Numbered Filenames**: Sequential (01_, 02_, 03_...) showing execution order
2. **Immediate Writes**: Files written as entities appear (not retroactively)
3. **Self-Describing Metadata**: Single `metadata.json` contains complete state
4. **Real-Time State Tracking**: Current stage/step/progress for frontend polling
5. **Metadata Enrichment**: Each entity can include contextual metadata

## Core Components

### 1. LivePipelineRecorder Class

**Location:** `pipeline_recorder/recorder.py`

**Key Methods:**

```python
class LivePipelineRecorder:
    def __init__(self, run_id, config_name, execution_mode, safety_level,
                 user_id='anonymous', base_path=None):
        """Initialize recorder and create run folder with metadata.json"""

    def set_state(self, stage: int, step: str):
        """Update current pipeline state for frontend queries"""

    def save_entity(self, entity_type: str, content: Union[str, bytes, dict],
                   metadata: Optional[Dict] = None) -> str:
        """Save entity to disk immediately with numbered filename"""

    def save_error(self, stage: int, error_type: str, message: str,
                  details: Optional[Dict] = None) -> str:
        """Save error entity"""

    def get_status(self) -> Dict:
        """Get complete status (returns metadata.json)"""

    def get_entity_path(self, entity_type: str) -> Optional[Path]:
        """Get file path for specific entity type"""
```

**Singleton Management:**

```python
from pipeline_recorder import get_recorder, load_recorder

# Create or get existing recorder for a run
recorder = get_recorder(
    run_id=run_id,
    config_name='stillepost',
    execution_mode='eco',
    safety_level='kids'
)

# Load existing recorder (for API endpoints)
recorder = load_recorder(run_id)
```

### 2. Integration in Pipeline Routes

**Location:** `my_app/routes/schema_pipeline_routes.py`

**Key Integration Points:**

```python
# 1. Generate unified run_id BEFORE initializing any systems
run_id = str(uuid.uuid4())
logger.info(f"[RUN_ID] Generated unified run_id: {run_id}")

# 2. Pass to MediaStorage
run_metadata = asyncio.run(media_storage.create_run(..., run_id=run_id))

# 3. Initialize recorder
recorder = get_recorder(
    run_id=run_id,
    config_name=schema_name,
    execution_mode=execution_mode,
    safety_level=safety_level
)
recorder.set_state(0, "pipeline_starting")

# 4. Save entities at each stage
recorder.save_entity('input', input_text)
recorder.set_state(1, "translation_and_safety")

# Stage 1: Translation + Safety
recorder.save_entity('translation', translated_text)
recorder.save_entity('safety', {'safe': True, ...})

# Stage 2: Interception
recorder.set_state(2, "interception")
recorder.save_entity('interception', result.final_output, metadata={
    'config': schema_name,
    'iterations': 8,
    'model_used': 'mistral-nemo:latest',
    'backend_used': 'ollama'
})

# Stage 3: Pre-output Safety
recorder.set_state(3, "pre_output_safety")
recorder.save_entity('safety_pre_output', {...})

# Stage 4: Media Generation
recorder.set_state(4, "media_generation")
# Copy media file from media_storage to recorder folder
recorder.save_entity('output_image', media_bytes, metadata={
    'config': output_config_name,
    'filename': 'image.png'
})
```

### 3. API Endpoints

**Location:** `my_app/routes/pipeline_routes.py`

#### GET /api/pipeline/{run_id}/status

**Purpose:** Real-time status polling for frontend

**Response:**
```json
{
  "run_id": "528e5af9-59b3-4551-b101-27e13dd6e43e",
  "timestamp": "2025-11-04T20:12:37.568803",
  "config_name": "stillepost",
  "execution_mode": "eco",
  "safety_level": "kids",
  "user_id": "anonymous",
  "expected_outputs": ["input", "translation", "safety", "interception", "safety_pre_output", "output_image"],
  "current_state": {
    "stage": 2,
    "step": "interception",
    "progress": "4/6"
  },
  "completed_outputs": ["input", "translation", "safety", "interception"],
  "entities": [
    {
      "sequence": 1,
      "type": "input",
      "filename": "01_input.txt",
      "timestamp": "2025-11-04T20:12:37.569096",
      "metadata": {}
    },
    {
      "sequence": 4,
      "type": "interception",
      "filename": "04_interception.txt",
      "timestamp": "2025-11-04T20:12:54.094220",
      "metadata": {
        "config": "stillepost",
        "iterations": 8,
        "model_used": "mistral-nemo:latest",
        "backend_used": "ollama"
      }
    }
  ]
}
```

**Frontend Usage:**
```javascript
// Poll every second for status updates
setInterval(async () => {
    const status = await fetch(`/api/pipeline/${runId}/status`).then(r => r.json());

    // Update progress bar
    const [completed, total] = status.current_state.progress.split('/');
    progressBar.style.width = `${(completed/total)*100}%`;

    // Check for new entities
    status.entities.forEach(entity => {
        if (!displayedEntities.has(entity.type)) {
            displayEntity(entity);
            displayedEntities.add(entity.type);
        }
    });
}, 1000);
```

#### GET /api/pipeline/{run_id}/entity/{entity_type}

**Purpose:** Serve entity files to frontend

**Supported Entity Types:**
- `input` - User's original input text
- `translation` - Translated/processed text
- `safety` - Safety check results (JSON)
- `interception` - Main pipeline output text
- `safety_pre_output` - Pre-output safety check (JSON)
- `output_image` - Generated image (PNG, JPG, etc.)
- `output_audio` - Generated audio (MP3, WAV, etc.)
- `output_video` - Generated video (MP4, WebM, etc.)
- `error` - Error information (JSON)

**Response:** Direct file content with appropriate MIME type

**Frontend Usage:**
```javascript
// Display text entity
const inputText = await fetch(`/api/pipeline/${runId}/entity/input`).then(r => r.text());
document.getElementById('input-display').textContent = inputText;

// Display JSON entity
const safety = await fetch(`/api/pipeline/${runId}/entity/safety`).then(r => r.json());
console.log('Safety result:', safety);

// Display image entity
const imageUrl = `/api/pipeline/${runId}/entity/output_image`;
document.getElementById('result-image').src = imageUrl;
```

#### GET /api/pipeline/{run_id}/entities

**Purpose:** Discovery - list all available entities

**Response:**
```json
{
  "run_id": "528e5af9-59b3-4551-b101-27e13dd6e43e",
  "entity_count": 4,
  "entities": [
    {
      "sequence": 1,
      "type": "input",
      "filename": "01_input.txt",
      "timestamp": "2025-11-04T20:12:37.569096",
      "metadata": {},
      "url": "/api/pipeline/528e5af9.../entity/input"
    },
    ...
  ]
}
```

## Metadata.json Structure

The `metadata.json` file is the single source of truth for a pipeline run:

```json
{
  "run_id": "528e5af9-59b3-4551-b101-27e13dd6e43e",
  "timestamp": "2025-11-04T20:12:37.568803",
  "config_name": "stillepost",
  "execution_mode": "eco",
  "safety_level": "kids",
  "user_id": "anonymous",

  "expected_outputs": [
    "input",
    "translation",
    "safety",
    "interception",
    "safety_pre_output",
    "output_image"
  ],

  "current_state": {
    "stage": 2,
    "step": "interception",
    "progress": "4/6"
  },

  "completed_outputs": [
    "input",
    "translation",
    "safety",
    "interception"
  ],

  "entities": [
    {
      "sequence": 1,
      "type": "input",
      "filename": "01_input.txt",
      "timestamp": "2025-11-04T20:12:37.569096",
      "metadata": {}
    },
    {
      "sequence": 2,
      "type": "translation",
      "filename": "02_translation.txt",
      "timestamp": "2025-11-04T20:12:42.467344",
      "metadata": {}
    },
    {
      "sequence": 3,
      "type": "safety",
      "filename": "03_safety.json",
      "timestamp": "2025-11-04T20:12:42.468763",
      "metadata": {}
    },
    {
      "sequence": 4,
      "type": "interception",
      "filename": "04_interception.txt",
      "timestamp": "2025-11-04T20:12:54.094220",
      "metadata": {
        "config": "stillepost",
        "iterations": 8,
        "model_used": "mistral-nemo:latest",
        "backend_used": "ollama"
      }
    }
  ]
}
```

## Entity Types Reference

| Entity Type | Format | Stage | Description |
|-------------|--------|-------|-------------|
| `input` | .txt | 0 | User's original input text |
| `translation` | .txt | 1 | Translated/corrected text |
| `safety` | .json | 1 | Stage 1 safety check (§86a) |
| `interception` | .txt | 2 | Main pipeline output (transformed prompt) |
| `safety_pre_output` | .json | 3 | Pre-output safety check (media-specific) |
| `output_image` | .png/.jpg | 4 | Generated image |
| `output_audio` | .mp3/.wav | 4 | Generated audio/music |
| `output_video` | .mp4/.webm | 4 | Generated video |
| `error` | .json | Any | Error information |

## Stage Flow

The recorder tracks progression through 4 stages:

```
Stage 0: pipeline_starting
  ↓ save_entity('input')

Stage 1: translation_and_safety
  ↓ save_entity('translation')
  ↓ save_entity('safety')

Stage 2: interception (main pipeline)
  ↓ save_entity('interception')

Stage 3: pre_output_safety (per output type)
  ↓ save_entity('safety_pre_output')

Stage 4: media_generation (per output config)
  ↓ save_entity('output_image' / 'output_audio' / 'output_video')
```

**State Updates:**
```python
recorder.set_state(stage=1, step="translation_and_safety")
# Updates current_state in metadata.json:
# {"stage": 1, "step": "translation_and_safety", "progress": "0/6"}
```

## Error Handling

When errors occur at any stage, save error entities:

```python
# Safety blocked at Stage 1
if not is_safe:
    recorder.save_error(
        stage=1,
        error_type='safety_blocked',
        message='Content violates §86a',
        details={'codes': ['§86a']}
    )
    # Still save what we have
    recorder.save_entity('translation', translated_text)
    recorder.save_entity('safety', {'safe': False, ...})
```

Error entities are saved with sequence numbers and appear in the entities array, making it easy to reconstruct what happened during execution.

## Testing

### Manual Testing

```bash
# 1. Start server
cd /home/joerissen/ai/ai4artsed_webserver/devserver
python3 server.py

# 2. Execute a pipeline
curl -X POST http://localhost:17801/api/schema/pipeline/execute \
  -H "Content-Type: application/json" \
  -d '{"schema":"stillepost","input_text":"Test input","execution_mode":"eco","safety_level":"kids"}'

# Response includes run_id:
# {"status": "success", "run_id": "528e5af9-59b3-4551-b101-27e13dd6e43e", ...}

# 3. Query status
curl http://localhost:17801/api/pipeline/528e5af9-59b3-4551-b101-27e13dd6e43e/status | jq '.'

# 4. Get specific entity
curl http://localhost:17801/api/pipeline/528e5af9-59b3-4551-b101-27e13dd6e43e/entity/input

# 5. List all entities
curl http://localhost:17801/api/pipeline/528e5af9-59b3-4551-b101-27e13dd6e43e/entities | jq '.'

# 6. Check the files on disk
ls -la pipeline_runs/528e5af9-59b3-4551-b101-27e13dd6e43e/
cat pipeline_runs/528e5af9-59b3-4551-b101-27e13dd6e43e/metadata.json | jq '.'
```

### Unit Tests

**Location:** `test_recorder.py`

```bash
python3 test_recorder.py
```

Tests cover:
- Basic recording functionality
- Singleton management (get_recorder)
- Entity path lookup
- Metadata updates
- State tracking

## Migration Notes

### Current Status (Session 29)

The LivePipelineRecorder runs **in parallel** with the old systems (ExecutionTracker + MediaStorage):

- ✅ **Unified run_id** generated upfront
- ✅ **All systems use same UUID** (synchronized)
- ✅ **LivePipelineRecorder fully functional** (all stages, all entity types)
- ✅ **API endpoints implemented and tested**
- ⏳ **Old systems still active** (for reference/comparison)

### Next Steps

After thorough testing and frontend integration:

1. **Remove ExecutionTracker** - No longer needed, recorder handles all tracking
2. **Remove MediaStorage metadata** - Recorder's metadata.json is the source of truth
3. **Keep MediaStorage file operations** - Still need actual media file storage in `exports/json/`
4. **Update frontend** - Use new `/api/pipeline/*` endpoints for polling and entity display

### Benefits of New System

✅ **Single Source of Truth**: One metadata.json per run
✅ **Real-Time Updates**: Immediate file writes, no retroactive reconstruction
✅ **Complete Synchronization**: One UUID everywhere
✅ **Transparent State**: Frontend can poll progress in real-time
✅ **Metadata Enrichment**: Context preserved for each entity
✅ **Simpler Architecture**: Fewer moving parts, clearer data flow

## Related Documentation

- **Root Cause Analysis:** `docs/SESSION_29_ROOT_CAUSE_ANALYSIS.md`
- **Design Document:** `docs/SESSION_29_LIVE_RECORDER_DESIGN.md`
- **Session Handover:** `docs/SESSION_29_HANDOVER.md` (if exists)
- **API Reference:** `my_app/routes/pipeline_routes.py` (inline documentation)

## Troubleshooting

### Run folder not created

**Symptom:** `pipeline_runs/{run_id}/` directory doesn't exist

**Cause:** Recorder not initialized or permissions issue

**Fix:**
```python
# Ensure recorder is initialized in schema_pipeline_routes.py
recorder = get_recorder(run_id=run_id, ...)
logger.info(f"[RECORDER] Initialized for run {run_id}")
```

### Entities not appearing

**Symptom:** `/api/pipeline/{run_id}/status` returns empty entities array

**Cause:** `recorder.save_entity()` not called at pipeline stages

**Fix:** Check that all entity save calls are present in `schema_pipeline_routes.py`:
- Line 225: save_entity('input')
- Line 280: save_entity('translation'), save_entity('safety')
- Line 355: save_entity('interception')
- Line 490: save_entity('safety_pre_output')
- Line 565: save_entity('output_image')

### Metadata enrichment missing

**Symptom:** Entity metadata dict is empty when it should have values

**Cause:** Not passing metadata parameter to save_entity()

**Fix:**
```python
# ❌ Wrong - no metadata
recorder.save_entity('interception', output_text)

# ✅ Correct - with metadata
recorder.save_entity('interception', output_text, metadata={
    'config': schema_name,
    'iterations': 8,
    'model_used': 'mistral-nemo:latest'
})
```

### API endpoints return 404

**Symptom:** `/api/pipeline/{run_id}/status` returns 404 Not Found

**Cause:** Blueprint not registered or run_id doesn't exist

**Fix:**
1. Check blueprint registration in `my_app/__init__.py`:
   ```python
   from my_app.routes.pipeline_routes import pipeline_bp
   app.register_blueprint(pipeline_bp)
   ```
2. Verify run_id exists:
   ```bash
   ls pipeline_runs/{run_id}/
   ```

---

**Last Updated:** 2025-11-04
**Maintained By:** Session 29 Implementation
**Version:** 1.0
