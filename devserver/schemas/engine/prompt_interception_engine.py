"""
Prompt Interception Engine - Migration der AI4ArtsEd Custom Node
Zentrale KI-Request-Funktionalität mit Multi-Backend und Fallback-System
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
    """
    
    def __init__(self):
        self.openrouter_models = self._get_openrouter_models()
        self.ollama_models = self._get_ollama_models()
        
    def _get_openrouter_models(self) -> Dict[str, Dict[str, str]]:
        """OpenRouter Modelle mit Metadaten"""
        return {
            "anthropic/claude-3.5-haiku": {"price": "$0.80/$4.00", "tag": "multilingual"},
            "anthropic/claude-3-haiku": {"price": "$0.80/$4.00", "tag": "multilingual"},
            "deepseek/deepseek-chat-v3-0324": {"price": "$0.27/$1.10", "tag": "rule-oriented"},
            "deepseek/deepseek-r1-0528": {"price": "$0.50/$2.15", "tag": "reasoning"},
            "google/gemini-2.5-flash": {"price": "$0.20/$2.50", "tag": "multilingual"},
            "google/gemma-3-27b-it": {"price": "$0.10/$0.18", "tag": "translator"},
            "meta-llama/llama-3.3-70b-instruct": {"price": "$0.59/$0.79", "tag": "rule-oriented"},
            "meta-llama/llama-guard-3-8b": {"price": "$0.05/$0.10", "tag": "rule-oriented"},
            "meta-llama/llama-3.2-1b-instruct": {"price": "$0.05/$0.10", "tag": "reasoning"},
            "mistralai/mistral-medium-3": {"price": "$0.40/$2.00", "tag": "reasoning"},
            "mistralai/mistral-small-3.1-24b-instruct": {"price": "$0.10/$0.30", "tag": "rule-oriented, vision"},
            "mistralai/mistral-nemo": {"price": "$0.01/$0.001", "tag": "multilingual"},
            "mistralai/ministral-8b": {"price": "$0.05/$0.10", "tag": "rule-oriented"},
            "mistralai/ministral-3b": {"price": "$0.05/$0.10", "tag": "rule-oriented"},
            "mistralai/mixtral-8x7b-instruct": {"price": "$0.45/$0.70", "tag": "cultural-expert"},
            "qwen/qwen3-32b": {"price": "$0.10/$0.30", "tag": "translator"},
        }
    
    def _get_ollama_models(self) -> List[str]:
        """Verfügbare Ollama Modelle abrufen"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            response.raise_for_status()
            return [m.get('name', '') for m in response.json().get("models", [])]
        except Exception:
            return []
    
    def extract_model_name(self, full_model_string: str) -> str:
        """Extrahiert echten Modellnamen aus Dropdown-Format"""
        if full_model_string.startswith("openrouter/"):
            without_prefix = full_model_string[11:]
            return without_prefix.split(" [")[0]
        elif full_model_string.startswith("local/"):
            without_prefix = full_model_string[6:]
            return without_prefix.split(" [")[0]
        else:
            return full_model_string
    
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
            
            # Backend-spezifische Verarbeitung
            if request.model.startswith("openrouter/") or real_model_name in self.openrouter_models:
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
            
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            messages = [
                {"role": "system", "content": "You are a fresh assistant instance. Forget all previous conversation history."},
                {"role": "user", "content": prompt}
            ]
            payload = {"model": model, "messages": messages, "temperature": 0.7}

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
            
            payload = {
                "model": model,
                "prompt": prompt,
                "system": "You are a fresh assistant instance. Forget all previous conversation history.",
                "stream": False
            }

            response = requests.post("http://localhost:11434/api/generate", json=payload)
            
            if response.status_code == 200:
                output = response.json().get("response", "")
                if output:
                    logger.info(f"[BACKEND] ✅ Ollama Success: {model} ({len(output)} chars)")
                    if unload_model:
                        try:
                            unload_payload = {"model": model, "prompt": "", "keep_alive": 0, "stream": False}
                            requests.post("http://localhost:11434/api/generate", json=unload_payload, timeout=30)
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
    
    def _get_openrouter_credentials(self) -> Tuple[str, str]:
        """OpenRouter Credentials aus Environment oder Key-File"""
        api_url = "https://openrouter.ai/api/v1/chat/completions"
        
        # 1. Try Environment Variable
        api_key = os.environ.get("OPENROUTER_API_KEY", "")
        if api_key:
            logger.debug("OpenRouter API Key from environment variable")
            return api_url, api_key
        
        # 2. Try Key-File (devserver/openrouter.key)
        try:
            # Relative to devserver root
            key_file = Path(__file__).parent.parent.parent / "openrouter.key"
            if key_file.exists():
                api_key = key_file.read_text().strip()
                # Validate key format (OpenRouter keys start with "sk-or-")
                if api_key and api_key.startswith("sk-or-"):
                    logger.info(f"OpenRouter API Key loaded from {key_file}")
                    return api_url, api_key
                elif api_key:
                    logger.error(f"Invalid OpenRouter API key format in {key_file} (must start with 'sk-or-')")
        except Exception as e:
            logger.warning(f"Failed to read openrouter.key: {e}")
        
        # 3. No key found
        logger.error("OpenRouter API Key not found! Set OPENROUTER_API_KEY environment variable or create devserver/openrouter.key file")
        return api_url, ""
    
    def _find_openrouter_fallback(self, failed_model: str, debug: bool) -> str:
        """Fallback für OpenRouter Modelle"""
        # Simplified fallback logic
        fallbacks = [
            "anthropic/claude-3.5-haiku",
            "meta-llama/llama-3.2-1b-instruct",
            "mistralai/ministral-8b"
        ]
        
        for fallback in fallbacks:
            if fallback in self.openrouter_models and fallback != failed_model:
                return fallback
        
        return "anthropic/claude-3-haiku"
    
    def _find_ollama_fallback(self, failed_model: str, debug: bool) -> Optional[str]:
        """Fallback für Ollama Modelle"""
        available_models = self._get_ollama_models()
        if not available_models:
            return None
        
        # Präferierte Fallbacks
        preferred = ["gemma2:9b", "llama3.2:1b", "llama3.1:8b"]
        for pref in preferred:
            if pref in available_models and pref != failed_model:
                return pref
        
        # Erstes verfügbares Modell
        return available_models[0] if available_models else None
    
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
