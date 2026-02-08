import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/select'
    },
    {
      path: '/home',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue'),
    },
    {
      path: '/select',
      name: 'property-selection',
      // Phase 1: Property-based config selection interface
      component: () => import('../views/PropertyQuadrantsView.vue'),
    },
    {
      path: '/execute/:configId',
      name: 'pipeline-execution',
      // Phase 2: Dynamically loads pipeline-specific Vue (e.g., direct.vue, text_transformation.vue)
      component: () => import('../views/PipelineRouter.vue'),
    },
    {
      path: '/text-transformation',
      name: 'text-transformation',
      // Phase 2: text_transformation pipeline visualization (text-based mode)
      component: () => import('../views/text_transformation.vue'),
    },
    {
      path: '/image-transformation',
      name: 'image-transformation',
      // Session 80: image_transformation pipeline visualization (image-based mode)
      component: () => import('../views/image_transformation.vue'),
    },
    {
      path: '/multi-image-transformation',
      name: 'multi-image-transformation',
      // Session 86+: Multi-image transformation (1-3 images → 1 image fusion)
      component: () => import('../views/multi_image_transformation.vue'),
    },
    {
      path: '/direct',
      name: 'direct',
      // Phase 2: direct pipeline (surrealization) visualization
      component: () => import('../views/direct.vue'),
    },
    {
      path: '/surrealizer',
      name: 'surrealizer',
      // Surrealizer: T5-CLIP interpolation for surreal image variations
      component: () => import('../views/surrealizer.vue'),
    },
    {
      path: '/settings',
      name: 'settings',
      // Configuration settings page
      component: () => import('../views/SettingsView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/impressum',
      name: 'impressum',
      component: () => import('../views/ImpressumView.vue'),
    },
    {
      path: '/datenschutz',
      name: 'datenschutz',
      component: () => import('../views/DatenschutzView.vue'),
    },
    {
      path: '/dokumentation',
      name: 'dokumentation',
      component: () => import('../views/DokumentationView.vue'),
    },
    {
      path: '/training',
      name: 'training',
      component: () => import('../views/TrainingView.vue'),
    },
    {
      path: '/canvas',
      name: 'canvas-workflow',
      // Session 129: Canvas workflow builder for parallel fan-out workflows
      component: () => import('../views/canvas_workflow.vue'),
    },
    {
      path: '/music-generation',
      name: 'music-generation',
      // Unified music generation with Simple/Advanced mode toggle
      component: () => import('../views/music_generation_unified.vue'),
    },
    {
      path: '/music-generation-simple',
      name: 'music-generation-simple',
      // Direct access to V1 (Simple) for testing
      component: () => import('../views/music_generation.vue'),
    },
    {
      path: '/music-generation-advanced',
      name: 'music-generation-advanced',
      // Direct access to V2 (Advanced) for testing
      component: () => import('../views/music_generation_v2.vue'),
    },
    {
      path: '/animation-test',
      name: 'animation-test',
      // Test page for GPU visualization animations
      component: () => import('../views/AnimationTestView.vue'),
    },
    {
      path: '/dev/pixel-editor',
      name: 'pixel-editor',
      // Dev tool: visual pixel template editor for Bits & Pixels animation
      component: () => import('../views/PixelTemplateEditorView.vue'),
    },
  ],
})

// Check authentication for protected routes
router.beforeEach(async (to, from, next) => {
  if (to.meta.requiresAuth) {
    try {
      const response = await fetch('/api/settings/check-auth', {
        credentials: 'include'
      })
      const data = await response.json()

      if (data.authenticated) {
        next()
      } else {
        // Redirect to home with auth requirement query param
        next({ name: 'property-selection', query: { authRequired: 'settings' } })
      }
    } catch (e) {
      console.error('Auth check failed:', e)
      next({ name: 'property-selection' })
    }
  } else {
    next()
  }
})

export default router
