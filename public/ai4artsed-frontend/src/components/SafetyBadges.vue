<template>
  <transition-group name="badge-fade" tag="div" class="safety-badges">
    <div v-for="check in checks" :key="check" class="safety-badge">
      <span class="badge-icon">✓</span>
      <span class="badge-label">{{ badgeLabel(check) }}</span>
    </div>
  </transition-group>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'

defineProps<{
  checks: string[]
}>()

const { t } = useI18n()

function badgeLabel(check: string): string {
  return t(`safetyBadges.${check}`, check)
}
</script>

<style scoped>
.safety-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  justify-content: center;
  align-items: center;
}

.safety-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.2rem 0.5rem;
  background: rgba(76, 175, 80, 0.12);
  border: 1px solid #4CAF50;
  border-radius: 6px;
  animation: badge-appear 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes badge-appear {
  0% {
    opacity: 0;
    transform: scale(0.7);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

.badge-icon {
  font-size: 0.75rem;
  color: #4CAF50;
  font-weight: bold;
  line-height: 1;
}

.badge-label {
  font-size: 0.65rem;
  font-weight: 600;
  color: #4CAF50;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  white-space: nowrap;
}

/* Transition classes */
.badge-fade-enter-active {
  transition: all 0.3s ease;
}
.badge-fade-leave-active {
  transition: all 0.2s ease;
}
.badge-fade-enter-from,
.badge-fade-leave-to {
  opacity: 0;
  transform: scale(0.7);
}
</style>
