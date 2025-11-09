# Implementation Plan: Phase 1 Property-Based Quadrant Selection

**Created:** 2025-11-07
**Status:** Ready for Implementation
**Estimated Time:** 3-4 days

---

## Overview

Implement a property-based visual selection interface for Phase 1 config selection, replacing the traditional tile/list/LLM modes with an organic, quadrant-based approach where users select properties and configs appear dynamically.

---

## Design Principles

1. **Anti-Solutionist:** No middle ground, forces positioning
2. **XOR within pairs:** Opposing properties mutually exclusive
3. **AND across pairs:** Properties from different pairs combine
4. **Visual clarity:** Rubber bands show connections, color-coded
5. **Organic layout:** Configs float randomly, no rigid grid
6. **Lower-half bias:** 80% of configs in Quadrants III & IV

---

## Architecture Components

### 1. Backend API Extension

**File:** `/devserver/api/schema_pipeline_routes.py`

#### New Endpoint: `/pipeline_configs_with_properties`

```python
@app.route('/pipeline_configs_with_properties', methods=['GET'])
def get_configs_with_properties():
    """
    Returns all configs with their properties metadata.

    Response format:
    {
        "configs": [
            {
                "id": "dada",
                "name": {"de": "Dada", "en": "Dada"},
                "icon": "🎨",
                "description": {
                    "de": "Zerstört Bedeutung. Du verlierst Kontrolle. KI produziert Nonsens.",
                    "en": "Destroys meaning. You lose control. AI produces nonsense."
                },
                "properties": ["chaotic", "narrative", "emotion", "historical", "create", "playful"],
                "difficulty": 3,
                "category": "art_movements",
                "pipeline": "text_transformation"
            },
            ...
        ],
        "property_pairs": [
            ["calm", "chaotic"],
            ["narrative", "algorithmic"],
            ["facts", "emotion"],
            ["historical", "contemporary"],
            ["explore", "create"],
            ["playful", "serious"]
        ]
    }
    ```

#### Config Metadata Addition

**File:** `/devserver/schemas/configs/interception/*.json`

Add `properties` field to all configs:

```json
{
  "id": "dada",
  "name": { "de": "Dada", "en": "Dada" },
  "properties": ["chaotic", "narrative", "emotion", "historical", "create", "playful"],
  "display": {
    "icon": "🎨",
    "phase1_description": {
      "de": "Zerstört Bedeutung. Du verlierst Kontrolle. KI produziert Nonsens.",
      "en": "Destroys meaning. You lose control. AI produces nonsense."
    }
  }
}
```

**Task:** Add properties to all 21 active configs based on `PROPERTY_TAXONOMY_ITERATION_03_BRAINSTORMING.md`

---

### 2. Frontend Vue Component Structure

**Base Path:** `/frontend/src/components/Phase1/`

```
Phase1/
├── PropertyQuadrants.vue         # Main container (4 quadrants)
├── PropertyCanvas.vue            # Quadrant II - property bubbles + rubber bands
├── ConfigCanvas.vue              # Quadrants I, III, IV - floating configs
├── PropertyBubble.vue            # Individual property bubble
├── RubberBand.vue                # SVG rubber band connector
├── ConfigCard.vue                # Floating config card
└── EmptyState.vue                # No configs / no selection state
```

---

### 3. State Management (Pinia)

**File:** `/frontend/src/stores/configSelectionStore.js`

