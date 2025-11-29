# Session 82: LLM Chat Helper Overlay Implementation

**Date**: 2025-11-29
**Goal**: Implement persistent LLM chat helper as overlay widget (bottom-left) with session-aware context

## Use Cases

1. **General Guidance** (no session context)
   - Help with system navigation
   - Explain features and concepts
   - Answer questions about AI4ArtsEd

2. **System Usage Help** (with basic context)
   - Guide users through the workflow
   - Explain current phase/stage
   - Troubleshooting

3. **Image Prompt Consultation** (with full session context)
   - Analyze current prompt
   - Suggest improvements
   - Explain pedagogical transformations
   - Help refine creative intent

## Architecture Overview

### Backend Components

#### 1. Configuration (`devserver/config.py`)
```python
# Chat Helper Model
CHAT_HELPER_MODEL = REMOTE_FAST_MODEL  # Claude Haiku 4.5
```

#### 2. Chat Routes (`devserver/my_app/routes/chat_routes.py`)
**NEW FILE**

Endpoint:
```
POST /api/chat
Body: {
  "message": "User's question",
  "run_id": "optional-uuid"  // If provided, loads session context
}

Response: {
  "reply": "Assistant's response",
  "context_used": true/false,
  "run_id": "uuid"  // Echoed back for history tracking
}
```

**Context Loading Logic:**
- If `run_id` provided:
  - Check `exports/json/{run_id}/` exists
  - Load session data:
    - `03_input.txt` - Original user input
    - `06_interception.txt` - Pedagogically transformed prompt
    - `02_config_used.json` - Config metadata (safety level, pipeline, etc.)
    - `metadata.json` - Session metadata
  - Build context-aware system prompt
- If NO `run_id`:
  - Use general guidance system prompt

**Chat History Storage:**
- Store in `exports/json/{run_id}/chat_history.json`
- Format: Array of `{"role": "user"|"assistant", "content": "...", "timestamp": "..."}`
- Load existing history if file exists
- Append new messages after each exchange

**System Prompt Templates:**

**General Mode (no context):**
```
You are an AI assistant for AI4ArtsEd, a pedagogical tool for creative AI experimentation
in arts education (ages 8-17).

Your role:
- Explain how the system works (4-stage pipeline: Translation → Interception → Safety → Generation)
- Help users understand interface elements
- Provide guidance on prompt creation
- Answer questions about AI concepts in age-appropriate language

Keep responses:
- Short and clear (2-3 sentences preferred)
- Age-appropriate (German students, ages 8-17)
- Encouraging and pedagogically supportive
```

**Session Mode (with context):**
```
You are helping a student currently working on an AI art project in AI4ArtsEd.

Current Session Context:
- Media Type: {media_type}
- Config/Model: {config_name}
- Safety Level: {safety_level}
- Original Input: {input_text}
- Transformed Prompt: {interception_text}
- Session Stage: {current_stage}

Your role:
- Help refine the current prompt
- Explain what the pedagogical transformation did
- Suggest creative improvements
- Answer questions about their current work

Keep responses:
- Focused on THEIR specific prompt
- Constructive and encouraging
- Short and actionable (2-4 sentences)
```

### Frontend Components

#### 3. Session Composable (`public/ai4artsed-frontend/src/composables/useCurrentSession.ts`)
**NEW FILE**

Global state management for current session:
```typescript
export interface SessionState {
  runId: string | null
  mediaType: string | null
  configName: string | null
}

export function useCurrentSession() {
  // Singleton state (shared across all components)
  return {
    currentSession: Ref<SessionState>,
    updateSession: (runId: string, metadata?: any) => void,
    clearSession: () => void
  }
}
```

**Usage in views:**
```typescript
// In text_transformation.vue, after pipeline execution:
const { updateSession } = useCurrentSession()
const response = await axios.post('/api/schema/pipeline/stream', ...)
const runId = response.data.run_id
updateSession(runId, { mediaType: 'image', configName: selectedConfig.value })
```

#### 4. Chat Overlay Component (`public/ai4artsed-frontend/src/components/ChatOverlay.vue`)
**NEW FILE**

**Features:**
- Fixed position: `bottom: 1rem; left: 1rem;`
- Two states:
  - **Collapsed**: Small circular icon (💬 or 🤖)
  - **Expanded**: Chat window (360px × 480px)
- Chat interface:
  - Message list (scrollable)
  - Input field at bottom
  - "Send" button
- Visual states:
  - Loading spinner while waiting for response
  - Disabled input during loading
  - Auto-scroll to bottom on new messages

**Context Awareness:**
- Uses `useCurrentSession()` to get current `run_id`
- Sends `run_id` with each message (if available)
- Shows indicator when context is active (e.g., "💡 Session-aware")

**Message History:**
- Loads existing history on expand (if session exists)
- Persists across collapse/expand
- Clears when session changes

