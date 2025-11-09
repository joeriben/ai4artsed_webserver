import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:17801',
        changeOrigin: true,
      },
      '/pipeline_configs_with_properties': {
        target: 'http://localhost:17801',
        changeOrigin: true,
      },
      '/pipeline_configs_metadata': {
        target: 'http://localhost:17801',
        changeOrigin: true,
      }
    }
  }
})
