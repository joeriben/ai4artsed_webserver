<template>
  <div class="multi-image-transformation-view">

    <div class="phase-2a" ref="mainContainerRef">

      <!-- Section 1: Three Image Upload Boxes -->
      <section class="input-images-section">
        <!-- Image 1 (Required) -->
        <MediaInputBox
          icon="🖼️"
          :label="$t('multiImage.image1Label')"
          :value="uploadedImage1 ?? ''"
          @update:value="(val: string) => uploadedImage1 = val || undefined"
          input-type="image"
          :initial-image="uploadedImage1"
          @image-uploaded="handleImage1Upload"
          @image-removed="handleImage1Remove"
        />

        <!-- Image 2 (Optional) -->
        <MediaInputBox
          icon="➕"
          :label="$t('multiImage.image2Label')"
          :value="uploadedImage2 ?? ''"
          @update:value="(val: string) => uploadedImage2 = val || undefined"
          input-type="image"
          :initial-image="uploadedImage2"
          @image-uploaded="handleImage2Upload"
          @image-removed="handleImage2Remove"
        />

        <!-- Image 3 (Optional) -->
        <MediaInputBox
          icon="➕"
          :label="$t('multiImage.image3Label')"
          :value="uploadedImage3 ?? ''"
          @update:value="(val: string) => uploadedImage3 = val || undefined"
          input-type="image"
          :initial-image="uploadedImage3"
          @image-uploaded="handleImage3Upload"
          @image-removed="handleImage3Remove"
        />
      </section>

      <!-- Section 2: Context Prompt -->
      <section class="context-section">
        <MediaInputBox
          icon="📋"
          :label="$t('multiImage.contextLabel')"
          :placeholder="$t('multiImage.contextPlaceholder')"
          v-model:value="contextPrompt"
          input-type="text"
          :rows="6"
          :is-filled="!!contextPrompt"
          :is-required="!contextPrompt"
        />
      </section>

      <!-- Section 3: Category Selection (only show when ready) -->
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
          >
            <span class="category-icon">{{ category.icon }}</span>
            <span class="category-label">{{ category.name }}</span>
          </div>
        </div>
      </section>

      <!-- Section 4: Config Selection (only show when category selected) -->
      <section v-if="selectedCategory && canSelectConfig" class="config-section">
        <h3>{{ $t('multiImage.selectConfig') }}</h3>
        <div class="config-cards">
          <div
            v-for="config in availableConfigs"
            :key="config.name"
            class="config-card"
            :class="{ selected: selectedConfig === config.name }"
            @click="selectConfig(config.name)"
          >
            <span class="config-icon">{{ config.ui_config?.icon || '🎨' }}</span>
            <span class="config-name">{{ config.display_name }}</span>
            <span class="config-badge" v-if="config.ui_config?.badge">{{ config.ui_config.badge }}</span>
          </div>
        </div>
      </section>

      <!-- Section 5: Generate Button -->
      <section v-if="canGenerate" class="generate-section">
        <button
          class="generate-button"
          @click="executeGeneration"
          :disabled="isGenerating"
        >
          {{ isGenerating ? $t('multiImage.generating') : $t('phase2.generateMedia') }}
        </button>
      </section>

      <!-- Section 6: Output Display -->
      <section v-if="generatedImageUrl" class="output-section">
        <h3>{{ $t('pipeline.generatedMedia') }}</h3>
        <img :src="generatedImageUrl" alt="Generated image" class="generated-image" />
      </section>

    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import MediaInputBox from '@/components/MediaInputBox.vue'

const { t } = useI18n()

// Image upload state (3 images)
const uploadedImage1 = ref<string | undefined>(undefined)
const uploadedImagePath1 = ref<string | undefined>(undefined)
const uploadedImage2 = ref<string | undefined>(undefined)
const uploadedImagePath2 = ref<string | undefined>(undefined)
const uploadedImage3 = ref<string | undefined>(undefined)
const uploadedImagePath3 = ref<string | undefined>(undefined)

// Context prompt
const contextPrompt = ref<string>('')

// Execution state
const executionPhase = ref<'initial' | 'images_uploaded' | 'ready_for_media' | 'generation_done'>('initial')
const isGenerating = ref(false)

// Category & Config selection
const selectedCategory = ref<string | null>(null)
const selectedConfig = ref<string | null>(null)
const availableCategories = ref<any[]>([])
const availableConfigs = ref<any[]>([])

// Output
const generatedImageUrl = ref<string | null>(null)

// Refs
const mainContainerRef = ref<HTMLElement | null>(null)
const categorySectionRef = ref<HTMLElement | null>(null)

// === COMPUTED === //

const canSelectMedia = computed(() => {
  return uploadedImagePath1.value && contextPrompt.value.trim().length > 0
})

const canSelectConfig = computed(() => {
  return selectedCategory.value && availableConfigs.value.length > 0
})

const canGenerate = computed(() => {
  return canSelectConfig.value && selectedConfig.value
})

// === IMAGE UPLOAD HANDLERS === //

