# Property Symbols - Non-Destructive Implementation Plan

**Date:** 2025-11-09
**Session:** 40
**Status:** Ready for Implementation
**Type:** Non-destructive (parallel implementation, easy rollback)

---

## Ziel

Testweise Implementierung der Property-Symbole im Vue-Frontend **ohne bestehenden Code zu zerstören**.

### Anforderungen:
- ✅ Alter Code bleibt unverändert
- ✅ Neuer Code läuft parallel
- ✅ Einfacher Wechsel zwischen alt/neu (Feature-Flag)
- ✅ Einfaches Rollback möglich

---

## Phase 1: Backend - Property-Pairs mit Symbolen erweitern

### Schritt 1.1: Neue Datenstruktur (NON-DESTRUCTIVE)

**Datei:** `devserver/my_app/routes/schema_pipeline_routes.py`

**Aktuelle Struktur (bleibt unverändert):**
```python
property_pairs = [
    ["chill", "chaotic"],
    ["narrative", "algorithmic"],
    ["facts", "emotion"],
    ["historical", "contemporary"],
    ["explore", "create"],
    ["playful", "serious"]
]
```

**Neue Struktur (parallel hinzufügen):**
```python
# NEW: Property pairs with symbols and tooltips (v2)
# To activate: set ENABLE_PROPERTY_SYMBOLS = True
ENABLE_PROPERTY_SYMBOLS = False  # Feature flag

property_pairs_v2 = [
    {
        "id": 1,
        "pair": ["predictable", "surprising"],
        "symbols": {
            "predictable": "🎯",
            "surprising": "🎲"
        },
        "labels": {
            "de": {
                "predictable": "vorhersagbar",
                "surprising": "überraschend"
            },
            "en": {
                "predictable": "predictable",
                "surprising": "surprising"
            }
        },
        "tooltips": {
            "de": {
                "predictable": "Output ist erwartbar und steuerbar",
                "surprising": "Output ist unvorhersehbar, überraschende Wendungen"
            },
            "en": {
                "predictable": "Output is expected and controllable",
                "surprising": "Output is unpredictable with surprising turns"
            }
        }
    },
    {
        "id": 2,
        "pair": ["narrative", "algorithmic"],
        "symbols": {
            "narrative": "✍️",
            "algorithmic": "🔢"
        },
        "labels": {
            "de": {
                "narrative": "semantisch",
                "algorithmic": "syntaktisch"
            },
            "en": {
                "narrative": "semantic",
                "algorithmic": "syntactic"
            }
        },
        "tooltips": {
            "de": {
                "narrative": "Schreiben: Bedeutung und Kontext",
                "algorithmic": "Rechnen: Regeln und Schritte"
            },
            "en": {
                "narrative": "Writing: meaning and context",
                "algorithmic": "Calculating: rules and steps"
            }
        }
    },
    {
        "id": 3,
        "pair": ["facts", "emotion"],
        "symbols": {
            "facts": "🧊",
            "emotion": "🔥"
        },
        "labels": {
            "de": {
                "facts": "nüchtern",
                "emotion": "emotional"
            },
            "en": {
                "facts": "sober",
                "emotion": "emotional"
            }
        },
        "tooltips": {
            "de": {
                "facts": "Nüchterner, sachlicher Bildeindruck",
                "emotion": "Emotionaler, atmosphärischer Bildeindruck"
            },
            "en": {
                "facts": "Sober, factual image impression",
                "emotion": "Emotional, atmospheric image impression"
            }
        }
    },
    {
        "id": 4,
        "pair": ["historical", "contemporary"],
        "symbols": {
            "historical": "🏛️",
            "contemporary": "🏙️"
        },
        "labels": {
            "de": {
                "historical": "museal",
                "contemporary": "lebendig"
            },
            "en": {
                "historical": "museum",
                "contemporary": "contemporary"
            }
        },
        "tooltips": {
            "de": {
                "historical": "Museumsgebäude (historisch, eingefroren)",
                "contemporary": "Wolkenkratzer (gegenwärtig, lebendig)"
            },
            "en": {
                "historical": "Museum building (historical, frozen)",
                "contemporary": "Skyscraper (contemporary, alive)"
            }
        }
    },
    {
        "id": 5,
        "pair": ["explore", "create"],
        "symbols": {
            "explore": "🔍",
            "create": "🎨"
        },
        "labels": {
            "de": {
                "explore": "austesten",
                "create": "artikulieren"
            },
            "en": {
                "explore": "test AI",
                "create": "articulate"
            }
        },
        "tooltips": {
            "de": {
                "explore": "KI challengen, kritisch hinterfragen (Detektiv)",
                "create": "Künstlerisch ausdrücken, gestalten (Künstler)"
            },
            "en": {
                "explore": "Challenge AI, critically question (detective)",
                "create": "Artistically express, create (artist)"
            }
        }
    },
    {
        "id": 6,
        "pair": ["playful", "serious"],
        "symbols": {
            "playful": "🪁",
            "serious": "🔧"
        },
        "labels": {
            "de": {
                "playful": "verspielt",
                "serious": "ernst"
            },
            "en": {
                "playful": "playful",
                "serious": "serious"
            }
        },
        "tooltips": {
            "de": {
                "playful": "Spielerisch, viele Freiheitsgrade (Drachen)",
                "serious": "Ernst, strukturiert, Genrekonventionen (Werkzeug)"
            },
            "en": {
                "playful": "Playful, many degrees of freedom (kite)",
                "serious": "Serious, structured, genre conventions (tool)"
            }
        }
    }
]

# Legacy mapping (for backward compatibility)
property_pairs = [
    ["chill", "chaotic"],
    ["narrative", "algorithmic"],
    ["facts", "emotion"],
    ["historical", "contemporary"],
    ["explore", "create"],
    ["playful", "serious"]
]
```

