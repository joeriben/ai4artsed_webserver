"""
GPU Service Configuration

Shared GPU inference service for Diffusers + HeartMuLa.
Runs as a standalone Flask/Waitress process on port 17803.
Both dev (17802) and prod (17801) backends call this via HTTP REST.
"""

import os
from pathlib import Path

# --- Server ---
HOST = "127.0.0.1"  # Localhost only — NEVER expose to network
PORT = int(os.environ.get("GPU_SERVICE_PORT", "17803"))
THREADS = 4  # GPU is the bottleneck, not I/O

# --- AI Tools Base ---
_AI_TOOLS_BASE = Path(os.environ.get("AI_TOOLS_BASE", str(Path.home() / "ai")))

# --- Diffusers ---
DIFFUSERS_ENABLED = os.environ.get("DIFFUSERS_ENABLED", "true").lower() == "true"
_diffusers_cache_env = os.environ.get("DIFFUSERS_CACHE_DIR", "")
DIFFUSERS_CACHE_DIR = Path(_diffusers_cache_env) if _diffusers_cache_env else None
DIFFUSERS_USE_TENSORRT = os.environ.get("DIFFUSERS_USE_TENSORRT", "false").lower() == "true"
DIFFUSERS_TORCH_DTYPE = os.environ.get("DIFFUSERS_TORCH_DTYPE", "float16")
DIFFUSERS_DEVICE = os.environ.get("DIFFUSERS_DEVICE", "cuda")
DIFFUSERS_ENABLE_ATTENTION_SLICING = os.environ.get("DIFFUSERS_ENABLE_ATTENTION_SLICING", "true").lower() == "true"
DIFFUSERS_ENABLE_VAE_TILING = os.environ.get("DIFFUSERS_ENABLE_VAE_TILING", "false").lower() == "true"
DIFFUSERS_VRAM_RESERVE_MB = int(os.environ.get("DIFFUSERS_VRAM_RESERVE_MB", "3072"))
DIFFUSERS_TENSORRT_MODELS = {
    "sd35_large": "stabilityai/stable-diffusion-3.5-large-tensorrt",
    "sd35_medium": "stabilityai/stable-diffusion-3.5-medium-tensorrt",
}

# --- HeartMuLa ---
HEARTMULA_ENABLED = os.environ.get("HEARTMULA_ENABLED", "true").lower() == "true"
HEARTMULA_MODEL_PATH = os.environ.get(
    "HEARTMULA_MODEL_PATH",
    str(_AI_TOOLS_BASE / "heartlib" / "ckpt")
)
HEARTMULA_VERSION = os.environ.get("HEARTMULA_VERSION", "3B")
HEARTMULA_LAZY_LOAD = os.environ.get("HEARTMULA_LAZY_LOAD", "true").lower() == "true"
HEARTMULA_DEVICE = os.environ.get("HEARTMULA_DEVICE", "cuda")

# --- Text/LLM (Latent Text Lab) ---
TEXT_ENABLED = os.environ.get("TEXT_ENABLED", "true").lower() == "true"
TEXT_DEVICE = os.environ.get("TEXT_DEVICE", "cuda")
TEXT_DEFAULT_DTYPE = os.environ.get("TEXT_DEFAULT_DTYPE", "bfloat16")
TEXT_VRAM_RESERVE_MB = int(os.environ.get("TEXT_VRAM_RESERVE_MB", "2048"))

# Model presets with VRAM estimates (bf16)
# Used for auto-quantization decisions
TEXT_MODEL_PRESETS = {
    "tiny": {
        "id": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        "vram_gb": 2.5,
        "description": "TinyLlama 1.1B - Fast iteration, limited capability"
    },
    "small": {
        "id": "meta-llama/Llama-3.2-3B-Instruct",
        "vram_gb": 7.0,
        "description": "Llama 3.2 3B - Good balance of speed and quality"
    },
    "medium": {
        "id": "meta-llama/Llama-3.2-8B-Instruct",
        "vram_gb": 17.0,
        "description": "Llama 3.2 8B - High quality, reasonable speed"
    },
    "large": {
        "id": "meta-llama/Llama-3.1-70B-Instruct",
        "vram_gb": 140.0,
        "description": "Llama 3.1 70B - Best quality, requires quantization"
    },
    "qwen-72b": {
        "id": "Qwen/Qwen2.5-72B-Instruct",
        "vram_gb": 144.0,
        "description": "Qwen 2.5 72B - Excellent multilingual, requires quantization"
    },
}

# Quantization VRAM multipliers
TEXT_QUANT_MULTIPLIERS = {
    "bf16": 1.0,
    "fp16": 1.0,
    "int8": 0.5,
    "int4": 0.25,
    "nf4": 0.25,  # bitsandbytes NormalFloat4
}
