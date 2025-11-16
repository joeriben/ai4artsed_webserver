"""
SwarmUI API Client - Proper image generation using SwarmUI's native API

Replaces the fragile ComfyUI history parsing approach with SwarmUI's clean API:
- /API/GetNewSession - Get session ID
- /API/GenerateText2Image - Generate image, returns paths directly
- /View/... - Download generated images

No history parsing, no polling - SwarmUI handles everything.
"""

import aiohttp
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class SwarmUIClient:
    """
    Client for SwarmUI's Text2Image API

    SwarmUI runs on port 7801 and wraps ComfyUI with a clean REST API.
    It returns image paths directly - no need to poll history endpoints.
    """

    def __init__(self, base_url: str = None):
        """
        Initialize SwarmUI client

        Args:
            base_url: SwarmUI API base URL (default: http://127.0.0.1:7801)
        """
        if base_url is None:
            from config import SWARMUI_API_PORT
            base_url = f"http://127.0.0.1:{SWARMUI_API_PORT}"

        self.base_url = base_url
        self._session_id = None
        logger.info(f"[SWARMUI] Initialized client for {base_url}")

    async def get_session(self) -> Optional[str]:
        """
        Get or refresh SwarmUI session ID

        Returns:
            session_id string, or None on failure
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/API/GetNewSession",
                    json={},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self._session_id = data.get("session_id")
                        logger.info(f"[SWARMUI] Got session ID: {self._session_id[:16]}...")
                        return self._session_id
                    else:
                        error_text = await response.text()
                        logger.error(f"[SWARMUI] Failed to get session: {response.status} - {error_text}")
                        return None
        except Exception as e:
            logger.error(f"[SWARMUI] Error getting session: {e}")
            return None

    async def generate_image(
        self,
        prompt: str,
        model: str,
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 1024,
        steps: int = 20,
        cfg_scale: float = 7.0,
        seed: int = -1,
        **extra_params
    ) -> Optional[List[str]]:
        """
        Generate image using SwarmUI API

        Args:
            prompt: Positive prompt text
            model: Model name (e.g., "OfficialStableDiffusion/sd_xl_base_1.0")
            negative_prompt: Negative prompt text
            width: Image width
            height: Image height
            steps: Number of steps
            cfg_scale: CFG scale
            seed: Random seed (-1 for random)
            **extra_params: Additional T2I parameters

        Returns:
            List of image paths (e.g., ["View/local/raw/2024-01-02/image.png"]), or None on failure
        """
        # Ensure we have a session
        if not self._session_id:
            await self.get_session()

        if not self._session_id:
            logger.error("[SWARMUI] Cannot generate without session ID")
            return None

        # Build request parameters
        # NOTE: All T2I params go at root level, not nested
        request_data = {
            "session_id": self._session_id,
            "images": 1,  # Generate 1 image
            "prompt": prompt,
            "model": model,
            "width": width,
            "height": height,
            "steps": steps,
            "cfgscale": cfg_scale,
            "seed": seed,
        }

        # Add negative prompt if provided
        if negative_prompt:
            request_data["negativeprompt"] = negative_prompt

        # Add any extra parameters
        request_data.update(extra_params)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/API/GenerateText2Image",
                    json=request_data,
                    timeout=aiohttp.ClientTimeout(total=120)  # 2 min timeout for generation
                ) as response:
                    if response.status == 200:
                        data = await response.json()

                        # Check for invalid session error
                        if "error_id" in data and data["error_id"] == "invalid_session_id":
                            logger.warning("[SWARMUI] Session expired, refreshing...")
                            await self.get_session()
                            # Retry once with new session
                            return await self.generate_image(
                                prompt, model, negative_prompt, width, height,
                                steps, cfg_scale, seed, **extra_params
                            )

                        # Check for general errors
                        if "error" in data:
                            logger.error(f"[SWARMUI] Generation error: {data['error']}")
                            return None

                        # Extract image paths
                        images = data.get("images", [])
                        if images:
                            logger.info(f"[SWARMUI] ✓ Generated {len(images)} image(s)")
                            return images
                        else:
                            logger.error("[SWARMUI] No images in response")
                            return None
                    else:
                        error_text = await response.text()
                        logger.error(f"[SWARMUI] Generation failed: {response.status} - {error_text}")
                        return None
        except aiohttp.ClientError as e:
            logger.error(f"[SWARMUI] Connection error during generation: {e}")
            return None
        except Exception as e:
            logger.error(f"[SWARMUI] Error generating image: {e}")
            return None

    async def download_image(self, image_path: str) -> Optional[bytes]:
        """
        Download generated image from SwarmUI

        Args:
            image_path: Path returned by generate_image (e.g., "View/local/raw/2024-01-02/image.png")

        Returns:
            Image bytes, or None on failure
        """
        try:
            # Handle both full URLs and relative paths
            if image_path.startswith("http"):
                url = image_path
            else:
                url = f"{self.base_url}/{image_path}"

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        logger.info(f"[SWARMUI] Downloaded image: {len(image_data)} bytes")
                        return image_data
                    else:
                        logger.error(f"[SWARMUI] Failed to download image: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"[SWARMUI] Error downloading image: {e}")
            return None

    async def health_check(self) -> bool:
        """
        Check if SwarmUI API is accessible

        Returns:
            True if accessible, False otherwise
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/API/GetNewSession",
                    json={},
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    return response.status == 200
        except Exception as e:
            logger.debug(f"[SWARMUI] Health check failed: {e}")
            return False


# Singleton instance
_client = None


def get_swarmui_client(base_url: str = None) -> SwarmUIClient:
    """
    Get SwarmUI client singleton

    Args:
        base_url: Optional explicit URL, otherwise auto-configured
    """
    global _client
    if _client is None:
        _client = SwarmUIClient(base_url)
    return _client
