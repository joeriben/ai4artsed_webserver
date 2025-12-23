<template>
  <div class="image-pair-transformation-view">

    <div class="phase-2a" ref="mainContainerRef">

      <!-- Section 1: Two Image Inputs (Side by Side) -->
      <section class="input-context-section">
        <!-- Primary Image (LEFT) -->
        <MediaInputBox
          icon="💡"
          label="Dein Bild"
          :value="uploadedImage ?? ''"
          @update:value="(val: string) => uploadedImage = val || undefined"
          input-type="image"
          :initial-image="uploadedImage"
          @image-uploaded="handleImageUpload"
          @image-removed="handleImageRemove"
          @copy="copyUploadedImage"
          @paste="pasteUploadedImage"
          @clear="clearImage"
        />

        <!-- Reference Image (RIGHT) -->
        <MediaInputBox
          icon="🖼️"
          label="Referenzbild hinzufügen"
          :value="referenceImage ?? ''"
          @update:value="(val: string) => referenceImage = val || undefined"
          input-type="image"
          :initial-image="referenceImage"
          @image-uploaded="handleReferenceImageUpload"
          @image-removed="handleReferenceImageRemove"
          @copy="copyReferenceImage"
          @paste="pasteReferenceImage"
          @clear="clearReferenceImage"
        />
      </section>

      <!-- Section 3: Category Selection (Horizontal Row) - Always visible after context -->
      <section v-if="canSelectMedia" class="category-section" ref="categorySectionRef">
        <div class="category-bubbles-row">
          <div
            v-for="category in availableCategories"
            :key="category.id"
            class="category-bubble"
            :class="{ selected: selectedCategory === category.id, disabled: category.disabled }"
            :style="{ '--bubble-color': category.color }"
            @click="!category.disabled && selectCategory(category.id)"
            role="button"
            :aria-pressed="selectedCategory === category.id"
            :aria-disabled="category.disabled"
            :tabindex="category.disabled ? -1 : 0"
            @keydown.enter="!category.disabled && selectCategory(category.id)"
            @keydown.space.prevent="!category.disabled && selectCategory(category.id)"
          >
            <div class="bubble-emoji-small">{{ category.emoji }}</div>
          </div>
        </div>
      </section>

      <!-- Section 3.5: Model Selection (appears BELOW category, filtered by selected category) -->
      <section v-if="selectedCategory" class="config-section">
        <h2 class="section-title">wähle ein Modell aus</h2>
        <div class="config-bubbles-container">
          <div class="config-bubbles-row">
            <div
              v-for="config in configsForCategory"
              :key="config.id"
              class="config-bubble"
              :class="{
                selected: selectedConfig === config.id,
                'light-bg': config.lightBg,
                disabled: false,
                hovered: hoveredConfigId === config.id
              }"
              :style="{ '--bubble-color': config.color }"
              @click="selectModel(config.id)"
              @mouseenter="hoveredConfigId = config.id"
              @mouseleave="hoveredConfigId = null"
              role="button"
              :aria-pressed="selectedConfig === config.id"
              tabindex="0"
            >
              <img v-if="config.logo" :src="config.logo" :alt="config.label" class="bubble-logo" />
              <div v-else class="bubble-emoji-medium">{{ config.emoji }}</div>

              <!-- Hover info overlay (shows INSIDE bubble when hovered) -->
              <div v-if="hoveredConfigId === config.id" class="bubble-hover-info">
                <div class="hover-info-name">{{ config.name }}</div>
                <div class="hover-info-meta">
                  <div class="meta-row">
                    <span class="meta-label">Qual.</span>
                    <span class="meta-value">
                      <span class="stars-filled">{{ '★'.repeat(config.quality) }}</span><span class="stars-unfilled">{{ '☆'.repeat(5 - config.quality) }}</span>
                    </span>
                  </div>
                  <div class="meta-row">
                    <span class="meta-label">Speed</span>
                    <span class="meta-value">
                      <span class="stars-filled">{{ '★'.repeat(config.speed) }}</span><span class="stars-unfilled">{{ '☆'.repeat(5 - config.speed) }}</span>
                    </span>
                  </div>
                  <div class="meta-row">
                    <span class="meta-value duration-only">⏱ {{ config.duration }} sec</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- START BUTTON (Always Visible) -->
      <div class="start-button-container">
        <button
          class="start-button"
          :class="{ disabled: !canStartGeneration || isPipelineExecuting }"
          :disabled="!canStartGeneration || isPipelineExecuting"
          @click="startGeneration"
        >
          <span class="button-arrows button-arrows-left">&gt;&gt;&gt;</span>
          <span class="button-text">Start</span>
          <span class="button-arrows button-arrows-right">&gt;&gt;&gt;</span>
        </button>

        <!-- Safety Stamp (next to button, not on image) -->
        <transition name="fade">
          <div v-if="showSafetyApprovedStamp" class="safety-stamp">
            <div class="stamp-inner">
              <div class="stamp-icon">✓</div>
              <div class="stamp-text">Safety<br/>Approved</div>
            </div>
          </div>
        </transition>
      </div>

      <!-- OUTPUT BOX (Template Component) -->
      <MediaOutputBox
        ref="pipelineSectionRef"
        :output-image="outputImage"
        :media-type="outputMediaType"
        :is-executing="isPipelineExecuting"
        :progress="generationProgress"
        :is-analyzing="isAnalyzing"
        :show-analysis="showAnalysis"
        :analysis-data="imageAnalysis"
        forward-button-title="Erneut Transformieren"
        @save="saveMedia"
        @print="printImage"
        @forward="sendToI2I"
        @download="downloadMedia"
        @analyze="analyzeImage"
        @image-click="showImageFullscreen"
        @close-analysis="showAnalysis = false"
      />

    </div>

    <!-- Fullscreen Image Modal -->
    <Teleport to="body">
      <Transition name="modal-fade">
        <div v-if="fullscreenImage" class="fullscreen-modal" @click="fullscreenImage = null">
          <img :src="fullscreenImage" alt="Dein Bild" class="fullscreen-image" />
          <button class="close-fullscreen" @click="fullscreenImage = null">×</button>
        </div>
      </Transition>
    </Teleport>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import axios from 'axios'
