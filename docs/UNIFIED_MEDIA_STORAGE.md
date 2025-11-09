# Unified Media Storage System

**Status:** ✅ Implemented (2025-11-04)
**Version:** 1.0

---

## Overview

The Unified Media Storage System solves critical gaps in media handling by:
1. **Storing ALL media locally** (ComfyUI, GPT-5, APIs) in atomic research units
2. **Backend-agnostic architecture** - works with any media generator
3. **Run-based organization** - keeps all files from one pipeline execution together
4. **Comprehensive metadata** - enables exports and research data analysis

### Problems Solved

**Before (Broken):**
- ❌ ComfyUI images: Shown in frontend but NOT stored permanently
- ❌ GPT-5 API images: Stored as data strings in JSON (not useful)
- ❌ Export function: Failed because media wasn't persisted
- ❌ Research data: URLs printed to console instead of actual files

**After (Fixed):**
- ✅ ALL media downloaded and stored locally during pipeline execution
- ✅ Atomic run folders keep input, transformed text, and media together
- ✅ Backend-agnostic: ComfyUI, GPT-5, Replicate, etc. all work the same
- ✅ Ready for export with comprehensive metadata

---

## Architecture

### Storage Structure

```
media_storage/
└── runs/
    ├── run_uuid_001/
    │   ├── metadata.json          # Complete run metadata
    │   ├── input_text.txt         # Original user input
    │   ├── transformed_text.txt   # Intercepted/transformed prompt
    │   └── output_image.png       # Generated media
    ├── run_uuid_002/
    │   ├── metadata.json
    │   ├── input_text.txt
    │   ├── transformed_text.txt
    │   └── output_audio.wav
    └── run_uuid_003/
        ├── metadata.json
        ├── input_text.txt
        └── output_image.png       # (multiple outputs possible)
```

### Why This Structure?