```javascript
import { defineStore } from 'pinia'

export const useConfigSelectionStore = defineStore('configSelection', {
  state: () => ({
    // Available configs from API
    configs: [],

    // Property pairs structure
    propertyPairs: [],

    // Selected properties (Set for uniqueness)
    selectedProperties: new Set(),

    // Filtered configs based on selection
    matchedConfigs: [],

    // Selected config (for Phase 2 transition)
    selectedConfig: null
  }),

  getters: {
    // Calculate match scores for all configs
    configsWithScores(state) {
      return state.configs.map(config => {
        const matches = config.properties.filter(p =>
          state.selectedProperties.has(p)
        ).length
        const matchScore = state.selectedProperties.size > 0
          ? matches / state.selectedProperties.size
          : 0
        return { config, matches, matchScore }
      }).filter(item => item.matches > 0)
    },

    // Check if any property is selected
    hasSelection(state) {
      return state.selectedProperties.size > 0
    }
  },

  actions: {
    // Load configs from API
    async loadConfigs() {
      const response = await fetch('/pipeline_configs_with_properties')
      const data = await response.json()
      this.configs = data.configs
      this.propertyPairs = data.property_pairs
    },

    // Toggle property with XOR logic
    toggleProperty(property) {
      if (this.selectedProperties.has(property)) {
        // Deselect
        this.selectedProperties.delete(property)
      } else {
        // Select and deselect opposite
        this.selectedProperties.add(property)

        // Find opposite and deselect if selected
        const opposite = this.findOpposite(property)
        if (opposite && this.selectedProperties.has(opposite)) {
          this.selectedProperties.delete(opposite)
        }
      }

      // Trigger reactivity
      this.selectedProperties = new Set(this.selectedProperties)
    },

    // Find opposite property in pair
    findOpposite(property) {
      for (const [prop1, prop2] of this.propertyPairs) {
        if (prop1 === property) return prop2
        if (prop2 === property) return prop1
      }
      return null
    },

    // Select config for Phase 2
    selectConfig(configId) {
      this.selectedConfig = this.configs.find(c => c.id === configId)
    },

    // Clear selection
    clearSelection() {
      this.selectedProperties.clear()
      this.selectedConfig = null
    }
  }
})
```

---

### 4. Key Implementation Details

#### A. No Overlapping Tiles

**Algorithm:** Force Field / Physics-based positioning

```javascript
// In ConfigCanvas.vue
function positionConfigsWithoutOverlap(configs, quadrantBounds) {
  const positions = []
  const cardWidth = 200
  const cardHeight = 220
  const padding = 20
  const maxAttempts = 50

  configs.forEach((config, index) => {
    let position = null
    let attempts = 0

    while (!position && attempts < maxAttempts) {
      // Generate random position
      const x = Math.random() * (quadrantBounds.width - cardWidth - padding)
      const y = Math.random() * (quadrantBounds.height - cardHeight - padding)

      // Check for overlaps with existing positions
      const overlaps = positions.some(pos => {
        return !(
          x + cardWidth + padding < pos.x ||
          x > pos.x + cardWidth + padding ||
          y + cardHeight + padding < pos.y ||
          y > pos.y + cardHeight + padding
        )
      })

      if (!overlaps) {
        position = { x, y, config }
      }

      attempts++
    }

    // If no position found after max attempts, use grid fallback
    if (!position) {
      const cols = Math.floor(quadrantBounds.width / (cardWidth + padding))
      const row = Math.floor(positions.length / cols)
      const col = positions.length % cols
      position = {
        x: col * (cardWidth + padding) + padding,
        y: row * (cardHeight + padding) + padding,
        config
      }
    }

    positions.push(position)
  })

  return positions
}
```

**Alternative (Simpler):** Grid with jitter

```javascript
function positionConfigsWithJitter(configs, quadrantBounds) {
  const cardWidth = 200
  const cardHeight = 220
  const padding = 30
  const jitter = 20 // Random offset

  const cols = Math.floor(quadrantBounds.width / (cardWidth + padding))

  return configs.map((config, index) => {
    const row = Math.floor(index / cols)
    const col = index % cols

    return {
      x: col * (cardWidth + padding) + padding + (Math.random() - 0.5) * jitter,
      y: row * (cardHeight + padding) + padding + (Math.random() - 0.5) * jitter,
      config
    }
  })
}
```

**Recommendation:** Start with grid+jitter (simpler), upgrade to force field if needed.

---

#### B. Handling No Config Matches

**Strategy 1: Suggest Similar Combinations**

