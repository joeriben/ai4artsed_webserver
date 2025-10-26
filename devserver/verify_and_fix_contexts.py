"""
Verify and fix context fields in pipeline configs
by comparing with legacy workflow sources
"""
import json
from pathlib import Path

schemas_path = Path("schemas")
configs_path = schemas_path / "configs"
workflows_path = Path("/home/joerissen/ai/ai4artsed_webserver/workflows")

# Map of config names to their expected legacy workflow paths (from meta.legacy_source)
configs_to_check = []

# Load all configs
for config_file in sorted(configs_path.glob("*.json")):
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)

    legacy_source = config.get('meta', {}).get('legacy_source')
    if legacy_source:
        configs_to_check.append({
            'config_name': config_file.stem,
            'config_path': config_file,
            'legacy_source': legacy_source,
            'current_context': config.get('context', '')
        })

print(f"Found {len(configs_to_check)} configs with legacy sources\n")

# Check each config
issues_found = []

for item in configs_to_check:
    legacy_path = workflows_path / item['legacy_source']

    if not legacy_path.exists():
        issues_found.append({
            'config': item['config_name'],
            'issue': 'Legacy workflow file not found',
            'legacy_path': str(legacy_path)
        })
        continue

    # Load legacy workflow
    with open(legacy_path, 'r', encoding='utf-8') as f:
        legacy_workflow = json.load(f)

    # Find the prompt_interception node with context (usually node 41 or similar)
    legacy_context = None
    context_node_id = None

    for node_id, node_data in legacy_workflow.items():
        if node_data.get('class_type') == 'ai4artsed_prompt_interception':
            # Look for the node with style_prompt containing transformation instructions
            style_prompt = node_data.get('inputs', {}).get('style_prompt', '')

            # This is likely the manipulation node if it has transformation instructions
            if 'transform' in style_prompt.lower() or 'pig latin' in style_prompt.lower() or 'ethical' in style_prompt.lower():
                # Now find the input_context - it might be a reference to another node
                input_context = node_data.get('inputs', {}).get('input_context', '')

                if isinstance(input_context, list):
                    # It's a reference to another node [node_id, output_index]
                    ref_node_id = str(input_context[0])
                    if ref_node_id in legacy_workflow:
                        ref_node = legacy_workflow[ref_node_id]
                        if ref_node.get('class_type') in ['PrimitiveString', 'PrimitiveStringMultiline']:
                            # Get value from referenced node
                            if isinstance(ref_node.get('inputs', {}).get('value'), list):
                                # It's another reference
                                ref2_node_id = str(ref_node['inputs']['value'][0])
                                if ref2_node_id in legacy_workflow:
                                    legacy_context = legacy_workflow[ref2_node_id].get('inputs', {}).get('value', '')
                            else:
                                legacy_context = ref_node.get('inputs', {}).get('value', '')
                elif isinstance(input_context, str):
                    legacy_context = input_context

                if legacy_context:
                    context_node_id = node_id
                    break

    if legacy_context:
        # Compare with current config
        current_context = item['current_context']

        # Normalize for comparison (strip whitespace)
        legacy_normalized = ' '.join(legacy_context.split())
        current_normalized = ' '.join(current_context.split())

        if legacy_normalized != current_normalized:
            # Check length difference
            if len(current_context) < 50 and len(legacy_context) > 100:
                # Probably wrong - current is too short
                issues_found.append({
                    'config': item['config_name'],
                    'issue': 'Context too short (likely incorrect)',
                    'current_length': len(current_context),
                    'legacy_length': len(legacy_context),
                    'current_preview': current_context[:100],
                    'legacy_preview': legacy_context[:100],
                    'fix_needed': True,
                    'correct_context': legacy_context
                })
            elif abs(len(current_context) - len(legacy_context)) > 100:
                # Significant difference
                issues_found.append({
                    'config': item['config_name'],
                    'issue': 'Context differs significantly from legacy',
                    'current_length': len(current_context),
                    'legacy_length': len(legacy_context),
                    'current_preview': current_context[:100],
                    'legacy_preview': legacy_context[:100],
                    'fix_needed': True,
                    'correct_context': legacy_context
                })

# Report findings
print("=" * 80)
print("CONTEXT VERIFICATION REPORT")
print("=" * 80)

if not issues_found:
    print("\n✓ All contexts appear correct!")
else:
    print(f"\n⚠ Found {len(issues_found)} issues:\n")

    for i, issue in enumerate(issues_found, 1):
        print(f"{i}. {issue['config']}")
        print(f"   Issue: {issue['issue']}")
        if 'current_length' in issue:
            print(f"   Current length: {issue['current_length']} chars")
            print(f"   Legacy length: {issue['legacy_length']} chars")
            print(f"   Current: {issue['current_preview']}...")
            print(f"   Legacy: {issue['legacy_preview']}...")
        print()

# Offer to fix
print("\n" + "=" * 80)
print("FIXES TO APPLY")
print("=" * 80)

fixes_to_apply = [issue for issue in issues_found if issue.get('fix_needed')]

if fixes_to_apply:
    print(f"\n{len(fixes_to_apply)} configs need to be fixed:\n")
    for fix in fixes_to_apply:
        print(f"  - {fix['config']}")

    print(f"\nWould you like to apply these fixes? (This will update the config files)")
    print(f"This script is for VERIFICATION ONLY. Fixes will be applied manually.")
else:
    print("\n✓ No fixes needed!")
