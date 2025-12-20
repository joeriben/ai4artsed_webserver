<template>
  <div class="image-upload-widget">
    <!-- Drop Zone -->
    <div
      class="drop-zone"
      :class="{ 'drag-over': isDragging, 'has-image': previewUrl }"
      @drop.prevent="handleDrop"
      @dragover.prevent="isDragging = true"
      @dragleave="isDragging = false"
      @click="triggerFileInput"
    >
      <!-- Preview -->
      <div v-if="previewUrl" class="image-preview">
        <img :src="previewUrl" alt="Uploaded image preview" />

        <!-- DEPRECATED 2025-12-15: Maske malen Button (not used, text-guided editing sufficient) -->
        <!--
        <button
          class="btn-create-mask"
          @click.stop="openMaskEditor"
          title="Maske für Inpainting erstellen"
        >
          🎨 Maske malen
        </button>
        -->

        <button class="remove-btn" @click.stop="removeImage" title="Bild entfernen">
          ✕
        </button>
      </div>

      <!-- Upload Prompt -->
      <div v-else class="upload-prompt">
        <div class="upload-icon">🖼️</div>
        <p class="upload-text">
          <strong>Klicke hier</strong> oder ziehe ein Bild hierher
        </p>
        <p class="upload-hint">PNG, JPG, WEBP (max 10MB)</p>
      </div>
    </div>

    <!-- Hidden File Input -->
    <input
      ref="fileInput"
      type="file"
      accept="image/png,image/jpeg,image/jpg,image/webp"
      @change="handleFileSelect"
      style="display: none"
    />

    <!-- Error Message -->
    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <!-- Upload Info -->
    <div v-if="uploadInfo" class="upload-info">
      <span class="info-label">Original:</span> {{ uploadInfo.original_size[0] }}×{{ uploadInfo.original_size[1] }}px
      <span v-if="wasResized" class="resize-badge">
        → {{ uploadInfo.resized_size[0] }}×{{ uploadInfo.resized_size[1] }}px
      </span>
      <span class="info-label">Größe:</span> {{ (uploadInfo.file_size_bytes / 1024).toFixed(1) }}KB
      <!-- DEPRECATED 2025-12-15: Mask badge (not used) -->
      <!--
      <span v-if="hasMask" class="mask-badge">
        🎨 Maske vorhanden
      </span>
      -->
    </div>

    <!-- DEPRECATED 2025-12-15: Mask Editor Modal (not used, text-guided editing sufficient) -->
    <!--
    <Teleport to="body">
      <div v-if="showMaskEditor" class="mask-editor-modal" @click="closeMaskEditor">
        <div class="mask-editor-content" @click.stop>
          <SimpleMaskEditor
            :image-url="previewUrl!"
            @save="handleMaskSave"
            @cancel="closeMaskEditor"
          />
        </div>
      </div>
    </Teleport>
    -->
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import axios from 'axios'
// DEPRECATED 2025-12-15: SimpleMaskEditor not actively used (text-guided editing sufficient)
// import SimpleMaskEditor from './SimpleMaskEditor.vue'

// Props
interface Props {
  maxSizeMB?: number
  initialImage?: string | null  // URL to pre-load image
}

const props = withDefaults(defineProps<Props>(), {
  maxSizeMB: 10,
  initialImage: null
})

// Emits
const emit = defineEmits<{
  'image-uploaded': [data: {
    image_id: string
    image_path: string
    filename: string
    preview_url: string
    upload_info: any
  }]
  'image-removed': []
}>()

// State
const fileInput = ref<HTMLInputElement | null>(null)
const previewUrl = ref<string | null>(null)
const isDragging = ref(false)
const error = ref<string | null>(null)
const uploadInfo = ref<any>(null)

// DEPRECATED 2025-12-15: Mask Editor State (not used, text-guided editing sufficient)
// const showMaskEditor = ref(false)
// const maskBlob = ref<Blob | null>(null)
// const hasMask = ref(false)

// Computed
const wasResized = computed(() => {
  if (!uploadInfo.value) return false
  const orig = uploadInfo.value.original_size
  const resized = uploadInfo.value.resized_size
  return orig[0] !== resized[0] || orig[1] !== resized[1]
})

// Allowed file types
const ALLOWED_TYPES = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp']

// Methods
function triggerFileInput() {
  if (!previewUrl.value) {
    fileInput.value?.click()
  }
}

function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    processFile(file)
  }
}

function handleDrop(event: DragEvent) {
  isDragging.value = false
  const file = event.dataTransfer?.files[0]
  if (file) {
    processFile(file)
  }
}

