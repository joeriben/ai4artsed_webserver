<template>
  <div id="app">
    <!-- Header with Mode Selection -->
    <header class="app-header">
      <div class="header-content">
        <div class="header-left">
          <a href="https://www.ucdcae.fau.de/" target="_blank" rel="noopener noreferrer" class="header-logo-link">
            <img src="/logos/unesco_chair.png" alt="UNESCO Chair" class="header-logo" />
          </a>
          <span class="app-title-wrapper">
            <span class="app-title">UCDCAE AI LAB</span>
            <span class="app-title-tooltip"><span class="tooltip-highlight">UNESCO Chair in Digital Culture and Arts in Education</span> AI Lab</span>
          </span>
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
            <router-link to="/music-generation" class="mode-button" active-class="active" title="Music Generation">
              <span class="mode-icon">
                <svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 -960 960 960" width="24" fill="currentColor">
                  <path d="M400-120q-66 0-113-47t-47-113q0-66 47-113t113-47q23 0 42.5 5.5T480-418v-422h240v160H560v400q0 66-47 113t-113 47Z"/>
                </svg>
              </span>
            </router-link>
            <router-link to="/canvas" class="mode-button" active-class="active" title="Canvas Workflow">
              <span class="mode-icon">
                <svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 0 24 24" width="24" fill="currentColor">
                  <path d="M22 11V3h-7v3H9V3H2v8h7V8h2v10h4v3h7v-8h-7v3h-2V8h2v3z"/>
                </svg>
              </span>
            </router-link>
            <router-link to="/latent-lab" class="mode-button" active-class="active" title="Latent Lab">
              <span class="mode-icon">
                <svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 -960 960 960" width="24" fill="currentColor">
                  <path d="M200-120v-80h200v-80q-83 0-141.5-58.5T200-480q0-61 33.5-111t90.5-73q8-34 35.5-55t62.5-21l-22-62 38-14-14-36 76-28 12 38 38-14 110 300-38 14 14 38-76 28-12-38-38 14-24-66q-15 14-34.5 21t-39.5 5q-22-2-41-13.5T338-582q-27 16-42.5 43T280-480q0 50 35 85t85 35h320v80H520v80h240v80H200Zm346-458 36-14-68-188-38 14 70 188Zm-126-22q17 0 28.5-11.5T460-640q0-17-11.5-28.5T420-680q-17 0-28.5 11.5T380-640q0 17 11.5 28.5T420-600Zm126 22Zm-126-62Zm0 0Z"/>
                </svg>
              </span>
            </router-link>
          </div>
        </div>

        <div class="header-right">
          <nav class="header-nav-links">
            <button @click="openAbout" class="nav-link" :title="$t('nav.about')">
              <svg xmlns="http://www.w3.org/2000/svg" height="20" viewBox="0 -960 960 960" width="20" fill="currentColor">
                <path d="M440-280h80v-240h-80v240Zm40-320q17 0 28.5-11.5T520-640q0-17-11.5-28.5T480-680q-17 0-28.5 11.5T440-640q0 17 11.5 28.5T480-600Zm0 520q-83 0-156-31.5T197-197q-54-54-85.5-127T80-480q0-83 31.5-156T197-763q54-54 127-85.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 83-31.5 156T763-197q-54 54-127 85.5T480-80Zm0-80q134 0 227-93t93-227q0-134-93-227t-227-93q-134 0-227 93t-93 227q0 134 93 227t227 93Zm0-320Z"/>
              </svg>
            </button>
            <button @click="openDokumentation" class="nav-link" :title="$t('nav.docs')">
              <svg xmlns="http://www.w3.org/2000/svg" height="20" viewBox="0 -960 960 960" width="20" fill="currentColor">
                <path d="M478-240q21 0 35.5-14.5T528-290q0-21-14.5-35.5T478-340q-21 0-35.5 14.5T428-290q0 21 14.5 35.5T478-240Zm-36-154h74q0-33 7.5-52t42.5-52q26-26 41-49.5t15-56.5q0-56-41-86t-97-30q-57 0-92.5 30T342-618l66 26q5-18 22.5-39t53.5-21q32 0 48 17.5t16 38.5q0 20-12 37.5T506-526q-44 39-54 59t-10 73Zm38 314q-83 0-156-31.5T197-197q-54-54-85.5-127T80-480q0-83 31.5-156T197-763q54-54 127-85.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 83-31.5 156T763-197q-54 54-127 85.5T480-80Zm0-80q134 0 227-93t93-227q0-134-93-227t-227-93q-134 0-227 93t-93 227q0 134 93 227t227 93Zm0-320Z"/>
              </svg>
            </button>
            <router-link to="/training" class="nav-link" title="LoRA Training">
              <svg xmlns="http://www.w3.org/2000/svg" height="20" width="20" viewBox="0 0 87.5 121.26" fill="currentColor">
                <g transform="translate(-53.85 -72.62)"><path d="M140.15 80.88c-3.78-9.98-29.01-15.44-38.8 10.78 30.9-4-14.24 39.34-21.73 64.88 1.22 10.36 1.58 21.85 4.87 29.55l1.87-3.05c.64 4.43 1.64 8.32 3.55 10.84l4.67-37.91c13.54-8.2 30.28-22.21 27.5-39.81 2.84-5.28 6.52-9.45 5.7-19.45-.23-2.42 2.14-6.09 3.57-9.3 0 0-2.76-5.06 8.8-6.53"/><path d="M139.97 82.26c2.6 4.36 1.94 12.14-5.57 14.72 2.21-6.04-.12-6.46-2.28-11.07 2.05-3.12 4.86-3.7 7.85-3.65"/><path d="M131.98 87.82c1.4 1.68 2.5 3.53 2.78 5.84a8.7 8.7 0 0 1-6.1 1.35 23 23 0 0 0 3.32-7.19"/><circle cx="127.69" cy="79.08" r="3.23" fill="white"/><path d="M99.38 93.15C84.64 95.65 76.6 134 75.55 150.62c-1.58 7.6-5.04 16.22-4.07 22.4 2.44.64 4.58-.86 6.7-2.4l-1.07-15.45c8.98-21.52 49.21-67.3 22.27-62.02"/><ellipse cx="112.66" cy="142.52" rx="3.11" ry="3.95"/><ellipse cx="106.91" cy="145.99" rx="3.11" ry="3.95"/><path d="M134.6 129.63c-5.54 2.46-12.32 6.24-17.82 8.78 1.17.95 1 2.3.6 3.88 6.04-2.62 12.77-6.65 18.9-9.19zm-64.53 33.76c-4.21 2.56-12.1 12.58-16.22 15.34l2.4.86c5.08-3.74 7.44-7.8 12.76-10.03z"/></g>
              </svg>
            </router-link>
            <router-link to="/settings" class="nav-link" :title="$t('nav.settings')">
              <svg xmlns="http://www.w3.org/2000/svg" height="20" viewBox="0 -960 960 960" width="20" fill="currentColor">
                <path d="m370-80-16-128q-13-5-24.5-12T307-235l-119 50L78-375l103-78q-1-7-1-13.5v-27q0-6.5 1-13.5L78-585l110-190 119 50q11-8 23-15t24-12l16-128h220l16 128q13 5 24.5 12t22.5 15l119-50 110 190-103 78q1 7 1 13.5v27q0 6.5-2 13.5l103 78-110 190-118-50q-11 8-23 15t-24 12L590-80H370Zm70-80h79l14-106q31-8 57.5-23.5T639-327l99 41 39-68-86-65q5-14 7-29.5t2-31.5q0-16-2-31.5t-7-29.5l86-65-39-68-99 42q-22-23-48.5-38.5T533-694l-13-106h-79l-14 106q-31 8-57.5 23.5T321-633l-99-41-39 68 86 64q-5 15-7 30t-2 32q0 16 2 31t7 30l-86 65 39 68 99-42q22 23 48.5 38.5T427-266l13 106Zm42-180q58 0 99-41t41-99q0-58-41-99t-99-41q-59 0-99.5 41T342-480q0 58 40.5 99t99.5 41Zm-2-140Z"/>
              </svg>
            </router-link>
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
    <FooterGallery />

    <!-- Modals -->
    <AboutModal v-model="showAbout" />
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
import FooterGallery from './components/FooterGallery.vue'
import AboutModal from './components/AboutModal.vue'
import DokumentationModal from './components/DokumentationModal.vue'
import ImpressumModal from './components/ImpressumModal.vue'
import SettingsAuthModal from './components/SettingsAuthModal.vue'

