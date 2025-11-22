# SESSION 65: Youth Flow Context Integration - Implementation Plan

**Datum**: 2025-11-22
**Session**: 65
**Status**: 🔴 PLAN ERSTELLT - BEREIT FÜR IMPLEMENTIERUNG
**Context Usage**: 84% - Agents konsultiert
**Previous Session**: Session 64 (Stage 2 endpoint refactoring)

---

## 🎯 Was verstanden wurde (via Agents)

### Architecture Agent Erkenntnisse:

**Stage 1-4 Flow (KRITISCH für Verständnis):**
```
Stage 1: Pre-Interception Safety
- NO translation! Works in original language (German for Youth)
- Bilingual §86a filter (DE/EN)
- Output: Checked text in GERMAN

Stage 2: Interception + Optimization
- Processes in original language (GERMAN)
- Media-specific optimization (optional)
- Output: Transformed prompt in GERMAN

Stage 3: Translation + Pre-Output Safety
- Translation DE → EN happens HERE!
- Before media generation
- Output: English prompt for AI models

Stage 4: Media Generation
- Uses English prompt from Stage 3
```

**Meta-Prompt System:**
- Configs store meta-prompts bilingual: `{en: "...", de: "..."}`
- `loadMetaPromptForLanguage()` extracts correct language version
- Even Youth Flow (German-only) MUST use this function
- Ensures proper store state management

**API Service Layer:**
- `transformPrompt()` from `@/services/api` - Type-safe, centralized
- Response: `response.transformed_prompt` (NOT `response.data.transformed_prompt`)
- Handles Vite proxy, error interceptors, TypeScript types
- NEVER use raw `axios.post()` directly

---

## 🐛 5 Critical Bugs Identified (via Bug Hunter Agent)

### Bug #1: Deprecated Endpoint + Raw Axios (Line 395)
**Current Code:**
```typescript
const response = await axios.post('http://localhost:17802/api/schema/pipeline/transform', {...})
```

**Problems:**
- Uses raw axios instead of typed API service
- Hardcodes `localhost:17802` (bypasses Vite proxy)
- No centralized error handling
- No TypeScript type checking
- Response structure differs from API service

**Impact**: Silent failures, wrong response parsing

---

### Bug #2: Hardcoded Schema (Lines 396, 452)
**Current Code:**
```typescript
schema: 'overdrive',  // Always 'overdrive' regardless of config!
```

**Problem**:
- User selects 'dada' or 'bauhaus' in Phase1
- Youth Flow ignores selection, always routes to 'overdrive'
- Handover doc Line 186 confirms this was reported as bug

**Impact**: Wrong pipeline executed

---

### Bug #3: Wrong Response Field (Line 406)
**Current Code:**
```typescript
interceptionResult.value = response.data.transformed_prompt || ''
```

**Problem**:
- When using `transformPrompt()` API service, response structure is:
  ```typescript
  {
    success: true,
    transformed_prompt: "...",  // Top-level, not nested!
    stage1_output: {...},
    stage2_output: {...}
  }
  ```
- Code looks for `response.data.transformed_prompt` but axios already extracted `.data`
- Should be: `response.transformed_prompt`

**Impact**: Interception result always empty (silent failure)

---

### Bug #4: Missing Context Edit Handler (Line 30 + script)
**Current Code:**
```vue
<textarea v-model="contextPrompt" />  <!-- No @input handler! -->
```

**Problem**:
- User edits context → local `contextPrompt.value` updates (v-model)
- BUT `pipelineStore.metaPromptModified` is NEVER set to true
- Backend never receives edited context
- RAM-Proxy system broken

**What's Missing:**
1. `@input="handleContextPromptEdit"` on textarea
2. `handleContextPromptEdit()` function
3. Watcher for `pipelineStore.metaPrompt` sync

**Impact**: Context edits are lost

---

### Bug #5: Missing onMounted Initialization (Line 339)
**Current Code:**
```typescript
onMounted(async () => {
  const configId = route.params.configId as string
  if (configId) {
    // MISSING: await pipelineStore.setConfig(configId)
    // MISSING: await pipelineStore.loadMetaPromptForLanguage('de')

    if (pipelineStore.metaPrompt) {
      contextPrompt.value = pipelineStore.metaPrompt
    }
  }
})
```

**Problem**:
- Config not loaded at mount
- `pipelineStore.selectedConfig` is null until user clicks
- Context not available until much later
- Breaks UX flow

**Impact**: Late initialization, null reference errors

---

## 📝 Implementation Plan (8 Fixes)

### Fix 1: Update Imports (Line ~181)
**Location**: Import section at top of `<script setup>`

**Add:**
```typescript
import { watch } from 'vue'
import { useUserPreferencesStore } from '@/stores/userPreferences'
import { transformPrompt } from '@/services/api'
```

