"""
Central configuration file for the AI4ArtsEd Web Server

ADMIN: Adjust settings in the "MAIN CONFIGURATION" section below!
"""
import os
from pathlib import Path

# ============================================================================
# ============================================================================
# MAIN CONFIGURATION - ADMIN: CHANGE THESE SETTINGS
# ============================================================================
# ============================================================================

# ----------------------------------------------------------------------------
# 1. USER INTERFACE MODE
# ----------------------------------------------------------------------------
# Controls interface complexity based on target age group:
#
# "kids" (ages 8-12):
#   - Simple, separated phases: Transform → See result → Choose medium → Generate
#   - Minimal technical details, focus on creative output
#   - Clear visual feedback: "⚙️ KI arbeitet..."
#
# "youth" (ages 13-17):
#   - Educational flow with pipeline visualization: 💡→📝→🎨→🖼️→✅
#   - Shows HOW AI processes work (transparency)
#   - Promotes technical understanding
#
# "expert" (teachers/developers):
#   - Full debug mode with all metadata
#   - JSON outputs, timing data, error details
#   - Complete transparency for analysis
#
UI_MODE = "youth"  # ADMIN: Change to "kids", "youth", or "expert"

# ----------------------------------------------------------------------------
# 2. SAFETY LEVEL (Content Filtering)
# ----------------------------------------------------------------------------
# Controls what content is blocked in generated images/media
# This is SEPARATE from UI_MODE (interface complexity)
#
# "kids": Maximum filtering (ages 8-12)
#   - Blocks: violence, horror, scary, sexual, explicit content
#   - Use for: Elementary school, young children
#
# "youth": Moderate filtering (ages 13-17)
#   - Blocks: explicit sexual, extreme violence, self-harm
#   - Allows: Mild scary themes, educational anatomy
#   - Use for: Secondary school, teenagers
#
# "adult": Minimal filtering (18+)
#   - Blocks: Only illegal content (§86a StGB - Nazi symbols, etc.)
#   - Allows: Artistic nudity, mature themes
#   - Use for: Art education, professional contexts
#
# "off": No content filtering (DEVELOPMENT ONLY)
#   - No automatic blocking
#   - Only use for testing/debugging!
#
DEFAULT_SAFETY_LEVEL = "youth"  # ADMIN: Change to "kids", "youth", "adult", or "off"

# ----------------------------------------------------------------------------
# 2b. DEFAULT INTERCEPTION CONFIG
# ----------------------------------------------------------------------------
# Default config for Stage 2 Prompt Interception when none is specified
# "user_defined" = neutral passthrough (empty context = no AI transformation)
# This allows users to have full control without unexpected transformations
DEFAULT_INTERCEPTION_CONFIG = "user_defined"  # ADMIN: Change to any interception config name

# ----------------------------------------------------------------------------
# 3. SERVER SETTINGS
# ----------------------------------------------------------------------------
HOST = "0.0.0.0"
PORT = 17802  # Development: 17802, Production: 17801
THREADS = 8

# ----------------------------------------------------------------------------
# 4. LANGUAGE
# ----------------------------------------------------------------------------
# Default language for interface (users can change this)
DEFAULT_LANGUAGE = "de"  # "de" or "en"

