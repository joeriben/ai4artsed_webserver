<template>
  <div id="app">
    <!-- Header with Mode Selection -->
    <header class="app-header">
      <div class="header-content">
        <div class="header-left">
          <span class="app-title">AI4ARTSED - AI LAB</span>
        </div>

        <div class="header-center">
          <div class="mode-selector">
            <router-link to="/" class="mode-button" active-class="active">
              <span class="mode-icon">
                <svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 -960 960 960" width="24" fill="currentColor">
                  <path d="M480-60q-50 0-85-35t-35-85q0-50 35-85t85-35q50 0 85 35t35 85q0 50-35 85t-85 35Zm0-80q17 0 28.5-11.5T520-180q0-17-11.5-28.5T480-220q-17 0-28.5 11.5T440-180q0 17 11.5 28.5T480-140Zm-260-70q-50 0-85-35t-35-85q0-50 35-85t85-35q50 0 85 35t35 85q0 50-35 85t-85 35Zm520 0q-50 0-85-35t-35-85q0-50 35-85t85-35q50 0 85 35t35 85q0 50-35 85t-85 35Zm-520-80q17 0 28.5-11.5T260-330q0-17-11.5-28.5T220-370q-17 0-28.5 11.5T180-330q0 17 11.5 28.5T220-290Zm520 0q17 0 28.5-11.5T780-330q0-17-11.5-28.5T740-370q-17 0-28.5 11.5T700-330q0 17 11.5 28.5T740-290ZM220-510q-50 0-85-35t-35-85q0-50 35-85t85-35q50 0 85 35t35 85q0 50-35 85t-85 35Zm520 0q-50 0-85-35t-35-85q0-50 35-85t85-35q50 0 85 35t35 85q0 50-35 85t-85 35Zm-520-80q17 0 28.5-11.5T260-630q0-17-11.5-28.5T220-670q-17 0-28.5 11.5T180-630q0 17 11.5 28.5T220-590Zm520 0q17 0 28.5-11.5T780-630q0-17-11.5-28.5T740-670q-17 0-28.5 11.5T700-630q0 17 11.5 28.5T740-590Zm-260-70q-50 0-85-35t-35-85q0-50 35-85t85-35q50 0 85 35t35 85q0 50-35 85t-85 35Zm0-80q17 0 28.5-11.5T520-780q0-17-11.5-28.5T480-820q-17 0-28.5 11.5T440-780q0 17 11.5 28.5T480-740Z"/>
                </svg>
              </span>
            </router-link>
            <router-link to="/text-transformation" class="mode-button" active-class="active">
              <span class="mode-icon">
                <svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 -960 960 960" width="24" fill="currentColor">
                  <path d="M160-200v-80h528l-42-42 56-56 138 138-138 138-56-56 42-42H160Zm116-200 164-440h80l164 440h-76l-38-112H392l-40 112h-76Zm138-176h132l-64-182h-4l-64 182Z"/>
                </svg>
              </span>
            </router-link>
            <router-link to="/image-transformation" class="mode-button" active-class="active">
              <span class="mode-icon">
                <svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 -960 960 960" width="24" fill="currentColor">
                  <path d="M200-120q-33 0-56.5-23.5T120-200v-560q0-33 23.5-56.5T200-840h560q33 0 56.5 23.5T840-760v560q0 33-23.5 56.5T760-120H200Zm0-80h560v-560H200v560Zm40-80h480L570-480 450-320l-90-120-120 160Zm-40 80v-560 560Z"/>
                </svg>
              </span>
            </router-link>
            <router-link to="/multi-image-transformation" class="mode-button" active-class="active">
              <span class="mode-icon">
                <svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 -960 960 960" width="24" fill="currentColor">
                  <path d="M120-840h320v320H120v-320Zm80 80v160-160Zm320-80h320v320H520v-320Zm80 80v160-160ZM120-440h320v320H120v-320Zm80 80v160-160Zm440-80h80v120h120v80H720v120h-80v-120H520v-80h120v-120Zm-40-320v160h160v-160H600Zm-400 0v160h160v-160H200Zm0 400v160h160v-160H200Z"/>
                </svg>
              </span>
            </router-link>
          </div>
        </div>

        <div class="header-right">
          <nav class="header-nav-links">
            <button @click="openAbout" class="nav-link" :title="$t('nav.about')">ⓘ</button>
            <button @click="openDatenschutz" class="nav-link" :title="$t('nav.privacy')">🔒</button>
            <button @click="openDokumentation" class="nav-link" :title="$t('nav.docs')">📖</button>
            <router-link to="/settings" class="nav-link" :title="$t('nav.settings')">⚙️</router-link>
            <button @click="toggleLanguage" class="nav-link lang-toggle" :title="$t('nav.language')">
              {{ currentLanguage === 'de' ? 'EN' : 'DE' }}
            </button>
            <button @click="openImpressum" class="nav-link nav-link-text">{{ $t('nav.impressum') }}</button>
          </nav>
        </div>
      </div>
    </header>

    <div class="app-content">
      <router-view />
    </div>

    <ChatOverlay />

    <!-- Permanent BMBFSFJ Funding Logo -->
    <div class="funding-logo-fixed">
      <a href="https://www.bmfsfj.de/" target="_blank" rel="noopener noreferrer">
        <img src="/logos/BMBFSFJ_logo.png" alt="Gefördert vom BMFSFJ" />
      </a>
    </div>

    <!-- Modals -->
    <AboutModal v-model="showAbout" />
    <DatenschutzModal v-model="showDatenschutz" />
    <DokumentationModal v-model="showDokumentation" />
    <ImpressumModal v-model="showImpressum" />
    <SettingsAuthModal v-model="showSettingsAuth" @authenticated="onSettingsAuthenticated" />
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
 * Session 86: Integrated return button into global header (always visible)
 */
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import ChatOverlay from './components/ChatOverlay.vue'
import AboutModal from './components/AboutModal.vue'
import DatenschutzModal from './components/DatenschutzModal.vue'
import DokumentationModal from './components/DokumentationModal.vue'
import ImpressumModal from './components/ImpressumModal.vue'
import SettingsAuthModal from './components/SettingsAuthModal.vue'

