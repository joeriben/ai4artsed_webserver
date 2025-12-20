"""
Prompt Interception Engine - Backend Proxy for Ollama/OpenRouter

ROLE: Backend proxy layer (NOT a chunk or pipeline)
- Routes requests to Ollama/OpenRouter APIs
- Handles model fallbacks and error recovery
- Called by BackendRouter for all Ollama/OpenRouter chunks

ARCHITECTURE:
  Chunk (manipulate.json)
    → ChunkBuilder → BackendRouter.route()
      → PromptInterceptionEngine (THIS) → Ollama/OpenRouter API

USAGE:
  1. backend_router.py:74 - Main routing (Ollama/OpenRouter backends)
  2. schema_pipeline_routes.py:1049 - Direct test endpoint

Migration der AI4ArtsEd Custom Node
Uses centralized ModelSelector for all model operations
"""

import os
import json
import requests
import re
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Import centralized model selector
from .model_selector import model_selector

@dataclass
class PromptInterceptionRequest:
    """Request für Prompt Interception Engine"""
    input_prompt: str
    input_context: str = ""
    style_prompt: str = ""
    model: str = "local/gemma2:9b"
    debug: bool = False
    unload_model: bool = False

@dataclass
class PromptInterceptionResponse:
    """Response von Prompt Interception Engine"""
    output_str: str
    output_float: float
    output_int: int
    output_binary: bool
    success: bool
    error: Optional[str] = None
    model_used: Optional[str] = None