# ----------------------------------------------------------------------------
# 5. MODEL CONFIGURATION (Per-Stage LLM Selection)
# ----------------------------------------------------------------------------
# REPLACES: Old execution_mode="eco"/"fast" system (deprecated in Session 55)
# NEW: Direct per-stage model configuration - admin controls exactly which model each stage uses
#
# Configure which models are used in each pipeline stage.
# Chunks reference these variables by name (e.g., "model": "STAGE2_MODEL")
#
# Provider Prefix Format & DSGVO Compliance:
#   - "local/model-name" → Ollama (local inference, DSGVO-compliant ✓)
#   - "bedrock/model-name" → AWS Bedrock with Anthropic (EU region, DSGVO-compliant ✓)
#   - "mistral/model-name" → Mistral AI API direct (EU-based, DSGVO-compliant ✓)
#   - "anthropic/model-name" → Anthropic API direct (NOT DSGVO-compliant ✗)
#   - "openai/model-name" → OpenAI API direct (US-based, NOT DSGVO-compliant ✗)
#   - "openrouter/provider/model-name" → OpenRouter aggregator (US proxy, NOT DSGVO-compliant ✗)
#
# IMPORTANT: OpenRouter routes through US servers even for EU models!
# For DSGVO compliance with cloud AI, use AWS Bedrock (bedrock/) or Mistral AI (mistral/).
#
# Base Models:
LOCAL_DEFAULT_MODEL = "local/gpt-OSS:20b"                    # Default local text model (24GB VRAM)
LOCAL_VISION_MODEL = "local/llama3.2-vision:latest"                # Local vision model
REMOTE_MULTIMODAL_MODEL = "openrouter/google/gemini-2.5-flash-lite"     # Input Modalitiestext, image, file, audio, video
REMOTE_SMALL_MODEL = "openrouter/mistralai/mistral-nemo"       # Fast, cheap cloud model
REMOTE_LIGHT_MODEL = "openrouter/mistralai/mistral-medium-3.1"       # Fast, cheap cloud model
REMOTE_FAST_MODEL = "bedrock/eu.anthropic.claude-haiku-4-5-20251001-v1:0"       # Fast, cheap cloud (AWS Bedrock EU, DSGVO ✓, Haiku 4.5)
REMOTE_ADVANCED_MODEL = "bedrock/eu.anthropic.claude-sonnet-4-5-20250929-v1:0"  # High-quality cloud (AWS Bedrock EU, DSGVO ✓, Sonnet 4.5)
REMOTE_EXTREME_MODEL = "bedrock/eu.anthropic.claude-opus-4-5-20251101-v2:0"  # Highest-quality cloud, VERY EXPENSIVE!

# Stage-Specific Models (Default to LOCAL for 24GB VRAM systems):
STAGE1_TEXT_MODEL = LOCAL_DEFAULT_MODEL                   # Stage 1: conditional safety checks (simple task)
STAGE1_VISION_MODEL = LOCAL_VISION_MODEL                  # Stage 1: Image analysis
STAGE2_INTERCEPTION_MODEL = LOCAL_DEFAULT_MODEL           # Stage 2: Prompt interception (complex task)
STAGE2_OPTIMIZATION_MODEL = LOCAL_DEFAULT_MODEL           # Stage 2: Prompt optimization (complex task)
STAGE3_MODEL = LOCAL_DEFAULT_MODEL                        # Stage 3: Translation and final safety check (simple task)
STAGE4_LEGACY_MODEL = LOCAL_DEFAULT_MODEL                 # For legacy workflow execution
CHAT_HELPER_MODEL = LOCAL_DEFAULT_MODEL                   # Chat overlay: Interactive help system

# Legacy Model Configuration
GPT_OSS_MODEL = "gpt-OSS:20b"  # openai/gpt-oss-safeguard-20b via Ollama
ANALYSIS_MODEL = "local/llama3.2-vision:latest"
TRANSLATION_MODEL = GPT_OSS_MODEL  # GPT-OSS replaces mistral-nemo
SAFETY_MODEL = GPT_OSS_MODEL

# Stage 5: Image Analysis (Reflexions-Stage) - Post-Generation Analysis
IMAGE_ANALYSIS_MODEL = "local/llama3.2-vision:latest"  # Reuses existing LLaVA model for pedagogical image analysis

