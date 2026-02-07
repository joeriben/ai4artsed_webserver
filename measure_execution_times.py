#!/usr/bin/env python3
"""
Measure execution times for Stage4 output configs.
Runs each config 3 times and records:
- First run time (cold start with model loading)
- Average of runs 2-3 (warm runs)
"""

import requests
import json
import time
from pathlib import Path

# Test prompt
TEST_PROMPT = """Massive stone manor centered, light-colored ashlar facade, frontal orientation, rusticated ground floor, regularly spaced fenestration above, pitched roof apex. Lateral light from upper left models wall depth through graduated shadow. Foreground: cultivated fields in ochre-green, hedge rows receding linearly, middle-ground figures—man with scythe left, two women field-working center, child at entrance. Cattle and sheep distributed right. Distant hills transition blue-gray, sky gradates pale horizon to deeper tone zenith. Oil paint medium: architecture rendered precise linear construction with thin stone-surface glazes; landscape built additive pigment layers, warm-cool tonal modulation creating spatial recession. Light from upper left creates warm wall reflections, cool shadow accumulation in field depressions. Ground plane slopes gently downward from house foundation. Atmospheric perspective compresses background features. Hedge geometry creates orthogonal depth vectors. Human figures maintain natural posture alignment within compositional grid. Animal forms occupy lower right quadrant, static positioning. Sky occupies upper third, graduated luminosity. All forms receive volumetric modeling through shadow-highlight distribution. Surface texture differentiation: smooth stone versus vegetation texture variation. Spatial layering: house plane, middle-ground activity zone, distant landform recession. Light quality: warm diffuse illumination with sharp shadow edges indicating clear atmospheric conditions. No symbolic content, no narrative implication—purely spatial, material, and perceptual configuration as observable physical arrangement."""

# Server configuration
API_BASE_URL = "http://localhost:5000"

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


def measure_config_execution(config_id: str, num_runs: int = 3) -> dict:
    """
    Measure execution time for a specific config.

    Args:
        config_id: The output config ID
        num_runs: Number of runs to perform (default 3)

    Returns:
        Dict with firstrun time and average warm time
    """
    print(f"\n{'='*60}")
    print(f"Testing config: {config_id}")
    print(f"{'='*60}")

    execution_times = []

    for run_num in range(1, num_runs + 1):
        print(f"\nRun {run_num}/{num_runs}...", end=" ", flush=True)

        # Prepare request payload
        payload = {
            "user_input": TEST_PROMPT,
            "config_id": config_id,
        }

        # Measure execution time
        start_time = time.time()

        try:
            response = requests.post(
                f"{API_BASE_URL}/api/stage4_direct",
                json=payload,
                timeout=300  # 5 minute timeout
            )

            end_time = time.time()
            execution_time = end_time - start_time

            if response.status_code == 200:
                execution_times.append(execution_time)
                print(f"✓ Completed in {execution_time:.2f}s")
            else:
                print(f"✗ Failed with status {response.status_code}")
                print(f"Response: {response.text}")
                return None

        except requests.exceptions.Timeout:
            print(f"✗ Timeout after 5 minutes")
            return None
        except Exception as e:
            print(f"✗ Error: {e}")
            return None

    # Calculate results
    if len(execution_times) >= 3:
        firstrun_time = execution_times[0]
        warm_times = execution_times[1:]
        average_warm_time = sum(warm_times) / len(warm_times)

        print(f"\n{'─'*60}")
        print(f"Results for {config_id}:")
        print(f"  First run (cold start):  {firstrun_time:.2f}s")
        print(f"  Run 2:                   {execution_times[1]:.2f}s")
        print(f"  Run 3:                   {execution_times[2]:.2f}s")
        print(f"  Average warm time:       {average_warm_time:.2f}s")
        print(f"{'─'*60}")

        return {
            "execution_time_firstrun": round(firstrun_time, 2),
            "execution_time_average": round(average_warm_time, 2)
        }

    return None


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

    # Write back
    with open(chunk_file, 'w', encoding='utf-8') as f:
        json.dump(chunk_data, f, indent=2, ensure_ascii=False)

    print(f"✓ Updated {chunk_file.name}")
    return True


def main():
    """Main execution function."""
    print("="*60)
    print("Stage4 Execution Time Measurement Script")
    print("="*60)
    print(f"\nTest prompt length: {len(TEST_PROMPT)} characters")
    print(f"Number of configs to test: {len(CONFIG_TO_CHUNK)}")
    print(f"Runs per config: 3")
    print(f"\nEstimated total time: ~30-90 minutes (depends on models)")

    input("\nPress Enter to start measurements...")

    results = {}

    # Measure each config
    for config_id, chunk_path in CONFIG_TO_CHUNK.items():
        timing_data = measure_config_execution(config_id)

        if timing_data:
            results[config_id] = timing_data

            # Update chunk immediately after measurement
            if update_chunk_with_timing(chunk_path, timing_data):
                print(f"✓ Chunk updated with timing data")
        else:
            print(f"✗ Failed to measure {config_id}")

        # Small delay between configs
        print("\nWaiting 5 seconds before next config...")
        time.sleep(5)

    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    for config_id, timing_data in results.items():
        print(f"\n{config_id}:")
        print(f"  First run:  {timing_data['execution_time_firstrun']}s")
        print(f"  Warm avg:   {timing_data['execution_time_average']}s")

    print("\n" + "="*60)
    print(f"Completed: {len(results)}/{len(CONFIG_TO_CHUNK)} configs")
    print("="*60)


if __name__ == "__main__":
    main()
