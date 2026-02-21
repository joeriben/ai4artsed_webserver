#!/usr/bin/env python3
"""
Config Context Translation Helper

Translates English context strings in interception configs to German
using a local Ollama model. Generates translations for human review.

Usage:
    python3 scripts/translate_config_contexts.py [--dry-run] [--config CONFIG_NAME]

Options:
    --dry-run           Show what would be translated without making changes
    --config CONFIG     Translate only specific config (e.g., "dada")
    --auto              Automatically apply translations (use with caution!)

Output:
    - Prints translation suggestions
    - With --auto: Updates config files directly
    - Without --auto: Shows diffs for review

Architecture:
    - Reads configs from schemas/configs/interception/
    - Uses Ollama API directly (same as ollama_service.py)
    - Changes context from string to {en: ..., de: ...}
"""

import json
import sys
import requests
from pathlib import Path
from typing import Dict, Optional

# Configuration
OLLAMA_API_BASE_URL = "http://localhost:11434"
TRANSLATION_MODEL = "qwen3:4b"
TIMEOUT = 120  # Longer timeout for translation

TRANSLATION_SYSTEM_PROMPT = """You are a professional translator specialized in educational content about art and AI.

Your task is to translate English text to German, preserving:
1. Pedagogical intent and tone
2. Technical terminology
3. Gender-inclusive language (use *in forms like Künstler*in)
4. Formal "Du" form (German youth/education standard)

Guidelines:
- Keep art movement names in original (Dadaismus, Bauhaus, etc.)
- Preserve technical terms (Prompt, Pipeline, etc.)
- Maintain instructional clarity
- Use inclusive language (*in, * for gender)

Translate ONLY the content, do NOT add explanations or comments."""


def translate_with_ollama(text: str) -> Optional[str]:
    """
    Translate English text to German using local Ollama model

    Args:
        text: English text to translate

    Returns:
        German translation or None if failed
    """
    prompt = f"Translate this educational text from English to German:\n\n{text}"

    payload = {
        "model": TRANSLATION_MODEL,
        "prompt": prompt,
        "system": TRANSLATION_SYSTEM_PROMPT,
        "stream": False,
        "keep_alive": "5m"  # Keep model loaded for batch processing
    }

    try:
        response = requests.post(
            f"{OLLAMA_API_BASE_URL}/api/generate",
            json=payload,
            timeout=TIMEOUT
        )
        response.raise_for_status()
        result = response.json()
        translated = result.get("response", "").strip()

        if not translated:
            print(f"⚠️  Empty translation received for: {text[:50]}...")
            return None

        return translated

    except requests.exceptions.RequestException as e:
        print(f"❌ Ollama API error: {e}")
        return None


