# LoRA Training mit FluxGym

Dieses Dokument erklärt, wie du **FluxGym** für professionelles LoRA-Training nutzen kannst. FluxGym bietet mehr Konfigurationsmöglichkeiten als das eingebaute Training und blockiert nicht die normale Bildgenerierung.

## Was ist FluxGym?

FluxGym ist eine benutzerfreundliche Web-Oberfläche für das Training von LoRA-Modellen. Es basiert auf den gleichen Kohya-Scripts wie unser eingebautes Training, bietet aber:

- Mehr Konfigurationsoptionen (Learning Rate, Rank, Alpha, etc.)
- Training im Hintergrund
- Unterstützung für verschiedene Modelle (SD3.5, SDXL, Flux, etc.)
- Fortschrittsanzeige mit Beispielbildern

## Installation

### Voraussetzungen

- Python 3.10+
- CUDA-fähige GPU (min. 24GB VRAM empfohlen)
- Git

### Schnellinstallation

```bash
# 1. Repository klonen
git clone https://github.com/cocktailpeanut/fluxgym
cd fluxgym

# 2. Installation starten (erstellt automatisch venv)
./install.sh
```

Die Installation dauert einige Minuten, da alle Abhängigkeiten heruntergeladen werden.

## Nutzung

### 1. FluxGym starten

```bash
cd fluxgym
./start.sh
```

FluxGym startet auf `http://localhost:7860`

### 2. Training konfigurieren

1. **Bilder hochladen**: Lade 10-50 hochwertige Bilder hoch
2. **Trigger-Wort festlegen**: z.B. `yoruba_art`
3. **Modell wählen**: SD3.5 Large, SDXL, oder Flux
4. **Parameter anpassen** (optional):
   - Learning Rate: 1e-4 (default) bis 4e-4 (aggressiver)
   - Network Rank: 16-64 (höher = mehr Details, aber größere Datei)
   - Epochs: 10-20 (je nach Bildanzahl)

### 3. Training starten

Klicke "Start Training" und beobachte den Fortschritt. Du siehst:
- Aktuelle Epoch/Step
- Loss-Werte
- Beispielbilder (alle paar Epochs)

### 4. LoRA verwenden

Nach dem Training findest du das LoRA unter:
```
fluxgym/outputs/<project_name>/
```

Kopiere die `.safetensors`-Datei nach:
```
/opt/SwarmUI/SwarmUI/Models/loras/
```

Dann kannst du das LoRA in ComfyUI/SwarmUI mit dem Trigger-Wort verwenden.

## Tipps für gutes Training

### Bildqualität

- Mindestens 512x512 Pixel, besser 1024x1024
- Konsistenter Stil über alle Bilder
- Variationen im Inhalt, aber nicht im Stil
- Keine Wasserzeichen oder Artefakte

### Training-Parameter

| VRAM | Batch Size | Gradient Checkpointing |
|------|------------|------------------------|
| 24GB | 1 | Ja |
| 48GB | 2-4 | Optional |
| 96GB | 4-8 | Nein |

### Trigger-Wörter

- Einzigartig und nicht im Vokabular (z.B. `sks_style`, `xyz_art`)
- Kurz und einfach zu merken
- Keine Leerzeichen

## Troubleshooting

### "CUDA out of memory"

- Batch Size auf 1 reduzieren
- Gradient Checkpointing aktivieren
- Resolution auf 512 reduzieren

### Training bricht ab

- Logs prüfen: `fluxgym/logs/`
- VRAM-Nutzung mit `nvidia-smi` prüfen
- Andere GPU-Programme beenden

### Schlechte Ergebnisse

- Mehr Bilder (min. 20)
- Mehr Epochs (15-20)
- Learning Rate reduzieren (1e-4)
- Bildqualität prüfen

## Weitere Ressourcen

- [FluxGym GitHub](https://github.com/cocktailpeanut/fluxgym)
- [Kohya SD-Scripts Wiki](https://github.com/kohya-ss/sd-scripts/wiki)
- [LoRA Training Guide (civitai)](https://civitai.com/articles/2799/the-ultimate-lora-training-guide)
