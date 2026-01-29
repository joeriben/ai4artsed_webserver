# MEMO: VRAM-Management und Workshop-Strategie

**Datum:** 29. Januar 2026
**Kontext:** Workshop-Analyse nach Session mit Timeout-Fehlern
**Bezug:** Design Decision "LLM-STRATEGIE: Wechsel zu Mistral" (2026-01-29)

---

## 1. Ausgangssituation: Workshop-Probleme

Am 29.1.2026 traten während eines Workshops massive Probleme auf:
- Viele Generierungen schlugen fehl ("No Media")
- Timeout-Fehler bei Legacy-Workflows (300s überschritten)
- SwarmUI zeigte "Queue Warning"
- Erste erfolgreiche Generation erst nach 6.5 Minuten "Prep-Zeit"

---

## 2. Technische Analyse

### 2.1 Ursprüngliche Annahme (widerlegt)

Erste Vermutung: **VRAM-Thrashing** - Ollama (65GB für gpt-OSS:120b) und ComfyUI konkurrieren um die 96GB VRAM der RTX 6000.

### 2.2 Tatsächliches Problem: Cold-Start-Latenz

Systemanalyse im Idle-Zustand zeigte:
- **GPU VRAM:** Nur 27GB / 98GB belegt (71GB frei!)
- **Ollama:** Prozess läuft, aber kein Modell geladen
- **ComfyUI:** Läuft mit minimalem VRAM

**Erkenntnis:** Das Problem ist nicht Konkurrenz um VRAM, sondern **ständiges Laden und Entladen** von Modellen durch kurze `keep_alive` Settings.

### 2.3 Der Cold-Start-Zyklus im Workshop

```
1. User A generiert Bild
   → Ollama lädt gpt-OSS:120b (65GB von SSD) ← DAUERT 1-6 MINUTEN
   → ComfyUI lädt Bildmodell (8-24GB)
   → Generation erfolgt

2. Pause (nächstes Kind ist dran, Erklärungen, etc.)
   → keep_alive: "10m" läuft ab
   → Modelle werden entladen

3. User B generiert Video
   → Ollama lädt gpt-OSS:120b ERNEUT (65GB)
   → ComfyUI lädt Videomodell (20GB)
   → Wieder lange Wartezeit

4. Zyklus wiederholt sich für jeden Teilnehmenden
```

### 2.4 Dezentrale keep_alive-Implementierung

Das VRAM-Management war über viele Stellen verstreut implementiert:

| Datei | Setting | Effekt |
|-------|---------|--------|
| `manipulate.json` | `keep_alive: "10m"` | Entladen nach 10 Min |
| `safety_check_*.json` | `keep_alive: "10m"` | Entladen nach 10 Min |
| `prompt_interception_engine.py` | `keep_alive: 0` | **Sofortiges Entladen!** |
| `image_analysis.py` | `keep_alive: "0s"` | Sofortiges Entladen |

> **Projektleiter-Kommentar:** "Das geht gar nicht mit dem Entladen - schon gar nicht an so intransparenter Stelle. Aber vermutlich war der Mechanismus nötig für den Betrieb - ist nur völlig dezentral implementiert."

---

## 3. LLM-Strategie: Wechsel zu Mistral

### 3.1 Problemstellung

> **Projektleiter-Analyse:**
> "Folgendes: Wir sehen immer wieder dass a) kleine LLM zu schlecht sind für die Aufgabe. b) große LLM 120b funktionieren sehr gut für Einzelsessions. c) für Workshops jedoch nicht, extremer VRAM-Stau wegen vieler parallel verwendeter Modelle. d) Jedoch auch in Einzelsession wird der kreative Flow behindert wenn man implizit weiß dass die Wahl eines anderen Modells dann wieder 'ewig' dauert - man vermeidet das intuitiv."

### 3.2 DSGVO-Analyse externer LLM-Anbieter

> **Projektleiter-Analyse:**
> "DSGVO-konforme externe LLM-Anbieter sind derzeit in Europa praktisch nicht zu finden, zumindest nicht auf Token-Basis für Kleinabnehmer wie uns. Einziger Anbieter ist Mistral. Selbst dessen großes Modell hat nach unseren Erfahrungen schlechtere Eignungswerte für unseren Use-Case; zumindest erscheint uns gpt-OSS:120b leistungsfähiger für Interception als das größte verfügbare Mistral-Modell."

