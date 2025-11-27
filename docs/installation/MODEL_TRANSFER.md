# AI4ArtsEd DevServer - Model Transfer Guide

Transfer AI models between servers over LAN for faster installation.

---

## Overview

**Why Transfer Instead of Download?**

| Method | Time (100Mbps) | Time (1 Gbps LAN) | Bandwidth Used |
|--------|----------------|-------------------|----------------|
| **Download from HuggingFace** | 45-60 min | N/A | 48GB internet |
| **Transfer over LAN** | 60-80 min | **6-8 min** 🚀 | 48GB local only |

**Benefits:**
- ⚡ Much faster on fast LAN (1 Gbps)
- 💾 No internet bandwidth wasted
- 🔄 Idempotent (can resume if interrupted)
- ✅ Automatic verification

---

## Prerequisites

### On Source Server (e.g., fedora):
- AI4ArtsEd DevServer installed with all models
- SSH server running
- rsync installed

### On Target Server (e.g., corsair):
- SSH access to source server
- rsync installed
- SwarmUI directory structure created

---

## Quick Start

### 1. Setup SSH Keys (One-Time)

**On target server:**
```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "ai4artsed-transfer"

# Copy to source server
ssh-copy-id ai4artsed@SOURCE_SERVER

# Test connection
ssh ai4artsed@SOURCE_SERVER "echo 'SSH OK'"
```

### 2. Run Transfer Script

```bash
cd /opt/ai4artsed/ai4artsed_webserver
./transfer_models.sh --source ai4artsed@SOURCE_SERVER
```

**That's it!** The script will transfer all models automatically.

---

## Advanced Usage

### Custom SwarmUI Path

```bash
./transfer_models.sh \
  --source ai4artsed@SOURCE_SERVER \
  --swarmui /custom/path/SwarmUI
```

### Dry Run (See What Will Be Transferred)

```bash
./transfer_models.sh \
  --source ai4artsed@SOURCE_SERVER \
  --dry-run
```

### Transfer Specific Models Only

The script transfers these models:
1. SD3.5 Large (`sd3.5_large.safetensors`) - 16GB
2. CLIP encoders (`clip_g.safetensors`, `t5xxl_enconly.safetensors`) - 6GB
3. T5 encoder for video (`t5xxl_fp16.safetensors`) - 11GB
4. LTX-Video (`ltxv-13b-0.9.7-distilled-fp8.safetensors`) - 15GB

**Total:** ~48GB

---

## What Gets Transferred

### Source Paths (on fedora):
```
/opt/ai4artsed/SwarmUI/
├── Models/Stable-Diffusion/OfficialStableDiffusion/
│   └── sd3.5_large.safetensors
└── dlbackend/ComfyUI/models/
    ├── clip/
    │   ├── clip_g.safetensors
    │   ├── t5xxl_enconly.safetensors
    │   └── t5xxl_fp16.safetensors
    └── checkpoints/
        └── ltxv-13b-0.9.7-distilled-fp8.safetensors
```

### Target Paths (on corsair):
Same structure as source.

### Symlink Created:
```bash
/opt/ai4artsed/SwarmUI/dlbackend/ComfyUI/models/checkpoints/OfficialStableDiffusion
→ ../../../Models/Stable-Diffusion/OfficialStableDiffusion
```

---

## Transfer Speed Examples

### 1 Gbps LAN:
```
SD3.5 Large (16GB):      ~2 min
CLIP Encoders (6GB):     ~1 min
T5 Video (11GB):         ~2 min
LTX-Video (15GB):        ~3 min
-----------------------------------
Total:                   ~8 min ⚡
```

### 100 Mbps LAN:
```
SD3.5 Large (16GB):      ~22 min
CLIP Encoders (6GB):     ~8 min
T5 Video (11GB):         ~15 min
LTX-Video (15GB):        ~20 min
-----------------------------------
Total:                   ~65 min
```

**Still faster than downloading from HuggingFace!**

---

## Troubleshooting

### SSH Connection Fails

**Error:**
```
SSH connection failed
```

**Solutions:**
```bash
# Check source server is reachable
ping SOURCE_SERVER

# Test SSH manually
ssh ai4artsed@SOURCE_SERVER

# Regenerate SSH keys if needed
ssh-keygen -t ed25519 -C "ai4artsed-transfer"
ssh-copy-id ai4artsed@SOURCE_SERVER
```

### rsync Not Found

**Error:**
```
rsync not found
```

**Install rsync:**
```bash
# Ubuntu/Debian
sudo apt install rsync

# Fedora
sudo dnf install rsync

# Arch
sudo pacman -S rsync
```

### Source Models Not Found

**Error:**
```
⚠ sd3.5_large.safetensors not found on source
```

**Check source paths:**
```bash
ssh ai4artsed@SOURCE_SERVER "ls -lh /opt/ai4artsed/SwarmUI/Models/Stable-Diffusion/OfficialStableDiffusion/"
```

