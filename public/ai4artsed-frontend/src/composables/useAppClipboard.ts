import { ref } from 'vue'

// Global clipboard state shared across all components
const appClipboard = ref('')

export function useAppClipboard() {
  const copy = (text: string) => {
    appClipboard.value = text
  }

  const paste = () => {
    return appClipboard.value
  }

  const clear = () => {
    appClipboard.value = ''
  }

  return {
    appClipboard,
    copy,
    paste,
    clear
  }
}
