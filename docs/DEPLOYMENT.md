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

### Single Directory, Dual Runtime Approach

As of November 2025, the deployment architecture has been simplified to use a **single directory** with different runtime configurations:

```
Single Directory: ~/ai/ai4artsed_webserver/
├── devserver/              # Flask backend
├── public/ai4artsed-frontend/
│   ├── src/               # Vue source code
│   ├── dist/              # Built production files (gitignored)
│   └── node_modules/      # npm dependencies (gitignored)
├── venv/                  # Python virtual environment
└── [workflows, exports, etc.]

Runtime Modes:
┌─────────────────────────┐    ┌─────────────────────────┐
│  Development Mode       │    │  Production Mode        │
│  ./3_start_backend_dev.sh│    │  ./5_start_backend_prod.sh│
│  PORT: 17802           │    │  PORT: 17801 (override) │
│  Branch: develop       │    │  Branch: main           │
│  Local testing         │    │  Internet via Cloudflare│
└─────────────────────────┘    └─────────────────────────┘
```

### Key Architecture Principles

1. **One Codebase**: Single git repository at `~/ai/ai4artsed_webserver/`
2. **PORT Override**: `config.py` has default PORT=17802, production startup script exports PORT=17801
3. **Branch Separation**: Work on `develop`, deploy from `main`
4. **Build Artifacts Gitignored**: `/dist` folder must be built locally, not pulled from git
5. **Runtime Mode Selection**: Startup script determines dev vs prod behavior

### How PORT Override Works

**config.py (constant across all branches):**
```python
PORT = 17802  # Default port for development
```

**server.py (reads environment first):**
```python
port = int(os.environ.get("PORT", config.PORT))
# Result: ENV var overrides config.py if set
```

**Startup scripts:**
```bash
# Development: ./3_start_backend_dev.sh
python3 server.py  # Uses PORT from config.py → 17802

# Production: ./5_start_backend_prod.sh
export PORT=17801  # Override the default
python3 server.py  # Uses PORT from environment → 17801
```

**Benefit**: No PORT merge conflicts when merging develop → main!

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

### 6. Why /dist is Gitignored

The `/dist` folder contains **built artifacts** (compiled JavaScript, CSS, etc.) that are generated from source code. These files:

1. **Change on every build** (hashed filenames like `index-B9ygI19o.js`)
2. **Are derived from source** (not source themselves)
3. **Would bloat git history** if committed (binary files, frequent changes)

**Best Practice**: Build locally when deploying, don't commit build artifacts.

```bash
# Before deploying to production, always rebuild:
cd ~/ai/ai4artsed_webserver/public/ai4artsed-frontend
npm run build
```

### 7. No Separate Production Directory

**Important**: As of November 2025, there is **no separate `/opt/ai4artsed-production/` directory**.

The previous dual-directory setup was simplified to a single-directory approach:
- ✅ Single codebase at `~/ai/ai4artsed_webserver/`
- ✅ PORT determined by startup script (dev: 17802, prod: 17801)
- ✅ Branch selection determines features (develop vs main)
- ✅ No PORT merge conflicts
- ✅ Simpler deployment workflow

If you're migrating from the old dual-directory setup, see the migration notes at the end of this document.

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

### Simplified 7-Step Process (November 2025)

This is the new streamlined workflow using the single-directory approach:

#### Step 1: Commit Changes to Develop

```bash
cd ~/ai/ai4artsed_webserver

# Ensure on develop branch
git checkout develop

# Commit any outstanding changes
git add -A
git commit -m "feat: Your feature description"
```

#### Step 2: Test Locally with Dev Backend

```bash
# Start development backend
./3_start_backend_dev.sh

# Test on http://localhost:17802/
# Verify functionality works as expected
```

#### Step 3: Push to GitHub

```bash
# Push develop branch
git push origin develop
```

#### Step 4: Merge Develop → Main on GitHub

```bash
# Option A: Push directly (if you have permissions)
git push origin develop:main

# Option B: Create pull request on GitHub (recommended)
# - Go to https://github.com/joeriben/ai4artsed_webserver
# - Create PR from develop to main
# - Review and merge
```

#### Step 5: Pull Main Locally

```bash
cd ~/ai/ai4artsed_webserver

# Update local main branch
git checkout main
git pull origin main

# Switch back to develop for continued work
git checkout develop
```

#### Step 6: Rebuild Frontend

```bash
cd ~/ai/ai4artsed_webserver/public/ai4artsed-frontend

# Rebuild production assets
npm run build

# Fix any TypeScript errors before proceeding!
```

#### Step 7: Restart Production Backend

```bash
cd ~/ai/ai4artsed_webserver

# Stop old backend (if running)
lsof -ti:17801 | xargs -r kill -9

# Start production backend (uses PORT=17801 override)
./5_start_backend_prod.sh

# Verify: https://lab.ai4artsed.org/
```

### Quick Deployment Checklist

- [ ] Code committed to develop branch
- [ ] Tested locally on dev backend (17802)
- [ ] Pushed to GitHub
- [ ] Merged develop → main
- [ ] Pulled main locally
- [ ] Frontend rebuilt (`npm run build` - no errors)
- [ ] Production backend restarted (17801)
- [ ] Verified at https://lab.ai4artsed.org/

### Key Benefits Over Old Workflow

**Before (10 steps with /opt/):**
- Two separate git clones to manage
- PORT merge conflicts every deployment
- Confusing local git origins
- "Branch ahead" confusion
- Risk of config.py conflicts

**After (7 steps, single directory):**
- ✅ One git repository
- ✅ No PORT merge conflicts
- ✅ Standard GitHub workflow
- ✅ Simpler to understand
- ✅ Faster deployment

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
