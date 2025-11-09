# 🎯 TERMINAL-MANAGER-TASK: AI4ArtsEd Schema-Pipeline für Enduser Editor

## VISION: Modularer Webserver für Pädagogen & Künstler

**Ursprüngliche Motivation:**
- Künstler/Pädagogen sollen EINFACH neue Interception-Prompts hinzufügen (ohne Programmieren!)
- Kinder sollen via Dialog mit LM eigene Prompts erstellen
- Keine ComfyUI-Abhängigkeit für Text-Pipelines
- Edit-Interface für Prompt-Templates (Translation, Dadaismus, UK Youth Slang, etc.)

---

## 📋 MANAGER-TASK-SUBTASKS (Sequential)

### SUBTASK 1️⃣: Verify Translation Pipeline Stability
**Goal:** Sicherstellen dass Pre-Pipeline Translation stabil läuft

```bash
# 1. Devserver starten (Background)
cd /home/joerissen/ai/ai4artsed_webserver
./start_devserver.sh &
sleep 5

# 2. Translation Test durchführen
curl -s -X POST http://localhost:17901/run_workflow \
  -H "Content-Type: application/json" \
  -d '{"input_text": "Ein Kamel trinkt Tee", "workflow_type": "simple_interception", "schema_data": "translation_en"}' \
  | python3 -m json.tool

# 3. Expected Result:
# - Input wird VOR Pipeline übersetzt
# - Output sollte: "A camel drinks tea" (oder ähnlich)
# - Status: SUCCESS, kein Error

# 4. Report:
# ✅ PASS: Translation stable + schnell?
# ❌ FAIL: Fehler? Welche?
```

**Report-Fragen:**
- Wurde Input übersetzt BEVOR die Pipeline lief?
- War die Response schnell? (< 3 sec?)
- Claude 3.5 Haiku stabil?

---

### SUBTASK 2️⃣: Test Schema Edit-Interface Prototype
**Goal:** Web-UI für Enduser-Editing testen

```bash
# 1. Browser öffnen
open http://localhost:17901/

# 2. Tests durchführen:
# - Dropdown: "Workflow Type" wechseln
# - Dropdown: "Schema Data" wechseln (translation_en, TEST_dadaismus, jugendsprache)
# - Input: "Ich bin ein Kunstwerk"
# - Run → Result anschauen

# 3. Für jedes Workflow testen:
# - Translation EN: German → English?
# - Dadaismus: Output ist absurd/surreal?
# - Jugendsprache: Output hat UK Youth Slang?

# 4. UX Feedback:
# - Interface verständlich?
# - Was fehlt für Enduser?
# - Dialog-LM Integration sichtbar machen?
```

**Feedback-Template:**
```
SUBTASK 2 Report:
- Translation EN: ✅ WORKS / ❌ BROKEN
- Dadaismus: ✅ WORKS / ❌ BROKEN  
- Jugendsprache: ✅ WORKS / ❌ BROKEN
- UX Feedback: [Deine Beobachtungen]
- Missing Features: [Was sollen Enduser noch können?]
```

---

### SUBTASK 3️⃣: Document - ENDUSER_GUIDE.md erstellen
**Goal:** Komplette Anleitung für Pädagogen wie sie neue Prompts hinzufügen

**Wichtig:** Schreibe für NON-PROGRAMMERS!

```bash
# Erstelle Datei: ENDUSER_GUIDE.md
# Inhalt sollte sein:

# 1. ÜBERBLICK
- Was ist Schema-Pipeline?
- Wie funktioniert Translation/Manipulation/Interception?
- Beispiele: Translation EN, Dadaismus, UK Youth Slang

# 2. Wie man NEUE Prompts hinzufügt (Step-by-Step)
## A) Einfach: Nur Config ändern
- Öffne: devserver/schemas/schema_data/[NAME].json
- Ändere TASK/CONTEXT/INSTRUCTION
- Save → Fertig!

## B) Mittel: Neue Config erstellen
- Copy: devserver/schemas/schema_data/translation_en.json
- Rename: mein_kunstprojekt.json
- Edit: TASK, CONTEXT, INSTRUCTIONS
- Push zu GitHub

## C) Erweitert: Neue Pipeline-Typen
- (Für später - kurz erklären)

# 3. DIALOG-LM PROPOSAL FÜR KINDER
## Konzept: "Prompt-Wizard für Kids"
- Kind klickt: "Ich möchte einen neuen Kunstprompt"
- Dialog:
  1. "Was ist dein Kunstthema?" → User input
  2. "Welche Emotion?" → Dropdown
  3. "Welche Technik?" → Dropdown
  4. LM generiert → Prompt-Template
  5. Kind sieht → Und kann testen!

# 4. Screenshots/Mockups
- Zeige: Current UI
- Zeige: Proposed Edit-Interface für Enduser
- Zeige: Dialog-LM Mockup

# 5. ROADMAP
- Phase 1 (DONE): Schema-Pipeline modulär ✅
- Phase 2 (NEXT): Enduser Edit-Interface
- Phase 3: Dialog-LM für Kinder
- Phase 4: Community Prompt Library (GitHub?)
```

