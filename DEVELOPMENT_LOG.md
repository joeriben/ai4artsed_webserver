# Development Log

## Session 112 - CRITICAL: Fix Streaming Connection Leak (CLOSE_WAIT) & Queue Implementation
**Date:** 2026-01-08
**Duration:** ~2 hours
**Focus:** Fix connection leak and concurrent request overload (Ollama)
**Status:** SUCCESS - Connection cleanup implemented, Queue implemented

### Problem 1: Connection Leak (CLOSE_WAIT)
Production system (lab.ai4artsed.org) experiencing streaming failures:
- Cloudflared tunnel logs: "stream X canceled by remote with error code 0"
- Backend accumulating connections in CLOSE_WAIT state
- Eventually all streaming requests failing

### Fix 1: Streaming Cleanup
Implemented `GeneratorExit` handling and explicit `response.close()` in streaming generators:
1. `/devserver/schemas/engine/prompt_interception_engine.py:381`
2. `/devserver/my_app/services/ollama_service.py:366`
3. `/devserver/my_app/routes/schema_pipeline_routes.py:1278`

Result: CLOSE_WAIT connections now clear properly (tested with load test).

### Problem 2: Ollama Overload (Timeouts)
Under load (e.g. 10 parallel requests), Ollama (120b model) gets overloaded.
- Requests time out after 90s (default `OLLAMA_TIMEOUT`)
- Model execution takes 100-260s
- Parallel requests cause congestion and failures

### Fix 2: Request Queueing & Timeouts
1. **Request Queue:**
   - Implemented `threading.Semaphore(3)` in `schema_pipeline_routes.py`.
   - Limits concurrent heavy model executions to 3 (others wait).
   - Applied to Stage 1 safety checks in `execute_pipeline_streaming`, `execute_pipeline` (POST), and `execute_stage2`.

2. **Timeout Increase:**
   - Increased `OLLAMA_TIMEOUT` in `config.py` from 90s to 300s.

3. **Bug Fix:**
   - Fixed `SyntaxError` in `streaming_response.py` (f-string syntax) that prevented backend startup.

### Test Results
**Load Test (10 concurrent requests):**
- Backend: Running on port 17802 (Dev script)
- Queue Logic: Verified in logs
  ```
  [OLLAMA-QUEUE] Initialized with max concurrent requests: 3
  [OLLAMA-QUEUE] Stream ...: Waiting for queue slot...
  [OLLAMA-QUEUE] Stream ...: Acquired slot...
  [OLLAMA-QUEUE] Stream ...: Released slot
  ```
- All requests queued and processed sequentially without timeout errors.

### Fix 3: User Feedback (Queue Visualization)
1. **Backend (SSE):**
   - Updated `execute_pipeline_streaming` to yield `queue_status` events while waiting in queue.
   - Frequency: Every 1 second.
   - Payload: `{'status': 'waiting', 'message': 'Warte auf freien Slot... (Xs)'}`.

2. **Frontend (MediaInputBox.vue):**
   - Added listener for `queue_status` event.
   - Visual Feedback:
     - Spinner turns **RED** (`.spinner-large.queued`) when status is 'waiting'.
     - Loading text pulses red and shows queue message.
     - Automatically resets to normal (blue) when slot is acquired.

### Next Steps
- Monitor production after deployment.

---

## Session 111 - CRITICAL: Unified Streaming Architecture Refactoring
**Date:** 2025-12-28
**Duration:** ~4 hours
- Supports both emoji and string icon names ('lightbulb', 'clipboard', etc.)
