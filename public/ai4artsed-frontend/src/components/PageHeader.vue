<template>
  <header class="page-header">
    <button class="return-button" @click="$router.push('/')" title="Zurück zu Phase 1">
      ← Phase 1
    </button>
    <h1 class="page-title">AI4ArtsEd - AI-Lab</h1>
  </header>
</template>

<script setup lang="ts">
// No props or state needed - static header
</script>

<style scoped>
.page-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;

  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2rem;
  padding: clamp(1rem, 2vh, 1.5rem) clamp(1rem, 3vw, 2rem);
  background: rgba(10, 10, 10, 0.95);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.page-title {
  font-size: clamp(1.2rem, 3vw, 1.5rem);
  font-weight: 700;
  color: #ffffff;
  margin: 0;
  text-align: center;
  letter-spacing: 0.5px;
}

.return-button {
  position: absolute;
  left: clamp(1rem, 3vw, 2rem);

  padding: clamp(0.4rem, 1vw, 0.6rem) clamp(0.8rem, 2vw, 1.2rem);
  background: rgba(30, 30, 30, 0.9);
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  color: #ffffff;
  font-size: clamp(0.85rem, 1.8vw, 0.95rem);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.return-button:hover {
  border-color: rgba(102, 126, 234, 0.8);
  background: rgba(102, 126, 234, 0.2);
  transform: translateX(-4px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.return-button:active {
  transform: translateX(-2px) scale(0.98);
}
</style>
