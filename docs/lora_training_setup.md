# LoRA-Trainingsumgebung für den AI4ArtsEd Webserver

Diese Anleitung erklärt Schritt für Schritt, wie du eine Trainingsumgebung für Low-Rank-Adaptation-(LoRA)-Modelle einrichtest, trainierst und die Ergebnisse in den AI4ArtsEd-Webserver integrierst. Die Schritte decken sowohl das Training auf demselben Host wie der Webserver als auch auf einer separaten Maschine oder in der Cloud ab.

## 1. Überblick: Wann lohnt sich LoRA?

LoRA ermöglicht es, große Diffusionsmodelle wie Stable Diffusion mit wenigen zusätzlichen Parametern für neue Stile oder Motive anzupassen. Statt komplette Modelle zu feintunen, werden kleine Zusatzgewichte trainiert, die später als `.safetensors`-Datei geladen werden. Dadurch:

- verkürzt sich die Trainingszeit drastisch,
- sinkt der GPU-Speicherbedarf,
- lassen sich mehrere Varianten parallel verwalten.

## 2. Voraussetzungen prüfen

| Komponente | Empfehlung |
| --- | --- |
| **GPU** | NVIDIA-GPU mit >= 12 GB VRAM (24 GB komfortabel); aktuelle CUDA-Treiber (>= 12.1) |
| **Betriebssystem** | Linux (getestet mit Ubuntu 22.04); Windows funktioniert mit WSL2 |
| **Python** | 3.10 oder 3.11 |
| **Speicherplatz** | 50–200 GB je nach Datensatz |
| **Zugriff** | Optional: Hugging Face-Token für geschützte Modelle |

> Prüfe mit `nvidia-smi`, ob die GPU korrekt erkannt wird. Falls der Webserver auf demselben Host läuft, stelle sicher, dass während des Trainings ausreichend VRAM frei ist.

## 3. Umgebung auf dem Webserver-Host einrichten

### Option A: Automatisiertes Setup (empfohlen)

Nutze das mitgelieferte Skript, um Systemabhängigkeiten zu installieren und eine dedizierte Python-Umgebung mit allen LoRA-Paketen einzurichten:

```bash
cd /workspace/ai4artsed_webserver
./scripts/install_lora_env.sh
```

- Das Skript legt standardmäßig ein `venv-lora/`-Verzeichnis an, installiert die Pakete aus [`requirements/lora.txt`](../requirements/lora.txt) und zeigt dir die nächsten Schritte an (`accelerate config`, `huggingface-cli login`).
- Mit `./scripts/install_lora_env.sh --help` siehst du weitere Optionen (z. B. abweichender Python-Pfad oder das Überspringen der Systempakete).

### Option B: Manuell

1. **Systempakete aktualisieren**
   ```bash
   sudo apt update && sudo apt install -y build-essential git python3-venv python3-dev ffmpeg libgl1
   ```

2. **Isolierte Python-Umgebung erstellen** (damit der Webserver nicht beeinflusst wird)
   ```bash
   cd /workspace/ai4artsed_webserver
   python3 -m venv venv-lora
   source venv-lora/bin/activate
   python -m pip install --upgrade pip wheel setuptools
   ```

3. **Trainingstools installieren**
   ```bash
   python -m pip install -r requirements/lora.txt
   ```

4. **Hugging Face authentifizieren (optional)**
   ```bash
   huggingface-cli login
   ```
   So kannst du auch geschützte Basis-Modelle (z. B. `stabilityai/stable-diffusion-xl-base-1.0`) laden.

## 4. Datensatz vorbereiten

1. **Datenstruktur**
   ```text
   training_data/
     my_concept/
       images/
         0001.png
         0002.png
       metadata.jsonl
   ```

2. **Metadaten-Datei (`metadata.jsonl`)**
   Jede Zeile enthält ein Prompt/Beschreibungspaar:
   ```json
   {"file": "0001.png", "prompt": "portrait of <my_token> in watercolor style"}
   {"file": "0002.png", "prompt": "close up photo of <my_token> with dramatic lighting"}
   ```
   Ersetze `<my_token>` durch dein Wunsch-Token. Vermeide Sondersymbole.

3. **Qualitätskontrolle**
   - Mindestens 20–30 hochwertige Bilder.
   - Einheitliche Auflösung (512×512 oder 768×768 für SDXL).
   - Entferne unscharfe oder nicht passende Bilder.

4. **Optional: Prompt-Negativliste**
   Speichere negative Prompts (z. B. "blurry, low quality") in einer Textdatei, um sie beim Training zu berücksichtigen.

## 5. Trainingsskript verwenden

Anstatt ein eigenes Skript zu erfinden, nutzen wir das bewährte Diffusers-Skript `train_text_to_image_lora.py` und passen es minimal an.

1. **Skript abrufen**
   ```bash
   mkdir -p training
   curl -o training/train_text_to_image_lora.py \
     https://raw.githubusercontent.com/huggingface/diffusers/main/examples/text_to_image/train_text_to_image_lora.py
   ```

