<template>
  <div id="app">
    <router-view />
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
  overflow: auto;
}
</style>
