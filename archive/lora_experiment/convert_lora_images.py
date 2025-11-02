#!/usr/bin/env python3
"""
LoRA Image Converter
Konvertiert Bilder aus loraimg/ zu 768x768 JPG für LoRA Training
Output: lora_training_images/
"""

import os
import sys
from pathlib import Path
from PIL import Image

# Konfiguration
SOURCE_DIR = Path("/home/joerissen/ai/ai4artsed_webserver/loraimg")
OUTPUT_DIR = Path("/home/joerissen/ai/ai4artsed_webserver/lora_training_images")
TARGET_SIZE = (768, 768)
QUALITY = 95

# Unterstützte Formate
SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.webp', '.JPG', '.JPEG', '.PNG', '.WEBP'}

def convert_images():
    """Konvertiert alle Bilder aus SOURCE_DIR zu JPG"""
    
    # Erstelle Output-Verzeichnis
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Sammle alle Bilder
    image_files = []
    for file in sorted(SOURCE_DIR.iterdir()):
        if file.suffix in SUPPORTED_FORMATS:
            image_files.append(file)
    
    if not image_files:
        print(f"FEHLER: Keine Bilder gefunden in {SOURCE_DIR}")
        return 1
    
    print(f"Gefunden: {len(image_files)} Bilder")
    print(f"Konvertiere zu: {TARGET_SIZE[0]}x{TARGET_SIZE[1]} JPG")
    print(f"Output: {OUTPUT_DIR}\n")
    
    successful = 0
    failed = 0
    
    for idx, src_file in enumerate(image_files, 1):
        try:
            # Öffne Bild
            img = Image.open(src_file)
            
            # Konvertiere zu RGB (falls RGBA, P, etc.)
            if img.mode in ('RGBA', 'LA', 'P'):
                # Erstelle weißen Hintergrund
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                # Paste mit Alpha-Maske
                if img.mode in ('RGBA', 'LA'):
                    rgb_img.paste(img, mask=img.split()[-1])
                else:
                    rgb_img.paste(img)
                img = rgb_img
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize mit Aspect Ratio
            img.thumbnail(TARGET_SIZE, Image.Resampling.LANCZOS)
            
            # Zentriere auf weißem Hintergrund
            canvas = Image.new('RGB', TARGET_SIZE, (255, 255, 255))
            offset = (
                (TARGET_SIZE[0] - img.width) // 2,
                (TARGET_SIZE[1] - img.height) // 2
            )
            canvas.paste(img, offset)
            
            # Speichere als JPG
            output_filename = OUTPUT_DIR / f"lora_{idx:03d}.jpg"
            canvas.save(output_filename, 'JPEG', quality=QUALITY)
            
            print(f"✓ {idx:2d}. {src_file.name:50s} -> lora_{idx:03d}.jpg ({canvas.width}x{canvas.height})")
            successful += 1
            
        except Exception as e:
            print(f"✗ FEHLER bei {src_file.name}: {str(e)}")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"Konvertierung abgeschlossen!")
    print(f"  Erfolgreich: {successful}")
    print(f"  Fehler: {failed}")
    print(f"  Output: {OUTPUT_DIR}")
    print(f"{'='*60}\n")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(convert_images())
