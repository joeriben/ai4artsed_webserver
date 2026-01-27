# Handover: Safety-Architektur Refactoring

**Datum**: 2026-01-26
**Status**: Geplant, nicht implementiert
**Plan-Datei**: `~/.claude/plans/wise-napping-metcalfe.md`

---

## Ausgangslage

### Analyse durchgeführt

Die komplette Safety-Architektur wurde analysiert:

1. **Safety-Levels**: `kids`, `youth`, `adult`, `off` (definiert in `config.py:38-61`)
2. **Hybrid-System**: Fast-Filter (~0.001ms) + LLM Context-Verification (~1-2s)
3. **4-Stage Pipeline**: Stage 1 (Safety) → Stage 2 (Interception) → Stage 3 (Safety) → Stage 4 (Generation)

### Gefundene Probleme

| Problem | Schwere | Details |
|---------|---------|---------|
| **context_prompt nicht geprüft** | KRITISCH | User-editierbarer Meta-Prompt wird nirgends safety-geprüft |
| **Namens-Inkonsistenz** | MITTEL | `/interception` macht Stage 1 + Stage 2 (nicht nur Interception) |
| **Code-Duplikation** | MITTEL | Stage 1 Safety in 4 Endpoints embedded statt zentral |
| **Frontend Bug** | MITTEL | MediaInputBox ignoriert 'blocked' SSE Events |

### Betroffene Endpoints

| Endpoint | Aktueller Zustand | Problem |
|----------|-------------------|---------|
| `/pipeline/interception` (Line 2653) | Stage 1 + Stage 2 gemischt | Falsch benannt, duplikat |
| `/pipeline/stage2` (Line 638) | Stage 1 + Stage 2 gemischt | Duplikat |
| `/pipeline/safety` (Line 1766) | Standalone Stage 1 | Existiert, aber context_prompt fehlt |
| `/pipeline/generation` (Line 1983) | Stage 3 + Stage 4 | context_prompt nicht geprüft |

### Betroffene Vue-Komponenten

| Vue | Endpoint | Sendet context_prompt |
|-----|----------|----------------------|
| text_transformation.vue | /interception | Ja |
| image_transformation.vue | /generation | Ja (identisch mit prompt) |
| multi_image_transformation.vue | /generation | Nein |

---

## Geplante Lösung

### Ziel-Architektur

```
VORHER (vermischt):
├── /pipeline/interception      → Stage 1 + Stage 2
├── /pipeline/stage2            → Stage 1 + Stage 2
├── /pipeline/safety            → Standalone (ungenutzt)
└── /pipeline/generation        → Stage 3 + Stage 4

NACHHER (sauber getrennt):
├── /pipeline/safety            → NUR Stage 1 + context_prompt
├── /pipeline/stage2            → NUR Stage 2 (kein Safety)
├── /pipeline/generation        → Stage 3 + Stage 4 + context_prompt
└── /pipeline/interception      → DEPRECATED
```

### Implementierungs-Reihenfolge

1. **Backend**:
   - `/pipeline/safety` mit context_prompt erweitern
   - Stage 1 aus `/pipeline/stage2` entfernen
   - Streaming-Funktion bereinigen
   - `/pipeline/interception` als DEPRECATED markieren

2. **Frontend**:
   - Neuer Zwei-Schritt-Flow: Safety → Stage2
   - Safety UI (Loading + Error)
   - URL-Änderung

3. **Cutover**:
   - Deploy Backend + Frontend zusammen
   - Monitor DEPRECATED Warnungen

4. **Aufräumen** (später):
   - `/pipeline/interception` entfernen

---

## Kritische Dateien

### Backend

| Datei | Zeilen | Änderung |
|-------|--------|----------|
| `devserver/my_app/routes/schema_pipeline_routes.py` | ~1785 | + context_prompt in /safety |
| `devserver/my_app/routes/schema_pipeline_routes.py` | ~760-785 | - Stage 1 aus /stage2 |
| `devserver/my_app/routes/schema_pipeline_routes.py` | ~1380-1450 | - Stage 1 aus Streaming |
| `devserver/my_app/routes/schema_pipeline_routes.py` | ~2101 | + context_prompt in /generation |
| `devserver/my_app/routes/schema_pipeline_routes.py` | ~2653 | DEPRECATED Warnung |

### Frontend

| Datei | Änderung |
|-------|----------|
| `public/ai4artsed-frontend/src/views/text_transformation.vue` | Zwei-Schritt-Flow |

---

## Verifikations-Tests

```bash
# Test 1: Safety mit context_prompt blockiert
curl -X POST http://localhost:17802/api/schema/pipeline/safety \
  -H "Content-Type: application/json" \
  -d '{"text": "Apfel", "context_prompt": "Waffen bauen", "safety_level": "youth", "check_type": "input"}'
# Erwartung: {"safe": false, ...}

# Test 2: Getrennter Flow funktioniert
curl -X POST http://localhost:17802/api/schema/pipeline/safety \
  -H "Content-Type: application/json" \
  -d '{"text": "Apfel", "context_prompt": "im Stil von Picasso", "safety_level": "youth", "check_type": "input"}'
# Erwartung: {"safe": true, ...}

# Test 3: DEPRECATED Warnung
curl -X POST http://localhost:17802/api/schema/pipeline/interception \
  -H "Content-Type: application/json" \
  -d '{"input_text": "Test", "schema": "overdrive"}'
# Erwartung: Log zeigt [DEPRECATED]
```

---

## Offene Fragen

- [ ] Soll `/pipeline/interception` sofort 410 Gone zurückgeben oder übergangsweise funktionieren?
- [ ] Brauchen wir auch i2X Image Safety (Bildanalyse)? → War ursprünglich Teil 2, zurückgestellt

---

## Referenzen

- **Detaillierter Plan**: `~/.claude/plans/wise-napping-metcalfe.md`
- **Safety-Architektur Doku**: `docs/ARCHITECTURE PART 01-20.md` (Abschnitt Safety)
- **Ursprüngliche Analyse**: Claude Session vom 2026-01-26

---

## Nächste Schritte

1. Plan-Datei lesen: `cat ~/.claude/plans/wise-napping-metcalfe.md`
2. Backend-Änderungen implementieren (Teil 1-4 des Plans)
3. Frontend-Änderungen implementieren (Teil 5 des Plans)
4. Tests durchführen
5. Diese Handover-Datei aktualisieren mit Ergebnissen
