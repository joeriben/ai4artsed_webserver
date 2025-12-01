<template>
  <div id="app">
    <!-- Header with Mode Selection -->
    <header class="app-header">
      <div class="header-content">
        <div class="header-left"></div>

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
 */
import ChatOverlay from './components/ChatOverlay.vue'
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
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 1rem 2rem;
  z-index: 50;
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
  /* Reserved for future use */
}

.header-center {
  display: flex;
  justify-content: center;
}

.mode-selector {
  display: flex;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 0.5rem;
}

.mode-button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem 1.5rem;
  background: transparent;
  border: 2px solid transparent;
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.6);
  text-decoration: none;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 80px;
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
  font-size: 2.5rem;
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
    padding: 0.75rem 1rem;
  }

  .header-content {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }

  .header-right {
    justify-content: center;
  }

  .app-title {
    font-size: 0.9rem;
  }

  .mode-button {
    padding: 0.75rem 1.25rem;
    min-width: 70px;
  }

  .mode-icon {
    font-size: 2rem;
  }
}
</style>
