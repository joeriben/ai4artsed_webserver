<template>
  <div class="latent-lab-page" :class="{ [`mode-${activeTab}`]: true }">
    <!-- Tab Toggle (floating at top) -->
    <div class="tab-toggle-container">
      <div class="tab-toggle">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          class="tab-btn"
          :class="{ active: activeTab === tab.id }"
          @click="setTab(tab.id)"
        >
          {{ t(`latentLab.tabs.${tab.id}`) }}
        </button>
      </div>
    </div>

    <!-- Conditional rendering of tab components -->
    <ImageLab v-if="activeTab === 'image'" />
    <LatentTextLab v-else-if="activeTab === 'textlab'" />
    <CrossmodalLab v-else-if="activeTab === 'crossmodal'" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import ImageLab from './latent_lab/image_lab.vue'
import LatentTextLab from './latent_lab/latent_text_lab.vue'
import CrossmodalLab from './latent_lab/crossmodal_lab.vue'

const { t } = useI18n()

type TabId = 'image' | 'textlab' | 'crossmodal'

const STORAGE_KEY = 'latent_lab_tab'

// Old tab IDs that should migrate to 'image'
const IMAGE_TAB_IDS = ['attention', 'probing', 'algebra', 'fusion', 'archaeology']

const tabs: { id: TabId }[] = [
  { id: 'image' },
  { id: 'textlab' },
  { id: 'crossmodal' },
]

const activeTab = ref<TabId>('image')

function setTab(tabId: TabId) {
  activeTab.value = tabId
  localStorage.setItem(STORAGE_KEY, tabId)
}

onMounted(() => {
  const saved = localStorage.getItem(STORAGE_KEY)
  if (saved) {
    // Backward-compatible migration: old image-related tab IDs → 'image'
    if (IMAGE_TAB_IDS.includes(saved)) {
      activeTab.value = 'image'
      localStorage.setItem(STORAGE_KEY, 'image')
    } else if (tabs.some(t => t.id === saved)) {
      activeTab.value = saved as TabId
    }
  }
})
</script>

<style scoped>
.latent-lab-page {
  min-height: 100vh;
  position: relative;
  background: transparent;
}

.tab-toggle-container {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  justify-content: center;
  padding: 1rem 1rem 0.5rem;
  background: inherit;
}

.tab-toggle {
  display: inline-flex;
  gap: 0.2rem;
  padding: 0.25rem;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(8px);
  border-radius: 12px;
  border: 1px solid rgba(102, 126, 234, 0.15);
}

.tab-btn {
  padding: 0.5rem 1rem;
  font-size: 0.8rem;
  font-weight: 600;
  border: none;
  border-radius: 10px;
  background: transparent;
  color: rgba(255, 255, 255, 0.4);
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: inherit;
  white-space: nowrap;
}

.tab-btn:hover:not(.active) {
  color: rgba(255, 255, 255, 0.7);
  background: rgba(255, 255, 255, 0.05);
}

.tab-btn.active {
  background: rgba(102, 126, 234, 0.25);
  color: #667eea;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
}
</style>