### Schritt 1.2: API-Endpoint erweitern (NON-DESTRUCTIVE)

**Datei:** `devserver/my_app/routes/schema_pipeline_routes.py`

Im bestehenden Endpoint `/pipeline_configs_with_properties`:

```python
@app.route('/pipeline_configs_with_properties', methods=['GET'])
def get_pipeline_configs_with_properties():
    try:
        init_schema_engine()

        # ... existing code for loading configs ...

        # Return based on feature flag
        if ENABLE_PROPERTY_SYMBOLS:
            return jsonify({
                "configs": configs_metadata,
                "property_pairs": property_pairs_v2,  # NEW version
                "symbols_enabled": True
            })
        else:
            return jsonify({
                "configs": configs_metadata,
                "property_pairs": property_pairs,  # OLD version
                "symbols_enabled": False
            })

    except Exception as e:
        logger.error(f"Error loading configs with properties: {e}")
        return jsonify({"error": "Failed to load configs with properties"}), 500
```

**Vorteil:** Alter Code bleibt funktional, neuer Code ist opt-in via Feature-Flag

---

## Phase 2: Frontend - Parallel Implementation

### Schritt 2.1: Neue i18n Struktur (NON-DESTRUCTIVE)

**Datei:** `public/ai4artsed-frontend/src/i18n-symbols.ts` (NEU!)