**Remove:**
```typescript
import axios from 'axios'  // Delete this line
```

---

### Fix 2: Add Store Instance (Line ~333)
**Location**: After `const pipelineStore = usePipelineExecutionStore()`

**Add:**
```typescript
const userPreferences = useUserPreferencesStore()
```

---

### Fix 3: Fix onMounted (Line 339-372)
**Location**: Replace existing onMounted implementation

**Replace with:**
```typescript
onMounted(async () => {
  const configId = route.params.configId as string

  if (configId) {
    console.log('[Youth Flow] Received configId from Phase1:', configId)

    try {
      // STEP 1: Load config from backend
      await pipelineStore.setConfig(configId)
      console.log('[Youth Flow] Config loaded:', pipelineStore.selectedConfig?.id)

      // STEP 2: Load meta-prompt for German
      await pipelineStore.loadMetaPromptForLanguage('de')
      console.log('[Youth Flow] Meta-prompt loaded:', pipelineStore.metaPrompt?.substring(0, 50))

      // STEP 3: Initialize context prompt
      contextPrompt.value = pipelineStore.metaPrompt || ''

      // STEP 4: Auto-select category + config (existing logic)
      let foundCategory: string | null = null
      for (const [categoryId, configs] of Object.entries(configsByCategory)) {
        if (configs.some(config => config.id === configId)) {
          foundCategory = categoryId
          break
        }
      }

      if (foundCategory) {
        console.log('[Youth Flow] Auto-selecting category:', foundCategory, 'and config:', configId)
        selectedCategory.value = foundCategory
        selectedConfig.value = configId
      } else {
        console.warn('[Youth Flow] ConfigId not found in any category:', configId)
      }
    } catch (error) {
      console.error('[Youth Flow] Initialization error:', error)
    }
  }
})
```

---

### Fix 4: Add @input to Template (Line 30)
**Location**: Context textarea in template

**Change from:**
```vue
<textarea
  v-model="contextPrompt"
  placeholder="Beschreibe alles so, wie es die Vögel auf den Bäumen wahrnehmen!"
  class="bubble-textarea"
  rows="3"
></textarea>
```

**Change to:**
```vue
<textarea
  v-model="contextPrompt"
  @input="handleContextPromptEdit"
  placeholder="Beschreibe alles so, wie es die Vögel auf den Bäumen wahrnehmen!"
  class="bubble-textarea"
  rows="3"
></textarea>
```

---

### Fix 5: Fix runInterception Function (Line 391-416)
**Location**: Replace entire `runInterception` function

**Replace with:**
```typescript
async function runInterception() {
  isInterceptionLoading.value = true

  try {
    // Build request data
    const requestData: any = {
      schema: pipelineStore.selectedConfig?.pipeline || 'overdrive',
      input_text: inputText.value,
      user_language: 'de',
      execution_mode: 'eco',
      safety_level: 'youth',
      output_config: selectedConfig.value
    }

    // Conditional context sending (RAM-Proxy pattern)
    if (pipelineStore.metaPromptModified) {
      requestData.context_prompt = pipelineStore.metaPrompt
      requestData.context_language = 'de'
      console.log('[Youth Flow] Passing edited context to backend (RAM-Proxy)')
    }

    // Call API service (NOT raw axios!)
    const response = await transformPrompt(requestData)

    if (response.success) {
      interceptionResult.value = response.transformed_prompt || ''
      console.log('[Youth Flow] Interception complete:', interceptionResult.value.substring(0, 60))
    } else {
      alert(`Fehler: ${response.error}`)
    }
  } catch (error: any) {
    console.error('[Youth Flow] Interception error:', error)
    alert(`Fehler: ${error.message}`)
  } finally {
    isInterceptionLoading.value = false
  }
}
```

---

### Fix 6: Add Context Edit Handler (After line ~493)
**Location**: Add new function in Methods section

**Add:**
```typescript
function handleContextPromptEdit() {
  pipelineStore.updateMetaPrompt(contextPrompt.value)
  console.log('[Youth Flow] Context prompt edited:', contextPrompt.value.substring(0, 50) + '...')
}
```

---

### Fix 7: Add Store Watcher (End of script, before style)
**Location**: After all functions, before `</script>`

**Add:**
```typescript
// Watch metaPrompt changes and sync to local state
watch(() => pipelineStore.metaPrompt, (newMetaPrompt) => {
  if (newMetaPrompt !== contextPrompt.value) {
    contextPrompt.value = newMetaPrompt || ''
    console.log('[Youth Flow] Meta-prompt synced from store')
  }
})
```

---

### Fix 8: Fix executePipeline Schema (Line 452)
**Location**: In `executePipeline` function

**Change from:**
```typescript
schema: 'overdrive',
```

