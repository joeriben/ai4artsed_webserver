<template>
  <div id="app">
    <router-view />
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
 */
</script>

<style>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html, body {
  width: 100%;
  height: auto;
  margin: 0;
  padding: 0;
  overflow: auto;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: #0a0a0a;
}

/* Smooth scrolling for all scroll actions */
@media (prefers-reduced-motion: no-preference) {
  html {
    scroll-behavior: smooth;
  }
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
</style>
