#!/usr/bin/env python3
"""
Resize new background images for config previews

Usage:
    python3 scripts/resize_new_backgrounds.py
"""

from PIL import Image
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
PREVIEW_DIR = PROJECT_ROOT / "public/ai4artsed-frontend/public/config-previews"

# Settings
TARGET_SIZE = (300, 300)
PNG_COMPRESS_LEVEL = 9

def resize_image(input_path, output_path):
    """Resize and optimize a single image"""
    print(f"Processing: {input_path.name}")

    with Image.open(input_path) as img:
        # Convert to RGB if necessary (for JPG input)
        if img.mode in ('RGBA', 'LA', 'P'):
            # Create white background for transparency
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        original_size = img.size
        print(f"  Original: {original_size[0]}x{original_size[1]}")

        # Resize with high-quality resampling
        img_resized = img.resize(TARGET_SIZE, Image.Resampling.LANCZOS)

        # Save as PNG
        img_resized.save(
            output_path,
            "PNG",
            optimize=True,
            compress_level=PNG_COMPRESS_LEVEL
        )

    # File size info
    input_size = input_path.stat().st_size
    output_size = output_path.stat().st_size
    reduction = ((input_size - output_size) / input_size) * 100

    print(f"  Output: {TARGET_SIZE[0]}x{TARGET_SIZE[1]}")
    print(f"  Size: {input_size/1024/1024:.2f}M → {output_size/1024:.0f}KB ({reduction:.1f}% reduction)")
    print()

def main():
    print("=" * 70)
    print("🖼️  RESIZE NEW BACKGROUND IMAGES")
    print("=" * 70)
    print()

    # Define images to process
    images_to_process = [
        ("overdrive_new.png", "overdrive.png", "Overdrive"),
        ("jugendsprache_new.jpg", "jugendsprache.png", "Jugendsprache"),
        ("yorubaheritage_new.jpg", "yorubaheritage.png", "Yoruba Heritage"),
        ("renaissance_new.png", "renaissance.png", "Renaissance"),
        ("piglatin_new.jpg", "piglatin.png", "Pig Latin"),
    ]

    processed_count = 0
    for input_name, output_name, display_name in images_to_process:
        input_path = PREVIEW_DIR / input_name
        if input_path.exists():
            resize_image(input_path, PREVIEW_DIR / output_name)
            print(f"✅ {display_name} background updated")
            processed_count += 1
        else:
            print(f"⏭️  {input_name} not found (skipped)")

    print("=" * 70)
    print(f"✅ {processed_count} backgrounds resized and optimized!")
    print("=" * 70)

if __name__ == "__main__":
    main()
