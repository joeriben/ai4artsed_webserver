<template>
  <div class="landing-view">

    <!-- Hero Section -->
    <section class="hero">
      <h1 class="hero-title">AI4ArtsEd</h1>
      <p class="hero-subtitle">{{ $t('landing.subtitle') }}</p>
      <p class="hero-research">{{ $t('landing.research') }}</p>
    </section>

    <!-- Feature Cards Grid -->
    <section class="features">
      <div class="feature-grid">
        <div
          v-for="feature in features"
          :key="feature.id"
          class="feature-card"
          :style="{ '--feature-color': feature.color }"
          @click="$router.push(feature.route)"
        >
          <!-- Preview images (staggered rotation per card) -->
          <div class="card-preview">
            <div
              class="preview-bg"
              :style="{ backgroundImage: feature.previewImages.length ? `url(${feature.previewImages[(previewIndices[feature.id] ?? 0) % feature.previewImages.length]})` : 'none' }"
            ></div>
            <div class="preview-overlay"></div>
          </div>

          <!-- Card content -->
          <div class="card-body">
            <div class="card-icon" v-html="feature.iconSvg"></div>
            <h3 class="card-title">{{ $t(feature.titleKey) }}</h3>
            <p class="card-description">{{ $t(feature.descriptionKey) }}</p>
          </div>

          <!-- Color accent bar -->
          <div class="card-accent"></div>
        </div>
      </div>
    </section>

    <!-- Funding -->
    <section class="funding">
      <a href="https://www.bmfsfj.de/" target="_blank" rel="noopener noreferrer">
        <img src="/logos/BMBFSFJ_logo.png" :alt="$t('about.funding.title')" class="funding-logo" />
      </a>
      <a href="https://kubi-meta.de/ai4artsed" target="_blank" rel="noopener noreferrer" class="project-link">
        kubi-meta.de/ai4artsed
      </a>
    </section>

  </div>
</template>

<script setup lang="ts">
import { reactive, onMounted, onUnmounted } from 'vue'

// Per-card preview index with staggered timing (±800ms random offset)
const previewIndices = reactive<Record<string, number>>({})
const timers: number[] = []

onMounted(() => {
  features.forEach((feature) => {
    previewIndices[feature.id] = 0
    const jitter = Math.random() * 1600 - 800 // -800ms to +800ms
    const interval = window.setInterval(() => {
      previewIndices[feature.id] = (previewIndices[feature.id] ?? 0) + 1
    }, 4000 + jitter)
    timers.push(interval)
  })
})

onUnmounted(() => {
  timers.forEach(t => clearInterval(t))
})

// Feature definitions with SVG icons from the header mode-selector
const features = [
  {
    id: 'text-transformation',
    route: '/text-transformation',
    color: '#667eea',
    titleKey: 'landing.features.textTransformation.title',
    descriptionKey: 'landing.features.textTransformation.description',
    iconSvg: '<svg xmlns="http://www.w3.org/2000/svg" height="32" viewBox="0 -960 960 960" width="32" fill="currentColor"><path d="M160-200v-80h528l-42-42 56-56 138 138-138 138-56-56 42-42H160Zm116-200 164-440h80l164 440h-76l-38-112H392l-40 112h-76Zm138-176h132l-64-182h-4l-64 182Z"/></svg>',
    previewImages: [
      '/config-previews/bauhaus.png',
      '/config-previews/dada.png',
      '/config-previews/de-biaser.png',
      '/config-previews/displaced_world.png',
      '/config-previews/hunkydoryharmonizer.png',
      '/config-previews/jugendsprache.png',
      '/config-previews/overdrive.png',
      '/config-previews/p5js_simplifier.png',
    ],
  },
  {
    id: 'image-transformation',
    route: '/image-transformation',
    color: '#e91e63',
    titleKey: 'landing.features.imageTransformation.title',
    descriptionKey: 'landing.features.imageTransformation.description',
    iconSvg: '<svg xmlns="http://www.w3.org/2000/svg" height="32" viewBox="0 -960 960 960" width="32" fill="currentColor"><path d="M200-120q-33 0-56.5-23.5T120-200v-560q0-33 23.5-56.5T200-840h560q33 0 56.5 23.5T840-760v560q0 33-23.5 56.5T760-120H200Zm0-80h560v-560H200v560Zm40-80h480L570-480 450-320l-90-120-120 160Zm-40 80v-560 560Z"/></svg>',
    previewImages: [
      '/config-previews/analog_photography_1870s.jpg',
      '/config-previews/analogue_copy.png',
      '/config-previews/cooked_negatives.png',
      '/config-previews/digital_photography.png',
    ],
  },
  {
    id: 'multi-image',
    route: '/multi-image-transformation',
    color: '#7C4DFF',
    titleKey: 'landing.features.multiImage.title',
    descriptionKey: 'landing.features.multiImage.description',
    iconSvg: '<svg xmlns="http://www.w3.org/2000/svg" height="32" viewBox="0 -960 960 960" width="32" fill="currentColor"><path d="M120-840h320v320H120v-320Zm80 80v160-160Zm320-80h320v320H520v-320Zm80 80v160-160ZM120-440h320v320H120v-320Zm80 80v160-160Zm440-80h80v120h120v80H720v120h-80v-120H520v-80h120v-120Zm-40-320v160h160v-160H600Zm-400 0v160h160v-160H200Zm0 400v160h160v-160H200Z"/></svg>',
    previewImages: [
      '/config-previews/multi_image_1.jpg',
      '/config-previews/multi_image_2.jpg',
      '/config-previews/multi_image_3.jpg',
    ],
  },
  {
    id: 'music',
    route: '/music-generation',
    color: '#FF6F00',
    titleKey: 'landing.features.music.title',
    descriptionKey: 'landing.features.music.description',
    iconSvg: '<svg xmlns="http://www.w3.org/2000/svg" height="32" viewBox="0 -960 960 960" width="32" fill="currentColor"><path d="M400-120q-66 0-113-47t-47-113q0-66 47-113t113-47q23 0 42.5 5.5T480-418v-422h240v160H560v400q0 66-47 113t-113 47Z"/></svg>',
    previewImages: [
      '/config-previews/music_gen_1.jpg',
      '/config-previews/music_gen_2.jpg',
    ],
  },
  {
    id: 'canvas',
    route: '/canvas',
    color: '#4CAF50',
    titleKey: 'landing.features.canvas.title',
    descriptionKey: 'landing.features.canvas.description',
    iconSvg: '<svg xmlns="http://www.w3.org/2000/svg" height="32" viewBox="0 0 24 24" width="32" fill="currentColor"><path d="M22 11V3h-7v3H9V3H2v8h7V8h2v10h4v3h7v-8h-7v3h-2V8h2v3z"/></svg>',
    previewImages: [
      '/config-previews/canvas_workflow_1.png',
      '/config-previews/canvas_workflow_2.png',
      '/config-previews/canvas_workflow_3.png',
    ],
  },
  {
    id: 'latent-lab',
    route: '/latent-lab',
    color: '#00BCD4',
    titleKey: 'landing.features.latentLab.title',
    descriptionKey: 'landing.features.latentLab.description',
    iconSvg: '<svg xmlns="http://www.w3.org/2000/svg" height="32" viewBox="0 -960 960 960" width="32" fill="currentColor"><path d="M200-120v-80h200v-80q-83 0-141.5-58.5T200-480q0-61 33.5-111t90.5-73q8-34 35.5-55t62.5-21l-22-62 38-14-14-36 76-28 12 38 38-14 110 300-38 14 14 38-76 28-12-38-38 14-24-66q-15 14-34.5 21t-39.5 5q-22-2-41-13.5T338-582q-27 16-42.5 43T280-480q0 50 35 85t85 35h320v80H520v80h240v80H200Zm346-458 36-14-68-188-38 14 70 188Zm-126-22q17 0 28.5-11.5T460-640q0-17-11.5-28.5T420-680q-17 0-28.5 11.5T380-640q0 17 11.5 28.5T420-600Zm126 22Zm-126-62Zm0 0Z"/></svg>',
    previewImages: [
      '/config-previews/latent_lab_1.jpg',
      '/config-previews/latent_lab_2.jpg',
      '/config-previews/latent_lab_3.jpg',
      '/config-previews/latent_lab_4.jpg',
      '/config-previews/latent_lab_5.jpg',
      '/config-previews/latent_lab_6.jpg',
      '/config-previews/partial_elimination.png',
    ],
  },
]
</script>