**If models are in different location on source:**
```bash
./transfer_models.sh \
  --source ai4artsed@SOURCE_SERVER \
  --swarmui /path/to/SwarmUI/on/source
```

### Transfer Interrupted

**The script is idempotent - just re-run it:**
```bash
./transfer_models.sh --source ai4artsed@SOURCE_SERVER
```

rsync will resume where it left off.

### Slow Transfer Speed

**Check network speed:**
```bash
# Install iperf3
sudo apt install iperf3  # Ubuntu
sudo dnf install iperf3  # Fedora

# On source server
iperf3 -s

# On target server
iperf3 -c SOURCE_SERVER
```

**Expected speeds:**
- 1 Gbps Ethernet: ~900-950 Mbps
- 100 Mbps Ethernet: ~90-95 Mbps
- WiFi: Varies widely

---

## Ollama Models Transfer (Optional)

The `transfer_models.sh` script does NOT transfer Ollama models.

**Two options for Ollama:**

### Option 1: Download on Target (RECOMMENDED)
```bash
# On target server
ollama pull gpt-OSS:20b
ollama pull llama3.2-vision:latest
```

**Time:** 15-25 minutes
**Pros:** Clean, safe, recommended by Ollama
**Cons:** Uses internet bandwidth

### Option 2: Transfer from Source (ADVANCED)
```bash
# On target server
rsync -avz --progress \
  ai4artsed@SOURCE_SERVER:~/.ollama/models/ \
  ~/.ollama/models/

# Restart Ollama
sudo systemctl restart ollama

# Verify
ollama list
```

**Time:** 5-10 minutes (LAN)
**Pros:** Faster, no internet needed
**Cons:** More complex, requires Ollama service restart

**⚠️ CAUTION:** Ollama model format may change between versions. Option 1 is safer.

---

## Security Considerations

### SSH Key Permissions
```bash
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
chmod 700 ~/.ssh
```

### Restrict SSH Key Usage (Optional)

**On source server (`~/.ssh/authorized_keys`):**
```bash
from="TARGET_SERVER_IP",command="/bin/false" ssh-ed25519 AAAA...
```

This allows rsync but blocks interactive SSH.

### Use SSH Config

**On target server (`~/.ssh/config`):**
```
Host ai4artsed-source
    HostName SOURCE_SERVER
    User ai4artsed
    IdentityFile ~/.ssh/id_ed25519
    Compression yes
```

**Then use:**
```bash
./transfer_models.sh --source ai4artsed-source
```

---

## Comparison: Transfer vs Download

### Transfer (LAN)
✅ **Pros:**
- Much faster on 1 Gbps LAN
- No internet bandwidth used
- No HuggingFace rate limits
- Idempotent/resumable

❌ **Cons:**
- Requires source server
- Requires SSH setup
- Not available for remote servers

### Download (Internet)
✅ **Pros:**
- Works anywhere with internet
- No source server needed
- Official model sources

❌ **Cons:**
- Slower (45-60 min typical)
- Uses 48GB internet bandwidth
- Subject to HuggingFace rate limits

---

## Integration with Installation

**transfer_models.sh** is called in [QUICKSTART.md](QUICKSTART.md) Option A.

**Workflow:**
1. Install system dependencies
2. Install Ollama
3. Install SwarmUI
4. **→ Transfer models** (Step 4 of QUICKSTART.md)
5. Install AI4ArtsEd app
6. Configure and start

---

## Script Options Reference

```bash
./transfer_models.sh --help
```

**Output:**
```
Usage: ./transfer_models.sh --source USER@HOST [OPTIONS]

Required:
  --source USER@HOST    Source server (e.g., ai4artsed@fedora)

Options:
  --swarmui PATH        SwarmUI path (default: /opt/ai4artsed/SwarmUI)
  --dry-run             Preview without transferring
  --help                Show help

Examples:
  ./transfer_models.sh --source ai4artsed@fedora
  ./transfer_models.sh --source ai4artsed@fedora --swarmui /custom/path
  ./transfer_models.sh --source ai4artsed@fedora --dry-run
```

---

## Next Steps

After model transfer:
1. **Verify models:** Script automatically verifies after transfer
2. **Start SwarmUI:** `cd /opt/ai4artsed/SwarmUI && ./launch-linux.sh`
3. **Continue installation:** Follow [QUICKSTART.md](QUICKSTART.md) Step 5+

---

## Getting Help

- **Transfer script issues:** Check script output for detailed errors
- **SSH problems:** See SSH troubleshooting above
- **Network issues:** Use `iperf3` to test LAN speed
- **General installation:** See [INSTALLATION.md](INSTALLATION.md)

---

**Last Updated:** 2025-01-27
**Script Location:** `/opt/ai4artsed/ai4artsed_webserver/transfer_models.sh`
