"""
TEST CONFIG - Color Grey - Make every color grey
TEMPORARY TEST FILE - NOT FOR PRODUCTION
"""

# Color manipulation instructions for testing
INSTRUCTIONS = """Your task is to transform the input text to make every color mentioned grey.

RULES:
1. Replace ALL color words with "grey" or "gray"
2. Keep the original sentence structure intact
3. Maintain all other descriptive elements
4. Only change color-related words (red, green, blue, yellow, white, black, brown, etc.)
5. Output ONLY the transformed text, no explanations

Examples:
- "red car" → "grey car"
- "blue sky and green grass" → "grey sky and grey grass" 
- "white horse on green meadow" → "grey horse on grey meadow"

Transform the following text by making every color grey:"""

PARAMETERS = {
    "temperature": 0.3,
    "top_p": 0.9,
    "max_tokens": 1024
}

METADATA = {
    "config_type": "manipulation",
    "manipulation_type": "color_replacement",
    "target_color": "grey",
    "description_de": "[TEST] Farb-Manipulation - Alle Farben zu Grau",
    "description_en": "[TEST] Color Manipulation - Make all colors grey",
    "test_file": True
}
