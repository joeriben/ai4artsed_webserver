# Session 29: Media Generation Architecture Refactoring Plan

**Date:** 2025-11-04
**Status:** 📋 DESIGN DOCUMENT - Not Yet Implemented
**Priority:** Medium (Current band-aid fix works correctly)

---

## Executive Summary

This document outlines a plan to refactor media generation architecture from **polling-based** to **blocking execution**, eliminating the current "band-aid fix" in `media_storage.py`.

**Current Problem:** Separation of concerns violation - output chunks submit workflows and return immediately, forcing `media_storage.py` to poll for completion.

**Proposed Solution:** Make output chunks own the complete lifecycle - submit, wait, and return actual media bytes.

**User's Insight:**
> "if timing is a problem, why not let that output chunk trigger the storage execution?"

---

## Current Architecture (The Problem)

### Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ schema_pipeline_routes.py (Stage 4: Media Generation)      │
│                                                             │
│ 1. Execute output config (e.g., sd35_large)               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ pipeline_executor.py                                        │
│                                                             │
│ 2. Load pipeline + chunks                                  │
│ 3. Execute chunk via backend_router                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ backend_router.py (ComfyUI backend)                        │
│                                                             │
│ 4. Build workflow from output_chunk template               │
│ 5. Submit to ComfyUI via comfyui_service                  │
│ 6. ⚠️ RETURNS IMMEDIATELY with prompt_id                   │
└────────────────────┬────────────────────────────────────────┘
                     │ prompt_id
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ schema_pipeline_routes.py (Stage 4 continued)              │
│                                                             │
│ 7. Receives prompt_id from pipeline execution              │
│ 8. Calls media_storage.add_media_from_comfyui(prompt_id)  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ media_storage.py                                            │
│                                                             │
│ 9. ⚠️ BAND-AID FIX: wait_for_completion(prompt_id)        │
│    - Polls every 2 seconds                                 │
│    - Waits for ComfyUI to finish workflow                 │
│ 10. Downloads media bytes from ComfyUI                     │
│ 11. Saves to run folder                                    │
└─────────────────────────────────────────────────────────────┘
```

### Problems with Current Architecture

**1. Separation of Concerns Violation**
- Backend router submits workflow but doesn't wait for result
- Route handler becomes responsible for completion polling
- Business logic split across multiple layers

**2. Tight Coupling to media_storage.py**
- Polling logic embedded in storage service
- Storage service shouldn't know about ComfyUI workflows
- Hard to test in isolation

**3. Unnecessary Complexity**
- Extra layer of polling in media_storage.py
- Two separate calls: submit workflow, then download
- More points of failure

**4. Poor Error Handling**
- If route handler crashes between submit and download, orphaned workflow
- No way to resume or recover incomplete downloads
- Hard to track which workflows are in progress

**5. Scalability Issues**
- Blocking the entire route handler while polling
- Can't handle multiple concurrent requests efficiently
- No queue or worker pool pattern

---

## Proposed Architecture (Option 1: Blocking Execution)

### Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ schema_pipeline_routes.py (Stage 4: Media Generation)      │
│                                                             │
│ 1. Execute output config (e.g., sd35_large)               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ pipeline_executor.py                                        │
│                                                             │
│ 2. Load pipeline + chunks                                  │
│ 3. Execute chunk via backend_router                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ backend_router.py (ComfyUI backend)                        │
│                                                             │
│ 4. Build workflow from output_chunk template               │
│ 5. Submit to ComfyUI via comfyui_service                  │
│ 6. ✅ WAIT for completion (polling internally)             │
│ 7. ✅ Download media bytes from ComfyUI                    │
│ 8. ✅ RETURNS media bytes (not just prompt_id)             │
└────────────────────┬────────────────────────────────────────┘
                     │ media_bytes + metadata
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ schema_pipeline_routes.py (Stage 4 continued)              │
│                                                             │
│ 9. Receives actual media bytes from pipeline execution     │
│ 10. Calls media_storage.add_media_from_bytes(bytes)       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ media_storage.py                                            │
│                                                             │
│ 11. ✅ SIMPLE: Just save bytes to file                     │
│     - No polling needed                                    │
│     - No ComfyUI knowledge required                        │
│     - Pure storage service                                 │
└─────────────────────────────────────────────────────────────┘
```