import MediaOutputBox from '@/components/MediaOutputBox.vue'
import MediaInputBox from '@/components/MediaInputBox.vue'
import { useAppClipboard } from '@/composables/useAppClipboard'

const { copy: copyToClipboard, paste: pasteFromClipboard } = useAppClipboard()

const uploadedImage = ref<string | undefined>(undefined)
const uploadedImagePath = ref<string | undefined>(undefined)
const uploadedImageId = ref<string | undefined>(undefined)

const referenceImage = ref<string | undefined>(undefined)
const referenceImagePath = ref<string | undefined>(undefined)
const referenceImageId = ref<string | undefined>(undefined)

const selectedCategory = ref<string | null>(null)
const selectedConfig = ref<string | null>(null)
const hoveredConfigId = ref<string | null>(null)

const previousImageCombo = ref<string | null>(null)
const currentSeed = ref<number | null>(null)

const executionPhase = ref<'initial' | 'image_uploaded' | 'ready_for_media' | 'generation_done'>('initial')
const isPipelineExecuting = ref(false)
const outputImage = ref<string | null>(null)
const outputMediaType = ref<string>('image')
const fullscreenImage = ref<string | null>(null)
const showSafetyApprovedStamp = ref(false)
const generationProgress = ref(0)
const estimatedDurationSeconds = ref<string>('30')

const isAnalyzing = ref(false)
const imageAnalysis = ref<{
  analysis: string
  reflection_prompts: string[]
  insights: string[]
  success: boolean
} | null>(null)
const showAnalysis = ref(false)

const mainContainerRef = ref<HTMLElement | null>(null)
const categorySectionRef = ref<HTMLElement | null>(null)
const pipelineSectionRef = ref<any>(null)

interface Category {
  id: string
  label: string
  emoji: string
  color: string
  disabled?: boolean
}

const availableCategories: Category[] = [
  { id: 'image', label: 'Bild', emoji: '🖼️', color: '#4CAF50' },
  { id: 'video', label: 'Video', emoji: '🎬', color: '#9C27B0' },
  { id: 'sound', label: 'Sound', emoji: '🔊', color: '#FF9800', disabled: true }
]

interface ModelConfig {
  id: string
  label: string
  emoji: string
  name: string
  quality: number
  speed: number
  duration: string
  color: string
  logo?: string
  lightBg?: boolean
}

