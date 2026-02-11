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
    <AttentionCartography v-if="activeTab === 'attention'" />
    <FeatureProbing v-else-if="activeTab === 'probing'" />
    <ConceptAlgebra v-else-if="activeTab === 'algebra'" />
    <Surrealizer v-else-if="activeTab === 'fusion'" />
    <DenoisingArchaeology v-else-if="activeTab === 'archaeology'" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import AttentionCartography from './latent_lab/attention_cartography.vue'
import FeatureProbing from './latent_lab/feature_probing.vue'
import ConceptAlgebra from './latent_lab/concept_algebra.vue'
import DenoisingArchaeology from './latent_lab/denoising_archaeology.vue'
import Surrealizer from './surrealizer.vue'

const { t } = useI18n()

type TabId = 'attention' | 'probing' | 'algebra' | 'fusion' | 'archaeology'

const STORAGE_KEY = 'latent_lab_tab'

const tabs: { id: TabId }[] = [
  { id: 'attention' },
  { id: 'probing' },
  { id: 'algebra' },
  { id: 'fusion' },
  { id: 'archaeology' },
]

const activeTab = ref<TabId>('attention')

function setTab(tabId: TabId) {
  activeTab.value = tabId
  localStorage.setItem(STORAGE_KEY, tabId)
}

onMounted(() => {
  const saved = localStorage.getItem(STORAGE_KEY)
  if (saved && tabs.some(t => t.id === saved)) {
    activeTab.value = saved as TabId
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

.placeholder-tab {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
}

.placeholder-content {
  text-align: center;
  color: rgba(255, 255, 255, 0.4);
}

.placeholder-content h2 {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
  color: rgba(255, 255, 255, 0.5);
}

.placeholder-content p {
  font-size: 1rem;
  font-style: italic;
}
</style>
