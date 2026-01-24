<template>
  <div class="chat-overlay">
    <!-- Collapsed State: Floating Icon Button -->
    <button
      v-if="!isExpanded"
      class="chat-toggle-icon"
      @click="expand"
      title="KI-Helfer öffnen (Träshy)"
    >
      <img :src="trashyIcon" alt="Träshy" class="chat-icon-img" />
    </button>

    <!-- Expanded State: Chat Window -->
    <div v-else class="chat-window">
      <!-- Header -->
      <div class="chat-header">
        <span class="chat-title">Träshy</span>
        <img :src="trashyIcon" alt="Träshy" class="header-trashy-icon" />
        <div class="header-right">
          <span v-if="hasContext" class="context-indicator" title="Session-Kontext aktiv">
            💡
          </span>
          <button class="close-button" @click="collapse" title="Schließen">×</button>
        </div>
      </div>

      <!-- Messages Container -->
      <div class="chat-messages" ref="messagesContainer">
        <!-- Initial greeting (only if no messages) -->
        <div v-if="messages.length === 0" class="message assistant greeting">
          <div class="message-content">
            Hallo! Ich bin dein KI-Helfer. Stelle mir Fragen über AI4ArtsEd oder lass dich bei deinem Prompt beraten.
          </div>
        </div>

        <!-- Message History -->
        <div
          v-for="msg in messages"
          :key="msg.id"
          :class="['message', msg.role]"
        >
          <div class="message-content">{{ msg.content }}</div>
        </div>

        <!-- Loading Indicator -->
        <div v-if="isLoading" class="message assistant loading">
          <div class="message-content">
            <span class="spinner"></span>
            <span class="loading-text">Denkt nach...</span>
          </div>
        </div>
      </div>

      <!-- Input Container -->
      <div class="chat-input-container">
        <textarea
          v-model="inputMessage"
          placeholder="Stelle eine Frage..."
          @keydown.enter.exact.prevent="sendMessage"
          @keydown.shift.enter="inputMessage += '\n'"
          :disabled="isLoading"
          rows="2"
          ref="inputTextarea"
        ></textarea>
        <button
          class="send-button"
          @click="sendMessage"
          :disabled="!canSend"
          title="Nachricht senden (Enter)"
        >
          ➤
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch, inject } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { useCurrentSession } from '../composables/useCurrentSession'
import { PAGE_CONTEXT_KEY, formatPageContextForLLM } from '../composables/usePageContext'
import trashyIcon from '../assets/trashy-icon.png'

interface Message {
  id: number
  role: 'user' | 'assistant'
  content: string
}

// State
const isExpanded = ref(false)
const isLoading = ref(false)
const inputMessage = ref('')
const messages = ref<Message[]>([])
let messageIdCounter = 0

// Refs
const messagesContainer = ref<HTMLElement | null>(null)
const inputTextarea = ref<HTMLTextAreaElement | null>(null)

// Session context
const { currentSession, hasActiveSession } = useCurrentSession()

// Page context (Session 133: Träshy knows about current page state)
const pageContext = inject(PAGE_CONTEXT_KEY, null)
const route = useRoute()

// Build draft context string for LLM
const draftContextString = computed(() => {
  if (!pageContext?.value) {
    // Fallback: just route info
    return formatPageContextForLLM(null, route.path)
  }
  return formatPageContextForLLM(pageContext.value, route.path)
})

// Computed
// Has context if either: session context (run_id) OR draft context (page provided)
const hasContext = computed(() => hasActiveSession() || (pageContext?.value?.pageContent !== undefined))

const canSend = computed(() => {
  return inputMessage.value.trim().length > 0 && !isLoading.value
})

// Methods
async function expand() {
  isExpanded.value = true

  // Focus input after expansion
  await nextTick()
  inputTextarea.value?.focus()

  // Load chat history if session exists
  if (currentSession.value.runId) {
    await loadChatHistory()
  }
}

function collapse() {
  isExpanded.value = false
}

async function loadChatHistory() {
  if (!currentSession.value.runId) return

  try {
    const response = await axios.get(`/api/chat/history/${currentSession.value.runId}`)
    const history = response.data.history || []

    // Convert history to messages (filter out system messages)
    messages.value = history
      .filter((msg: any) => msg.role !== 'system')
      .map((msg: any, index: number) => ({
        id: index,
        role: msg.role,
        content: msg.content
      }))

    messageIdCounter = messages.value.length

    // Scroll to bottom
    await nextTick()
    scrollToBottom()

    console.log('[ChatOverlay] Loaded chat history:', messages.value.length, 'messages')
  } catch (error) {
    console.error('[ChatOverlay] Error loading chat history:', error)
    // Don't show error to user - just start with empty chat
  }
}

