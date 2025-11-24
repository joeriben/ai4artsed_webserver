# Session Handover: Cloudflare Tunnel Port Mismatch Fix

**Date:** 2025-11-17
**Issue:** Frontend displaying error messages when accessing via https://lab.ai4artsed.org

---

## Problem

Users accessing the application via internet (https://lab.ai4artsed.org) see error messages in red boxes. These are frontend error displays triggered by failed API calls.

## Root Cause

Cloudflare tunnel configuration routes to **wrong port**.

### Evidence

```bash
$ cloudflared tunnel ingress rule https://lab.ai4artsed.org
service: http://localhost:80  # ❌ WRONG - nothing listens on port 80

$ lsof -i :17801
python3 117127 ... *:17801 (LISTEN)  # ✅ Flask actually runs on 17801
```

### Config Files

Two cloudflared config files exist:
- `/etc/cloudflared/config.yml` → **port 17801** (correct, but not used)
- `~/.cloudflared/config.yml` → **port 80** (incorrect, currently active)

Cloudflared service loads `~/.cloudflared/config.yml` by default.

## Solution

### 1. Fix Cloudflare Config

Edit `~/.cloudflared/config.yml`:

```bash
nano ~/.cloudflared/config.yml
```

Find line with:
```yaml
service: http://localhost:80
```

Change to:
```yaml
service: http://localhost:17801
```

### 2. Restart Cloudflared

```bash
sudo systemctl restart cloudflared
```

### 3. Verify Fix

```bash
# Check routing
cloudflared tunnel ingress rule https://lab.ai4artsed.org
# Should output: service: http://localhost:17801

# Test external access
curl -I https://lab.ai4artsed.org/
# Should return: HTTP/2 200

curl -s https://lab.ai4artsed.org/pipeline_configs_with_properties | jq '.configs | length'
# Should return: 18 (or current config count)
```

## Technical Details

### Frontend Error Flow

1. Frontend calls `fetch('/pipeline_configs_with_properties')`
2. Request goes through Cloudflare tunnel to localhost:80
3. Nothing listens on port 80 → connection refused/timeout
4. Frontend receives error response
5. `configSelection.ts` line 170-171: throws error
6. `PropertyQuadrantsView.vue` line 10-16: displays red error box

### What Works

- ✅ Local access (localhost:17801, localhost:17802)
- ✅ WiFi access (192.168.178.144:17801)
- ❌ External access (https://lab.ai4artsed.org) - wrong port

## Files Modified

None yet - fix needs to be applied.

## Related

- Cloudflare tunnel: `werkraum-tunnel`
- Credentials: `/home/joerissen/.cloudflared/b614ccb7-c8f3-4831-bfbb-d4674a0e2749.json`
- Active config: `~/.cloudflared/config.yml`
