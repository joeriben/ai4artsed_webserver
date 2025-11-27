# PC2 (corsair) Installation - Schritt-für-Schritt

**Ziel:** AI4ArtsEd auf corsair (PC2) installieren mit Model-Transfer von fedora

**Geschätzte Zeit:** 55-65 Minuten

**Systeme:**
- **Quelle (Models):** fedora (per SSH erreichbar)
- **Ziel (Installation):** corsair (PC2)

---

## Vorbereitung (5 min)

### 1. SSH-Verbindung fedora → corsair einrichten

**Auf fedora ausführen:**

```bash
# SSH-Key für Transfer generieren (falls noch nicht vorhanden)
ssh-keygen -t ed25519 -C "ai4artsed-model-transfer"

# Key zu corsair kopieren
ssh-copy-id ai4artsed@corsair

# Testen
ssh ai4artsed@corsair "echo 'SSH works from fedora to corsair'"
```

**Expected:** "SSH works from fedora to corsair"

---

### 2. API Keys besorgen

**Jetzt holen, während Installation läuft:**

1. **OpenRouter (REQUIRED):** https://openrouter.ai/keys
   - Sign up / Log in
   - Create new key
   - Kopieren: `sk-or-v1-...`

2. **OpenAI (Optional):** https://platform.openai.com/api-keys
   - Nur wenn GPT-Image-1 genutzt werden soll

---

## Installation auf corsair (PC2)

### Phase 1: System Setup (20 min)

**Alle folgenden Commands auf corsair (PC2) ausführen!**

#### Schritt 1: Prerequisites Check (1 min)

```bash
# Check System Requirements
nvidia-smi  # GPU vorhanden?
df -h /     # >350GB frei?
python3 --version  # 3.11+?
node --version     # v20+?
```

**Falls Probleme → siehe SYSTEM_REQUIREMENTS.md**

---

#### Schritt 2: System Dependencies (5 min)

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install -y \
  git curl wget rsync \
  python3 python3-pip python3-venv \
  build-essential \
  libcairo2-dev libpango1.0-dev libjpeg-dev libgif-dev libgirepository1.0-dev \
  nodejs npm

# Fedora (falls corsair auch Fedora ist)
sudo dnf install -y \
  git curl wget rsync \
  python3 python3-pip \
  gcc make \
  cairo-devel pango-devel libjpeg-devel giflib-devel gobject-introspection-devel \
  nodejs npm
```

---

#### Schritt 3: Ollama + Models (20 min)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
sudo systemctl enable ollama
sudo systemctl start ollama

# Download Models (~29GB, läuft im Hintergrund weiter)
echo "Downloading gpt-OSS:20b (21GB)..."
ollama pull gpt-OSS:20b &

echo "Downloading llama3.2-vision (8GB)..."
ollama pull llama3.2-vision:latest &

# Status checken (in neuem Terminal)
ollama list
```

**💡 Tipp:** Diese Downloads laufen parallel zu nächsten Schritten!

---

### Phase 2: SwarmUI Installation (10 min)

#### Schritt 4: SwarmUI Setup

```bash
# Create installation directory
cd /opt
sudo mkdir -p ai4artsed && sudo chown $USER:$USER ai4artsed
cd ai4artsed

# Clone SwarmUI
git clone https://github.com/mcmonkeyprojects/SwarmUI.git SwarmUI
cd SwarmUI

# Run installer (~5-10 min)
./install-linux.sh

# Test start (dann Ctrl+C nach "Server started")
./launch-linux.sh
# Wait for "Server started", then press Ctrl+C
```

---

### Phase 3: Model Transfer (10-15 min)

#### Schritt 5: AI4ArtsEd Repository klonen

```bash
cd /opt/ai4artsed
git clone https://github.com/joerissenbenjamin/ai4artsed_webserver.git
cd ai4artsed_webserver
```

---

#### Schritt 6: Models von fedora transferieren

**🚀 Das ist der Time-Saver! 48GB über LAN statt Internet.**

```bash
# Check prerequisites
./check_prerequisites.sh

# Transfer models from fedora
./transfer_models.sh --source ai4artsed@fedora
```

**Was passiert:**
```
[1/4] Transferring SD3.5 Large (16GB)...
[2/4] Transferring CLIP encoders (6GB)...
[3/4] Transferring T5 encoder for video (11GB)...
[4/4] Transferring LTX-Video model (15GB)...
[Verify] Checking transferred models...
✓ All models transferred!
```

**Zeit:**
- 1 Gbps LAN: 6-8 Minuten ⚡
- 100 Mbps LAN: 60-80 Minuten

