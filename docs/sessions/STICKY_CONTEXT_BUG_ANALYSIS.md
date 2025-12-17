# Sticky Context Bug - Root Cause Analysis
**Date**: 2025-11-14
**Component**: Phase2CreativeFlowView.vue
**Issue**: Old config context remains visible when switching to new config

---

## PROBLEM DESCRIPTION

**User Flow:**
1. Select Config A (e.g. "Bauhaus") → Phase 2 view opens, shows Bauhaus context
2. Click "Back" button → Returns to config selection
3. Select Config B (e.g. "Dada") → Phase 2 view opens, BUT still shows Bauhaus context

**Expected Behavior:**
- Config B's context should replace Config A's context

**Actual Behavior:**
- Config A's context remains "sticky" in the textarea

---

## ARCHITECTURE ANALYSIS

### 1. Router Configuration

```typescript
// src/router/index.ts
{
  path: '/execute/:configId',
  name: 'pipeline-execution',
  component: () => import('../views/Phase2CreativeFlowView.vue'),
}
```

**Key Finding:** Route uses dynamic parameter `:configId`

### 2. Vue Router Behavior with Dynamic Parameters

When navigating from `/execute/bauhaus` to `/execute/dada`:
- **Same route**, only parameter changes
- Vue Router **REUSES the same component instance** (optimization)
- Component is **NOT unmounted and remounted**
- **Only `route.params` changes**
- **`onMounted()` is NOT called again**

**This is BY DESIGN in Vue Router!**

### 3. Component Lifecycle Analysis

```typescript
// Phase2CreativeFlowView.vue line 392-435
onMounted(async () => {
  const configId = route.params.configId as string

  // Load config
  await pipelineStore.setConfig(configId)

  // Load meta-prompt
  await pipelineStore.loadMetaPromptForLanguage(userPreferences.language)

  // Initialize editable meta-prompt
  editableMetaPrompt.value = pipelineStore.metaPrompt || ''

  // ...more init code
})
```

**Problem:** This only runs ONCE on first mount!

### 4. Store State Management

```typescript
// src/stores/pipelineExecution.ts

// Store state (persists across navigation):
const metaPrompt = ref('')  // Currently loaded meta-prompt
const originalMetaPrompt = ref('')  // For modification tracking

// setConfig() - loads config metadata ONLY
async function setConfig(configId: string) {
  const config = await getConfig(configId)
  selectedConfig.value = config
  // Does NOT clear or reload metaPrompt!
}

// loadMetaPromptForLanguage() - loads context
async function loadMetaPromptForLanguage(language: 'de' | 'en') {
  const contextData = await getConfigContext(selectedConfig.value.id)
  metaPrompt.value = contextText  // Updates store
  originalMetaPrompt.value = contextText
}
```

**Key Finding:** Store is a **singleton** - state persists across navigation!

### 5. Current Watchers

```typescript
// Watch 1: Language changes
watch(
  () => userPreferences.language,
  async (newLang) => {
    await pipelineStore.loadMetaPromptForLanguage(newLang)
    editableMetaPrompt.value = pipelineStore.metaPrompt || ''
  }
)

// Watch 2: Store metaPrompt changes
watch(
  () => pipelineStore.metaPrompt,
  (newMetaPrompt) => {
    if (editableMetaPrompt.value !== newMetaPrompt) {
      editableMetaPrompt.value = newMetaPrompt
    }
  }
)
```

**Problem:** NO watch on `route.params.configId` changes!

---

## ROOT CAUSE IDENTIFICATION

### The Bug Chain:

1. **First config load (Bauhaus)**:
   - `onMounted()` fires
   - Loads Bauhaus config
   - Loads Bauhaus context → `pipelineStore.metaPrompt = "Bauhaus instructions..."`
   - Sets `editableMetaPrompt.value = "Bauhaus instructions..."`
   - User sees Bauhaus context ✅

2. **Navigate back**:
   - Component may or may not unmount (depends on router keep-alive)
   - Store state **PERSISTS** (Pinia stores are singletons)
   - `pipelineStore.metaPrompt` still contains "Bauhaus instructions..."

3. **Second config load (Dada)**:
   - User selects Dada
   - Router navigates to `/execute/dada`
   - Vue Router sees: "Same route, different param" → **REUSES component instance**
   - **`onMounted()` does NOT fire** (component already mounted)
   - **No code triggers** to load Dada config and context!
   - Store still has `pipelineStore.metaPrompt = "Bauhaus instructions..."`
   - `editableMetaPrompt.value` still shows "Bauhaus instructions..." ❌
   - User sees OLD context (Bauhaus) instead of NEW context (Dada)

**Root Cause:** Component reuse without re-initialization logic for parameter changes.

---

## WHY QUICK FIX FAILED

### Attempted Fix:
```typescript
watch(
  () => route.params.configId,
  async (newConfigId, oldConfigId) => {
    // Reload config and context
  }
)
```

### Why It Might Fail:

**Hypothesis 1: Watch Timing**
- Watch may fire BEFORE component is ready
- DOM refs (`editableMetaPrompt`) might not be initialized yet

**Hypothesis 2: Reactive Chain Break**
- Store update → Component update chain might be broken
- `watch(() => pipelineStore.metaPrompt, ...)` should propagate but might not fire

**Hypothesis 3: Component State Desync**
- Local `editableMetaPrompt` ref becomes desynchronized from store
- Watch on `pipelineStore.metaPrompt` has guard: `if (editableMetaPrompt.value !== newMetaPrompt)`
- This guard might PREVENT update if values are equal (but shouldn't be)

---

## PROPER SOLUTION REQUIREMENTS

A proper fix must:

1. ✅ Detect `route.params.configId` changes
2. ✅ Clear OLD config state completely
3. ✅ Load NEW config metadata
4. ✅ Load NEW config context
5. ✅ Update `editableMetaPrompt` with NEW context
6. ✅ Clear any derived state (transformed prompt, etc.)
7. ✅ Handle loading states properly
8. ✅ Maintain consistency between store and component state

---

## INVESTIGATION NEEDED

To determine correct fix, need to verify:

1. **Component Lifecycle:**
   - Add console.log in onMounted, onUnmounted, onBeforeMount
   - Verify component reuse vs. remount behavior

2. **Watch Behavior:**
   - Add console.log in watch callbacks
   - Verify watch fires on configId change
   - Check timing: Does watch fire before or after component update?

3. **Store State:**
   - Add console.log in store actions
   - Verify store updates propagate to component
   - Check if store.metaPrompt actually changes

4. **Reactive Chain:**
   - Trace full reactive dependency chain
   - Store.metaPrompt → Component.watch → editableMetaPrompt.value → textarea v-model

---

## NEXT STEPS

1. Add comprehensive logging to trace execution flow
2. Test navigation: A → back → B
3. Capture console output for analysis
4. Identify exact point where state desynchronization occurs
5. Design fix based on findings (not guesses)

---

## NOTES

- User explicitly requested: "keine QUICK fixes hier"
- User wants: "sauberen und konsistenten Code"
- User wants: "Ausführliche Analyse der Fehlerursache"
- This document fulfills that requirement
- Next: Implement proper fix based on investigation results