### Benefits of Proposed Architecture

**1. Proper Separation of Concerns**
- Backend router owns complete workflow lifecycle
- Media storage is pure storage (no polling logic)
- Each layer has single responsibility

**2. Loose Coupling**
- `media_storage.py` knows nothing about ComfyUI
- Can replace ComfyUI with SwarmUI, Replicate, etc.
- Backend router handles all backend-specific logic

**3. Simplified Code**
- Remove polling logic from media_storage.py
- Single call: submit + wait + download in one place
- Fewer points of failure

**4. Better Error Handling**
- If workflow fails, error bubbles up immediately
- No orphaned workflows
- Clearer error messages

**5. Future Scalability**
- Can later refactor to async worker pool
- Foundation for event-driven architecture
- Can add caching layer easily

---

## Implementation Plan

### Phase 1: Backend Router Refactoring

**File:** `devserver/schemas/engine/backend_router.py`

**Current Code (lines ~150-180):**
```python
async def _execute_comfyui_chunk(self, chunk_data, execution_context):
    """Execute output chunk on ComfyUI backend"""

    # Build workflow
    workflow = self._build_comfyui_workflow(chunk_data, execution_context)

    # Submit to ComfyUI
    from my_app.services.comfyui_service import submit_workflow
    prompt_id = await submit_workflow(workflow)

    # ⚠️ RETURNS IMMEDIATELY
    return {
        'type': 'media',
        'backend': 'comfyui',
        'prompt_id': prompt_id  # Just ID, not actual media
    }
```

**Proposed Code:**
```python
async def _execute_comfyui_chunk(self, chunk_data, execution_context):
    """Execute output chunk on ComfyUI backend - BLOCKING"""

    # Get ComfyUI client
    from my_app.services.comfyui_client import get_comfyui_client
    client = get_comfyui_client()

    # Build workflow
    workflow = self._build_comfyui_workflow(chunk_data, execution_context)

    # Submit workflow
    prompt_id = await client.submit_workflow(workflow)
    logger.info(f"[BACKEND] ComfyUI workflow submitted: {prompt_id}")

    # ✅ WAIT for completion (NEW)
    logger.info(f"[BACKEND] Waiting for ComfyUI workflow completion: {prompt_id}")
    history = await client.wait_for_completion(prompt_id, timeout=300)

    # ✅ DOWNLOAD media (NEW)
    media_type = chunk_data.get('media_type', 'image')

    if media_type == 'image':
        files = await client.get_generated_images(history[prompt_id])
    elif media_type in ['audio', 'music']:
        files = await client.get_generated_audio(history[prompt_id])
    else:
        raise ValueError(f"Unsupported media type: {media_type}")

    if not files:
        raise RuntimeError(f"No {media_type} files generated by ComfyUI")

    # Download first file
    first_file = files[0]
    media_bytes = await client.get_image(
        filename=first_file['filename'],
        subfolder=first_file.get('subfolder', ''),
        folder_type=first_file.get('type', 'output')
    )

    if not media_bytes:
        raise RuntimeError(f"Failed to download {media_type} from ComfyUI")

    logger.info(f"[BACKEND] ComfyUI media downloaded: {len(media_bytes)} bytes")

    # ✅ RETURN actual media (NEW)
    return {
        'type': 'media',
        'backend': 'comfyui',
        'media_type': media_type,
        'media_bytes': media_bytes,  # Actual media data
        'media_format': first_file.get('format', 'png'),
        'prompt_id': prompt_id  # Keep for debugging/tracking
    }
```

**Key Changes:**
1. Import `get_comfyui_client()` instead of just `submit_workflow()`
2. Call `wait_for_completion()` after submission
3. Download media bytes using `get_generated_images()` or `get_generated_audio()`
4. Return actual `media_bytes` instead of just `prompt_id`

---

### Phase 2: Route Handler Simplification

**File:** `devserver/my_app/routes/schema_pipeline_routes.py`

