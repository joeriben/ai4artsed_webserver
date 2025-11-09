"""
SD 3.5 Standard ComfyUI-Workflow-Generation Config
Erstellt automatisch ComfyUI-Workflows für Stable Diffusion 3.5 Large
"""

CONFIG = {
    "backend_type": "comfyui",
    "workflow_template": "sd35_standard",  # Template im ComfyUIWorkflowGenerator
    "parameters": {
        "checkpoint": "OfficialStableDiffusion/sd3.5_large.safetensors",
        "width": 1024,
        "height": 1024,
        "steps": 25,
        "cfg": 5.5,
        "sampler": "euler",
        "scheduler": "normal",
        "negative_prompt": "watermark, text, bad quality, blurry, low resolution"
    },
    "placeholders": {
        "PROMPT": "{{PREVIOUS_OUTPUT}}",  # Output der vorherigen Pipeline-Stufe
        "USER_INPUT": "{{USER_INPUT}}",
        "INPUT_TEXT": "{{INPUT_TEXT}}"
    },
    "meta": {
        "description": "Generiert ComfyUI-Workflow für SD 3.5 Large basierend auf Pipeline-Output",
        "output_type": "comfyui_workflow",
        "expected_input": "optimized_image_prompt"
    }
}
