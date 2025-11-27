#!/usr/bin/env python3
"""
Update chunk files with execution timing metadata from timing_results.json
"""

import json
from pathlib import Path

# Config to chunk mapping
CONFIG_TO_CHUNK = {
    # Image configs
    "sd35_large": "devserver/schemas/chunks/output_image_sd35_large.json",
    "gpt_image_1": "devserver/schemas/chunks/output_image_gpt_image_1.json",
    "gemini_3_pro_image": "devserver/schemas/chunks/output_image_gemini_3_pro.json",
    "qwen": "devserver/schemas/chunks/output_image_qwen.json",

    # Video configs
    "ltx_video": "devserver/schemas/chunks/output_video_ltx.json",
    "wan22_video": "devserver/schemas/chunks/output_video_wan22.json",

    # Sound configs
    "acenet_t2instrumental": "devserver/schemas/chunks/output_audio_acenet.json",
    "stableaudio_open": "devserver/schemas/chunks/output_audio_stableaudio.json",
}


def update_chunk_with_timing(chunk_path: str, timing_data: dict):
    """
    Update a chunk file with timing metadata.

    Args:
        chunk_path: Path to the chunk JSON file
        timing_data: Dict with execution_time_firstrun and execution_time_average
    """
    chunk_file = Path(chunk_path)

    if not chunk_file.exists():
        print(f"✗ Chunk file not found: {chunk_path}")
        return False

    # Read chunk
    with open(chunk_file, 'r', encoding='utf-8') as f:
        chunk_data = json.load(f)

    # Update meta section
    if "meta" not in chunk_data:
        chunk_data["meta"] = {}

    chunk_data["meta"]["execution_time_firstrun"] = timing_data["execution_time_firstrun"]
    chunk_data["meta"]["execution_time_average"] = timing_data["execution_time_average"]

    # Write back with proper formatting
    with open(chunk_file, 'w', encoding='utf-8') as f:
        json.dump(chunk_data, f, indent=2, ensure_ascii=False)
        f.write('\n')  # Add final newline

    print(f"✓ Updated {chunk_file.name}")
    return True


def main():
    """Main execution function."""
    print("="*60)
    print("Update Chunks with Timing Metadata")
    print("="*60)

    # Check Stage 3 timing file
    stage3_file = Path("stage3_timing.json")
    if stage3_file.exists():
        with open(stage3_file, 'r') as f:
            stage3_timing = json.load(f)
        print(f"\n✓ Stage 3 timing found:")
        print(f"  First run:  {stage3_timing['execution_time_firstrun']}s")
        print(f"  Warm avg:   {stage3_timing['execution_time_average']}s")
        print(f"\nNote: Stage 3 timing is stored in {stage3_file}")
        print("      Frontend will add Stage3 + Stage4 times together")
    else:
        print(f"\n⚠ Stage 3 timing file not found: {stage3_file}")

    # Load Stage 4 timing results
    results_file = Path("timing_results.json")

    if not results_file.exists():
        print(f"\n✗ Results file not found: {results_file}")
        print("Please run measure_execution_times.sh first!")
        return 1

    with open(results_file, 'r') as f:
        timing_results = json.load(f)

    print(f"\nLoaded Stage 4 timing results for {len(timing_results)} configs\n")

    # Update each chunk
    updated_count = 0
    for config_id, timing_data in timing_results.items():
        chunk_path = CONFIG_TO_CHUNK.get(config_id)

        if not chunk_path:
            print(f"✗ No chunk mapping found for config: {config_id}")
            continue

        print(f"\nUpdating {config_id}:")
        print(f"  First run:  {timing_data['execution_time_firstrun']}s")
        print(f"  Warm avg:   {timing_data['execution_time_average']}s")

        if update_chunk_with_timing(chunk_path, timing_data):
            updated_count += 1

    # Print summary
    print("\n" + "="*60)
    print(f"Updated {updated_count}/{len(timing_results)} Stage 4 chunks successfully")
    print("="*60)

    # Remind about Stage 3
    stage3_file = Path("stage3_timing.json")
    if stage3_file.exists():
        print(f"\n✓ Stage 3 timing is available in: {stage3_file}")
        print("  Frontend should add Stage 3 + Stage 4 times for total duration")

    if updated_count == len(timing_results):
        print("\n✓ All chunks updated! You can now commit the changes.")
        return 0
    else:
        print(f"\n⚠ {len(timing_results) - updated_count} chunks failed to update")
        return 1


if __name__ == "__main__":
    exit(main())
