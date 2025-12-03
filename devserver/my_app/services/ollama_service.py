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

    def analyze_image_pedagogical(self, image_data: str, original_prompt: str, safety_level: str = 'youth', language: str = 'en') -> Dict[str, Any]:
        """
        Stage 5: Pedagogical image analysis using LLaVA (llama3.2-vision)

        Analyzes AI-generated image with focus on pedagogical reflection and learning outcomes.

        Args:
            image_data: Base64 encoded image data
            original_prompt: Original prompt used to generate the image
            safety_level: Safety level ('kids', 'youth', 'open') for age-appropriate language
            language: Output language ('en', 'de', etc.) - respects i18n

        Returns:
            Dictionary with:
            - 'analysis': str (Full analysis text in specified language)
            - 'reflection_prompts': List[str] (3-5 conversation starters)
            - 'insights': List[str] (Key themes/techniques identified)
            - 'success': bool
        """
        # Remove data URL prefix if present
        if ',' in image_data:
            image_data = image_data.split(',', 1)[-1]

        # Age-appropriate language based on safety level
        age_mapping = {
            'kids': ('8-12', 'children', 'Kinder'),
            'youth': ('13-17', 'teenagers', 'Jugendliche'),
            'open': ('16-18', 'young adults', 'junge Erwachsene')
        }
        age_range_en, audience_en, audience_de = age_mapping.get(safety_level, ('8-17', 'students', 'Schüler'))

        # Language-specific prompts
        if language == 'de':
            pedagogical_prompt = f"""Du analysierst ein KI-generiertes Bild, das von einem Schüler (Alter: {age_range_en} Jahren) im Kunstunterricht erstellt wurde.

ORIGINAL SCHÜLER-PROMPT: "{original_prompt}"

Erstelle eine strukturierte Analyse nach diesem Schema:

1. MATERIELLE UND MEDIALE EIGENSCHAFTEN
   - Identifiziere den KI-Generierungsstil und visuelle Charakteristika
   - Beschreibe die technische Umsetzung (Rendering, Textur, Beleuchtung)

2. VORIKONOGRAPHISCHE BESCHREIBUNG
   - Beschreibe ALLE sichtbaren Elemente: Objekte, Figuren, Räumlichkeit
   - Analysiere Komposition, Farbgebung, Texturen, räumliche Beziehungen
   - Beschreibe Perspektive und visuelle Struktur

3. IKONOGRAPHISCHE ANALYSE
   - Interpretiere symbolische Bedeutungen und künstlerische Techniken
   - Erkläre, wie die KI den Schüler-Prompt interpretiert hat
   - Identifiziere künstlerische Stile oder Referenzen

4. IKONOLOGISCHE INTERPRETATION
   - Reflektiere, wie die KI die kreative Vision des Schülers umgesetzt hat
   - Diskutiere kulturelle und konzeptuelle Bedeutungen
   - Bewerte die Beziehung zwischen Prompt und visueller Umsetzung

5. PÄDAGOGISCHE REFLEXIONSFRAGEN
   Generiere 3-5 konkrete Gesprächsanregungen:
   - Fragen zu kreativen Entscheidungen und Intentionen
   - Fragen zur KI-Interpretation des Prompts
   - Fragen zu künstlerischen Techniken und Konzepten
   - Fragen zu möglichen Verbesserungen oder Experimenten

KRITISCHE REGELN:
- Schreibe auf Deutsch
- Verwende deklarative Sprache (als Fakten formulieren, nicht als Möglichkeiten)
- Fokus auf Lernmöglichkeiten, nicht auf Kritik
- Keine Phrasen wie "möglicherweise", "könnte sein", "schwer zu bestimmen"
- Generiere spezifische, umsetzbare Reflexionsfragen

FORMATIERUNG FÜR REFLEXIONSFRAGEN:
Am Ende der Analyse füge einen eigenen Abschnitt hinzu:

REFLEXIONSFRAGEN:
- [Konkrete Frage 1]
- [Konkrete Frage 2]
- [Konkrete Frage 3]
- [...]
"""
        else:  # English
            pedagogical_prompt = f"""You are analyzing an AI-generated image created by a student (age: {age_range_en}) in an arts education context.

ORIGINAL STUDENT PROMPT: "{original_prompt}"

Provide a structured analysis following this framework:

1. MATERIAL AND MEDIAL PROPERTIES
   - Identify the AI generation style and visual characteristics
   - Describe the technical implementation (rendering, texture, lighting)

2. PRE-ICONOGRAPHIC DESCRIPTION
   - Describe ALL visible elements: objects, figures, spatial relationships
   - Analyze composition, color palette, textures, spatial structure
   - Describe perspective and visual organization

3. ICONOGRAPHIC ANALYSIS
   - Interpret symbolic meanings and artistic techniques
   - Explain how the AI interpreted the student's prompt
   - Identify artistic styles or references

4. ICONOLOGICAL INTERPRETATION
   - Reflect on how the AI realized the student's creative vision
   - Discuss cultural and conceptual meanings
   - Evaluate the relationship between prompt and visual output

5. PEDAGOGICAL REFLECTION QUESTIONS
   Generate 3-5 specific conversation prompts:
   - Questions about creative decisions and intentions
   - Questions about the AI's interpretation
   - Questions about artistic techniques and concepts
   - Questions about possible improvements or experiments

CRITICAL RULES:
- Write in English
- Use declarative language (state as facts, not possibilities)
- Focus on learning opportunities, not critique
- No phrases like "possibly", "might be", "difficult to determine"
- Generate specific, actionable reflection questions

FORMATTING FOR REFLECTION QUESTIONS:
At the end of the analysis, add a dedicated section:

REFLECTION QUESTIONS:
- [Specific question 1]
- [Specific question 2]
- [Specific question 3]
- [...]
"""

        try:
            from config import IMAGE_ANALYSIS_MODEL

            payload = {
                "model": IMAGE_ANALYSIS_MODEL,
                "prompt": pedagogical_prompt,
                "images": [image_data],
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 2000  # Allow longer responses for detailed analysis
                },
                "keep_alive": "0s"  # Unload model after use (save VRAM)
            }

            logger.info(f"[STAGE 5] Sending image to {IMAGE_ANALYSIS_MODEL} for pedagogical analysis (language: {language})")
            result = self._make_request("api/generate", payload)

            if not result:
                return {
                    'analysis': '',
                    'reflection_prompts': [],
                    'insights': [],
                    'success': False,
                    'error': 'Ollama request failed'
                }

            analysis_text = result.get("response", "").strip()

            if not analysis_text:
                return {
                    'analysis': '',
                    'reflection_prompts': [],
                    'insights': [],
                    'success': False,
                    'error': 'Empty analysis response'
                }

            logger.info(f"[STAGE 5] Analysis complete: {len(analysis_text)} chars")

            # Extract reflection prompts from analysis
            reflection_prompts = self._extract_reflection_prompts(analysis_text, language)

            # Extract key insights (optional, for tag display)
            insights = self._extract_insights(analysis_text, language)

            return {
                'analysis': analysis_text,
                'reflection_prompts': reflection_prompts,
                'insights': insights,
                'success': True
            }

        except Exception as e:
            logger.error(f"[STAGE 5] Pedagogical analysis error: {e}")
            import traceback
            traceback.print_exc()
            return {
                'analysis': '',
                'reflection_prompts': [],
                'insights': [],
                'success': False,
                'error': str(e)
            }

    def _extract_reflection_prompts(self, analysis_text: str, language: str = 'en') -> list:
        """
        Extract reflection prompts from analysis text

        Looks for section starting with "REFLEXIONSFRAGEN:" (DE) or "REFLECTION QUESTIONS:" (EN)
        and extracts bullet points.

        Args:
            analysis_text: Full analysis text from vision model
            language: Output language for fallback prompts

        Returns:
            List of reflection prompts (strings)
        """
        prompts = []

        # Find section header based on language
        section_header = "REFLEXIONSFRAGEN:" if language == 'de' else "REFLECTION QUESTIONS:"

        if section_header in analysis_text:
            # Split at section header
            parts = analysis_text.split(section_header, 1)
            if len(parts) > 1:
                questions_section = parts[1].strip()

                # Extract bullet points (lines starting with - or •)
                lines = questions_section.split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith('-') or line.startswith('•'):
                        # Remove bullet point prefix
                        question = line.lstrip('-•').strip()
                        if question:
                            prompts.append(question)

        # Fallback: If no section found, generate generic prompts
        if not prompts:
            logger.warning("[STAGE 5] No reflection prompts found in analysis, using fallback")
            if language == 'de':
                prompts = [
                    "Was war deine Hauptidee bei diesem Bild?",
                    "Hat die KI deinen Prompt so umgesetzt, wie du es dir vorgestellt hast?",
                    "Welche künstlerischen Techniken oder Stile siehst du in dem Bild?",
                    "Was würdest du beim nächsten Mal anders machen?"
                ]
            else:
                prompts = [
                    "What was your main idea for this image?",
                    "Did the AI implement your prompt as you imagined?",
                    "What artistic techniques or styles do you see in the image?",
                    "What would you do differently next time?"
                ]

        return prompts

    def _extract_insights(self, analysis_text: str, language: str = 'en') -> list:
        """
        Extract key insights/themes from analysis for tag display

        Simple keyword extraction looking for art historical terms.

        Args:
            analysis_text: Full analysis text
            language: Analysis language (for keyword matching)

        Returns:
            List of short insight tags (max 5)
        """
        insights = []

        # Language-specific keywords
        if language == 'de':
            keywords = [
                'Perspektive', 'Komposition', 'Farbgebung', 'Symbolik',
                'Realismus', 'Abstraktion', 'Surrealismus', 'Expressionismus',
                'Licht und Schatten', 'Textur', 'Räumlichkeit', 'Figur',
                'Landschaft', 'Portrait', 'Stillleben', 'Fantasy'
            ]
        else:
            keywords = [
                'Perspective', 'Composition', 'Color', 'Symbolism',
                'Realism', 'Abstraction', 'Surrealism', 'Expressionism',
                'Light and Shadow', 'Texture', 'Spatiality', 'Figure',
                'Landscape', 'Portrait', 'Still Life', 'Fantasy'
            ]

        text_lower = analysis_text.lower()
        for keyword in keywords:
            if keyword.lower() in text_lower:
                insights.append(keyword)
                if len(insights) >= 5:
                    break

        return insights

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


# Create a singleton instance
ollama_service = OllamaService()
