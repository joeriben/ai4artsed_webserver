#!/usr/bin/env python3
"""
Test Auto-Audio-Generation
Direkter Test ohne Frontend
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_audio_generation():
    """Test audio generation directly"""
    
    print("=" * 80)
    print("AUTO-AUDIO-GENERATION TEST")
    print("=" * 80)
    
    # Import components
    from schemas.engine.comfyui_workflow_generator import get_workflow_generator
    from my_app.services.comfyui_client import get_comfyui_client
    
    # Test prompt
    test_prompt = "Peaceful forest sounds with birds chirping and gentle wind"
    print(f"\nPrompt: {test_prompt}")
    
    # 1. Generate workflow
    print("\n[1] Generating Stable Audio workflow...")
    print("-" * 80)
    
    schemas_path = Path(__file__).parent / "schemas"
    generator = get_workflow_generator(schemas_path)
    
    workflow = generator.generate_workflow(
        template_name="stable_audio_standard",
        schema_output=test_prompt,
        parameters={}  # Use defaults
    )
    
    if not workflow:
        print("❌ Failed to generate workflow")
        return
    
    print(f"✅ Workflow generated with {len(workflow)} nodes")
    print(f"   Duration: 47.0s, Steps: 150, CFG: 7.0")
    
    # 2. Submit to ComfyUI
    print("\n[2] Submitting to ComfyUI...")
    print("-" * 80)
    
    client = get_comfyui_client()
    
    # Health check first
    is_healthy = await client.health_check()
    if not is_healthy:
        print("⚠️  ComfyUI not reachable")
        print("   Make sure ComfyUI is running with Stable Audio nodes")
        return
    
    print("✅ ComfyUI is reachable")
    
    # Submit workflow
    prompt_id = await client.submit_workflow(workflow)
    
    if not prompt_id:
        print("❌ Failed to submit workflow")
        return
    
    print(f"✅ Audio generation queued!")
    print(f"   Prompt ID: {prompt_id}")
    
    # 3. Wait for completion
    print("\n[3] Waiting for audio generation...")
    print("-" * 80)
    print("This will take ~60 seconds (150 steps)...")
    
    import time
    start_time = time.time()
    max_wait = 120  # 2 minutes
    
    while time.time() - start_time < max_wait:
        history = await client.get_history(prompt_id)
        
        if history and prompt_id in history:
            outputs = history[prompt_id].get("outputs", {})
            if outputs:
                elapsed = time.time() - start_time
                print(f"\n✅ Audio generation completed in {elapsed:.1f}s!")
                
                # Check for audio files
                audio_found = False
                for node_id, output in outputs.items():
                    if "audio" in output:
                        audio_found = True
                        for aud in output["audio"]:
                            filename = aud.get("filename")
                            print(f"   🎵 Audio: {filename}")
                
                if not audio_found:
                    print("⚠️  No audio output found in workflow")
                    print(f"   Outputs: {list(outputs.keys())}")
                
                print(f"\n📁 Access via:")
                print(f"   URL: /api/media/audio/{prompt_id}")
                print(f"   Or check ComfyUI output folder")
                
                return
        
        await asyncio.sleep(2)
        elapsed = time.time() - start_time
        if int(elapsed) % 10 == 0:  # Update every 10s
            print(f"   ... {int(elapsed)}s elapsed")
    
    print(f"\n⏱️  Timeout after {max_wait}s")
    print("   Audio generation may still be running in ComfyUI")

    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    print("\n🎵 Testing Auto-Audio-Generation with ComfyUI Stable Audio")
    print("Prerequisites: ComfyUI with Stable Audio Custom Nodes\n")
    asyncio.run(test_audio_generation())
