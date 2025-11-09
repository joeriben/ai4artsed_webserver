"""
Add instruction_type field to all interception configs

This ensures configs explicitly declare their instruction type,
making the system more transparent and allowing per-config overrides.
"""

import json
from pathlib import Path

def add_instruction_type_to_config(config_path: Path):
    """Add instruction_type field to a single config"""

    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # Check if already has instruction_type
    if 'instruction_type' in config:
        print(f"✓ {config_path.stem} - already has instruction_type: {config['instruction_type']}")
        return False

    # Determine instruction type based on config name
    config_name = config_path.stem.lower()

    if 'passthrough' in config_name:
        instruction_type = "passthrough"
    else:
        instruction_type = "artistic_transformation"

    # Insert instruction_type after pipeline field
    new_config = {}
    for key, value in config.items():
        new_config[key] = value
        if key == 'pipeline':
            new_config['instruction_type'] = instruction_type

    # Write back
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(new_config, f, indent=2, ensure_ascii=False)
        f.write('\n')  # Add newline at end

    print(f"✓ {config_path.stem} - added instruction_type: {instruction_type}")
    return True

def main():
    """Add instruction_type to all interception configs"""

    configs_dir = Path(__file__).parent / 'schemas' / 'configs' / 'interception'

    if not configs_dir.exists():
        print(f"❌ Config directory not found: {configs_dir}")
        return

    config_files = sorted(configs_dir.glob('*.json'))

    print("=" * 80)
    print("ADDING instruction_type TO INTERCEPTION CONFIGS")
    print("=" * 80)
    print(f"\nFound {len(config_files)} config files\n")

    modified_count = 0
    skipped_count = 0

    for config_file in config_files:
        try:
            was_modified = add_instruction_type_to_config(config_file)
            if was_modified:
                modified_count += 1
            else:
                skipped_count += 1
        except Exception as e:
            print(f"❌ {config_file.stem} - ERROR: {e}")

    print("\n" + "=" * 80)
    print(f"✅ DONE: Modified {modified_count} configs, skipped {skipped_count}")
    print("=" * 80)

if __name__ == '__main__':
    main()