# Stage 5: Image Analysis Prompts (4 Theoretical Frameworks)
IMAGE_ANALYSIS_PROMPTS = {
    'bildwissenschaftlich': {
        # Panofsky - Art-historical analysis (4-stage iconological method)
        'de': """Du analysierst ein KI-generiertes Bild im Kunstunterricht.

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
   - Identifiziere künstlerische Stile oder Referenzen

4. IKONOLOGISCHE INTERPRETATION
   - Diskutiere kulturelle und konzeptuelle Bedeutungen
   - Reflektiere über die visuelle Umsetzung

5. PÄDAGOGISCHE REFLEXIONSFRAGEN
   Generiere 3-5 konkrete Gesprächsanregungen:
   - Fragen zu kreativen Entscheidungen
   - Fragen zu künstlerischen Techniken und Konzepten
   - Fragen zu möglichen Experimenten

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
- [...]""",
        'en': """You are analyzing an AI-generated image in an arts education context.

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
   - Identify artistic styles or references

4. ICONOLOGICAL INTERPRETATION
   - Discuss cultural and conceptual meanings
   - Reflect on the visual realization

5. PEDAGOGICAL REFLECTION QUESTIONS
   Generate 3-5 specific conversation prompts:
   - Questions about creative decisions
   - Questions about artistic techniques and concepts
   - Questions about possible experiments

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
- [...]"""
    },

    'bildungstheoretisch': {
        # Jörissen/Marotzki - Analysis of educational potentials (Bildungspotenziale)
        'de': """TODO: User provides prompt for bildungstheoretisch analysis (DE)
Jörissen/Marotzki framework - Analyse von Bildungspotenzialen""",
        'en': """TODO: User provides prompt for bildungstheoretisch analysis (EN)
Jörissen/Marotzki framework - Analysis of educational potentials"""
    },

    'ethisch': {
        # Ethical analysis (see legacy → ethical advisor)
        'de': """TODO: User provides prompt for ethisch analysis (DE)
Ethische Bildanalyse""",
        'en': """TODO: User provides prompt for ethisch analysis (EN)
Ethical image analysis"""
    },

    'kritisch': {
        # Decolonial & critical media studies
        'de': """TODO: User provides prompt for kritisch analysis (DE)
Dekoloniale & kritische Medienwissenschaft""",
        'en': """TODO: User provides prompt for kritisch analysis (EN)
Decolonial & critical media studies"""
    }
}

# Note: Stage 4 (output generation) models are defined in output configs (SD3.5, FLUX, etc.)

# ============================================================================
# END OF MAIN CONFIGURATION
# ============================================================================
# Technical settings below - only change if you know what you're doing!
# ============================================================================

# Base paths
THIS_FILE = Path(__file__).resolve()
BASE_DIR = THIS_FILE.parent.parent
LOCAL_WORKFLOWS_DIR = BASE_DIR / "workflows"
PUBLIC_DIR = Path(__file__).parent.parent / "public" / "ai4artsed-frontend" / "dist"
EXPORTS_DIR = BASE_DIR / "exports"
JSON_STORAGE_DIR = EXPORTS_DIR / "json"
UPLOADS_TMP_DIR = EXPORTS_DIR / "uploads_tmp"  # Temporary image uploads for img2img

# API Configuration
# LLM Provider: "ollama" or "lmstudio"
# TODO 2026: Refactor to Option C (Adapter Pattern with LLMProvider base class)
# NOTE: LM Studio does NOT support model unloading via API - use Ollama for proper VRAM management
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "ollama")  # Ollama supports keep_alive for VRAM management
OLLAMA_API_BASE_URL = os.environ.get("OLLAMA_API_BASE_URL", "http://localhost:11434")
LMSTUDIO_API_BASE_URL = os.environ.get("LMSTUDIO_API_BASE_URL", "http://localhost:1234")

# External LLM Provider for cloud-based models
# Options: "none", "openrouter", "anthropic", "openai", "mistral"
EXTERNAL_LLM_PROVIDER = os.environ.get("EXTERNAL_LLM_PROVIDER", "none")

# DSGVO Conformity - determines if cloud services are allowed
# True = DSGVO-compliant (no cloud services), False = Cloud services allowed
DSGVO_CONFORMITY = os.environ.get("DSGVO_CONFORMITY", "true").lower() == "true"
COMFYUI_PREFIX = "comfyui"
COMFYUI_PORT = "7821"  # SwarmUI integrated ComfyUI (RTX 5090 compatible)
SWARMUI_API_PORT = "7801"  # SwarmUI REST API (proper image generation endpoint)

# SwarmUI Orchestration Configuration
# "Single Front Door" Architecture (Port 7801 for everything)
USE_SWARMUI_ORCHESTRATION = True  # Default: Route all workflows via SwarmUI
ALLOW_DIRECT_COMFYUI = False      # Emergency only: Allow direct access to Port 7821

