"""
Image Prompt Optimization for Stable Diffusion 3.5
Optimiert Prompts für die Bildgenerierung mit SD 3.5 Large
"""

CONFIG = {
    "backend_type": "ollama",
    "model": "gemma2:9b",
    "parameters": {
        "temperature": 0.7,
        "max_tokens": 500
    },
    "task": """Optimize the following prompt for Stable Diffusion 3.5 image generation.

CRITICAL RULES:
1. Create a detailed, visual description optimized for SD 3.5
2. Include specific visual elements: lighting, composition, style, colors
3. Add technical photography/art terms that improve image quality
4. Keep the core concept from the original prompt
5. Output ONLY the optimized prompt, no meta-comments
6. Maximum 75 words for optimal SD 3.5 performance
7. Use present tense and descriptive language

OPTIMIZATION STRATEGIES:
- Add lighting: "soft natural lighting", "dramatic shadows", "golden hour"
- Include style: "photorealistic", "highly detailed", "8K resolution"
- Specify composition: "centered composition", "rule of thirds", "close-up"
- Technical terms: "sharp focus", "professional photography", "masterpiece"
""",
    "context": "Visual Art Specialist, Image Generation Expert",
    "placeholders": {
        "INPUT_TEXT": "{{INPUT_TEXT}}",
        "PREVIOUS_OUTPUT": "{{PREVIOUS_OUTPUT}}",
        "USER_INPUT": "{{USER_INPUT}}"
    }
}
