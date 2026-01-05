<template>
  <section class="pipeline-section" ref="sectionRef">
    <!-- Output Frame (Always visible) -->
    <div class="output-frame" :class="{ empty: !isExecuting && !outputImage, generating: isExecuting && !outputImage }">
      <!-- Generation Progress Animation -->
      <div v-if="isExecuting && !outputImage" class="generation-animation-container">
        <SpriteProgressAnimation :progress="progress" />
      </div>

      <!-- Empty State with inactive Actions -->
      <div v-else-if="!outputImage" class="empty-with-actions">
        <!-- Action Toolbar (inactive) -->
        <div class="action-toolbar inactive">
          <button class="action-btn" disabled title="Merken (Coming Soon)">
            <span class="action-icon">⭐</span>
          </button>
          <button class="action-btn" disabled title="Drucken">
            <span class="action-icon">🖨️</span>
          </button>
          <button class="action-btn" disabled :title="forwardButtonTitle">
            <span class="action-icon">➡️</span>
          </button>
          <button class="action-btn" disabled title="Herunterladen">
            <span class="action-icon">💾</span>
          </button>
          <button class="action-btn" disabled title="Bildanalyse">
            <span class="action-icon">🔍</span>
          </button>
        </div>
      </div>

      <!-- Final Output -->
      <div v-else-if="outputImage" class="final-output">
        <!-- Image with Actions -->
        <div v-if="mediaType === 'image'" class="image-with-actions">
          <img
            :src="outputImage"
            alt="Generiertes Bild"
            class="output-image"
            @click="$emit('image-click', outputImage)"
          />

          <!-- Action Toolbar (vertical, right side) -->
          <div class="action-toolbar">
            <button class="action-btn" @click="$emit('save')" disabled title="Merken (Coming Soon)">
              <span class="action-icon">⭐</span>
            </button>
            <button class="action-btn" @click="$emit('print')" title="Drucken">
              <span class="action-icon">🖨️</span>
            </button>
            <button class="action-btn" @click="$emit('forward')" :title="forwardButtonTitle">
              <span class="action-icon">➡️</span>
            </button>
            <button class="action-btn" @click="$emit('download')" title="Herunterladen">
              <span class="action-icon">💾</span>
            </button>
            <button class="action-btn" @click="$emit('analyze')" :disabled="isAnalyzing" :title="isAnalyzing ? 'Analysiere...' : 'Bildanalyse'">
              <span class="action-icon">{{ isAnalyzing ? '⏳' : '🔍' }}</span>
            </button>
          </div>
        </div>

        <!-- Video with Actions -->
        <div v-else-if="mediaType === 'video'" class="video-with-actions">
          <video
            :src="outputImage"
            controls
            class="output-video"
          />

          <!-- Action Toolbar -->
          <div class="action-toolbar">
            <button class="action-btn" @click="$emit('save')" disabled title="Merken (Coming Soon)">
              <span class="action-icon">⭐</span>
            </button>
            <button class="action-btn" @click="$emit('download')" title="Herunterladen">
              <span class="action-icon">💾</span>
            </button>
          </div>
        </div>

        <!-- Audio / Music with Actions -->
        <div v-else-if="mediaType === 'audio' || mediaType === 'music'" class="audio-with-actions">
          <audio
            :src="outputImage"
            controls
            class="output-audio"
          />

          <!-- Action Toolbar -->
          <div class="action-toolbar">
            <button class="action-btn" @click="$emit('save')" disabled title="Merken (Coming Soon)">
              <span class="action-icon">⭐</span>
            </button>
            <button class="action-btn" @click="$emit('download')" title="Herunterladen">
              <span class="action-icon">💾</span>
            </button>
          </div>
        </div>

        <!-- 3D Model with Actions -->
        <div v-else-if="mediaType === '3d'" class="model-with-actions">
          <div class="model-container">
            <div class="model-icon">🎨</div>
            <p class="model-hint">3D-Modell erstellt</p>
          </div>

          <!-- Action Toolbar -->
          <div class="action-toolbar">
            <button class="action-btn" @click="$emit('save')" disabled title="Merken (Coming Soon)">
              <span class="action-icon">⭐</span>
            </button>
            <button class="action-btn" @click="$emit('download')" title="Herunterladen">
              <span class="action-icon">💾</span>
            </button>
          </div>
        </div>

        <!-- Fallback for unknown types with Actions -->
        <div v-else class="unknown-media-with-actions">
          <div class="unknown-media">
            <p>Mediendatei erstellt</p>
          </div>

          <!-- Action Toolbar -->
          <div class="action-toolbar">
            <button class="action-btn" @click="$emit('download')" title="Herunterladen">
              <span class="action-icon">💾</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Image Analysis Section -->
      <Transition name="analysis-expand">
        <div v-if="showAnalysis && analysisData" class="image-analysis-section">
          <div class="analysis-header">
            <h3>🔍 Bildanalyse</h3>
            <button class="collapse-btn" @click="$emit('close-analysis')" title="Schließen">×</button>
          </div>

          <div class="analysis-content">
            <!-- Main Analysis Text -->
            <div class="analysis-main">
              <p class="analysis-text">{{ analysisData.analysis }}</p>
            </div>

            <!-- Reflection Prompts -->
            <div v-if="analysisData.reflection_prompts && analysisData.reflection_prompts.length > 0" class="reflection-prompts">
              <h4>💬 Sprich mit Träshi über:</h4>
              <ul>
                <li v-for="(prompt, idx) in analysisData.reflection_prompts" :key="idx">
                  {{ prompt }}
                </li>
              </ul>
            </div>
          </div>
        </div>
      </Transition>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import SpriteProgressAnimation from '@/components/SpriteProgressAnimation.vue'

