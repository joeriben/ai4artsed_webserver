import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import i18n from './i18n'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(i18n)

// Initialize global user preferences and sync with i18n
// Must be done after pinia and i18n are installed
import { useUserPreferencesStore } from './stores/userPreferences'
import { useSafetyLevelStore } from './stores/safetyLevel'
import { watch } from 'vue'

const userPreferences = useUserPreferencesStore()

// Fetch safety level for feature gating (non-blocking)
const safetyLevelStore = useSafetyLevelStore()
safetyLevelStore.fetchLevel()

// Initial sync with vue-i18n
i18n.global.locale.value = userPreferences.language

// Watch for language changes and sync with i18n
watch(
  () => userPreferences.language,
  (newLanguage) => {
    i18n.global.locale.value = newLanguage
    console.log(`[i18n] Language synced to: ${newLanguage}`)
  }
)

app.mount('#app')