```javascript
// In configSelectionStore.js
getters: {
  // Find configs with partial matches
  partialMatches(state) {
    if (state.selectedProperties.size === 0) return []

    return state.configs.map(config => {
      const matches = config.properties.filter(p =>
        state.selectedProperties.has(p)
      ).length
      return { config, matches }
    })
    .filter(item => item.matches > 0)
    .sort((a, b) => b.matches - a.matches)
    .slice(0, 5) // Top 5 partial matches
  },

  // Suggest property adjustments
  suggestedAdjustments(state) {
    // Find which single property change would yield results
    const suggestions = []

    state.propertyPairs.forEach(([prop1, prop2]) => {
      const current = state.selectedProperties.has(prop1) ? prop1 :
                     state.selectedProperties.has(prop2) ? prop2 : null

      if (current) {
        const opposite = current === prop1 ? prop2 : prop1

        // Check if switching would yield results
        const testSet = new Set(state.selectedProperties)
        testSet.delete(current)
        testSet.add(opposite)

        const matches = state.configs.filter(config =>
          config.properties.some(p => testSet.has(p))
        ).length

        if (matches > 0) {
          suggestions.push({
            from: current,
            to: opposite,
            matchCount: matches
          })
        }
      }
    })

    return suggestions.sort((a, b) => b.matchCount - a.matchCount)
  }
}
```

**UI Component: NoConfigsState.vue**

```vue
<template>
  <div class="no-configs-state">
    <div class="icon">🤔</div>
    <h3>Keine Workflows mit dieser Kombination</h3>

    <div v-if="partialMatches.length > 0" class="suggestions">
      <p>Aber diese könnten interessant sein:</p>
      <div class="partial-matches">
        <ConfigCard
          v-for="item in partialMatches"
          :key="item.config.id"
          :config="item.config"
          :matchCount="item.matches"
          @click="selectConfig(item.config.id)"
        />
      </div>
    </div>

    <div v-if="suggestedAdjustments.length > 0" class="adjustments">
      <p>Versuche:</p>
      <button
        v-for="suggestion in suggestedAdjustments.slice(0, 3)"
        :key="suggestion.from + suggestion.to"
        @click="applySuggestion(suggestion)"
        class="suggestion-btn"
      >
        {{ suggestion.from }} → {{ suggestion.to }}
        <span class="match-count">({{ suggestion.matchCount }} Workflows)</span>
      </button>
    </div>

    <button @click="clearSelection" class="clear-btn">
      Auswahl zurücksetzen
    </button>
  </div>
</template>
```

**Strategy 2: Ensure Coverage (Ideal)**

**File:** `/devserver/scripts/validate_property_coverage.py`

```python
#!/usr/bin/env python3
"""
Validate that all reasonable property combinations have at least one config.
"""

import json
import itertools
from pathlib import Path

def load_configs():
    """Load all configs with properties."""
    configs_dir = Path(__file__).parent.parent / 'schemas/configs/interception'
    configs = []

    for config_file in configs_dir.glob('*.json'):
        with open(config_file) as f:
            config = json.load(f)
            if 'properties' in config:
                configs.append(config)

    return configs

def get_property_pairs():
    """Define the 6 property pairs."""
    return [
        ('calm', 'chaotic'),
        ('narrative', 'algorithmic'),
        ('facts', 'emotion'),
        ('historical', 'contemporary'),
        ('explore', 'create'),
        ('playful', 'serious')
    ]

def generate_reasonable_combinations():
    """
    Generate reasonable property combinations.
    We consider combinations of 2-6 properties (one from each pair).
    """
    pairs = get_property_pairs()

    # All possible selections (one per pair, or none)
    combinations = []

    # Generate all possible combinations
    for r in range(2, 7):  # 2 to 6 properties
        for combo_pairs in itertools.combinations(range(len(pairs)), r):
            # For each selected pair, try both properties
            for selections in itertools.product([0, 1], repeat=len(combo_pairs)):
                combo = []
                for i, pair_idx in enumerate(combo_pairs):
                    property_choice = selections[i]
                    combo.append(pairs[pair_idx][property_choice])
                combinations.append(frozenset(combo))

    return combinations

def find_uncovered_combinations(configs, combinations):
    """Find combinations with no matching configs."""
    uncovered = []

    for combo in combinations:
        # Check if any config matches all properties in combo
        matches = [c for c in configs if combo.issubset(set(c['properties']))]

        if not matches:
            uncovered.append(combo)

    return uncovered

def main():
    configs = load_configs()
    combinations = generate_reasonable_combinations()
    uncovered = find_uncovered_combinations(configs, combinations)

    print(f"Total configs: {len(configs)}")
    print(f"Total combinations checked: {len(combinations)}")
    print(f"Uncovered combinations: {len(uncovered)}\n")

    if uncovered:
        print("Missing coverage for:")
        for combo in sorted(uncovered, key=lambda x: len(x), reverse=True)[:20]:
            print(f"  - {', '.join(sorted(combo))}")

        print("\n⚠️  Consider creating configs for high-priority gaps!")
    else:
        print("✅ All reasonable combinations covered!")

if __name__ == '__main__':
    main()
```

