# Production/Development Separation Architecture

**Created:** 2025-11-14
**Status:** Implementation in progress
**Version:** v2.0.0-alpha.3

---

## Overview

This document describes the separation of Production and Development environments for AI4ArtsEd DevServer to enable:

1. **Stable production** for workshops with multiple users
2. **Unrestricted development** without disrupting active workshops
3. **Clear deployment workflow** with version control

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              Cloudflare Tunnel                      │
│          lab.ai4artsed.org → Port 17801            │
└────────────────────┬────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────┐
│  PRODUCTION (systemd service, stable)               │
│  /opt/ai4artsed-production/                        │
│    ├── devserver/                                   │
│    │   ├── server.py                               │
│    │   ├── my_app/                                 │
│    │   └── schemas/                                │
│    ├── public/ai4artsed-frontend/dist/            │
│    ├── venv/ (production Python env)               │
│    └── .git/ (main branch)                         │
│                                                     │
│  Port: 17801 (public via Cloudflare)              │
│  Status: Runs permanently, auto-restart            │
│  Managed by: systemd (ai4artsed-production)       │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  DEVELOPMENT (manual, experimental)                 │
│  /home/joerissen/ai/ai4artsed_webserver/          │
│    ├── devserver/                                   │
│    ├── public/ai4artsed-frontend/                 │
│    │   ├── src/ (source code)                     │
│    │   └── dist/ (local builds)                   │
│    ├── venv/ (development Python env)              │
│    └── .git/ (develop branch)                      │
│                                                     │
│  Port: 17802 (local only or dev.ai4artsed.org)    │
│  Status: Started manually when developing          │
│  Managed by: ~/start_backend_dev.sh               │
└─────────────────────────────────────────────────────┘
```

---

## Directory Structure

### Production (`/opt/ai4artsed-production/`)

```
/opt/ai4artsed-production/
├── devserver/
│   ├── server.py
│   ├── config.py
│   ├── my_app/
│   │   ├── __init__.py
│   │   └── routes/
│   ├── schemas/
│   │   ├── configs/
│   │   ├── chunks/
│   │   └── pipelines/
│   └── requirements.txt
├── public/
│   └── ai4artsed-frontend/
│       └── dist/              # Production build only
├── venv/                      # Isolated Python environment
├── .git/
└── logs/
    ├── backend.log
    └── systemd/ (via journalctl)