async function processFile(file: File) {
  error.value = null

  // Validate file type
  if (!ALLOWED_TYPES.includes(file.type)) {
    error.value = 'Ungültiges Dateiformat. Nur PNG, JPG und WEBP erlaubt.'
    return
  }

  // Validate file size
  const maxBytes = props.maxSizeMB * 1024 * 1024
  if (file.size > maxBytes) {
    error.value = `Datei zu groß. Maximum: ${props.maxSizeMB}MB`
    return
  }

  // Create preview
  const reader = new FileReader()
  reader.onload = (e) => {
    previewUrl.value = e.target?.result as string
  }
  reader.readAsDataURL(file)

  // Upload to server
  try {
    const formData = new FormData()
    formData.append('file', file)

    // DEPRECATED 2025-12-15: Maske hinzufügen falls vorhanden (not used, text-guided editing sufficient)
    // if (maskBlob.value) {
    //   formData.append('mask', maskBlob.value, 'mask.png')
    //   console.log('[ImageUploadWidget] Uploading with mask:', maskBlob.value.size, 'bytes')
    // }

    const response = await axios.post('/api/media/upload/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    if (response.data.success) {
      uploadInfo.value = response.data

      emit('image-uploaded', {
        image_id: response.data.image_id,
        image_path: response.data.image_path,
        filename: response.data.filename,
        preview_url: previewUrl.value!,
        upload_info: response.data
      })
    } else {
      error.value = 'Upload fehlgeschlagen'
      previewUrl.value = null
    }
  } catch (err: any) {
    console.error('Upload error:', err)
    error.value = err.response?.data?.error || 'Upload fehlgeschlagen'
    previewUrl.value = null
  }
}

function removeImage() {
  previewUrl.value = null
  uploadInfo.value = null
  error.value = null
  // DEPRECATED 2025-12-15: Mask cleanup (not used)
  // maskBlob.value = null
  // hasMask.value = false
  if (fileInput.value) {
    fileInput.value.value = ''
  }
  emit('image-removed')
}

// DEPRECATED 2025-12-15: Mask Editor Functions (not used, text-guided editing sufficient)
/*
function openMaskEditor() {
  if (!previewUrl.value) return
  showMaskEditor.value = true
}

function closeMaskEditor() {
  showMaskEditor.value = false
}

async function handleMaskSave(blob: Blob) {
  console.log('[ImageUploadWidget] Mask saved:', blob.size, 'bytes')
  maskBlob.value = blob
  hasMask.value = true
  showMaskEditor.value = false

  // Optional: Re-upload image with mask immediately
  // For now, mask will be sent on next upload
}
*/

// Watch for initial image prop changes
watch(() => props.initialImage, (newImage) => {
  console.log('[ImageUploadWidget] Initial image changed:', newImage)
  // Always sync previewUrl with initialImage (including null/empty)
  previewUrl.value = newImage || null
}, { immediate: true })

// Load initial image on mount (if provided)
onMounted(() => {
  if (props.initialImage) {
    console.log('[ImageUploadWidget] Mounted with initial image:', props.initialImage)
    previewUrl.value = props.initialImage
  }
})
</script>

<style scoped>
.image-upload-widget {
  width: 100%;
}

.drop-zone {
  width: 100%;
  min-height: 200px;
  border: 2px dashed #4a8f4d;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: rgba(0, 0, 0, 0.3);
  position: relative;
}

.drop-zone:hover {
  border-color: #5fb563;
  background: rgba(74, 143, 77, 0.1);
}

.drop-zone.drag-over {
  border-color: #76c77b;
  background: rgba(74, 143, 77, 0.2);
  border-style: solid;
}

.drop-zone.has-image {
  cursor: default;
  border-color: #4a8f4d;
}

.drop-zone.has-image:hover {
  background: rgba(0, 0, 0, 0.3);
}

/* Upload Prompt */
.upload-prompt {
  text-align: center;
  padding: 2rem;
}

.upload-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.7;
}

.upload-text {
  font-size: 1.1rem;
  color: #e0e0e0;
  margin-bottom: 0.5rem;
}

.upload-text strong {
  color: #fff;
}

.upload-hint {
  font-size: 0.9rem;
  color: #999;
}

/* Image Preview */
.image-preview {
  width: 100%;
  height: 100%;
  min-height: 200px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.image-preview img {
  max-width: 100%;
  max-height: 400px;
  border-radius: 8px;
  object-fit: contain;
}

.remove-btn {
  position: absolute;
  top: 1rem;
  right: 1rem;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 0, 0, 0.8);
  color: white;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  z-index: 10;
}

.remove-btn:hover {
  background: rgba(255, 0, 0, 1);
  transform: scale(1.1);
}

/* Error Message */
.error-message {
  margin-top: 0.5rem;
  padding: 0.5rem 1rem;
  background: rgba(255, 0, 0, 0.2);
  border: 1px solid rgba(255, 0, 0, 0.5);
  border-radius: 6px;
  color: #ff6b6b;
  font-size: 0.9rem;
}

/* Upload Info */
.upload-info {
  margin-top: 0.5rem;
  padding: 0.5rem 1rem;
  background: rgba(74, 143, 77, 0.2);
  border: 1px solid rgba(74, 143, 77, 0.5);
  border-radius: 6px;
  font-size: 0.85rem;
  color: #b0e0b3;
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.info-label {
  color: #76c77b;
  font-weight: 600;
}

.resize-badge {
  color: #FFB300;
}

.mask-badge {
  color: #4a9eff;
  font-weight: 600;
}

/* NEU: Maske malen Button */
.btn-create-mask {
  position: absolute;
  bottom: 1rem;
  left: 1rem;
  padding: 0.6rem 1.2rem;
  background: rgba(74, 158, 255, 0.9);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 500;
  transition: all 0.2s ease;
  z-index: 9;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-create-mask:hover {
  background: rgba(74, 158, 255, 1);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(74, 158, 255, 0.4);
}

/* NEU: Mask Editor Modal */
.mask-editor-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  animation: fadeIn 0.2s ease;
}

.mask-editor-content {
  width: 90vw;
  max-width: 1200px;
  height: 85vh;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
  animation: slideUp 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    transform: translateY(50px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}
</style>
