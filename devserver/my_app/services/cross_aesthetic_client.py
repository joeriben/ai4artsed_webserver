"""
Cross-Aesthetic HTTP Client — GPU Service Backend

Calls the shared GPU service (port 17803) for crossmodal generation.
Crossmodal Lab v2: Latent Audio Synth, ImageBind Guidance, MMAudio.
"""

import base64
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class CrossAestheticClient:
    """HTTP client for crossmodal generation on the GPU service."""

    def __init__(self):
        from config import GPU_SERVICE_URL, GPU_SERVICE_TIMEOUT
        self.base_url = GPU_SERVICE_URL.rstrip('/')
        self.timeout = GPU_SERVICE_TIMEOUT

    def _post(self, path: str, data: dict) -> Optional[dict]:
        import requests
        url = f"{self.base_url}{path}"
        try:
            resp = requests.post(url, json=data, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.ConnectionError:
            logger.error(f"[CROSSMODAL-CLIENT] GPU service unreachable at {url}")
            return None
        except requests.Timeout:
            logger.error(f"[CROSSMODAL-CLIENT] Timeout after {self.timeout}s: {path}")
            return None
        except Exception as e:
            logger.error(f"[CROSSMODAL-CLIENT] Request failed: {e}")
            return None

    def _get(self, path: str) -> Optional[dict]:
        import requests
        url = f"{self.base_url}{path}"
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"[CROSSMODAL-CLIENT] GET failed: {e}")
            return None

    async def is_available(self) -> bool:
        import asyncio
        try:
            result = await asyncio.to_thread(self._get, '/api/cross_aesthetic/available')
            return result is not None and result.get('available', False)
        except Exception:
            return False

    async def synth(
        self,
        prompt_a: str,
        prompt_b: Optional[str] = None,
        alpha: float = 0.5,
        magnitude: float = 1.0,
        noise_sigma: float = 0.0,
        dimension_offsets: Optional[Dict[int, float]] = None,
        duration_seconds: float = 1.0,
        steps: int = 20,
        cfg_scale: float = 3.5,
        seed: int = -1,
    ) -> Optional[Dict[str, Any]]:
        """Latent Audio Synth: T5 embedding manipulation + Stable Audio generation."""
        import asyncio

        data: Dict[str, Any] = {
            'prompt_a': prompt_a,
            'alpha': alpha,
            'magnitude': magnitude,
            'noise_sigma': noise_sigma,
            'duration_seconds': duration_seconds,
            'steps': steps,
            'cfg_scale': cfg_scale,
            'seed': seed,
        }
        if prompt_b:
            data['prompt_b'] = prompt_b
        if dimension_offsets:
            data['dimension_offsets'] = dimension_offsets

        result = await asyncio.to_thread(self._post, '/api/cross_aesthetic/synth', data)
        if result is None or not result.get('success'):
            return None

        return {
            'audio_bytes': base64.b64decode(result['audio_base64']),
            'embedding_stats': result.get('embedding_stats'),
            'generation_time_ms': result.get('generation_time_ms'),
            'seed': result.get('seed'),
        }

    async def image_guided_audio(
        self,
        image_bytes: bytes,
        prompt: str = "",
        lambda_guidance: float = 0.1,
        warmup_steps: int = 10,
        total_steps: int = 50,
        duration_seconds: float = 10.0,
        cfg_scale: float = 7.0,
        seed: int = -1,
    ) -> Optional[Dict[str, Any]]:
        """ImageBind gradient guidance: image-guided audio generation."""
        import asyncio

        result = await asyncio.to_thread(self._post, '/api/cross_aesthetic/image_guided_audio', {
            'image_base64': base64.b64encode(image_bytes).decode('utf-8'),
            'prompt': prompt,
            'lambda_guidance': lambda_guidance,
            'warmup_steps': warmup_steps,
            'total_steps': total_steps,
            'duration_seconds': duration_seconds,
            'cfg_scale': cfg_scale,
            'seed': seed,
        })

        if result is None or not result.get('success'):
            return None

        return {
            'audio_bytes': base64.b64decode(result['audio_base64']),
            'cosine_similarity': result.get('cosine_similarity'),
            'generation_time_ms': result.get('generation_time_ms'),
            'seed': result.get('seed'),
        }

    async def mmaudio(
        self,
        image_bytes: Optional[bytes] = None,
        prompt: str = "",
        negative_prompt: str = "",
        duration_seconds: float = 8.0,
        cfg_strength: float = 4.5,
        num_steps: int = 25,
        seed: int = -1,
    ) -> Optional[Dict[str, Any]]:
        """MMAudio: image/text to audio generation."""
        import asyncio

        data: Dict[str, Any] = {
            'prompt': prompt,
            'negative_prompt': negative_prompt,
            'duration_seconds': duration_seconds,
            'cfg_strength': cfg_strength,
            'num_steps': num_steps,
            'seed': seed,
        }
        if image_bytes:
            data['image_base64'] = base64.b64encode(image_bytes).decode('utf-8')

        result = await asyncio.to_thread(self._post, '/api/cross_aesthetic/mmaudio', data)
        if result is None or not result.get('success'):
            return None

        return {
            'audio_bytes': base64.b64decode(result['audio_base64']),
            'generation_time_ms': result.get('generation_time_ms'),
            'seed': result.get('seed'),
        }


# Singleton
_client: Optional[CrossAestheticClient] = None


def get_cross_aesthetic_client() -> CrossAestheticClient:
    global _client
    if _client is None:
        _client = CrossAestheticClient()
    return _client