# ============================================================================
# SWARMUI AUTO-RECOVERY CONFIGURATION
# ============================================================================
# Controls automatic startup of SwarmUI when needed
SWARMUI_AUTO_START = os.environ.get("SWARMUI_AUTO_START", "true").lower() == "true"
SWARMUI_STARTUP_TIMEOUT = int(os.environ.get("SWARMUI_STARTUP_TIMEOUT", "120"))  # seconds
SWARMUI_HEALTH_CHECK_INTERVAL = float(os.environ.get("SWARMUI_HEALTH_CHECK_INTERVAL", "2.0"))  # seconds


# Feature Flags
ENABLE_VALIDATION_PIPELINE = True
ENABLE_AUTO_EXPORT = True
ENABLE_TEXT_STREAMING = True  # Enable character-by-character text streaming (typewriter effect)
TEXT_STREAM_SPEED_MS = 30  # Milliseconds per character in frontend typewriter display (~33 chars/sec)
NO_TRANSLATE = False  # Set to True to skip translation of prompts
LOOP_GENERATION = 1
LOOP_COMFYUI = 1

# ----------------------------------------------------------------------------
# WIKIPEDIA RESEARCH - Fundamental Interception Capability
# ----------------------------------------------------------------------------
# Enables LLM to fetch Wikipedia content during prompt interception using
# <wiki lang="de">term</wiki> markers in its output.
#
# Language Detection: Default language is auto-detected from user's input.
# WIKIPEDIA_FALLBACK_LANGUAGE is only used when input language cannot be determined.
#
WIKIPEDIA_MAX_ITERATIONS = int(os.environ.get("WIKIPEDIA_MAX_ITERATIONS", "3"))
WIKIPEDIA_MAX_LOOKUPS_PER_ITERATION = int(os.environ.get("WIKIPEDIA_MAX_LOOKUPS_PER_ITERATION", "5"))
WIKIPEDIA_FALLBACK_LANGUAGE = os.environ.get("WIKIPEDIA_FALLBACK_LANGUAGE", "de")  # Fallback when input lang unknown
WIKIPEDIA_CACHE_TTL = int(os.environ.get("WIKIPEDIA_CACHE_TTL", "3600"))  # Cache TTL in seconds (default 1h)

# Translation Prompt
TRANSLATION_PROMPT = """Translate the following text to English. CRITICAL RULES:
1. Preserve ALL brackets exactly as they appear: (), [], {{}}, and especially triple brackets ((()))
2. Do NOT remove or modify any brackets or parentheses
3. Translate the prompt into English with maximal semantic preservation. Maintain the original structure, and preserve all culturally specific terms or non-translatable phrases in their original form. 
4. Do not translate proper names, ritual terms, or material names unless they have a common English usage. Instead, leave them untranslated and preserve their position. 
5. Do not paraphrase, interpret, or summarize. Do not add any comments or explanations.
6. Do NOT add any meta-comments or explanations
7. Output ONLY the translated text, nothing else
8. If text is already in English, return it unchanged!
9. Maintain the exact structure and formatting

Text to translate:

{text}"""