**Change to:**
```typescript
schema: pipelineStore.selectedConfig?.pipeline || 'overdrive',
```

---

## 📂 Files to Modify

### Primary File:
`public/ai4artsed-frontend/src/views/Phase2YouthFlowView.vue`

**Changes Summary:**
- Line ~181: Update imports
- Line ~333: Add userPreferences store
- Line 30: Add @input handler to textarea
- Line 339-372: Replace onMounted
- Line 391-416: Replace runInterception
- After ~493: Add handleContextPromptEdit function
- Line 452: Fix executePipeline schema
- End of script: Add watcher

**Total Locations**: 8

---

## ✅ Testing Plan

### Test 1: Initial Load
1. Navigate to Youth Flow with a config (e.g., `/youth-flow/dada`)
2. **Expected**: Context appears in "Regeln" textarea (in German)
3. **Verify**: Console shows "Config loaded" + "Meta-prompt loaded"

### Test 2: Context Editing
1. Edit text in "Regeln" textarea
2. **Expected**: Console shows "Context prompt edited"
3. **Verify**: `pipelineStore.metaPromptModified` is true (check via Vue DevTools)

### Test 3: Interception with Custom Context
1. Type input: "Ein roter Apfel"
2. Edit context: "Beschreibe es wie ein Gedicht"
3. Click config button
4. **Expected**: Interception runs with edited context
5. **Verify**: Backend logs show context_prompt in request

### Test 4: Schema Routing
1. Select 'Dada' config
2. **Expected**: Request uses `schema: 'dada'` (not 'overdrive')
3. **Verify**: Backend logs show correct schema
4. **Result**: Transformed prompt uses Dada pipeline

### Test 5: Transformed Prompt Display
1. Run interception
2. **Expected**: "Idee + Regeln = Prompt" section shows German text
3. **Verify**: Text is NOT empty
4. **Verify**: Text is in German (not English)

### Test 6: Full Flow
1. Input: "Ein Bild mit Bergen"
2. Context: Custom rules
3. Config: SD 3.5
4. **Expected**: Full pipeline works
5. **Result**: Image generates successfully

---

## 🔗 Reference Files

### Architecture Documentation:
- `docs/ARCHITECTURE PART 01 - 4-Stage Orchestration Flow.md` (Stage 1-4 flow)
- `docs/ARCHITECTURE PART 20 - Stage2-Pipeline-Capabilities.md` (Interception details)
- `docs/SESSION_YOUTH_FLOW_CONTEXT_HANDOVER.md` (Previous attempt, partially correct)

### Reference Implementation:
- `public/ai4artsed-frontend/src/views/Phase2CreativeFlowView.vue` (Kids Flow - correct pattern)

### API Service:
- `public/ai4artsed-frontend/src/services/api.ts` (transformPrompt function)

### Store:
- `public/ai4artsed-frontend/src/stores/pipelineExecution.ts` (loadMetaPromptForLanguage)

### Backend:
- `devserver/my_app/routes/schema_pipeline_routes.py` (Stage 2 endpoint implementation)

---

## 📊 Agent Consultation Summary

### devserver-architecture-expert:
✅ Confirmed Stage 1-2 work in original language (German)
✅ Confirmed Stage 3 does translation (DE→EN)
✅ Confirmed meta-prompts stored bilingual
✅ Confirmed correct endpoint: via `transformPrompt()` API service
✅ Confirmed response field: `transformed_prompt` (top-level)

### bug-hunter-analyzer:
✅ Identified 5 critical bugs with line numbers
✅ Provided root cause analysis for each
✅ Compared with Kids Flow implementation
✅ Confirmed architectural inconsistencies
✅ Validated store integration issues

---

## 🚀 Next Steps

### Immediate (Next Session):
1. Implement all 8 fixes sequentially
2. Test after each fix (incremental validation)
3. Verify with testing plan above
4. Document any issues in this file

### Follow-up:
1. Consider unifying Kids + Youth patterns (shared composable?)
2. Add TypeScript strict mode to catch similar issues
3. Document RAM-Proxy pattern in architecture docs

---

## 💡 Key Learnings

### What Was Wrong With Previous Attempts:
1. **Misunderstood translation timing** - Thought Stage 2 translated (it doesn't!)
2. **Bypassed API service layer** - Used raw axios, lost type safety
3. **Incorrect response field** - Assumed nested `.data` structure
4. **Incomplete pattern** - Copied Kids Flow but missed critical pieces

### What We Now Know:
1. **Stage 2 = German output** - Translation is Stage 3 job
2. **Always use API service** - Never raw axios for endpoints
3. **Meta-prompts are bilingual** - Even German-only flows use language loading
4. **Store patterns matter** - Watchers + handlers required for state sync

---

**Session 65 Complete - Ready for Implementation**
**Next Session**: Execute 8 fixes + test + commit
