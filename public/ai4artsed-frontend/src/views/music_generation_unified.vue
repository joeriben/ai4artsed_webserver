<template>
  <div class="music-unified-page" :class="{ 'mode-advanced': mode === 'advanced' }">
    <!-- Mode Toggle (floating at top) -->
    <div class="mode-toggle-container">
      <div class="mode-toggle">
        <button
          class="mode-btn"
          :class="{ active: mode === 'simple' }"
          @click="setMode('simple')"
        >
          {{ $t('musicGen.simpleMode') }}
        </button>
        <button
          class="mode-btn"
          :class="{ active: mode === 'advanced' }"
          @click="setMode('advanced')"
        >
          {{ $t('musicGen.advancedMode') }}
        </button>
      </div>
    </div>

    <!-- Conditional rendering of V1 (Simple) or V2 (Advanced) -->
    <MusicGenerationSimple v-if="mode === 'simple'" />
    <MusicGenerationAdvanced v-else />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import MusicGenerationSimple from './music_generation.vue'
import MusicGenerationAdvanced from './music_generation_v2.vue'

const STORAGE_KEY = 'music_generation_mode'

const mode = ref<'simple' | 'advanced'>('simple')

function setMode(newMode: 'simple' | 'advanced') {
  mode.value = newMode
  localStorage.setItem(STORAGE_KEY, newMode)
}

onMounted(() => {
  const saved = localStorage.getItem(STORAGE_KEY)
  if (saved === 'simple' || saved === 'advanced') {
    mode.value = saved
  }
})
</script>

<style scoped>
.music-unified-page {
  min-height: 100vh;
  position: relative;
  background: #0a0a0a;
}

.music-unified-page.mode-advanced {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
}

.mode-toggle-container {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  justify-content: center;
  padding: 1rem 1rem 0.5rem;
  background: inherit;
}

.mode-toggle {
  display: inline-flex;
  gap: 0.25rem;
  padding: 0.25rem;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(8px);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.mode-btn {
  padding: 0.5rem 1.25rem;
  font-size: 0.85rem;
  font-weight: 600;
  border: none;
  border-radius: 10px;
  background: transparent;
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: inherit;
}

.mode-btn:hover:not(.active) {
  color: rgba(255, 255, 255, 0.8);
  background: rgba(255, 255, 255, 0.05);
}

.mode-btn.active {
  background: rgba(156, 39, 176, 0.4);
  color: white;
  box-shadow: 0 2px 8px rgba(156, 39, 176, 0.3);
}
</style>

<style>
/* Override child component backgrounds since unified page handles it */
.music-unified-page .music-generation-view {
  background: transparent !important;
}
</style>
