#!/usr/bin/env python3
"""
Optimize config preview images for faster web loading

Usage:
    python3 scripts/optimize_preview_images.py

What it does:
- Resizes images from 1024x1024 to 300x300 (suitable for preview bubbles)
- Optimizes PNG compression (max level)
- Creates backups of original images in originals_backup/
- Reduces total size by ~90% (30MB → 2.6MB)

Author: Claude (AI4ArtsEd DevServer)
Date: 2025-11-24
"""

from PIL import Image
import os
from pathlib import Path

# Paths (relative to project root)
PROJECT_ROOT = Path(__file__).parent.parent
SOURCE_DIR = PROJECT_ROOT / "public/ai4artsed-frontend/public/config-previews"
BACKUP_DIR = SOURCE_DIR / "originals_backup"

# Settings
TARGET_SIZE = (300, 300)  # Optimal size for preview bubbles
OPTIMIZE = True
PNG_COMPRESS_LEVEL = 9  # Max PNG compression (0-9)

def main():
    print("=" * 70)
    print("🖼️  CONFIG PREVIEW IMAGE OPTIMIZER")
    print("=" * 70)
    print()

    # Verify source directory exists
    if not SOURCE_DIR.exists():
        print(f"❌ Error: Source directory not found: {SOURCE_DIR}")
        return

    # Create backup directory
    BACKUP_DIR.mkdir(exist_ok=True)
    print(f"📁 Source: {SOURCE_DIR}")
    print(f"📁 Backup: {BACKUP_DIR}")
    print(f"🎯 Target size: {TARGET_SIZE[0]}x{TARGET_SIZE[1]}")
    print()

    # Get all PNG files
    png_files = list(SOURCE_DIR.glob("*.png"))

    if not png_files:
        print("⚠️  No PNG files found in source directory")
        return

    print(f"🖼️  Found {len(png_files)} PNG files")
    print()

    total_original = 0
    total_optimized = 0
    processed = 0

    for png_file in png_files:
        if png_file.parent == BACKUP_DIR:
            continue  # Skip backup directory

        try:
            # Get original size
            original_size = png_file.stat().st_size
            total_original += original_size

            # Backup original (if not already backed up)
            backup_path = BACKUP_DIR / png_file.name
            if not backup_path.exists():
                import shutil
                shutil.copy2(png_file, backup_path)
                print(f"💾 Backed up: {png_file.name}")
            else:
                print(f"⏭️  Already backed up: {png_file.name}")

            # Open and resize
            with Image.open(png_file) as img:
                original_dimensions = img.size

                # Resize with high-quality resampling (LANCZOS)
                img_resized = img.resize(TARGET_SIZE, Image.Resampling.LANCZOS)

                # Save optimized
                img_resized.save(
                    png_file,
                    "PNG",
                    optimize=OPTIMIZE,
                    compress_level=PNG_COMPRESS_LEVEL
                )

            # Get new size
            new_size = png_file.stat().st_size
            total_optimized += new_size
            reduction = ((original_size - new_size) / original_size) * 100

            print(f"   ✅ {original_dimensions[0]}x{original_dimensions[1]} → {TARGET_SIZE[0]}x{TARGET_SIZE[1]}")
            print(f"      {original_size/1024/1024:.2f}M → {new_size/1024:.0f}KB ({reduction:.1f}% reduction)")
            print()

            processed += 1

        except Exception as e:
            print(f"   ❌ Error processing {png_file.name}: {e}")
            print()

    # Summary
    print("=" * 70)
    print("📊 OPTIMIZATION SUMMARY")
    print("=" * 70)
    print(f"Files processed: {processed}/{len(png_files)}")
    print(f"Original total:  {total_original/1024/1024:.2f}M")
    print(f"Optimized total: {total_optimized/1024/1024:.2f}M")
    print(f"Total reduction: {((total_original - total_optimized) / total_original) * 100:.1f}%")
    print(f"Backups saved:   {BACKUP_DIR}")
    print()
    print("✅ Optimization complete!")

if __name__ == "__main__":
    main()