const configsByCategory: Record<string, ModelConfig[]> = {
  image: [
    {
      id: 'qwen2_vl_dual',
      label: 'Qwen2-VL',
      emoji: '🪷',
      name: 'Qwen2-VL Dual Image',
      quality: 4,
      speed: 4,
      duration: '28',
      color: '#9C27B0',
      logo: '/logos/Qwen_logo.png'
    },
    {
      id: 'flux2_img2img',
      label: 'Flux 2',
      emoji: '⚡',
      name: 'Flux2 Dev IMG2IMG',
      quality: 5,
      speed: 3,
      duration: '45',
      color: '#FF6B35',
      logo: '/logos/flux2_logo.png',
      lightBg: false
    },
    {
      id: 'kolors_xl_style_blend',
      label: 'Kolors XL',
      emoji: '🎨',
      name: 'Kolors XL Style Blend',
      quality: 5,
      speed: 3,
      duration: '55',
      color: '#4DB6AC',
      lightBg: true
    }
  ],
  video: [
    {
      id: 'wan22_i2v_video',
      label: 'WAN 2.2',
      emoji: '🎬',
      name: 'WAN 2.2 Image-to-Video (14B)',
      quality: 4,
      speed: 3,
      duration: '35',
      color: '#9C27B0',
      logo: '/logos/wan_logo.png',
      lightBg: false
    }
  ],
  sound: []
}

const configsForCategory = computed(() => {
  if (!selectedCategory.value) return []
  return configsByCategory[selectedCategory.value] || []
})

const canSelectMedia = computed(() => {
  return uploadedImage.value && referenceImage.value
})

const canStartGeneration = computed(() => {
  return (
    uploadedImage.value &&
    referenceImage.value &&
    selectedCategory.value &&
    selectedConfig.value &&
    !isPipelineExecuting.value
  )
})

function updateExecutionPhase() {
  if (uploadedImage.value && referenceImage.value) {
    executionPhase.value = 'ready_for_media'
  } else if (uploadedImage.value || referenceImage.value) {
    executionPhase.value = 'image_uploaded'
  } else {
    executionPhase.value = 'initial'
  }
}

function handleImageUpload(data: any) {
  uploadedImage.value = data.preview_url
  uploadedImagePath.value = data.image_path
  uploadedImageId.value = data.image_id
  updateExecutionPhase()
}

function handleReferenceImageUpload(data: any) {
  referenceImage.value = data.preview_url
  referenceImagePath.value = data.image_path
  referenceImageId.value = data.image_id
  updateExecutionPhase()
}

function clearImage() {
  handleImageRemove()
  sessionStorage.removeItem('i2i_dual_uploaded_image')
  sessionStorage.removeItem('i2i_dual_uploaded_image_path')
  sessionStorage.removeItem('i2i_dual_uploaded_image_id')
}

function clearReferenceImage() {
  handleReferenceImageRemove()
  sessionStorage.removeItem('i2i_dual_reference_image')
  sessionStorage.removeItem('i2i_dual_reference_image_path')
  sessionStorage.removeItem('i2i_dual_reference_image_id')
}

function copyUploadedImage() {
  if (!uploadedImage.value) return
  copyToClipboard(uploadedImage.value)
}

function copyReferenceImage() {
  if (!referenceImage.value) return
  copyToClipboard(referenceImage.value)
}

function base64ToBlob(dataUrl: string): Blob | null {
  try {
    const arr = dataUrl.split(',')
    const mime = arr[0].match(/:(.*?);/)?.[1] || 'image/png'
    const bstr = atob(arr[1])
    let n = bstr.length
    const u8arr = new Uint8Array(n)
    while (n--) {
      u8arr[n] = bstr.charCodeAt(n)
    }
    return new Blob([u8arr], { type: mime })
  } catch (error) {
    console.error('[base64ToBlob] Error converting Base64 to Blob:', error)
    return null
  }
}

async function uploadImageToBackend(imageBlob: Blob, filename: string = 'pasted-image.png'): Promise<string | null> {
  const formData = new FormData()
  formData.append('image', imageBlob, filename)

  try {
    const response = await axios.post('/api/upload_image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    if (response.data.status === 'success') {
      return response.data.image_path
    } else {
      console.error('[I2I] Upload failed:', response.data.error)
      return null
    }
  } catch (error: any) {
    console.error('[I2I] Upload error:', error)
    return null
  }
}

async function pasteUploadedImage() {
  await pasteGenericImage('primary')
}

async function pasteReferenceImage() {
  await pasteGenericImage('reference')
}