2. **Patch für JSONL-Datensätze anwenden** (damit das Skript dein `metadata.jsonl` liest)
   ```bash
   apply_patch <<'PATCH'
   *** Begin Patch
   *** Update File: training/train_text_to_image_lora.py
   @@
   -    dataset = load_dataset(
   -        args.dataset_name,
   -        args.dataset_config_name,
   -        cache_dir=args.cache_dir,
   -    ) if args.dataset_name is not None else load_dataset(
   -        "imagefolder",
   -        data_dir=args.train_data_dir,
   -        cache_dir=args.cache_dir,
   -    )
   +    if args.train_data_dir is not None and (Path(args.train_data_dir) / "metadata.jsonl").exists():
   +        dataset = load_dataset(
   +            "json",
   +            data_files=str(Path(args.train_data_dir) / "metadata.jsonl"),
   +            cache_dir=args.cache_dir,
   +        )
   +        column_names = dataset["train"].column_names
   +        image_column = "file"
   +        caption_column = "prompt"
   +    else:
   +        dataset = load_dataset(
   +            args.dataset_name,
   +            args.dataset_config_name,
   +            cache_dir=args.cache_dir,
   +        ) if args.dataset_name is not None else load_dataset(
   +            "imagefolder",
   +            data_dir=args.train_data_dir,
   +            cache_dir=args.cache_dir,
   +        )
   +        column_names = dataset["train"].column_names
   +        image_column = args.image_column or column_names[0]
   +        caption_column = args.caption_column or column_names[1]
   *** End Patch
   PATCH
   ```

   > Tipp: Falls das Skript den Import `from pathlib import Path` nicht enthält, füge ihn zu den anderen Imports hinzu, bevor du das Training startest.

   Die Änderung sorgt dafür, dass das Skript bei vorhandener `metadata.jsonl` automatisch Prompts und Dateinamen nutzt.

3. **Beschleuniger konfigurieren**
   ```bash
   accelerate config
   ```
   Wähle z. B. "single GPU" und 16-bit Mixed Precision.

4. **Training starten**
   ```bash
   accelerate launch training/train_text_to_image_lora.py \
     --pretrained_model_name_or_path="runwayml/stable-diffusion-v1-5" \
     --train_data_dir="/workspace/datasets/training_data/my_concept" \
     --resolution=512 \
     --train_batch_size=1 \
     --gradient_accumulation_steps=4 \
     --learning_rate=1e-4 \
     --lr_scheduler="cosine" \
     --lr_warmup_steps=100 \
     --max_train_steps=2000 \
     --checkpointing_steps=500 \
     --output_dir="outputs/lora/my_concept" \
     --validation_prompt="portrait of <my_token>" \
     --report_to="wandb"
   ```

   - Passe `resolution` an das Zielmodell an (512 für SD 1.5, 768 für SDXL).
   - Nutze `--mixed_precision=fp16`, falls Speicher knapp ist.
   - Für DreamBooth-Style: `--class_prompt` und `--with_prior_preservation` setzen.

5. **Trainingsfortschritt beobachten**
   - `wandb`-Dashboard oder TensorBoard (`--report_to tensorboard`).
   - Konsolen-Logs zeigen Loss-Werte und Beispielbilder.

6. **Modell speichern**
   Das Skript legt im `output_dir` Unterordner wie `checkpoint-1500` an. Nach dem Training findest du LoRA-Gewichte unter:
   ```text
   outputs/lora/my_concept/pytorch_lora_weights.safetensors
   outputs/lora/my_concept/adapter_config.json
   ```
   Kopiere beide Dateien zusammen, damit andere Tools wissen, wie das LoRA aufgebaut ist.

## 6. Training auf externer Hardware oder in der Cloud

1. **GPU-Instanz wählen**
   - Anbieter wie RunPod, Vast.ai, Lambda Labs oder AWS EC2.
   - Wähle ein Image mit aktuellem CUDA + PyTorch. Viele Anbieter stellen `diffusers`-Container bereit.

2. **Repository & Daten synchronisieren**
   ```bash
   git clone https://github.com/<dein-org>/ai4artsed_webserver.git
   rsync -avz ./training_data user@remote:/workspace/datasets/training_data
   ```

3. **Training wie in Abschnitt 5**
   - Gleiche Befehle, ggf. Pfade anpassen.
   - Verwende `wandb` oder `tensorboard` für Remote-Monitoring.

4. **Ergebnisse zurückkopieren**
   ```bash
   scp -r user@remote:/workspace/ai4artsed_webserver/outputs/lora/my_concept \
       ./outputs/lora/
   ```

## 7. LoRA Studio Webinterface

Der Webserver stellt unter [`/lora`](../public/lora/index.html) eine schlanke Oberfläche bereit, um Trainingsjobs zu konfigurieren und für das Team zu dokumentieren.

