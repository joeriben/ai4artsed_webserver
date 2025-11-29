# AI4ArtsEd DevServer - Deployment Guide

**Last Updated:** 2025-11-29 (Session 80)

---

## System Architecture

### Directories

```
Development:  /home/joerissen/ai/ai4artsed_development/
Production:   /home/joerissen/ai/ai4artsed_production/
```

### Key Principles

1. **Source code is committed**, `/dist` is gitignored
2. **Each environment builds its own frontend** locally
3. **Work on develop**, deploy from main
4. **Production pulls from GitHub**, not from local dev repo

---

## Production Deployment (5 Steps)

### Step 1: Build Frontend (Development)

```bash
cd /home/joerissen/ai/ai4artsed_development/public/ai4artsed-frontend
npm run build
```

### Step 2: Commit & Push to Develop

```bash
cd /home/joerissen/ai/ai4artsed_development
git add -A
git commit -m "feat: Description of changes"
git push origin develop
```

### Step 3: Merge & Push to Main

```bash
git checkout main
git merge develop
git push origin main
git checkout develop  # Switch back to develop for continued work
```

### Step 4: Pull in Production

```bash
cd /home/joerissen/ai/ai4artsed_production
git checkout main
git pull origin main
```

### Step 5: Build & Restart in Production

```bash
# Build frontend in production
cd /home/joerissen/ai/ai4artsed_production/public/ai4artsed-frontend
npm run build

# Restart production server (manual terminal window)
cd /home/joerissen/ai/ai4artsed_production
# Kill old server if needed: lsof -ti:17801 | xargs -r kill -9
./5_start_backend_prod.sh
```

**Verify:** https://lab.ai4artsed.org/

---

## Port Configuration

```
Service                Port    Environment
──────────────────────────────────────────
Backend Dev            17802   Development
Backend Prod           17801   Production
SwarmUI API            7801    Both (shared)
Ollama API            11434    Both (shared)
Frontend Dev (Vite)    5173    Development only
Cloudflare Tunnel      Auto    Production (→ 17801)
```

**How PORT override works:**

- `config.py`: Default PORT = 17802
- `server.py`: Reads `os.environ.get("PORT", config.PORT)`
- `5_start_backend_prod.sh`: Exports `PORT=17801` before starting

---

## Why /dist is Gitignored

The `/dist` folder contains **compiled build artifacts**:

- ❌ Don't commit (binary files, hashed names like `index-B9ygI19o.js`)
- ✅ Build locally in each environment
- ✅ Source code in git, builds are ephemeral

**Best Practice:** Each environment builds from source when deploying.

---

## Troubleshooting

### Merge Conflicts During Pull

```bash
cd /home/joerissen/ai/ai4artsed_production
git pull --rebase origin main

# If conflicts occur:
git status  # See conflicting files
# Resolve manually, then:
git add <resolved-files>
git rebase --continue
```

### TypeScript Build Errors

```bash
cd public/ai4artsed-frontend
npm run build

# Read error messages, fix issues:
# - Add null checks: value && doSomething(value)
# - Optional chaining: object?.property
# - Type assertions: value as Type
# - Fallbacks: value || defaultValue
```

### Frontend Changes Not Visible

- Clear browser cache (Ctrl+Shift+R)
- Verify build completed successfully
- Check browser console for errors
- Verify production server restarted

### Production Server Won't Start

```bash
# Check if port is already in use
lsof -ti:17801

# Kill if needed
lsof -ti:17801 | xargs -r kill -9

# Check logs
tail -f ~/ai/ai4artsed_production/logs/devserver.log
```

---

## Quick Reference

```bash
# COMPLETE DEPLOYMENT FLOW
cd ~/ai/ai4artsed_development/public/ai4artsed-frontend && npm run build
cd ~/ai/ai4artsed_development
git add -A && git commit -m "feat: Description"
git push origin develop
git checkout main && git merge develop && git push origin main && git checkout develop
cd ~/ai/ai4artsed_production && git pull origin main
cd public/ai4artsed-frontend && npm run build
cd ~/ai/ai4artsed_production && ./5_start_backend_prod.sh

# EMERGENCY ROLLBACK
cd ~/ai/ai4artsed_production
git log  # Find previous commit hash
git reset --hard <commit-hash>
cd public/ai4artsed-frontend && npm run build
./5_start_backend_prod.sh
```

---

## Related Documentation

- [ARCHITECTURE PART 01-20.md](./ARCHITECTURE%20PART%2001-20.md) - Full system architecture
- [DEVELOPMENT_LOG.md](../DEVELOPMENT_LOG.md) - Development history
- [DEVELOPMENT_DECISIONS.md](./DEVELOPMENT_DECISIONS.md) - Architectural decisions
- [CLAUDE.md](../.claude/CLAUDE.md) - Development guidelines

---

**Maintained By:** Development Team
**Last Deployment:** 2025-11-29 (Session 80 - Auto-Scroll Implementation)
