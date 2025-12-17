#!/usr/bin/env python3
"""
Fix Hardware Matrix in settings_routes.py
Add 3rd option: DSGVO-compliant Cloud (Anthropic direct)
"""

# Template for new matrix structure
NEW_MATRIX = {
    "vram_96": {
        "dsgvo_local": {
            "label": "96 GB VRAM (DSGVO, local only)",
            "models": {
                "STAGE1_TEXT_MODEL": "local/llama3.2-vision:90b",
                "STAGE1_VISION_MODEL": "local/llama3.2-vision:90b",
                "STAGE2_INTERCEPTION_MODEL": "local/llama3.2-vision:90b",
                "STAGE2_OPTIMIZATION_MODEL": "local/llama3.2-vision:90b",
                "STAGE3_MODEL": "local/llama3.2-vision:90b",
                "STAGE4_LEGACY_MODEL": "local/llama3.2-vision:90b",
                "CHAT_HELPER_MODEL": "local/llama3.2-vision:90b",
                "IMAGE_ANALYSIS_MODEL": "local/llama3.2-vision:90b"
            },
            "EXTERNAL_LLM_PROVIDER": "none",
            "DSGVO_CONFORMITY": True
        },
        "dsgvo_cloud": {
            "label": "96 GB VRAM (DSGVO, Anthropic Cloud)",
            "models": {
                "STAGE1_TEXT_MODEL": "anthropic/claude-3-5-haiku-20241022",
                "STAGE1_VISION_MODEL": "local/llama3.2-vision:90b",
                "STAGE2_INTERCEPTION_MODEL": "anthropic/claude-3-5-sonnet-20241022",
                "STAGE2_OPTIMIZATION_MODEL": "anthropic/claude-3-5-haiku-20241022",
                "STAGE3_MODEL": "anthropic/claude-3-5-haiku-20241022",
                "STAGE4_LEGACY_MODEL": "anthropic/claude-3-5-haiku-20241022",
                "CHAT_HELPER_MODEL": "anthropic/claude-3-5-haiku-20241022",
                "IMAGE_ANALYSIS_MODEL": "local/llama3.2-vision:90b"
            },
            "EXTERNAL_LLM_PROVIDER": "anthropic",
            "DSGVO_CONFORMITY": True
        },
        "non_dsgvo": {
            "label": "96 GB VRAM (OpenRouter aggregator)",
            "models": {
                "STAGE1_TEXT_MODEL": "openrouter/anthropic/claude-3-5-haiku",
                "STAGE1_VISION_MODEL": "local/llama3.2-vision:90b",
                "STAGE2_INTERCEPTION_MODEL": "openrouter/anthropic/claude-3-5-sonnet",
                "STAGE2_OPTIMIZATION_MODEL": "openrouter/anthropic/claude-3-5-haiku",
                "STAGE3_MODEL": "openrouter/anthropic/claude-3-5-haiku",
                "STAGE4_LEGACY_MODEL": "openrouter/anthropic/claude-3-5-haiku",
                "CHAT_HELPER_MODEL": "openrouter/anthropic/claude-3-5-haiku",
                "IMAGE_ANALYSIS_MODEL": "local/llama3.2-vision:90b"
            },
            "EXTERNAL_LLM_PROVIDER": "openrouter",
            "DSGVO_CONFORMITY": False
        }
    }
}

print("HARDWARE_MATRIX = {")
for vram, configs in NEW_MATRIX.items():
    print(f'    "{vram}": {{')
    for config_name, config_data in configs.items():
        print(f'        "{config_name}": {{')
        print(f'            "label": "{config_data["label"]}",')
        print(f'            "models": {{')
        for model_key, model_value in config_data["models"].items():
            print(f'                "{model_key}": "{model_value}",')
        print(f'            }},')
        print(f'            "EXTERNAL_LLM_PROVIDER": "{config_data["EXTERNAL_LLM_PROVIDER"]}",')
        print(f'            "DSGVO_CONFORMITY": {config_data["DSGVO_CONFORMITY"]}')
        print(f'        }},')
    print(f'    }},')
print("}")