---

#### C. Rubber Band Implementation

**Component:** `RubberBand.vue`

```vue
<template>
  <svg class="rubber-bands" :viewBox="`0 0 ${width} ${height}`">
    <path
      v-for="(band, index) in rubberBands"
      :key="index"
      :d="band.path"
      :stroke="band.color"
      :class="['rubber-band', { active: band.active }]"
      class="rubber-band"
    />
  </svg>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useConfigSelectionStore } from '@/stores/configSelectionStore'

const props = defineProps({
  bubbles: Array // Array of bubble elements
})

const store = useConfigSelectionStore()
const width = ref(0)
const height = ref(0)

// Calculate rubber band paths
const rubberBands = computed(() => {
  if (!props.bubbles || props.bubbles.length === 0) return []

  const bands = []

  // Group bubbles by pair
  const pairs = {}
  props.bubbles.forEach(bubble => {
    const pairId = bubble.dataset.pair
    if (!pairs[pairId]) pairs[pairId] = []
    pairs[pairId].push(bubble)
  })

  // Draw bands between each pair
  Object.entries(pairs).forEach(([pairId, bubbles]) => {
    if (bubbles.length !== 2) return

    const [bubble1, bubble2] = bubbles
    const rect1 = bubble1.getBoundingClientRect()
    const rect2 = bubble2.getBoundingClientRect()

    const x1 = rect1.left + rect1.width / 2
    const y1 = rect1.top + rect1.height / 2
    const x2 = rect2.left + rect2.width / 2
    const y2 = rect2.top + rect2.height / 2

    // Quadratic curve for organic feel
    const cx = (x1 + x2) / 2
    const cy = (y1 + y2) / 2 + 20

    const path = `M ${x1} ${y1} Q ${cx} ${cy} ${x2} ${y2}`

    // Check if either property is selected
    const prop1 = bubble1.dataset.property
    const prop2 = bubble2.dataset.property
    const active = store.selectedProperties.has(prop1) ||
                   store.selectedProperties.has(prop2)

    bands.push({
      path,
      color: getColorForPair(parseInt(pairId)),
      active
    })
  })

  return bands
})

function getColorForPair(pairId) {
  const colors = {
    1: '#9b59b6',
    2: '#3498db',
    3: '#e74c3c',
    4: '#f39c12',
    5: '#2ecc71',
    6: '#f1c40f'
  }
  return colors[pairId] || '#888'
}

function updateSize() {
  width.value = window.innerWidth
  height.value = window.innerHeight
}

onMounted(() => {
  updateSize()
  window.addEventListener('resize', updateSize)
})

onUnmounted(() => {
  window.removeEventListener('resize', updateSize)
})
</script>

<style scoped>
.rubber-bands {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 2;
}

.rubber-band {
  stroke-width: 3;
  fill: none;
  stroke-dasharray: 8 4;
  animation: rubberFlow 3s linear infinite;
  filter: drop-shadow(0 0 8px currentColor);
  opacity: 0.6;
  transition: all 0.3s;
}

.rubber-band.active {
  stroke-width: 4;
  opacity: 1;
  filter: drop-shadow(0 0 12px currentColor);
}

@keyframes rubberFlow {
  to { stroke-dashoffset: -12; }
}
</style>
```

