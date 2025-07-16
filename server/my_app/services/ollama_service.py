"""
Service for interacting with Ollama API
"""
import logging
import requests
from typing import Dict, Optional, Any

from config import (
    OLLAMA_API_BASE_URL,
    OLLAMA_TIMEOUT,
    TRANSLATION_MODEL,
    SAFETY_MODEL,
    ANALYSIS_MODEL,
    ANALYSIS_SYSTEM_PROMPT,
    PROMPT_CACHE,
    TRANSLATION_PROMPT
)

logger = logging.getLogger(__name__)


class OllamaService:
    """Service class for Ollama API interactions"""
    
    def __init__(self):
        self.base_url = OLLAMA_API_BASE_URL
        self.timeout = OLLAMA_TIMEOUT
        
    def _make_request(self, endpoint: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Make a request to Ollama API
        
        Args:
            endpoint: API endpoint path
            payload: Request payload
            
        Returns:
            Response data or None if request fails
        """
        try:
            response = requests.post(
                f"{self.base_url}/{endpoint}",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API request failed: {e}")
            return None
    
    def translate_text(self, text: str) -> Optional[str]:
        """
        Translate text to English using Ollama
        
        Args:
            text: Text to translate
            
        Returns:
            Translated text or None if translation fails
        """
        prompt = TRANSLATION_PROMPT.format(text=text)
        
        payload = {
            "model": TRANSLATION_MODEL,
            "prompt": prompt,
            "stream": False,
            "keep_alive": "0s"
        }
        
        result = self._make_request("api/generate", payload)
        if result:
            return result.get("response", "").strip()
        return None
    
    def check_safety(self, text: str) -> Dict[str, Any]:
        """
        Check if text is safe using Ollama safety model
        
        Args:
            text: Text to check
            
        Returns:
            Dictionary with 'is_safe' boolean and optional 'reason' if unsafe
        """
        prompt = f"Is the following text safe? Please classify it. The text is:\n\n{text}"
        
        payload = {
            "model": SAFETY_MODEL,
            "prompt": prompt,
            "stream": False,
            "keep_alive": "0s"
        }
        
        result = self._make_request("api/generate", payload)
        if not result:
            return {"is_safe": True, "note": "Safety check service failed, bypassing check."}
        
        safety_response = result.get("response", "").strip()
        if safety_response.lower().strip().startswith("safe"):
            return {"is_safe": True}
        else:
            codes = [p.strip() for p in safety_response.strip().split('\n')]
            reasons = [p for p in codes]
            return {
                "is_safe": False,
                "reason": f"Sorry, your prompt has been rejected due to potential issues: {', '.join(sorted(list(set(reasons))))}"
            }
    
    def analyze_image(self, image_data: str) -> Optional[str]:
        """
        Analyze an image using Ollama's vision model
        
        Args:
            image_data: Base64 encoded image data
            
        Returns:
            Analysis text or None if analysis fails
        """
        # Remove data URL prefix if present
        if ',' in image_data:
            image_data = image_data.split(',', 1)[-1]
        
        payload = {
            "model": ANALYSIS_MODEL,
            "prompt": "Analyze the image.",
            "system": ANALYSIS_SYSTEM_PROMPT,
            "images": [image_data],
            "stream": False,
            "keep_alive": "0s"  # Unload model immediately after use
        }
        
        logger.info(f"Sending image to Ollama model: {ANALYSIS_MODEL} (will unload after).")
        result = self._make_request("api/generate", payload)
        
        if result:
            generated_text = result.get("response", "").strip()
            logger.info("Ollama analysis successful.")
            return generated_text
        return None
    
    def validate_and_translate_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Validate and translate a prompt with caching
        
        Args:
            prompt: Original prompt text
            
        Returns:
            Dictionary with 'success', 'translated_prompt', and optional 'error'
        """
        cache_key = prompt.strip().lower()
        
        # Check cache first
        if cache_key in PROMPT_CACHE:
            return {
                "success": True,
                "translated_prompt": PROMPT_CACHE[cache_key]["translated"],
                "cached": True
            }
        
        # Check if this is an image analysis prompt (already in English)
        is_image_analysis = prompt.strip().startswith("Material and medial properties:")
        
        # Translate prompt only if it's not already in English and not an image analysis
        if is_image_analysis:
            # Image analysis prompts are already in English, skip translation
            translated_prompt = prompt
            logger.info("Skipping translation for image analysis prompt")
        else:
            # Translate prompt (handles English detection internally)
            translated_prompt = self.translate_text(prompt)
            if not translated_prompt:
                return {"success": False, "error": "Übersetzungs-Service fehlgeschlagen."}
        
        # Check safety for ALL prompts
        safety_result = self.check_safety(translated_prompt)
        if not safety_result["is_safe"]:
            return {"success": False, "error": safety_result.get("reason", "Prompt rejected for safety reasons.")}
        
        # Cache the result
        PROMPT_CACHE[cache_key] = {
            "translated": translated_prompt,
            "is_safe": True
        }
        logger.info(f"Cached new prompt: {cache_key[:50]}...")
        
        return {
            "success": True,
            "translated_prompt": translated_prompt,
            "cached": False
        }


# Create a singleton instance
ollama_service = OllamaService()