| Anbieter | DSGVO-Status | Verfügbarkeit für Kleinabnehmer |
|----------|--------------|--------------------------------|
| OpenAI | ❌ US-Server | Nicht nutzbar |
| Anthropic | ❌ US-Server | Nicht nutzbar |
| Google | ⚠️ Kompliziert | Nicht praktikabel |
| AWS Bedrock EU | ✅ EU-Server | Nur Enterprise-Verträge |
| **Mistral** | ✅ Frankreich | **Token-basiert verfügbar** |

### 3.3 Strategische Entscheidung

> **Projektleiter-Schlussfolgerung:**
> "Wir können nur Mistral als externe LLM-Lösung wählen. Ergo müssen wir alle Meta-Prompts für Mistral optimieren."

**Konsequenzen:**
1. Migration von lokalem gpt-OSS:120b zu externem Mistral
2. Alle Meta-Prompts müssen für Mistral optimiert werden
3. VRAM wird vollständig für Bild-/Video-Modelle verfügbar (96GB statt 31GB)
4. Keine Cold-Start-Latenz mehr für LLM-Aufrufe (API statt Modell-Loading)

---

## 4. Pädagogische Implikationen: Workshop-Design

### 4.1 Grundsatz

> **Für die pädagogische Praxis bedeutet das - je nach VRAM: Workshop-Konzepte sollten häufige VRAM-Load-Zeiten vermeiden, indem sie auf jeweils 1-2 Modelle fokussieren für alle Teilnehmenden.**

### 4.2 Empfehlungen für Workshop-Konzeption

**A) Modell-Fokussierung**

| Workshop-Typ | Empfohlene Modelle | VRAM-Budget |
|--------------|-------------------|-------------|
| Bildgenerierung | sd3.5_large ODER flux2 | 8-18 GB |
| Videogenerierung | wan22_video ODER ltx_video | 16-20 GB |
| Audio/Musik | stableaudio ODER acenet | 8-15 GB |
| Mixed Media | 1 Bild + 1 Video | ~28 GB |

**B) Workshop-Vorbereitung ("Warmup")**

Vor Workshop-Beginn:
1. Alle geplanten Modelle einmal laden (Dummy-Request)
2. Modelle bleiben dann für keep_alive-Dauer geladen
3. Erste Teilnehmer-Requests sind sofort schnell

**C) Vermeidung von Modell-Wechseln**

- **Ungünstig:** "Jeder probiert aus was er will" → ständiger Modellwechsel
- **Günstig:** "Heute arbeiten wir alle mit Video" → ein Modell bleibt geladen
- **Kompromiss:** Gruppen bilden (Gruppe A: Video, Gruppe B: Bild)

### 4.3 Technische Unterstützung

**Zukünftige Features (nach Mistral-Migration):**

1. **Workshop-Modus im Frontend**
   - Auswahl: "Workshop mit Fokus auf [Video/Bild/Audio]"
   - Nicht-fokussierte Modelle werden ausgegraut/versteckt
   - Verhindert versehentliche Modellwechsel

2. **Modell-Preloading**
   - Admin-Funktion: "Diese Modelle für Workshop vorladen"
   - Automatisches Warmup vor Session-Start

3. **Queue-Feedback**
   - User sieht: "3 Jobs vor dir (~2 Min)"
   - Transparenz über Wartezeiten

---

## 5. Zusammenfassung

### Problem
Cold-Start-Latenz durch kurze keep_alive Settings führt zu inakzeptablen Wartezeiten im Workshop-Betrieb. Kinder und Jugendliche warten nicht 6+ Minuten auf ein "Fake-AI-Bild".

### Technische Lösung
1. **Mistral statt lokales LLM** → Eliminiert 65GB VRAM-Loading
2. **Längere keep_alive für ComfyUI** → Modelle bleiben geladen
3. **Dezentrale Settings bereinigen** → Kein verstecktes Entladen mehr

### Pädagogische Lösung
Workshop-Konzepte auf 1-2 Modelle fokussieren, um VRAM-Load-Zeiten zu minimieren. Die technische Limitation wird zur didaktischen Struktur: Fokussierung fördert Vertiefung statt oberflächlichem "Alles ausprobieren".

---

## 6. Offene Punkte

- [ ] Mistral-Qualitätstest für Interception-Aufgaben
- [ ] Meta-Prompt-Optimierung für Mistral
- [ ] Workshop-Modus im Frontend implementieren
- [ ] Dokumentation für Workshop-Leitende erstellen

---

*Erstellt basierend auf Analyse-Session 147, 29. Januar 2026*