**Erstelle die Datei!**

---

### SUBTASK 4️⃣: Create + Review Pull Request
**Goal:** Feature-Branch als PR auf GitHub mit vollständiger Dokumentation

```bash
# 1. Stelle sicher dass alles committed ist
cd /home/joerissen/ai/ai4artsed_webserver
git status

# 2. Falls Änderungen von Subtask 3:
git add ENDUSER_GUIDE.md
git commit -m "Add ENDUSER_GUIDE: Schema-Pipeline für Pädagogen & Künstler"

# 3. Push zu feature/schema-architecture-v2
git push origin feature/schema-architecture-v2

# 4. Erstelle PR auf GitHub:
# https://github.com/joeriben/ai4artsed_webserver/pull/new/feature/schema-architecture-v2

# PR Description sollte sein:
"""
## 🎯 Schema-Pipeline Modularisierung für Enduser Editor

### Feature
Verwandelt starre ComfyUI-Workflows in wiederverwendbare, modulare Pipelines.
Pädagogen & Künstler können EINFACH neue Interception-Prompts hinzufügen.

### Changes
- ✅ Pre-Pipeline Translation (Server-Level)
- ✅ Prompt Interception Engine für Multi-Backend
- ✅ Schema-based Pipeline Architecture
- ✅ Web-Interface für Schema-Editing
- ✅ ENDUSER_GUIDE für Pädagogen

### Testing
- [x] Translation Pipeline: Stabil ✅
- [x] Web-Interface: Functional ✅
- [x] Dadaismus & UK Youth Slang: Working ✅

### Next Steps (Phase 2)
- [ ] Dialog-LM für Kinder (Prompt-Wizard)
- [ ] Community Prompt Library
- [ ] Advanced Pipeline Chaining

### Related
- Closes: [falls Issue existiert]
- See: ENDUSER_GUIDE.md für Vision
"""

# 5. Request Review!
```

---

## 🚀 TERMINAL-COMMANDS (Quick Copy-Paste)

```bash
# START: Alle Subtasks ausführen

cd /home/joerissen/ai/ai4artsed_webserver

# ====== SUBTASK 1 ======
echo "=== SUBTASK 1: Translation Test ==="
./start_devserver.sh &
sleep 5
curl -s -X POST http://localhost:17901/run_workflow \
  -H "Content-Type: application/json" \
  -d '{"input_text": "Ein Kamel trinkt Tee", "workflow_type": "simple_interception", "schema_data": "translation_en"}' \
  | python3 -m json.tool | head -50

# ====== SUBTASK 2 ======
echo "=== SUBTASK 2: Web-UI Test ==="
echo "Open in Browser: http://localhost:17901/"
echo "Test: Wechsel zwischen Workflows"
echo "Press ENTER wenn Tests fertig..."
read

# ====== SUBTASK 3 ======
echo "=== SUBTASK 3: ENDUSER_GUIDE.md schreiben ==="
echo "Erstelle: ENDUSER_GUIDE.md (siehe oben)"
echo "Inhalte: Overview, How-To, Dialog-LM Proposal, Roadmap"

# ====== SUBTASK 4 ======
echo "=== SUBTASK 4: PR erstellen ==="
git add ENDUSER_GUIDE.md
git commit -m "Add ENDUSER_GUIDE for Pedagogues & Artists"
git push origin feature/schema-architecture-v2
echo "Create PR: https://github.com/joeriben/ai4artsed_webserver/pull/new/feature/schema-architecture-v2"
```

---

## 📝 Für Terminal-Cline einfach kopieren:

```
MANAGER-TASK: AI4ArtsEd Schema-Pipeline für Enduser Editor

SUBTASK 1: Verify Translation Pipeline Stability
- Start devserver
- Test: curl -X POST http://localhost:17901/run_workflow -d '{"input_text": "Ein Kamel trinkt Tee", ...}'
- Report: ✅ PASS oder ❌ FAIL?

SUBTASK 2: Test Web-UI Schema-Editor
- Open: http://localhost:17901/
- Test: Workflow switching, Schema-Editing
- Report: UX Feedback, Missing Features

SUBTASK 3: Write ENDUSER_GUIDE.md
- Pädagogen-freundlich!
- Include: Überblick, How-To Prompts hinzufügen, Dialog-LM Proposal, Roadmap

SUBTASK 4: Create Pull Request
- Add & Commit ENDUSER_GUIDE.md
- Push zu feature/schema-architecture-v2
- Create PR auf GitHub mit vollständiger Description
```

---

**VIEL ERFOLG! 🚀**
