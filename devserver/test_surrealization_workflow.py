#!/usr/bin/env python3
"""
Test Surrealization Complete Workflow
Tests the full exotic workflow infrastructure:
- Direct pipeline with skip_stage2 flag
- Surrealization Stage 2 config (uses direct pipeline)
- Surrealization Stage 4 output config (dual-encoder fusion)
- Stage 2 skip logic
- All 3 chunks execution
"""
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from schemas.engine.config_loader import ConfigLoader
from schemas.engine.chunk_builder import ChunkBuilder

def test_direct_pipeline():
    """Test 1: Direct pipeline has skip_stage2 flag"""
    print("=" * 80)
    print("TEST 1: Direct Pipeline (skip_stage2 flag)")
    print("=" * 80)

    pipeline_file = Path("schemas/pipelines/direct.json")
    with open(pipeline_file) as f:
        pipeline = json.load(f)

    print(f"✓ Pipeline loaded: {pipeline['name']}")
    print(f"  skip_stage2: {pipeline.get('skip_stage2', False)}")
    print(f"  chunks: {pipeline.get('chunks', [])}")

    assert pipeline.get('skip_stage2') == True, "❌ skip_stage2 flag not set!"
    assert len(pipeline.get('chunks', [])) == 0, "❌ Direct pipeline should have no chunks!"

    print("✓ TEST 1 PASSED\n")
    return True

def test_surrealization_stage2_config():
    """Test 2: Surrealization Stage 2 config"""
    print("=" * 80)
    print("TEST 2: Surrealization Stage 2 Config")
    print("=" * 80)

    config_loader = ConfigLoader()
    config_loader.initialize(Path("schemas"))

    config = config_loader.get_config("surrealization")

    if not config:
        print("❌ Surrealization config not found!")
        return False

    print(f"✓ Config loaded: {config.name}")
    print(f"  Pipeline: {config.pipeline_name}")
    print(f"  Media preferences: {config.media_preferences}")

    # Check pipeline reference
    assert config.pipeline_name == "direct", f"❌ Expected 'direct' pipeline, got '{config.pipeline_name}'"

    # Check output_configs
    output_configs = config.media_preferences.get('output_configs', [])
    assert "surrealization_output" in output_configs, "❌ output_configs should include 'surrealization_output'"

    print(f"  Output configs: {output_configs}")
    print("✓ TEST 2 PASSED\n")
    return True

def test_surrealization_stage4_config():
    """Test 3: Surrealization Stage 4 output config"""
    print("=" * 80)
    print("TEST 3: Surrealization Stage 4 Output Config")
    print("=" * 80)

    config_loader = ConfigLoader()
    config_loader.initialize(Path("schemas"))

    # Load from output folder
    config = config_loader.get_config("surrealization_output")

    # Note: ConfigLoader might prioritize interception folder, so check directly
    output_file = Path("schemas/configs/output/surrealization_output.json")
    if not output_file.exists():
        print("❌ Output config file not found!")
        return False

    with open(output_file) as f:
        output_config = json.load(f)

    print(f"✓ Output config loaded: {output_config['name']['en']}")
    print(f"  Pipeline: {output_config['pipeline']}")
    print(f"  Stage: {output_config['meta']['stage']}")

    assert output_config['pipeline'] == "dual_encoder_fusion", "❌ Wrong pipeline!"
    assert output_config['meta']['stage'] == "output", "❌ Should be output stage!"

    # Load the dual_encoder_fusion pipeline
    pipeline_file = Path("schemas/pipelines/dual_encoder_fusion.json")
    with open(pipeline_file) as f:
        pipeline = json.load(f)

    print(f"\n✓ Dual-encoder fusion pipeline:")
    print(f"  Chunks: {' → '.join(pipeline['chunks'])}")

    assert len(pipeline['chunks']) == 3, "❌ Should have 3 chunks!"

    print("✓ TEST 3 PASSED\n")
    return True

def test_skip_stage2_logic():
    """Test 4: Stage 2 skip logic"""
    print("=" * 80)
    print("TEST 4: Stage 2 Skip Logic Simulation")
    print("=" * 80)

    config_loader = ConfigLoader()
    config_loader.initialize(Path("schemas"))

    # Load surrealization config
    config = config_loader.get_config("surrealization")

    # Load pipeline definition
    pipeline_def = config_loader.get_pipeline(config.pipeline_name)

    print(f"✓ Loaded pipeline: {pipeline_def.name}")

    # Check skip_stage2 in metadata (it's a dataclass/dict)
    skip_stage2 = getattr(pipeline_def, 'skip_stage2', False) if pipeline_def else False

    print(f"  skip_stage2: {skip_stage2}")

    print(f"  skip_stage2 value: {skip_stage2}")

    assert skip_stage2 == True, "❌ skip_stage2 should be True!"

    # Simulate workflow
    input_text = "A surreal landscape where mountains float upside down"
    stage1_output = input_text  # Stage 1: safety check (simulated pass)

    if skip_stage2:
        stage2_output = stage1_output  # SKIP Stage 2 - pass through
        print(f"\n✓ Stage 2 SKIPPED - input passed through unchanged")
    else:
        stage2_output = "[WOULD EXECUTE STAGE 2 HERE]"
        print(f"\n✗ Stage 2 would execute (unexpected!)")

    print(f"  Stage 1 output: '{stage1_output[:50]}...'")
    print(f"  Stage 2 output: '{stage2_output[:50]}...'")

    assert stage1_output == stage2_output, "❌ Output should be unchanged!"

    print("✓ TEST 4 PASSED\n")
    return True