# Analysis System Prompt
# GPT-OSS Safety System Prompt (§86a StGB Compliance)
GPT_OSS_SAFETY_SYSTEM_PROMPT = """You are operating under GERMAN LAW (§86a StGB).

CONTEXT:
- Target users: Children/adolescents aged 8-17 in arts education
- Jurisdiction: Germany (not US - First Amendment does NOT apply)
- Legal framework: § 86a StGB "Verwenden von Kennzeichen verfassungswidriger und terroristischer Organisationen"

§86a StGB FULL TEXT:
"Mit Freiheitsstrafe bis zu drei Jahren oder mit Geldstrafe wird bestraft, wer im Inland Kennzeichen einer der in § 86 Abs. 1 Nr. 1, 2 und 4 oder Abs. 2 bezeichneten Parteien oder Vereinigungen verbreitet oder öffentlich, in einer Versammlung oder in einem von ihm verbreiteten Inhalt verwendet."

English: Using symbols of unconstitutional and terrorist organizations is punishable by up to 3 years imprisonment or fine.

PROHIBITED SYMBOLS (§86a):
- Nazi symbols: Hakenkreuz (swastika in Nazi context), SS-Runen, Schwarze Sonne, Wolfsangel, Sig-Rune, etc.
- Terrorist organizations: ISIS/ISIL/IS symbols, Al-Qaeda, PKK, RAF (Red Army Faction), etc.
- Extremist codes: 88 (HH = Heil Hitler), 18 (AH = Adolf Hitler), 28 (Blood & Honour), 14 (14 Words)

CRITICAL RULES FOR STUDENT PROMPTS:
1. Students DON'T distinguish capitalization: "isis" = "ISIS" = terrorist organization
2. Students DON'T know cultural context: "Indische Swastika" may mean Nazi flag
3. Modern context overrides mythology: spray cans + "Isis" = ISIS terrorist (not goddess)
4. NO benefit of doubt: Ambiguous → Block with explanation
5. Educational exemption requires: Critical analysis + clear anti-extremist stance

PROHIBITED PHRASES/PATTERNS:
- "Isis-Kämpfer" / "isis warrior" / "ISIS fighter" = Terrorist (NOT goddess worshiper)
- "Isis-Zeichen" / "ISIS symbol" = Terrorist symbol (NOT Egyptian hieroglyph)
- "Hakenkreuz" / "swastika on red flag" = Nazi symbol (NOT Hindu/Buddhist)
- "SS-Runen" / "lightning bolt symbols" = Nazi symbols
- "88" on posters/flags = Nazi code (exception: birth year 1988 in clear context)

OUTPUT FORMAT:
- SAFE: "SAFE: [translated text]"
- UNSAFE: "BLOCKED: §86a StGB - [specific symbol/organization] - [brief explanation]"

Your goal: Protect children from creating/viewing illegal content under German law.
"""

# Translation + Correction System Prompt (GPT-OSS)
GPT_OSS_TRANSLATION_SYSTEM_PROMPT = """You assist children/adolescents (ages 8-17) in Arts Education.

TASKS:
1. CORRECT SPELLING for creative image prompts
   - Common typos: "Haustir" → "Haustier" (not "Haustür")
   - Preserve creative intent, fix technical errors
2. TRANSLATE German→English (preserve structure)
   - Maintain ALL brackets: (), [], {{}}, ((()))
   - Keep proper names unchanged
   - If already English, return unchanged

OUTPUT: Translated text only, no meta-comments
"""

ANALYSIS_SYSTEM_PROMPT = """You are an art historian providing a formal image analysis. You are not from a western country. You do not redpruce western patterns of observation. Follow this exact structure:

1. Material and medial properties: State the specific media type (oil painting, photograph, digital image, sculpture, etc.)

2. Pre-iconographic description: Describe ONLY what is directly visible:
   - Objects, figures, settings
   - Spatial relationships and composition
   - Colors, textures, forms
   - Perspective and visual structure

3. Iconographic analysis: Interpret symbolic meanings and cultural references based on what is visible. State interpretations as facts, not possibilities.

4. Iconological interpretation: Present the cultural and conceptual meanings as direct statements.

CRITICAL RULES:
- NEVER use phrases like "it could be", "possibly", "might be", "difficult to determine", "without additional context"
- NEVER apologize or explain limitations
- NEVER mention what you cannot see or determine
- State ALL interpretations as facts, not suggestions
- Write in complete, declarative sentences
- If something is unclear, make your best interpretation and state it as fact
- NEVER end with disclaimers like "Please note", "These analyses", "should be considered", "interpretations rather than"
- NEVER add meta-comments about your analysis
- END your response after completing step 4, with NO additional text"""

