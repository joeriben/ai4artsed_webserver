# DevServer Documentation

This directory contains technical documentation for the AI4ArtsEd DevServer implementation.

## Quick Start

**New to this codebase?** Start here:

1. **Pipeline Execution Tracking (NEW - Session 29)**
   - [`LIVE_PIPELINE_RECORDER.md`](./LIVE_PIPELINE_RECORDER.md) - Unified pipeline execution tracking system
   - Replaces the broken dual-ID architecture
   - Provides real-time status API for frontend

2. **Media Storage**
   - [`UNIFIED_MEDIA_STORAGE.md`](./UNIFIED_MEDIA_STORAGE.md) - Unified media storage system
   - All media files in one location regardless of backend

3. **Session Summaries**
   - [`SESSION_27_SUMMARY.md`](./SESSION_27_SUMMARY.md) - Previous session work

## System Overview

The DevServer implements a template-based pipeline system for AI-generated art with pedagogical prompt interception.

### Key Components

```
User Input
    ↓
[Stage 1: Translation + Safety]  ← GPT-OSS (local LLM)
    ↓
[Stage 2: Interception]          ← Main pipeline (prompt transformation)
    ↓
[Stage 3: Pre-Output Safety]    ← Llama-Guard (local)
    ↓
[Stage 4: Media Generation]      ← ComfyUI/OpenRouter
    ↓
Output (Image/Audio/Video)
```

### Architecture Layers

1. **Chunks** (`schemas/chunks/*.json`)
   - Primitive operations (text transformation, media generation)
   - Templates with placeholders

2. **Pipelines** (`schemas/pipelines/*.json`)
   - Orchestration by INPUT type (not output type)
   - Backend-agnostic

3. **Configs** (`schemas/configs/*.json`)
   - Content and instructions
   - Metadata for model selection

## Key Features

### LivePipelineRecorder (Session 29)

**Problem Solved:** The old system used two different UUIDs (ExecutionTracker + MediaStorage), causing complete desynchronization where execution history referenced non-existent media files.

**Solution:** ONE unified `run_id` passed to all systems, with immediate file writes and real-time state tracking.

**File Structure:**
```
pipeline_runs/{run_id}/
├── metadata.json         # Single source of truth
├── 01_input.txt         # User input
├── 02_translation.txt   # Translated text
├── 03_safety.json       # Safety results
├── 04_interception.txt  # Transformed prompt
├── 05_safety_pre_output.json
└── 06_output_image.png  # Generated media
```

**API Endpoints:**
- `GET /api/pipeline/{run_id}/status` - Real-time status polling
- `GET /api/pipeline/{run_id}/entity/{type}` - Serve entity files
- `GET /api/pipeline/{run_id}/entities` - List all entities

See [`LIVE_PIPELINE_RECORDER.md`](./LIVE_PIPELINE_RECORDER.md) for complete documentation.

### Unified Media Storage (Session 27)

All media files stored in `exports/json/{run_id}/` regardless of backend:
- Local ComfyUI generations
- Cloud OpenRouter generations
- All accessible via `/api/media/*` endpoints

See [`UNIFIED_MEDIA_STORAGE.md`](./UNIFIED_MEDIA_STORAGE.md) for details.

## Current Status

### ✅ Completed

- **Unified run_id generation** - All systems synchronized
- **LivePipelineRecorder** - Fully functional with all stages
- **API endpoints** - Status polling and entity serving working
- **Entity tracking** - All pipeline stages save entities
- **Metadata enrichment** - Context preserved for each entity

### ⏳ In Progress

- **Frontend integration** - Use new `/api/pipeline/*` endpoints
- **Old system removal** - After thorough testing, remove ExecutionTracker

### 📋 Future Work

- Pre-Interception 4-Stage system (design complete in other docs)
- Frontend real-time progress display
- Media generation entity tracking (Stage 4)

## Testing

### Quick Test

```bash
# 1. Start server
cd /home/joerissen/ai/ai4artsed_webserver/devserver
python3 server.py

# 2. Execute pipeline
curl -X POST http://localhost:17801/api/schema/pipeline/execute \
  -H "Content-Type: application/json" \
  -d '{"schema":"stillepost","input_text":"Test","execution_mode":"eco","safety_level":"kids"}'

# 3. Check status (replace run_id from response)
curl http://localhost:17801/api/pipeline/{run_id}/status | jq '.'

# 4. Get entity
curl http://localhost:17801/api/pipeline/{run_id}/entity/input
```

### Unit Tests

```bash
# Test recorder
python3 test_recorder.py

# Test architecture
python3 test_refactored_system.py

# Test pipeline execution
python3 test_pipeline_execution.py
```

## Common Tasks

### View Pipeline Run

```bash
# List all runs
ls -lt pipeline_runs/

# View specific run
cd pipeline_runs/{run_id}/
cat metadata.json | jq '.'
ls -la  # See all entity files
```

### Debug Pipeline Execution

```bash
# Check server logs
tail -f /tmp/devserver.log

# Check specific entity
cat pipeline_runs/{run_id}/04_interception.txt

# Check safety results
cat pipeline_runs/{run_id}/03_safety.json | jq '.'
```

### Query Run Status via API

```bash
# Get complete status
curl http://localhost:17801/api/pipeline/{run_id}/status | jq '.current_state'

# List completed entities
curl http://localhost:17801/api/pipeline/{run_id}/entities | jq '.entities[].type'

# Get specific entity
curl http://localhost:17801/api/pipeline/{run_id}/entity/translation
```

## File Locations

### Source Code
- **Recorder**: `pipeline_recorder/recorder.py` (core implementation)
- **API Routes**: `my_app/routes/pipeline_routes.py` (endpoints)
- **Integration**: `my_app/routes/schema_pipeline_routes.py` (entity saves)

### Data Directories
- **Pipeline Runs**: `pipeline_runs/{run_id}/` (recorder output)
- **Media Storage**: `exports/json/{run_id}/` (actual media files)
- **Execution History**: `exports/pipeline_runs/` (old system, will be removed)

### Configuration
- **Chunks**: `schemas/chunks/*.json`
- **Pipelines**: `schemas/pipelines/*.json`
- **Configs**: `schemas/configs/*.json`

## Troubleshooting

See individual documentation files for detailed troubleshooting:
- [`LIVE_PIPELINE_RECORDER.md`](./LIVE_PIPELINE_RECORDER.md#troubleshooting) - Recorder issues
- [`UNIFIED_MEDIA_STORAGE.md`](./UNIFIED_MEDIA_STORAGE.md) - Media storage issues

## Related Documentation

### Session Documents
- **Session 27**: [`SESSION_27_SUMMARY.md`](./SESSION_27_SUMMARY.md)
- **Session 29**: Design documents in `docs/` (SESSION_29_*)

### Code Documentation
- Inline documentation in source files
- API endpoint docstrings in `my_app/routes/pipeline_routes.py`

---

**Last Updated:** 2025-11-04 (Session 29)
**Maintained By:** Active development sessions
