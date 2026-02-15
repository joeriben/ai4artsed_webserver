"""
HeartMuLa Backend - Direct inference for music generation

Session XXX: Music generation backend using HeartMuLa library (heartlib).
Standalone Python-based music generation using LLM + Audio Codec architecture.

Features:
- HeartMuLa 3B model for lyrics-to-music generation
- Multilingual support (EN, ZH, JA, KO, ES)
- On-demand lazy loading (first request loads model)
- VRAM management with unload support

Usage:
    backend = get_heartmula_backend()
    if await backend.is_available():
        audio_bytes = await backend.generate_music(
            lyrics="[Verse] Hello world...",
            tags="pop, upbeat, male vocal"
        )
"""

import logging
from typing import Optional, Dict, Any
from pathlib import Path
import asyncio

logger = logging.getLogger(__name__)


class HeartMuLaMusicGenerator:
    """
    Direct music generation using HeartMuLa (heartlib)

    Supports:
    - HeartMuLa 3B model for lyrics + tags → music
    - Multilingual lyrics (EN, ZH, JA, KO, ES)
    - Lazy model loading for VRAM efficiency
    - Configurable generation parameters
    """

    def __init__(self):
        """Initialize HeartMuLa backend"""
        from config import (
            HEARTMULA_MODEL_PATH,
            HEARTMULA_VERSION,
            HEARTMULA_LAZY_LOAD,
            HEARTMULA_DEVICE
        )

        self.model_path = HEARTMULA_MODEL_PATH
        self.version = HEARTMULA_VERSION
        self.lazy_load = HEARTMULA_LAZY_LOAD
        self.device = HEARTMULA_DEVICE

        # Pipeline (lazy-loaded)
        self._pipeline = None
        self._is_loaded = False
        self._vram_mb: float = 0  # Measured after loading
        self._last_used: float = 0
        self._in_use: int = 0

        # Register with VRAM coordinator for cross-backend eviction
        self._register_with_coordinator()

        logger.info(f"[HEARTMULA] Initialized: model_path={self.model_path}, version={self.version}, lazy_load={self.lazy_load}, device={self.device}")

    def _register_with_coordinator(self):
        """Register with VRAM coordinator for cross-backend eviction."""
        try:
            from services.vram_coordinator import get_vram_coordinator
            coordinator = get_vram_coordinator()
            coordinator.register_backend(self)
            logger.info("[HEARTMULA] Registered with VRAM coordinator")
        except Exception as e:
            logger.warning(f"[HEARTMULA] Failed to register with VRAM coordinator: {e}")

    # =========================================================================
    # VRAMBackend Protocol Implementation
    # =========================================================================

    def get_backend_id(self) -> str:
        """Unique identifier for this backend."""
        return "heartmula"

    def get_registered_models(self) -> list:
        """Return list of models with VRAM info for coordinator."""
        from services.vram_coordinator import EvictionPriority

        if not self._is_loaded:
            return []

        return [
            {
                "model_id": f"heartmula-{self.version}",
                "vram_mb": self._vram_mb,
                "priority": EvictionPriority.NORMAL,
                "last_used": self._last_used,
                "in_use": self._in_use,
            }
        ]

    def evict_model(self, model_id: str) -> bool:
        """Evict the HeartMuLa model (called by coordinator)."""
        import asyncio
        # Run async unload in sync context
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(self.unload_pipeline())
        finally:
            loop.close()

    async def is_available(self) -> bool:
        """
        Check if HeartMuLa backend is available

        Returns:
            True if heartlib is installed and model files exist
        """
        try:
            # Check if heartlib is installed
            from heartlib import HeartMuLaGenPipeline

            # Check if model files exist
            model_path = Path(self.model_path)
            if not model_path.exists():
                logger.warning(f"[HEARTMULA] Model path not found: {self.model_path}")
                return False

            # Check for HeartMuLa model directory
            heartmula_dir = model_path / f"HeartMuLa-oss-{self.version}"
            if not heartmula_dir.exists():
                # Try alternative naming
                heartmula_dir = model_path / "HeartMuLa-oss-3B"
                if not heartmula_dir.exists():
                    logger.warning(f"[HEARTMULA] HeartMuLa model not found in {model_path}")
                    return False

            # Check for HeartCodec
            codec_dir = model_path / "HeartCodec-oss"
            if not codec_dir.exists():
                logger.warning(f"[HEARTMULA] HeartCodec not found: {codec_dir}")
                return False

            logger.info("[HEARTMULA] Backend available")
            return True

        except ImportError as e:
            logger.error(f"[HEARTMULA] heartlib not installed: {e}")
            return False
        except Exception as e:
            logger.error(f"[HEARTMULA] Error checking availability: {e}")
            return False

    async def get_gpu_info(self) -> Dict[str, Any]:
        """Get GPU memory information"""
        try:
            import torch
            if torch.cuda.is_available():
                props = torch.cuda.get_device_properties(0)
                allocated = torch.cuda.memory_allocated(0) / 1024**3
                reserved = torch.cuda.memory_reserved(0) / 1024**3
                total = props.total_memory / 1024**3

                return {
                    "gpu_name": props.name,
                    "total_vram_gb": round(total, 2),
                    "allocated_gb": round(allocated, 2),
                    "reserved_gb": round(reserved, 2),
                    "free_gb": round(total - reserved, 2)
                }
            return {"available": False}
        except Exception as e:
            logger.error(f"[HEARTMULA] Error getting GPU info: {e}")
            return {"error": str(e)}

    async def _load_pipeline(self) -> bool:
        """
        Load HeartMuLa pipeline into memory

        Returns:
            True if loaded successfully
        """
        if self._is_loaded:
            logger.info("[HEARTMULA] Pipeline already loaded")
            return True

        try:
            import torch
            import time
            from heartlib import HeartMuLaGenPipeline

            # Request VRAM from coordinator (HeartMuLa ~7GB estimated)
            try:
                from services.vram_coordinator import get_vram_coordinator, EvictionPriority
                coordinator = get_vram_coordinator()
                coordinator.request_vram("heartmula", 7000, EvictionPriority.NORMAL)
            except Exception as e:
                logger.warning(f"[HEARTMULA] VRAM coordinator request failed: {e}")

            logger.info(f"[HEARTMULA] Loading pipeline from {self.model_path}...")

            # Measure VRAM before loading
            vram_before = torch.cuda.memory_allocated(0) if torch.cuda.is_available() else 0

            # Determine device configuration
            if self.device == "cuda" and torch.cuda.is_available():
                device_config = {
                    "mula": torch.device("cuda"),
                    "codec": torch.device("cuda")
                }
            else:
                device_config = {
                    "mula": torch.device("cpu"),
                    "codec": torch.device("cpu")
                }

            # Determine dtype configuration (bfloat16 for MuLa, float32 for codec)
            dtype_config = {
                "mula": torch.bfloat16 if self.device == "cuda" else torch.float32,
                "codec": torch.float32
            }

            # Load pipeline in thread to avoid blocking event loop
            def _load():
                pipe = HeartMuLaGenPipeline.from_pretrained(
                    self.model_path,
                    device=device_config,
                    dtype=dtype_config,
                    version=self.version,
                    lazy_load=self.lazy_load
                )
                return pipe

            self._pipeline = await asyncio.to_thread(_load)
            self._is_loaded = True
            self._last_used = time.time()

            # Measure VRAM after loading
            vram_after = torch.cuda.memory_allocated(0) if torch.cuda.is_available() else 0
            self._vram_mb = (vram_after - vram_before) / (1024 * 1024)

            logger.info(f"[HEARTMULA] Pipeline loaded (VRAM: {self._vram_mb:.0f}MB)")

            return True

        except Exception as e:
            logger.error(f"[HEARTMULA] Failed to load pipeline: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def unload_pipeline(self) -> bool:
        """
        Unload pipeline from memory to free VRAM

        Returns:
            True if unloaded successfully
        """
        if not self._is_loaded:
            logger.warning("[HEARTMULA] Pipeline not loaded")
            return False

        try:
            import torch

            del self._pipeline
            self._pipeline = None
            self._is_loaded = False
            self._vram_mb = 0
            self._in_use = 0

            # Force CUDA memory cleanup
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.synchronize()

            logger.info("[HEARTMULA] Pipeline unloaded")
            return True

        except Exception as e:
            logger.error(f"[HEARTMULA] Error unloading pipeline: {e}")
            return False

    async def generate_music(
        self,
        lyrics: str,
        tags: str,
        temperature: float = 1.0,
        topk: int = 70,
        cfg_scale: float = 3.0,
        max_audio_length_ms: int = 240000,
        seed: Optional[int] = None,
        output_format: str = "mp3"
    ) -> Optional[bytes]:
        """
        Generate music from lyrics and tags

        Args:
            lyrics: Song lyrics with structure markers [Verse], [Chorus], etc.
            tags: Comma-separated style tags (genre, mood, instruments)
            temperature: Creativity (0.1-2.0), default 1.0
            topk: Token sampling parameter, default 70
            cfg_scale: Classifier-free guidance scale, default 3.0
            max_audio_length_ms: Maximum audio length in ms, default 240000 (4 min)
            seed: Seed for reproducibility (None = random)
            output_format: Output format ('mp3' or 'wav'), default 'mp3'

        Returns:
            Audio bytes in specified format, or None on failure
        """
        try:
            import torch
            import tempfile
            import os
            import time

            # Ensure pipeline is loaded
            if not self._is_loaded:
                if not await self._load_pipeline():
                    logger.error("[HEARTMULA] Failed to load pipeline")
                    return None

            # Mark as in-use (prevents eviction during generation)
            self._in_use += 1
            self._last_used = time.time()

            try:
                # Handle seed
                if seed is not None:
                    import random
                    random.seed(seed)
                    torch.manual_seed(seed)
                    if torch.cuda.is_available():
                        torch.cuda.manual_seed(seed)

                # Prepare input
                input_data = {
                    "lyrics": lyrics,
                    "tags": tags
                }

                logger.info(f"[HEARTMULA] Generating music: lyrics={len(lyrics)} chars, tags={tags[:100]}...")
                logger.info(f"[HEARTMULA] Parameters: temp={temperature}, topk={topk}, cfg={cfg_scale}, max_ms={max_audio_length_ms}")

                # Create temporary file for output
                suffix = f".{output_format}"
                with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_file:
                    save_path = tmp_file.name

                try:
                    # Generate in thread to avoid blocking
                    def _generate():
                        with torch.no_grad():
                            logger.info(f"[HEARTMULA-DEBUG] Calling pipeline with:")
                            logger.info(f"  lyrics length: {len(lyrics)} chars")
                            logger.info(f"  tags: '{tags}'")
                            logger.info(f"  max_audio_length_ms: {max_audio_length_ms}")
                            logger.info(f"  topk: {topk}, temp: {temperature}, cfg: {cfg_scale}")

                            self._pipeline(
                                input_data,
                                max_audio_length_ms=max_audio_length_ms,
                                save_path=save_path,
                                topk=topk,
                                temperature=temperature,
                                cfg_scale=cfg_scale
                            )

                    await asyncio.to_thread(_generate)

                    # Read generated audio
                    if os.path.exists(save_path):
                        with open(save_path, 'rb') as f:
                            audio_bytes = f.read()

                        logger.info(f"[HEARTMULA] Generated audio: {len(audio_bytes)} bytes")
                        return audio_bytes
                    else:
                        logger.error(f"[HEARTMULA] Output file not created: {save_path}")
                        return None

                finally:
                    # Clean up temporary file
                    if os.path.exists(save_path):
                        os.unlink(save_path)

            finally:
                # Release in-use lock
                self._in_use -= 1

        except Exception as e:
            logger.error(f"[HEARTMULA] Generation error: {e}")
            import traceback
            traceback.print_exc()
            return None


# Singleton instance
_backend: Optional[HeartMuLaMusicGenerator] = None


def get_heartmula_backend() -> HeartMuLaMusicGenerator:
    """
    Get HeartMuLa backend singleton

    Returns:
        HeartMuLaMusicGenerator instance
    """
    global _backend
    if _backend is None:
        _backend = HeartMuLaMusicGenerator()
    return _backend


def reset_heartmula_backend():
    """Reset the singleton backend (for testing)"""
    global _backend
    _backend = None
