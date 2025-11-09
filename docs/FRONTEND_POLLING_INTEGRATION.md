# Frontend Polling Integration - LivePipelineRecorder

**Status:** 📋 Planned (Session 30)
**Version:** 1.0
**Date:** 2025-11-04

## Overview

This document details the frontend integration plan for LivePipelineRecorder's real-time status API. The integration adds real-time progress tracking to the existing execution flow, providing users with visibility into pipeline execution stages and pedagogically relevant prompt transformation processes.

## Problem Statement

### Current Limitations

**Existing Frontend Behavior** (`execution-handler.js`):
1. User submits prompt → `/api/schema/pipeline/execute` called
2. Wait (no feedback) until backend responds
3. Display final result when complete
4. Poll for media if ComfyUI generation needed

**Issues:**
- No real-time feedback during execution (15-30s wait)
- User has no visibility into 4-stage pipeline process
- Pedagogical opportunity missed (users don't see prompt interception happening)
- Network issues over internet cause "load failed" messages

**Network Context:**
- Server: 12 Mbit/s upload bandwidth (adequate for JSON responses)
- **Critical Issue:** "Load failed" messages only occur when accessing **over internet**, NOT on local WiFi
- **Root Cause:** Latency/timeout issues, NOT bandwidth limitations
- Existing media polling uses 1-second intervals with 120s timeout

## Architecture Decision

### Two-Layer Polling System

**Design Rationale:** Separate concerns between pipeline execution tracking and media generation waiting.

```
User Action: Submit Prompt
    ↓
[Layer 1: Pipeline Status Polling]  ← NEW
    - Track execution through 4 stages
    - Display entities as they appear
    - Show progress percentage
    - Handle network timeouts gracefully
    ↓
Pipeline Complete
    ↓
[Layer 2: Media Polling]  ← EXISTING
    - Wait for ComfyUI generation
    - Poll /api/media/info/{prompt_id}
    - Display when ready
```

### Why Not SSE (Server-Sent Events)?

**Considered but rejected:**
- Adds significant backend complexity (filesystem watching, connection management)
- Proxy/firewall compatibility issues
- Connection timeouts over slow internet would be same problem
- Polling with smart error handling is simpler and equally effective for this use case

**Decision:** Use polling with robust error handling and user feedback.

## Design Decisions (All Approved)

### 1. Polling Interval: 1 Second

**Decision:** Use 1-second intervals as recommended in `LIVE_PIPELINE_RECORDER.md`

**Rationale:**
- Status API responses are tiny (~2KB JSON)
- Much less likely to timeout than large media files (2-3MB)
- Provides real-time feel without overwhelming server
- Same interval used successfully by existing media polling

**Network Impact:**
```
1-second interval = 60 requests/minute
Response size: ~2KB
Bandwidth usage: 120KB/minute (0.01% of 12 Mbit/s upload)
```

**Performance Analysis:**
- Even with 10 concurrent users: 600KB/min (0.04% of bandwidth)
- Bottleneck is media serving (2MB PNG = 13s @ 12 Mbit/s), not status polling

### 2. Error Handling: Persistent with User Feedback

**Decision:** Keep retrying at 1-second intervals, show "Verbindung langsam..." message on timeout

**Behavior:**
```javascript
// On successful poll
- Update UI immediately
- Keep 1-second interval

// On timeout/error
- Don't give up
- Show: "Verbindung langsam, Versuch läuft..."
- Continue polling at 1-second intervals
- Update message: "Versuch läuft... (10 Sekunden)"

// On recovery
- Hide error message
- Resume normal UI updates
```

**Rationale:**
- User knows system is working, just slow
- No hard failure (frustrating on slow connections)
- Matches expectation that execution takes 15-30s anyway

### 3. UI Complexity: Full Entity List (Pedagogical)

**Decision:** Display progress bar + stage name + entity list with timestamps

**UI Elements:**

```
┌─────────────────────────────────────┐
│ Pipeline-Ausführung                 │
├─────────────────────────────────────┤
│ [████████████░░░░░░░] 67%          │
│ Stage 2: Interception               │
│                                     │
│ ✓ Input (22:05:38)                 │
│ ✓ Translation (22:05:45)           │
│ ✓ Safety Check (22:05:45)          │
│ ⏳ Interception...                  │
│                                     │
│ Verbindung langsam, Versuch läuft...│ [if timeout]
└─────────────────────────────────────┘
```

**Rationale:**
- **Pedagogical Value:** Users see prompt interception process unfold in real-time
- Aligns with project's educational mission (counter-hegemonic pedagogy)
- Makes "black box" AI process transparent
- Users understand the 4-stage pipeline architecture

### 4. Integration Approach: Post-Execution Polling

**Decision:** Backend returns `run_id`, frontend polls AFTER execute response received

**Flow:**

```javascript
async function submitPrompt() {
    // 1. Submit execution
    const response = await fetch('/api/schema/pipeline/execute', {...});
    const result = await response.json();

    // 2. Start status polling with run_id
    pollPipelineStatus(result.run_id);

    // 3. Status polling completes
    // (updates UI in real-time)

    // 4. If media_output exists, start media polling
    if (result.media_output) {
        pollForMedia(result.media_output.output);
    }
}
```

**Rationale:**
- Clean separation of concerns
- Backend already generates `run_id` upfront
- No race conditions (backend ensures entity files exist before responding)
- Simple to understand and maintain

## Technical Specification

### Backend Requirements

#### Verification Needed

Check that `/api/schema/pipeline/execute` response includes `run_id`:

```json
{
  "status": "success",
  "run_id": "528e5af9-59b3-4551-b101-27e13dd6e43e",  // ← VERIFY THIS
  "final_output": "...",
  "media_output": {
    "status": "pending",
    "output": "prompt_xyz123"
  }
}
```

**If missing:** Add `run_id` to response in `schema_pipeline_routes.py:execute_pipeline()` (line ~450)

#### API Contract

**Endpoint:** `GET /api/pipeline/{run_id}/status`

**Response:** (Already implemented, documented in `LIVE_PIPELINE_RECORDER.md`)

```json
{
  "run_id": "528e5af9-...",
  "config_name": "stillepost",
  "execution_mode": "eco",
  "expected_outputs": ["input", "translation", "safety", "interception", ...],
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
    ...
  ]
}
```

**Error Responses:**
- `404`: Run not found (invalid run_id)
- `500`: Server error

### Frontend Implementation

#### New Components

**File:** `public_dev/js/execution-handler.js`

**New Functions:**

1. **`pollPipelineStatus(runId)`**
   - Main polling loop
   - Calls status API every 1 second
   - Updates UI based on response
   - Handles errors gracefully
   - Stops when pipeline complete

2. **`updatePipelineProgress(statusData)`**
   - Parses `current_state.progress` ("4/6")
   - Updates progress bar width
   - Updates stage indicator text

3. **`updateEntityList(entities)`**
   - Adds new entities to display as they appear
   - Shows checkmark for completed
   - Shows spinner for in-progress
   - Displays timestamps

4. **`handlePollingError(attemptCount, error)`**
   - Shows "Verbindung langsam..." message
   - Updates with attempt duration
   - Logs error for debugging

5. **`isPipelineComplete(statusData)`**
   - Checks if execution finished
   - Returns true when no more entities expected
   - Uses `expected_outputs` vs `completed_outputs`

#### Modified Functions

**`submitPrompt()` (lines 12-72):**

```javascript
// BEFORE: Just wait for response
const result = await response.json();
displayResult(result);

// AFTER: Start polling with run_id
const result = await response.json();
if (result.run_id) {
    await pollPipelineStatus(result.run_id);
}
displayResult(result);
```

**`displayResult()` (lines 77-110):**
- No changes needed
- Already handles media polling correctly

#### UI Components

**File:** `public_dev/index.html`

**New HTML Structure:**

```html
<div id="pipeline-progress-container" style="display:none;">
    <div class="progress-header">
        <h3>Pipeline-Ausführung</h3>
    </div>

    <!-- Progress bar -->
    <div class="progress-bar-container">
        <div id="pipeline-progress-bar" class="progress-bar" style="width:0%"></div>
    </div>
    <div id="pipeline-progress-text" class="progress-text">0%</div>

    <!-- Stage indicator -->
    <div id="pipeline-stage-indicator" class="stage-indicator">
        Stage 0: Wird gestartet...
    </div>

    <!-- Entity list -->
    <ul id="pipeline-entity-list" class="entity-list"></ul>

    <!-- Error message (shown on timeout) -->
    <div id="pipeline-error-message" class="error-message" style="display:none;">
        Verbindung langsam, Versuch läuft...
    </div>
</div>
```

**CSS Styling:**

```css
.progress-bar-container {
    width: 100%;
    height: 20px;
    background-color: #e0e0e0;
    border-radius: 10px;
    overflow: hidden;
}

.progress-bar {
    height: 100%;
    background-color: #4CAF50;
    transition: width 0.3s ease;
}

.stage-indicator {
    margin: 10px 0;
    font-weight: bold;
    color: #333;
}

.entity-list {
    list-style: none;
    padding: 0;
}

.entity-item {
    padding: 5px 0;
    border-bottom: 1px solid #eee;
}

.entity-item.completed::before {
    content: "✓ ";
    color: green;
}

.entity-item.in-progress::before {
    content: "⏳ ";
}
```

## Implementation Plan

### Phase 1: Backend Verification (5 min)

**Task:** Verify `run_id` is included in execute response

**Steps:**
1. Read `schema_pipeline_routes.py:execute_pipeline()` return statement
2. Check if `run_id` is in response JSON
3. If missing: Add `"run_id": run_id` to response dict

**Files:**
- `devserver/my_app/routes/schema_pipeline_routes.py`

### Phase 2: Frontend - Status Polling Logic (30 min)

**Task:** Implement core polling mechanism

**Steps:**
1. Add `pollPipelineStatus(runId)` function
2. Implement 1-second interval with `setInterval`
3. Handle API responses (update UI)
4. Handle errors (show message, keep trying)
5. Implement completion detection

**Functions:**
- `pollPipelineStatus(runId)`
- `handlePollingError(attemptCount, error)`
- `isPipelineComplete(statusData)`

**Files:**
- `public_dev/js/execution-handler.js`

### Phase 3: Frontend - UI Updates (20 min)

**Task:** Implement progress display functions

**Steps:**
1. Add `updatePipelineProgress(statusData)` - progress bar
2. Add `updateEntityList(entities)` - entity list
3. Modify `submitPrompt()` to start polling
4. Test UI updates with mock data

**Functions:**
- `updatePipelineProgress(statusData)`
- `updateEntityList(entities)`

**Files:**
- `public_dev/js/execution-handler.js`

### Phase 4: Frontend - HTML/CSS (15 min)

**Task:** Add UI components to page

**Steps:**
1. Add progress container HTML to `index.html`
2. Add CSS styling for progress bar, entity list
3. Position elements in page layout
4. Test visibility toggling

**Files:**
- `public_dev/index.html`
- `public_dev/css/*.css` (or inline)

### Phase 5: Integration Testing (20 min)

**Task:** Test complete flow end-to-end

**Test Cases:**
1. **Normal execution:** Submit prompt, watch progress, see entities, complete
2. **Network timeout simulation:** Delay status API, verify error message shows
3. **Media generation:** Verify transition from status polling to media polling
4. **Multiple concurrent runs:** Verify run_id isolation
5. **Error handling:** Submit invalid config, verify graceful failure

**Test Method:**
```bash
# Start server
cd /home/joerissen/ai/ai4artsed_webserver/devserver
python3 server.py

# Open browser
# Navigate to http://localhost:17801
# Submit various pipeline executions
```

### Phase 6: Remote Access Testing (15 min)

**Task:** Test over internet connection (simulated slow network)

**Test Method:**
```bash
# Simulate slow connection with tc (traffic control)
sudo tc qdisc add dev eth0 root netem delay 200ms loss 5%

# Test polling behavior
# Verify "Verbindung langsam..." message appears
# Verify recovery when connection improves

# Remove simulation
sudo tc qdisc del dev eth0 root
```

## Error Handling Specifications

### Network Timeout

**Trigger:** Status API request takes >10s or fails

**Behavior:**
```javascript
let errorCount = 0;
let errorStartTime = null;

// On error
errorCount++;
if (!errorStartTime) errorStartTime = Date.now();

// Show message
const duration = Math.floor((Date.now() - errorStartTime) / 1000);
showError(`Verbindung langsam, Versuch läuft... (${duration}s)`);

// On recovery
errorCount = 0;
errorStartTime = null;
hideError();
```

### API Errors

**404 Not Found:**
- Run doesn't exist yet (should not happen with our flow)
- Log error, retry (may appear before backend creates folder)

**500 Server Error:**
- Backend crashed or disk full
- Show error message
- Stop polling after 30 attempts (30 seconds)

**Network Unreachable:**
- No internet connection
- Show message: "Keine Verbindung zum Server"
- Keep retrying

### Race Conditions

**Problem:** Frontend polls before backend creates run folder

**Solution:** Backend creates folder and metadata.json BEFORE returning run_id, so folder always exists when frontend polls.

**Code Check:** Verify in `schema_pipeline_routes.py` that recorder is initialized before response sent.

## Performance Considerations

### Frontend Resource Usage

**Per Pipeline Run:**
- 1 `setInterval` (1 second)
- ~60 API requests (15-30s execution time)
- ~120KB data transfer total
- Minimal CPU (JSON parsing, DOM updates)

**Multiple Concurrent Runs:**
- Each run has isolated polling loop
- No interference between runs
- Browser limit: ~6 concurrent AJAX requests (not an issue with 1s interval)

### Backend Resource Usage

**Per Status Request:**
- Read 1 file (`metadata.json`): ~2KB
- No computation (just file read)
- Response time: <10ms

**Scaling:**
- 10 concurrent users = 600 requests/minute
- Trivial load for modern server
- Bottleneck remains media generation, not status API

## Testing Strategy

### Unit Tests (Manual)

**Test:** `pollPipelineStatus()` function
- Mock `fetch` to return fake status data
- Verify UI updates correctly
- Verify polling stops when complete

**Test:** Error handling
- Mock `fetch` to throw error
- Verify error message displays
- Verify polling continues

### Integration Tests

**Test:** Full execution flow
1. Submit "dada" pipeline
2. Verify progress bar updates
3. Verify entities appear in order: input → translation → safety → interception
4. Verify final result displays
5. Verify media polling starts (if media requested)

**Test:** Network resilience
1. Submit pipeline
2. Disconnect network mid-execution
3. Verify error message appears
4. Reconnect network
5. Verify polling recovers and completes

### User Acceptance

**Success Criteria:**
- ✅ User sees progress during execution (no more "black box")
- ✅ Entity list shows prompt transformation process (pedagogical goal)
- ✅ "Load failed" messages eliminated or reduced
- ✅ Graceful degradation on slow connections (message, not failure)

## Rollback Plan

**If polling causes issues:**

1. **Quick Fix:** Add feature flag
   ```javascript
   const ENABLE_STATUS_POLLING = false;  // Disable temporarily
   ```

2. **Revert:** Remove polling code, restore previous `submitPrompt()` behavior

3. **Fallback:** Keep backend API (no harm), just don't use in frontend

**Risk Assessment:**
- **Low Risk:** Polling is purely additive (doesn't break existing flow)
- **Existing functionality preserved:** Media polling unchanged
- **Easy to disable:** Single boolean flag

## Future Enhancements

**Not in Scope (Session 30):**

1. **WebSocket Support** - Real-time push instead of polling
2. **Entity Content Preview** - Click entity to see content
3. **Stage Substeps** - Show iteration count for `stillepost` (8 translations)
4. **Error Entity Display** - Show error details if pipeline fails
5. **Run History** - Browse previous pipeline runs
6. **Pause/Cancel** - Stop execution mid-pipeline

**Priority for Future Sessions:**
- Entity content preview (high pedagogical value)
- Error entity display (better debugging)

## Documentation Updates

**After Implementation:**

1. Update `docs/README.md` "Current Status" section:
   ```markdown
   ### ✅ Completed
   - **Frontend integration** - Real-time status polling implemented
   ```

2. Update `LIVE_PIPELINE_RECORDER.md` with frontend code examples

3. Create user guide (if needed) explaining progress indicators

## Success Metrics

**Technical:**
- ✅ Polling interval: 1 second (as designed)
- ✅ API response time: <100ms (file read)
- ✅ Error recovery: <5 seconds after timeout
- ✅ UI updates: Real-time (within 1 second)

**User Experience:**
- ✅ Progress visibility: Users see stages unfold
- ✅ Reduced "load failed": Graceful error messages instead
- ✅ Pedagogical value: Users understand pipeline architecture

## References

- **Backend API:** `docs/LIVE_PIPELINE_RECORDER.md`
- **Existing Frontend:** `public_dev/js/execution-handler.js`
- **Architecture:** `docs/README.md`

---

**Document Status:** ✅ Complete - Ready for Implementation
**Next Step:** Phase 1 - Backend Verification
**Estimated Total Time:** ~2 hours (including testing)
