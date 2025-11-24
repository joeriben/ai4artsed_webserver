# Session 40 - Handover: Property Symbols Design

**Date:** 2025-11-09
**Duration:** ~3 hours
**Status:** Design abgeschlossen, bereit für Implementierung
**Branch:** main

---

## Was wurde gemacht

### Property-Symbole für Vue-Frontend entworfen

**Problem:** Property-Begriffe (chill/chaotic, narrative/algorithmic, etc.) sind abstrakt und schwer für Jugendliche zu verstehen.

**Lösung:** Symbole als visuelle Anker + Tooltips

### Finale Symbol-Übersicht (alle 6 Paare):

```
1. vorhersagbar ↔ überraschend:  🎯 ↔ 🎲  (Ziel vs. Würfel)
2. semantisch ↔ syntaktisch:     ✍️ ↔ 🔢  (Schreiben vs. Rechnen)
3. nüchtern ↔ emotional:         🧊 ↔ 🔥  (Eis vs. Feuer)
4. museal ↔ lebendig:            🏛️ ↔ 🏙️  (Museum vs. Wolkenkratzer)
5. austesten ↔ artikulieren:     🔍 ↔ 🎨  (Detektiv vs. Künstler)
6. playful ↔ serious:            🪁 ↔ 🔧  (Drachen vs. Werkzeug)
```

**Wichtig:**
- Paar 1: chill/chaotic → **vorhersagbar/überraschend** umbenennen
- Paar 2: narrative = **semantisch** (Bedeutung), algorithmic = **syntaktisch** (Regeln)
- Paar 6: playful ≠ "frei", sondern verspielt vs. ernst

---

## Erstelle Dokumente

### Design-Dokumente:
1. **`docs/archive/PROPERTY_TAXONOMY_SYMBOLS_DISCUSSION.md`**
   - Top-down: Von Emoji-Auswahl zur Bedeutung
   - Diskussion über Kongruenz Kat 1 & 6
   - Symbol-Vorschläge Version 1

2. **`docs/archive/PROPERTY_TAXONOMY_VISUAL_CONCEPTS.md`**
   - Bottom-up: Von Konzept zu visueller Darstellung
   - Detaillierte Analyse aller 6 Paare
   - Finale Symbol-Empfehlungen mit Begründungen

3. **`docs/PROPERTY_SYMBOLS_IMPLEMENTATION_PLAN.md`**
   - Non-destructive Implementierung
   - Feature-Flag-basiert (ENABLE_PROPERTY_SYMBOLS)
   - Parallel-Code (property_pairs_v2)
   - 4 Phasen: Backend (30min), Frontend (1h), Testing (2h), Rollback

---

## Nächste Schritte (Implementation)

### Phase 1: Backend (30 Min)
```python
# devserver/my_app/routes/schema_pipeline_routes.py

ENABLE_PROPERTY_SYMBOLS = False  # Feature-Flag

property_pairs_v2 = [
    {
        "id": 1,
        "pair": ["predictable", "surprising"],
        "symbols": {"predictable": "🎯", "surprising": "🎲"},
        "labels": {"de": {...}, "en": {...}},
        "tooltips": {"de": {...}, "en": {...}}
    },
    # ... 5 weitere Paare
]
```

### Phase 2: Frontend (1h)
- Neue Datei: `public/ai4artsed-frontend/src/i18n-symbols.ts`
- PropertyBubble.vue erweitern (Symbol + Text)
- Store: symbolsEnabled State

### Phase 3: Testing
- Feature-Flag auf True setzen
- Symbole testen (Desktop: Symbol+Text, Mobile: nur Symbol)
- Tooltips on hover

### Phase 4: Rollback falls nötig
- Feature-Flag auf False → Alles wie vorher

---

## Wichtige Designentscheidungen

### 1. Kategorie-Umbenennung
**Kat 1: chill/chaotic → vorhersagbar/überraschend**
- Grund: Weniger Kongruenz mit Kat 6 (playful/serious)
- "chill" = Erwartbarkeit, nicht Gemütszustand

### 2. Semantisch statt "Geschichten erzählen"
**Kat 2: narrative = semantisch (Bedeutung), nicht narrativ**
- Schreiben (✍️) = Bedeutung/Kontext
- Rechnen (🔢) = Regeln/Syntax

### 3. Kindgerechte Symbole
- Museum/Wolkenkratzer statt Standuhren (Kinder kennen Standuhren evtl. nicht)
- Drachen statt Teddybär (allgemeiner, nicht zu spezifisch)
- Würfel NUR bei "überraschend" (Zufall/Unabsehbarkeit)