---

## Implementation Steps

### Phase 1: Backend Preparation (Day 1)

1. ✅ **Add properties to all 21 configs**
   - Use data from `PROPERTY_TAXONOMY_ITERATION_03_BRAINSTORMING.md`
   - Add `properties` array to each config JSON
   - Add `display.phase1_description` for agency-oriented text

2. ✅ **Create API endpoint**
   - `/pipeline_configs_with_properties` in `schema_pipeline_routes.py`
   - Return configs with properties + property pairs structure

3. ✅ **Validation script**
   - Create `/devserver/scripts/validate_property_coverage.py`
   - Run to identify gaps
   - Document gaps for future config creation

### Phase 2: Frontend Structure (Day 2 Morning)

4. ✅ **Create Pinia store**
   - `/frontend/src/stores/configSelectionStore.js`
   - XOR logic for property pairs
   - Match score calculation
   - Partial match suggestions

5. ✅ **Create base components**
   - `PropertyQuadrants.vue` - Main container
   - `PropertyCanvas.vue` - Quadrant II
   - `ConfigCanvas.vue` - Quadrants I, III, IV
   - `PropertyBubble.vue`
   - `ConfigCard.vue`
   - `EmptyState.vue`
   - `NoConfigsState.vue`

### Phase 3: Visual Implementation (Day 2 Afternoon - Day 3)

6. ✅ **Implement property bubbles**
   - Positioning in Quadrant II
   - Click handlers with XOR logic
   - Selected state styling

7. ✅ **Implement rubber bands**
   - SVG path calculation
   - Color coding by pair
   - Active state when property selected
   - Resize handling

8. ✅ **Implement config cards**
   - Grid+jitter positioning algorithm
   - Overlap prevention
   - Weighted random distribution (80% lower half)
   - Staggered animation
   - Property tag display

9. ✅ **Implement empty/no-match states**
   - EmptyState when nothing selected
   - NoConfigsState with suggestions
   - Partial match display
   - Property adjustment buttons

### Phase 4: Integration & Polish (Day 3 - Day 4)

10. ✅ **Wire up to router**
    - Make Phase 1 entry point
    - Transition to Phase 2 on config selection

11. ✅ **Responsive design**
    - Mobile/tablet layouts
    - Touch interactions
    - Rubber band scaling

12. ✅ **Accessibility**
    - Keyboard navigation
    - Screen reader labels
    - Focus management

13. ✅ **Testing**
    - Property selection logic
    - Config filtering
    - Overlap prevention
    - Edge cases (no matches)

14. ✅ **Documentation**
    - Update ARCHITECTURE.md
    - Add to DEVELOPMENT_LOG.md
    - Screenshot for docs

---

## Testing Checklist

### Unit Tests
- [ ] Property XOR logic (opposites mutually exclusive)
- [ ] Property AND logic (across pairs combinable)
- [ ] Match score calculation
- [ ] Partial match suggestions
- [ ] Config positioning without overlap

### Integration Tests
- [ ] API endpoint returns correct data
- [ ] Store state updates on property toggle
- [ ] Rubber bands update on selection
- [ ] Configs filter correctly
- [ ] No-match state shows suggestions

### E2E Tests
- [ ] User can select properties
- [ ] Configs appear in correct quadrants
- [ ] Clicking config transitions to Phase 2
- [ ] Empty state shows when nothing selected
- [ ] No-match state shows appropriate suggestions
- [ ] Responsive layout works on mobile

---

## Edge Cases & Error Handling

1. **No configs match selected properties**
   - Show NoConfigsState
   - Display partial matches
   - Suggest property adjustments
   - Provide reset button

2. **Too many configs (>20)**
   - Limit display to top 20 by match score
   - Add "Show more" button if needed
   - Ensure performance stays smooth

