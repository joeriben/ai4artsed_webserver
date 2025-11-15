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
      // Phase 2: Organic force-based creative input interface
      component: () => import('../views/Phase2CreativeFlowView.vue'),
    },
  ],
})

export default router
