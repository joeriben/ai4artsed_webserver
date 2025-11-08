# Session 37 - Property Taxonomy Revision

**Date:** 2025-11-08
**Status:** Analysis Complete, Awaiting Implementation
**Branch:** feature/schema-architecture-v2

---

## Kontext

Session 34 hat ein Property-System mit 6 Dimensionen (12 Terme) entwickelt und auf alle Configs angewendet. Die Zuweisungen waren jedoch **unsystematisch und teilweise semantisch inkonsistent**.

Diese Session überarbeitet die Termini und prüft systematisch alle Config-Zuweisungen.

---

## TEIL 1: Finale Termini (Deutsch + Englisch)

### Die 6 Dimensionen mit überarbeiteten Übersetzungen:

| Nr | Deutsch | Englisch | Bedeutung |
|----|---------|----------|-----------|
| 1 | **chillig - wild** | **chill - wild** | Kontrollierter Kontext vs. Kontrollverlust |
| 2 | **Geschichten erzählen - nach Regeln gehen** | **tell stories - follow rules** | Narrativ vs. Algorithmizität |
| 3 | **harte Fakten - weiche Gefühle** | **hard facts - soft feelings** | Rational vs. Affektiv |
| 4 | **Geschichte - Gegenwart** | **history - present** | Museal (eingefroren) vs. Living Heritage |
| 5 | **KI austesten - Kunst machen** | **test AI - make art** | Explorativ vs. Produktiv |
| 6 | **bisschen verrückt - eher ernst** | **playful - serious** | Spielerisch vs. Ernsthaft |

### Wichtige semantische Klärungen:

#### 1. "chillig" ≠ "ruhig" (Gemütszustand)
- **"chillig"** = in einem kontrollierten Kontext sein können (Erwartbarkeit, Steuerbarkeit)
- **Nicht:** entspannt/relaxed (Hängematte)
- **Sondern:** unter Kontrolle, vorhersagbar

#### 2. "nach Regeln gehen" ≠ "berechnen"
- **"nach Regeln gehen"** = algorithmisch, deterministisch, schrittweise
- **Nicht:** mathematisch/kalkulatorisch
- **Sondern:** regelbasierte Transformation

#### 3. "Geschichte" ≠ temporale Vergangenheit
- **"Geschichte"** = museale Kunstbewegung (eingefroren, verändert sich nicht mehr)
- **"Gegenwart"** = living heritage (wird heute noch praktiziert/verändert) ODER zeitlose Konzepte
- **Beispiel:** Dada (Geschichte) vs. Stille Post (Gegenwart, weil living heritage)

#### 4. "KI austesten" vs. "Kunst machen"
- **"KI austesten"** = explorativ, experimentell, prozessorientiert
- **"Kunst machen"** = produktiv, gestalterisch, ergebnisorientiert
- **Nicht universell**, sondern **AI4ArtsEd-spezifisch**

#### 5. Modalwörter als Kontext-Geber
- **"bisschen verrückt"** / **"eher ernst"** = nicht Abschwächung, sondern Kontext
- 2-Wort-Konstellationen erleichtern Verständnis für Nicht-Muttersprachler

---

## TEIL 2: Systematische Config-Prüfung

### Aktueller Stand: 18 aktive Configs

Configs: Bauhaus, ClichéFilter V2, ConfucianLiterati, Dadaism, Expressionism, HunkyDoryHarmonizer, ImageAndSound, ImageToSound, UK Youth Slang, Overdrive, PigLatin, Renaissance, SplitAndCombineSpherical, SD 3.5 TellAStory, StillePost, Surrealization, TechnicalDrawing, TheOpposite

---

### TERM 1: calm (chillig) - "Kontrollierter Kontext"

**Aktuell (8):** Bauhaus, ClichéFilter V2, ConfucianLiterati, HunkyDoryHarmonizer, PigLatin, Renaissance, SD 3.5 TellAStory, TechnicalDrawing

**Vorgeschlagene Änderungen:**
- ❌ **ENTFERNEN:** ClichéFilter V2 (bricht Erwartungen, ist eher "chaotic")
- ⚠️ **PRÜFEN:** SD 3.5 TellAStory (narrativ, aber ist es "chillig"? → Eher neutral)