const { locale, t } = useI18n()
const route = useRoute()
const router = useRouter()
const currentLanguage = computed(() => locale.value)
const showAbout = ref(false)
const showDokumentation = ref(false)
const showImpressum = ref(false)
const showSettingsAuth = ref(false)

function toggleLanguage() {
  locale.value = locale.value === 'de' ? 'en' : 'de'
}

function openAbout() {
  showAbout.value = true
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
  align-items: center;
  gap: 0.5rem;
  justify-content: flex-start;
}

.header-logo-link {
  display: flex;
  align-items: center;
  opacity: 0.85;
  transition: opacity 0.2s;
}

.header-logo-link:hover {
  opacity: 1;
}

.header-logo {
  height: 28px;
  width: auto;
  border-radius: 3px;
}

.header-logo-round {
  border-radius: 50%;
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

.app-title-wrapper {
  position: relative;
  cursor: default;
}

.app-title {
  font-size: 1rem;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.9);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.app-title-tooltip {
  display: none;
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  margin-top: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: rgba(30, 30, 30, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 400;
  letter-spacing: 0;
  text-transform: none;
  white-space: nowrap;
  color: rgba(255, 255, 255, 0.8);
  z-index: 1001;
}

.app-title-wrapper:hover .app-title-tooltip {
  display: block;
}

.tooltip-highlight {
  color: #FF6F00;
  font-weight: 600;
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

.nav-link svg {
  width: 20px;
  height: 20px;
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
  min-width: 90px;
  padding: 0.4rem 0.8rem;
  font-size: 0.85rem;
  text-align: center;
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

}
</style>
