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
    host: '0.0.0.0',   // Listen on all network interfaces (WLAN + Cloudflare)
    port: 5173,
    strictPort: true,  // Fail if port is already in use (required for Cloudflared)
    allowedHosts: [
      'lab.ai4artsed.org',  // Allow Cloudflare tunnel subdomain
      '.ai4artsed.org',     // Allow all subdomains
    ],
    hmr: false,  // Disable HMR for Cloudflare deployment
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
