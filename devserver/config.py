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
# Format: "local/model-name" for Ollama, "openrouter/provider/model-name" for cloud
#
# Base Models:
LOCAL_DEFAULT_MODEL = "gpt-OSS:20b"                          # Default local text model
LOCAL_VISION_MODEL = "local/llama3.2-vision:latest"                # Local vision model
REMOTE_MULTIMODAL_MODEL = "openrouter/google/gemini-2.5-flash-lite"     # Input Modalitiestext, image, file, audio, video
REMOTE_SMALL_MODEL = "openrouter/mistralai/mistral-nemo"       # Fast, cheap cloud model
REMOTE_LIGHT_MODEL = "openrouter/mistralai/mistral-medium-3.1"       # Fast, cheap cloud model
REMOTE_FAST_MODEL = "openrouter/anthropic/claude-haiku-4.5"       # Fast, cheap cloud model
REMOTE_ADVANCED_MODEL = "openrouter/anthropic/claude-sonnet-4.5"  # High-quality cloud model
REMOTE_EXTREME_MODEL = "openrouter/anthropic/claude-opus-4.1"  # Highest-quality cloud model, VERY EXPENSIVE!

# Stage-Specific Models:
STAGE1_TEXT_MODEL = REMOTE_FAST_MODEL                     # Stage 1: conditional safety checks (simple task)
STAGE1_VISION_MODEL = LOCAL_VISION_MODEL                  # Stage 1: Image analysis
STAGE2_INTERCEPTION_MODEL = REMOTE_FAST_MODEL         # Stage 2: Prompt interception (complex task)
STAGE2_OPTIMIZATION_MODEL = REMOTE_FAST_MODEL         # Stage 2: Prompt optimization (complex task)
STAGE3_MODEL = REMOTE_FAST_MODEL                          # Stage 3: Translation and final safety check (simple task)

# Legacy Model Configuration
GPT_OSS_MODEL = "gpt-OSS:20b"  # openai/gpt-oss-safeguard-20b via Ollama
ANALYSIS_MODEL = "local/llama3.2-vision:latest"
TRANSLATION_MODEL = GPT_OSS_MODEL  # GPT-OSS replaces mistral-nemo
SAFETY_MODEL = GPT_OSS_MODEL

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

# API Configuration
# LLM Provider: "ollama" or "lmstudio"
# TODO 2026: Refactor to Option C (Adapter Pattern with LLMProvider base class)
# NOTE: LM Studio does NOT support model unloading via API - use Ollama for proper VRAM management
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "ollama")  # Ollama supports keep_alive for VRAM management
OLLAMA_API_BASE_URL = os.environ.get("OLLAMA_API_BASE_URL", "http://localhost:11434")
LMSTUDIO_API_BASE_URL = os.environ.get("LMSTUDIO_API_BASE_URL", "http://localhost:1234")
COMFYUI_PREFIX = "comfyui"
COMFYUI_PORT = "7821"  # SwarmUI integrated ComfyUI (RTX 5090 compatible)
SWARMUI_API_PORT = "7801"  # SwarmUI REST API (proper image generation endpoint)



# Feature Flags
ENABLE_VALIDATION_PIPELINE = True
ENABLE_AUTO_EXPORT = True
NO_TRANSLATE = False  # Set to True to skip translation of prompts
LOOP_GENERATION = 1
LOOP_COMFYUI = 1

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

# Logging Configuration
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# Request Timeouts (in seconds)
OLLAMA_TIMEOUT = 90
COMFYUI_TIMEOUT = 480  # 8 minutes for data-rich workflows
POLLING_TIMEOUT = 15
MEDIA_DOWNLOAD_TIMEOUT = 30

# Model Path Resolution Configuration
ENABLE_MODEL_PATH_RESOLUTION = True  # ENABLED: SwarmUI uses OfficialStableDiffusion/ prefix format
MODEL_RESOLUTION_FALLBACK = True      # Fallback to original names if resolution fails

# Base paths for model resolution (configure these to your actual paths)
SWARMUI_BASE_PATH = os.environ.get("SWARMUI_PATH", "/home/joerissen/ai/SwarmUI")
COMFYUI_BASE_PATH = os.environ.get("COMFYUI_PATH", "/home/joerissen/ai/ComfyUI")

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
