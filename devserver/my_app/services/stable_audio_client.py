"""
Stable Audio API Client
Generiert Audio mit Stability AI's Stable Audio API
"""
import asyncio
import aiohttp
import logging
import time
import base64
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class StableAudioClient:
    """Client für Stable Audio API"""
    
    def __init__(self, api_key: str = None):
        """
        Initialize Stable Audio client
        
        Args:
            api_key: Stability AI API key (loaded from file if not provided)
        """
        self.base_url = "https://api.stability.ai/v2beta/stable-audio"
        self.api_key = api_key or self._load_api_key()
        
        if not self.api_key:
            logger.warning("⚠️ Stable Audio API key not configured")
        else:
            logger.info("✅ Stable Audio client initialized")
    
    @staticmethod
    def _load_api_key() -> Optional[str]:
        """Load API key from file"""
        try:
            key_file = Path(__file__).parent.parent.parent / "stability.key"
            if key_file.exists():
                with open(key_file, 'r') as f:
                    return f.read().strip()
        except Exception as e:
            logger.error(f"Failed to load Stability API key: {e}")
        return None
    
    async def generate_audio(
        self,
        text_description: str,
        duration_seconds: float = 10.0,
        cfg_scale: float = 7.0,
        seed: int = None
    ) -> Optional[str]:
        """
        Generate audio from text description
        
        Args:
            text_description: Text describing the audio to generate
            duration_seconds: Duration in seconds (max 47.0)
            cfg_scale: Classifier-free guidance scale (default 7.0)
            seed: Random seed for reproducibility
            
        Returns:
            generation_id for polling, or None on error
        """
        if not self.api_key:
            logger.error("Stable Audio API key not configured")
            return None
        
        try:
            # Prepare request
            payload = {
                "text_description": text_description[:500],  # Max 500 chars
                "duration_seconds": min(duration_seconds, 47.0),  # Max 47s
                "cfg_scale": cfg_scale
            }
            
            if seed is not None:
                payload["seed"] = seed
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/generate/audio",
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        generation_id = result.get("id")
                        logger.info(f"✅ Audio generation started: {generation_id}")
                        return generation_id
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Stable Audio API error {response.status}: {error_text}")
                        return None
        
        except Exception as e:
            logger.error(f"❌ Error generating audio: {e}", exc_info=True)
            return None
    
    async def get_generation_status(self, generation_id: str) -> Optional[Dict[str, Any]]:
        """
        Check generation status
        
        Args:
            generation_id: The generation ID from generate_audio()
            
        Returns:
            Status dict with 'status' and optionally 'audio' (base64)
        """
        if not self.api_key:
            return None
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/generate/{generation_id}",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Failed to get status: {response.status}")
                        return None
        
        except Exception as e:
            logger.error(f"Error getting generation status: {e}")
            return None
    
    async def wait_for_completion(
        self,
        generation_id: str,
        timeout: int = 120,
        poll_interval: float = 2.0
    ) -> Optional[bytes]:
        """
        Wait for audio generation to complete
        
        Args:
            generation_id: The generation ID to monitor
            timeout: Maximum wait time in seconds
            poll_interval: How often to check status
            
        Returns:
            Audio bytes or None if timeout/error
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status_data = await self.get_generation_status(generation_id)
            
            if not status_data:
                await asyncio.sleep(poll_interval)
                continue
            
            status = status_data.get("status")
            
            if status == "completed":
                # Get audio data (base64 encoded)
                audio_b64 = status_data.get("audio")
                if audio_b64:
                    audio_bytes = base64.b64decode(audio_b64)
                    logger.info(f"✅ Audio generation completed: {len(audio_bytes)} bytes")
                    return audio_bytes
                else:
                    logger.error("No audio data in completed response")
                    return None
            
            elif status == "failed":
                error = status_data.get("error", "Unknown error")
                logger.error(f"❌ Audio generation failed: {error}")
                return None
            
            elif status == "processing":
                await asyncio.sleep(poll_interval)
            
            else:
                logger.warning(f"Unknown status: {status}")
                await asyncio.sleep(poll_interval)
        
        logger.error(f"⏱️ Timeout waiting for audio generation ({timeout}s)")
        return None
    
    async def health_check(self) -> bool:
        """
        Check if Stable Audio API is accessible
        
        Returns:
            True if accessible, False otherwise
        """
        if not self.api_key:
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            async with aiohttp.ClientSession() as session:
                # Try to get user account info (simple health check)
                async with session.get(
                    "https://api.stability.ai/v1/user/account",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    return response.status in [200, 403]  # 403 = valid key, wrong endpoint
        
        except Exception as e:
            logger.debug(f"Stable Audio health check failed: {e}")
            return False


# Singleton instance
_client = None

def get_stable_audio_client() -> StableAudioClient:
    """Get Stable Audio client singleton"""
    global _client
    if _client is None:
        _client = StableAudioClient()
    return _client