**💡 Während Transfer läuft:** API Keys bereithalten (siehe Vorbereitung)

---

### Phase 4: AI4ArtsEd Setup (15 min)

#### Schritt 7: App Setup

```bash
cd /opt/ai4artsed/ai4artsed_webserver

# Setup Python venv + Frontend build (~8 min)
./setup.sh

# Install ComfyUI custom nodes (~3 min)
./install_comfyui_nodes.sh
```

---

#### Schritt 8: Konfiguration (5 min)

**Edit config.py:**
```bash
nano devserver/config.py
```

**Änderungen:**
```python
# Line 298-299: Paths (sollte schon korrekt sein)
SWARMUI_BASE_PATH = "/opt/ai4artsed/SwarmUI"
COMFYUI_BASE_PATH = "/opt/ai4artsed/SwarmUI/dlbackend/ComfyUI"

# Line 67: Port (für Production)
PORT = 17801

# Line 66: Host
HOST = "0.0.0.0"  # Für Netzwerk-Zugriff

# Lines 35, 61: UI und Safety
UI_MODE = "youth"
DEFAULT_SAFETY_LEVEL = "youth"
```

**Speichern:** Ctrl+X, Y, Enter

---

**API Keys File erstellen:**
```bash
nano devserver/api_keys.json
```

**Inhalt (mit Ihren Keys von Vorbereitung):**
```json
{
  "openrouter": "sk-or-v1-YOUR_OPENROUTER_KEY_HERE",
  "openai": "sk-proj-YOUR_OPENAI_KEY_HERE",
  "openai_org_id": "org-YOUR_ORG_HERE"
}
```

**Speichern und sichern:**
```bash
chmod 600 devserver/api_keys.json
```

---

### Phase 5: Services Starten (5 min)

#### Schritt 9: Start Services

**Terminal 1 - SwarmUI:**
```bash
cd /opt/ai4artsed/SwarmUI
./launch-linux.sh
```

**Warten bis:** "Server started on http://localhost:7801"

---

**Terminal 2 - Backend:**
```bash
cd /opt/ai4artsed/ai4artsed_webserver/devserver
source ../venv/bin/activate
python3 server.py
```

**Warten bis:** "Waitress serving on http://0.0.0.0:17801"

---

#### Schritt 10: Verification

**In Terminal 3:**
```bash
# Check Ollama
ollama list
# Should show: gpt-OSS:20b, llama3.2-vision:latest

# Check SwarmUI
curl http://localhost:7801/API/GetNewSession

# Check Backend
curl http://localhost:17801/

# Open in Browser
xdg-open http://localhost:17801
```

**Expected:**
- Browser öffnet AI4ArtsEd Interface
- Sprachauswahl: Deutsch / English

---

## ✅ Installation Complete!

**Gesamtzeit:** ~55-65 Minuten

**Test:**
1. Sprache wählen (Deutsch)
2. Prompt eingeben: "ein roter Apfel"
3. "Transformieren" klicken
4. "Bild" wählen
5. Warten (~30 Sekunden)
6. ✅ Bild generiert!

---

## Production Deployment (Optional)

### Systemd Services einrichten

**SwarmUI Service:**
```bash
sudo nano /etc/systemd/system/ai4artsed-swarmui.service
```

**Inhalt:**
```ini
[Unit]
Description=AI4ArtsEd SwarmUI
After=network.target ollama.service

[Service]
Type=simple
User=ai4artsed
WorkingDirectory=/opt/ai4artsed/SwarmUI
Environment="PATH=/opt/ai4artsed/SwarmUI/venv/bin:/usr/bin:/bin"
ExecStart=/opt/ai4artsed/SwarmUI/launch-linux.sh
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

---

**Backend Service:**
```bash
sudo nano /etc/systemd/system/ai4artsed-backend.service
```

**Inhalt:**
```ini
[Unit]
Description=AI4ArtsEd Backend
After=network.target ai4artsed-swarmui.service
Requires=ai4artsed-swarmui.service

[Service]
Type=simple
User=ai4artsed
WorkingDirectory=/opt/ai4artsed/ai4artsed_webserver/devserver
Environment="PATH=/opt/ai4artsed/ai4artsed_webserver/venv/bin:/usr/bin:/bin"
ExecStart=/opt/ai4artsed/ai4artsed_webserver/venv/bin/python3 server.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

---

**Enable & Start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable ai4artsed-swarmui ai4artsed-backend
sudo systemctl start ai4artsed-swarmui ai4artsed-backend