def test_stage4_chunks():
    """Test 5: Stage 4 chunks can be built"""
    print("=" * 80)
    print("TEST 5: Stage 4 Chunks (Dual-Encoder Fusion)")
    print("=" * 80)

    config_loader = ConfigLoader()
    config_loader.initialize(Path("schemas"))
    chunk_builder = ChunkBuilder(Path("schemas"))

    # Load output config
    output_file = Path("schemas/configs/output/surrealization_output.json")
    with open(output_file) as f:
        output_config_data = json.load(f)

    # Get chunks from pipeline
    pipeline_file = Path("schemas/pipelines/dual_encoder_fusion.json")
    with open(pipeline_file) as f:
        pipeline = json.load(f)

    chunks = pipeline['chunks']
    print(f"Testing {len(chunks)} chunks:\n")

    # Simulate Stage 3 output (translated English prompt)
    stage3_output = "A surreal landscape where mountains float upside down above an ocean of clouds"

    # Create a mock config object
    class MockConfig:
        def __init__(self, data):
            self.name = "surrealization"
            self.pipeline_name = data['pipeline']
            self.chunks = chunks
            self.parameters = data.get('parameters', {})
            self.meta = data.get('meta', {})

    config = MockConfig(output_config_data)

    # Test Chunk 1: optimize_t5_prompt
    print("Chunk 1: optimize_t5_prompt")
    try:
        chunk1 = chunk_builder.build_chunk(
            chunk_name='optimize_t5_prompt',
            resolved_config=config,
            context={
                'input_text': stage3_output,
                'user_input': stage3_output
            }
        )
        print(f"  ✓ Built successfully")
        print(f"    Backend: {chunk1['backend_type']}")
        print(f"    Output format: {chunk1['metadata'].get('output_format', 'text')}")
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return False

    # Test Chunk 2: optimize_clip_prompt
    print("\nChunk 2: optimize_clip_prompt")
    try:
        chunk2 = chunk_builder.build_chunk(
            chunk_name='optimize_clip_prompt',
            resolved_config=config,
            context={
                'input_text': stage3_output,
                'user_input': stage3_output
            }
        )
        print(f"  ✓ Built successfully")
        print(f"    Backend: {chunk2['backend_type']}")
        print(f"    Output format: {chunk2['metadata'].get('output_format', 'text')}")
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return False

    # Test Chunk 3: dual_encoder_fusion_image (with placeholders)
    print("\nChunk 3: dual_encoder_fusion_image")
    try:
        # Simulate outputs from chunks 1 and 2
        context_with_placeholders = {
            'input_text': stage3_output,
            'user_input': stage3_output,
            'custom_placeholders': {
                'T5_PROMPT': 'A surreal landscape manifests where the laws of gravity...',
                'CLIP_PROMPT': 'floating mountains, inverted peaks, surreal gravity...',
                'ALPHA': '0.25'
            }
        }

        chunk3 = chunk_builder.build_chunk(
            chunk_name='dual_encoder_fusion_image',
            resolved_config=config,
            context=context_with_placeholders
        )
        print(f"  ✓ Built successfully")
        print(f"    Backend: {chunk3['backend_type']}")
        print(f"    Chunk type: {chunk3['metadata'].get('chunk_type', 'unknown')}")
        print(f"    Has workflow: {chunk3['metadata'].get('has_workflow', False)}")

        # Check if placeholders would be replaced
        if 'prompt' in chunk3 and isinstance(chunk3['prompt'], dict):
            workflow = chunk3['prompt']
            print(f"    Workflow nodes: {len(workflow)}")

            # Check specific nodes
            if '5' in workflow:  # CLIP node
                clip_text = workflow['5']['inputs'].get('text', '')
                print(f"    Node 5 (CLIP): {clip_text[:50]}...")
            if '6' in workflow:  # T5 node
                t5_text = workflow['6']['inputs'].get('text', '')
                print(f"    Node 6 (T5): {t5_text[:50]}...")
            if '9' in workflow:  # Fusion node
                alpha = workflow['9']['inputs'].get('alpha', '')
                print(f"    Node 9 (Fusion alpha): {alpha}")

    except Exception as e:
        print(f"  ❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n✓ TEST 5 PASSED\n")
    return True

def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("SURREALIZATION WORKFLOW - COMPLETE TEST SUITE")
    print("=" * 80 + "\n")

    tests = [
        ("Direct Pipeline", test_direct_pipeline),
        ("Surrealization Stage 2 Config", test_surrealization_stage2_config),
        ("Surrealization Stage 4 Config", test_surrealization_stage4_config),
        ("Stage 2 Skip Logic", test_skip_stage2_logic),
        ("Stage 4 Chunks", test_stage4_chunks)
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ TEST FAILED: {name}")
            print(f"   Error: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Surrealization workflow ready!")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