1. **Aufrufen** – Starte den Webserver (`./start_webserver.sh`) und öffne `https://<dein-host>/lora`.
2. **Projekt konfigurieren** – Vergib Projektname und (optional) ein Trigger-Token. Wähle das Basismodell aus den eingebauten Presets.
3. **Datensatz importieren** – Lädt ein neues ZIP (Bilder + `metadata.jsonl`) direkt auf den Server oder greif auf vorhandene Datensätze zurück.
4. **Hyperparameter festlegen** – Wähle zunächst eine der vorkonfigurierten Voreinstellungen, die typische Foto- und Kunst-Workflows abdecken, und passe bei Bedarf einzelne Werte an. Die Oberfläche zeigt den resultierenden `accelerate launch`-Befehl live an.

   > Hinweis: Die Eingaben werden serverseitig auf sinnvolle Bereiche geprüft (z. B. Auflösung 256–1536 px, Lernrate ≥ 1e-6, Schritte > 0 und nur gültige Scheduler). So bleiben Experimente für Einsteiger:innen auf stabilen Werten.

   | Preset | Geeignet für | Schwerpunkte |
   | --- | --- | --- |
   | **Fotostudio – Schnellstart** | 10–30 Portrait- oder Objektmotive, schnelle Tests | Kurzes Training mit 512 px Auflösung und UNet-Feintuning |
   | **Atelier – Detailtreue** | 30–75 stilistisch ähnliche Aufnahmen | Mehr Schritte, feinere Lernrate, höhere LoRA-Ranks |
   | **Galerie – Feinabstimmung** | 75–150 kuratierte Kunstwerke | 640 px Auflösung, Text-Encoder-Training, benötigt ≥ 16 GB VRAM |
5. **Job speichern & exportieren** – Mit „Job anlegen“ wird die Konfiguration als JSON unter `lora/jobs/<id>.json` gesichert und in der Tabelle gelistet. Der Kopier-Button liefert dir den exakten Trainingsbefehl, der 1:1 im Terminal nutzbar ist.

> Tipp: Nach dem Training kannst du denselben Job in der Tabelle wiederverwenden, um Parameteränderungen zu dokumentieren oder Varianten anzulegen.

## 8. Integration in den AI4ArtsEd-Webserver

1. **Pfadvariablen setzen**
   Stelle sicher, dass in deiner `.env` oder Service-Unit die Pfade bekannt sind:
   ```bash
   export COMFYUI_PATH="/opt/comfyui"
   export SWARMUI_PATH="/opt/swarmui"
   ```

2. **LoRA-Dateien kopieren**
   ```bash
   cp outputs/lora/my_concept/pytorch_lora_weights.safetensors /opt/comfyui/models/loras/my_concept.safetensors
   cp outputs/lora/my_concept/adapter_config.json /opt/comfyui/models/loras/my_concept.json
   ```

3. **Workflow anpassen**
   - Öffne den gewünschten Workflow (z. B. `workflows/vector/<workflow>.json`).
   - Trage unter dem LoRA-Knoten den neuen Dateinamen ein.

4. **Serverdienste neu starten**
   ```bash
   ./stop_all_services_improved.sh
   ./start_webserver.sh
   ```

5. **Smoke-Test durchführen**
   - Führe einen Webserver-Job mit dem angepassten Workflow aus.
   - Überprüfe die Logs (`server/logs/`) auf Hinweise des `ModelPathResolver`.

## 9. Qualitäts- und Sicherheitskontrollen

| Prüfschritt | Warum? | Werkzeug |
| --- | --- | --- |
| Visuelle Review | Artefakte, Verzerrungen erkennen | Manuelle Bildsichtung |
| Prompt-Sicherheit | Ungeeignete Inhalte filtern | `SAFETY_NEGATIVE_TERMS` in `server/config.py` |
| Versionierung | Reproduzierbarkeit, Rollback | Git-Repo oder DVC für `outputs/lora` |
| Bias-Analyse | Vermeidung diskriminierender Ergebnisse | Testprompts mit diversen Merkmalen |

## 10. Troubleshooting

| Problem | Ursache | Lösung |
| --- | --- | --- |
| `CUDA out of memory` | Zu hohe Auflösung oder Batchgröße | `--resolution`, `--train_batch_size`, `--gradient_checkpointing` anpassen |
| Verluste stagnieren | Lernrate ungeeignet | `--learning_rate` variieren, `--max_train_steps` erhöhen |
| LoRA wird nicht geladen | Pfad falsch oder `adapter_config.json` fehlt | Pfade prüfen, beide Dateien kopieren |
| Farbverschiebungen im Output | Falsches Basismodell beim Inferenz | Sicherstellen, dass Training & Inferenz dasselbe Basismodell nutzen |
| Training zu langsam | IO-Engpass | Datensatz lokal cachen, SSD nutzen |

## 11. Nächste Schritte

- Automatisiere Trainingsläufe mit CI/CD (z. B. GitHub Actions + self-hosted Runner mit GPU).
- Dokumentiere Hyperparameter und Ergebnisse im Repo (`training/README.md`).
- Teile erprobte LoRA-Modelle intern, damit andere Workflows profitieren.

Mit dieser Anleitung erhältst du eine reproduzierbare, produktionsnahe LoRA-Trainingspipeline, die sich sauber in den AI4ArtsEd-Webserver integrieren lässt.