def load_config(config_path: Path) -> Optional[Dict]:
    """Load and parse a config JSON file"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {config_path.name}: {e}")
        return None
    except Exception as e:
        print(f"❌ Error loading {config_path.name}: {e}")
        return None


def save_config(config_path: Path, config_data: Dict) -> bool:
    """Save config to JSON file with proper formatting"""
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ Error saving {config_path.name}: {e}")
        return False


def translate_config(config_path: Path, dry_run: bool = False, auto: bool = False):
    """
    Process a single config file for translation

    Args:
        config_path: Path to config file
        dry_run: If True, only show what would be translated
        auto: If True, automatically apply translations
    """
    print(f"\n{'='*80}")
    print(f"📄 Processing: {config_path.name}")
    print(f"{'='*80}")

    # Load config
    config = load_config(config_path)
    if not config:
        return

    # Check if context exists
    if 'context' not in config:
        print("⚠️  No 'context' field found, skipping")
        return

    context = config['context']

    # Check if already translated
    if isinstance(context, dict) and 'en' in context and 'de' in context:
        print("✅ Already translated (has en/de structure)")
        print(f"   EN: {context['en'][:60]}...")
        print(f"   DE: {context['de'][:60]}...")
        return

    # Ensure context is a string
    if not isinstance(context, str):
        print(f"⚠️  Context is not a string (type: {type(context).__name__}), skipping")
        return

    print(f"\n📝 Original context (EN):")
    print(f"   {context[:200]}...")
    print(f"   [Total length: {len(context)} chars]")

    if dry_run:
        print("\n🔍 DRY RUN: Would translate this context")
        return

    # Translate
    print(f"\n🔄 Translating with {TRANSLATION_MODEL}...")
    translated = translate_with_ollama(context)

    if not translated:
        print("❌ Translation failed, skipping")
        return

    print(f"\n📝 Generated translation (DE):")
    print(f"   {translated[:200]}...")
    print(f"   [Total length: {len(translated)} chars]")

    # Create new structure
    new_context = {
        "en": context,
        "de": translated
    }

    if auto:
        # Apply automatically
        config['context'] = new_context
        if save_config(config_path, config):
            print("\n✅ Translation applied and saved")
        else:
            print("\n❌ Failed to save translation")
    else:
        # Show for review
        print("\n" + "="*80)
        print("📋 REVIEW REQUIRED")
        print("="*80)
        print("\nProposed change:")
        print(json.dumps({"context": new_context}, ensure_ascii=False, indent=2))
        print("\nTo apply this translation:")
        print(f"  python3 scripts/translate_config_contexts.py --config {config_path.stem} --auto")


def main():
    """Main translation workflow"""
    import argparse

    parser = argparse.ArgumentParser(description='Translate config contexts to German')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be translated without translating')
    parser.add_argument('--config', type=str,
                       help='Translate only specific config (e.g., "dada")')
    parser.add_argument('--auto', action='store_true',
                       help='Automatically apply translations (use with caution!)')

    args = parser.parse_args()

    # Determine base path (script location or devserver/)
    script_dir = Path(__file__).parent.parent
    configs_path = script_dir / "schemas" / "configs" / "interception"

    if not configs_path.exists():
        print(f"❌ Configs directory not found: {configs_path}")
        sys.exit(1)

    print("🚀 Config Context Translation Helper")
    print(f"📂 Configs directory: {configs_path}")
    print(f"🤖 Model: {TRANSLATION_MODEL}")
    print(f"🔧 Mode: {'DRY RUN' if args.dry_run else 'AUTO' if args.auto else 'REVIEW'}")

    # Get list of configs to process
    if args.config:
        # Single config
        config_file = configs_path / f"{args.config}.json"
        if not config_file.exists():
            print(f"❌ Config not found: {config_file}")
            sys.exit(1)
        configs = [config_file]
    else:
        # All configs
        configs = sorted(configs_path.glob("*.json"))
        configs = [c for c in configs if c.is_file()]

        # Exclude deactivated folder
        configs = [c for c in configs if "deactivated" not in c.parts]

    print(f"📊 Found {len(configs)} config(s) to process\n")

    # Check Ollama availability
    if not args.dry_run:
        try:
            response = requests.get(f"{OLLAMA_API_BASE_URL}/api/tags", timeout=5)
            response.raise_for_status()
            print("✅ Ollama API is reachable")
        except Exception as e:
            print(f"❌ Cannot reach Ollama API: {e}")
            print(f"   Make sure Ollama is running: ollama serve")
            sys.exit(1)

        # Check if model is available
        try:
            models = response.json().get("models", [])
            model_names = [m.get("name", "") for m in models]
            if not any(TRANSLATION_MODEL in name for name in model_names):
                print(f"⚠️  Model {TRANSLATION_MODEL} not found in Ollama")
                print(f"   Available models: {', '.join(model_names)}")
                print(f"   Pull model: ollama pull {TRANSLATION_MODEL}")
                sys.exit(1)
            print(f"✅ Model {TRANSLATION_MODEL} is available\n")
        except Exception as e:
            print(f"⚠️  Could not verify model availability: {e}\n")

    # Process configs
    translated_count = 0
    skipped_count = 0
    failed_count = 0

    for config_path in configs:
        try:
            translate_config(config_path, dry_run=args.dry_run, auto=args.auto)
            if not args.dry_run:
                translated_count += 1
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user")
            break
        except Exception as e:
            print(f"❌ Unexpected error processing {config_path.name}: {e}")
            failed_count += 1

    # Summary
    print("\n" + "="*80)
    print("📊 SUMMARY")
    print("="*80)
    print(f"Total configs: {len(configs)}")
    if not args.dry_run:
        print(f"Translated: {translated_count}")
        print(f"Failed: {failed_count}")
    print(f"Skipped (already translated): {skipped_count}")

    if not args.auto and not args.dry_run:
        print("\n💡 TIP: Review translations above, then run with --auto to apply")


if __name__ == "__main__":
    main()
