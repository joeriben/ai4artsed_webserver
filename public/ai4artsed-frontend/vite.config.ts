import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['apple-touch-icon.png', 'icon-192x192.png', 'icon-512x512.png'],
      manifest: {
        name: 'AI4ArtsEd',
        short_name: 'AI4Arts',
        description: 'AI-powered art education platform with prompt interception',
        theme_color: '#0a0a0a',
        background_color: '#0a0a0a',
        display: 'standalone',
        icons: [
          {
            src: 'icon-192x192.png',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: 'icon-512x512.png',
            sizes: '512x512',
            type: 'image/png'
          },
          {
            src: 'apple-touch-icon.png',
            sizes: '180x180',
            type: 'image/png',
            purpose: 'apple touch icon'
          }
        ]
      },
      workbox: {
        // Cache static assets only, not API calls
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff,woff2}'],
        // Don't cache API routes
        navigateFallbackDenylist: [/^\/api/, /^\/pipeline_configs/],
        runtimeCaching: [
          {
            // Cache generated images from media API
            urlPattern: /^https:\/\/lab\.ai4artsed\.org\/api\/media\/.*/i,
            handler: 'CacheFirst',
            options: {
              cacheName: 'media-cache',
              expiration: {
                maxEntries: 50,
                maxAgeSeconds: 60 * 60 * 24 * 7 // 7 days
              },
              cacheableResponse: {
                statuses: [0, 200]
              }
            }
          }
        ]
      }
    })
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