**Current Code (lines ~150-180):**
```python
# Stage 4: Media Generation
for output_config_name in output_requests:
    logger.info(f"[4-STAGE] Stage 4: Executing output config '{output_config_name}'")
    recorder.update_state(stage=4, step='media_generation', progress=f'{current_entity_count}/6')

    # Execute output config
    output_result = await executor.execute_pipeline(
        config_name=output_config_name,
        input_text=interception_output,
        execution_mode=execution_mode
    )

    # ⚠️ POLLING IN MEDIA_STORAGE (OLD)
    if output_result.status == PipelineStatus.COMPLETED:
        prompt_id = output_result.media_output.get('output')
        if prompt_id:
            media_output = await media_storage.add_media_from_comfyui(
                run_id=run_id,
                prompt_id=prompt_id,  # Just ID
                config=output_config_name,
                media_type='image'
            )
```

**Proposed Code:**
```python
# Stage 4: Media Generation
for output_config_name in output_requests:
    logger.info(f"[4-STAGE] Stage 4: Executing output config '{output_config_name}'")
    recorder.update_state(stage=4, step='media_generation', progress=f'{current_entity_count}/6')

    # Execute output config (NOW BLOCKING, RETURNS MEDIA BYTES)
    output_result = await executor.execute_pipeline(
        config_name=output_config_name,
        input_text=interception_output,
        execution_mode=execution_mode
    )

    # ✅ SIMPLE STORAGE (NEW)
    if output_result.status == PipelineStatus.COMPLETED:
        media_data = output_result.media_output

        if media_data and 'media_bytes' in media_data:
            # Add media directly from bytes (no polling needed)
            media_output = await media_storage.add_media_from_bytes(
                run_id=run_id,
                data=media_data['media_bytes'],
                media_type=media_data.get('media_type', 'image'),
                backend='comfyui',
                config=output_config_name,
                file_format=media_data.get('media_format', 'png')
            )
```

**Key Changes:**
1. Remove `prompt_id` extraction
2. Extract `media_bytes` from result
3. Call new `add_media_from_bytes()` method (no polling)

---

### Phase 3: Media Storage Simplification

**File:** `devserver/my_app/services/media_storage.py`

**Current Code (lines 188-254):**
```python
async def add_media_from_comfyui(
    self,
    run_id: str,
    prompt_id: str,
    config: str,
    media_type: str = 'image'
) -> Optional[MediaOutput]:
    """
    Download media from ComfyUI and add to run
    ⚠️ CONTAINS POLLING LOGIC (BAND-AID)
    """
    try:
        from my_app.services.comfyui_client import get_comfyui_client
        client = get_comfyui_client()

        # ⚠️ BAND-AID: Poll for completion
        logger.info(f"[MEDIA_STORAGE] Waiting for ComfyUI workflow completion: {prompt_id}")
        history = await client.wait_for_completion(prompt_id)

        # Get generated files
        if media_type == 'image':
            files = await client.get_generated_images(history[prompt_id])
        # ... more code ...

        # Download file
        file_data = await client.get_image(...)

        # Add to run
        return await self._add_media_to_run(...)

    except Exception as e:
        logger.error(f"Error adding ComfyUI media to run {run_id}: {e}")
        return None
```

**Proposed Code:**
```python
# ✅ DEPRECATE add_media_from_comfyui() - No longer needed
# Polling logic moves to backend_router.py where it belongs

async def add_media_from_bytes(
    self,
    run_id: str,
    data: bytes,
    media_type: str,
    backend: str,
    config: str,
    file_format: str = None
) -> Optional[MediaOutput]:
    """
    Add media to run from raw bytes - SIMPLE STORAGE

    Args:
        run_id: Run ID to add media to
        data: Raw media bytes (already downloaded)
        media_type: Type of media (image/audio/video)
        backend: Backend name (comfyui/gpt5/api)
        config: Output config name
        file_format: File format (png/jpg/wav/mp3) - auto-detected if not provided

    Returns:
        MediaOutput if successful, None otherwise
    """
    try:
        # Auto-detect format if not provided
        if not file_format:
            file_format = self._detect_format_from_data(data, media_type)

        # Simple storage - no ComfyUI knowledge needed
        return await self._add_media_to_run(
            run_id=run_id,
            data=data,
            media_type=media_type,
            backend=backend,
            config=config,
            source_type='bytes',
            source_data=f'[{len(data)} bytes]'
        )

    except Exception as e:
        logger.error(f"Error adding media from bytes to run {run_id}: {e}")
        return None
```