### 4. Ikonisch-konkrete Objekte
- Alle 6 Paare: Erkennbare Objekte (keine Abstraktionen)
- Keine Symbol-Dopplung
- Tooltips für pädagogischen Kontext

---

## Offene Punkte

### 1. Forschungsprojekt-Diskussion
- User-Testing mit Jugendlichen (12-16)
- A/B-Test: Mit vs. ohne Symbole
- Feedback zu Tooltips

### 2. Begriffe finalisieren
- "vorhersagbar/überraschend" statt "chill/chaotic" OK?
- "semantisch/syntaktisch" statt "narrative/algorithmic" OK?
- Deutsche Labels finalisieren

### 3. Config-Updates (später)
**Wenn Begriffe ändern:**
- 18 Configs müssen angepasst werden
- properties: ["chill"] → ["predictable"]
- properties: ["chaotic"] → ["surprising"]

---

## Technische Details

### Backend-Struktur (property_pairs_v2):
```python
{
    "id": 1,
    "pair": ["predictable", "surprising"],
    "symbols": {"predictable": "🎯", "surprising": "🎲"},
    "labels": {
        "de": {"predictable": "vorhersagbar", "surprising": "überraschend"},
        "en": {"predictable": "predictable", "surprising": "surprising"}
    },
    "tooltips": {
        "de": {
            "predictable": "Output ist erwartbar und steuerbar",
            "surprising": "Output ist unvorhersehbar, überraschende Wendungen"
        },
        "en": {...}
    }
}
```

### Frontend-Integration:
```vue
<PropertyBubble
  :property="property"
  :symbols-enabled="symbolsEnabled"
  :language="currentLanguage"
/>
```

---

## Testing-Checkliste

### Backend:
- [ ] API `/pipeline_configs_with_properties` mit flag false/true
- [ ] property_pairs_v2 hat alle 6 Paare
- [ ] Alle Symbole, Labels, Tooltips vorhanden

### Frontend:
- [ ] Symbol + Text auf Desktop
- [ ] Nur Symbol auf Mobile
- [ ] Tooltip on hover (Desktop)
- [ ] Config-Auswahl funktioniert wie vorher
- [ ] XOR-Logik funktioniert

### User-Testing:
- [ ] Symbole intuitiv verständlich?
- [ ] Tooltips hilfreich?
- [ ] Unklare Symbole identifizieren

---

## Risiken & Mitigation

**Risiko 1: Symbole nicht verständlich**
- Mitigation: Feature-Flag → einfaches Rollback
- Testing vor Produktiv-Release

**Risiko 2: Emoji-Darstellung plattformabhängig**
- Mitigation: Custom SVG-Icons als Alternative
- Dokumentiert in VISUAL_CONCEPTS.md

**Risiko 3: Tooltip auf Touch-Geräten**
- Mitigation: Click-to-show statt hover
- Mobile: Symbol allein muss verständlich sein

---

## Dateien-Übersicht

### Erstellt (Design):
```
docs/archive/PROPERTY_TAXONOMY_SYMBOLS_DISCUSSION.md
docs/archive/PROPERTY_TAXONOMY_VISUAL_CONCEPTS.md
docs/PROPERTY_SYMBOLS_IMPLEMENTATION_PLAN.md
docs/SESSION_40_HANDOVER.md (diese Datei)
```

### Zu ändern (Implementation):
```
devserver/my_app/routes/schema_pipeline_routes.py
  → property_pairs_v2 hinzufügen
  → ENABLE_PROPERTY_SYMBOLS = False

public/ai4artsed-frontend/src/i18n-symbols.ts
  → NEU erstellen

public/ai4artsed-frontend/src/components/PropertyBubble.vue
  → symbolsEnabled prop hinzufügen

public/ai4artsed-frontend/src/stores/configSelection.ts
  → symbolsEnabled state hinzufügen
```

---

## Session-Metriken

**Dauer:** ~3 Stunden
**Kosten:** ~$XX (geschätzt)
**Files Created:** 4 Dokumentationsdateien
**Files Modified:** 0 (nur Design, keine Implementierung)

---

## Nächste Session: Implementation starten

1. **Backend:** property_pairs_v2 hinzufügen (30 Min)
2. **Frontend:** i18n-symbols.ts erstellen (30 Min)
3. **Components:** PropertyBubble erweitern (30 Min)
4. **Testing:** Feature-Flag aktivieren, testen (1h)

**Geschätzter Gesamt-Aufwand:** 3-4 Stunden

---

**Session 40 abgeschlossen.**
**Nächster Schritt:** Implementation gemäß PROPERTY_SYMBOLS_IMPLEMENTATION_PLAN.md