# Model Mapping Configuration
OLLAMA_TO_OPENROUTER_MAP = {
    # Maps a local model's base name to its OpenRouter equivalent.
    "deepcoder": "agentica-org/deepcoder-14b-preview",
    "deepseek-r1": "deepseek/deepseek-r1",
    "gemma-2-9b-it": "google/gemma-2-9b-it",
    "gemma-2-27b-it": "google/gemma-2-27b-it",
    "gemma-3-1b-it": "google/gemma-3-1b-it",
    "gemma-3-4b-it": "google/gemma-3-4b-it",
    "gemma-3-12b-it": "google/gemma-3-12b-it",
    "gemma-3-27b-it": "google/gemma-3-27b-it",
    "gemma-3n-e4b-it": "google/gemma-3n-e4b-it",
    "shieldgemma-9b": "google/shieldgemma-9b",
    "llava": "liuhaotian/llava-7b",
    "llava:13b": "liuhaotian/llava-13b",
    "llama-3.1-8b-instruct": "meta-llama/llama-3.1-8b-instruct",
    "llama-3.2-1b-instruct": "meta-llama/llama-3.2-1b-instruct",
    "llama-3.3-8b-instruct": "meta-llama/llama-3.3-8b-instruct",
    "llama-guard-3-1b": "meta-llama/llama-guard-3-1b",
    "llama-guard-3-8b": "meta-llama/llama-guard-3-8b",
    "codestral": "mistralai/codestral",
    "mistral-7b": "mistralai/mistral-7b",
    "mistral-nemo": "mistralai/mistral-nemo",
    "mistral-small:24b": "mistralai/mistral-small-24b",
    "mixtral-8x7b-instruct": "mistralai/mixtral-8x7b-instruct",
    "ministral-8b": "mistralai/ministral-8b",
    "phi-4": "microsoft/phi-4",
    "qwen2.5-translator": "qwen/qwen2.5-translator",
    "qwen2.5-32b-instruct": "qwen/qwen2.5-32b-instruct",
    "qwen3-8b": "qwen/qwen3-8b",
    "qwen3-14b": "qwen/qwen3-14b",
    "qwen3-30b-a3b": "qwen/qwen3-30b-a3b",
    "qwq-32b": "qwen/qwq-32b",
    "sailor2-20b": "sailor2/sailor2-20b",
}

OPENROUTER_TO_OLLAMA_MAP = {v: k for k, v in OLLAMA_TO_OPENROUTER_MAP.items()}

# Cache Configuration
PROMPT_CACHE = {}

# API Cache Control (for Browser Caching)
# Development: Set to True to disable all API caching (aggressive no-cache headers)
# Production: Set to False to enable intelligent caching (configs/models: 5min cache)
DISABLE_API_CACHE = os.environ.get("DISABLE_API_CACHE", "true").lower() == "true"

# Cache strategy for production (only applies when DISABLE_API_CACHE=False)
# Only GET requests to these routes will be cached. POST/SSE are never cached by browsers.
CACHE_STRATEGY = {
    "/api/config/": "public, max-age=300",         # Configs: 5 minutes
    "/pipeline_configs_": "public, max-age=300",   # Metadata: 5 minutes
    "/api/models/": "public, max-age=300",         # Models: 5 minutes (matches backend cache TTL)
}

# Logging Configuration
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# Request Timeouts (in seconds)
OLLAMA_TIMEOUT = 300  # 5 minutes for heavy models (gpt-OSS:120b needs 100-262s)
COMFYUI_TIMEOUT = 480  # 8 minutes for data-rich workflows
POLLING_TIMEOUT = 15
MEDIA_DOWNLOAD_TIMEOUT = 30

# Model Path Resolution Configuration
ENABLE_MODEL_PATH_RESOLUTION = True  # ENABLED: SwarmUI uses OfficialStableDiffusion/ prefix format
MODEL_RESOLUTION_FALLBACK = True      # Fallback to original names if resolution fails

# Base paths for model resolution (configure these to your actual paths)
# Default: SwarmUI is a sibling directory to the server directory
_SERVER_BASE = Path(__file__).parent.parent  # devserver parent = ai4artsed_development
_AI_TOOLS_BASE = _SERVER_BASE.parent  # ai4artsed_development parent = ai/
SWARMUI_BASE_PATH = os.environ.get("SWARMUI_PATH", str(_AI_TOOLS_BASE / "SwarmUI"))
COMFYUI_BASE_PATH = os.environ.get("COMFYUI_PATH", str(_AI_TOOLS_BASE / "SwarmUI" / "dlbackend" / "ComfyUI"))