const { locale, t } = useI18n()
const route = useRoute()
const router = useRouter()
const currentLanguage = computed(() => locale.value)
const showAbout = ref(false)
const showDatenschutz = ref(false)
const showDokumentation = ref(false)
const showImpressum = ref(false)
const showSettingsAuth = ref(false)

function toggleLanguage() {
  locale.value = locale.value === 'de' ? 'en' : 'de'
}

function openAbout() {
  showAbout.value = true
}

function openDatenschutz() {
  showDatenschutz.value = true
}

function openDokumentation() {
  showDokumentation.value = true
}

function openImpressum() {
  showImpressum.value = true
}

// Watch for auth requirement from router guard
watch(() => route.query.authRequired, (authRequired) => {
  if (authRequired === 'settings') {
    showSettingsAuth.value = true
  }
})

// Handle successful authentication
function onSettingsAuthenticated() {
  router.push('/settings')
}
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
  padding: 0.5rem 0;
  z-index: 1000;
  flex-shrink: 0;
}

.header-content {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 1rem;
}

.header-left {
  display: flex;
  justify-content: flex-start;
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
  display: flex;
  align-items: center;
  justify-content: center;
}

.mode-icon svg {
  width: 24px;
  height: 24px;
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

/* Header Right Reorganization */
.header-right {
  display: flex;
  align-items: center;
}

/* Navigation Links */
.header-nav-links {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.nav-link {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.4rem 0.6rem;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 4px;
  color: rgba(255, 255, 255, 0.6);
  text-decoration: none;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 32px;
  height: 32px;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.9);
}

.nav-link.router-link-active {
  color: #4CAF50;
  border-color: rgba(76, 175, 80, 0.3);
}

.lang-toggle {
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.nav-link-text {
  min-width: auto;
  padding: 0.4rem 0.8rem;
  font-size: 0.85rem;
}

/* Content Area */
.app-content {
  flex: 1;
  overflow: auto;
}

/* Permanent Funding Logo - Fixed Bottom Right */
.funding-logo-fixed {
  position: fixed;
  bottom: 1.5rem;
  right: 1.5rem;
  z-index: 900;
  background: white;
  padding: 0.75rem;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.funding-logo-fixed:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.4);
}

.funding-logo-fixed a {
  display: block;
  line-height: 0;
}

.funding-logo-fixed img {
  width: 180px;
  height: auto;
  display: block;
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

  .header-nav-links {
    gap: 0.25rem;
    padding-left: 0.5rem;
  }

  .nav-link {
    padding: 0.3rem 0.5rem;
    font-size: 0.8rem;
    min-width: 28px;
    height: 28px;
  }

  .funding-logo-fixed {
    bottom: 1rem;
    right: 1rem;
    padding: 0.5rem;
  }

  .funding-logo-fixed img {
    width: 140px;
  }
}
</style>