async function pasteGenericImage(target: 'primary' | 'reference') {
  const clipboardContent = pasteFromClipboard()
  if (!clipboardContent) return

  const isImageUrl = clipboardContent.startsWith('data:image/') ||
    clipboardContent.startsWith('/api/media/image/') ||
    clipboardContent.startsWith('http://') ||
    clipboardContent.startsWith('https://')

  if (!isImageUrl) return

  const setImage = (preview: string, path: string, id: string) => {
    if (target === 'primary') {
      uploadedImage.value = preview
      uploadedImagePath.value = path
      uploadedImageId.value = id
    } else {
      referenceImage.value = preview
      referenceImagePath.value = path
      referenceImageId.value = id
    }
    updateExecutionPhase()
  }

  if (!clipboardContent.startsWith('data:image/')) {
    const runIdMatch = clipboardContent.match(/\/api\/media\/image\/(.+)$/)
    setImage(clipboardContent, clipboardContent, runIdMatch ? runIdMatch[1] : `pasted_${Date.now()}`)
    return
  }

  const imageBlob = base64ToBlob(clipboardContent)
  if (!imageBlob) return

  const timestamp = Date.now()
  const filename = `pasted-image-${timestamp}.png`
  setImage(clipboardContent, clipboardContent, `pasted_${timestamp}`)

  const serverPath = await uploadImageToBackend(imageBlob, filename)
  if (serverPath) {
    setImage(serverPath, serverPath, `pasted_${timestamp}`)
  }
}

function handleImageRemove() {
  uploadedImage.value = undefined
  uploadedImagePath.value = undefined
  uploadedImageId.value = undefined
  selectedCategory.value = null
  selectedConfig.value = null
  hoveredConfigId.value = null
  outputImage.value = null
  isPipelineExecuting.value = false
  updateExecutionPhase()
}

function handleReferenceImageRemove() {
  referenceImage.value = undefined
  referenceImagePath.value = undefined
  referenceImageId.value = undefined
  selectedCategory.value = null
  selectedConfig.value = null
  hoveredConfigId.value = null
  outputImage.value = null
  isPipelineExecuting.value = false
  updateExecutionPhase()
}

function selectModel(modelId: string) {
  selectedConfig.value = modelId
}

async function selectCategory(categoryId: string) {
  selectedCategory.value = categoryId
  await nextTick()
  scrollDownOnly(categorySectionRef.value, 'start')
}

async function startGeneration() {
  if (!canStartGeneration.value) return

  isPipelineExecuting.value = true
  generationProgress.value = 0
  outputImage.value = null

  await nextTick()
  setTimeout(() => scrollDownOnly(pipelineSectionRef.value?.sectionRef, 'start'), 150)

  let durationSeconds = 30
  const durationStr = estimatedDurationSeconds.value

  if (durationStr.includes('-')) {
    durationSeconds = parseInt(durationStr.split('-')[0] || '30')
  } else {
    durationSeconds = parseInt(durationStr)
  }

  if (durationSeconds === 0 || isNaN(durationSeconds)) {
    durationSeconds = 5
  }

  durationSeconds = durationSeconds * 0.9
  const targetProgress = 98
  const updateInterval = 100
  const totalUpdates = (durationSeconds * 1000) / updateInterval
  const progressPerUpdate = targetProgress / totalUpdates

  const progressInterval = setInterval(() => {
    if (generationProgress.value < targetProgress) {
      generationProgress.value += progressPerUpdate
      if (generationProgress.value > targetProgress) {
        generationProgress.value = targetProgress
      }
    }
  }, updateInterval)

  const comboKey = `${uploadedImageId.value || uploadedImagePath.value}-${referenceImageId.value || referenceImagePath.value}`
  const comboChanged = comboKey !== previousImageCombo.value
  if (comboChanged || currentSeed.value === null) {
    currentSeed.value = Math.floor(Math.random() * 1000000000)
  }
  previousImageCombo.value = comboKey

  try {
    const response = await axios.post('/api/schema/pipeline/execute', {
      schema: 'image_pair_transformation',
      input_image: uploadedImagePath.value,
      reference_image: referenceImagePath.value,
      output_config: selectedConfig.value,
      user_language: 'de',
      safety_level: 'youth',
      seed: currentSeed.value
    })

    if (response.data.status === 'success') {
      clearInterval(progressInterval)
      generationProgress.value = 100

      const runId = response.data.media_output?.run_id || response.data.run_id
      const mediaType = response.data.media_output?.media_type || 'image'

      if (runId) {
        outputMediaType.value = mediaType
        outputImage.value = `/api/media/${mediaType}/${runId}`
        executionPhase.value = 'generation_done'
        showSafetyApprovedStamp.value = true

        setTimeout(() => {
          showSafetyApprovedStamp.value = false
        }, 3000)

        await nextTick()
        setTimeout(() => scrollDownOnly(pipelineSectionRef.value?.sectionRef, 'start'), 150)
      }
    } else {
      clearInterval(progressInterval)
      alert(`Generation fehlgeschlagen: ${response.data.error}`)
      generationProgress.value = 0
    }
  } catch (error: any) {
    clearInterval(progressInterval)
    alert('Fehler bei der Generierung: ' + (error.response?.data?.error || error.message))
    generationProgress.value = 0
  } finally {
    isPipelineExecuting.value = false
  }
}

