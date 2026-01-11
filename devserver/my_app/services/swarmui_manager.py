"""
SwarmUI Manager Service - Automatic lifecycle management

This service handles SwarmUI availability detection and automatic startup:
- Detects when SwarmUI is not running (health checks on ports 7801 + 7821)
- Automatically starts SwarmUI using 2_start_swarmui.sh when needed
- Waits for ready state with timeout
- Prevents race conditions with asyncio.Lock

Architecture: Lazy recovery (on-demand startup)
Pattern: Singleton with double-check locking
"""
import logging
import asyncio
import subprocess
import time
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class SwarmUIManager:
    """Manages SwarmUI lifecycle: startup, health checks, auto-recovery

    Design Pattern: Singleton with lazy initialization
    Thread Safety: asyncio.Lock for concurrent startup attempts
    """

    def __init__(self):
        """Initialize SwarmUI Manager with configuration from config.py"""
        # Import config values
        try:
            from config import (
                SWARMUI_API_PORT,
                COMFYUI_PORT,
                SWARMUI_AUTO_START,
                SWARMUI_STARTUP_TIMEOUT,
                SWARMUI_HEALTH_CHECK_INTERVAL,
                BASE_DIR
            )

            # Ports
            self.swarmui_port = int(SWARMUI_API_PORT)  # REST API (default: 7801)
            self.comfyui_port = int(COMFYUI_PORT)  # ComfyUI backend (default: 7821)

            # Configuration
            self._auto_start_enabled = SWARMUI_AUTO_START
            self._startup_timeout = SWARMUI_STARTUP_TIMEOUT
            self._health_check_interval = SWARMUI_HEALTH_CHECK_INTERVAL
            self._base_dir = BASE_DIR

            # Concurrency control
            self._startup_lock = asyncio.Lock()
            self._is_starting = False

            logger.info(
                f"[SWARMUI-MANAGER] Initialized (SwarmUI: {self.swarmui_port}, "
                f"ComfyUI: {self.comfyui_port}, Auto-start: {self._auto_start_enabled})"
            )

        except ImportError as e:
            logger.error(f"[SWARMUI-MANAGER] Failed to import config: {e}")
            # Fallback defaults
            self.swarmui_port = 7801
            self.comfyui_port = 7821
            self._auto_start_enabled = True
            self._startup_timeout = 120
            self._health_check_interval = 2.0
            self._base_dir = Path(__file__).parent.parent.parent.parent
            self._startup_lock = asyncio.Lock()
            self._is_starting = False

    async def ensure_swarmui_available(self) -> bool:
        """Ensure SwarmUI is running, start if needed

        This is the main entry point for all services needing SwarmUI.
        Call this before any SwarmUI/ComfyUI operations.

        Returns:
            True if SwarmUI is available (was running or successfully started)
            False if auto-start disabled or startup failed
        """
        # 1. Quick health check (no lock needed)
        if await self.is_healthy():
            logger.debug("[SWARMUI-MANAGER] Already healthy")
            return True

        # 2. Check if auto-start is enabled
        if not self._auto_start_enabled:
            logger.warning("[SWARMUI-MANAGER] Auto-start disabled, SwarmUI not available")
            return False

        # 3. Acquire lock (prevent multiple threads starting)
        async with self._startup_lock:
            # Double-check after acquiring lock (another thread might have started)
            if await self.is_healthy():
                logger.info("[SWARMUI-MANAGER] Another thread started SwarmUI")
                return True

            # 4. Start SwarmUI
            logger.warning("[SWARMUI-MANAGER] SwarmUI not available, starting...")
            return await self._start_swarmui()

    async def is_healthy(self) -> bool:
        """Check if SwarmUI is fully operational

        Checks BOTH ports:
        - Port 7801 (SwarmUI REST API)
        - Port 7821 (ComfyUI backend)

        Returns True only if both are responsive.
        """
        # Import clients to reuse their health_check methods
        try:
            from my_app.services.swarmui_client import SwarmUIClient
            from my_app.services.comfyui_client import ComfyUIClient

            swarmui_client = SwarmUIClient(f"http://127.0.0.1:{self.swarmui_port}")
            comfyui_client = ComfyUIClient(f"http://127.0.0.1:{self.comfyui_port}")

            # Both must be healthy
            swarmui_ok = await swarmui_client.health_check()
            comfyui_ok = await comfyui_client.health_check()

            is_healthy = swarmui_ok and comfyui_ok

            if not is_healthy:
                logger.debug(
                    f"[SWARMUI-MANAGER] Health check: "
                    f"SwarmUI={swarmui_ok}, ComfyUI={comfyui_ok}"
                )

            return is_healthy

        except Exception as e:
            logger.debug(f"[SWARMUI-MANAGER] Health check failed: {e}")
            return False

    async def _start_swarmui(self) -> bool:
        """Execute startup script and wait for ready state

        Returns:
            True if startup successful, False otherwise
        """
        try:
            self._is_starting = True

            # 1. Resolve script path
            script_path = self._get_startup_script_path()
            if not script_path.exists():
                logger.error(f"[SWARMUI-MANAGER] Startup script not found: {script_path}")
                logger.error("[SWARMUI-MANAGER] Please start SwarmUI manually")
                return False

            logger.info(f"[SWARMUI-MANAGER] Starting SwarmUI via: {script_path}")

            # 2. Execute script in background (non-blocking)
            # Note: The startup script passes --launch_mode none to SwarmUI
            # to prevent it from opening a browser tab automatically.
            # This works on any SwarmUI installation via command-line override.
            process = subprocess.Popen(
                [str(script_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=script_path.parent,  # Run from repo root
                start_new_session=True  # Detach from parent process group
            )

            logger.info(f"[SWARMUI-MANAGER] SwarmUI process started (PID: {process.pid})")

            # 3. Wait for SwarmUI to be ready (polling)
            return await self._wait_for_ready()

        except Exception as e:
            logger.error(f"[SWARMUI-MANAGER] Startup failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            self._is_starting = False

    async def _wait_for_ready(self) -> bool:
        """Poll health endpoints until ready or timeout

        Returns:
            True if ready within timeout, False otherwise
        """
        start_time = time.time()
        logger.info(
            f"[SWARMUI-MANAGER] Waiting for SwarmUI "
            f"(timeout: {self._startup_timeout}s)..."
        )

        while True:
            elapsed = time.time() - start_time

            # Check timeout
            if elapsed > self._startup_timeout:
                logger.error(
                    f"[SWARMUI-MANAGER] Startup timeout after {self._startup_timeout}s"
                )
                logger.error("[SWARMUI-MANAGER] Check SwarmUI logs for startup issues")
                return False

            # Check health
            if await self.is_healthy():
                logger.info(f"[SWARMUI-MANAGER] ✓ SwarmUI ready! (took {elapsed:.1f}s)")
                return True

            # Wait before next check
            logger.debug(
                f"[SWARMUI-MANAGER] Still waiting... ({elapsed:.1f}s elapsed)"
            )
            await asyncio.sleep(self._health_check_interval)

    def _get_startup_script_path(self) -> Path:
        """Resolve path to 2_start_swarmui.sh

        Uses BASE_DIR from config.py to find script at repo root.
        """
        script_path = self._base_dir / "2_start_swarmui.sh"
        return script_path

    def is_starting(self) -> bool:
        """Check if SwarmUI is currently in startup process

        Returns:
            True if startup in progress, False otherwise
        """
        return self._is_starting


# Singleton pattern
_swarmui_manager: Optional[SwarmUIManager] = None


def get_swarmui_manager() -> SwarmUIManager:
    """Get singleton SwarmUI Manager instance

    Returns:
        SwarmUIManager singleton instance
    """
    global _swarmui_manager
    if _swarmui_manager is None:
        _swarmui_manager = SwarmUIManager()
    return _swarmui_manager
