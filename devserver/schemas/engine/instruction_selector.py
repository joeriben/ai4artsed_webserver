"""
Instruction Type Selector for Prompt Interception

Mirrors the architecture of model_selector.py but for TASK instructions.
Provides instruction templates that tell LLMs HOW to perform transformations.

Partly compressed for use with GPT-OSS:20b. Original: instruction_selector_original.txt
"""

INSTRUCTION_TYPES = {
    # PRIMARY instruction for all interceptions
    "transformation": {
        "description": "Transform Input according to Context rules (Prompt Interception)",
        "default": """Transform the Input according to the rules in Context.

Output ONLY the transformed result.
NO meta-commentary ("I will...", "This shows...", "wird ausgeführt als...").
Use the specific vocabulary and techniques defined in Context."""
    },

    # LEGACY alias - redirects to "transformation"
    "artistic_transformation": {
        "description": "[DEPRECATED] Use 'transformation' instead",
        "default": None  # Will be handled in get_instruction()
    },

    "prompt_optimization": {
        "description": "Translate cultural/artistic concepts into visual rendering instructions",
        "default": """Translate the Input into visual instructions for image generation.

TASK: Convert cultural and artistic concepts into HOW THEY LOOK.

Examples:
- "qiyun shengdong" → dynamic brushstrokes, sense of movement, living energy in lines
- "Three Distances" → high horizon, layered depth planes, atmospheric perspective
- "konfuzianische Ordnung" → ordered composition, hierarchical figure placement
- "sfumato" → soft blurred edges, smoky transitions, no hard outlines

Keep the cultural SPECIFICITY - translate the concept, don't genericize it.

OUTPUT FORMAT (in input language):
[CLIP: visual keywords, 25 words max] || [T5: descriptive sentence capturing the style]

Output ONLY the formatted line."""
    },

    "passthrough": {
        "description": "No transformation - direct pass-through (for testing/debugging)",
        "default": """Output the input_prompt exactly as provided, with no modification or transformation."""
    }
}


def get_instruction(instruction_type: str, custom_override: str = None) -> str:
    """
    Get instruction text for a given instruction type.

    Args:
        instruction_type: The type of instruction (e.g., "transformation")
        custom_override: Optional custom instruction to use instead of the default

    Returns:
        The instruction text to use in the prompt

    Priority:
        1. Custom override (if provided)
        2. Type-specific default
        3. Fallback to "transformation" if type not found
    """
    if custom_override:
        return custom_override

    # Handle legacy alias
    if instruction_type == "artistic_transformation":
        instruction_type = "transformation"

    # Handle any unknown type - redirect to transformation
    if instruction_type not in INSTRUCTION_TYPES or INSTRUCTION_TYPES[instruction_type]["default"] is None:
        instruction_type = "transformation"

    return INSTRUCTION_TYPES[instruction_type]["default"]


def list_instruction_types() -> dict:
    """
    List all available instruction types with their descriptions.

    Returns:
        Dictionary mapping instruction type names to their descriptions
    """
    return {
        name: info["description"]
        for name, info in INSTRUCTION_TYPES.items()
    }
