#!/usr/bin/env python3
"""
Generate new 3-tier Hardware Matrix for settings_routes.py
Tiers: dsgvo_local, dsgvo_cloud (bedrock), non_dsgvo (openrouter)
"""

# Bedrock models (exact IDs)
BEDROCK_HAIKU = "bedrock/eu.anthropic.claude-3-5-haiku-20241022-v2:0"
BEDROCK_SONNET = "bedrock/eu.anthropic.claude-sonnet-4-5-20250929-v1:0"

# OpenRouter models (short names)
OR_HAIKU = "openrouter/anthropic/claude-3-5-haiku"
OR_SONNET = "openrouter/anthropic/claude-3-5-sonnet"

# Template for each VRAM size
VRAM_CONFIGS = {
    "vram_96": {
        "local_text": "local/llama3.2-vision:90b",
        "local_vision": "local/llama3.2-vision:90b",
    },
    "vram_32": {
        "local_text": "local/llama3.2-vision:90b",
        "local_vision": "local/llama3.2-vision:90b",
    },
    "vram_24": {
        "local_text": "local/mistral-nemo",
        "local_vision": "local/llama3.2-vision:11b",
    },
    "vram_16": {
        "local_text": "local/gemma:9b",
        "local_vision": "local/llama3.2-vision:11b",
    },
    "vram_8": {
        "local_text": "local/gemma:2b",
        "local_vision": "local/llama3.2-vision:latest",
    },
}

def generate_matrix():
    matrix = {}

    for vram_key, local_models in VRAM_CONFIGS.items():
        vram_size = vram_key.split("_")[1]

        matrix[vram_key] = {
            # Tier 1: Local only
            "dsgvo_local": {
                "label": f"{vram_size} GB VRAM (DSGVO, local only)",
                "models": {
                    "STAGE1_TEXT_MODEL": local_models["local_text"],
                    "STAGE1_VISION_MODEL": local_models["local_vision"],
                    "STAGE2_INTERCEPTION_MODEL": local_models["local_text"],
                    "STAGE2_OPTIMIZATION_MODEL": local_models["local_text"],
                    "STAGE3_MODEL": local_models["local_text"],
                    "STAGE4_LEGACY_MODEL": local_models["local_text"],
                    "CHAT_HELPER_MODEL": local_models["local_text"],
                    "IMAGE_ANALYSIS_MODEL": local_models["local_vision"],
                },
                "EXTERNAL_LLM_PROVIDER": "none",
                "DSGVO_CONFORMITY": True,
            },
            # Tier 2: AWS Bedrock EU (DSGVO-compliant Cloud)
            "dsgvo_cloud": {
                "label": f"{vram_size} GB VRAM (DSGVO, AWS Bedrock EU)",
                "models": {
                    "STAGE1_TEXT_MODEL": BEDROCK_HAIKU,
                    "STAGE1_VISION_MODEL": local_models["local_vision"],
                    "STAGE2_INTERCEPTION_MODEL": BEDROCK_SONNET,
                    "STAGE2_OPTIMIZATION_MODEL": BEDROCK_HAIKU,
                    "STAGE3_MODEL": BEDROCK_HAIKU,
                    "STAGE4_LEGACY_MODEL": BEDROCK_HAIKU,
                    "CHAT_HELPER_MODEL": BEDROCK_HAIKU,
                    "IMAGE_ANALYSIS_MODEL": local_models["local_vision"],
                },
                "EXTERNAL_LLM_PROVIDER": "bedrock",
                "DSGVO_CONFORMITY": True,
            },
            # Tier 3: OpenRouter (non-DSGVO)
            "non_dsgvo": {
                "label": f"{vram_size} GB VRAM (non-DSGVO, OpenRouter)",
                "models": {
                    "STAGE1_TEXT_MODEL": OR_HAIKU,
                    "STAGE1_VISION_MODEL": local_models["local_vision"],
                    "STAGE2_INTERCEPTION_MODEL": OR_SONNET,
                    "STAGE2_OPTIMIZATION_MODEL": OR_HAIKU,
                    "STAGE3_MODEL": OR_HAIKU,
                    "STAGE4_LEGACY_MODEL": OR_HAIKU,
                    "CHAT_HELPER_MODEL": OR_HAIKU,
                    "IMAGE_ANALYSIS_MODEL": local_models["local_vision"],
                },
                "EXTERNAL_LLM_PROVIDER": "openrouter",
                "DSGVO_CONFORMITY": False,
            },
        }

    return matrix

# Generate and print
import json
matrix = generate_matrix()
print("HARDWARE_MATRIX = " + json.dumps(matrix, indent=4))
