"""
Central configuration file for the AI4ArtsEd Web Server
"""
import os
from pathlib import Path

# Base paths
THIS_FILE = Path(__file__).resolve()
BASE_DIR = THIS_FILE.parent.parent
LOCAL_WORKFLOWS_DIR = BASE_DIR / "workflows"
PUBLIC_DIR = BASE_DIR / "public"
EXPORTS_DIR = BASE_DIR / "exports"

# API Configuration
OLLAMA_API_BASE_URL = os.environ.get("OLLAMA_API_BASE_URL", "http://localhost:11434")
COMFYUI_PREFIX = "comfyui"
COMFYUI_PORT = "7821"

# Model Configuration
ANALYSIS_MODEL = "llava:13b"
TRANSLATION_MODEL = "thinkverse/towerinstruct"
SAFETY_MODEL = "llama-guard3:8b"

# Feature Flags
ENABLE_VALIDATION_PIPELINE = True
ENABLE_AUTO_EXPORT = True

# Analysis System Prompt
ANALYSIS_SYSTEM_PROMPT = """Instruction: ANALYZE THE IMAGE IN THE STYLE OF A SCIENTIFIC PRINTED ANALYSIS. REGARD THE FOLLOWING RULES: 

    Material and medial properties: Identify the media type (e.g. oil painting, guache, mural, silver gelatine print, analog photography, digital foto, film still, scultpure, billboard, etc.)
    
    Pre-iconographic description: Identify and describe all visible forms, objects, gestures, settings, and compositional elements. Make a list of EACH entity of the image. Describe each entity, its position, spatial relatedness, shape, texture, colours, and state.
    Include a planimetrical analysis of the spatial structure: describe lines of sight, perspectives, depth layers, symmetry/asymmetry, visual hierarchies, and dominant spatial axes.

    Iconographic analysis: Interpret the symbolic meaning of identified motifs, figures, or actions based on conventional themes, narratives, or allegories. Identify their historical or cultural references. Identify atmospheres and affective aspects.

    Iconological interpretation: Deduce the underlying worldview, socio-cultural context, or conceptual structure expressed through the image. Identify latent meanings or ideological structures that inform the image's visual rhetoric. 

NO META-COMMENTS; NAMING OF METHODS; LABELS; CATEGORIES; ME; OR YOURSELF WHATSOEVER!
Do not comment on the method or your own analysis. NEVER MENTION MISSING CONTEXT. Always interpret as if for a printed text. Should you fail to infer meanings, choose thorough description as a fallback.
."""

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

# Server Configuration
HOST = "0.0.0.0"
PORT = 5000
THREADS = 8

# Kids Safety Configuration
KIDS_SAFETY_NEGATIVE_TERMS = [
    # Violence and Death
    "violence", "violent", "execution", "killing", "murder", "death", "corpse", 
    "torture", "pain", "suffering", "injury", "wound", "bleeding",
    
    # Blood and Gore
    "blood", "bloody", "gore", "gory", "mutilation", "dismemberment",
    
    # Psychological Distress
    "despair", "suicide", "suicidal", "self-harm", "depression", "hatred", "hate",
    "horror", "scary", "frightening", "terror", "nightmare", "disturbing",
    
    # Supernatural/Scary Elements
    "demon", "zombie", "skeleton", "skull", "evil",
    "haunted", "creepy", "eerie", "sinister", "dark", "macabre",
    
    # Pornographic/Sexual Elements  
    "nude", "naked", "nsfw", "sexual", "erotic", "pornographic",
    "genital",
    
    # Other Problematic Content
    "abuse"
]