// Template ref for autoscroll functionality
const sectionRef = ref<HTMLElement | null>(null)

interface AnalysisData {
  analysis: string
  reflection_prompts: string[]
  insights: string[]
  success: boolean
}

interface Props {
  outputImage: string | null
  mediaType: string
  isExecuting: boolean
  progress: number
  isAnalyzing?: boolean
  showAnalysis?: boolean
  analysisData?: AnalysisData | null
  forwardButtonTitle?: string
}

const props = withDefaults(defineProps<Props>(), {
  mediaType: 'image',
  isExecuting: false,
  progress: 0,
  isAnalyzing: false,
  showAnalysis: false,
  analysisData: null,
  forwardButtonTitle: 'Weiterreichen'
})

defineEmits<{
  'save': []
  'print': []
  'forward': []
  'download': []
  'analyze': []
  'image-click': [imageUrl: string]
  'close-analysis': []
}>()

// Expose the section element for autoscroll functionality
defineExpose({
  sectionRef
})
</script>

<style scoped>
/* ============================================================================
   Output Frame (3 States)
   ============================================================================ */

.pipeline-section {
  width: 100%;
  display: flex;
  justify-content: center;
}

.output-frame {
  width: 100%;
  max-width: 1000px;
  margin: clamp(1rem, 3vh, 2rem) auto;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: clamp(1.5rem, 3vh, 2rem);
  background: rgba(30, 30, 30, 0.9);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: clamp(12px, 2vw, 20px);
  transition: all 0.3s ease;
}

.output-frame.empty {
  min-height: clamp(320px, 40vh, 450px);
  border: 2px dashed rgba(255, 255, 255, 0.2);
  background: rgba(20, 20, 20, 0.5);
}

.output-frame.generating {
  min-height: clamp(320px, 40vh, 450px);
  border: 2px solid rgba(76, 175, 80, 0.6);
  background: rgba(30, 30, 30, 0.9);
  box-shadow: 0 0 30px rgba(76, 175, 80, 0.3);
}

/* Generation Animation Container */
.generation-animation-container {
  width: 100%;
  display: flex;
  justify-content: center;
}

/* Final Output */
.final-output {
  width: 100%;
  text-align: center;
}

.output-image {
  max-width: 100%;
  max-height: clamp(300px, 40vh, 500px);
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.5);
  cursor: pointer;
  transition: transform 0.3s ease;
}

.output-image:hover {
  transform: scale(1.02);
}

.output-video {
  width: 100%;
  max-height: 500px;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.5);
}

.output-audio {
  width: 100%;
  max-height: 500px;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.5);
}

/* ============================================================================
   Action Toolbar for Output Media
   ============================================================================ */

/* Empty State with Actions */
.empty-with-actions {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
}

/* Image with Actions Container */
.image-with-actions {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  justify-content: center;
}

/* Universal Media with Actions Containers */
.video-with-actions,
.audio-with-actions,
.model-with-actions,
.unknown-media-with-actions {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  width: 100%;
}

.video-with-actions .output-video,
.audio-with-actions .output-audio {
  flex: 1;
  max-width: 800px;
}

.model-with-actions .model-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

/* Action Toolbar (vertical, right side) */
.action-toolbar {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0.5rem;
  background: rgba(20, 20, 20, 0.9);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.action-toolbar.inactive {
  opacity: 0.3;
  pointer-events: none;
}

/* Action Buttons */
.action-btn {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(30, 30, 30, 0.9);
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  padding: 0;
}

.action-btn:hover:not(:disabled) {
  background: rgba(102, 126, 234, 0.3);
  border-color: rgba(102, 126, 234, 0.8);
  transform: scale(1.05);
}

.action-btn:active:not(:disabled) {
  transform: scale(0.95);
}

.action-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.action-icon {
  font-size: 1.5rem;
  line-height: 1;
}

/* Model/Unknown Media Styling */
.model-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.model-hint {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
}

.unknown-media p {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
}

/* ============================================================================
   Analysis Section
   ============================================================================ */

.image-analysis-section {
  margin-top: 1.5rem;
  padding: 1.5rem;
  background: rgba(30, 30, 30, 0.9);
  border: 2px solid rgba(102, 126, 234, 0.5);
  border-radius: 12px;
  animation: fadeIn 0.3s ease;
}

.analysis-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.analysis-header h3 {
  margin: 0;
  font-size: 1.25rem;
  color: rgba(255, 255, 255, 0.95);
}

.collapse-btn {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  font-size: 2rem;
  cursor: pointer;
  line-height: 1;
  padding: 0;
  transition: color 0.2s;
}

.collapse-btn:hover {
  color: rgba(255, 255, 255, 1);
}

.analysis-text {
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.6;
  white-space: pre-wrap;
}

.reflection-prompts {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
}

.reflection-prompts h4 {
  margin: 0 0 0.5rem 0;
  color: rgba(255, 179, 0, 0.95);
}

.reflection-prompts li {
  color: rgba(255, 255, 255, 0.85);
  line-height: 1.5;
  margin-bottom: 0.5rem;
}

.analysis-expand-enter-active,
.analysis-expand-leave-active {
  transition: all 0.3s ease;
  max-height: 1000px;
  overflow: hidden;
}

.analysis-expand-enter-from,
.analysis-expand-leave-to {
  max-height: 0;
  opacity: 0;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Responsive: Stack toolbar below on mobile */
@media (max-width: 768px) {
  .image-with-actions,
  .video-with-actions,
  .audio-with-actions {
    flex-direction: column;
  }

  .action-toolbar {
    flex-direction: row;
  }

  .action-btn {
    width: 40px;
    height: 40px;
  }

  .action-icon {
    font-size: 1.25rem;
  }
}
</style>
