# AI4ArtsEd DevServer - Deployment Guide

> **Audience:** System administrators, developers setting up the system for the first time

This guide covers the complete deployment workflow from development to production.

---

## Table of Contents

1. [System Architecture Overview](#system-architecture-overview)
2. [Initial Setup (First Time)](#initial-setup-first-time)
3. [Development Workflow](#development-workflow)
4. [Production Deployment Workflow](#production-deployment-workflow)
5. [Port Configuration](#port-configuration)
6. [Cloudflare Tunnel Setup](#cloudflare-tunnel-setup)
7. [Troubleshooting](#troubleshooting)

---

## System Architecture Overview

### Two Parallel Environments

```
Development Environment                Production Environment
┌─────────────────────────┐          ┌─────────────────────────┐
│ ~/ai/ai4artsed_webserver│          │ /opt/ai4artsed-production│
│                         │          │                         │
│ - PORT: 17802          │          │ - PORT: 17801          │
│ - Git: develop branch  │          │ - Git: main branch     │
│ - Frontend: dev + dist │          │ - Frontend: dist only  │
│ - For testing          │          │ - Public-facing        │
└─────────────────────────┘          └─────────────────────────┘
         │                                      │
         └──────── Both use same ───────────────┘
                  exports/ storage
                  (via symlink)
```

### Key Differences

| Aspect | Development | Production |
|--------|-------------|------------|
| **Location** | `~/ai/ai4artsed_webserver/` | `/opt/ai4artsed-production/` |
| **Port** | 17802 | 17801 |
| **Branch** | `develop` | `main` |
| **Git Remote** | GitHub | Local dev repo |
| **Frontend** | Source + build | Build only |
| **Purpose** | Testing, development | Public access |

---

## Initial Setup (First Time)

### Prerequisites

```bash
# System requirements
- Ubuntu/Debian Linux
- Python 3.10+
- Node.js 18+ & npm
- Git
- SwarmUI (for image generation)
- Ollama (for LLM models)
```

### 1. Clone Development Repository

```bash
cd ~/ai/
git clone https://github.com/joeriben/ai4artsed_webserver.git
cd ai4artsed_webserver
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Install Frontend Dependencies

```bash
cd public/ai4artsed-frontend
npm install
```

### 4. Configure Development Environment

Edit `devserver/config.py`:

```python
# Development settings
PORT = 17802  # Development port
UI_MODE = "youth"  # or "kids", "expert"
DEFAULT_SAFETY_LEVEL = "youth"
DEFAULT_LANGUAGE = "de"
```

### 5. Build Frontend (First Time)

```bash
cd public/ai4artsed-frontend
npm run build
```

### 6. Set Up Production Environment

```bash
# Create production directory
sudo mkdir -p /opt/ai4artsed-production
sudo chown -R $USER:$USER /opt/ai4artsed-production

# Clone from local development repo
cd /opt/
git clone ~/ai/ai4artsed_webserver/.git ai4artsed-production
cd ai4artsed-production

# Switch to main branch
git checkout main

# Configure remote to point to local dev
git remote set-url origin ~/ai/ai4artsed_webserver/.git
```

### 7. Set Up Production Python Environment

```bash
cd /opt/ai4artsed-production
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 8. Configure Production Environment

Edit `/opt/ai4artsed-production/devserver/config.py`:

```python
# Production settings
PORT = 17801  # Production port (different from dev!)
UI_MODE = "youth"
DEFAULT_SAFETY_LEVEL = "youth"
DEFAULT_LANGUAGE = "de"
```

**CRITICAL:** Production must use `PORT = 17801` to avoid conflicts with development (17802).

### 9. Set Up Shared Storage

```bash
# Production uses dev's exports folder via symlink
cd /opt/ai4artsed-production

# Backup existing exports if any
if [ -d "exports" ]; then
    mv exports exports.backup_$(date +%Y%m%d_%H%M%S)
fi

# Create symlink to dev exports
ln -s ~/ai/ai4artsed_webserver/exports exports

# Verify symlink
ls -la exports
# Should show: exports -> /home/user/ai/ai4artsed_webserver/exports
```

### 10. Install Frontend in Production

```bash
cd /opt/ai4artsed-production/public/ai4artsed-frontend
npm install
npm run build
```

---

## Development Workflow

### Daily Development Cycle

```bash
# 1. Start in development
cd ~/ai/ai4artsed_webserver

# 2. Make changes to code

# 3. If Vue/frontend changes, rebuild
cd public/ai4artsed-frontend
npm run build

# 4. Test locally (use start scripts)
./3_start_backend_dev.sh  # Terminal 1
./4_start_frontend_dev.sh # Terminal 2 (for Vue hot reload)

# 5. When satisfied, commit
git add -A
git commit -m "feat: Description of changes"

# 6. Push to develop branch
git push origin develop
```

### Code Review & Testing

- Test all changes in development (PORT 17802)
- Verify frontend builds without TypeScript errors
- Check that pipeline execution works correctly
- Review documentation updates if architecture changed

---

## Production Deployment Workflow

### Standard Deployment (Current Session Process)

This is the workflow we just performed - use this as the standard procedure.

#### Step 1: Prepare Development

```bash
cd ~/ai/ai4artsed_webserver

# Ensure on develop branch
git checkout develop

# Verify clean state
git status

# Commit any outstanding changes
git add -A
git commit -m "Your commit message"
```

#### Step 2: Build Frontend

```bash
cd public/ai4artsed-frontend

# Build and verify TypeScript passes
npm run build

# Fix any TypeScript errors before proceeding!
```

#### Step 3: Push to Develop

```bash
cd ~/ai/ai4artsed_webserver
git push origin develop
```

#### Step 4: Merge to Main

```bash
# Push develop to main (without switching branches)
git push origin develop:main
```

#### Step 5: Update Dev's Local Main Branch

```bash
# Update dev's local main to match remote
git checkout main
git pull origin main
git checkout develop
```

#### Step 6: Deploy to Production

```bash
# Navigate to production
cd /opt/ai4artsed-production

# Pull latest from dev's main (production fetches from local dev repo)
git pull --rebase origin main

# The rebase preserves the local PORT=17801 config
```

#### Step 7: Verify Production Config

```bash
# Check that production still uses correct port
cd /opt/ai4artsed-production
grep "^PORT" devserver/config.py

# Expected output:
# PORT = 17801  # Production port
```

#### Step 8: Verify Deployment

```bash
cd /opt/ai4artsed-production

# Check git status
git status
# Expected: "Your branch is ahead of 'origin/main' by 1 commit"
# (This is the PORT config merge commit - this is normal)

# Check latest commits
git log --oneline -3

# Verify frontend dist exists
ls -la public/ai4artsed-frontend/dist/
```

#### Step 9: Restart Production Services

```bash
# Stop existing production backend
pkill -f "python.*devserver.*17801"

# Start production backend
cd /opt/ai4artsed-production
./5_start_backend_prod.sh

# Production frontend is served by backend from dist/
# No separate frontend process needed
```

### Quick Deployment Checklist

- [ ] Code changes committed in dev
- [ ] Frontend builds successfully (`npm run build`)
- [ ] No TypeScript errors
- [ ] Pushed to develop
- [ ] Merged develop to main (`git push origin develop:main`)
- [ ] Updated dev's local main branch
- [ ] Pulled in production (`git pull --rebase origin main`)
- [ ] Verified PORT = 17801 in production config
- [ ] Restarted production backend

---

## Port Configuration

### Port Allocation

```
Service                    Port    Environment
─────────────────────────────────────────────────
Backend Dev                17802   Development
Backend Prod               17801   Production
SwarmUI API                7801    Both (shared)
ComfyUI                    7821    Both (shared)
Ollama API                 11434   Both (shared)
Frontend Dev (Vite HMR)    5173    Development only
Cloudflare Tunnel          Auto    Production (maps to 17801)
```

### Why Two Backend Ports?

- Allows simultaneous development and production
- No conflicts when testing changes
- Safe to restart dev without affecting users
- Production remains stable during development

### Critical Config Files

**Development:** `~/ai/ai4artsed_webserver/devserver/config.py`
```python
PORT = 17802  # Development: 17802, Production: 17801
```

**Production:** `/opt/ai4artsed-production/devserver/config.py`
```python
PORT = 17801  # Production port
```

**Never change production PORT to 17802 - this will break the separation!**

---

## Cloudflare Tunnel Setup

### Initial Setup (One Time)

```bash
# Install cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# Authenticate with Cloudflare
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create ai4artsed-prod

# Note the tunnel UUID from output
```

### Configure Tunnel

Create `~/.cloudflared/config.yml`:

```yaml
tunnel: <your-tunnel-uuid>
credentials-file: /home/<user>/.cloudflared/<tunnel-uuid>.json

ingress:
  # Route to production backend
  - hostname: your-domain.com
    service: http://localhost:17801

  # Catch-all rule (required)
  - service: http_status:404
```

### Start Tunnel

```bash
# Use provided start script
./6_start_cloudflared.sh

# Or manually
cloudflared tunnel run ai4artsed-prod
```

### Verify Tunnel

```bash
# Check tunnel status
cloudflared tunnel info ai4artsed-prod

# Test public access
curl https://your-domain.com/health
```

---

## Start Scripts Reference

### Development Scripts

```bash
# Start development backend (PORT 17802)
./3_start_backend_dev.sh

# Start frontend dev server with hot reload (PORT 5173)
./4_start_frontend_dev.sh
```

### Production Scripts

```bash
# Start production backend (PORT 17801)
./5_start_backend_prod.sh

# Start Cloudflare tunnel (public access)
./6_start_cloudflared.sh
```

### Management Scripts

```bash
# Stop all services
./1_stop_all.sh

# Start SwarmUI (image generation)
./2_start_swarmui.sh
```

---

## Troubleshooting

### Issue: Production PORT Wrong After Update

**Symptom:** Production config shows `PORT = 17802` after pull

**Solution:**
```bash
cd /opt/ai4artsed-production

# Edit config
nano devserver/config.py

# Change line to:
PORT = 17801  # Production port

# Commit the fix
git add devserver/config.py
git commit -m "fix: Restore production PORT to 17801"

# Restart backend
pkill -f "python.*devserver.*17801"
./5_start_backend_prod.sh
```

### Issue: Merge Conflicts in Production

**Symptom:** `fatal: Need to specify how to reconcile divergent branches`

**Solution:**
```bash
cd /opt/ai4artsed-production
git pull --rebase origin main

# If conflicts occur, resolve manually:
# 1. Edit conflicted files
# 2. git add <resolved-files>
# 3. git rebase --continue
```

### Issue: Frontend Changes Not Visible

**Symptom:** Changes to Vue components don't appear in production

**Solution:**
```bash
# Rebuild frontend in development
cd ~/ai/ai4artsed_webserver/public/ai4artsed-frontend
npm run build

# Commit and deploy
cd ~/ai/ai4artsed_webserver
git add -A
git commit -m "fix: Rebuild frontend with latest changes"
git push origin develop
git push origin develop:main

# Update dev's local main
git checkout main && git pull origin main && git checkout develop

# Pull in production
cd /opt/ai4artsed-production
git pull --rebase origin main

# Restart production backend (serves new dist/)
pkill -f "python.*devserver.*17801"
./5_start_backend_prod.sh
```

### Issue: "Production branch ahead of origin/main"

**Symptom:** `git status` shows "Your branch is ahead of 'origin/main' by 1 commit"

**Status:** **This is normal!**

The production environment maintains a local commit for the PORT configuration. This commit rebases on top of every pull to preserve the production-specific config.

**No action needed** - this is the expected state.

### Issue: Missing Dependencies After Update

**Symptom:** Import errors or module not found

**Solution:**
```bash
# Update production dependencies
cd /opt/ai4artsed-production
source venv/bin/activate
pip install -r requirements.txt

# Restart backend
pkill -f "python.*devserver.*17801"
./5_start_backend_prod.sh
```

### Issue: TypeScript Errors Block Build

**Symptom:** `npm run build` fails with type errors

**Solution:**
```bash
cd ~/ai/ai4artsed_webserver/public/ai4artsed-frontend

# Read error messages carefully
npm run build

# Fix type errors in indicated files:
# - Add null checks: value && doSomething(value)
# - Add type assertions: value as string
# - Use optional chaining: object?.property
# - Provide fallbacks: value || defaultValue

# Rebuild after fixes
npm run build
```

---

## Architecture Notes

### Production Remote Setup

**Important:** Production does NOT fetch from GitHub directly!

```bash
# Production's remote points to local dev repo
cd /opt/ai4artsed-production
git remote -v

# Output:
# origin  /home/user/ai/ai4artsed_webserver/.git (fetch)
# origin  /home/user/ai/ai4artsed_webserver/.git (push)
```

**Why this architecture?**
- Deployment happens through local main branch
- Production isolated from direct GitHub access
- Allows testing in dev before production
- Faster deployment (local network)

### Storage Architecture

**Shared exports folder** (via symlink):

```
~/ai/ai4artsed_webserver/exports/
  └── json/  (pipeline run storage)

/opt/ai4artsed-production/exports → (symlink to above)
```

**Why shared storage?**
- Research data in accessible location (not hidden in /opt/)
- Both environments can analyze same runs
- No duplication of large result files
- Easy data management

---

## Security Considerations

### File Permissions

```bash
# Development: Normal user permissions
~/ai/ai4artsed_webserver/  - user:user

# Production: Normal user permissions (NOT root)
/opt/ai4artsed-production/ - user:user
```

**Never run backend as root!**

### Port Security

- Backend ports (17801, 17802) should NOT be exposed directly
- Use Cloudflare Tunnel for public access
- Tunnel handles SSL/TLS automatically
- Backend only listens on localhost (0.0.0.0)

### API Keys

Store sensitive keys in environment variables or separate config:

```bash
# Add to ~/.bashrc or systemd service
export OPENROUTER_API_KEY="your-key-here"
export ANTHROPIC_API_KEY="your-key-here"
```

Never commit API keys to git!

---

## Maintenance Tasks

### Regular Updates

```bash
# Weekly: Update dependencies
cd ~/ai/ai4artsed_webserver
source venv/bin/activate
pip install --upgrade -r requirements.txt

cd public/ai4artsed-frontend
npm update
```

### Logs & Monitoring

```bash
# Check backend logs
tail -f ~/ai/ai4artsed_webserver/logs/devserver.log

# Monitor production backend
journalctl -u ai4artsed-production -f

# Check storage usage
du -sh ~/ai/ai4artsed_webserver/exports/
```

### Backup Critical Data

```bash
# Backup exports (run results)
tar -czf exports_backup_$(date +%Y%m%d).tar.gz \
    ~/ai/ai4artsed_webserver/exports/

# Backup configurations
tar -czf config_backup_$(date +%Y%m%d).tar.gz \
    ~/ai/ai4artsed_webserver/devserver/config.py \
    /opt/ai4artsed-production/devserver/config.py
```

---

## Related Documentation

- [ARCHITECTURE PART 01-20.md](./ARCHITECTURE PART 01-20.md) - System architecture
- [DEVELOPMENT_LOG.md](./DEVELOPMENT_LOG.md) - Development history
- [SESSION_42_PRODUCTION_SETUP_COMPLETE.md](./sessions/SESSION_42_PRODUCTION_SETUP_COMPLETE.md) - Initial production setup
- [CLAUDE.md](../.claude/CLAUDE.md) - Development guidelines

---

## Quick Reference Card

```bash
# DEPLOYMENT FLOW
1. cd ~/ai/ai4artsed_webserver
2. npm run build (in public/ai4artsed-frontend)
3. git add -A && git commit -m "message"
4. git push origin develop
5. git push origin develop:main
6. git checkout main && git pull origin main && git checkout develop
7. cd /opt/ai4artsed-production
8. git pull --rebase origin main
9. grep "^PORT" devserver/config.py  # Verify 17801
10. ./5_start_backend_prod.sh

# ROLLBACK
cd /opt/ai4artsed-production
git reset --hard <previous-commit-hash>
./5_start_backend_prod.sh

# EMERGENCY STOP
./1_stop_all.sh
```

---

**Last Updated:** 2025-11-26
**Maintained By:** Development Team
**Contact:** See project README for support channels