```typescript
// NEW: Property symbols and tooltips (v2)
// This file is used when symbols_enabled = true

export const propertySymbols = {
  predictable: '🎯',
  surprising: '🎲',
  narrative: '✍️',
  algorithmic: '🔢',
  facts: '🧊',
  emotion: '🔥',
  historical: '🏛️',
  contemporary: '🏙️',
  explore: '🔍',
  create: '🎨',
  playful: '🪁',
  serious: '🔧'
}

export const propertyLabels = {
  de: {
    predictable: 'vorhersagbar',
    surprising: 'überraschend',
    narrative: 'semantisch',
    algorithmic: 'syntaktisch',
    facts: 'nüchtern',
    emotion: 'emotional',
    historical: 'museal',
    contemporary: 'lebendig',
    explore: 'austesten',
    create: 'artikulieren',
    playful: 'verspielt',
    serious: 'ernst'
  },
  en: {
    predictable: 'predictable',
    surprising: 'surprising',
    narrative: 'semantic',
    algorithmic: 'syntactic',
    facts: 'sober',
    emotion: 'emotional',
    historical: 'museum',
    contemporary: 'contemporary',
    explore: 'test AI',
    create: 'articulate',
    playful: 'playful',
    serious: 'serious'
  }
}

export const propertyTooltips = {
  de: {
    predictable: 'Output ist erwartbar und steuerbar',
    surprising: 'Output ist unvorhersehbar, überraschende Wendungen',
    narrative: 'Schreiben: Bedeutung und Kontext',
    algorithmic: 'Rechnen: Regeln und Schritte',
    facts: 'Nüchterner, sachlicher Bildeindruck',
    emotion: 'Emotionaler, atmosphärischer Bildeindruck',
    historical: 'Museumsgebäude (historisch, eingefroren)',
    contemporary: 'Wolkenkratzer (gegenwärtig, lebendig)',
    explore: 'KI challengen, kritisch hinterfragen (Detektiv)',
    create: 'Künstlerisch ausdrücken, gestalten (Künstler)',
    playful: 'Spielerisch, viele Freiheitsgrade (Drachen)',
    serious: 'Ernst, strukturiert, Genrekonventionen (Werkzeug)'
  },
  en: {
    predictable: 'Output is expected and controllable',
    surprising: 'Output is unpredictable with surprising turns',
    narrative: 'Writing: meaning and context',
    algorithmic: 'Calculating: rules and steps',
    facts: 'Sober, factual image impression',
    emotion: 'Emotional, atmospheric image impression',
    historical: 'Museum building (historical, frozen)',
    contemporary: 'Skyscraper (contemporary, alive)',
    explore: 'Challenge AI, critically question (detective)',
    create: 'Artistically express, create (artist)',
    playful: 'Playful, many degrees of freedom (kite)',
    serious: 'Serious, structured, genre conventions (tool)'
  }
}
```

**Alte Datei bleibt unverändert:** `src/i18n.ts`

---

### Schritt 2.2: PropertyBubble mit Symbolen (NON-DESTRUCTIVE)

**Option A: Neue Komponente erstellen**

**Datei:** `src/components/PropertyBubbleWithSymbols.vue` (NEU!)

```vue
<template>
  <div
    :class="['property-bubble-v2', { selected: isSelected }]"
    :style="bubbleStyle"
    :title="tooltip"
    @click="handleClick"
    :data-property="property"
  >
    <span class="property-symbol">{{ symbol }}</span>
    <span class="property-label">{{ label }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { propertySymbols, propertyLabels, propertyTooltips } from '@/i18n-symbols'

interface Props {
  property: string
  color: string
  isSelected: boolean
  x: number
  y: number
  language: 'de' | 'en'
}

const props = defineProps<Props>()

const emit = defineEmits<{
  toggle: [property: string]
}>()

const symbol = computed(() => propertySymbols[props.property as keyof typeof propertySymbols] || '?')
const label = computed(() => propertyLabels[props.language][props.property as keyof typeof propertyLabels.de] || props.property)
const tooltip = computed(() => propertyTooltips[props.language][props.property as keyof typeof propertyTooltips.de] || '')

const bubbleStyle = computed(() => ({
  left: `${props.x}px`,
  top: `${props.y}px`,
  '--bubble-color': props.color,
  '--bubble-shadow': props.isSelected ? `0 0 20px ${props.color}` : 'none'
}))

function handleClick() {
  emit('toggle', props.property)
}
</script>

<style scoped>
.property-bubble-v2 {
  position: absolute;
  padding: 10px 20px;
  background: rgba(20, 20, 20, 0.9);
  border: 2px solid var(--bubble-color);
  border-radius: 25px;
  color: var(--bubble-color);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  user-select: none;
  box-shadow: var(--bubble-shadow);
  transform: translate(-50%, -50%);
  display: flex;
  align-items: center;
  gap: 8px;
}

.property-symbol {
  font-size: 18px;
  line-height: 1;
}

.property-label {
  font-size: 13px;
}

.property-bubble-v2:hover {
  background: rgba(30, 30, 30, 0.95);
  transform: translate(-50%, -50%) scale(1.05);
}

.property-bubble-v2.selected {
  background: var(--bubble-color);
  color: #0a0a0a;
  font-weight: 600;
  box-shadow: 0 0 20px var(--bubble-color);
}

.property-bubble-v2.selected .property-symbol {
  filter: brightness(0.2);
}

/* Mobile: Only show symbol */
@media (max-width: 768px) {
  .property-label {
    display: none;
  }

  .property-bubble-v2 {
    padding: 12px;
  }

  .property-symbol {
    font-size: 24px;
  }
}
</style>
```