**Begründung:**
- ClichéFilter V2 entfernt vorhersagbare Klischees → macht Sprache unerwarteter → "wild", nicht "chillig"

---

### TERM 2: chaotic (wild) - "Kontrollverlust"

**Aktuell (8):** Dadaism, Expressionism, UK Youth Slang, Overdrive, SplitAndCombineSpherical, StillePost, Surrealization, TheOpposite

**Vorgeschlagene Änderungen:**
- ✅ **HINZUFÜGEN:** ClichéFilter V2

**Begründung:**
- ClichéFilter V2 bricht erwartete Muster → unvorhersagbares Ergebnis

---

### TERM 3: narrative (Geschichten erzählen) - "Bedeutungsvoll, kontextuell"

**Aktuell (8):** Bauhaus, ClichéFilter V2, ConfucianLiterati, Dadaism, Expressionism, UK Youth Slang, Renaissance, SD 3.5 TellAStory

**Vorgeschlagene Änderungen:**
- ❌ **ENTFERNEN:** Bauhaus (funktionalistisch/strukturell, nicht erzählerisch)
- ❌ **ENTFERNEN:** ClichéFilter V2 (filtert, erzählt nicht)
- ✅ **HINZUFÜGEN:** HunkyDoryHarmonizer (erzählt durch harmonische Atmosphäre)

**Begründung:**
- Bauhaus = geometrische Reduktion, keine Erzählung (eher "facts")
- ClichéFilter = Filterfunktion, keine narrative Transformation
- HunkyDoryHarmonizer = erzeugt emotionale/atmosphärische Erzählung

---

### TERM 4: algorithmic (nach Regeln gehen) - "Regelbasiert"

**Aktuell (7):** ImageAndSound, ImageToSound, Overdrive, PigLatin, SplitAndCombineSpherical, StillePost, TheOpposite

**Vorgeschlagene Änderungen:**
- ✅ **HINZUFÜGEN:** Bauhaus (geometrische Reduktion = formaler Algorithmus)
- ✅ **HINZUFÜGEN:** TechnicalDrawing (technische Übersetzung = feste Regeln)
- ✅ **HINZUFÜGEN:** ClichéFilter V2 (Klischee-Erkennung = Regel)

**Begründung:**
- Bauhaus wendet formale Reduktionsregeln an
- TechnicalDrawing übersetzt nach technischen Regeln
- ClichéFilter wendet Filterregeln an

---

### TERM 5: facts (harte Fakten) - "Objektiv, sachlich"

**Aktuell (5):** Bauhaus, ClichéFilter V2, ConfucianLiterati, Renaissance, TechnicalDrawing

**Vorgeschlagene Änderungen:**
- ❌ **ENTFERNEN:** ConfucianLiterati (hochgradig emotional: Harmonie, Rituale, Werte)

**Begründung:**
- Konfuzianische Kultur ist emotional/moralisch, nicht faktisch

---

### TERM 6: emotion (weiche Gefühle) - "Affektiv, emotional"

**Aktuell (6):** ConfucianLiterati, Dadaism, Expressionism, HunkyDoryHarmonizer, UK Youth Slang, Surrealization

**Vorgeschlagene Änderungen:**
- ✅ Keine Änderungen (gut abgedeckt)

**Begründung:**
- Alle zugewiesenen Configs sind emotional korrekt

---

### TERM 7: historical (Geschichte) - "Museale Kunstbewegung"

**Aktuell (5):** Bauhaus, ConfucianLiterati, Dadaism, Expressionism, Renaissance

**Vorgeschlagene Änderungen:**
- ✅ Keine Änderungen

**Begründung:**
- Alle sind historische Kunstbewegungen/kulturelle Positionen, die sich nicht mehr verändern

---

### TERM 8: contemporary (Gegenwart) - "Living heritage / zeitlos"

**Aktuell (6):** ClichéFilter V2, HunkyDoryHarmonizer, ImageAndSound, ImageToSound, UK Youth Slang, TechnicalDrawing

