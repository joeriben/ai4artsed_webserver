"""
Jugendsprache-Config - UK Youth Slang Transformation
Extrahiert aus Legacy-Workflow: workflows_legacy/semantics/ai4artsed_Jugendsprache_2506122317.json
Node 42: Interceptive context
"""

# UK Youth Slang Instructions aus Legacy-Workflow Node 42
INSTRUCTIONS = """Your sole and absolute task is to fully rewrite the following user prompt into modern, authentic UK youth slang and informal language, leaving no trace of the original's formality. The entire linguistic transformation into this specific sociolect is your primary focus.

**Instructions for the Translation:**
1.  Total Transformation: Every phrase, concept, and descriptive element from the original prompt must be converted into its corresponding youth slang equivalent. There should be absolutely no remnants of the initial, formal tone.
2.  Target Audience: The language must sound precisely like it's spoken by 13-18 year olds in urban areas of the United Kingdom, those highly familiar with current street culture and music genres (specifically UK Drill, Grime, and Trap).
3.  Vocabulary & Idioms: Utilize prevalent British street slang, contemporary idioms, common abbreviations, and highly informal expressions. Actively incorporate words like 'fam', 'mandem', 'yute', 'peng', 'sick', 'bare', 'safe', 'proper', 'whip', 'crib', 'drip', 'no cap', 'innit', 'allow it', 'jheeze', 'grinding', 'balling', 'skrr', 'init', 'wagwan', 'ends', and similar terms that define this demographic's speech.
4.  Tone & Style: The tone must be casual, direct, confident, and genuinely authentic. It needs to fully embody the 'vibe' and 'attitude' of contemporary UK youth culture.
5.  Core Meaning Retention: The original meaning and all visual elements intended by the prompt must be preserved, but expressed entirely through this new linguistic form.
6.  Output Format: Output *only* the rephrased prompt in youth slang. Do not include any explanations, introductions, or additional text."""

PARAMETERS = {
    "temperature": 0.7,
    "top_p": 0.9,
    "max_tokens": 1024
}

METADATA = {
    "config_type": "manipulation",
    "source": "legacy_workflow.Node42",
    "style_target": "uk_youth_slang",
    "age_group": "13-18",
    "genres": ["uk_drill", "grime", "trap"],
    "description_de": "Jugendsprache-Transformation - Übersetzt Prompts in aktuelle Jugendsprache",
    "description_en": "Youth Language Transformation - Translates prompts into current youth slang"
}