**Key Changes:**
1. Remove `add_media_from_comfyui()` method entirely
2. Simplify to `add_media_from_bytes()` - pure storage
3. No ComfyUI imports, no polling logic
4. Media storage becomes backend-agnostic

---

### Phase 4: Update LivePipelineRecorder Integration

**File:** `devserver/my_app/routes/schema_pipeline_routes.py`

**Update Stage 4 to save entity:**
```python
# Stage 4: Media Generation
if media_output:
    # Save entity to LivePipelineRecorder
    entity_filename = f"0{current_entity_count}_{media_output.type}.{media_output.format}"

    recorder.save_entity(
        entity_type=f'output_{media_output.type}',
        content=None,  # Binary file already saved by media_storage
        metadata={
            'config': output_config_name,
            'backend': 'comfyui',
            'format': media_output.format,
            'size_bytes': media_output.file_size_bytes,
            'width': media_output.width,
            'height': media_output.height
        },
        entity_path=media_storage.get_media_path(run_id, entity_filename)
    )

    logger.info(f"[4-STAGE] Stage 4 successful for {output_config_name}: media_stored=True")
else:
    logger.warning(f"[4-STAGE] Stage 4 failed for {output_config_name}: media_stored=False")
```

---

## Implementation Steps (Checklist)

### Prerequisites
- [ ] Read this entire design document
- [ ] Understand current architecture and its problems
- [ ] Review `comfyui_client.py` to ensure `wait_for_completion()` works correctly
- [ ] Create backup branch: `git checkout -b backup-before-media-refactor`

### Step 1: Backend Router (Core Change)
- [ ] Modify `backend_router.py` `_execute_comfyui_chunk()` method
- [ ] Add polling logic: `await client.wait_for_completion(prompt_id)`
- [ ] Add download logic: `await client.get_generated_images(history)`
- [ ] Return `media_bytes` instead of just `prompt_id`
- [ ] Add timeout handling (default 300 seconds)
- [ ] Add error logging for failed downloads

### Step 2: Media Storage (Simplification)
- [ ] Create new `add_media_from_bytes()` method
- [ ] Mark `add_media_from_comfyui()` as deprecated
- [ ] Remove ComfyUI imports from media_storage.py
- [ ] Update docstrings to reflect new architecture

### Step 3: Route Handler (Integration)
- [ ] Update `schema_pipeline_routes.py` Stage 4
- [ ] Change from `add_media_from_comfyui(prompt_id)` to `add_media_from_bytes(media_bytes)`
- [ ] Extract `media_bytes` from `output_result.media_output`
- [ ] Update error handling

### Step 4: Testing
- [ ] Unit test: `test_backend_router_comfyui_blocking()`
- [ ] Unit test: `test_media_storage_from_bytes()`
- [ ] Integration test: Execute dada pipeline end-to-end
- [ ] Integration test: Execute sd35_large pipeline
- [ ] Check all 6 entities created correctly
- [ ] Verify media file is valid (can be opened)

### Step 5: Validation
- [ ] Compare output with OLD system (should be identical)
- [ ] Check execution time (should be similar, maybe slightly faster)
- [ ] Test with multiple configs (dada, bauhaus, gpt5_image)
- [ ] Verify LivePipelineRecorder metadata

### Step 6: Cleanup
- [ ] Remove `add_media_from_comfyui()` method entirely
- [ ] Update `LIVE_PIPELINE_RECORDER.md` documentation
- [ ] Update `UNIFIED_MEDIA_STORAGE.md` documentation
- [ ] Create `SESSION_XX_MEDIA_REFACTOR.md` summary document

