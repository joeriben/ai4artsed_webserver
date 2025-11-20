#!/usr/bin/env python3
"""
Test Stage 2 with Claude Sonnet 4.5 (Phases 1-3)
Tests: config.py → chunk_builder → manipulate chunk → Claude 4.5
"""
import asyncio
import sys
from pathlib import Path

# Add devserver to path
sys.path.insert(0, str(Path(__file__).parent / "devserver"))

from schemas.engine.chunk_builder import ChunkBuilder
from schemas.engine.config_loader import config_loader
from schemas.engine.backend_router import BackendRouter, BackendRequest, BackendType
import devserver.config as config

async def test_stage2_claude():
    print("=" * 80)
    print("TEST: Stage 2 Prompt Interception with Claude Sonnet 4.5")
    print("=" * 80)

    # Test input (user's example)
    user_prompt = "katze auf der matratze"
    user_rules = "alles muss grün-rosa-kariert sein!"

    print(f"\n📝 Input Prompt: {user_prompt}")
    print(f"📏 User Rules: {user_rules}")

    # Step 1: Check config.py variables
    print(f"\n✅ Step 1: Config variables loaded")
    print(f"   STAGE2_MODEL = {config.STAGE2_MODEL}")

    # Step 2: Load manipulate chunk
    schemas_path = Path(__file__).parent / "devserver" / "schemas"
    chunk_builder = ChunkBuilder(schemas_path)

    chunk_template = chunk_builder.templates.get("manipulate")
    print(f"\n✅ Step 2: Manipulate chunk loaded")
    print(f"   chunk.model = {chunk_template.model}")

    # Step 3: Test config lookup in chunk_builder
    base_model = chunk_template.model
    if hasattr(config, base_model):
        final_model = getattr(config, base_model)
        print(f"\n✅ Step 3: Config lookup successful")
        print(f"   {base_model} → {final_model}")
    else:
        final_model = base_model
        print(f"\n⚠️  Step 3: Using direct model (no config var)")
        print(f"   {base_model}")

    # Step 4: Build chunk request
    config_loader.initialize(schemas_path)
    user_defined_config = config_loader.get_config("user_defined")

    # Context for manipulate chunk
    context = {
        "TASK_INSTRUCTION": "Transform the following prompt according to the user's rules",
        "CONTEXT": user_rules,  # User's rules go here
        "INPUT_TEXT": user_prompt
    }

    # Build chunk (this will use our new config lookup)
    chunk_request = chunk_builder.build_chunk(
        chunk_name="manipulate",
        resolved_config=user_defined_config,
        context=context
    )

    print(f"\n✅ Step 4: Chunk request built")
    print(f"   Model: {chunk_request['model']}")
    print(f"   Backend: {chunk_request['backend_type']}")

    # Step 5: Call backend (OpenRouter with Claude 4.5)
    print(f"\n🚀 Step 5: Calling {final_model}...")
    print(f"   (This will use OpenRouter API)")

    backend_router = BackendRouter()

    request = BackendRequest(
        backend_type=BackendType.OPENROUTER,
        model=chunk_request['model'],
        prompt=chunk_request['prompt'],
        parameters=chunk_request['parameters'],
        stream=False
    )

    response = await backend_router.process_request(request)

    if response.success:
        print(f"\n✅ SUCCESS! Claude 4.5 response:")
        print("=" * 80)
        print(response.content)
        print("=" * 80)

        # Check if rules were followed
        keywords = ["grün", "rosa", "kariert", "green", "pink", "checkered", "checked"]
        found_keywords = [kw for kw in keywords if kw.lower() in response.content.lower()]

        if found_keywords:
            print(f"\n✅ Rules followed! Found keywords: {', '.join(found_keywords)}")
        else:
            print(f"\n⚠️  Rules might not be followed - no pattern keywords found")

    else:
        print(f"\n❌ FAILED: {response.error}")

if __name__ == "__main__":
    asyncio.run(test_stage2_claude())