# LoRA Training Paths (Kohya SS)
KOHYA_DIR = Path(os.environ.get("KOHYA_DIR", str(_AI_TOOLS_BASE / "kohya_ss_new")))
LORA_OUTPUT_DIR = Path(os.environ.get("LORA_OUTPUT_DIR", str(_AI_TOOLS_BASE / "SwarmUI" / "Models" / "loras")))
TRAINING_DATASET_DIR = KOHYA_DIR / "dataset"
TRAINING_LOG_DIR = KOHYA_DIR / "logs"
# Note: Output prefix (e.g. "sd35_") is determined by the model-specific config generator in training_service.py

# Model paths for training (relative to SWARMUI_BASE_PATH)
_SWARMUI_PATH = Path(SWARMUI_BASE_PATH)
SD35_LARGE_MODEL_PATH = _SWARMUI_PATH / "Models" / "Stable-Diffusion" / "OfficialStableDiffusion" / "sd3.5_large.safetensors"
CLIP_L_PATH = _SWARMUI_PATH / "Models" / "clip" / "clip_l.safetensors"
CLIP_G_PATH = _SWARMUI_PATH / "Models" / "clip" / "clip_g.safetensors"
T5XXL_PATH = _SWARMUI_PATH / "Models" / "clip" / "t5xxl_fp16.safetensors"

# Default Negative Terms Configuration
DEFAULT_NEGATIVE_TERMS = "blurry, bad quality, worst quality, low quality, low resolution, extra limbs, extra fingers, distorted, deformed, jpeg artifacts, watermark"

# Safety Filter Configuration (Used by Stage 3 safety check)
SAFETY_NEGATIVE_TERMS = {
    "kids": [
        # Violence & Death
        "violence", "violent", "execution", "killing", "murder", "death", "corpse",
        "torture", "pain", "suffering", "injury", "wound", "bleeding",
        "blood", "bloody", "gore", "gory", "mutilation", "dismemberment",
        # Mental Health
        "despair", "suicide", "suicidal", "self-harm", "depression",
        # Horror & Scary
        "horror", "scary", "frightening", "terror", "nightmare", "disturbing",
        "demon", "zombie", "skeleton", "skull", "evil",
        "haunted", "creepy", "eerie", "sinister", "dark", "macabre",
        # Sexual Content
        "nude", "naked", "nsfw", "sexual", "rape", "pornographic",
        "genital", "abuse",
    ],
    "youth": [
        # Extreme Violence
        "explicit", "hardcore", "brutal", "savage", "cruelty", "sadistic",
        # Explicit Sexual
        "pornographic", "sexual", "nsfw", "rape", "abuse",
        "genitals", "penis", "vagina",
        # Self-Harm
        "self-harm", "suicide", "cutting",
    ],
    "adult": [
        # Only illegal content under German law (§86a StGB)
        "nazi", "swastika", "hakenkreuz", "ss-runen", "hitler",
        "isis", "al-qaeda", "terrorist symbols",
        # Explicit illegal content
        "child", "minor", "underage",
    ],
    "off": []  # Development/testing only - NO filtering
}

# Backwards compatibility
KIDS_SAFETY_NEGATIVE_TERMS = SAFETY_NEGATIVE_TERMS["kids"]

# Workflow Selection Configuration
WORKFLOW_SELECTION = "user"  # "user", "fixed", "system"
FIXED_WORKFLOW = "model/ai4artsed_Stable-Diffusion-3.5_2507152202.json"  # Only used when WORKFLOW_SELECTION = "fixed"

# System mode: Random workflow selection from specified folders
# These correspond directly to folder names under /workflows_legacy/
SYSTEM_WORKFLOW_FOLDERS = ["aesthetics", "semantics", "arts"]

# ============================================================================
# LORA CONFIGURATION (Temporary - will be replaced by dynamic source)
# ============================================================================
# Format: List of dicts with 'name' and 'strength'
# 'name' = filename without path (file must be in SwarmUI/Models/loras/)
# Set to empty list [] to disable LoRA injection
#
LORA_TRIGGERS = [
    # Empty by default - LoRAs are specified per-config in meta.loras
    # Example: {"name": "my_lora.safetensors", "strength": 1.0}
]

# ============================================================================
# USER SETTINGS
# ============================================================================
# User settings can be overridden via devserver/user_settings.json
# Loaded automatically by the Flask app on startup (see my_app/__init__.py)