class PromptInterceptionEngine:
    """
    Prompt Interception Engine - Zentrale KI-Request-Funktionalität
    Migration der ai4artsed_prompt_interception Custom Node
    Now uses centralized ModelSelector for all model operations
    """
    
    def __init__(self):
        # Use centralized model selector instead of local methods
        self.model_selector = model_selector
        self.openrouter_models = self.model_selector.get_openrouter_models()
        self.ollama_models = self.model_selector.get_ollama_models()
    
    def extract_model_name(self, full_model_string: str) -> str:
        """Extract model name using centralized selector"""
        return self.model_selector.extract_model_name(full_model_string)
    
    def build_full_prompt(self, input_prompt: str, input_context: str = "", style_prompt: str = "") -> str:
        """Baut vollständigen Prompt im Custom Node Format"""
        return (
            f"Task:\n{style_prompt.strip()}\n\n"
            f"Context:\n{input_context.strip()}\n"
            f"Prompt:\n{input_prompt.strip()}"
        )
    
    async def process_request(self, request: PromptInterceptionRequest) -> PromptInterceptionResponse:
        """Hauptmethode - Request verarbeiten"""
        try:
            # Full-Prompt erstellen
            full_prompt = self.build_full_prompt(
                request.input_prompt,
                request.input_context, 
                request.style_prompt
            )
            
            # Modellnamen extrahieren
            real_model_name = self.extract_model_name(request.model)
            
            # Backend-spezifische Verarbeitung (check fresh model lists)
            self.openrouter_models = self.model_selector.get_openrouter_models()
            self.ollama_models = self.model_selector.get_ollama_models()

            # Route based on provider prefix
            if request.model.startswith("bedrock/"):
                output_text, model_used = await self._call_aws_bedrock(
                    full_prompt, real_model_name, request.debug
                )
            elif request.model.startswith("anthropic/"):
                output_text, model_used = await self._call_anthropic(
                    full_prompt, real_model_name, request.debug
                )
            elif request.model.startswith("openai/"):
                output_text, model_used = await self._call_openai(
                    full_prompt, real_model_name, request.debug
                )
            elif request.model.startswith("mistral/"):
                output_text, model_used = await self._call_mistral(
                    full_prompt, real_model_name, request.debug
                )
            elif request.model.startswith("openrouter/") or real_model_name in self.openrouter_models:
                output_text, model_used = await self._call_openrouter(
                    full_prompt, real_model_name, request.debug
                )
            elif request.model.startswith("local/") or real_model_name in self.ollama_models:
                output_text, model_used = await self._call_ollama(
                    full_prompt, real_model_name, request.debug, request.unload_model
                )
            else:
                return PromptInterceptionResponse(
                    output_str="", output_float=0.0, output_int=0, output_binary=False,
                    success=False, error=f"Unbekanntes Modell-Format: {request.model}"
                )
            
            # Output-Formatierung (alle vier Formate)
            output_str, output_float, output_int, output_binary = self._format_outputs(output_text)
            
            return PromptInterceptionResponse(
                output_str=output_str,
                output_float=output_float,
                output_int=output_int,
                output_binary=output_binary,
                success=True,
                model_used=model_used
            )
            
        except Exception as e:
            logger.error(f"Prompt Interception Fehler: {e}")
            return PromptInterceptionResponse(
                output_str="", output_float=0.0, output_int=0, output_binary=False,
                success=False, error=str(e)
            )
    
    async def _call_openrouter(self, prompt: str, model: str, debug: bool) -> Tuple[str, str]:
        """OpenRouter API Call mit Fallback"""
        try:
            logger.info(f"[BACKEND] ☁️  OpenRouter Request: {model}")
            
            api_url, api_key = self._get_openrouter_credentials()
            
            if not api_key:
                raise Exception("OpenRouter API Key not configured")
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            # WICHTIG: OpenRouter-Modelle (speziell Gemma) ignorieren System-Messages oft
            # Daher: Kompletter Prompt als User-Message (wie Legacy Custom Node)
            messages = [
                {"role": "user", "content": prompt}
            ]
            payload = {
                "model": model,
                "messages": messages,
                "temperature": 0.7
            }

            response = requests.post(api_url, headers=headers, data=json.dumps(payload))
            if response.status_code == 200:
                result = response.json()
                output_text = result["choices"][0]["message"]["content"]
                logger.info(f"[BACKEND] ✅ OpenRouter Success: {model} ({len(output_text)} chars)")
                
                if debug:
                    self._log_debug("OpenRouter", model, prompt, output_text)
                
                return output_text, model
            else:
                raise Exception(f"API Error: {response.status_code}\n{response.text}")
                
        except Exception as e:
            if debug:
                logger.error(f"OpenRouter Modell {model} fehlgeschlagen: {e}")
            
            # Fallback versuchen
            fallback_model = self._find_openrouter_fallback(model, debug)
            if fallback_model != model:
                if debug:
                    logger.info(f"OpenRouter Fallback: {fallback_model}")
                return await self._call_openrouter(prompt, fallback_model, debug)
            else:
                raise e
    
    async def _call_ollama(self, prompt: str, model: str, debug: bool, unload_model: bool) -> Tuple[str, str]:
        """Ollama API Call mit Fallback"""
        try:
            logger.info(f"[BACKEND] 🏠 Ollama Request: {model}")
            
            # WICHTIG: Kein System-Prompt für Ollama
            # Der Prompt enthält bereits alle Instructions (Task/Context/Input)
            from config import OLLAMA_API_BASE_URL

            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }

            response = requests.post(f"{OLLAMA_API_BASE_URL}/api/generate", json=payload)
            
            if response.status_code == 200:
                output = response.json().get("response", "")
                if output:
                    logger.info(f"[BACKEND] ✅ Ollama Success: {model} ({len(output)} chars)")
                    if unload_model:
                        try:
                            unload_payload = {"model": model, "prompt": "", "keep_alive": 0, "stream": False}
                            requests.post(f"{OLLAMA_API_BASE_URL}/api/generate", json=unload_payload, timeout=30)
                        except:
                            pass

                    if debug:
                        self._log_debug("Ollama", model, prompt, output)

                    return output, model
            
            raise Exception(f"Ollama Error: {response.status_code}")
            
        except Exception as e:
            if debug:
                logger.error(f"Ollama Modell {model} fehlgeschlagen: {e}")
            
            # Fallback versuchen
            fallback_model = self._find_ollama_fallback(model, debug)
            if fallback_model and fallback_model != model:
                if debug:
                    logger.info(f"Ollama Fallback: {fallback_model}")
                return await self._call_ollama(prompt, fallback_model, debug, unload_model)
            else:
                raise e
    
    async def _call_anthropic(self, prompt: str, model: str, debug: bool) -> Tuple[str, str]:
        """Anthropic API Call (direct, DSGVO-compliant with EU region)"""
        try:
            logger.info(f"[BACKEND] ☁️  Anthropic Request: {model}")

            api_url, api_key = self._get_api_credentials("anthropic")

            if not api_key:
                raise Exception("Anthropic API Key not configured")

            headers = {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            }

            payload = {
                "model": model,
                "max_tokens": 4096,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }

            response = requests.post(api_url, headers=headers, data=json.dumps(payload))
            if response.status_code == 200:
                result = response.json()
                output_text = result["content"][0]["text"]
                logger.info(f"[BACKEND] ✅ Anthropic Success: {model} ({len(output_text)} chars)")

                if debug:
                    self._log_debug("Anthropic", model, prompt, output_text)

                return output_text, model
            else:
                raise Exception(f"API Error: {response.status_code}\n{response.text}")

        except Exception as e:
            logger.error(f"Anthropic API call failed: {e}")
            raise e

    async def _call_openai(self, prompt: str, model: str, debug: bool) -> Tuple[str, str]:
        """OpenAI API Call (direct)"""
        try:
            logger.info(f"[BACKEND] ☁️  OpenAI Request: {model}")

            api_url, api_key = self._get_api_credentials("openai")

            if not api_key:
                raise Exception("OpenAI API Key not configured")

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            messages = [
                {"role": "user", "content": prompt}
            ]
            payload = {
                "model": model,
                "messages": messages,
                "temperature": 0.7
            }

            response = requests.post(api_url, headers=headers, data=json.dumps(payload))
            if response.status_code == 200:
                result = response.json()
                output_text = result["choices"][0]["message"]["content"]
                logger.info(f"[BACKEND] ✅ OpenAI Success: {model} ({len(output_text)} chars)")

                if debug:
                    self._log_debug("OpenAI", model, prompt, output_text)

                return output_text, model
            else:
                raise Exception(f"API Error: {response.status_code}\n{response.text}")

        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise e

    async def _call_mistral(self, prompt: str, model: str, debug: bool) -> Tuple[str, str]:
        """Mistral AI API Call (direct, EU-based, DSGVO-compliant)"""
        try:
            logger.info(f"[BACKEND] ☁️  Mistral Request: {model}")

            api_url, api_key = self._get_api_credentials("mistral")

            if not api_key:
                raise Exception("Mistral API Key not configured")

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            messages = [
                {"role": "user", "content": prompt}
            ]

            # IMPORTANT: Remove 'mistral/' prefix before sending to API
            # Config uses "mistral/model-name" but API expects just "model-name"
            api_model = model.replace("mistral/", "") if model.startswith("mistral/") else model

            payload = {
                "model": api_model,
                "messages": messages,
                "temperature": 0.7
            }

            response = requests.post(api_url, headers=headers, data=json.dumps(payload))
            if response.status_code == 200:
                result = response.json()
                output_text = result["choices"][0]["message"]["content"]
                logger.info(f"[BACKEND] ✅ Mistral Success: {model} ({len(output_text)} chars)")

                if debug:
                    self._log_debug("Mistral", model, prompt, output_text)

                return output_text, model
            else:
                raise Exception(f"API Error: {response.status_code}\n{response.text}")

        except Exception as e:
            logger.error(f"Mistral API call failed: {e}")
            raise e

    async def _call_aws_bedrock(self, prompt: str, model: str, debug: bool) -> Tuple[str, str]:
        """AWS Bedrock API Call for Anthropic Claude (EU region: eu-central-1)

        IMPORTANT:
        - Credentials loaded from environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
        - Region: eu-central-1
        - Model ID must be exact Bedrock model ID (e.g., eu.anthropic.claude-sonnet-4-5-20250929-v1:0)
        """
        try:
            logger.info(f"[BACKEND] ☁️  AWS Bedrock Request: {model}")

            # Import boto3 (AWS SDK)
            try:
                import boto3
            except ImportError:
                raise Exception("boto3 not installed. Run: pip install boto3")

            # Create Bedrock Runtime client
            # boto3 automatically loads credentials from environment:
            # - AWS_ACCESS_KEY_ID
            # - AWS_SECRET_ACCESS_KEY
            # - AWS_SESSION_TOKEN (optional)
            bedrock = boto3.client(
                service_name="bedrock-runtime",
                region_name="eu-central-1"
            )

            # Model ID is used as-is (exact Bedrock model ID)
            # Example: eu.anthropic.claude-sonnet-4-5-20250929-v1:0
            bedrock_model_id = model

            # Build request body (Anthropic Messages API format)
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }

            # Call Bedrock
            response = bedrock.invoke_model(
                modelId=bedrock_model_id,
                body=json.dumps(request_body)
            )

            # Parse response
            response_body = json.loads(response['body'].read())
            output_text = response_body['content'][0]['text']

            logger.info(f"[BACKEND] ✅ AWS Bedrock Success: {model} ({len(output_text)} chars)")

            if debug:
                self._log_debug("AWS Bedrock", model, prompt, output_text)

            return output_text, model

        except Exception as e:
            logger.error(f"AWS Bedrock API call failed: {e}")
            raise e

    def _get_api_credentials(self, provider: str) -> Tuple[str, str]:
        """Get API credentials for any provider (openrouter, anthropic, openai)

        Args:
            provider: Provider name ("openrouter", "anthropic", "openai")

        Returns:
            Tuple of (api_url, api_key)
        """
        # Provider-specific configuration
        provider_config = {
            "openrouter": {
                "url": "https://openrouter.ai/api/v1/chat/completions",
                "key_file": "openrouter.key",
                "env_var": "OPENROUTER_API_KEY",
                "key_prefix": "sk-or-"
            },
            "anthropic": {
                "url": "https://api.anthropic.com/v1/messages",
                "key_file": "anthropic.key",
                "env_var": "ANTHROPIC_API_KEY",
                "key_prefix": "sk-ant-"
            },
            "openai": {
                "url": "https://api.openai.com/v1/chat/completions",
                "key_file": "openai.key",
                "env_var": "OPENAI_API_KEY",
                "key_prefix": "sk-"
            },
            "mistral": {
                "url": "https://api.mistral.ai/v1/chat/completions",
                "key_file": "mistral.key",
                "env_var": "MISTRAL_API_KEY",
                "key_prefix": ""
            }
        }

        if provider not in provider_config:
            logger.error(f"Unknown provider: {provider}")
            return "", ""

        config = provider_config[provider]
        api_url = config["url"]

        # 1. Try Environment Variable
        api_key = os.environ.get(config["env_var"], "")
        if api_key:
            logger.debug(f"{provider.title()} API Key from environment variable")
            return api_url, api_key

        # 2. Try Key-File (devserver/{provider}.key)
        try:
            # Relative to devserver root
            key_file = Path(__file__).parent.parent.parent / config["key_file"]
            if key_file.exists():
                # Read file and skip comment lines
                lines = key_file.read_text().strip().split('\n')
                api_key = None
                for line in lines:
                    line = line.strip()
                    # Skip empty lines and comments
                    if line and not line.startswith('#') and not line.startswith('//'):
                        # Check if this looks like a valid API key for this provider
                        if line.startswith(config["key_prefix"]) or line.startswith("sk-"):
                            api_key = line
                            break

                if api_key:
                    logger.info(f"{provider.title()} API Key loaded from {key_file.name}")
                    return api_url, api_key
                else:
                    logger.error(f"No valid API key found in {key_file} (looking for keys starting with '{config['key_prefix']}')")
            else:
                logger.debug(f"{provider.title()} key file not found: {key_file}")
        except Exception as e:
            logger.warning(f"Failed to read {config['key_file']}: {e}")

        # 3. No key found
        logger.error(f"{provider.title()} API Key not found! Set {config['env_var']} environment variable or create devserver/{config['key_file']} file")
        return api_url, ""

    def _get_openrouter_credentials(self) -> Tuple[str, str]:
        """OpenRouter Credentials - Legacy wrapper for backward compatibility"""
        return self._get_api_credentials("openrouter")
    
    def _find_openrouter_fallback(self, failed_model: str, debug: bool) -> str:
        """Use centralized OpenRouter fallback logic"""
        return self.model_selector.find_openrouter_fallback(failed_model, debug)
    
    def _find_ollama_fallback(self, failed_model: str, debug: bool) -> Optional[str]:
        """Use centralized Ollama fallback logic"""
        return self.model_selector.find_ollama_fallback(failed_model, debug)
    
    def _format_outputs(self, output_text: str) -> Tuple[str, float, int, bool]:
        """Formatiert Output in alle vier Rückgabeformate (Custom Node Logic)"""
        output_str = output_text.strip()
        
        # Pattern für Zahlen-Extraktion
        german_pattern = r"[-+]?\d{1,3}(?:\.\d{3})*,\d+"
        english_pattern = r"[-+]?\d*\.\d+"
        int_pattern = r"[-+]?\d+"
        
        # Float-Extraktion
        m = re.search(german_pattern, output_str)
        if m:
            num = m.group().replace(".", "").replace(",", ".")
            try:
                output_float = float(num)
            except:
                output_float = 0.0
        else:
            m = re.search(english_pattern, output_str)
            if m:
                try:
                    output_float = float(m.group())
                except:
                    output_float = 0.0
            else:
                m = re.search(int_pattern, output_str)
                if m:
                    try:
                        output_float = float(m.group())
                    except:
                        output_float = 0.0
                else:
                    output_float = 0.0
        
        # Int-Extraktion
        m_int = re.search(int_pattern, output_str)
        if m_int:
            try:
                output_int = int(round(float(m_int.group())))
            except:
                output_int = 0
        else:
            output_int = 0
        
        # Binary-Extraktion
        lower = output_str.lower()
        num_match = re.search(english_pattern, output_str) or re.search(int_pattern, output_str)
        if ("true" in lower or re.search(r"\b1\b", lower) or 
            (num_match and float(num_match.group()) != 0)):
            output_binary = True
        else:
            output_binary = False
        
        return output_str, output_float, output_int, output_binary
    
    def _log_debug(self, backend: str, model: str, prompt: str, output: str):
        """Debug-Logging im Custom Node Format"""
        logger.info(f"\n{'='*60}")
        logger.info(f">>> AI4ARTSED PROMPT INTERCEPTION ENGINE <<<")
        logger.info(f"{'='*60}")
        logger.info(f"Backend: {backend}")
        logger.info(f"Model: {model}")
        logger.info(f"-" * 40)
        logger.info(f"Prompt sent:\n{prompt}")
        logger.info(f"-" * 40)
        logger.info(f"Response received:\n{output}")
        logger.info(f"{'='*60}")

# Singleton-Instanz
engine = PromptInterceptionEngine()