function handleImage1Upload(data: any) {
  console.log('[Image 1 Upload] Success:', data)
  uploadedImage1.value = data.preview_url
  uploadedImagePath1.value = data.image_path
  executionPhase.value = 'images_uploaded'
  checkIfReadyForMedia()
}

function handleImage1Remove() {
  uploadedImage1.value = undefined
  uploadedImagePath1.value = undefined
}

function handleImage2Upload(data: any) {
  console.log('[Image 2 Upload] Success:', data)
  uploadedImage2.value = data.preview_url
  uploadedImagePath2.value = data.image_path
}

function handleImage2Remove() {
  uploadedImage2.value = undefined
  uploadedImagePath2.value = undefined
}

function handleImage3Upload(data: any) {
  console.log('[Image 3 Upload] Success:', data)
  uploadedImage3.value = data.preview_url
  uploadedImagePath3.value = data.image_path
}

function handleImage3Remove() {
  uploadedImage3.value = undefined
  uploadedImagePath3.value = undefined
}

function checkIfReadyForMedia() {
  if (canSelectMedia.value) {
    executionPhase.value = 'ready_for_media'
    // Scroll to category section
    setTimeout(() => {
      categorySectionRef.value?.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }, 100)
  }
}

// === CATEGORY & CONFIG === //

async function loadCategories() {
  try {
    const response = await axios.get('/api/config/categories')
    availableCategories.value = response.data.categories || []
  } catch (error) {
    console.error('[Categories] Failed to load:', error)
  }
}

function selectCategory(categoryId: string) {
  selectedCategory.value = categoryId
  selectedConfig.value = null
  loadConfigsForCategory(categoryId)
}

async function loadConfigsForCategory(categoryId: string) {
  try {
    const response = await axios.get(`/api/config/category/${categoryId}`)
    // Filter only multi-image configs
    availableConfigs.value = (response.data.configs || []).filter((c: any) => {
      return c.capabilities?.multi_image === true
    })
  } catch (error) {
    console.error('[Configs] Failed to load:', error)
  }
}

function selectConfig(configName: string) {
  selectedConfig.value = configName
}

// === GENERATION === //

async function executeGeneration() {
  if (!canGenerate.value) return

  isGenerating.value = true
  generatedImageUrl.value = null

  try {
    const response = await axios.post('/api/schema-pipeline/execute', {
      schema: 'multi_image_transformation',
      input_text: contextPrompt.value,
      input_image1: uploadedImagePath1.value,
      input_image2: uploadedImagePath2.value || null,
      input_image3: uploadedImagePath3.value || null,
      context_prompt: contextPrompt.value,
      output_config: selectedConfig.value,
      user_language: 'de',
      safety_level: 'youth',
      seed: Math.floor(Math.random() * 1000000)
    })

    console.log('[Generation] Response:', response.data)

    if (response.data.success) {
      // Extract generated image URL from response
      const outputs = response.data.outputs || []
      const imageOutput = outputs.find((o: any) => o.type === 'image')
      if (imageOutput?.url) {
        generatedImageUrl.value = imageOutput.url
        executionPhase.value = 'generation_done'
      }
    }
  } catch (error) {
    console.error('[Generation] Failed:', error)
  } finally {
    isGenerating.value = false
  }
}

// === LIFECYCLE === //

onMounted(() => {
  loadCategories()
})
</script>

<style scoped>
.multi-image-transformation-view {
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

.phase-2a {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* Input Images Section */
.input-images-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

/* Context Section */
.context-section {
  width: 100%;
}

/* Category Section */
.category-section {
  width: 100%;
}

.category-bubbles-row {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: center;
}

.category-bubble {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1.5rem;
  border-radius: 1rem;
  background: var(--bubble-color, #e0e0e0);
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 120px;
}

.category-bubble:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.category-bubble.selected {
  outline: 3px solid #007bff;
  outline-offset: 2px;
}

.category-bubble.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.category-icon {
  font-size: 2rem;
}

.category-label {
  font-weight: 600;
  text-align: center;
}

/* Config Section */
.config-section h3 {
  text-align: center;
  margin-bottom: 1rem;
}

.config-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.config-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1.5rem;
  border: 2px solid #ddd;
  border-radius: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.config-card:hover {
  border-color: #007bff;
  transform: translateY(-2px);
}

.config-card.selected {
  border-color: #007bff;
  background: #e7f3ff;
}

.config-icon {
  font-size: 2rem;
}

.config-name {
  font-weight: 600;
  text-align: center;
}

.config-badge {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: #ff6b6b;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 0.5rem;
  font-size: 0.75rem;
  font-weight: bold;
}

/* Generate Section */
.generate-section {
  display: flex;
  justify-content: center;
}

.generate-button {
  padding: 1rem 3rem;
  font-size: 1.25rem;
  font-weight: bold;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 2rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.generate-button:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

.generate-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Output Section */
.output-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.output-section h3 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.generated-image {
  max-width: 100%;
  max-height: 600px;
  border-radius: 1rem;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}
</style>
