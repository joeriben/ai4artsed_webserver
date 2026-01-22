# Memo: Kritisch-Reflexive Elemente im AI4ArtsEd System

**Status:** Konzeptphase abgeschlossen, Implementierung pausiert
**Datum:** 2026-01-21
**Speicherort:** `docs/PARKED_reflexion_feature_konzept.md`
**Grund der Dokumentation:** Festhalten aller Ideen und Erklärung, warum keine Implementierung erfolgt

---

## 1. Ausgangspunkt: Das pädagogische Defizit

### Ursprüngliche Vision (aus Projektdokumentation)
- Kritische Eingriffsmöglichkeit an jeder Stelle
- Diversitäts- und ethisch orientierte Evaluationen
- Abduktion - Erwartungen nicht entsprechen
- Kritische Auseinandersetzung mit generativen KIs

### Befund der Analyse
**Technisch exzellent, pädagogisch unterentwickelt.**

Die kritisch-reflexive Substanz existiert im Backend:
- Safety-Level-Konfigurationen (kids, youth, open)
- Prompt Interception mit pädagogischer Transformation
- Diversitäts-Orientierungen in den Configs

**Problem:** All das ist für Lernende unsichtbar. Sie erleben das System als "Prompt rein → Bild raus", ohne Reflexionsanreize.

---

## 2. Lösungsansatz: LLM-generierte Reflexionsfragen

### Kernidee
Träshy (das Maskottchen) zeigt kontextabhängige Reflexionsfragen. Das LLM generiert diese basierend auf Anweisungen - keine vordefinierten Fragen, sondern jeweils einzigartig und auf den konkreten Prompt/Output bezogen.

### Zwei geplante Reflexions-Momente

**Moment 1: Prompt-Analyse (vor/nach Transformation)**
- Input: Original-Prompt + transformierter Prompt + Config-Info
- Output: Eine Reflexionsfrage zur Transformation
- Beispiel: "Die KI hat 'Prinzessin' durch 'selbstbewusste Abenteurerin' ersetzt. Was denkst Du darüber?"

**Moment 2: Bild-Analyse (nach Generierung)**
- Input: Prompt + generiertes Bild (multimodales LLM)
- Output: Feedback/Frage zum generierten Bild
- Beispiel: "Entspricht das Bild dem, was Du Dir vorgestellt hast?"

### Geplante LLM-Anweisungen

**Für Prompt-Reflexion:**
```
Du bist ein pädagogischer Begleiter für Kinder und Jugendliche.
Generiere EINE kurze Reflexionsfrage (max 2 Sätze) zu diesem Prompt.

ORIENTIERUNG:
- Ästhetische Aspekte: Vorstellung vs. Beschreibung, Detailgrad
- Ethische Aspekte: Klischees, Stereotype, Originalität
- Transformation: Was hat die KI verändert? Passt das?

STIL:
- Kurz und verständlich (Kinder, Nicht-Muttersprachler)
- Nicht belehrend, sondern fragend
- Neugierig, nicht wertend
```

**Für Bild-Reflexion:**
```
Du bist ein pädagogischer Begleiter. Du siehst einen Prompt und das generierte Bild.
Generiere EINE kurze Reflexionsfrage oder ein Feedback (max 2 Sätze).

ORIENTIERUNG:
- Vergleich: Entspricht das Bild dem Prompt? Was ist anders?
- Ästhetik: Was fällt auf? Was ist gelungen/überraschend?
- Kritik: Stereotype? Klischees? Problematische Darstellungen?
```

### Kernprinzipien

| Prinzip | Bedeutung |
|---------|-----------|
| Kurze Texte | Verständlich für Kinder und Nicht-Muttersprachler |
| Kontextabhängig | LLM generiert Frage basierend auf konkretem Prompt/Output |
| Nicht blockierend | Analyse läuft parallel, unterbricht nicht den Flow |
| Keine Belehrung | Fragen regen zur eigenen Reflexion an |
| Begleitend | Träshy als freundlicher Helfer, nicht als Autorität |

---

## 3. Geplante technische Architektur

### Backend-Endpoints (Pattern wie chat_routes.py)

```python
# reflection_routes.py
@reflection_bp.route('/prompt', methods=['POST'])
def generate_prompt_reflection():
    # Lädt Anweisungen aus trashy_prompt_reflection.txt
    # Baut System-Prompt mit Kontext
    # Ruft CHAT_HELPER_MODEL auf
    # Gibt Reflexionsfrage zurück
```

### Dateistruktur

```
devserver/
├── trashy_interface_reference.txt      # (existiert) Allgemeines Systemwissen
├── trashy_prompt_reflection.txt        # NEU: Anweisungen für Prompt-Reflexion
├── trashy_image_reflection.txt         # NEU: Anweisungen für Bild-Reflexion
└── my_app/routes/
    ├── chat_routes.py                  # (existiert) Chat-Hilfe
    └── reflection_routes.py            # NEU: Reflexions-Endpoints
```

### Entschiedene Fragen

| Frage | Entscheidung |
|-------|--------------|
| Welches LLM? | CHAT_HELPER_MODEL (wie Chat) |
| Multimodales LLM? | Lokal (LLaVA oder Qwen-VL, je nach Qualität) |
| Trigger? | MediaBoxen-Events (aktionsbasiert) |
| User-Reaktionen speichern? | Nein (zu komplex für erste Version) |

