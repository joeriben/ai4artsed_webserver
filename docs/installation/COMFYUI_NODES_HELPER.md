# ComfyUI Custom Nodes Installation Helper

Automated installer for AI4ArtsEd ComfyUI custom nodes.

## Quick Start

```bash
cd /home/joerissen/ai/ai4artsed_webserver
./install_comfyui_nodes.sh
```

Or with custom SwarmUI path:

```bash
SWARMUI_PATH=/custom/path/SwarmUI ./install_comfyui_nodes.sh
```

## What This Script Does

Automates installation of 3 essential ComfyUI custom nodes:

1. **ComfyUI-LTXVideo** - Video generation capability
2. **ai4artsed_comfyui** - Pedagogical workflow nodes
3. **comfyui-sound-lab** - Audio generation capability

**Automation features:**
- Auto-detects SwarmUI path or accepts custom path via `SWARMUI_PATH` env variable
- Activates SwarmUI's virtual environment automatically
- Clones or updates each node repository
- Installs Python dependencies from requirements.txt
- Gracefully handles missing files and optional dependencies
- Provides colored output for clear status feedback

## Prerequisites

Before running:
1. SwarmUI must be installed (see [INSTALLATION.md](INSTALLATION.md#swarmui-installation))
2. ComfyUI integrated with SwarmUI (automatic during SwarmUI setup)
3. SwarmUI virtual environment created (automatic during SwarmUI setup)

## Usage

### Default Installation

Uses SwarmUI path `/opt/ai4artsed/SwarmUI`:

```bash
./install_comfyui_nodes.sh
```

### Custom SwarmUI Path

Override default path with environment variable:

```bash
export SWARMUI_PATH=/my/custom/path/SwarmUI
./install_comfyui_nodes.sh
```

Or inline:

```bash
SWARMUI_PATH=/my/custom/path/SwarmUI ./install_comfyui_nodes.sh
```

## Output

**Success:**
```
=== AI4ArtsEd - ComfyUI Custom Nodes Installer ===

SwarmUI Path: /opt/ai4artsed/SwarmUI

[✓] ComfyUI custom_nodes directory found

[Activating] SwarmUI virtual environment...
[✓] Virtual environment activated

[1/3] Installing ComfyUI-LTXVideo (Video Generation)...
[✓] ComfyUI-LTXVideo installed

[2/3] Installing ai4artsed_comfyui (Pedagogical Nodes)...
[✓] ai4artsed_comfyui installed

[3/3] Installing comfyui-sound-lab (Audio Generation)...
[✓] comfyui-sound-lab installed

[✓] All custom nodes installed!

Installed nodes:
ComfyUI-LTXVideo
ai4artsed_comfyui
comfyui-sound-lab

Next steps:
  1. Restart SwarmUI
  2. Check ComfyUI can load the nodes
```

## When to Use

### Use this script for:
- Initial custom nodes installation
- Updating existing nodes to latest versions
- Re-installing if nodes become corrupted

### Alternative: Manual Installation

For more control, see [INSTALLATION.md - ComfyUI Custom Nodes](INSTALLATION.md#comfyui-custom-nodes) for step-by-step manual instructions.

## Behavior Details

### Node Paths

Nodes are installed to:
```
$SWARMUI_PATH/dlbackend/ComfyUI/custom_nodes/
├── ComfyUI-LTXVideo/
├── ai4artsed_comfyui/
└── comfyui-sound-lab/
```

### Update Logic

If a node already exists:
- Runs `git pull` to fetch latest version
- Reinstalls dependencies

Otherwise:
- Clones fresh repository
- Installs dependencies

### Dependency Installation

For each node:
1. Checks for `requirements.txt`
2. Installs via `pip install -r requirements.txt`
3. Continues even if installation fails (some dependencies are optional, e.g., flash-attention for audio)

## Troubleshooting

### SwarmUI path not found

**Error:**
```
[✗] SwarmUI not found at: /opt/ai4artsed/SwarmUI
```

**Solution:**
```bash
# Find SwarmUI installation
find /opt -name SwarmUI -type d 2>/dev/null

# Install with correct path
SWARMUI_PATH=/path/to/SwarmUI ./install_comfyui_nodes.sh
```

### ComfyUI directory not found

**Error:**
```
[✗] ComfyUI custom_nodes directory not found
```

**Causes:**
- SwarmUI path is incorrect
- SwarmUI not fully installed
- ComfyUI not integrated with SwarmUI

**Solution:**
```bash
# Verify structure
ls -la $SWARMUI_PATH/dlbackend/ComfyUI/custom_nodes/

# Reinstall SwarmUI if needed
cd $SWARMUI_PATH
./install-linux.sh
```

### Dependency installation fails

**Error:**
```
pip: command not found
```

**Cause:** SwarmUI venv not properly activated

**Solution:**
```bash
# Check venv exists
ls -la $SWARMUI_PATH/venv/bin/activate

# Manually activate and retry
source $SWARMUI_PATH/venv/bin/activate
pip install -r requirements.txt
deactivate
```

### Some dependencies fail (warnings)

**Error:**
```
[⚠] Some dependencies failed (flash-attention is optional)
```

**Expected:** Some packages like flash-attention are optional. Script continues successfully.

## Integration with Installation Flow

This script is called automatically by:
1. [INSTALLATION.md - Step 5](INSTALLATION.md#comfyui-custom-nodes) (recommended approach)
2. Or run manually after SwarmUI is ready

**Or run manually:**

```bash
# After SwarmUI installation
cd /opt/ai4artsed/ai4artsed_webserver
./install_comfyui_nodes.sh

# Continue with next installation steps
# See INSTALLATION.md for full workflow
```

## Next Steps After Installation

1. **Restart SwarmUI:**
   ```bash
   sudo systemctl restart ai4artsed-swarmui
   # OR manually restart if running in terminal
   ```

2. **Verify nodes loaded:**
   - Open SwarmUI at http://localhost:7801
   - Check node browser for new nodes

3. **Continue with AI model downloads:**
   - See [INSTALLATION.md - AI Model Downloads](INSTALLATION.md#ai-model-downloads)

## Script Location

- **Repository:** `/home/joerissen/ai/ai4artsed_webserver/`
- **Executable:** `/home/joerissen/ai/ai4artsed_webserver/install_comfyui_nodes.sh`
- **Requires:** Executable permissions (check with `ls -l install_comfyui_nodes.sh`)

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SWARMUI_PATH` | `/opt/ai4artsed/SwarmUI` | Path to SwarmUI installation |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success - All nodes installed |
| 1 | Error - SwarmUI path invalid or ComfyUI directory not found |

---

**For detailed installation instructions, see:** [INSTALLATION.md](INSTALLATION.md)
