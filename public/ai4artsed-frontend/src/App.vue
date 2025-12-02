<template>
  <div id="app">
    <!-- Header with Mode Selection -->
    <header class="app-header">
      <div class="header-content">
        <div class="header-left">
          <button
            v-if="showReturnButton"
            class="return-button"
            @click="$router.push('/')"
            title="Zurück zu Phase 1"
          >
            ← Phase 1
          </button>
        </div>

        <div class="header-center">
          <div class="mode-selector">
            <router-link to="/text-transformation" class="mode-button" active-class="active">
              <span class="mode-icon">📝</span>
            </router-link>
            <router-link to="/image-transformation" class="mode-button" active-class="active">
              <span class="mode-icon">🖼️</span>
            </router-link>
          </div>
        </div>

        <div class="header-right">
          <span class="app-title">AI4ARTSED - AI LAB</span>
        </div>
      </div>
    </header>

    <div class="app-content">
      <router-view />
    </div>

    <ChatOverlay />
  </div>
</template>

<script setup lang="ts">
/**
 * App.vue - Main application component
 *
 * Uses Vue Router to render different views:
 * - / (home): Legacy execution interface
 * - /select: Phase 1 Property Quadrants selection interface
 * - /about: About page
 *
 * Session 82: Added ChatOverlay global component for interactive LLM help
 * Session 86: Integrated return button into global header
 */
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import ChatOverlay from './components/ChatOverlay.vue'

const route = useRoute()
const showReturnButton = computed(() => {
  return route.path === '/text-transformation' || route.path === '/image-transformation'
})
</script>

<style>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html, body {
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
  overflow: auto;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: #0a0a0a;
}

#app {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* Header */
.app-header {
  background: rgba(10, 10, 10, 0.95);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 0.5rem 1.5rem;
  z-index: 1000;
  flex-shrink: 0;
}

.header-content {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  max-width: 1400px;
  margin: 0 auto;
}

.header-left {
  display: flex;
  justify-content: flex-start;
}

.return-button {
  padding: 0.4rem 1rem;
  background: rgba(30, 30, 30, 0.9);
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  color: #ffffff;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.return-button:hover {
  border-color: rgba(102, 126, 234, 0.8);
  background: rgba(102, 126, 234, 0.2);
  transform: translateX(-4px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.return-button:active {
  transform: translateX(-2px) scale(0.98);
}

.header-center {
  display: flex;
  justify-content: center;
}

.mode-selector {
  display: flex;
  gap: 0.25rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 0.25rem;
}

.mode-button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1rem;
  background: transparent;
  border: 2px solid transparent;
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.6);
  text-decoration: none;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 60px;
}

.mode-button:hover {
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.9);
}

.mode-button.active {
  background: rgba(76, 175, 80, 0.15);
  border-color: rgba(76, 175, 80, 0.5);
  color: #4CAF50;
}

.mode-icon {
  font-size: 1.5rem;
}

.header-right {
  display: flex;
  justify-content: flex-end;
}

.app-title {
  font-size: 1rem;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.9);
  text-transform: uppercase;
  letter-spacing: 1px;
}

/* Content Area */
.app-content {
  flex: 1;
  overflow: auto;
}

/* Responsive */
@media (max-width: 768px) {
  .app-header {
    padding: 0.5rem 1rem;
  }

  .header-content {
    grid-template-columns: auto 1fr auto;
    gap: 0.5rem;
  }

  .header-left,
  .header-center,
  .header-right {
    justify-content: center;
  }

  .return-button {
    font-size: 0.8rem;
    padding: 0.3rem 0.8rem;
  }

  .app-title {
    font-size: 0.8rem;
  }

  .mode-button {
    padding: 0.4rem 0.8rem;
    min-width: 50px;
  }

  .mode-icon {
    font-size: 1.25rem;
  }
}
</style>