---

## 4. Verbleibende Probleme (Gründe für Nicht-Implementierung)

### 4.1 Das Flächen-Problem

**Problem:** Text braucht Platz. Reflexionsfragen - selbst kurze - benötigen UI-Fläche.

**Warum kritisch:**
- Die MediaBox-UI ist bereits dicht gepackt
- Zusätzlicher Text konkurriert mit dem generierten Bild
- Die bestehende ChatOverlay-Komponente ist "viel zu groß" für diesen Zweck

**Mögliche Lösungen (nicht ausgereift):**
- Sehr kurze Fragen (1 Satz, ~40 Zeichen) - aber verliert dann Tiefe
- Mini-Icon mit Tooltip bei Hover - aber dann übersehbar
- Audio statt Text (Träshy spricht) - aber Accessibility-Probleme
- Subtile visuelle Hinweise ohne Text - aber was sagt ein Icon ohne Worte?

**Status:** Kein überzeugendes UI-Konzept gefunden.

### 4.2 Das Latenz-Problem

**Problem:** LLM-Aufrufe brauchen Zeit und können das System blockieren.

**Warum kritisch:**
- Selbst kleine LLMs brauchen 1-3 Sekunden
- Parallel laufen bedeutet trotzdem: Frage erscheint verzögert
- Wenn Frage nach Bild-Generierung kommt, ist der Moment vorbei
- User wartet nicht auf Reflexion, sondern auf das Bild

**Mögliche Lösungen (nicht ausgereift):**
- Pre-generierte generische Fragen als Fallback - aber widerspricht Kontextabhängigkeit
- Sehr kleines/schnelles lokales LLM - aber Qualitätsverlust
- Frage erscheint später als "Nachtrag" - aber dann ist der Moment vorbei

**Status:** Technisch lösbar, aber UX bleibt unbefriedigend.

### 4.3 Der Spagat: Begleitend vs. Störend

**Problem:** Reflexion soll präsent, aber nicht aufdringlich sein.

**Warum schwierig:**
- Zu subtil → wird ignoriert
- Zu prominent → stört den kreativen Flow
- Zu häufig → nervt
- Zu selten → verliert pädagogischen Wert

**Status:** Grundsätzliches UX-Dilemma ohne klare Lösung.

### 4.4 Konzeptionelle Unreife

**Ehrliche Einschätzung:** Das Konzept ist auf Seiten des Projektverantwortlichen noch nicht ausgereift genug für eine Implementierung. Es fehlt:

- Ein klares mentales Bild, wie die Interaktion aussehen soll
- Erfahrungswerte, ob LLM-generierte Fragen pädagogisch wirksam sind
- Ein testbares Minimal-Konzept

---

## 5. Alternative Ansätze (nicht weiterverfolgt)

### 5.1 Statische Reflexionsfragen
Vordefinierte Fragen, die zufällig oder rotierend erscheinen.
- **Vorteil:** Keine Latenz, kein LLM-Aufruf
- **Nachteil:** Nicht kontextabhängig, wirkt schnell repetitiv

### 5.2 Reflexion-on-Demand
User klickt aktiv auf "Träshy fragen" für Reflexions-Input.
- **Vorteil:** Nicht störend, User-initiiert
- **Nachteil:** Wird wahrscheinlich nie genutzt

### 5.3 Post-Session-Reflexion
Reflexionsfragen am Ende einer Sitzung, nicht während der Generierung.
- **Vorteil:** Unterbricht nicht den Flow
- **Nachteil:** Verliert den "teachable moment"

### 5.4 Visuelle Hints ohne Text
Farb-Coding oder Icons, die auf Transformation hinweisen.
- **Vorteil:** Platzsparend, nicht störend
- **Nachteil:** Unklar was sie bedeuten, braucht Onboarding

---

## 6. Fazit

### Was wir haben
- Eine klare Analyse des pädagogischen Defizits
- Einen technisch machbaren Lösungsansatz
- Entscheidungen zu Backend-Architektur und LLM-Auswahl

### Was uns fehlt
- Ein überzeugendes UI/UX-Konzept für nicht-störende Reflexion
- Eine Lösung für das Latenz-Problem, die pädagogisch sinnvoll ist
- Konzeptionelle Klarheit auf Projektseite

### Empfehlung
Das Feature parken, bis:
1. Ein konkretes UI-Konzept existiert (Skizze, Mockup)
2. Die Frage "Wie fühlt sich gute Reflexionsbegleitung an?" beantwortet ist
3. Eventuell ein Low-Fidelity-Prototyp getestet wurde

---

## 7. Referenzen für spätere Wiederaufnahme

**Relevante Dateien im System:**
- `devserver/trashy_interface_reference.txt` - Bestehendes Träshy-Systemwissen
- `devserver/my_app/routes/chat_routes.py` - Pattern für LLM-Aufrufe
- `my_app/config/*.json` - Safety-Configs mit pädagogischer Substanz

**Dieses Memo:** Enthält alle Entwürfe und kann als Startpunkt dienen, wenn das Konzept weiterentwickelt wird.