function showImageFullscreen(imageUrl: string) {
  fullscreenImage.value = imageUrl
}

function scrollDownOnly(element: HTMLElement | null, block: ScrollLogicalPosition = 'start') {
  if (!element) return
  const rect = element.getBoundingClientRect()
  const targetTop = block === 'start' ? rect.top : rect.bottom - window.innerHeight
  if (targetTop > 0) {
    element.scrollIntoView({ behavior: 'smooth', block })
  }
}

function saveMedia() {
  alert('Speichern-Funktion kommt bald!')
}

function printImage() {
  if (!outputImage.value) return
  const printWindow = window.open('', '_blank')
  if (printWindow) {
    printWindow.document.write(`
      <html><head><title>Druck: Transformiertes Bild</title></head>
      <body style="margin:0;display:flex;justify-content:center;align-items:center;height:100vh;">
        <img src="${outputImage.value}" style="max-width:100%;max-height:100%;" onload="window.print();window.close()">
      </body></html>
    `)
    printWindow.document.close()
  }
}

function sendToI2I() {
  if (!outputImage.value || outputMediaType.value !== 'image') return

  uploadedImage.value = outputImage.value
  uploadedImagePath.value = outputImage.value
  uploadedImageId.value = `retransform_${Date.now()}`
  outputImage.value = null
  isPipelineExecuting.value = false
  executionPhase.value = 'image_uploaded'
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

async function downloadMedia() {
  if (!outputImage.value) return

  try {
    const response = await fetch(outputImage.value)
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url

    const timestamp = new Date().toISOString().slice(0, 19).replace(/[:]/g, '-')
    const ext = outputMediaType.value === 'video' ? 'mp4' :
                outputMediaType.value === 'audio' || outputMediaType.value === 'music' ? 'mp3' :
                'png'
    a.download = `ai4artsed_i2i_dual_${timestamp}.${ext}`

    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    alert('Fehler beim Herunterladen')
  }
}

async function analyzeImage() {
  if (!outputImage.value || isAnalyzing.value) return

  isAnalyzing.value = true

  try {
    const response = await fetch('/api/image/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        image_url: outputImage.value,
        reference_image: referenceImagePath.value || '',
        context: ''
      })
    })

    const data = await response.json()

    if (data.success) {
      imageAnalysis.value = {
        analysis: data.analysis || '',
        reflection_prompts: data.reflection_prompts || [],
        insights: data.insights || [],
        success: true
      }
      showAnalysis.value = true
    } else {
      alert('Bildanalyse fehlgeschlagen')
    }
  } catch (error) {
    alert('Fehler bei der Bildanalyse')
  } finally {
    isAnalyzing.value = false
  }
}

onMounted(() => {
  const savedPrimary = sessionStorage.getItem('i2i_dual_uploaded_image')
  const savedPrimaryPath = sessionStorage.getItem('i2i_dual_uploaded_image_path')
  const savedPrimaryId = sessionStorage.getItem('i2i_dual_uploaded_image_id')

  if (savedPrimary) {
    uploadedImage.value = savedPrimary
    uploadedImagePath.value = savedPrimaryPath || savedPrimary
    uploadedImageId.value = savedPrimaryId || `restored_${Date.now()}`
  }

  const savedReference = sessionStorage.getItem('i2i_dual_reference_image')
  const savedReferencePath = sessionStorage.getItem('i2i_dual_reference_image_path')
  const savedReferenceId = sessionStorage.getItem('i2i_dual_reference_image_id')

  if (savedReference) {
    referenceImage.value = savedReference
    referenceImagePath.value = savedReferencePath || savedReference
    referenceImageId.value = savedReferenceId || `restored_${Date.now()}`
  }

  updateExecutionPhase()
})

watch(uploadedImage, (newVal) => {
  if (newVal) {
    sessionStorage.setItem('i2i_dual_uploaded_image', newVal)
  } else {
    sessionStorage.removeItem('i2i_dual_uploaded_image')
  }
})

watch(uploadedImagePath, (newVal) => {
  if (newVal) {
    sessionStorage.setItem('i2i_dual_uploaded_image_path', newVal)
  } else {
    sessionStorage.removeItem('i2i_dual_uploaded_image_path')
  }
})

watch(uploadedImageId, (newVal) => {
  if (newVal) {
    sessionStorage.setItem('i2i_dual_uploaded_image_id', newVal)
  } else {
    sessionStorage.removeItem('i2i_dual_uploaded_image_id')
  }
})