**Component Structure:**
```vue
<template>
  <div class="chat-overlay">
    <!-- Collapsed State -->
    <button v-if="!isExpanded" class="chat-toggle-icon" @click="expand()">
      💬
    </button>

    <!-- Expanded State -->
    <div v-else class="chat-window">
      <div class="chat-header">
        <span class="chat-title">KI-Helfer</span>
        <span v-if="hasSessionContext" class="context-indicator">💡</span>
        <button class="close-button" @click="collapse()">×</button>
      </div>

      <div class="chat-messages" ref="messagesContainer">
        <div v-for="msg in messages" :key="msg.id" :class="['message', msg.role]">
          {{ msg.content }}
        </div>
        <div v-if="isLoading" class="message assistant loading">
          <span class="spinner"></span> Denkt nach...
        </div>
      </div>

      <div class="chat-input-container">
        <textarea
          v-model="inputMessage"
          placeholder="Stelle eine Frage..."
          @keydown.enter.prevent="sendMessage()"
          :disabled="isLoading"
        ></textarea>
        <button @click="sendMessage()" :disabled="!inputMessage.trim() || isLoading">
          Senden
        </button>
      </div>
    </div>
  </div>
</template>
```

#### 5. App Integration (`public/ai4artsed-frontend/src/App.vue`)

Add ChatOverlay component globally:
```vue
<template>
  <div id="app">
    <router-view />
    <ChatOverlay />  <!-- Global overlay, always mounted -->
  </div>
</template>

<script setup lang="ts">
import ChatOverlay from './components/ChatOverlay.vue'
</script>
```

## Implementation Order

1. ✅ **Backend Config** - Add `CHAT_HELPER_MODEL` to `config.py`
2. ✅ **Backend Routes** - Create `chat_routes.py` with context loading
3. ✅ **Register Routes** - Import and register in Flask app
4. ✅ **Frontend Composable** - Create `useCurrentSession.ts`
5. ✅ **Frontend Component** - Create `ChatOverlay.vue`
6. ✅ **Global Integration** - Add to `App.vue`
7. ✅ **View Updates** - Update `text_transformation.vue` to call `updateSession()`
8. ✅ **Testing** - Test all three use cases

## Technical Decisions

### Why Option A (Explicit run_id)?
- ✅ Reliable and explicit
- ✅ Works with multi-user scenarios
- ✅ No ambiguity about which session
- ✅ Frontend has full control

### Why NOT hardcode in individual views?
- ❌ Maintenance nightmare (many views)
- ✅ Global composable = single source of truth
- ✅ Any view can update, ChatOverlay can read

### Why chat history per session?
- Contextual continuity - user can continue conversation about same work
- Pedagogical value - students can review guidance
- Stored in session folder - natural organization

### Why Vue component over QuikChat library?
- ✅ Full control over styling (match AI4ArtsEd aesthetic)
- ✅ Better TypeScript integration
- ✅ No external dependencies
- ✅ Easier to customize for pedagogical context

## UI/UX Considerations

### Positioning (Bottom-Left)
- Not obstructing typical chat widget space (bottom-right)
- Close to "Phase 1" return button (consistent left-side navigation)
- Leaves right side free for potential future controls

### Visual Design
- Match AI4ArtsEd dark theme (`background: #0a0a0a`)
- Accent color: Green (`#4CAF50`) to match existing UI
- Rounded corners, subtle shadows
- Clear visual hierarchy

### Accessibility
- Keyboard navigation support
- Enter to send message
- ESC to collapse
- Focus management

### Mobile Considerations
- Initially desktop-focused
- Chat overlay should be responsive
- May need mobile-specific positioning

## Testing Strategy

### Test Case 1: General Guidance (No Context)
1. Open AI4ArtsEd (no session started)
2. Expand chat overlay
3. Ask: "Wie funktioniert AI4ArtsEd?"
4. Verify: General explanation, no session-specific info

### Test Case 2: System Usage Help
1. Start a session (enter input, select category)
2. Open chat overlay
3. Ask: "Was bedeutet 'Prompt Interception'?"
4. Verify: Explanation referencing current workflow phase

### Test Case 3: Prompt Consultation
1. Complete interception (have a transformed prompt)
2. Open chat overlay
3. Ask: "Wie kann ich meinen Prompt verbessern?"
4. Verify: Specific suggestions based on current prompt

### Test Case 4: Chat History Persistence
1. Have conversation in session
2. Collapse chat overlay
3. Expand again
4. Verify: Previous messages still visible

### Test Case 5: Session Change
1. Chat in Session A
2. Start new Session B (new run_id)
3. Verify: Chat history resets or loads Session B history

## Future Enhancements (Out of Scope)

- Voice input/output
- Multi-language support (auto-detect from UI_MODE language)
- Prompt templates library
- Export chat history
- Share conversation with teachers
- RAG integration (search documentation)
- Image upload for prompt consultation

## Notes

- Chat is entirely optional - users can ignore it
- No analytics/tracking in initial version
- All data stays local (exports/json/)
- GDPR compliant (no external API calls with personal data)
- Run_id is anonymous UUID, no PII