**Vorgeschlagene Änderungen:**
- ✅ **HINZUFÜGEN:** PigLatin (wird heute noch gespielt)
- ✅ **HINZUFÜGEN:** StillePost (wird heute noch gespielt)
- ✅ **HINZUFÜGEN:** TheOpposite (zeitloses Konzept)
- ✅ **HINZUFÜGEN:** SplitAndCombineSpherical (zeitloses Konzept)
- ✅ **HINZUFÜGEN:** Overdrive (zeitloses Konzept)
- ✅ **HINZUFÜGEN:** SD 3.5 TellAStory (moderne Technik, 2024)

**Begründung:**
- Alle algorithmischen Spiele sind living heritage (werden heute gespielt)
- Moderne technische Konzepte sind contemporary

---

### TERM 9: explore (KI austesten) - "Explorativ, experimentell"

**Aktuell (8):** ClichéFilter V2, ConfucianLiterati, Overdrive, PigLatin, SplitAndCombineSpherical, StillePost, Surrealization, TheOpposite

**Vorgeschlagene Änderungen:**
- ✅ Keine Änderungen (gut abgedeckt)

**Begründung:**
- Alle Configs mit "explore" sind experimentell/explorativ

---

### TERM 10: create (Kunst machen) - "Produktiv, gestalterisch"

**Aktuell (10):** Bauhaus, Dadaism, Expressionism, HunkyDoryHarmonizer, ImageAndSound, ImageToSound, UK Youth Slang, Renaissance, SD 3.5 TellAStory, TechnicalDrawing

**Vorgeschlagene Änderungen:**
- ✅ Keine Änderungen

**Begründung:**
- "create" = bewusste künstlerische/gestalterische Absicht
- Algorithmische Spiele (PigLatin, etc.) sind eher "explore" (prozessorientiert)

---

### TERM 11: playful (bisschen verrückt) - "Spielerisch"

**Aktuell (8):** Dadaism, HunkyDoryHarmonizer, UK Youth Slang, Overdrive, PigLatin, SplitAndCombineSpherical, StillePost, TheOpposite

**Vorgeschlagene Änderungen:**
- ✅ Keine Änderungen (gut abgedeckt)

**Begründung:**
- Alle Configs sind spielerisch/leicht

---

### TERM 12: serious (eher ernst) - "Ernst gemeint"

**Aktuell (8):** Bauhaus, ClichéFilter V2, ConfucianLiterati, Expressionism, ImageAndSound, ImageToSound, Renaissance, TechnicalDrawing

**Vorgeschlagene Änderungen:**
- ✅ **HINZUFÜGEN:** SD 3.5 TellAStory (narrative Bildgenerierung ist ernst)
- ⚠️ **PRÜFEN:** Surrealization (erkundet Unbewusstes = kann ernst sein, aber auch spielerisch)

**Begründung:**
- SD 3.5 TellAStory ist für ernsthafte narrative Arbeit gedacht
- Surrealization ist grenzwertig (explorativ, aber mit ernstem psychologischen Hintergrund)

---

## TEIL 3: Zusammenfassung aller Änderungen

### Configs mit Änderungen:

#### **Bauhaus**
- ❌ ENTFERNEN: narrative
- ✅ HINZUFÜGEN: algorithmic
- **Neu:** calm, chaotic→, algorithmic✓, facts, historical, create, serious

#### **ClichéFilter V2**
- ❌ ENTFERNEN: calm
- ✅ HINZUFÜGEN: chaotic
- ❌ ENTFERNEN: narrative
- ✅ HINZUFÜGEN: algorithmic
- **Neu:** chaotic✓, algorithmic✓, facts, contemporary, explore, serious

#### **ConfucianLiterati**
- ❌ ENTFERNEN: facts
- **Neu:** calm, narrative, emotion, historical, explore, serious

#### **HunkyDoryHarmonizer**
- ✅ HINZUFÜGEN: narrative
- **Neu:** calm, narrative✓, emotion, contemporary, create, playful

#### **PigLatin**
- ✅ HINZUFÜGEN: contemporary
- **Neu:** calm, algorithmic, contemporary✓, explore, playful

#### **StillePost**
- ✅ HINZUFÜGEN: contemporary
- **Neu:** chaotic, algorithmic, contemporary✓, explore, playful

#### **TheOpposite**
- ✅ HINZUFÜGEN: contemporary
- **Neu:** chaotic, algorithmic, contemporary✓, explore, playful

#### **SplitAndCombineSpherical**
- ✅ HINZUFÜGEN: contemporary
- **Neu:** chaotic, algorithmic, contemporary✓, explore, playful