# Check status
sudo systemctl status ai4artsed-backend
sudo systemctl status ai4artsed-swarmui
```

---

## Troubleshooting

### SSH von fedora zu corsair funktioniert nicht

**Problem:** `ssh ai4artsed@corsair` schlägt fehl

**Lösung:**
```bash
# Auf fedora
ssh-keygen -t ed25519 -C "ai4artsed-transfer"
ssh-copy-id ai4artsed@corsair

# Test
ssh ai4artsed@corsair "hostname"
# Should print: corsair
```

---

### Model Transfer schlägt fehl

**Problem:** `transfer_models.sh` findet Models nicht auf fedora

**Check auf fedora:**
```bash
ssh ai4artsed@fedora "ls -lh /opt/ai4artsed/SwarmUI/Models/Stable-Diffusion/OfficialStableDiffusion/"
```

**Falls Models woanders:**
```bash
./transfer_models.sh --source ai4artsed@fedora --swarmui /custom/path
```

---

### Port 17801 bereits belegt

**Problem:** Backend startet nicht, Port in use

**Lösung:**
```bash
sudo lsof -i :17801
# Kill process
sudo kill -9 $(sudo lsof -t -i:17801)

# Oder Port in config.py ändern
nano devserver/config.py  # Change PORT = 17802
```

---

### Ollama Models fehlen

**Problem:** `ollama list` zeigt Models nicht

**Lösung:**
```bash
# Nochmal pullen
ollama pull gpt-OSS:20b
ollama pull llama3.2-vision:latest

# Status checken
ollama list
```

---

### GPU nicht erkannt

**Problem:** `nvidia-smi` schlägt fehl

**Lösung:**
```bash
# Check drivers installed
nvidia-smi

# Install if missing (Ubuntu)
sudo ubuntu-drivers autoinstall
sudo reboot

# Check after reboot
nvidia-smi
```

---

## Cheat Sheet - Komplette Command Sequence

**Copy-Paste Installation (alle Commands auf corsair):**

```bash
# 1. System Deps
sudo apt update && sudo apt install -y git curl wget rsync python3 python3-pip python3-venv build-essential libcairo2-dev libpango1.0-dev libjpeg-dev libgif-dev libgirepository1.0-dev nodejs npm

# 2. Ollama
curl -fsSL https://ollama.com/install.sh | sh && sudo systemctl enable ollama && sudo systemctl start ollama
ollama pull gpt-OSS:20b &
ollama pull llama3.2-vision:latest &

# 3. SwarmUI
cd /opt && sudo mkdir -p ai4artsed && sudo chown $USER:$USER ai4artsed && cd ai4artsed
git clone https://github.com/mcmonkeyprojects/SwarmUI.git SwarmUI
cd SwarmUI && ./install-linux.sh

# 4. Repository
cd /opt/ai4artsed
git clone https://github.com/joerissenbenjamin/ai4artsed_webserver.git
cd ai4artsed_webserver

# 5. Transfer Models (auf fedora: SSH-Keys setup!)
./transfer_models.sh --source ai4artsed@fedora

# 6. App Setup
./setup.sh
./install_comfyui_nodes.sh

# 7. Configure
nano devserver/config.py         # Update paths, port
nano devserver/api_keys.json     # Add API keys
chmod 600 devserver/api_keys.json

# 8. Start
# Terminal 1: cd /opt/ai4artsed/SwarmUI && ./launch-linux.sh
# Terminal 2: cd /opt/ai4artsed/ai4artsed_webserver/devserver && source ../venv/bin/activate && python3 server.py
```

---

## Timing Breakdown

| Phase | Schritte | Zeit |
|-------|----------|------|
| **Vorbereitung** | SSH, API Keys | 5 min |
| **System Setup** | Dependencies, Ollama | 20 min |
| **SwarmUI** | Clone, Install | 10 min |
| **Model Transfer** | 48GB über LAN | **10-15 min** ⚡ |
| **App Setup** | Setup, Config | 15 min |
| **Start & Verify** | Services, Test | 5 min |
| **TOTAL** | | **55-65 min** |

---

## Next Steps

- **Update System:** `./update.sh`
- **Monitor Logs:** `sudo journalctl -u ai4artsed-backend -f`
- **GPU Usage:** `watch -n 1 nvidia-smi`

---

**Installation auf PC2 (corsair) abgeschlossen!** 🎉

---

**Erstellt:** 2025-01-27
**Für:** corsair (PC2) mit Model-Transfer von fedora
**Wartung:** Prof. Dr. Benjamin Jörissen
