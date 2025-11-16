import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
// import { VitePWA } from 'vite-plugin-pwa'  // DISABLED: Causing caching issues

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    // PWA DISABLED: Service worker caching was causing inconsistent behavior
    // across iOS/Firefox and making debugging impossible. Can re-enable later
    // with proper cache versioning once system is stable.
    // VitePWA({ ... })
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
      // Dev frontend proxies to dev backend (17802)
      // Production uses 17801
      '/api': {
        target: 'http://localhost:17802',
        changeOrigin: true,
      },
      '/pipeline_configs_with_properties': {
        target: 'http://localhost:17802',
        changeOrigin: true,
      },
      '/pipeline_configs_metadata': {
        target: 'http://localhost:17802',
        changeOrigin: true,
      }
    }
  }
})