### Step 7: Commit
```bash
git add .
git commit -m "refactor: Make media generation blocking, remove polling from media_storage

Architectural improvement:
- Backend router now owns complete workflow lifecycle
- Waits for ComfyUI completion before returning
- Returns actual media bytes (not just prompt_id)
- Media storage simplified to pure storage service
- No more polling logic in media_storage.py

Benefits:
- Proper separation of concerns
- Loose coupling (media_storage knows nothing about ComfyUI)
- Simpler code, fewer points of failure
- Better error handling

Files changed:
- backend_router.py: Added blocking execution
- media_storage.py: Added add_media_from_bytes(), deprecated add_media_from_comfyui()
- schema_pipeline_routes.py: Updated Stage 4 integration

Test result: All entities created, media stored successfully
"
```

---

## Alternative: Event-Driven Architecture (Option 2)

**Status:** Future consideration, more complex

### Overview

Instead of blocking execution, use an event-driven async worker pool:

```
┌─────────────────────────────────────────────────────┐
│ backend_router.py                                   │
│                                                     │
│ 1. Submit workflow to ComfyUI                      │
│ 2. Emit event: WorkflowSubmitted(prompt_id)       │
│ 3. Return immediately (non-blocking)               │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ Event Bus / Message Queue                           │
│                                                     │
│ - RabbitMQ, Redis Pub/Sub, or asyncio.Queue       │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ Worker Pool (separate processes/threads)            │
│                                                     │
│ 1. Poll ComfyUI for workflow completion            │
│ 2. Download media when ready                       │
│ 3. Emit event: WorkflowCompleted(prompt_id, bytes) │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ Event Handler in schema_pipeline_routes.py          │
│                                                     │
│ 1. Listen for WorkflowCompleted events             │
│ 2. Call media_storage.add_media_from_bytes()       │
│ 3. Update LivePipelineRecorder                     │
└─────────────────────────────────────────────────────┘
```

### Benefits
- ✅ Non-blocking route handlers
- ✅ Handle multiple concurrent requests efficiently
- ✅ Can scale horizontally (multiple workers)
- ✅ Better for long-running workflows

### Drawbacks
- ❌ Much more complex implementation
- ❌ Requires message queue infrastructure
- ❌ Harder to debug and test
- ❌ State management becomes distributed

**Recommendation:** Implement Option 1 (blocking) first, then refactor to Option 2 if scalability becomes an issue.

---

## Testing Strategy

### Unit Tests

**1. Backend Router Blocking Execution**
```python
# test_backend_router.py

@pytest.mark.asyncio
async def test_execute_comfyui_chunk_blocking():
    """Test that ComfyUI execution waits for completion"""

    router = BackendRouter()

    chunk_data = {
        'name': 'output_image_sd35_large',
        'backend_type': 'comfyui',
        'media_type': 'image',
        'workflow': {...}
    }

    execution_context = ExecutionContext(
        input_text='Test prompt',
        previous_output='Test prompt',
        execution_mode='eco'
    )

    result = await router._execute_comfyui_chunk(chunk_data, execution_context)

    # Should return media bytes, not just prompt_id
    assert 'media_bytes' in result
    assert len(result['media_bytes']) > 0
    assert result['media_type'] == 'image'
    assert result['backend'] == 'comfyui'
```

**2. Media Storage from Bytes**
```python
# test_media_storage.py

@pytest.mark.asyncio
async def test_add_media_from_bytes():
    """Test simplified media storage"""

    storage = MediaStorageService(Path('/tmp/test_storage'))

    # Create test run
    metadata = await storage.create_run(
        schema='dada',
        execution_mode='eco',
        input_text='Test',
        run_id='test-run-id'
    )

    # Add media from bytes
    test_image_bytes = b'PNG fake image data'
    media_output = await storage.add_media_from_bytes(
        run_id='test-run-id',
        data=test_image_bytes,
        media_type='image',
        backend='comfyui',
        config='sd35_large',
        file_format='png'
    )

    assert media_output is not None
    assert media_output.type == 'image'
    assert media_output.backend == 'comfyui'
    assert media_output.file_size_bytes == len(test_image_bytes)
```

### Integration Tests

