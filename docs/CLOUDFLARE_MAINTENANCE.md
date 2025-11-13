# Cloudflare Maintenance Guide

**Last Updated:** 2025-11-13
**System Version:** 2.0.0-alpha.2

---

## Overview

The ai4artsed system is deployed via **Cloudflare Tunnel**, which connects the local Flask backend (running on port 17801) to the public internet at **https://lab.ai4artsed.org**.

This guide explains how Cloudflare works with our system and critical maintenance operations.

---

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Internet User                      │
└───────────────────┬─────────────────────────────────┘
                    │
                    ↓ HTTPS (with Cloudflare Access)
┌─────────────────────────────────────────────────────┐
│         Cloudflare Edge Network (CDN)               │
│              lab.ai4artsed.org                      │
│                                                     │
│  ┌──────────────────────────────────────┐         │
│  │  Edge Cache (CRITICAL!)              │         │
│  │  • Caches responses (including 404s) │         │
│  │  • Can serve stale content           │         │
│  │  • Must be purged after deployments  │         │
│  └──────────────────────────────────────┘         │
└───────────────────┬─────────────────────────────────┘
                    │
                    ↓ Cloudflare Tunnel (port 17801)
┌─────────────────────────────────────────────────────┐
│       Flask Backend (127.0.0.1:17801)              │
│                                                     │
│  • Serves production build (dist/)                 │
│  • MIME types: text/javascript                     │
│  • SPA routing: index.html fallback                │
│  • API endpoints: /api/*, /pipeline_configs_*      │
└─────────────────────────────────────────────────────┘
```

---

## Understanding Cloudflare's Edge Cache

### What is the Edge Cache?

Cloudflare operates a **Content Delivery Network (CDN)** with servers around the world. When a user accesses your site:

1. Request goes to nearest Cloudflare edge server
2. **If content is cached**, Cloudflare serves it directly (FAST)
3. **If not cached**, Cloudflare fetches from your origin server (Flask)
4. Cloudflare then **caches the response** for future requests

### Why This Caused the 404 Problem

**Timeline of what happened:**

1. **Old config**: Cloudflare Tunnel pointed to Vite dev server (port 5173)
2. **User accessed site**: Cloudflare fetched assets, got 404s (MIME type issues)
3. **Cloudflare cached those 404s** at edge servers
4. **We fixed Flask config**: Changed tunnel to point to port 17801
5. **User accessed site again**: Cloudflare served **cached 404s** (not new content!)
6. **We restarted backend/tunnel**: No effect - cache is on **Cloudflare's edge**, not our server
7. **Purged cache**: Forced Cloudflare to fetch fresh content from Flask
8. **System worked**: ✅

### Key Insight

**Cloudflare caches EVERYTHING** - including error responses. Even after fixing your backend, users see old cached responses until you purge the cache.

---

## Deployment Workflow

### Standard Deployment (No Code Changes)

If you're just rebuilding the frontend with no route changes:

```bash
cd /home/joerissen/ai/ai4artsed_webserver/public/ai4artsed-frontend
./deploy_production.sh
```

**No cache purge needed** - Vite generates new filenames (e.g., `index-ABC123.js` → `index-DEF456.js`), so old cached files are automatically bypassed.

### Deployment After Route/Config Changes

If you changed:
- Flask routes (`static_routes.py`, API endpoints)
- Cloudflare tunnel config
- Backend server configuration
- Any structural changes

**You MUST purge Cloudflare cache:**

1. Run deployment script:
   ```bash
   cd /home/joerissen/ai/ai4artsed_webserver/public/ai4artsed-frontend
   ./deploy_production.sh
   ```

2. **Purge Cloudflare cache** (see below)

3. **Test in browser** with Ctrl+Shift+R (hard refresh)

---

## Cloudflare Cache Operations

### How to Purge Cache

**Option 1: Cloudflare Dashboard (Recommended)**

1. Log in to [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Select domain: **ai4artsed.org**
3. Go to **Caching** → **Configuration**
4. Click **Purge Everything** button
5. Confirm purge
6. Wait 30 seconds for propagation

**Option 2: Cloudflare API (Advanced)**

```bash
# Get Zone ID
ZONE_ID="your_zone_id"
API_TOKEN="your_api_token"

# Purge everything
curl -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/purge_cache" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"purge_everything":true}'
```

### Development Mode

**What it does:** Bypasses Cloudflare's edge cache entirely - all requests go directly to origin (Flask).

**When to use:**
- During active development/testing
- When debugging cache-related issues
- After major deployments (temporary)

**How to enable:**

1. Cloudflare Dashboard → **Caching** → **Configuration**
2. Toggle **Development Mode** ON
3. **Auto-disables after 3 hours**

**Performance impact:** Site will be slower (no edge caching), but ensures fresh content.

**Remember to disable** once testing is complete!

---

## Cloudflare Tunnel Operations

### Check Tunnel Status

```bash
# Check if cloudflared service is running
systemctl status cloudflared

# View live logs
journalctl -u cloudflared -f

# Check tunnel connections
# Should show "Registered tunnel connection" x4
journalctl -u cloudflared --since "5 minutes ago" | grep -i connection
```

### Restart Tunnel

**When to restart:**
- After changing `/etc/cloudflared/config.yml`
- If tunnel connections drop
- After backend port changes

```bash
sudo systemctl restart cloudflared
```

### Tunnel Configuration

**File:** `/etc/cloudflared/config.yml`

```yaml
tunnel: werkraum-tunnel
credentials-file: /home/joerissen/.cloudflared/b614ccb7-c8f3-4831-bfbb-d4674a0e2749.json

ingress:
  - hostname: lab.ai4artsed.org
    service: http://127.0.0.1:17801  # Flask backend (production)
    originRequest:
      httpHostHeader: lab.ai4artsed.org
      connectTimeout: 30s

  - hostname: ssh-fedora.ai4artsed.org
    service: ssh://localhost:22

  - service: http_status:404
```

**Backup:** `/etc/cloudflared/config.yml.backup` (created 2025-11-13)

### Change Backend Port

1. Edit config:
   ```bash
   sudo nano /etc/cloudflared/config.yml
   ```

2. Change `service` line:
   ```yaml
   service: http://127.0.0.1:NEW_PORT
   ```

3. Restart tunnel:
   ```bash
   sudo systemctl restart cloudflared
   ```

4. **Purge Cloudflare cache** (important!)

5. Test new configuration

---

## Backend Operations

### Start/Stop/Restart Backend

**Start backend:**
```bash
cd /home/joerissen/ai/ai4artsed_webserver/devserver
python3 server.py > /tmp/backend_production.log 2>&1 &
```

**Check if running:**
```bash
lsof -ti:17801
# Returns PID if running
```

**Stop backend:**
```bash
pkill -f "python3.*server.py"
```

**View logs:**
```bash
tail -f /tmp/backend_production.log
```

### Backend Serves From

**Production build location:**
```
/home/joerissen/ai/ai4artsed_webserver/public/ai4artsed-frontend/dist/
```

**Configured in:** `devserver/config.py` (line 11)
```python
PUBLIC_DIR = Path(__file__).parent.parent / "public" / "ai4artsed-frontend" / "dist"
```

---

## Troubleshooting

### Problem: Site shows old content after deployment

**Symptoms:**
- Deployed new version but see old UI
- Browser shows cached version
- No errors, just outdated

**Solution:**
1. Purge Cloudflare cache (see above)
2. Hard refresh browser: Ctrl+Shift+R (Linux/Win) or Cmd+Shift+R (Mac)
3. Clear browser cache if needed

---

### Problem: 404 errors for all assets

**Symptoms:**
- Browser console: `404 Not Found` for `.js` files
- Black/white screen
- No Vue app loads

**Solution:**
1. Check Flask backend is running:
   ```bash
   lsof -i:17801
   ```

2. Test local access:
   ```bash
   curl -I http://localhost:17801/
   # Should return 200 OK
   ```

3. If backend not running, restart it:
   ```bash
   cd /home/joerissen/ai/ai4artsed_webserver/public/ai4artsed-frontend
   ./deploy_production.sh
   ```

4. **Purge Cloudflare cache** (critical!)

5. Check tunnel is running:
   ```bash
   systemctl status cloudflared
   ```

---

### Problem: MIME type errors

**Symptoms:**
- Browser console: `disallowed MIME type ('')`
- or: `MIME type ('text/html') is not a supported stylesheet MIME type`
- Assets loading as HTML instead of JavaScript

**Solution:**
1. Verify Flask serves correct MIME type locally:
   ```bash
   curl -I http://localhost:17801/assets/index-*.js | grep Content-Type
   # Should show: text/javascript; charset=utf-8
   ```

2. If MIME type is wrong locally:
   - Check `devserver/my_app/routes/static_routes.py` has explicit MIME handling
   - Clear Python cache: `rm -rf devserver/my_app/__pycache__`
   - Restart backend

3. If MIME type correct locally but wrong through Cloudflare:
   - **Purge Cloudflare cache**
   - Enable Development Mode temporarily
   - Test again

---

### Problem: Vue routes return 404 (e.g., /select, /execute/123)

**Symptoms:**
- Direct navigation to `/select` shows 404
- Refresh on any Vue route shows error
- Only root `/` works

**Solution:**
1. Verify SPA routing works locally:
   ```bash
   curl -I http://localhost:17801/select
   # Should return 200 OK (serves index.html)
   ```

2. Check `static_routes.py` has catch-all route:
   ```python
   @static_bp.route('/', defaults={'path': ''})
   @static_bp.route('/<path:path>')
   def serve_spa(path):
       # ... serves index.html for non-file paths
   ```

3. Verify blueprint order in `__init__.py`:
   - API blueprints registered FIRST
   - `static_bp` registered LAST

4. **Purge Cloudflare cache**

---

### Problem: API endpoints return 404

**Symptoms:**
- Frontend loads but shows no data
- Console errors: `404` on `/api/*` or `/pipeline_configs_*`

**Solution:**
1. Test API locally:
   ```bash
   curl http://localhost:17801/pipeline_configs_with_properties
   # Should return JSON
   ```

2. If 404 locally:
   - Check API blueprint registration in `__init__.py`
   - Ensure API blueprints registered BEFORE `static_bp`

3. Check backend logs:
   ```bash
   tail -50 /tmp/backend_production.log
   ```

---

### Problem: Cloudflare tunnel not connecting

**Symptoms:**
- `systemctl status cloudflared` shows errors
- No tunnel connections established
- Site completely inaccessible

**Solution:**
1. Check tunnel logs:
   ```bash
   journalctl -u cloudflared --since "10 minutes ago"
   ```

2. Look for connection errors:
   - `connection refused` → Backend not running
   - `authentication failed` → Credentials issue
   - `timeout` → Network/firewall issue

3. Verify backend is accessible:
   ```bash
   curl http://127.0.0.1:17801/
   ```

4. Restart tunnel:
   ```bash
   sudo systemctl restart cloudflared
   ```

5. If still failing, check config:
   ```bash
   cat /etc/cloudflared/config.yml
   # Verify port matches backend
   ```

---

## Complete Deployment Checklist

Use this checklist for major deployments:

### Pre-Deployment

- [ ] Code changes committed to git
- [ ] Frontend builds successfully (`npm run build`)
- [ ] Backend runs without errors locally
- [ ] API endpoints tested locally

### Deployment

- [ ] Run deployment script:
  ```bash
  ./deploy_production.sh
  ```
- [ ] Verify backend started (check script output)
- [ ] Check backend logs for errors:
  ```bash
  tail -20 /tmp/backend_production.log
  ```

### Post-Deployment

- [ ] **Purge Cloudflare cache** (if route/config changes)
- [ ] Test root URL: https://lab.ai4artsed.org/
- [ ] Test Vue routes: `/select`, `/execute/test`
- [ ] Test API endpoints (check browser console)
- [ ] Verify MIME types (no console errors)
- [ ] Test functionality end-to-end

### If Issues Occur

- [ ] Check browser console for errors
- [ ] Test local access: http://localhost:17801
- [ ] Enable Cloudflare Development Mode
- [ ] Purge cache again
- [ ] Check tunnel status: `systemctl status cloudflared`
- [ ] Review backend logs: `tail -f /tmp/backend_production.log`

---

## Quick Reference Commands

### Most Common Operations

```bash
# Deploy new frontend build
cd /home/joerissen/ai/ai4artsed_webserver/public/ai4artsed-frontend
./deploy_production.sh

# Check if backend is running
lsof -i:17801

# Restart backend manually
pkill -f "python3.*server.py"
cd /home/joerissen/ai/ai4artsed_webserver/devserver
python3 server.py > /tmp/backend_production.log 2>&1 &

# Check backend logs
tail -f /tmp/backend_production.log

# Check tunnel status
systemctl status cloudflared

# Restart tunnel
sudo systemctl restart cloudflared

# View tunnel logs
journalctl -u cloudflared -f
```

### Testing Commands

```bash
# Test local backend (MIME type)
curl -I http://localhost:17801/assets/index-*.js | grep Content-Type

# Test local backend (SPA routing)
curl -I http://localhost:17801/select

# Test local backend (API)
curl http://localhost:17801/pipeline_configs_with_properties | jq .

# Test through Cloudflare (requires authentication in browser)
curl -L https://lab.ai4artsed.org/
```

---

## Important Files

### Configuration Files

| File | Purpose | Backup Location |
|------|---------|-----------------|
| `/etc/cloudflared/config.yml` | Tunnel routing config | `/etc/cloudflared/config.yml.backup` |
| `devserver/config.py` | Flask config (PUBLIC_DIR) | Git versioned |
| `devserver/my_app/__init__.py` | Blueprint registration | Git versioned |
| `devserver/my_app/routes/static_routes.py` | SPA routing logic | Git versioned |
| `public/ai4artsed-frontend/vite.config.ts` | Vite build config | Git versioned |

### Log Files

| File | Content |
|------|---------|
| `/tmp/backend_production.log` | Flask backend logs (from deploy script) |
| `/tmp/backend_final.log` | Flask backend logs (manual starts) |
| `journalctl -u cloudflared` | Cloudflare tunnel logs (systemd) |

---

## Emergency Rollback

If deployment breaks everything:

1. **Restore old Cloudflare config:**
   ```bash
   sudo cp /etc/cloudflared/config.yml.backup /etc/cloudflared/config.yml
   sudo systemctl restart cloudflared
   ```

2. **Revert git changes:**
   ```bash
   cd /home/joerissen/ai/ai4artsed_webserver
   git log --oneline -5  # Find commit before deployment
   git revert <commit_hash>
   ```

3. **Rebuild frontend from old code:**
   ```bash
   cd public/ai4artsed-frontend
   npm run build
   ```

4. **Restart backend:**
   ```bash
   pkill -f "python3.*server.py"
   cd ../../devserver
   python3 server.py > /tmp/backend_production.log 2>&1 &
   ```

5. **Purge Cloudflare cache**

---

## Version History

### v2.0.0-alpha.2 (2025-11-13)

**Changes:**
- Implemented production build deployment
- Fixed Flask SPA routing with explicit MIME types
- Updated Cloudflare tunnel config (5173 → 17801)
- Created automated deployment script
- **Resolved:** Cloudflare edge cache issue (required manual purge)

**Key Files Modified:**
- `devserver/config.py` - PUBLIC_DIR path
- `devserver/my_app/__init__.py` - Blueprint order
- `devserver/my_app/routes/static_routes.py` - Complete rewrite
- `/etc/cloudflared/config.yml` - Port change

**Lesson Learned:** Always purge Cloudflare cache after route/config changes.

---

## Additional Resources

- **Cloudflare Tunnel Docs:** https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/
- **Cloudflare Caching Docs:** https://developers.cloudflare.com/cache/
- **Vite Deployment Guide:** https://vitejs.dev/guide/static-deploy.html
- **Vue Router HTML5 Mode:** https://router.vuejs.org/guide/essentials/history-mode.html

---

## Support

If you encounter issues not covered in this guide:

1. Check `docs/PRODUCTION_DEPLOYMENT_IMPLEMENTATION_SUMMARY.md` for implementation details
2. Review `docs/VITE_VUE_CLOUDFLARE_DEPLOYMENT_GUIDE.md` for architectural guidance
3. Check git history for recent changes that might have caused issues

**System Status:** ✅ Operational
**Last Verified:** 2025-11-13
**Public URL:** https://lab.ai4artsed.org
