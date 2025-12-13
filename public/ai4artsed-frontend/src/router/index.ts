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
      path: '/partial-elimination',
      name: 'partial-elimination',
      // Partial Elimination: Vector dimension manipulation (3 images)
      component: () => import('../views/partial_elimination.vue'),
    },
    {
      path: '/settings',
      name: 'settings',
      // Configuration settings page
      component: () => import('../views/SettingsView.vue'),
    },
  ],
})



export default router
