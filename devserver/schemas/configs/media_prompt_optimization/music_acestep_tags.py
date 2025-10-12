"""
Music Tags Optimization for AceStep 
Generiert musikalische Style-Tags basierend auf dem Workflow-Beispiel
"""

CONFIG = {
    "backend_type": "ollama", 
    "model": "mistral-nemo:latest",
    "parameters": {
        "temperature": 0.8,
        "max_tokens": 300
    },
    "task": """Write a prompt for a music generating AI. No remarks or comments, just the description for the Audio/Music AI.

Your task is to analyze the input. If it where a song, which kind of song would it be? Which epoch, which style? Or would it rather be a soundscape? Describe the song or soundscape meticulously!

IMPORTANT:
- Focus on musical style, genre, instruments, and atmosphere
- Be specific about musical elements
- Output ONLY the music description, no meta-comments
- Keep it concise but detailed""",
    "context": "Write a prompt for a music generating AI. No remarks or comments, just the description for the Audio/Music AI.",
    "placeholders": {
        "INPUT_TEXT": "{{INPUT_TEXT}}",
        "PREVIOUS_OUTPUT": "{{PREVIOUS_OUTPUT}}",
        "USER_INPUT": "{{USER_INPUT}}"
    }
}
