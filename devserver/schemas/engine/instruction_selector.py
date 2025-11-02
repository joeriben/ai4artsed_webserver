"""
Instruction Type Selector for Prompt Interception

Mirrors the architecture of model_selector.py but for TASK instructions.
Provides instruction templates that tell LLMs HOW to perform transformations.
"""

INSTRUCTION_TYPES = {
    "artistic_transformation": {
        "description": "Transform prompt through artistic/cultural lens (Prompt Interception)",
        "default": """Transform the input_prompt into a description according to the instructions defined in the input_context. Explicitely communicate the input_context as cultural cf. artistic. cf intervening context. Also communicate genres/artistic traditions in a concrete way (i.e. is it a dance, a photo, a painting, a song, a movie, a statue/sculpture? how should it be translated into media?)

This is not a linguistic translation, but an aesthetic, semantic and structural transformation. Be verbose!

Reconstruct all entities and their relations as specified, ensuring that:
- Each entity is retained – or respectively transformed – as instructed.
- Each relation is altered in line with the particular aesthetics, genre-typical traits, and logic of the "Context". Be explicit about visual aesthetics in terms of materials, techniques, composition, and overall atmosphere. Mention the input_context als cultural, cf. artistic, c.f intervening context in your OUTPUT explicitely.

Output only the transformed description as plain descriptive text. Be aware if the output is something depicted (like a ritual or any situation) OR itself a cultural artefact (such as a specific drawing technique). Describe accordingly. In your output, communicate which elements are most important for an succeeding media generation.

DO NOT USE ANY META-TERMS, NO HEADERS, STRUCTURAL MARKERS WHATSOEVER. DO NOT EXPLAIN YOUR REASONING. JUST PUT OUT THE TRANSFORMED DESCRIPTIVE TEXT."""
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
        instruction_type: The type of instruction (e.g., "artistic_transformation")
        custom_override: Optional custom instruction to use instead of the default

    Returns:
        The instruction text to use in the prompt

    Priority:
        1. Custom override (if provided)
        2. Type-specific default
        3. Fallback to "artistic_transformation" if type not found
    """
    if custom_override:
        return custom_override

    if instruction_type in INSTRUCTION_TYPES:
        return INSTRUCTION_TYPES[instruction_type]["default"]

    # Fallback to artistic_transformation if type not recognized
    return INSTRUCTION_TYPES["artistic_transformation"]["default"]


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
