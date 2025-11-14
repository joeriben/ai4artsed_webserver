# Progressive Web App (PWA) Setup

**Date:** 2025-11-14
**Status:** ✅ Active
**Purpose:** Enable installation of AI4ArtsEd as mobile/desktop app

---

## What is a PWA?

A Progressive Web App allows users to "install" the web application on their device without going through an app store.

**Benefits:**
- ✅ Install from browser (no App Store needed)
- ✅ Works offline (with cached assets)
- ✅ Faster loading (cached JS/CSS)
- ✅ App-like experience (no browser UI)
- ✅ Automatic updates
- ✅ Works on iOS, Android, Desktop

---

## Installation Instructions

### On iPad/iPhone:

1. Open **Safari** (not Chrome!)
2. Navigate to `https://lab.ai4artsed.org`
3. Tap **Share button** (square with arrow)
4. Scroll down and tap **"Zum Home-Bildschirm hinzufügen"** / **"Add to Home Screen"**
5. Tap **"Hinzufügen"** / **"Add"**
6. App icon appears on Home Screen!

### On Android:

1. Open **Chrome**
2. Navigate to `https://lab.ai4artsed.org`
3. Tap **menu** (3 dots)
4. Tap **"App installieren"** / **"Install app"**
5. App icon appears on Home Screen!

### On Desktop:

1. Open **Chrome** or **Edge**
2. Navigate to `https://lab.ai4artsed.org`
3. Look for **install icon** in address bar (⊕ or ↓)
4. Click to install
5. App opens in separate window!

---

## Technical Implementation

### Files Modified:

**1. `public/ai4artsed-frontend/package.json`**
- Added: `vite-plugin-pwa: ^0.21.1`

**2. `public/ai4artsed-frontend/vite.config.ts`**
- Added PWA plugin configuration
- Configured Service Worker
- Set up caching strategy

**3. Icons Created:**
- `public/icon-192x192.png` (192x192 Android icon)
- `public/icon-512x512.png` (512x512 Android icon)
- `public/apple-touch-icon.png` (180x180 iOS icon)

### Generated Files (in dist/ after build):

- `sw.js` - Service Worker (auto-generated)
- `workbox-*.js` - Workbox library (auto-generated)
- `manifest.webmanifest` - App metadata (auto-generated)
- `registerSW.js` - Service Worker registration (auto-generated)

---

## Caching Strategy

### What is Cached:
✅ Static assets (JS, CSS, HTML)
✅ Icons and fonts
✅ Generated images from `/api/media/*` (7 days max)

### What is NOT Cached:
❌ API calls (`/api/*`)
❌ Config endpoints (`/pipeline_configs*`)
❌ Dynamic data

**Result:** App loads fast, but always shows fresh data!

---

## Update Strategy

**Mode:** `autoUpdate`

**How it works:**
1. User opens app
2. Service Worker checks for new version
3. If new version available:
   - Downloads in background
   - Activates on next app start
4. User gets update automatically (no manual action needed)

**Alternative:** Set `registerType: 'prompt'` to ask user before updating.

---

## Configuration Details

### Manifest Settings:

```json
{
  "name": "AI4ArtsEd",
  "short_name": "AI4Arts",
  "description": "AI-powered art education platform with prompt interception",
  "theme_color": "#0a0a0a",
  "background_color": "#0a0a0a",
  "display": "standalone"
}
```

### Service Worker Settings:

- **Precache:** 19 entries (~341 KB)
- **Cache Name:** `media-cache` (for generated images)
- **Max Entries:** 50 images
- **Max Age:** 7 days

---

## Testing

### Test on Production:

1. Build: `npm run build`
2. Deploy to production (copy dist/ to server)
3. Open https://lab.ai4artsed.org on mobile device
4. Install app (see instructions above)
5. Open app → should work without browser UI
6. Test offline: Turn off WiFi → app should still load (with cached assets)

### Verify Service Worker:

**Chrome DevTools:**
1. Open https://lab.ai4artsed.org
2. Open DevTools (F12)
3. Go to **Application** tab
4. Check **Service Workers** → should show `sw.js` as active
5. Check **Manifest** → should show app metadata
6. Check **Cache Storage** → should show cached files

---

## Troubleshooting

### "Install" button doesn't appear:

- ✅ Use HTTPS (required for PWA)
- ✅ Must be in browser (not already installed)
- ✅ Use supported browser (Safari on iOS, Chrome on Android)

### Service Worker not registering:

- Check browser console for errors
- Verify `sw.js` is served correctly
- Clear cache and reload

### Cached old version:

1. Uninstall app
2. Clear browser cache
3. Reinstall

### Icons not showing:

- Check icons exist in `public/` directory
- Verify icon paths in manifest
- Clear browser cache

---

## Future Enhancements

**Possible additions (not implemented yet):**

- 🔔 **Push Notifications** (requires backend support)
- 📸 **Camera Access** (for image capture in prompts)
- 📂 **File System Access** (for saving/loading projects)
- 🔄 **Background Sync** (for offline generation queue)

**To add these:** Switch from PWA to Capacitor (see `docs/CAPACITOR_SETUP.md` - to be created)

---

## References

- [Vite PWA Plugin Documentation](https://vite-pwa-org.netlify.app/)
- [PWA on MDN](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)
- [iOS PWA Support](https://developer.apple.com/documentation/webkit/supporting_pwas)

---

## Notes

- PWA works best on **HTTPS** (already configured via Cloudflare)
- iOS has **limitations** vs native apps (no push notifications, no background processing)
- For full native features → use Capacitor instead
- Current setup: **Browser + PWA** (best of both worlds)
