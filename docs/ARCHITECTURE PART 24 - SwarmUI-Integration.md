# ARCHITECTURE PART 24 - SwarmUI Integration

**Created:** 2026-01-18
**Sessions:** 113, 120
**Status:** Production Ready

---

## Overview

SwarmUI serves as AI4ArtsEd's image generation backend, providing access to Stable Diffusion models via both a REST API and a ComfyUI backend. This document covers the integration architecture, auto-recovery system, and proxy routing.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         AI4ArtsEd DevServer                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐    ┌───────────────────┐    ┌────────────────────┐   │
│  │   Backend    │───▶│  SwarmUI Manager  │───▶│  Health Checks     │   │
│  │   Router     │    │   (Singleton)     │    │  (7801 + 7821)     │   │
│  └──────────────┘    └───────────────────┘    └────────────────────┘   │
│         │                     │                         │               │
│         │                     │ Auto-Start              │ Polling       │
│         ▼                     ▼                         ▼               │
│  ┌──────────────┐    ┌───────────────────┐    ┌────────────────────┐   │
│  │  Simple API  │    │  2_start_swarmui  │    │  SwarmUI Process   │   │
│  │  (Text2Img)  │    │      .sh          │    │  (Subprocess)      │   │
│  └──────────────┘    └───────────────────┘    └────────────────────┘   │
│         │                                                               │
│         ▼                                                               │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                        SwarmUI (Port 7801)                        │  │
│  │  ┌──────────────────┐              ┌───────────────────────────┐ │  │
│  │  │   REST API       │              │   ComfyUI Backend         │ │  │
│  │  │   /API/*         │              │   (Port 7821)             │ │  │
│  │  └──────────────────┘              └───────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## SwarmUI Manager Service

### Purpose
Automatic lifecycle management for SwarmUI - starts on demand, recovers from crashes.

### Location
`devserver/my_app/services/swarmui_manager.py`

### Design Pattern: Lazy Recovery

```python
class SwarmUIManager:
    """
    Singleton service for SwarmUI lifecycle management.

    Key Principle: Start only when needed (not at DevServer startup).
    """

    _instance = None
    _lock = asyncio.Lock()

    async def ensure_swarmui_available(self) -> bool:
        """
        Main entry point. Guarantees SwarmUI is running.
        Called before any image generation operation.
        """
        if await self.is_healthy():
            return True

        async with self._lock:
            # Double-check after acquiring lock
            if await self.is_healthy():
                return True

            return await self._start_and_wait()
```

### Health Checks

```python
async def is_healthy(self) -> bool:
    """
    Check both SwarmUI ports:
    - 7801: REST API (main interface)
    - 7821: ComfyUI backend (workflow execution)

    Both must be responsive for SwarmUI to be considered healthy.
    """
    try:
        # Check REST API
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{SWARMUI_HOST}:{SWARMUI_PORT}/API/GetServerInfoBasic",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                if resp.status != 200:
                    return False

        # Check ComfyUI backend
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{COMFYUI_HOST}:{COMFYUI_PORT}/system_stats",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                return resp.status == 200

    except Exception:
        return False
```

### Auto-Start Logic

```python
async def _start_swarmui(self) -> bool:
    """
    Start SwarmUI via the designated startup script.
    """
    script_path = Path(PROJECT_ROOT) / "2_start_swarmui.sh"

    # Start process without blocking
    self._process = subprocess.Popen(
        [str(script_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(script_path.parent)
    )

    logger.info(f"[SWARMUI-MANAGER] Started SwarmUI (PID: {self._process.pid})")
    return True

async def _wait_for_ready(self, timeout: int = 120) -> bool:
    """
    Poll health endpoints until SwarmUI is ready.
    """
    start = time.time()
    while time.time() - start < timeout:
        if await self.is_healthy():
            elapsed = time.time() - start
            logger.info(f"[SWARMUI-MANAGER] ✓ SwarmUI ready! (took {elapsed:.1f}s)")
            return True
        await asyncio.sleep(HEALTH_CHECK_INTERVAL)

    logger.error(f"[SWARMUI-MANAGER] Timeout waiting for SwarmUI ({timeout}s)")
    return False
```

---

## Integration Points

### Backend Router Integration

**Location:** `devserver/schemas/engine/backend_router.py`

The SwarmUI Manager is called before any operation that requires SwarmUI:

```python
class BackendRouter:
    def __init__(self):
        self.swarmui_manager = SwarmUIManager.get_instance()

    async def _process_image_chunk_simple(self, chunk, prompt, ...):
        """Simple Text2Image via SwarmUI API."""
        # Ensure SwarmUI is available
        await self.swarmui_manager.ensure_swarmui_available()

        # Proceed with generation
        response = await self._swarmui_text2image(prompt, ...)
        return response

    async def _process_workflow_chunk(self, chunk, workflow, ...):
        """ComfyUI workflow execution via SwarmUI."""
        await self.swarmui_manager.ensure_swarmui_available()

        # Submit workflow to ComfyUI backend
        response = await self._submit_comfyui_workflow(workflow)
        return response
```

### Legacy Workflow Service

**Location:** `devserver/my_app/services/legacy_workflow_service.py`

```python
class LegacyWorkflowService:
    async def execute_workflow(self, workflow_name: str, inputs: dict):
        # Ensure SwarmUI before legacy workflow execution
        await SwarmUIManager.get_instance().ensure_swarmui_available()

        # Execute legacy workflow
        return await self._run_legacy_workflow(workflow_name, inputs)
```

---

## Configuration

### config.py Settings

```python
# SwarmUI Configuration
SWARMUI_HOST = os.environ.get("SWARMUI_HOST", "http://127.0.0.1")
SWARMUI_PORT = int(os.environ.get("SWARMUI_PORT", "7801"))

# ComfyUI Backend (via SwarmUI)
COMFYUI_HOST = os.environ.get("COMFYUI_HOST", "http://127.0.0.1")
COMFYUI_PORT = int(os.environ.get("COMFYUI_PORT", "7821"))

# Auto-Recovery Settings
SWARMUI_AUTO_START = os.environ.get("SWARMUI_AUTO_START", "true").lower() == "true"
SWARMUI_STARTUP_TIMEOUT = int(os.environ.get("SWARMUI_STARTUP_TIMEOUT", "120"))
SWARMUI_HEALTH_CHECK_INTERVAL = float(os.environ.get("SWARMUI_HEALTH_CHECK_INTERVAL", "2.0"))
```

### Startup Script

**Location:** `2_start_swarmui.sh`

```bash
#!/bin/bash
cd /home/joerissen/ai/SwarmUI

# Start without opening browser tab
./launch-linux.sh --launch_mode none
```

The `--launch_mode none` flag prevents SwarmUI from opening a browser tab, keeping the AI4ArtsEd frontend in focus.

---

## Proxy Routing

### SwarmUI as ComfyUI Proxy

SwarmUI acts as a proxy to the underlying ComfyUI backend:

```
DevServer → SwarmUI (7801) → ComfyUI (7821)
                ↓
        /ComfyBackendDirect/*
```

### API Endpoints

| Endpoint | Description |
|----------|-------------|
| `/API/GenerateText2Image` | Simple text-to-image generation |
| `/API/GetServerInfoBasic` | Server status and capabilities |
| `/API/ListModels` | Available models |
| `/ComfyBackendDirect/*` | Direct ComfyUI API proxy |

### Workflow Submission

```python
async def _submit_comfyui_workflow(self, workflow: dict) -> dict:
    """
    Submit ComfyUI workflow via SwarmUI proxy.
    """
    url = f"{SWARMUI_HOST}:{SWARMUI_PORT}/ComfyBackendDirect/prompt"

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={"prompt": workflow}) as resp:
            result = await resp.json()
            return result
```

---

## Browser Tab Prevention

### Problem
SwarmUI's default behavior opens a browser tab on startup, which:
- Hides the AI4ArtsEd frontend
- Confuses users
- Disrupts the workflow

### Solution
Override via command-line argument:

```bash
./launch-linux.sh --launch_mode none
```

This overrides the `LaunchMode: web` setting in SwarmUI's `Settings.fds` file without modifying it, ensuring compatibility with any SwarmUI installation.

---

## Error Recovery

### Automatic Recovery Scenarios

| Scenario | Detection | Action |
|----------|-----------|--------|
| SwarmUI not running | Health check fails (7801 + 7821) | Start via script, wait for ready |
| SwarmUI crashed | Health check fails during operation | Restart and retry |
| ComfyUI unresponsive | 7821 health check fails | Full SwarmUI restart |

### Concurrency Safety

```python
async with self._lock:
    # Only one thread can start SwarmUI at a time
    if await self.is_healthy():
        return True  # Another thread started it while we waited
    return await self._start_and_wait()
```

### Recovery Log Output

```
[SWARMUI-TEXT2IMAGE] Ensuring SwarmUI is available...
[SWARMUI-MANAGER] SwarmUI not available, starting...
[SWARMUI-MANAGER] Starting SwarmUI via: /home/joerissen/ai/ai4artsed_development/2_start_swarmui.sh
[SWARMUI-MANAGER] SwarmUI process started (PID: 12345)
[SWARMUI-MANAGER] Waiting for SwarmUI (timeout: 120s)...
[SWARMUI-MANAGER] Checking health... (attempt 1)
[SWARMUI-MANAGER] Checking health... (attempt 5)
[SWARMUI-MANAGER] ✓ SwarmUI ready! (took 45.2s)
[SWARMUI] ✓ Generated 1 image(s)
```

---

## Custom ComfyUI Nodes

AI4ArtsEd includes custom ComfyUI nodes for specialized workflows:

**Location:** `/home/joerissen/ai/SwarmUI/ComfyUI/custom_nodes/ai4artsed_comfyui/`

| Node | Purpose |
|------|---------|
| `AI4ArtsEdPromptInterceptor` | Intercept and transform prompts |
| `AI4ArtsEdStyleInjector` | Apply LoRA styles dynamically |
| `AI4ArtsEdImageComposite` | Create composite images |
| `AI4ArtsEdSafetyFilter` | Content safety validation |

### Workflow Templates

**Location:** `/home/joerissen/ai/SwarmUI/ComfyUI/custom_nodes/ai4artsed_comfyui_workflows/`

Pre-built workflows for common operations:
- `text2image_sd35.json` - Standard image generation
- `partial_elimination.json` - Concept elimination workflow
- `split_and_combine.json` - Vector fusion workflow
- `surrealizer.json` - Surreal transformation workflow

---

## Related Documentation

- **Session 113:** Auto-recovery implementation
- **Session 120:** Full integration completion
- **ARCHITECTURE PART 08:** Backend routing details
- **ARCHITECTURE PART 22:** Legacy workflow architecture
- **ARCHITECTURE PART 23:** LoRA Training Studio (uses SwarmUI)

---

## Troubleshooting

### SwarmUI Won't Start

1. Check if another instance is running: `pgrep -f swarmui`
2. Verify script permissions: `chmod +x 2_start_swarmui.sh`
3. Check logs: `journalctl -u swarmui` or process output

### Health Check Always Fails

1. Verify ports: `netstat -tlnp | grep -E '7801|7821'`
2. Check firewall: `sudo ufw status`
3. Test manually: `curl http://127.0.0.1:7801/API/GetServerInfoBasic`

### Slow Startup

SwarmUI startup time varies (30-120 seconds) based on:
- Model loading (SD3.5 Large ~12GB)
- VRAM availability
- System resources

Increase timeout if needed:
```bash
export SWARMUI_STARTUP_TIMEOUT=180
```
