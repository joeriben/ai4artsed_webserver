#!/usr/bin/env python3
"""
Analyze context prompts: Compare legacy prompts with current configs
"""
import json
from pathlib import Path
from typing import Dict, List, Any
import re

# Mapping of legacy node names to current config names
LEGACY_TO_CONFIG_MAPPING = {
    'arts_bauhaus': 'bauhaus',
    'arts_dada': 'dada',
    'arts_renaissance': 'renaissance',
    'arts_expressionism': 'expressionism',
    'arts_confucian_literati': 'confucianliterati',
    'arts_yoruba': None,  # Deactivated
    'arts_traditional_chinese': None,  # Not found in active configs
    'aesthetics_cliche_filter': 'clichéfilter_v2',
    'aesthetics_overdrive': 'overdrive',
    'aesthetics_harmonizer': 'hunkydoryharmonizer',
    'aesthetics_quantum': None,  # Deactivated
    'aesthetics_technical': 'technicaldrawing',
    'aesthetics_surreal': 'surrealization',
    'semantics_youth_language': 'jugendsprache',
    'semantics_pig_latin': 'piglatin',
    'semantics_stille_post': 'stillepost',
    'semantics_opposite': 'theopposite',
    'technical_vector': 'splitandcombinespherical',
}

def load_legacy_contexts(legacy_file: Path) -> Dict[str, str]:
    """Extract all input_context prompts from legacy workflows"""
    with open(legacy_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    contexts = {}

    # Iterate through all categories
    for category_name, category_data in data.items():
        if not isinstance(category_data, dict) or 'workflows' not in category_data:
            continue

        # Iterate through workflows
        for workflow in category_data['workflows']:
            if 'nodes' not in workflow:
                continue

            # Iterate through node types
            for node_type, nodes in workflow['nodes'].items():
                if not nodes or not isinstance(nodes, list):
                    continue

                # Get first node with input_context
                for node in nodes:
                    if 'input_context' in node and node['input_context']:
                        # Store by node type
                        if node_type not in contexts:
                            contexts[node_type] = node['input_context']
                        break

    return contexts

def load_current_configs(config_dir: Path) -> Dict[str, Dict[str, Any]]:
    """Load all current config files"""
    configs = {}

    for config_file in config_dir.glob('*.json'):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                config_name = config_file.stem

                # Extract context - handle both string and dict formats
                context = data.get('context', '')
                context_de = data.get('context_de', '')

                # If context is a dict, try to extract 'en' or 'default' key
                if isinstance(context, dict):
                    context = context.get('en', context.get('default', ''))
                if isinstance(context_de, dict):
                    context_de = context_de.get('de', context_de.get('default', ''))

                configs[config_name] = {
                    'context': str(context) if context else '',
                    'context_de': str(context_de) if context_de else '',
                    'name': data.get('name', ''),
                    'description': data.get('description', ''),
                    'file': str(config_file)
                }
        except Exception as e:
            print(f"Error loading {config_file}: {e}")

    return configs

def is_nonsensical_context(context: str) -> tuple[bool, str]:
    """Check if context is nonsensical or placeholder"""
    if not context or context.strip() == '':
        return True, "Empty context"

    # Check for translation placeholders
    if re.search(r'translate\s+this', context, re.IGNORECASE):
        return True, "Contains 'translate this' placeholder"

    # Check for generic/short contexts
    if len(context.strip()) < 50:
        return True, f"Too short ({len(context)} chars)"

    # Check for TODO markers
    if re.search(r'TODO|FIXME|XXX|\?\?\?', context, re.IGNORECASE):
        return True, "Contains TODO/placeholder markers"

    return False, "OK"

def compare_contexts(legacy_contexts: Dict[str, str],
                     current_configs: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Compare legacy and current contexts"""
    results = []

    # Check each legacy context
    for legacy_name, legacy_context in legacy_contexts.items():
        # Find corresponding current config
        current_config_name = LEGACY_TO_CONFIG_MAPPING.get(legacy_name)

        result = {
            'legacy_name': legacy_name,
            'current_config': current_config_name,
            'status': 'unknown'
        }

        if current_config_name is None:
            result['status'] = 'deactivated'
            result['note'] = 'Config deactivated or not found in mapping'
            results.append(result)
            continue

        if current_config_name not in current_configs:
            result['status'] = 'missing'
            result['note'] = f'Config file {current_config_name}.json not found'
            results.append(result)
            continue

        current_config = current_configs[current_config_name]
        current_context = current_config['context']
        current_context_de = current_config['context_de']

        # Check for issues
        is_nonsense, nonsense_reason = is_nonsensical_context(current_context)
        is_nonsense_de, nonsense_reason_de = is_nonsensical_context(current_context_de)

        # Compare lengths
        legacy_len = len(legacy_context)
        current_len = len(current_context)
        current_de_len = len(current_context_de)

        # Determine status
        if is_nonsense:
            result['status'] = 'broken'
            result['issue'] = f"English context: {nonsense_reason}"
        elif is_nonsense_de:
            result['status'] = 'missing_translation'
            result['issue'] = f"German context: {nonsense_reason_de}"
        elif abs(legacy_len - current_len) > legacy_len * 0.5:
            # More than 50% difference in length
            result['status'] = 'significant_change'
            result['issue'] = f"Length difference: legacy={legacy_len}, current={current_len}"
        else:
            result['status'] = 'ok'

        result['legacy_length'] = legacy_len
        result['current_length'] = current_len
        result['current_de_length'] = current_de_len
        result['legacy_preview'] = legacy_context[:100] + '...'
        result['current_preview'] = current_context[:100] + '...' if current_context else '[EMPTY]'
        result['current_de_preview'] = current_context_de[:100] + '...' if current_context_de else '[EMPTY]'

        results.append(result)

    # Check for configs without legacy counterpart
    all_current_configs = set(current_configs.keys())
    all_mapped_configs = set(v for v in LEGACY_TO_CONFIG_MAPPING.values() if v)
    unmapped_configs = all_current_configs - all_mapped_configs

    for config_name in unmapped_configs:
        current_config = current_configs[config_name]
        is_nonsense, nonsense_reason = is_nonsensical_context(current_config['context'])
        is_nonsense_de, nonsense_reason_de = is_nonsensical_context(current_config['context_de'])

        result = {
            'legacy_name': None,
            'current_config': config_name,
            'status': 'new_config',
            'current_length': len(current_config['context']),
            'current_de_length': len(current_config['context_de']),
            'current_preview': current_config['context'][:100] + '...' if current_config['context'] else '[EMPTY]',
            'current_de_preview': current_config['context_de'][:100] + '...' if current_config['context_de'] else '[EMPTY]'
        }

        if is_nonsense:
            result['issue'] = f"English context: {nonsense_reason}"
        if is_nonsense_de:
            if 'issue' in result:
                result['issue'] += f" | German context: {nonsense_reason_de}"
            else:
                result['issue'] = f"German context: {nonsense_reason_de}"

        results.append(result)

    return results

def generate_report(results: List[Dict[str, Any]]) -> str:
    """Generate markdown report"""
    report = []
    report.append("# Context Prompts Analysis Report")
    report.append(f"\nGenerated: {Path(__file__).name}\n")

    # Summary statistics
    status_counts = {}
    for result in results:
        status = result['status']
        status_counts[status] = status_counts.get(status, 0) + 1

    report.append("## Summary\n")
    report.append(f"Total configs analyzed: {len(results)}\n")
    for status, count in sorted(status_counts.items()):
        report.append(f"- **{status}**: {count}")
    report.append("\n")

    # Detailed results by status
    statuses_order = ['broken', 'missing_translation', 'significant_change', 'missing', 'deactivated', 'new_config', 'ok']

    for status in statuses_order:
        matching = [r for r in results if r['status'] == status]
        if not matching:
            continue

        report.append(f"\n## Status: {status.upper()} ({len(matching)})\n")

        for result in sorted(matching, key=lambda x: str(x.get('current_config') or x.get('legacy_name') or '')):
            legacy = result.get('legacy_name', 'N/A')
            current = result.get('current_config', 'N/A')

            report.append(f"\n### {current} (Legacy: {legacy})\n")

            if 'issue' in result:
                report.append(f"**Issue:** {result['issue']}\n")

            if 'note' in result:
                report.append(f"**Note:** {result['note']}\n")

            if 'legacy_length' in result:
                report.append(f"- Legacy length: {result['legacy_length']} chars")
            if 'current_length' in result:
                report.append(f"- Current EN length: {result['current_length']} chars")
            if 'current_de_length' in result:
                report.append(f"- Current DE length: {result['current_de_length']} chars")

            report.append("\n**Previews:**\n")
            if 'legacy_preview' in result:
                report.append(f"- Legacy: `{result['legacy_preview']}`")
            if 'current_preview' in result:
                report.append(f"- Current EN: `{result['current_preview']}`")
            if 'current_de_preview' in result:
                report.append(f"- Current DE: `{result['current_de_preview']}`")

            report.append("\n")

    return "\n".join(report)

def main():
    base_path = Path(__file__).parent.parent
    legacy_file = base_path / 'docs/archive/reference/prompt_interception_categorized.json'
    config_dir = Path(__file__).parent / 'schemas/configs/interception'
    output_file = base_path / 'docs/CONTEXT_PROMPTS_STATUS.md'

    print("Loading legacy contexts...")
    legacy_contexts = load_legacy_contexts(legacy_file)
    print(f"Found {len(legacy_contexts)} legacy contexts")

    print("\nLoading current configs...")
    current_configs = load_current_configs(config_dir)
    print(f"Found {len(current_configs)} current configs")

    print("\nComparing contexts...")
    results = compare_contexts(legacy_contexts, current_configs)

    print("\nGenerating report...")
    report = generate_report(results)

    # Write report
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\nReport written to: {output_file}")

    # Print summary to console
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    status_counts = {}
    for result in results:
        status = result['status']
        status_counts[status] = status_counts.get(status, 0) + 1

    for status, count in sorted(status_counts.items()):
        print(f"{status:20s}: {count:3d}")

if __name__ == '__main__':
    main()
