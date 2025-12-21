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
    hmr: true,  // Enable HMR for instant browser updates
    proxy: {
      // Dev frontend proxies to dev backend (17802)
      // Production uses 17801
      '/api/text_stream': {
        target: 'http://localhost:17802',
        changeOrigin: true,
        // CRITICAL: Disable buffering for SSE streams
        configure: (proxy, options) => {
          proxy.on('proxyReq', (proxyReq, req, res) => {
            // Set headers to prevent buffering
            proxyReq.setHeader('X-Accel-Buffering', 'no')
          })
          proxy.on('proxyRes', (proxyRes, req, res) => {
            // Disable all buffering for SSE
            proxyRes.headers['x-accel-buffering'] = 'no'
            proxyRes.headers['cache-control'] = 'no-cache'
          })
        }
      },
      '/api': {
        target: 'http://localhost:17802',
        changeOrigin: true,
      },
      '/exports/json': {
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
