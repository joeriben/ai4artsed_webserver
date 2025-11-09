<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Redirect to property selection on mount
onMounted(() => {
  router.replace('/select')
})
</script>

<template>
  <div class="home-redirect">
    <!-- Redirecting to property selection... -->
  </div>
</template>

<style scoped>
.home-redirect {
  display: none;
}
</style>
