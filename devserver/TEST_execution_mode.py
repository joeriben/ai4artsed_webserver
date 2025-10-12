#!/usr/bin/env python3
"""
Test Script: Execution Mode Support (eco/fast) für Schema-Pipelines
"""
import asyncio
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from schemas.engine.pipeline_executor import PipelineExecutor
from schemas.engine.model_selector import ModelSelector

def test_model_selector():
    """Test ModelSelector with different modes"""
    print("=" * 80)
    print("TEST 1: ModelSelector - Model Switching Logic")
    print("=" * 80)
    
    selector = ModelSelector()
    
    # Test eco mode (local/Ollama)
    print("\n[ECO MODE TESTS - Concrete Models]")
    test_cases_eco = [
        "gemma2:9b",
        "openrouter/anthropic/claude-3.5-haiku",
        "local/llama-3.1-8b-instruct",
    ]
    
    for model in test_cases_eco:
        result = selector.select_model_for_mode(model, 'eco')
        print(f"  {model} → {result}")
    
    # Test fast mode (cloud/OpenRouter)
    print("\n[FAST MODE TESTS - Concrete Models]")
    test_cases_fast = [
        "gemma2:9b",
        "local/gemma2:9b",
        "llama-3.1-8b-instruct",
        "mistral-nemo",
        "phi-4",
    ]
    
    for model in test_cases_fast:
        result = selector.select_model_for_mode(model, 'fast')
        print(f"  {model} → {result}")
    
    # Test task-based selection
    print("\n[TASK-BASED SELECTION - ECO MODE]")
    for task in selector.list_task_types():
        result = selector.select_model_for_mode(f"task:{task}", 'eco')
        desc = selector.get_task_description(task)
        print(f"  task:{task} → {result}")
        print(f"    ({desc})")
    
    print("\n[TASK-BASED SELECTION - FAST MODE]")
    for task in selector.list_task_types():
        result = selector.select_model_for_mode(f"task:{task}", 'fast')
        desc = selector.get_task_description(task)
        print(f"  task:{task} → {result}")
        print(f"    ({desc})")
    
    print("\n✓ ModelSelector tests completed\n")


async def test_pipeline_execution_modes():
    """Test Pipeline Executor with different execution modes"""
    print("=" * 80)
    print("TEST 2: Pipeline Execution with ECO and FAST modes")
    print("=" * 80)
    
    schemas_path = Path(__file__).parent / "schemas"
    executor = PipelineExecutor(schemas_path)
    
    # Initialize
    executor.schema_registry.initialize(schemas_path)
    executor.backend_router.initialize()
    
    # Get available schemas
    schemas = executor.get_available_schemas()
    if not schemas:
        print("❌ No schemas found!")
        return
    
    # Use first available schema for testing
    test_schema = schemas[0]
    print(f"\nUsing test schema: {test_schema}")
    
    test_prompt = "Ein Kamel in der Wüste"
    
    # Test ECO mode
    print("\n[ECO MODE - Local/Ollama]")
    print(f"Schema: {test_schema}")
    print(f"Prompt: {test_prompt}")
    print(f"Execution Mode: eco")
    
    try:
        result_eco = await executor.execute_pipeline(
            schema_name=test_schema,
            input_text=test_prompt,
            execution_mode='eco'
        )
        
        print(f"Status: {result_eco.status.value}")
        print(f"Steps: {len(result_eco.steps)}")
        if result_eco.status.value == 'completed':
            print(f"Final Output: {result_eco.final_output[:100]}...")
            # Check model usage
            for step in result_eco.steps:
                if 'final_model' in step.metadata:
                    print(f"  Step {step.step_id}: {step.metadata['final_model']}")
        else:
            print(f"Error: {result_eco.error}")
    except Exception as e:
        print(f"❌ ECO mode test failed: {e}")
    
    # Test FAST mode
    print("\n[FAST MODE - Cloud/OpenRouter]")
    print(f"Schema: {test_schema}")
    print(f"Prompt: {test_prompt}")
    print(f"Execution Mode: fast")
    
    try:
        result_fast = await executor.execute_pipeline(
            schema_name=test_schema,
            input_text=test_prompt,
            execution_mode='fast'
        )
        
        print(f"Status: {result_fast.status.value}")
        print(f"Steps: {len(result_fast.steps)}")
        if result_fast.status.value == 'completed':
            print(f"Final Output: {result_fast.final_output[:100]}...")
            # Check model usage
            for step in result_fast.steps:
                if 'final_model' in step.metadata:
                    print(f"  Step {step.step_id}: {step.metadata['final_model']}")
        else:
            print(f"Error: {result_fast.error}")
    except Exception as e:
        print(f"❌ FAST mode test failed: {e}")
    
    print("\n✓ Pipeline execution mode tests completed\n")


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("EXECUTION-MODE SUPPORT TEST SUITE")
    print("Testing eco (local/Ollama) vs fast (cloud/OpenRouter) mode switching")
    print("=" * 80 + "\n")
    
    # Test 1: ModelSelector
    test_model_selector()
    
    # Test 2: Pipeline Execution (async)
    print("\nNote: Pipeline execution tests require running Ollama and/or OpenRouter API keys.")
    print("Tests will show model selection even if backends are not available.\n")
    
    try:
        asyncio.run(test_pipeline_execution_modes())
    except Exception as e:
        print(f"❌ Pipeline tests failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("TEST SUITE COMPLETED")
    print("=" * 80)
    print("\nNext Steps:")
    print("1. Start devserver: ./start_devserver.sh")
    print("2. Open browser: http://localhost:17801")
    print("3. Select workflow: dev/TEST_dadaismus")
    print("4. Test with 'Öko (lokal)' → Should use Ollama")
    print("5. Test with 'Schnell (cloud)' → Should use OpenRouter")
    print("\nCheck server logs for:")
    print("  [EXECUTION-MODE] messages")
    print("  [ECO MODE] or [FAST MODE] model conversions")
    print("  [BACKEND] Ollama/OpenRouter request indicators")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
