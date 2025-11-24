<template>
  <component :is="pipelineComponent" v-if="pipelineComponent" />
  <div v-else class="loading">
    <div class="spinner"></div>
    <p>Pipeline wird geladen...</p>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, defineAsyncComponent } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const pipelineComponent = ref<any>(null)

onMounted(async () => {
  const configId = route.params.configId as string

  try {
    // Fetch config pipeline metadata to determine which Vue to load
    const response = await axios.get(`/api/config/${configId}/pipeline`)
    const pipelineName = response.data.pipeline_name

    console.log(`[PipelineRouter] Config '${configId}' uses pipeline '${pipelineName}'`)

    // Dynamically import the Vue component matching the pipeline name
    pipelineComponent.value = defineAsyncComponent(() =>
      import(`../views/${pipelineName}.vue`)
        .catch(() => {
          // Fallback to text_transformation if specific pipeline Vue doesn't exist
          console.warn(`[PipelineRouter] Vue for pipeline '${pipelineName}' not found, using text_transformation`)
          return import('../views/text_transformation.vue')
        })
    )
  } catch (error) {
    console.error('[PipelineRouter] Error loading pipeline:', error)
    // Fallback to text_transformation
    pipelineComponent.value = defineAsyncComponent(() => import('../views/text_transformation.vue'))
  }
})
</script>

<style scoped>
.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: #0a0a0a;
  color: white;
  gap: 1rem;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 255, 255, 0.1);
  border-top-color: #4CAF50;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
