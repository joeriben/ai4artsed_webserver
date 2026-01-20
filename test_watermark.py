#!/usr/bin/env python3
"""
Test script for watermark functionality.
Run after server restart: python3 test_watermark.py
"""
import sys
sys.path.insert(0, 'devserver')

from pathlib import Path
from my_app.services.watermark_service import WatermarkService

# Find most recent generated image
import glob
images = sorted(glob.glob("exports/json/2026-*/*/*.png"), key=lambda x: Path(x).stat().st_mtime, reverse=True)

if not images:
    print("Keine Bilder gefunden. Generiere erst ein Bild über die Weboberfläche.")
    sys.exit(1)

latest = Path(images[0])
print(f"Teste: {latest}")
print(f"Erstellt: {latest.stat().st_mtime}")

service = WatermarkService("AI4ArtsEd")
extracted = service.extract_watermark(latest.read_bytes())

if extracted == "AI4ArtsEd":
    print(f"\n✅ ERFOLG: Watermark '{extracted}' gefunden!")
else:
    print(f"\n❌ FEHLER: Watermark nicht gefunden ('{extracted}')")
    print("   Server neustarten und neues Bild generieren.")
