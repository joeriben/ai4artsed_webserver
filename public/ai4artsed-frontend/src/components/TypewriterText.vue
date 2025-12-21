<template>
  <div class="typewriter-container">
    <div class="typewriter-text" :class="{ 'blinking-cursor': isStreaming }">
      {{ displayedText }}
      <span v-if="isStreaming" class="cursor">▋</span>
    </div>
    <div v-if="showProgress && isStreaming" class="stream-progress">
      {{ characterCount }} Zeichen • {{ elapsedTime }}s
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onUnmounted, onMounted } from 'vue'

interface Props {
  streamEndpoint?: string
  runId?: string
  text?: string  // For providing the text to stream (e.g., Stage 1)
  prompt?: string  // For Stage 2 prompt interception
  context?: string
  stylePrompt?: string
  model?: string
  showProgress?: boolean
  speedMs?: number  // Milliseconds per character (default: 30ms)
  autoStart?: boolean  // Auto-connect when component mounts
}

const props = withDefaults(defineProps<Props>(), {
  showProgress: true,
  speedMs: 30,  // ~33 characters per second
  autoStart: false
})

const emit = defineEmits<{
  complete: [text: string]
  error: [error: string]
  'stream-timeout': []
}>()

const displayedText = ref('')
const isStreaming = ref(false)
const characterCount = ref(0)
const elapsedTime = ref(0)
const eventSource = ref<EventSource | null>(null)
const buffer = ref<string[]>([])
let displayInterval: number | null = null
let timeInterval: number | null = null
let timeoutHandle: number | null = null

const STREAM_TIMEOUT_MS = 120000  // 2 minutes

// Display buffered characters at consistent speed
function startDisplayLoop() {
  displayInterval = window.setInterval(() => {
    if (buffer.value.length > 0) {
      const char = buffer.value.shift()!
      displayedText.value += char
      characterCount.value++
    }
  }, props.speedMs)
}

// Track elapsed time
function startTimeTracking() {
  const startTime = Date.now()
  timeInterval = window.setInterval(() => {
    elapsedTime.value = Math.floor((Date.now() - startTime) / 1000)
  }, 1000)
}

// Connect to SSE endpoint
function connectStream() {
  if (!props.streamEndpoint || !props.runId) {
    console.warn('[TypewriterText] Missing streamEndpoint or runId')
    return
  }

  isStreaming.value = true
  displayedText.value = ''
  buffer.value = []
  characterCount.value = 0
  elapsedTime.value = 0

  // Build URL with query parameters
  let url = `${props.streamEndpoint}/${props.runId}`
  const params = new URLSearchParams()

  if (props.text) params.append('text', props.text)
  if (props.prompt) params.append('prompt', props.prompt)
  if (props.context) params.append('context', props.context)
  if (props.stylePrompt) params.append('style_prompt', props.stylePrompt)
  if (props.model) params.append('model', props.model)

  if (params.toString()) {
    url += `?${params.toString()}`
  }

  console.log('[TypewriterText] Connecting to:', url)

  eventSource.value = new EventSource(url)

  startDisplayLoop()
  startTimeTracking()

  // Set timeout for stream completion
  timeoutHandle = window.setTimeout(() => {
    console.error('[TypewriterText] Stream timeout - closing connection')
    isStreaming.value = false
    closeStream()
    emit('stream-timeout')
  }, STREAM_TIMEOUT_MS)

  eventSource.value.addEventListener('connected', (event) => {
    const data = JSON.parse(event.data)
    console.log('[TypewriterText] Connected:', data)
  })

  eventSource.value.addEventListener('chunk', (event) => {
    const data = JSON.parse(event.data)
    // Add chunk characters to buffer for smooth display
    buffer.value.push(...data.text_chunk.split(''))
  })

  eventSource.value.addEventListener('complete', (event) => {
    if (timeoutHandle) {
      clearTimeout(timeoutHandle)
      timeoutHandle = null
    }

    const data = JSON.parse(event.data)
    console.log('[TypewriterText] Complete:', data)

    // Display any remaining buffered characters immediately
    displayedText.value = data.final_text
    characterCount.value = data.final_text.length
    isStreaming.value = false

    emit('complete', data.final_text)
    closeStream()
  })

  eventSource.value.addEventListener('error', (event) => {
    console.error('[TypewriterText] Stream error:', event)

    if (timeoutHandle) {
      clearTimeout(timeoutHandle)
      timeoutHandle = null
    }

    isStreaming.value = false
    emit('error', 'Stream connection failed')
    closeStream()
  })

  eventSource.value.onerror = () => {
    console.error('[TypewriterText] EventSource error')

    if (timeoutHandle) {
      clearTimeout(timeoutHandle)
      timeoutHandle = null
    }

    isStreaming.value = false
    emit('error', 'Stream connection error')
    closeStream()
  }
}

function closeStream() {
  if (eventSource.value) {
    eventSource.value.close()
    eventSource.value = null
  }
  if (displayInterval) {
    clearInterval(displayInterval)
    displayInterval = null
  }
  if (timeInterval) {
    clearInterval(timeInterval)
    timeInterval = null
  }
  if (timeoutHandle) {
    clearTimeout(timeoutHandle)
    timeoutHandle = null
  }
}

// Watch for runId changes to start streaming
watch(() => props.runId, (newRunId) => {
  if (newRunId && props.autoStart) {
    connectStream()
  }
})

onMounted(() => {
  if (props.autoStart && props.runId) {
    connectStream()
  }
})

onUnmounted(() => {
  closeStream()
})

// Expose methods for manual control
defineExpose({
  connectStream,
  closeStream,
  isStreaming
})
</script>

<style scoped>
.typewriter-container {
  font-family: 'Monaco', 'Courier New', monospace;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 8px;
  min-height: 3rem;
}

.typewriter-text {
  font-size: 1rem;
  line-height: 1.6;
  color: #2c3e50;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.cursor {
  color: #42b983;
  animation: blink 1s infinite;
  margin-left: 2px;
  font-weight: bold;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

.stream-progress {
  margin-top: 0.5rem;
  font-size: 0.85rem;
  color: #666;
  font-style: italic;
}

/* Dark theme support */
@media (prefers-color-scheme: dark) {
  .typewriter-container {
    background: rgba(255, 255, 255, 0.05);
  }

  .typewriter-text {
    color: #e0e0e0;
  }

  .cursor {
    color: #4ade80;
  }

  .stream-progress {
    color: #999;
  }
}
</style>
