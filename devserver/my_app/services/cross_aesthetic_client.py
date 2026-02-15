"""
Cross-Aesthetic HTTP Client — GPU Service Backend

Calls the shared GPU service (port 17803) for cross-aesthetic generation.
Three strategies: image→audio, shared seed, latent cross-decoding.
"""

import base64
import logging
from typing import Optional, Tuple, Dict, Any

logger = logging.getLogger(__name__)


class CrossAestheticClient:
    """HTTP client for cross-aesthetic generation on the GPU service."""

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
            logger.error(f"[CROSS-AESTHETIC-CLIENT] GPU service unreachable at {url}")
            return None
        except requests.Timeout:
            logger.error(f"[CROSS-AESTHETIC-CLIENT] Timeout after {self.timeout}s: {path}")
            return None
        except Exception as e:
            logger.error(f"[CROSS-AESTHETIC-CLIENT] Request failed: {e}")
            return None

    def _get(self, path: str) -> Optional[dict]:
        import requests
        url = f"{self.base_url}{path}"
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"[CROSS-AESTHETIC-CLIENT] GET failed: {e}")
            return None

    async def is_available(self) -> bool:
        import asyncio
        try:
            result = await asyncio.to_thread(self._get, '/api/cross_aesthetic/available')
            return result is not None and result.get('available', False)
        except Exception:
            return False

    async def image_to_audio(
        self,
        image_bytes: bytes,
        duration_seconds: float = 10.0,
        steps: int = 100,
        cfg_scale: float = 7.0,
        seed: int = -1,
    ) -> Optional[Dict[str, Any]]:
        """
        Strategy A: CLIP image → Stable Audio conditioning.

        Returns:
            Dict with 'audio_bytes', 'seed', 'strategy_info' or None
        """
        import asyncio

        result = await asyncio.to_thread(self._post, '/api/cross_aesthetic/image_to_audio', {
            'image_base64': base64.b64encode(image_bytes).decode('utf-8'),
            'duration_seconds': duration_seconds,
            'steps': steps,
            'cfg_scale': cfg_scale,
            'seed': seed,
        })

        if result is None or not result.get('success'):
            return None

        return {
            'audio_bytes': base64.b64decode(result['audio_base64']),
            'seed': result.get('seed'),
            'strategy_info': result.get('strategy_info'),
        }

    async def shared_seed(
        self,
        prompt: str,
        seed: int = 42,
        image_params: Optional[Dict] = None,
        audio_params: Optional[Dict] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Strategy B: Same noise seed → image + audio.

        Returns:
            Dict with 'image_bytes', 'audio_bytes', 'seed', 'strategy_info' or None
        """
        import asyncio

        result = await asyncio.to_thread(self._post, '/api/cross_aesthetic/shared_seed', {
            'prompt': prompt,
            'seed': seed,
            'image_params': image_params or {},
            'audio_params': audio_params or {},
        })

        if result is None or not result.get('success'):
            return None

        output = {
            'seed': result.get('seed'),
            'strategy_info': result.get('strategy_info'),
        }
        if 'image_base64' in result:
            output['image_bytes'] = base64.b64decode(result['image_base64'])
        if 'audio_base64' in result:
            output['audio_bytes'] = base64.b64decode(result['audio_base64'])

        return output

    async def cross_decode(
        self,
        prompt: str,
        direction: str = "image_to_audio",
        seed: int = 42,
        image_params: Optional[Dict] = None,
        audio_params: Optional[Dict] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Strategy C: Latent cross-decoding.

        Returns:
            Dict with 'output_bytes', 'output_type', 'seed', 'strategy_info' or None
        """
        import asyncio

        result = await asyncio.to_thread(self._post, '/api/cross_aesthetic/cross_decode', {
            'prompt': prompt,
            'direction': direction,
            'seed': seed,
            'image_params': image_params or {},
            'audio_params': audio_params or {},
        })

        if result is None or not result.get('success'):
            return None

        return {
            'output_bytes': base64.b64decode(result['output_base64']),
            'output_type': result.get('output_type'),
            'seed': result.get('seed'),
            'strategy_info': result.get('strategy_info'),
        }


# Singleton
_client: Optional[CrossAestheticClient] = None


def get_cross_aesthetic_client() -> CrossAestheticClient:
    global _client
    if _client is None:
        _client = CrossAestheticClient()
    return _client