async function sendMessage() {
  if (!canSend.value) return

  const userMessage = inputMessage.value.trim()
  inputMessage.value = ''

  // Build full message with draft context (only if no run_id session)
  // Session context (from run_id files) takes priority over draft context
  let messageForBackend = userMessage
  if (!currentSession.value.runId && draftContextString.value) {
    messageForBackend = `${draftContextString.value}\n\n${userMessage}`
    console.log('[ChatOverlay] Prepending draft context to message')
  }

  // Add user message to UI (show original message, not context-prefixed)
  messages.value.push({
    id: messageIdCounter++,
    role: 'user',
    content: userMessage
  })

  // Scroll to bottom
  await nextTick()
  scrollToBottom()

  // Call API
  isLoading.value = true

  try {
    // Prepare history for backend
    const historyForBackend = messages.value.map(msg => ({
      role: msg.role,
      content: msg.content
    }))

    const response = await axios.post('/api/chat', {
      message: messageForBackend,  // Send with context prepended
      run_id: currentSession.value.runId || undefined,
      history: historyForBackend
    })

    const assistantReply = response.data.reply

    // Add assistant response to UI
    messages.value.push({
      id: messageIdCounter++,
      role: 'assistant',
      content: assistantReply
    })

    // Scroll to bottom
    await nextTick()
    scrollToBottom()

    console.log('[ChatOverlay] Message sent, context_used:', response.data.context_used)
  } catch (error) {
    console.error('[ChatOverlay] Error sending message:', error)

    // Add error message
    messages.value.push({
      id: messageIdCounter++,
      role: 'assistant',
      content: 'Entschuldigung, es gab einen Fehler beim Senden der Nachricht. Bitte versuche es erneut.'
    })

    await nextTick()
    scrollToBottom()
  } finally {
    isLoading.value = false
    inputTextarea.value?.focus()
  }
}

function scrollToBottom() {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// Watch for session changes - clear messages if session changes
watch(
  () => currentSession.value.runId,
  async (newRunId, oldRunId) => {
    // If run_id changed (and not just initialized), reload history
    if (newRunId !== oldRunId && isExpanded.value) {
      if (newRunId) {
        console.log('[ChatOverlay] Session changed, reloading history')
        await loadChatHistory()
      } else {
        // Session cleared
        console.log('[ChatOverlay] Session cleared, resetting chat')
        messages.value = []
        messageIdCounter = 0
      }
    }
  }
)
</script>

<style scoped>
.chat-overlay {
  position: fixed;
  bottom: 1rem;
  left: 1rem;
  z-index: 10000;
}

/* Collapsed State */
.chat-toggle-icon {
  width: clamp(75px, 10vw, 100px);
  height: clamp(75px, 10vw, 100px);
  background: transparent;
  border: none;
  box-shadow: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  padding: 0;
}

.chat-toggle-icon:hover {
  transform: scale(1.1);
}

.chat-icon-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.3));
}

/* Expanded State: Chat Window */
.chat-window {
  width: 380px;
  height: 520px;
  background: #1a1a1a;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid #333;
}

/* Header */
.chat-header {
  background: #1a1a1a;
  padding: 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #BED882;
  position: relative;
  border-bottom: 2px solid #BED882;
}

.chat-title {
  font-weight: 700;
  font-size: 1.1rem;
  color: #BED882;
  text-shadow: none;
  flex-shrink: 0;
}

.header-trashy-icon {
  width: 40px;
  height: 40px;
  object-fit: contain;
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.context-indicator {
  font-size: 1.2rem;
  cursor: help;
}

.close-button {
  background: none;
  border: none;
  color: white;
  font-size: 1.8rem;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background 0.2s ease;
}

.close-button:hover {
  background: #E79EAF;
}

/* Messages Container */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  background: #0a0a0a;
}

/* Scrollbar styling */
.chat-messages::-webkit-scrollbar {
  width: 8px;
}

.chat-messages::-webkit-scrollbar-track {
  background: #1a1a1a;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: #333;
  border-radius: 4px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: #444;
}

/* Message Bubbles */
.message {
  display: flex;
  max-width: 85%;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message.user {
  align-self: flex-end;
}

.message.assistant {
  align-self: flex-start;
}

.message-content {
  padding: 0.75rem 1rem;
  border-radius: 12px;
  font-size: 0.9rem;
  line-height: 1.4;
  word-wrap: break-word;
  white-space: pre-wrap;
}

.message.user .message-content {
  background: #BED882;
  color: white;
  border-bottom-right-radius: 4px;
}

.message.assistant .message-content {
  background: #2a2a2a;
  color: #e0e0e0;
  border-bottom-left-radius: 4px;
}

.message.greeting .message-content {
  background: #2a3a2a;
  border: 1px solid #BED882;
  color: #d4edb8;
  font-style: italic;
}

/* Loading State */
.message.loading .message-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #2a2a2a;
  color: #999;
}

.spinner {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid rgba(190, 216, 130, 0.3);
  border-top-color: #BED882;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-text {
  font-size: 0.85rem;
}

/* Input Container */
.chat-input-container {
  padding: 1rem;
  background: #1a1a1a;
  border-top: 1px solid #333;
  display: flex;
  gap: 0.5rem;
  align-items: flex-end;
}

.chat-input-container textarea {
  flex: 1;
  background: #0a0a0a;
  border: 1px solid #333;
  border-radius: 8px;
  padding: 0.75rem;
  color: white;
  font-family: inherit;
  font-size: 0.9rem;
  resize: none;
  max-height: 80px;
  transition: border-color 0.2s ease;
}

.chat-input-container textarea:focus {
  outline: none;
  border-color: #BED882;
}

.chat-input-container textarea:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-button {
  width: 40px;
  height: 40px;
  background: #BED882;
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 1.2rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.send-button:hover:not(:disabled) {
  background: #E79EAF;
  transform: translateY(-2px);
}

.send-button:disabled {
  background: #333;
  color: #666;
  cursor: not-allowed;
  transform: none;
}

/* Mobile Responsiveness (Future) */
@media (max-width: 768px) {
  .chat-window {
    width: calc(100vw - 2rem);
    height: 60vh;
  }

  .chat-overlay {
    left: 1rem;
    right: 1rem;
  }
}
</style>