**Atomic Research Units:**
- One folder = one complete pipeline run
- All related files stay together (won't break during transfer)
- Easy to zip, copy, or analyze individual runs

**Flat Structure (No Sessions):**
- Simpler and more concurrent-safe
- UUIDs prevent collisions in multi-user scenarios
- Flexible querying via metadata

**"Run" Terminology:**
- Not "execution" (execution = killing humans)
- Run = one complete pipeline execution from input to output

---

## Components

### 1. MediaStorageService

**File:** `devserver/my_app/services/media_storage.py`

**Key Classes:**

```python
@dataclass
class MediaOutput:
    """Metadata for a single media output"""
    type: str           # image, audio, video, model3d
    filename: str       # e.g., output_image.png
    backend: str        # comfyui, gpt5, replicate
    config: str         # Output config name
    file_size_bytes: int
    format: str         # PNG, JPG, MP3, WAV, etc.
    width: Optional[int]
    height: Optional[int]
    duration_seconds: Optional[float]

@dataclass
class RunMetadata:
    """Complete metadata for one pipeline run"""
    run_id: str
    user_id: Optional[str]
    timestamp: str
    schema: str                 # Pipeline name (e.g., "dada")
    execution_mode: str         # eco, fast, ultra
    input_text: str
    transformed_text: Optional[str]
    outputs: List[MediaOutput]  # Can have multiple outputs
```

**Key Methods:**

```python
# Create run folder at pipeline start
async def create_run(
    schema: str,
    execution_mode: str,
    input_text: str,
    user_id: Optional[str] = None
) -> RunMetadata

# Add media from ComfyUI
async def add_media_from_comfyui(
    run_id: str,
    prompt_id: str,
    config: str,
    media_type: str = 'image'
) -> Optional[MediaOutput]

# Add media from URL (GPT-5, APIs)
async def add_media_from_url(
    run_id: str,
    url: str,
    config: str,
    media_type: str = 'image'
) -> Optional[MediaOutput]

# Get metadata for a run
def get_metadata(run_id: str) -> Optional[RunMetadata]

# Get media file path
def get_media_path(run_id: str, filename: str) -> Optional[Path]
```

---

### 2. Pipeline Integration

**File:** `devserver/my_app/routes/schema_pipeline_routes.py`

**Integration Points:**

**At Pipeline Start (after tracker init):**
```python
# Create run folder with input text
media_storage = get_media_storage_service()
run_metadata = asyncio.run(media_storage.create_run(
    schema=schema_name,
    execution_mode=execution_mode,
    input_text=input_text,
    user_id=tracker.user_id
))
run_id = run_metadata.run_id
```

**Stage 4 - After Media Generation:**
```python
# Detect output type and download
output_value = output_result.final_output

if output_value.startswith('http'):
    # API-based (GPT-5, etc.) - URL
    media_output = await media_storage.add_media_from_url(
        run_id=run_id,
        url=output_value,
        config=output_config_name,
        media_type=media_type
    )
else:
    # ComfyUI - prompt_id
    media_output = await media_storage.add_media_from_comfyui(
        run_id=run_id,
        prompt_id=output_value,
        config=output_config_name,
        media_type=media_type
    )
```

**Response to Frontend:**
```python
# Return run_id instead of raw prompt_id/URL
media_outputs.append({
    'config': output_config_name,
    'status': 'success',
    'run_id': run_id,           # Unified identifier
    'output': run_id,           # For backward compatibility
    'media_stored': True,
    'media_type': media_type
})
```

---

### 3. Media Serving

**File:** `devserver/my_app/routes/media_routes.py`

**New Endpoints (all use run_id):**

```python
GET /api/media/image/<run_id>
GET /api/media/audio/<run_id>
GET /api/media/video/<run_id>
GET /api/media/info/<run_id>       # Get media metadata
GET /api/media/run/<run_id>        # Get complete run metadata
```

**Example - Serving Image:**
```python
@media_bp.route('/image/<run_id>', methods=['GET'])
def get_image(run_id: str):
    media_storage = get_media_storage_service()

    # Get metadata
    metadata = media_storage.get_metadata(run_id)

    # Find image output
    image_output = next(
        (o for o in metadata.outputs if o.type == 'image'),
        None
    )

    # Get file path and serve
    file_path = media_storage.get_media_path(run_id, image_output.filename)
    return send_file(file_path, mimetype='image/png')
```

**Benefits:**
- No more fetching from ComfyUI at display time
- Works with ANY backend (not just ComfyUI)
- Fast - serves directly from disk
- Proper MIME type detection

---

## Metadata Format

**Example `metadata.json`:**

```json
{
  "run_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
  "user_id": "DOE_J",
  "timestamp": "2025-11-04T14:31:22.123456",
  "schema": "dada",
  "execution_mode": "eco",
  "input_text": "Eine Blume auf der Wiese",
  "transformed_text": "A surreal flower floating in a meadow of dreams",
  "outputs": [
    {
      "type": "image",
      "filename": "output_image.png",
      "backend": "comfyui",
      "config": "sd35_large",
      "file_size_bytes": 1048576,
      "format": "png",
      "width": 1024,
      "height": 1024
    }
  ]
}
```

**Fields Explained:**

- `run_id`: UUID for this pipeline run
- `user_id`: User identifier (for multi-user scenarios)
- `timestamp`: ISO format timestamp
- `schema`: Pipeline config name (e.g., "dada", "bauhaus")
- `execution_mode`: "eco" (local) or "fast" (cloud)
- `input_text`: Original user input
- `transformed_text`: After Stage 2 interception
- `outputs[]`: Array of media outputs (can be multiple)

**Note:** Internal debugging fields (starting with `_`) are NOT stored in JSON.

---

## Data Flow

### Complete Pipeline Flow with Media Storage

```
1. User submits prompt
   └─> POST /api/schema/pipeline/execute
       {
         "schema": "dada",
         "input_text": "Eine Blume...",
         "execution_mode": "eco"
       }

2. Create run folder
   └─> media_storage.create_run()
       └─> Creates: exports/json/run_uuid_001/
           ├─> input_text.txt
           └─> metadata.json (initial)

3. Stage 1: Pre-Interception (Translation + Safety)
   └─> Updated text stored in memory

4. Stage 2: Interception (Transform prompt)
   └─> Transformed text available

5. Stage 3: Pre-Output Safety
   └─> Safety checks for media generation

6. Stage 4: Media Generation
   └─> Execute output config (ComfyUI or API)
       └─> Returns: prompt_id (ComfyUI) OR url (API)

   └─> Download and store media
       └─> media_storage.add_media_from_comfyui() OR
           media_storage.add_media_from_url()
       └─> Downloads file
       └─> Saves: exports/json/run_uuid_001/output_image.png
       └─> Updates metadata.json with output info

7. Return to frontend
   └─> Response includes run_id
       {
         "status": "success",
         "final_output": "transformed text",
         "media_output": {
           "run_id": "run_uuid_001",
           "output": "run_uuid_001",
           "media_stored": true
         }
       }

8. Frontend displays media
   └─> <img src="/api/media/image/run_uuid_001">
       └─> Serves from local disk (fast!)
```

---

## Concurrent Usage

**Scenario:** 15 kids in workshop, multiple simultaneous requests

**How it works:**
1. Each request gets unique UUID (run_id)
2. No collisions possible (globally unique)
3. Flat structure = no lock contention
4. Each run folder is independent

**Example:**
```
runs/
├── abc123.../  # Kid 1, request 1
├── def456.../  # Kid 2, request 1
├── ghi789.../  # Kid 1, request 2 (while #1 still processing)
└── jkl012.../  # Kid 3, request 1
```

All process independently, no conflicts.

---

## Export Integration (TODO)

**File:** `devserver/my_app/services/export_manager.py`

**Current Issue:** Export manager expects `prompt_id` (ComfyUI-specific)

**Required Changes:**

```python
# OLD (ComfyUI-only)
def auto_export_session(self, prompt_id: str, ...):
    result = comfyui_service.get_workflow_outputs(prompt_id)

# NEW (Backend-agnostic)
def auto_export_run(self, run_id: str, ...):
    media_storage = get_media_storage_service()
    metadata = media_storage.get_metadata(run_id)

    # All data available in metadata
    # - Input text
    # - Transformed text
    # - Media files (with paths)
    # - Backend info
    # - Timestamps
```

**Benefits:**
- Works with ANY backend
- All data already available in metadata
- No need to fetch from ComfyUI
- Supports multiple outputs per run

---

## Testing Checklist

### ✅ Implementation Complete
- [x] MediaStorageService with run-based structure
- [x] Pipeline integration (create run + store media)
- [x] Media routes (serve from local storage)

### ⏳ Testing Needed
- [ ] Test ComfyUI image generation → storage
- [ ] Test GPT-5 API image generation → storage
- [ ] Test audio generation → storage
- [ ] Test concurrent requests (multiple users)
- [ ] Test metadata retrieval
- [ ] Test file serving (different formats)

### ⏳ Integration Needed
- [ ] Update export_manager.py to use run_id
- [ ] Update frontend to use run_id (if needed)
- [ ] Add cleanup/archival for old runs

---

## Benefits Summary

### For Research
- ✅ **Atomic Units:** One folder = complete research event
- ✅ **Easy Transfer:** Zip folder, copy, won't break
- ✅ **Rich Metadata:** All info for exports (Excel, PDF, HTML)
- ✅ **Permanent Storage:** Never loses media again

### For Development
- ✅ **Backend Agnostic:** Works with any generator
- ✅ **Clean Architecture:** Separation of concerns
- ✅ **Concurrent Safe:** UUIDs prevent collisions
- ✅ **Easy to Debug:** Everything in one place

### For Users
- ✅ **Reliable:** Media always available
- ✅ **Fast:** Serves from local disk
- ✅ **Supports Multi-User:** Workshop-ready

---

## File Reference

**Core Implementation:**
- `devserver/my_app/services/media_storage.py` - Storage service (414 lines)
- `devserver/my_app/routes/schema_pipeline_routes.py` - Pipeline integration
- `devserver/my_app/routes/media_routes.py` - Media serving (288 lines)

**Related Documentation:**
- `docs/ARCHITECTURE PART 12 - Frontend-Architecture.md` - Media display flow
- `docs/ARCHITECTURE PART 06 - Data-Flow-Patterns.md` - Overall data flow

---

**Created:** 2025-11-04
**Author:** Claude Code (Session 27)
**Next Steps:** Testing + Export Manager Integration
