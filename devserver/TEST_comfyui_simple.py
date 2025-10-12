#!/usr/bin/env python3
"""
Simple ComfyUI Connection Test
Tests auto-discovery and basic connectivity
"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from my_app.services.comfyui_client import get_comfyui_client

async def test_comfyui():
    print("=" * 70)
    print("COMFYUI CONNECTION TEST")
    print("=" * 70)
    print()
    
    # Step 1: Auto-Discovery
    print("Step 1: Auto-Discovery")
    print("-" * 70)
    client = get_comfyui_client()
    print(f"✓ Client created")
    print(f"  URL: {client.base_url}")
    print()
    
    # Step 2: Health Check
    print("Step 2: Health Check")
    print("-" * 70)
    is_healthy = await client.health_check()
    
    if is_healthy:
        print(f"✓ ComfyUI is ONLINE")
        print(f"  Server responding on {client.base_url}")
    else:
        print(f"✗ ComfyUI is OFFLINE")
        print(f"  Server not responding on {client.base_url}")
        print()
        print("TROUBLESHOOTING:")
        print("  1. Check if ComfyUI/SwarmUI is running")
        print("  2. Check ports: 8188 (ComfyUI) or 7821 (SwarmUI)")
        print("  3. Try: ps aux | grep -i comfy")
        return False
    print()
    
    # Step 3: Queue Status
    print("Step 3: Queue Status")
    print("-" * 70)
    queue = await client.get_queue_status()
    
    if queue:
        running = len(queue.get('queue_running', []))
        pending = len(queue.get('queue_pending', []))
        print(f"✓ Queue accessible")
        print(f"  Running: {running} jobs")
        print(f"  Pending: {pending} jobs")
    else:
        print(f"✗ Could not get queue status")
    print()
    
    # Summary
    print("=" * 70)
    print("RESULT: ComfyUI is ready for workflow submission!")
    print("=" * 70)
    print()
    print("NEXT STEPS:")
    print("  1. Run: python TEST_comfyui_workflow_only.py")
    print("     (Tests workflow generation without Ollama)")
    print()
    print("  2. Run: python TEST_full_comfyui_pipeline.py")
    print("     (Full pipeline: Dadaismus → Workflow → Image)")
    print()
    
    return True

if __name__ == "__main__":
    try:
        result = asyncio.run(test_comfyui())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
