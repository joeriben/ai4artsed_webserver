"""
Service for interacting with Ollama API
"""
import logging
import requests
from typing import Dict, Optional, Any

from config import (
    LLM_PROVIDER,
    OLLAMA_API_BASE_URL,
    LMSTUDIO_API_BASE_URL,
    OLLAMA_TIMEOUT,
    TRANSLATION_MODEL,
    SAFETY_MODEL,
    ANALYSIS_MODEL,
    ANALYSIS_SYSTEM_PROMPT,
    PROMPT_CACHE,
    TRANSLATION_PROMPT,
    NO_TRANSLATE,
    GPT_OSS_MODEL,
    GPT_OSS_SAFETY_SYSTEM_PROMPT,
    GPT_OSS_TRANSLATION_SYSTEM_PROMPT
)

logger = logging.getLogger(__name__)


class OllamaService:
    """Service class for LLM API interactions (Ollama or LM Studio)"""

    def __init__(self):
        self.provider = LLM_PROVIDER
        self.base_url = LMSTUDIO_API_BASE_URL if self.provider == "lmstudio" else OLLAMA_API_BASE_URL
        self.timeout = OLLAMA_TIMEOUT
        logger.info(f"Initialized LLM service with provider: {self.provider} at {self.base_url}")
        
    def _make_request(self, endpoint: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Make a request to LLM API (Ollama or LM Studio format)

        Args:
            endpoint: API endpoint path (Ollama format)
            payload: Request payload (Ollama format)

        Returns:
            Response data in Ollama format or None if request fails
        """
        try:
            # Convert to LM Studio format if needed
            if self.provider == "lmstudio":
                keep_alive = payload.get("keep_alive", "5m")
                model = payload.get("model", "")

                lmstudio_payload, lmstudio_endpoint = self._convert_to_lmstudio_format(payload, endpoint)
                response = requests.post(
                    f"{self.base_url}/{lmstudio_endpoint}",
                    json=lmstudio_payload,
                    timeout=self.timeout
                )
                response.raise_for_status()
                result = response.json()

                # Unload model from VRAM if keep_alive is "0s"
                if keep_alive == "0s":
                    self._unload_lmstudio_model(model)

                # Convert back to Ollama format
                return self._convert_from_lmstudio_format(result)
            else:
                # Standard Ollama request
                response = requests.post(
                    f"{self.base_url}/{endpoint}",
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"{self.provider.upper()} API request failed: {e}")
            return None

    def _unload_lmstudio_model(self, model: str) -> None:
        """
        Unload a model from LM Studio VRAM

        Args:
            model: Model identifier to unload
        """
        try:
            # LM Studio API endpoint for model unloading
            response = requests.post(
                f"{self.base_url}/v1/models/unload",
                json={"model": model},
                timeout=5
            )
            if response.status_code == 200:
                logger.info(f"Unloaded {model} from VRAM (LM Studio)")
            else:
                logger.warning(f"Failed to unload {model} from LM Studio (status {response.status_code})")
        except requests.exceptions.RequestException as e:
            logger.warning(f"Could not unload model from LM Studio: {e}")

    def _convert_to_lmstudio_format(self, ollama_payload: Dict[str, Any], endpoint: str) -> tuple[Dict[str, Any], str]:
        """
        Convert Ollama API format to LM Studio (OpenAI-compatible) format

        Args:
            ollama_payload: Ollama format payload
            endpoint: Ollama endpoint

        Returns:
            Tuple of (LM Studio payload, LM Studio endpoint)
        """
        model = ollama_payload.get("model", "openai/gpt-oss-20b")
        prompt = ollama_payload.get("prompt", "")
        system = ollama_payload.get("system", "")

        # Build messages array
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        lmstudio_payload = {
            "model": model,
            "messages": messages,
            "temperature": ollama_payload.get("temperature", 0.7),
            "max_tokens": ollama_payload.get("max_tokens", 512),
            "stream": False
        }

        return lmstudio_payload, "v1/chat/completions"

    def _convert_from_lmstudio_format(self, lmstudio_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert LM Studio (OpenAI-compatible) response to Ollama format

        Args:
            lmstudio_response: LM Studio API response

        Returns:
            Ollama format response
        """
        # Extract the assistant's message content
        content = ""
        if "choices" in lmstudio_response and len(lmstudio_response["choices"]) > 0:
            choice = lmstudio_response["choices"][0]
            if "message" in choice and "content" in choice["message"]:
                content = choice["message"]["content"]

        return {
            "response": content,
            "model": lmstudio_response.get("model", ""),
            "done": True
        }
    
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

    def check_safety_gpt_oss(self, text: str, keep_alive: str = "10m") -> Dict[str, Any]:
        """
        Check if text is safe using GPT-OSS-20b with §86a StGB compliance

        Args:
            text: Text to check (German or English)
            keep_alive: How long to keep model in VRAM (default: 10m for Stage 1-3)

        Returns:
            Dictionary with:
            - 'is_safe': Boolean
            - 'translated_text': If safe, the translated text
            - 'reason': If unsafe, the §86a blocking reason
            - 'symbol': If unsafe, the specific symbol/organization
        """
        prompt = f"Check this text for safety under §86a StGB:\n\n{text}"

        payload = {
            "model": GPT_OSS_MODEL,
            "prompt": prompt,
            "system": GPT_OSS_SAFETY_SYSTEM_PROMPT,
            "stream": False,
            "keep_alive": keep_alive
        }

        result = self._make_request("api/generate", payload)
        if not result:
            logger.error("GPT-OSS safety check failed, falling back to llama-guard3")
            # Fallback to legacy safety check
            return self.check_safety(text)

        response = result.get("response", "").strip()

        # Parse response format: "SAFE: [text]" or "BLOCKED: §86a StGB - [symbol] - [explanation]"
        if response.startswith("SAFE:"):
            translated_text = response[5:].strip()  # Remove "SAFE: " prefix
            return {
                "is_safe": True,
                "translated_text": translated_text
            }
        elif response.startswith("BLOCKED:"):
            # Parse: "BLOCKED: §86a StGB - ISIS symbols - ISIS is a terrorist organization"
            blocked_parts = response[8:].strip()  # Remove "BLOCKED: " prefix

            # Extract symbol and reason
            parts = blocked_parts.split(" - ", 2)
            law_reference = parts[0] if len(parts) > 0 else "§86a StGB"
            symbol = parts[1] if len(parts) > 1 else "extremist content"
            explanation = parts[2] if len(parts) > 2 else "This content violates German law"

            return {
                "is_safe": False,
                "reason": f"⚠️ Dein Prompt wurde blockiert\n\nGRUND: {law_reference} - {symbol}\n\n{explanation}\n\nWARUM DIESE REGEL?\nDiese Symbole werden benutzt, um Gewalt und Hass zu verbreiten.\nWir schützen dich und andere vor gefährlichen Inhalten.",
                "symbol": symbol,
                "law_reference": law_reference
            }
        else:
            # Unexpected format - log and fallback
            logger.warning(f"GPT-OSS returned unexpected format: {response[:100]}")
            return self.check_safety(text)
    
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

        # Check if translation is disabled
        if NO_TRANSLATE:
            # Skip translation entirely when NO_TRANSLATE is True
            translated_prompt = prompt
            logger.info("Translation disabled by NO_TRANSLATE flag, using original prompt")
        elif is_image_analysis:
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

    # ===== STREAMING METHODS (for text streaming feature) =====

    def _make_streaming_request(self, endpoint: str, payload: Dict[str, Any]):
        """
        Make streaming request to Ollama API
        Yields text chunks as they arrive from the API

        Args:
            endpoint: API endpoint path (e.g., "api/generate")
            payload: Request payload (Ollama format)

        Yields:
            Text chunks as they arrive from the API

        Raises:
            requests.exceptions.RequestException: If request fails
        """
        response = None
        try:
            # Enable streaming in payload
            payload["stream"] = True

            logger.info(f"Starting streaming request to {self.provider} at {self.base_url}/{endpoint}")

            response = requests.post(
                f"{self.base_url}/{endpoint}",
                json=payload,
                timeout=self.timeout,
                stream=True  # Enable response streaming
            )
            response.raise_for_status()

            # Iterate over response lines (newline-delimited JSON)
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        text_chunk = data.get("response", "")
                        done = data.get("done", False)

                        if text_chunk:
                            yield text_chunk

                        if done:
                            logger.info("Streaming completed successfully")
                            break
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to decode streaming response line: {e}")
                        continue

        except GeneratorExit:
            logger.info(f"Client disconnected from Ollama stream: {endpoint}")
            raise  # Propagate to caller for proper cleanup

        except requests.exceptions.RequestException as e:
            logger.error(f"Streaming request failed: {e}")
            raise

        finally:
            if response is not None:
                try:
                    response.close()
                    logger.debug(f"Ollama connection closed for {endpoint}")
                except Exception as e:
                    logger.warning(f"Failed to close Ollama connection: {e}")

    def translate_text_stream(self, text: str):
        """
        Stream translation of text to English using Ollama
        Yields text chunks as they are generated

        Args:
            text: Text to translate

        Yields:
            Text chunks as they are generated

        Raises:
            Exception: If streaming fails
        """
        prompt = TRANSLATION_PROMPT.format(text=text)

        payload = {
            "model": TRANSLATION_MODEL,
            "prompt": prompt,
            "keep_alive": "0s"
        }

        logger.info(f"Starting translation stream for text: {text[:50]}...")
        yield from self._make_streaming_request("api/generate", payload)

    def check_safety_gpt_oss_stream(self, text: str, keep_alive: str = "10m"):
        """
        Stream safety check using GPT-OSS-20b with §86a StGB compliance
        Yields text chunks as they are generated

        Note: Safety checks typically return short responses (SAFE/BLOCKED),
        so streaming may not provide significant UX benefit. This method is
        provided for consistency with other streaming methods.

        Args:
            text: Text to check (German or English)
            keep_alive: How long to keep model in VRAM (default: 10m)

        Yields:
            Text chunks as they are generated

        Raises:
            Exception: If streaming fails
        """
        prompt = f"Check this text for safety under §86a StGB:\n\n{text}"

        payload = {
            "model": GPT_OSS_MODEL,
            "prompt": prompt,
            "system": GPT_OSS_SAFETY_SYSTEM_PROMPT,
            "keep_alive": keep_alive
        }

        logger.info(f"Starting safety check stream for text: {text[:50]}...")
        yield from self._make_streaming_request("api/generate", payload)


# Create a singleton instance
ollama_service = OllamaService()