3. **Single config matches**
   - Still show in random position
   - Maybe suggest similar configs?

4. **API failure**
   - Show error state
   - Provide retry button
   - Cache last successful response

5. **Browser doesn't support required features**
   - Graceful degradation to list view
   - Feature detection

---

## Performance Considerations

1. **Config positioning**
   - Compute positions once, cache
   - Only recompute on selection change
   - Use CSS transforms (not top/left) for animation

2. **Rubber bands**
   - Use single SVG element
   - Debounce resize events
   - Only redraw on selection change

3. **Property bubbles**
   - Virtual positioning (CSS only)
   - No DOM updates unless selection changes

4. **Config cards**
   - Lazy load if >20 configs
   - Use intersection observer for off-screen cards
   - Optimize property tag rendering

---

## Future Enhancements (Post-MVP)

1. **Physics-based positioning**
   - Replace grid+jitter with force-directed layout
   - Configs repel each other organically
   - Smooth animation between states

2. **Property relationship visualization**
   - Show which properties are commonly combined
   - Thickness of rubber bands indicates usage frequency

3. **User preference persistence**
   - Remember last selection
   - Save favorite combinations

4. **LLM-assisted property selection**
   - "Help me choose" button
   - Conversational interface suggests properties
   - Integration with Mode C from original plan

5. **Analytics**
   - Track which property combinations are popular
   - Identify gaps in config coverage
   - Inform future config creation

---

## Dependencies

### Backend
- Flask (existing)
- JSON config loader (existing)

### Frontend
- Vue 3 (planned)
- Pinia (planned)
- Vue Router (planned)

### New
- None! Uses existing stack

---

## Success Criteria

✅ **Functional:**
- [ ] All 21 configs have properties assigned
- [ ] Property XOR logic works correctly
- [ ] Configs filter based on selected properties
- [ ] No config tiles overlap
- [ ] No-match state provides helpful suggestions
- [ ] Config selection transitions to Phase 2

✅ **Pedagogical:**
- [ ] Interface forces positioning (no defaults)
- [ ] Agency-oriented descriptions visible
- [ ] Rubber bands make relationships clear
- [ ] Experience feels organic, not mechanical

✅ **Technical:**
- [ ] API response time <100ms
- [ ] UI updates <16ms (60fps)
- [ ] Works on Chrome, Firefox, Safari
- [ ] Mobile responsive

---

## Rollout Plan

### Stage 1: Backend Only (Can merge immediately)
- Add properties to configs
- Add API endpoint
- Backward compatible (doesn't break existing UI)

### Stage 2: Frontend Parallel Development
- Develop components in isolation
- Use Storybook for component development
- No impact on existing Phase 1

### Stage 3: Integration
- Wire up to router as `/phase1-v2`
- A/B test with original Phase 1
- Collect user feedback

### Stage 4: Replacement
- Make default Phase 1
- Archive old Phase 1 components
- Update docs

---

## Open Questions

1. **Should we show config difficulty in this view?**
   - Pro: Helps users understand complexity
   - Con: May bias toward easier configs
   - **Decision:** Show as small indicator, not prominent

2. **What happens if a config has 0 selected properties?**
   - Should it appear at all?
   - **Decision:** Only show configs with >0 matches

3. **Should rubber bands always be visible or only when property is selected?**
   - **Decision:** Always visible (dim), bright when active

4. **Quadrant labels: keep or remove?**
   - **Decision:** Remove in production (only for mockup clarity)

---

## Resources

- **Mockup:** `/docs/tmp/mockup_phase1_property_quadrants.html`
- **Property Taxonomy:** `/docs/tmp/PROPERTY_TAXONOMY_ITERATION_03_BRAINSTORMING.md`
- **Gap Analysis:** `/docs/tmp/PROPERTY_GAP_ANALYSIS.md`
- **Original Frontend Spec:** `/docs/tmp/FRONTEND_02_PHASE_1_SCHEMA_SELECTION.md`

---

**Ready to implement!** 🚀