**Option B: Bestehende Komponente erweitern (mit Feature-Flag)**

**Datei:** `src/components/PropertyBubble.vue` (erweitern, nicht ersetzen)

```vue
<template>
  <div
    :class="['property-bubble', { selected: isSelected }]"
    :style="bubbleStyle"
    :title="symbolsEnabled ? tooltip : undefined"
    @click="handleClick"
    :data-property="property"
  >
    <span v-if="symbolsEnabled" class="property-symbol">{{ symbol }}</span>
    <span class="property-label">{{ label }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { propertySymbols, propertyLabels, propertyTooltips } from '@/i18n-symbols'

interface Props {
  property: string
  color: string
  isSelected: boolean
  x: number
  y: number
  symbolsEnabled?: boolean  // NEW: Feature flag
  language?: 'de' | 'en'    // NEW: Language
}

const props = withDefaults(defineProps<Props>(), {
  symbolsEnabled: false,
  language: 'de'
})

// ... rest stays the same, but add symbol/label logic ...

const symbol = computed(() => {
  if (!props.symbolsEnabled) return ''
  return propertySymbols[props.property as keyof typeof propertySymbols] || ''
})

const label = computed(() => {
  if (props.symbolsEnabled) {
    return propertyLabels[props.language][props.property as keyof typeof propertyLabels.de] || props.property
  }
  return props.$t('properties.' + props.property)
})

const tooltip = computed(() => {
  if (!props.symbolsEnabled) return ''
  return propertyTooltips[props.language][props.property as keyof typeof propertyTooltips.de] || ''
})
</script>
```

---

### Schritt 2.3: PropertyCanvas anpassen (NON-DESTRUCTIVE)

**Datei:** `src/components/PropertyCanvas.vue`

Erweitern um Feature-Flag-Support:

```vue
<script setup lang="ts">
// ... existing imports ...

interface Props {
  propertyPairs: PropertyPair[]
  selectedProperties: string[]
  canvasWidth: number
  canvasHeight: number
  symbolsEnabled?: boolean  // NEW
  language?: 'de' | 'en'    // NEW
}

const props = withDefaults(defineProps<Props>(), {
  symbolsEnabled: false,
  language: 'de'
})

// In template:
<PropertyBubble
  v-for="(property, index) in allProperties"
  :key="property"
  :property="property"
  :color="getPropertyColorByName(property)"
  :is-selected="isPropertySelected(property)"
  :x="propertyPositions[property]?.x || 0"
  :y="propertyPositions[property]?.y || 0"
  :symbols-enabled="symbolsEnabled"
  :language="language"
  @toggle="handlePropertyToggle"
/>
</script>
```

---

### Schritt 2.4: Store erweitern (NON-DESTRUCTIVE)

**Datei:** `src/stores/configSelection.ts`

```typescript
export const useConfigSelectionStore = defineStore('configSelection', () => {
  // ... existing code ...

  /** NEW: Symbols enabled flag from API */
  const symbolsEnabled = ref(false)

  async function loadConfigs() {
    isLoading.value = true
    error.value = null

    try {
      const response = await fetch('/pipeline_configs_with_properties')
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
      }

      const data: ConfigsResponse = await response.json()

      availableConfigs.value = data.configs
      propertyPairs.value = data.property_pairs
      symbolsEnabled.value = data.symbols_enabled || false  // NEW

      console.log(`[ConfigSelection] Symbols enabled: ${symbolsEnabled.value}`)
    } catch (err) {
      // ... error handling ...
    }
  }

  return {
    // ... existing exports ...
    symbolsEnabled: computed(() => symbolsEnabled.value),  // NEW
  }
})
```

---

## Phase 3: Aktivierung via Feature-Flag

### Schritt 3.1: Feature-Flag umschalten

**Backend:** `devserver/my_app/routes/schema_pipeline_routes.py`

```python
# Set to True to enable symbols
ENABLE_PROPERTY_SYMBOLS = True  # <-- HIER UMSCHALTEN
```

**Das war's!** Frontend erkennt automatisch `symbols_enabled: true` und zeigt Symbole.

---

### Schritt 3.2: Rollback (falls Probleme)

**Einfach Feature-Flag zurücksetzen:**

```python
ENABLE_PROPERTY_SYMBOLS = False
```

**Kein Code muss gelöscht werden!**

---

