"""
Music Lyrics Generation for AceStep
Generiert Liedtexte basierend auf dem Workflow-Beispiel
"""

CONFIG = {
    "backend_type": "ollama",
    "model": "mistral-nemo:latest", 
    "parameters": {
        "temperature": 0.9,
        "max_tokens": 400
    },
    "task": """Your task is to analyze the input. If it is a song, which lyrics would it have? Write the lyrics for this song. Output ONLY the lyrics! Any comments would be sung, too! Keep the lines short, and regard the poetic rhythm (metrical feet).

If it is a soundscape, sharply reflect if it needs words, or not. If not, just output "."

IMPORTANT:
- For songs: Write actual lyrics with verses and chorus
- Keep lines short for better musical flow
- Consider rhythm and rhyme
- For soundscapes/instrumentals: Output only "."
- No meta-comments or explanations""",
    "context": "Lyricist, Song writer, word smith",
    "placeholders": {
        "INPUT_TEXT": "{{PREVIOUS_OUTPUT}}",  # Uses output from tags step
        "PREVIOUS_OUTPUT": "{{PREVIOUS_OUTPUT}}",
        "USER_INPUT": "{{USER_INPUT}}"
    }
}