```

### Development (`~/ai/ai4artsed_webserver/`)

```
/home/joerissen/ai/ai4artsed_webserver/
├── devserver/
│   ├── server.py
│   ├── config.py
│   └── ... (same structure as production)
├── public/
│   └── ai4artsed-frontend/
│       ├── src/               # Vue source code
│       ├── dist/              # Local builds for testing
│       └── node_modules/      # Dev dependencies
├── venv/                      # Dev Python environment
├── .git/
└── docs/                      # Documentation (not in prod)
```

---

## Port Configuration

| Environment | Backend Port | Frontend Port | Access |
|-------------|--------------|---------------|--------|
| Production  | 17801        | - (served by backend) | https://lab.ai4artsed.org |
| Development | 17802        | 5173 (Vite dev server) | http://localhost:5173 |

---

## Git Workflow

### Branches

```
main        → Production-ready code (deployed to /opt/)
develop     → Active development (in ~/ai/ai4artsed_webserver/)
feature/*   → Feature branches (merge to develop)
```

### Development Cycle

```bash
# 1. Work on feature (in development directory)
cd ~/ai/ai4artsed_webserver
git checkout develop
git checkout -b feature/new-interception-mode

# ... make changes ...

git add .
git commit -m "feat: Add new interception mode"
git push origin feature/new-interception-mode

# 2. Merge to develop
git checkout develop
git merge feature/new-interception-mode

# 3. Test in development environment
~/start_backend_dev.sh         # Terminal 1
~/start_frontend_dev.sh         # Terminal 2
# ... test thoroughly ...

# 4. When ready for production deployment
git checkout main
git merge develop
git push origin main

# 5. Deploy to production
~/deploy_to_production.sh
```

---

## Services Management

### Production (systemd service)

**Service file:** `/etc/systemd/system/ai4artsed-production.service`

```ini
[Unit]
Description=AI4ArtsEd Production Backend
After=network.target

[Service]
Type=simple
User=joerissen
WorkingDirectory=/opt/ai4artsed-production/devserver
Environment="PATH=/opt/ai4artsed-production/venv/bin"
ExecStart=/opt/ai4artsed-production/venv/bin/python3 server.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Commands:**
```bash
# Start
sudo systemctl start ai4artsed-production

# Stop
sudo systemctl stop ai4artsed-production

# Restart
sudo systemctl restart ai4artsed-production

# Status
sudo systemctl status ai4artsed-production

# Logs
journalctl -u ai4artsed-production -f

# Enable auto-start on boot
sudo systemctl enable ai4artsed-production
```

### Development (manual)

**Scripts in `~/.`:**

```bash
# Backend (port 17802)
~/start_backend_dev.sh

# Frontend (Vite dev server, port 5173)
~/start_frontend_dev.sh

# Stop all development processes
~/stop_dev.sh
```

---

## Deployment Process

### Automated Deployment Script

**Script:** `~/deploy_to_production.sh`

```bash
#!/bin/bash
# Deploys latest main branch to production

set -e

echo "=== AI4ArtsEd Production Deployment ==="
echo ""

# 1. Pull latest code
echo "[1/6] Pulling latest code from main branch..."
cd /opt/ai4artsed-production
git fetch origin
git checkout main
git pull origin main

# 2. Update Python dependencies
echo "[2/6] Updating Python dependencies..."
source venv/bin/activate
pip install -r devserver/requirements.txt

# 3. Rebuild frontend
echo "[3/6] Rebuilding frontend..."
cd public/ai4artsed-frontend
npm install
npm run build

# 4. Clear Python cache
echo "[4/6] Clearing Python cache..."
cd /opt/ai4artsed-production/devserver
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# 5. Restart service
echo "[5/6] Restarting production service..."
sudo systemctl restart ai4artsed-production

# 6. Verify deployment
echo "[6/6] Verifying deployment..."
sleep 3
if systemctl is-active --quiet ai4artsed-production; then
    echo ""
    echo "✅ Deployment successful!"
    echo ""
    echo "Production status:"
    sudo systemctl status ai4artsed-production --no-pager -l
    echo ""
    echo "Access at: https://lab.ai4artsed.org"
else
    echo ""
    echo "❌ Deployment failed! Service is not running."
    echo ""
    echo "Check logs:"
    echo "  journalctl -u ai4artsed-production -n 50"
    exit 1
fi
```

### Manual Deployment Steps

If automated script fails:

```bash
# 1. SSH into server (if remote)
ssh user@server

# 2. Navigate to production directory
cd /opt/ai4artsed-production

# 3. Pull latest code
git fetch origin
git checkout main
git pull origin main

# 4. Update dependencies
source venv/bin/activate
pip install -r devserver/requirements.txt

# 5. Rebuild frontend
cd public/ai4artsed-frontend
npm install
npm run build

# 6. Restart service
sudo systemctl restart ai4artsed-production

# 7. Check status
sudo systemctl status ai4artsed-production
journalctl -u ai4artsed-production -f
```

---

## Configuration Differences

### Production (`/opt/ai4artsed-production/devserver/config.py`)

```python
# Server configuration
HOST = "0.0.0.0"
PORT = 17801

# Frontend build path
PUBLIC_DIR = Path(__file__).parent.parent / "public" / "ai4artsed-frontend" / "dist"

# Production settings
DEBUG = False
LOG_LEVEL = "INFO"
```

### Development (`~/ai/ai4artsed_webserver/devserver/config.py`)

```python
# Server configuration
HOST = "0.0.0.0"
PORT = 17802  # Different port!

# Frontend build path (same)
PUBLIC_DIR = Path(__file__).parent.parent / "public" / "ai4artsed-frontend" / "dist"

# Development settings
DEBUG = True
LOG_LEVEL = "DEBUG"
```

---

## Testing Procedures

### Before Deployment to Production

**In development environment:**

1. ✅ Run all tests: `pytest devserver/tests/`
2. ✅ Test all API endpoints manually
3. ✅ Test pipeline execution (Stage 1-4)
4. ✅ Test frontend functionality (Phase 1, Phase 2)
5. ✅ Check for Python errors: `python3 -m py_compile devserver/**/*.py`
6. ✅ Build frontend successfully: `npm run build`
7. ✅ Test production build locally (port 17802)

**Checklist:**
```bash
# Backend tests
cd ~/ai/ai4artsed_webserver/devserver
pytest tests/

# Frontend build
cd ~/ai/ai4artsed_webserver/public/ai4artsed-frontend
npm run build

# Test production mode locally
~/start_backend_dev.sh
# Open http://localhost:17802 in browser
# Test all features
```

### After Deployment to Production

1. ✅ Check service status: `sudo systemctl status ai4artsed-production`
2. ✅ Monitor logs for errors: `journalctl -u ai4artsed-production -f`
3. ✅ Test public access: https://lab.ai4artsed.org
4. ✅ Test API endpoints via Cloudflare
5. ✅ Run smoke tests (basic pipeline execution)
6. ✅ Verify static assets load (check browser console)

---

## Rollback Procedure

If deployment breaks production:

```bash
# 1. Check current commit
cd /opt/ai4artsed-production
git log -1

# 2. Find last working commit
git log --oneline -10

# 3. Rollback to specific commit
git checkout <commit-hash>

# 4. Rebuild if needed
cd public/ai4artsed-frontend
npm run build

# 5. Restart service
sudo systemctl restart ai4artsed-production

# 6. Verify
sudo systemctl status ai4artsed-production
```

**Alternative: Revert last commit**
```bash
cd /opt/ai4artsed-production
git revert HEAD
git push origin main
~/deploy_to_production.sh
```

---

## Monitoring and Maintenance

### Production Health Checks

**Automated monitoring (future):**
- Service status check every 5 minutes
- Ping https://lab.ai4artsed.org/api/health
- Alert if service down > 2 minutes

**Manual checks:**
```bash
# Service status
sudo systemctl status ai4artsed-production

