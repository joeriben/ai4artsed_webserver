"""
Audio Prompt Optimization for Stable Audio
Optimiert Prompts für die Audiogenerierung mit Stable Audio
"""

CONFIG = {
    "backend_type": "ollama",
    "model": "gemma2:9b",
    "parameters": {
        "temperature": 0.7,
        "max_tokens": 400
    },
    "task": """Optimize the following prompt for Stable Audio generation.

CRITICAL RULES:
1. Create a detailed, audio-focused description for Stable Audio
2. Include specific audio elements: instruments, ambience, tempo, mood
3. Add technical audio terms that improve sound quality
4. Keep the core concept from the original prompt
5. Output ONLY the optimized prompt, no meta-comments
6. Maximum 50 words for optimal Stable Audio performance
7. Use descriptive audio language

OPTIMIZATION STRATEGIES:
- Specify instruments: "acoustic guitar", "piano", "synthesizer", "drums"
- Include ambience: "reverb", "echo", "ambient", "atmospheric"
- Add tempo: "slow", "medium tempo", "upbeat", "rhythmic"
- Technical terms: "high-quality", "clear", "professional recording"
- Mood/Genre: "peaceful", "energetic", "classical", "electronic"

EXAMPLE TRANSFORMATIONS:
- "Bell ringing" → "Large cathedral bell ringing, deep resonant tones, ambient reverb"
- "Happy music" → "Upbeat acoustic guitar melody, major key, cheerful rhythm"
- "Ocean sounds" → "Gentle ocean waves, natural ambience, peaceful soundscape"
""",
    "context": "Audio Engineer, Sound Design Expert",
    "placeholders": {
        "INPUT_TEXT": "{{INPUT_TEXT}}",
        "PREVIOUS_OUTPUT": "{{PREVIOUS_OUTPUT}}",
        "USER_INPUT": "{{USER_INPUT}}"
    }
}
