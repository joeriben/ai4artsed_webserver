#!/usr/bin/env python3
"""
ComfyUI Workflow Generation Test (No Ollama Required)
Tests workflow generation and submission without AI transformation
"""
import asyncio
import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from schemas.engine.comfyui_workflow_generator import get_workflow_generator
from my_app.services.comfyui_client import get_comfyui_client

async def test_workflow_generation():
    print("=" * 70)
    print("COMFYUI WORKFLOW GENERATION TEST")
    print("(No Ollama required - direct workflow generation)")
    print("=" * 70)
    print()
    
    # Simple test prompt
    test_prompt = "A flying camel over the Black Forest, dadaist art style"
    print(f"Test Prompt: {test_prompt}")
    print()
    
    # Step 1: Generate Workflow
    print("Step 1: Generate ComfyUI Workflow")
    print("-" * 70)
    
    schemas_path = Path(__file__).parent / "schemas"
    generator = get_workflow_generator(schemas_path)
    
    workflow = generator.generate_workflow(
        template_name="sd35_standard",
        schema_output=test_prompt,
        parameters={
            "WIDTH": 1024,
            "HEIGHT": 1024,
            "STEPS": 20,
            "CFG": 5.5
        }
    )
    
    if workflow:
        print(f"✓ Workflow generated successfully")
        print(f"  Nodes: {len(workflow)}")
        print(f"  Template: sd35_standard")
        
        # Save for inspection
        output_file = Path("TEST_workflow_output.json")
        with open(output_file, 'w') as f:
            json.dump(workflow, f, indent=2)
        print(f"  Saved to: {output_file}")
    else:
        print(f"✗ Workflow generation failed")
        return False
    print()
    
    # Step 2: Check ComfyUI
    print("Step 2: Check ComfyUI Connection")
    print("-" * 70)
    
    client = get_comfyui_client()
    print(f"  URL: {client.base_url}")
    
    is_healthy = await client.health_check()
    
    if not is_healthy:
        print(f"✗ ComfyUI not available")
        print(f"\nWorkflow generated but cannot submit (ComfyUI offline)")
        print(f"Check TEST_workflow_output.json for generated workflow")
        return False
    
    print(f"✓ ComfyUI is online")
    print()
    
    # Step 3: Submit Workflow
    print("Step 3: Submit Workflow to ComfyUI")
    print("-" * 70)
    
    prompt_id = await client.submit_workflow(workflow)
    
    if prompt_id:
        print(f"✓ Workflow submitted successfully!")
        print(f"  Prompt ID: {prompt_id}")
        print()
        
        # Step 4: Monitor (optional - don't wait for completion)
        print("Step 4: Queue Status")
        print("-" * 70)
        
        queue = await client.get_queue_status()
        if queue:
            running = len(queue.get('queue_running', []))
            pending = len(queue.get('queue_pending', []))
            print(f"  Running: {running} jobs")
            print(f"  Pending: {pending} jobs")
        print()
        
        print("=" * 70)
        print("SUCCESS! Workflow is in ComfyUI queue")
        print("=" * 70)
        print()
        print(f"Prompt ID: {prompt_id}")
        print(f"\nTo monitor progress:")
        print(f"  1. Check SwarmUI interface (if using SwarmUI)")
        print(f"  2. Check ComfyUI output folder")
        print(f"  3. Or wait for completion in full pipeline test")
        print()
        
        return True
    else:
        print(f"✗ Workflow submission failed")
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(test_workflow_generation())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