watch(referenceImage, (newVal) => {
  if (newVal) {
    sessionStorage.setItem('i2i_dual_reference_image', newVal)
  } else {
    sessionStorage.removeItem('i2i_dual_reference_image')
  }
})

watch(referenceImagePath, (newVal) => {
  if (newVal) {
    sessionStorage.setItem('i2i_dual_reference_image_path', newVal)
  } else {
    sessionStorage.removeItem('i2i_dual_reference_image_path')
  }
})

watch(referenceImageId, (newVal) => {
  if (newVal) {
    sessionStorage.setItem('i2i_dual_reference_image_id', newVal)
  } else {
    sessionStorage.removeItem('i2i_dual_reference_image_id')
  }
})
</script></script>

<style scoped>
/* ============================================================================
   Root Container
   ============================================================================ */

.image-pair-transformation-view {
  min-height: 100%;
  background: #0a0a0a;
  color: #ffffff;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  overflow-y: auto;
  overflow-x: hidden;
}

/* ============================================================================
   Phase 2a: Vertical Flow
   ============================================================================ */

.phase-2a {
  max-width: clamp(320px, 90vw, 1100px);
  width: 100%;
  padding: clamp(1rem, 3vw, 2rem);
  padding-top: clamp(1rem, 3vw, 2rem); /* Reduced - App.vue header is smaller now */

  display: flex;
  flex-direction: column;
  align-items: center;
  gap: clamp(1rem, 3vh, 2rem);
}

/* ============================================================================
   Input + Context Section (Side by Side)
   ============================================================================ */

.input-context-section {
  display: flex;
  gap: clamp(0.75rem, 2vw, 1.5rem);
  width: 100%;
  max-width: 1000px;
  align-items: stretch;
}

.input-bubble,
.context-bubble {
  flex: 1;
  min-width: 0;
}

@media (max-width: 768px) {
  .input-context-section {
    flex-direction: column;
  }
}

/* ============================================================================
   Bubble Cards (Input/Context)
   ============================================================================ */

.bubble-card {
  background: rgba(20, 20, 20, 0.9);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: clamp(12px, 2vw, 20px);
  padding: clamp(1rem, 2.5vw, 1.5rem);
  transition: all 0.3s ease;
  width: 100%;
  max-width: 1000px;
  display: flex;
  flex-direction: column;
}

.bubble-card.filled {
  border-color: rgba(102, 126, 234, 0.6);
  background: rgba(102, 126, 234, 0.1);
}

.bubble-card.required {
  border-color: rgba(255, 193, 7, 0.6);
  background: rgba(255, 193, 7, 0.05);
  animation: pulse-required 2s ease-in-out infinite;
}

@keyframes pulse-required {
  0%, 100% {
    border-color: rgba(255, 193, 7, 0.6);
  }
  50% {
    border-color: rgba(255, 193, 7, 0.9);
  }
}

.bubble-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.bubble-icon {
  font-size: clamp(1.25rem, 3vw, 1.5rem);
  flex-shrink: 0;
}

.bubble-label {
  font-size: clamp(0.9rem, 2vw, 1rem);
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.bubble-actions {
  display: flex;
  gap: 0.25rem;
  margin-left: auto;
}

.action-btn {
  background: transparent;
  border: none;
  font-size: 0.9rem;
  opacity: 0.4;
  cursor: pointer;
  transition: opacity 0.2s;
  padding: 0.25rem;
}

.action-btn:hover {
  opacity: 0.8;
}

.bubble-textarea {
  width: 100%;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: white;
  font-size: clamp(0.9rem, 2vw, 1rem);
  padding: clamp(0.5rem, 1.5vw, 0.75rem);
  resize: vertical;
  font-family: inherit;
  line-height: 1.4;
  flex-grow: 1;
  min-height: 0;
}

.bubble-textarea:focus {
  outline: none;
  border-color: rgba(102, 126, 234, 0.8);
  background: rgba(0, 0, 0, 0.4);
}

.bubble-textarea::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

/* ============================================================================
   Section: Image Upload & Context
   ============================================================================ */

.image-upload-section,
.context-section {
  width: 100%;
  display: flex;
  justify-content: center;
}

/* ============================================================================
   Section 3: Category Bubbles (Horizontal Row)
   ============================================================================ */

.category-section {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.category-bubbles-row {
  display: flex;
  flex-direction: row;
  gap: clamp(1rem, 2.5vw, 1.5rem);
  justify-content: center;
  flex-wrap: wrap;
}

.category-bubble {
  width: clamp(70px, 12vw, 90px);
  height: clamp(70px, 12vw, 90px);

  display: flex;
  align-items: center;
  justify-content: center;

  background: rgba(30, 30, 30, 0.9);
  border: 3px solid var(--bubble-color, rgba(255, 255, 255, 0.3));
  border-radius: 50%;

  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  outline: none;
}

.category-bubble:hover {
  transform: scale(1.08);
  box-shadow: 0 0 20px var(--bubble-color);
  border-width: 4px;
}

.category-bubble.selected {
  transform: scale(1.15);
  background: var(--bubble-color);
  box-shadow: 0 0 30px var(--bubble-color),
              0 0 60px var(--bubble-color);
  border-color: #ffffff;
}

.category-bubble:focus-visible {
  outline: 3px solid rgba(102, 126, 234, 0.8);
  outline-offset: 4px;
}

.category-bubble:active {
  transform: scale(0.95);
}

.category-bubble.disabled {
  opacity: 0.3;
  cursor: not-allowed;
  pointer-events: none;
  filter: grayscale(1);
}

.bubble-emoji-small {
  font-size: clamp(2rem, 4.5vw, 2.5rem);
  line-height: 1;
  transition: filter 0.3s ease;
}

.category-bubble.selected .bubble-emoji-small {
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.5));
}