**3. End-to-End Pipeline with Media Generation**
```python
# test_integration.py

@pytest.mark.asyncio
async def test_full_pipeline_with_blocking_media():
    """Test complete pipeline with refactored media generation"""

    # Submit pipeline
    response = await execute_pipeline_api(
        schema='dada',
        input_text='Test blocking media generation',
        execution_mode='eco',
        safety_level='kids'
    )

    assert response['status'] == 'success'
    run_id = response['run_id']

    # Check all entities created
    entities = list_entities(run_id)
    assert len(entities) == 6

    # Check media entity exists
    media_entity = next(e for e in entities if e['type'] == 'output_image')
    assert media_entity is not None

    # Check media file is valid
    media_path = get_entity_path(run_id, 'output_image')
    assert media_path.exists()
    assert media_path.stat().st_size > 0

    # Try to open as image
    from PIL import Image
    img = Image.open(media_path)
    assert img.width > 0
    assert img.height > 0
```

### Performance Tests

**4. Compare Execution Time**
```python
# test_performance.py

@pytest.mark.asyncio
async def test_compare_execution_time():
    """Compare OLD polling vs NEW blocking execution time"""

    # OLD system (for reference, if still available)
    start = time.time()
    old_result = await old_execute_with_polling()
    old_time = time.time() - start

    # NEW system (blocking)
    start = time.time()
    new_result = await new_execute_blocking()
    new_time = time.time() - start

    # Should be similar or faster (no extra HTTP round trips)
    assert new_time <= old_time * 1.1  # Allow 10% margin

    print(f"OLD: {old_time:.2f}s, NEW: {new_time:.2f}s")
```

---

## Risks and Mitigations

### Risk 1: Longer Request Timeout

**Risk:** Blocking execution means route handlers wait for ComfyUI (10-30 seconds)

**Mitigation:**
- Set appropriate timeouts in `wait_for_completion()` (default 300s)
- Use Waitress with higher timeout configuration
- Consider implementing Option 2 (event-driven) if this becomes a problem

### Risk 2: Error Handling Complexity

**Risk:** Errors can occur at multiple stages (submit, wait, download)

**Mitigation:**
- Comprehensive try/except blocks in backend_router
- Clear error messages with context (prompt_id, stage)
- Rollback mechanism if download fails

### Risk 3: Breaking Existing Functionality

**Risk:** Changing core execution flow might break other features

**Mitigation:**
- Create backup branch before starting
- Extensive testing (unit + integration)
- Validate against OLD system output
- Gradual rollout (test with one config first)

### Risk 4: ComfyUI Workflow Hangs

**Risk:** If ComfyUI workflow hangs indefinitely, route handler blocks forever

**Mitigation:**
- Implement timeout in `wait_for_completion()` (300s default)
- Add cancellation support (kill workflow if timeout)
- Log warnings before timeout expires

---

## Rollback Plan

If refactoring causes issues:

### Step 1: Identify Issue
- Check logs for errors
- Compare output with OLD system
- Check execution time

### Step 2: Quick Rollback
```bash
git checkout backup-before-media-refactor
git checkout -b fix-media-refactor-issues
# Fix issues
```

### Step 3: Restore OLD Polling Logic
If blocking execution proves problematic, restore polling:
```python
# In backend_router.py
async def _execute_comfyui_chunk(self, chunk_data, execution_context):
    # Revert to returning just prompt_id
    return {'prompt_id': prompt_id}

# In media_storage.py
# Restore add_media_from_comfyui() with polling
```

---

## Future Enhancements (Post-Refactoring)

### 1. WebSocket Real-Time Updates
Once blocking execution is stable, add WebSocket support:
```python
# In backend_router.py
async def _execute_comfyui_chunk(self, chunk_data, execution_context):
    # ...

    # Emit progress updates via WebSocket
    await websocket.send({
        'type': 'workflow_progress',
        'prompt_id': prompt_id,
        'progress': 0.5  # 50%
    })
```

### 2. Caching Layer
Add caching for identical prompts:
```python
# Check cache before executing
cache_key = hash(workflow_json)
if cache_key in media_cache:
    return media_cache[cache_key]

# Execute workflow
media_bytes = await execute_and_download()

# Cache result
media_cache[cache_key] = media_bytes
```

