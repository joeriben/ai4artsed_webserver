#!/usr/bin/env python3
"""
Test Auto-Media-Generation System
Tests that text-only pipelines automatically generate images
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from schemas.engine.pipeline_executor import PipelineExecutor
from schemas.engine.comfyui_workflow_generator import get_workflow_generator
from my_app.services.comfyui_client import get_comfyui_client

async def test_auto_media_generation():
    """Test the complete auto-media-generation flow"""
    
    print("=" * 80)
    print("AUTO-MEDIA-GENERATION TEST")
    print("=" * 80)
    
    # 1. Test Pipeline Execution (Text-only)
    print("\n[1] Testing Schema-Pipeline: TEST_dadaismus")
    print("-" * 80)
    
    schemas_path = Path(__file__).parent / "schemas"
    executor = PipelineExecutor(schemas_path)
    executor.schema_registry.initialize(schemas_path)
    
    test_prompt = "Ein Kamel fliegt über den Schwarzwald"
    print(f"Input: {test_prompt}")
    
    result = await executor.execute_pipeline(
        schema_name="TEST_dadaismus",
        input_text=test_prompt,
        user_input=test_prompt
    )
    
    print(f"\nPipeline Status: {result.status.value}")
    print(f"Execution Time: {result.execution_time:.2f}s")
    print(f"Steps Completed: {len(result.steps)}")
    
    if result.status.value == 'completed':
        print(f"\n✓ Pipeline completed successfully!")
        print(f"Final Output: {result.final_output[:200]}...")
        
        # Check if ComfyUI was triggered in pipeline
        comfyui_triggered = False
        for step in result.steps:
            if step.metadata and 'prompt_id' in step.metadata:
                comfyui_triggered = True
                print(f"\n✓ ComfyUI was triggered in pipeline: {step.metadata['prompt_id']}")
                break
        
        if not comfyui_triggered:
            print("\n✗ No ComfyUI generation in pipeline (expected for text-only)")
    else:
        print(f"\n✗ Pipeline failed: {result.error}")
        return
    
    # 2. Test Output Type Detection
    print("\n[2] Testing Output Type Detection")
    print("-" * 80)
    
    from my_app.routes.workflow_routes import detect_output_type
    
    schema_info = executor.get_schema_info("TEST_dadaismus")
    final_output = result.final_output or ""
    
    detected_type = detect_output_type(final_output, schema_info)
    print(f"Detected Output Type: {detected_type}")
    
    # 3. Test Auto-Image-Generation
    if detected_type == "image" and not comfyui_triggered:
        print("\n[3] Testing Auto-Image-Generation")
        print("-" * 80)
        
        from my_app.routes.workflow_routes import generate_image_from_text
        
        # Clean output (remove tags)
        clean_output = final_output.replace("#image#", "").strip()
        print(f"Cleaned Prompt: {clean_output[:100]}...")
        
        # Generate image
        print("\nGenerating image via ComfyUI...")
        prompt_id = await generate_image_from_text(
            text_prompt=clean_output,
            schema_name="TEST_dadaismus"
        )
        
        if prompt_id:
            print(f"✓ Image generation queued!")
            print(f"Prompt ID: {prompt_id}")
            print(f"Media URL: /api/media/image/{prompt_id}")
            
            # Wait for completion (optional, for testing)
            print("\nWaiting for image generation...")
            client = get_comfyui_client()
            
            # Poll for completion
            import time
            max_wait = 60
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                history = await client.get_history(prompt_id)
                if history and prompt_id in history:
                    outputs = history[prompt_id].get("outputs", {})
                    if outputs:
                        print(f"\n✓ Image generation completed!")
                        
                        # Extract image info
                        images = await client.get_generated_images(history[prompt_id])
                        if images:
                            print(f"Generated {len(images)} image(s):")
                            for img in images:
                                print(f"  - {img['filename']}")
                        break
                
                await asyncio.sleep(2)
                print(".", end="", flush=True)
            else:
                print(f"\n⚠ Timeout waiting for image (>60s)")
        else:
            print(f"\n✗ Failed to queue image generation")
    else:
        print(f"\n[3] Skipped (output type: {detected_type}, comfyui: {comfyui_triggered})")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_auto_media_generation())