<style scoped>
.landing-view {
  min-height: 100vh;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3rem;
}

/* Hero */
.hero {
  text-align: center;
  max-width: 700px;
  padding: 2rem 0;
}

.hero-title {
  font-size: clamp(2rem, 5vw, 3rem);
  font-weight: 700;
  color: rgba(255, 255, 255, 0.95);
  margin: 0 0 0.5rem 0;
  letter-spacing: 0.05em;
}

.hero-subtitle {
  font-size: clamp(1rem, 2.5vw, 1.25rem);
  color: rgba(255, 255, 255, 0.7);
  margin: 0 0 1rem 0;
  line-height: 1.5;
}

.hero-research {
  font-size: clamp(0.85rem, 2vw, 0.95rem);
  color: rgba(255, 255, 255, 0.45);
  margin: 0;
  line-height: 1.6;
}

/* Feature Grid */
.features {
  width: 100%;
  max-width: 1100px;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

/* Feature Card */
.feature-card {
  position: relative;
  background: rgba(20, 20, 20, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-4px);
  border-color: var(--feature-color);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), 0 0 20px color-mix(in srgb, var(--feature-color) 20%, transparent);
}

/* Preview area */
.card-preview {
  position: relative;
  height: 160px;
  overflow: hidden;
}

.preview-bg {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center;
  background-color: rgba(30, 30, 30, 0.8);
  transition: background-image 1s ease;
}

.preview-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to bottom, transparent 40%, rgba(20, 20, 20, 0.95) 100%);
}

/* Card body */
.card-body {
  padding: 1.25rem;
  position: relative;
}

.card-icon {
  color: var(--feature-color);
  margin-bottom: 0.75rem;
  display: flex;
  align-items: center;
}

.card-icon :deep(svg) {
  width: 28px;
  height: 28px;
}

.card-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  margin: 0 0 0.5rem 0;
}

.card-description {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
  line-height: 1.5;
}

/* Accent bar */
.card-accent {
  height: 3px;
  background: var(--feature-color);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.feature-card:hover .card-accent {
  opacity: 1;
}

/* Funding */
.funding {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 3rem 0 2rem;
  opacity: 0.8;
  transition: opacity 0.3s;
}

.funding:hover {
  opacity: 1;
}

.funding-logo {
  height: 80px;
  width: auto;
}

.project-link {
  color: rgba(255, 255, 255, 0.4);
  text-decoration: none;
  font-size: 0.85rem;
}

.project-link:hover {
  color: rgba(255, 255, 255, 0.7);
}

/* Responsive */
@media (max-width: 600px) {
  .landing-view {
    padding: 1rem;
    gap: 2rem;
  }

  .feature-grid {
    grid-template-columns: 1fr;
  }

  .card-preview {
    height: 120px;
  }
}
</style>