# Resource usage
top -p $(pgrep -f "python3.*server.py")

# Disk space
df -h /opt/ai4artsed-production

# Recent logs
journalctl -u ai4artsed-production --since "1 hour ago"

# Error count
journalctl -u ai4artsed-production --since "today" | grep -c ERROR
```

### Log Rotation

**System handles via journald:**
```bash
# Configure in /etc/systemd/journald.conf
SystemMaxUse=1G
SystemKeepFree=2G
MaxRetentionSec=1month
```

### Backup Strategy

**What to backup:**
- Configuration files: `/opt/ai4artsed-production/devserver/config.py`
- Schemas: `/opt/ai4artsed-production/devserver/schemas/`
- Database (if added later)

**Backup script (future):**
```bash
#!/bin/bash
BACKUP_DIR="/backup/ai4artsed/$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"
cp -r /opt/ai4artsed-production/devserver/schemas "$BACKUP_DIR/"
tar -czf "$BACKUP_DIR/configs.tar.gz" /opt/ai4artsed-production/devserver/config.py
```

---

## Security Considerations

### File Permissions

```bash
# Production directory ownership
sudo chown -R joerissen:joerissen /opt/ai4artsed-production

# Restrict write access to production
chmod 755 /opt/ai4artsed-production
chmod 755 /opt/ai4artsed-production/devserver

# Config files
chmod 644 /opt/ai4artsed-production/devserver/config.py
```

### Network Security

**Firewall rules:**
```bash
# Production port (via Cloudflare Tunnel only)
# Port 17801 should NOT be exposed directly
sudo ufw deny 17801/tcp

# Development port (local only)
# Port 17802 should NOT be accessible externally
sudo ufw deny 17802/tcp
```

**Cloudflare Access:**
- Enable authentication for lab.ai4artsed.org
- Restrict by geography (Deutschland only)
- Rate limiting enabled

---

## Troubleshooting

### Production Service Won't Start

**Check logs:**
```bash
journalctl -u ai4artsed-production -n 50
```

**Common issues:**

1. **Port already in use:**
   ```bash
   lsof -i:17801
   # Kill conflicting process
   ```

2. **Missing dependencies:**
   ```bash
   cd /opt/ai4artsed-production
   source venv/bin/activate
   pip install -r devserver/requirements.txt
   ```

3. **Permission errors:**
   ```bash
   sudo chown -R joerissen:joerissen /opt/ai4artsed-production
   ```

4. **Python import errors:**
   ```bash
   # Clear Python cache
   find /opt/ai4artsed-production -type d -name "__pycache__" -exec rm -rf {} +
   ```

### Development Environment Issues

**Port 17802 already in use:**
```bash
lsof -ti:17802 | xargs -r kill -9
```

**Can't switch Git branches:**
```bash
# Stash changes
git stash
git checkout develop
git stash pop
```

---

## Migration Checklist

**Initial setup (one-time):**

- [ ] Create production directory `/opt/ai4artsed-production/`
- [ ] Copy code from development to production
- [ ] Setup separate Python venv for production
- [ ] Install dependencies in production venv
- [ ] Build frontend in production directory
- [ ] Create systemd service file
- [ ] Enable and start systemd service
- [ ] Update Cloudflare Tunnel config (if needed)
- [ ] Configure development to use port 17802
- [ ] Create deployment scripts (`~/deploy_to_production.sh`)
- [ ] Setup Git branches (main/develop)
- [ ] Test both environments
- [ ] Update all documentation

**Ongoing workflow:**

- [ ] Always develop in `~/ai/ai4artsed_webserver/` (develop branch)
- [ ] Test changes in development environment first
- [ ] Merge to main branch when ready
- [ ] Deploy to production with `~/deploy_to_production.sh`
- [ ] Verify production deployment
- [ ] Monitor logs after deployment

---

## Future Enhancements

### Phase 2 (Beta)
- [ ] Docker containerization (optional alternative installation)
- [ ] Automated testing in CI/CD pipeline
- [ ] Blue-green deployment strategy
- [ ] Database replication (if database added)

### Phase 3 (Production)
- [ ] Load balancing for multiple instances
- [ ] Horizontal scaling
- [ ] Advanced monitoring (Prometheus + Grafana)
- [ ] Automated backups

---

## References

- Main documentation: `docs/README.md`
- Cloudflare operations: `docs/CLOUDFLARE_MAINTENANCE.md`
- Development log: `docs/DEVELOPMENT_LOG.md`
- Architecture overview: `docs/ARCHITECTURE PART 01-20`

---

## Version History

### v2.0.0-alpha.3 (2025-11-14)
- Initial production/development separation
- Systemd service implementation
- Git workflow established
- Deployment automation added

---

**Status:** Ready for implementation
**Next Steps:** Execute migration checklist
