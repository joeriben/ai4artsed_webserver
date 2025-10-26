"""
Standard-Übersetzungs-Config - Wiederverwendung der Legacy TRANSLATION_PROMPT
"""

# Legacy TRANSLATION_PROMPT aus config.py wiederverwenden
INSTRUCTIONS = """Translate the following text to English. CRITICAL RULES:
1. Preserve ALL brackets exactly as they appear: (), [], {{}}, and especially triple brackets ((()))
2. Do NOT remove or modify any brackets or parentheses
3. Translate the prompt into English with maximal semantic preservation. Maintain the original structure, and preserve all culturally specific terms or non-translatable phrases in their original form. 
4. Do not translate proper names, ritual terms, or material names unless they have a common English usage. Instead, leave them untranslated and preserve their position. 
5. Do not paraphrase, interpret, or summarize. Do not add any comments or explanations.
6. Do NOT add any meta-comments or explanations
7. Output ONLY the translated text, nothing else
8. If text is already in English, return it unchanged!
9. Maintain the exact structure and formatting"""

PARAMETERS = {
    "temperature": 0.1,
    "top_p": 0.9,
    "max_tokens": 2048
}

METADATA = {
    "config_type": "translation",
    "source": "legacy_config.TRANSLATION_PROMPT",
    "language_target": "english",
    "preserve_structure": True
}
