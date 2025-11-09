# AI4ArtsEd WebServer - DevServer

**Modern 3-Layer Pipeline Architecture for Pedagogical AI Systems**

This repository contains the **DevServer** implementation - a next-generation architecture for the AI4ArtsEd pedagogical platform.

## 🏗️ Repository Structure

This repository is now **DevServer-focused**. The Legacy Flask server has been moved to a separate repository for maintenance and stability.

- **This Repository (Main)**: DevServer development and new features
- **[Legacy Repository](https://github.com/joeriben/ai4artsed_webserver_legacy)**: Production Flask server (maintenance mode)

## 🎯 What is DevServer?

DevServer implements a **Three-Layer Pipeline System** designed specifically for pedagogical AI applications:

```
Layer 3: CONFIGS (Content)
  ↓ references
Layer 2: PIPELINES (Input-Type Orchestration)
  ↓ uses
Layer 1: CHUNKS (Primitive Operations)
```

### Key Features

- **Pedagogical Prompt Interception**: Transform user prompts through educational lenses (Bauhaus, Dada, Renaissance, etc.)
- **Backend-Agnostic**: Same pipeline works with ComfyUI, OpenRouter, Ollama
- **Input-Type Classification**: Pipelines categorized by what they consume, not output media
- **Safety & Compliance**: 4-Stage system with translation, safety checks, and content filtering
- **Template-Based**: JSON configs separate content from code

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Ollama (for local LLM) - `ollama serve`
- ComfyUI or SwarmUI (for media generation)

### Installation

```bash
# Navigate to devserver directory
cd devserver

# Install dependencies
pip install -r requirements.txt

# Start DevServer
python3 server.py
```

DevServer runs on `http://localhost:17801`

### Configuration

Edit `devserver/config.py` to configure:
- Model selection (mistral-nemo, llama-guard3, etc.)
- Backend ports (Ollama: 11434, ComfyUI: 7821)
- Execution modes (eco vs fast)

## 📁 Project Structure

```
ai4artsed_webserver/
├── devserver/                    # DevServer (NEW ARCHITECTURE)
│   ├── server.py                 # Entry point
│   ├── config.py                 # Configuration
│   ├── schemas/
│   │   ├── chunks/               # Layer 1: Primitives
│   │   ├── pipelines/            # Layer 2: Orchestration
│   │   ├── configs/              # Layer 3: Content
│   │   └── engine/               # Core execution logic
│   ├── my_app/                   # Server routes & services
│   ├── public_dev/               # Frontend
│   └── docs/                     # Comprehensive documentation
├── workflows_legacy/             # Historical ComfyUI workflows (reference only)
├── exports/                      # Generated media output
└── fyi_comfyui-customnodes_ai4artsed_comfyui/  # Legacy Custom Node

```

## 📚 Documentation

**Start here:** [`devserver/docs/README_FIRST.md`](devserver/docs/README_FIRST.md) (~55 min reading time)

Required reading before contributing - explains:
- Pedagogical concepts (Prompt Interception, Counter-Hegemonic Pedagogy)
- Three-Layer System architecture
- Why pipelines are input-type based
- Pre-Interception 4-Stage System

### Additional Documentation

- [`devserver/CLAUDE.md`](devserver/CLAUDE.md) - AI assistant guidance
- [`devserver/docs/ARCHITECTURE.md`](devserver/docs/ARCHITECTURE.md) - Technical reference
- [`devserver/docs/DEVELOPMENT_DECISIONS.md`](devserver/docs/DEVELOPMENT_DECISIONS.md) - Decision history
- [`devserver/docs/devserver_todos.md`](devserver/docs/devserver_todos.md) - Current priorities

## 🔄 Legacy Server

The production Flask server has been moved to: **[ai4artsed_webserver_legacy](https://github.com/joeriben/ai4artsed_webserver_legacy)**

Use the legacy server if you need:
- Stable production environment
- Original ComfyUI Custom Node (`ai4artsed_prompt_interception`)
- Legacy workflow compatibility

The legacy server is in **maintenance mode** - new features are developed in DevServer.

## 🛠️ Development Status

### ✅ Completed

- Frontend 100% migrated to Backend-abstracted architecture
- All 37 configs working with new API
- Media polling and serving via Backend
- Backend routing system (Ollama, ComfyUI, OpenRouter)
- Task-based model selection

### 🚧 In Progress

- Pre-Interception 4-Stage System (translation, safety checks)
- Safety filtering for youth/kids audiences
- Image+Text dual-input pipelines (inpainting, outpainting)

### 📋 Planned

- Cloud backend support (Replicate, Stability AI)
- Advanced flow controls (loops, quality checks)
- Multi-modal safety analysis

## 🏛️ Workflows Legacy

The `/workflows_legacy` directory contains **historical ComfyUI workflows** from the original Flask server. These are:

- ✅ Reference material for DevServer config creation
- ✅ Documentation of pedagogical implementations
- ✅ Source for `legacy_source` field in DevServer configs
- ❌ NOT for direct execution (requires Legacy Server + Custom Node)

See [`workflows_legacy/LEGACY_WORKFLOWS_README.md`](workflows_legacy/LEGACY_WORKFLOWS_README.md) for details.

## 🤝 Contributing

Before contributing:

1. ✅ Read [`devserver/docs/README_FIRST.md`](devserver/docs/README_FIRST.md) completely
2. ✅ Understand pedagogical concepts (Prompt Interception)
3. ✅ Review [`devserver/CLAUDE.md`](devserver/CLAUDE.md) for development guidelines
4. ✅ Check [`devserver/docs/devserver_todos.md`](devserver/docs/devserver_todos.md) for current priorities

**Important**: This is a pedagogical platform, not a typical API server. Technical "optimizations" that bypass educational features will be rejected.

## 📄 License

[Add your license information here]

## 🔗 Related Resources

- **Legacy Server**: https://github.com/joeriben/ai4artsed_webserver_legacy
- **ComfyUI**: https://github.com/comfyanonymous/ComfyUI
- **Ollama**: https://ollama.ai
- **Research**: [Add link to pedagogical research/papers]

---

**Last Updated**: 2025-10-30
**DevServer Version**: 2.0 (Schema Architecture v2)
**Status**: Active Development
