"""
MMAudio Backend — CVPR 2025 Video/Image-to-Audio Generation

Dedicated crossmodal model trained on both visual and audio modalities.
157M parameters, flow matching (NOT diffusion), 25 Euler steps.
Generates up to 8s of 44.1kHz audio in ~1.2s.

Features:
- Image-to-audio generation (duplicates image as pseudo-video frames)
- Text-to-audio generation
- Combined image + text conditioning
- Lazy loading with VRAM coordinator integration
- ~6GB VRAM when loaded

Requirements:
    git clone https://github.com/hkchengrex/MMAudio
    pip install -e ./MMAudio

Usage:
    backend = get_mmaudio_backend()
    if await backend.is_available():
        audio_bytes = await backend.generate_from_image(image_bytes, prompt="fire crackling")
"""

import logging
import time
from typing import Optional, Dict, Any, List
import asyncio

logger = logging.getLogger(__name__)


class MMAudioBackend:
    """
    MMAudio generation backend.

    Implements VRAMBackend protocol for VRAM coordinator integration.
    Lazy-loads the model on first use.
    """

    def __init__(self):
        from config import MMAUDIO_MODEL, MMAUDIO_REPO

        self.model_variant = MMAUDIO_MODEL  # e.g. "large_44k_v2"
        self.repo_path = MMAUDIO_REPO

        self._model = None
        self._feature_utils = None
        self._net = None
        self._is_loaded = False
        self._vram_mb: float = 0
        self._last_used: float = 0
        self._in_use: int = 0

        self._register_with_coordinator()
        logger.info(f"[MMAUDIO] Initialized: model={self.model_variant}, repo={self.repo_path}")

    def _register_with_coordinator(self):
        try:
            from services.vram_coordinator import get_vram_coordinator
            coordinator = get_vram_coordinator()
            coordinator.register_backend(self)
            logger.info("[MMAUDIO] Registered with VRAM coordinator")
        except Exception as e:
            logger.warning(f"[MMAUDIO] Failed to register: {e}")

    # =========================================================================
    # VRAMBackend Protocol
    # =========================================================================

    def get_backend_id(self) -> str:
        return "mmaudio"

    def get_registered_models(self) -> List[Dict[str, Any]]:
        from services.vram_coordinator import EvictionPriority

        if not self._is_loaded:
            return []

        return [
            {
                "model_id": f"mmaudio_{self.model_variant}",
                "vram_mb": self._vram_mb,
                "priority": EvictionPriority.NORMAL,
                "last_used": self._last_used,
                "in_use": self._in_use,
            }
        ]

    def evict_model(self, model_id: str) -> bool:
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(self.unload())
        finally:
            loop.close()

    # =========================================================================
    # Lifecycle
    # =========================================================================

    async def is_available(self) -> bool:
        """Check if MMAudio can be loaded."""
        try:
            import sys
            if self.repo_path not in sys.path:
                sys.path.insert(0, self.repo_path)
            import mmaudio  # noqa: F401
            return True
        except ImportError:
            logger.warning("[MMAUDIO] mmaudio package not importable")
            return False

    async def _load(self) -> bool:
        """Load MMAudio model and feature extractors."""
        if self._is_loaded:
            return True

        try:
            import torch
            import sys
            if self.repo_path not in sys.path:
                sys.path.insert(0, self.repo_path)

            try:
                from services.vram_coordinator import get_vram_coordinator, EvictionPriority
                coordinator = get_vram_coordinator()
                coordinator.request_vram("mmaudio", 6000, EvictionPriority.NORMAL)
            except Exception as e:
                logger.warning(f"[MMAUDIO] VRAM coordinator request failed: {e}")

            logger.info(f"[MMAUDIO] Loading model: {self.model_variant}...")
            vram_before = torch.cuda.memory_allocated(0) if torch.cuda.is_available() else 0

            def _load_sync():
                from mmaudio.eval_utils import ModelConfig, setup_eval_logging
                from mmaudio.model.flow_matching import FlowMatching
                from mmaudio.model.utils import load_model

                setup_eval_logging()
                model_config = ModelConfig(self.model_variant)
                net, feature_utils = load_model(model_config, device='cuda')
                net.eval()
                return net, feature_utils, model_config

            self._net, self._feature_utils, self._model_config = await asyncio.to_thread(_load_sync)
            self._is_loaded = True
            self._last_used = time.time()

            vram_after = torch.cuda.memory_allocated(0) if torch.cuda.is_available() else 0
            self._vram_mb = (vram_after - vram_before) / (1024 * 1024)

            logger.info(f"[MMAUDIO] Model loaded (VRAM: {self._vram_mb:.0f}MB)")
            return True

        except Exception as e:
            logger.error(f"[MMAUDIO] Failed to load: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def unload(self) -> bool:
        """Unload MMAudio from GPU."""
        if not self._is_loaded:
            return False

        try:
            import torch

            del self._net
            del self._feature_utils
            self._net = None
            self._feature_utils = None
            self._is_loaded = False
            self._vram_mb = 0
            self._in_use = 0

            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.synchronize()

            logger.info("[MMAUDIO] Model unloaded")
            return True

        except Exception as e:
            logger.error(f"[MMAUDIO] Unload error: {e}")
            return False

    # =========================================================================
    # Generation
    # =========================================================================

    async def generate_from_image(
        self,
        image_bytes: bytes,
        prompt: str = "",
        negative_prompt: str = "",
        duration_seconds: float = 8.0,
        cfg_strength: float = 4.5,
        num_steps: int = 25,
        seed: int = -1,
    ) -> Optional[Dict[str, Any]]:
        """
        Generate audio from an image (+ optional text prompt).

        MMAudio is a video-to-audio model. For image input, we duplicate
        the single frame to create pseudo-video input matching the expected
        temporal structure.

        Args:
            image_bytes: Input image as bytes
            prompt: Optional text conditioning
            negative_prompt: Negative text conditioning
            duration_seconds: Audio duration (max 8s)
            cfg_strength: Classifier-free guidance strength
            num_steps: Euler ODE solver steps
            seed: Random seed (-1 = random)

        Returns:
            Dict with audio_bytes, seed, generation_time_ms or None
        """
        import random as random_mod

        if not self._is_loaded:
            if not await self._load():
                return None

        self._in_use += 1
        self._last_used = time.time()
        start_time = time.time()

        try:
            import torch
            import torchaudio
            from PIL import Image
            import io
            import numpy as np

            duration_seconds = min(duration_seconds, 8.0)
            if seed == -1:
                seed = random_mod.randint(0, 2**32 - 1)

            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

            def _generate():
                with torch.no_grad():
                    rng = torch.Generator(device='cuda')
                    rng.manual_seed(seed)

                    # MMAudio expects video frames as tensor
                    # For single image: duplicate to ~8fps * duration
                    from torchvision import transforms
                    transform = transforms.Compose([
                        transforms.Resize((384, 384)),
                        transforms.ToTensor(),
                        transforms.Normalize(mean=[0.48145466, 0.4578275, 0.40821073],
                                             std=[0.26862954, 0.26130258, 0.27577711]),
                    ])
                    frame = transform(image).unsqueeze(0).cuda()  # [1, 3, 384, 384]
                    # Duplicate along time dim: [1, T, 3, 384, 384]
                    num_frames = int(duration_seconds * 8)  # 8 fps
                    video = frame.unsqueeze(1).expand(-1, num_frames, -1, -1, -1)

                    # Generate audio
                    audios = self._net.generate(
                        video=video,
                        text=[prompt] if prompt else [''],
                        negative_text=[negative_prompt] if negative_prompt else [''],
                        duration=duration_seconds,
                        cfg_strength=cfg_strength,
                        num_steps=num_steps,
                        rng=rng,
                        feature_utils=self._feature_utils,
                    )

                    return audios  # [1, T_audio]

            audio_tensor = await asyncio.to_thread(_generate)

            # Encode to WAV
            audio_bytes = self._encode_wav(audio_tensor)
            if audio_bytes is None:
                return None

            elapsed_ms = int((time.time() - start_time) * 1000)
            logger.info(
                f"[MMAUDIO] Generated from image: duration={duration_seconds}s, "
                f"time={elapsed_ms}ms, seed={seed}"
            )

            return {
                "audio_bytes": audio_bytes,
                "seed": seed,
                "generation_time_ms": elapsed_ms,
            }

        except Exception as e:
            logger.error(f"[MMAUDIO] Generation error: {e}")
            import traceback
            traceback.print_exc()
            return None

        finally:
            self._in_use -= 1

    async def generate_from_text(
        self,
        prompt: str,
        negative_prompt: str = "",
        duration_seconds: float = 8.0,
        cfg_strength: float = 4.5,
        num_steps: int = 25,
        seed: int = -1,
    ) -> Optional[Dict[str, Any]]:
        """
        Generate audio from text prompt only (no visual input).

        Args:
            prompt: Text description of desired audio
            negative_prompt: Negative text conditioning
            duration_seconds: Audio duration (max 8s)
            cfg_strength: CFG strength
            num_steps: Euler solver steps
            seed: Random seed

        Returns:
            Dict with audio_bytes, seed, generation_time_ms or None
        """
        import random as random_mod

        if not self._is_loaded:
            if not await self._load():
                return None

        self._in_use += 1
        self._last_used = time.time()
        start_time = time.time()

        try:
            import torch

            duration_seconds = min(duration_seconds, 8.0)
            if seed == -1:
                seed = random_mod.randint(0, 2**32 - 1)

            def _generate():
                with torch.no_grad():
                    rng = torch.Generator(device='cuda')
                    rng.manual_seed(seed)

                    audios = self._net.generate(
                        video=None,
                        text=[prompt],
                        negative_text=[negative_prompt] if negative_prompt else [''],
                        duration=duration_seconds,
                        cfg_strength=cfg_strength,
                        num_steps=num_steps,
                        rng=rng,
                        feature_utils=self._feature_utils,
                    )

                    return audios

            audio_tensor = await asyncio.to_thread(_generate)

            audio_bytes = self._encode_wav(audio_tensor)
            if audio_bytes is None:
                return None

            elapsed_ms = int((time.time() - start_time) * 1000)
            logger.info(
                f"[MMAUDIO] Generated from text: prompt='{prompt[:60]}...', "
                f"duration={duration_seconds}s, time={elapsed_ms}ms"
            )

            return {
                "audio_bytes": audio_bytes,
                "seed": seed,
                "generation_time_ms": elapsed_ms,
            }

        except Exception as e:
            logger.error(f"[MMAUDIO] Text generation error: {e}")
            import traceback
            traceback.print_exc()
            return None

        finally:
            self._in_use -= 1

    def _encode_wav(self, audio_tensor) -> Optional[bytes]:
        """Encode audio tensor to WAV bytes."""
        import io
        import numpy as np

        try:
            if hasattr(audio_tensor, 'cpu'):
                audio_np = audio_tensor.cpu().float().numpy()
            else:
                audio_np = np.array(audio_tensor)

            # Ensure [samples, channels] for soundfile
            if audio_np.ndim == 1:
                audio_np = audio_np[:, np.newaxis]
            elif audio_np.ndim == 2 and audio_np.shape[0] < audio_np.shape[1]:
                audio_np = audio_np.T  # [channels, samples] -> [samples, channels]
            elif audio_np.ndim == 3:
                audio_np = audio_np.squeeze(0).T

            import soundfile as sf
            buffer = io.BytesIO()
            sf.write(buffer, audio_np, 44100, format="WAV")
            buffer.seek(0)
            return buffer.getvalue()

        except Exception as e:
            logger.error(f"[MMAUDIO] WAV encoding error: {e}")
            return None


# =============================================================================
# Singleton
# =============================================================================

_backend: Optional[MMAudioBackend] = None


def get_mmaudio_backend() -> MMAudioBackend:
    global _backend
    if _backend is None:
        _backend = MMAudioBackend()
    return _backend


def reset_mmaudio_backend():
    global _backend
    _backend = None