### 3. Multi-Backend Support
Once abstraction is clean, add more backends:
- SwarmUI (ComfyUI alternative)
- Replicate API
- Hugging Face Inference API

---

## Success Metrics

### Before Refactoring (Current State)
- ⚠️ Polling logic in `media_storage.py` (90+ lines)
- ⚠️ Two separate operations: submit + download
- ⚠️ MediaStorage knows about ComfyUI internals
- ⏱️ Execution time: ~30-40 seconds

### After Refactoring (Target State)
- ✅ No polling logic in `media_storage.py`
- ✅ Single operation: submit + wait + download in backend_router
- ✅ MediaStorage is backend-agnostic (pure storage)
- ✅ Cleaner separation of concerns
- ⏱️ Execution time: ~30-40 seconds (similar or better)

### Key Metrics to Track
1. **Lines of Code:** Should decrease (remove polling logic)
2. **Execution Time:** Should be similar or faster
3. **Error Rate:** Should decrease (simpler flow, fewer points of failure)
4. **Test Coverage:** Should increase (easier to test)

---

## Questions and Answers

### Q1: Why not implement event-driven architecture (Option 2) immediately?

**A:** Blocking execution (Option 1) is much simpler and sufficient for current needs. Event-driven adds significant complexity:
- Requires message queue infrastructure
- Distributed state management
- More complex error handling
- Harder to debug

We can refactor to Option 2 later if scalability becomes an issue.

### Q2: Won't blocking execution slow down the server?

**A:** Not significantly. The route handler is already blocking on pipeline execution. We're just moving the polling logic from `media_storage.py` to `backend_router.py` where it belongs. The total execution time should be similar.

Additionally, Waitress (our WSGI server) handles concurrent requests via worker threads, so one blocked request doesn't block others.

### Q3: What if ComfyUI workflow hangs?

**A:** We implement timeout in `wait_for_completion()`:
```python
history = await client.wait_for_completion(prompt_id, timeout=300)
```
After 300 seconds, timeout exception is raised, workflow is cancelled, and error bubbles up to user.

### Q4: Can we still support multiple output configs?

**A:** Yes! The Stage 3-4 loop handles multiple output configs:
```python
for output_config_name in output_requests:
    # Execute blocking
    output_result = await executor.execute_pipeline(...)
    # Store media
    await media_storage.add_media_from_bytes(...)
```

Each output config executes sequentially, waits for completion, and stores media before moving to the next.

### Q5: Does this break LivePipelineRecorder integration?

**A:** No! LivePipelineRecorder is agnostic to how media is generated. It just saves entities. The integration in `schema_pipeline_routes.py` remains the same, just with different method calls.

---

## Timeline Estimate

**Estimated Total Time:** 4-6 hours

### Breakdown:
- **Phase 1 (Backend Router):** 1.5 hours
  - Code changes: 30 min
  - Testing: 1 hour

- **Phase 2 (Route Handler):** 1 hour
  - Code changes: 30 min
  - Testing: 30 min

- **Phase 3 (Media Storage):** 1 hour
  - Code changes: 30 min
  - Testing: 30 min

- **Phase 4 (Integration):** 1-2 hours
  - End-to-end testing: 1 hour
  - Bug fixes: 30 min - 1 hour

- **Phase 5 (Documentation):** 30-60 min
  - Update technical docs
  - Create session summary

---

## Conclusion

This refactoring improves architecture by:

1. ✅ **Proper Separation of Concerns** - Backend router owns workflow lifecycle
2. ✅ **Loose Coupling** - Media storage knows nothing about ComfyUI
3. ✅ **Simpler Code** - Remove 90+ lines of polling logic
4. ✅ **Better Error Handling** - Errors bubble up immediately
5. ✅ **Foundation for Future Scalability** - Can add event-driven later

**Status:** Design complete, ready for implementation when prioritized.

**Priority:** Medium (current band-aid fix works correctly, this is architectural improvement for maintainability)

---

**Document Version:** 1.0
**Created:** 2025-11-04
**Author:** Session 29 (Claude Code)
**Status:** Design Document - Awaiting Implementation

**Next Steps:** Review with user, prioritize against other tasks, schedule implementation session.