## Phase 4: Testing-Checkliste

### Backend-Tests:

- [ ] API `/pipeline_configs_with_properties` mit `ENABLE_PROPERTY_SYMBOLS = False`
  - [ ] Returns `symbols_enabled: false`
  - [ ] Returns old `property_pairs` structure

- [ ] API mit `ENABLE_PROPERTY_SYMBOLS = True`
  - [ ] Returns `symbols_enabled: true`
  - [ ] Returns new `property_pairs_v2` structure with symbols
  - [ ] All 6 pairs have symbols, labels, tooltips

### Frontend-Tests:

- [ ] PropertyBubble zeigt Text ohne Symbole (symbols_enabled = false)
- [ ] PropertyBubble zeigt Symbol + Text (symbols_enabled = true)
- [ ] Tooltip erscheint on hover
- [ ] Mobile: Nur Symbol, kein Text
- [ ] Desktop: Symbol + Text
- [ ] Config-Auswahl funktioniert wie vorher
- [ ] XOR-Logik funktioniert wie vorher

### User-Tests (mit Jugendlichen):

- [ ] Sind Symbole intuitiv verständlich?
- [ ] Helfen Tooltips beim Verständnis?
- [ ] Bevorzugen sie mit oder ohne Symbole?
- [ ] Gibt es Symbole die unklar sind?

---

## Phase 5: Finalisierung (nach erfolgreichem Test)

### Wenn Symbole gut funktionieren:

1. **Feature-Flag entfernen** (Code aufräumen)
2. **Alte property_pairs entfernen**
3. **property_pairs_v2 → property_pairs umbenennen**
4. **Alte PropertyBubble-Variante entfernen (falls neu erstellt)**

### Wenn Symbole nicht funktionieren:

1. **Feature-Flag auf false lassen**
2. **Dokumentieren warum nicht**
3. **Code bleibt für spätere Iteration**

---

## Datei-Übersicht

### Neue Dateien (werden erstellt):
```
docs/PROPERTY_SYMBOLS_IMPLEMENTATION_PLAN.md  (diese Datei)
public/ai4artsed-frontend/src/i18n-symbols.ts (Symbol-Definitionen)
```

### Optional neue Datei:
```
public/ai4artsed-frontend/src/components/PropertyBubbleWithSymbols.vue
```

### Geänderte Dateien (non-destructive):
```
devserver/my_app/routes/schema_pipeline_routes.py  (property_pairs_v2 hinzufügen)
public/ai4artsed-frontend/src/components/PropertyBubble.vue  (symbolsEnabled flag)
public/ai4artsed-frontend/src/components/PropertyCanvas.vue  (props erweitern)
public/ai4artsed-frontend/src/stores/configSelection.ts  (symbolsEnabled state)
```

### Unverändert (bleiben wie sie sind):
```
public/ai4artsed-frontend/src/i18n.ts  (alte Übersetzungen)
public/ai4artsed-frontend/src/components/*.vue  (alle anderen)
devserver/schemas/configs/interception/*.json  (configs unverändert)
```

---

## Implementierungs-Reihenfolge

### Tag 1: Backend (30 Min)
1. property_pairs_v2 in schema_pipeline_routes.py hinzufügen
2. Feature-Flag hinzufügen (ENABLE_PROPERTY_SYMBOLS = False)
3. API-Response erweitern
4. Backend-Server neu starten
5. Testen: API mit curl

### Tag 2: Frontend Struktur (1h)
1. i18n-symbols.ts erstellen
2. PropertyBubble.vue erweitern (oder neu erstellen)
3. PropertyCanvas.vue anpassen
4. configSelection.ts Store erweitern

### Tag 3: Testing & Refinement (2h)
1. Feature-Flag auf True setzen
2. Frontend neu builden
3. Symbole im Browser testen
4. Tooltips testen
5. Mobile-Ansicht testen
6. Feedback sammeln

### Tag 4: User-Testing (optional)
1. Mit 5-10 Jugendlichen testen
2. Feedback dokumentieren
3. Anpassungen falls nötig

---

**Status:** Ready for Implementation
**Geschätzter Aufwand:** 3-4 Stunden Development + Testing
**Risiko:** Sehr niedrig (non-destructive, easy rollback)
**Nächster Schritt:** Backend property_pairs_v2 hinzufügen