#### **Overdrive**
- ✅ HINZUFÜGEN: contemporary
- **Neu:** chaotic, algorithmic, contemporary✓, explore, playful

#### **SD 3.5 TellAStory**
- ✅ HINZUFÜGEN: contemporary
- ✅ HINZUFÜGEN: serious
- **Neu:** calm, narrative, contemporary✓, create, serious✓

#### **TechnicalDrawing**
- ✅ HINZUFÜGEN: algorithmic
- **Neu:** calm, algorithmic✓, facts, contemporary, create, serious

---

## TEIL 4: Implementierungs-Plan

### Schritt 1: i18n.ts aktualisieren

Pfad: `/public/ai4artsed-frontend/src/i18n.ts`

**Deutsch:**
```typescript
properties: {
  calm: 'chillig',
  chaotic: 'wild',
  narrative: 'Geschichten erzählen',
  algorithmic: 'nach Regeln gehen',
  facts: 'harte Fakten',
  emotion: 'weiche Gefühle',
  historical: 'Geschichte',
  contemporary: 'Gegenwart',
  explore: 'KI austesten',
  create: 'Kunst machen',
  playful: 'bisschen verrückt',
  serious: 'eher ernst'
}
```

**Englisch:**
```typescript
properties: {
  calm: 'chill',
  chaotic: 'wild',
  narrative: 'tell stories',
  algorithmic: 'follow rules',
  facts: 'hard facts',
  emotion: 'soft feelings',
  historical: 'history',
  contemporary: 'present',
  explore: 'test AI',
  create: 'make art',
  playful: 'playful',
  serious: 'serious'
}
```

### Schritt 2: Config Properties aktualisieren

**11 Configs ändern:**
1. Bauhaus: `-narrative, +algorithmic`
2. ClichéFilter V2: `-calm, +chaotic, -narrative, +algorithmic`
3. ConfucianLiterati: `-facts`
4. HunkyDoryHarmonizer: `+narrative`
5. PigLatin: `+contemporary`
6. StillePost: `+contemporary`
7. TheOpposite: `+contemporary`
8. SplitAndCombineSpherical: `+contemporary`
9. Overdrive: `+contemporary`
10. SD 3.5 TellAStory: `+contemporary, +serious`
11. TechnicalDrawing: `+algorithmic`

### Schritt 3: Dokumentation

Dieses Dokument in `/docs/SESSION_37_PROPERTY_TAXONOMY_REVISION.md` sichern.

---

## Kritische Erkenntnisse

### 1. "chillig" vs. "ruhig"
**"chillig"** bedeutet NICHT Gemütszustand (ruhig), sondern **kontrollierter Kontext** (Erwartbarkeit, Steuerbarkeit). Dies ist eine pädagogische Schlüsselunterscheidung.

### 2. Geschichte vs. Gegenwart = Museal vs. Living Heritage
**Nicht temporal** (wann?), sondern **konzeptuell** (verändert es sich noch?).
- Dada = Geschichte (eingefroren seit 1930ern)
- Stille Post = Gegenwart (wird heute noch gespielt)

### 3. Property-Zuweisungen waren inkonsistent
- ClichéFilter V2 hatte "calm" (sollte "chaotic" sein)
- ConfucianLiterati hatte "facts" (ist aber hochgradig emotional)
- Bauhaus hatte "narrative" (ist aber algorithmisch/funktional)
- 6 algorithmische Spiele fehlte "contemporary"

### 4. Modalwörter sind Kontext-Geber
**"bisschen verrückt"** und **"eher ernst"** sind nicht Abschwächungen, sondern helfen durch zusätzlichen Kontext beim Verständnis (besonders für Nicht-Muttersprachler).

---

## Nächste Schritte

1. **User-Approval:** Änderungen mit Prof. Rissen besprechen
2. **Implementation:** i18n.ts + 11 Configs aktualisieren
3. **Testing:** Frontend testen mit neuen Property-Labels
4. **Git Commit:** "feat(properties): Revise taxonomy with consistent semantics"

---

**Session Duration:** ~2h (estimated)
**Files Modified:** 1 i18n file + 11 config files = 12 files
**Status:** Ready for implementation after approval