/* ============================================================================
   Start Button Container
   ============================================================================ */

.start-button-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: clamp(1rem, 3vw, 2rem);
  flex-wrap: wrap;
}

/* ============================================================================
   Start Button
   ============================================================================ */

.start-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: clamp(0.5rem, 1.5vw, 0.75rem);
  padding: clamp(0.75rem, 2vw, 1rem) clamp(1.5rem, 4vw, 2.5rem);
  font-size: clamp(1rem, 2.5vw, 1.2rem);
  font-weight: 700;
  background: #000000;
  color: #FFB300;
  border: 3px solid #FFB300;
  border-radius: 16px;
  cursor: pointer;
  box-shadow: 0 0 20px rgba(255, 179, 0, 0.4),
              0 4px 15px rgba(0, 0, 0, 0.5);
  text-shadow: 0 0 10px rgba(255, 179, 0, 0.6);
  transition: all 0.3s ease;
}

.button-arrows {
  font-size: clamp(0.9rem, 2vw, 1.1rem);
}

.button-arrows-left {
  animation: arrow-pulse-left 1.5s ease-in-out infinite;
}

.button-arrows-right {
  animation: arrow-pulse-right 1.5s ease-in-out infinite;
}

.button-text {
  font-size: clamp(1rem, 2.5vw, 1.2rem);
}

@keyframes arrow-pulse-left {
  0%, 100% {
    opacity: 0.4;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.2);
  }
}

@keyframes arrow-pulse-right {
  0%, 100% {
    opacity: 1;
    transform: scale(1.2);
  }
  50% {
    opacity: 0.4;
    transform: scale(1);
  }
}

.start-button:hover {
  transform: scale(1.05) translateY(-2px);
  box-shadow: 0 0 30px rgba(255, 179, 0, 0.6),
              0 6px 25px rgba(0, 0, 0, 0.6);
  border-color: #FF8F00;
}

.start-button:active {
  transform: scale(0.98);
}

.start-button.disabled,
.start-button:disabled {
  opacity: 0.3;
  cursor: not-allowed;
  pointer-events: none;
  filter: grayscale(0.8);
  box-shadow: none;
  text-shadow: none;
}

.start-button.disabled .button-arrows,
.start-button:disabled .button-arrows {
  animation: none;
  opacity: 0.3;
}

/* Safety Approved Stamp */
.safety-stamp {
  display: flex;
  justify-content: center;
  align-items: center;
}

.stamp-inner {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: clamp(0.4rem, 1.5vw, 0.6rem) clamp(0.8rem, 2.5vw, 1.2rem);
  background: rgba(76, 175, 80, 0.15);
  border: 2px solid #4CAF50;
  border-radius: 12px;
  box-shadow: 0 0 20px rgba(76, 175, 80, 0.3);
  animation: stamp-appear 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes stamp-appear {
  0% {
    opacity: 0;
    transform: scale(0.5) rotate(-10deg);
  }
  100% {
    opacity: 1;
    transform: scale(1) rotate(0deg);
  }
}

.stamp-icon {
  font-size: clamp(1.2rem, 3vw, 1.5rem);
  color: #4CAF50;
  font-weight: bold;
  line-height: 1;
}

.stamp-text {
  font-size: clamp(0.65rem, 1.5vw, 0.75rem);
  font-weight: 700;
  color: #4CAF50;
  text-align: center;
  line-height: 1.2;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Output box styles moved to MediaOutputBox.vue component */

/* ============================================================================
   Fullscreen Modal
   ============================================================================ */

.fullscreen-modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.95);
  backdrop-filter: blur(8px);
  z-index: 10000;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.fullscreen-image {
  max-width: 90vw;
  max-height: 90vh;
  object-fit: contain;
  border-radius: 8px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.close-fullscreen {
  position: absolute;
  top: 2rem;
  right: 2rem;
  width: 4rem;
  height: 4rem;
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid white;
  color: white;
  font-size: 2.5rem;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.close-fullscreen:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.1);
}

/* ============================================================================
   Transitions
   ============================================================================ */

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

/* ============================================================================
   Responsive: Mobile Adjustments
   ============================================================================ */

@media (max-width: 768px) {
  .category-bubbles-row {
    gap: 1rem;
  }
}

/* iPad 1024×768 Optimization */
@media (min-width: 1024px) and (max-height: 768px) {
  .phase-2a {
    padding: 1.5rem;
    gap: 1.25rem;
  }
}

/* ============================================================================
   Model Selection Bubbles (copied from text_transformation.vue)
   ============================================================================ */

.config-section {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.config-bubbles-container {
  width: 100%;
  display: flex;
  justify-content: center;
}

.config-bubbles-row {
  display: inline-flex;
  flex-direction: row;
  gap: clamp(0.75rem, 2vw, 1rem);
  justify-content: center;
  flex-wrap: wrap;
  max-width: fit-content;
}

.config-bubble {
  position: relative;
  z-index: 1;
  width: clamp(80px, 12vw, 100px);
  height: clamp(80px, 12vw, 100px);
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(30, 30, 30, 0.9);
  border: 3px solid var(--bubble-color, rgba(255, 255, 255, 0.3));
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  outline: none;
}

.config-bubble:hover:not(.disabled),
.config-bubble.hovered {
  transform: scale(2.0);
  background: rgba(20, 20, 20, 0.9);
  box-shadow: 0 0 30px var(--bubble-color);
  z-index: 100;
}

.config-bubble.selected {
  transform: scale(1.1);
  background: var(--bubble-color);
  box-shadow: 0 0 30px var(--bubble-color);
  border-color: #ffffff;
}

.config-bubble.disabled {
  opacity: 0.3;
  cursor: not-allowed;
  pointer-events: none;
  filter: grayscale(0.8);
}

.bubble-emoji-medium {
  font-size: clamp(2.5rem, 5vw, 3.5rem);
  line-height: 1;
}

.bubble-logo {
  width: clamp(72px, 11vw, 92px);
  height: clamp(72px, 11vw, 92px);
  object-fit: contain;
}

.config-bubble.light-bg {
  background: rgba(255, 255, 255, 0.95);
}

.config-bubble.light-bg.selected {
  background: var(--bubble-color);
}

/* Hover info overlay */
.bubble-hover-info {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 18%;
  color: white;
  z-index: 10;
  pointer-events: none;
  gap: 0.3rem;
}

.hover-info-name {
  font-size: 0.5rem;
  font-weight: 600;
  text-align: center;
  line-height: 1.25;
  margin-bottom: 0;
  letter-spacing: -0.01em;
  color: rgba(255, 255, 255, 0.95);
  max-width: 100%;
  word-wrap: break-word;
}

.hover-info-meta {
  display: flex;
  flex-direction: column;
  gap: 0;
  width: 100%;
}

.meta-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.18rem;
  width: 100%;
  line-height: 1;
  margin: 0;
  padding: 0;
}

.meta-label {
  font-size: 0.45rem;
  color: rgba(255, 255, 255, 0.75);
  font-weight: 400;
  text-align: left;
  flex-shrink: 0;
  flex-basis: 35%;
  letter-spacing: -0.01em;
}

.meta-value {
  font-size: 0.65rem;
  font-weight: 500;
  text-align: right;
  white-space: nowrap;
  flex-shrink: 0;
  flex-basis: 60%;
  letter-spacing: 0.02em;
}

.stars-filled {
  color: #FFD700;
}

.stars-unfilled {
  color: rgba(150, 150, 150, 0.5);
}

.meta-value.duration-only {
  width: 100%;
  text-align: center;
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.45rem;
  flex-basis: auto;
  margin-top: 0.25rem;
  line-height: 1;
}

/* Hide logo/emoji when hovering */
.config-bubble.hovered .bubble-logo,
.config-bubble.hovered .bubble-emoji-medium {
  opacity: 0;
  display: none;
}

/* Action toolbar and analysis styles moved to MediaOutputBox.vue component */
</style>
