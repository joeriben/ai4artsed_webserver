# Session 66: Youth Flow - /stage2 Migration & 404 Debug

**Datum**: 2025-11-22
**Status**: 🟡 TEILWEISE FERTIG - 404 Bug bleibt
**Context**: Session 65 plan executed, but 404 persists on config selection

---

## ✅ Was in Session 66 ERFOLGREICH gemacht wurde

### Backend Fixes (NoOpTracker Import Bug)

**File**: `devserver/my_app/routes/schema_pipeline_routes.py`

**Problem**: `/stage2` endpoint hatte ImportError:
```python
from execution_history.tracker import NoOpTracker  # ❌ NoOpTracker nicht in diesem Modul!
```

**Solution**: `NoOpTracker` ist lokal definiert (Zeile 31 in routes file). Import entfernt, lokale Klasse verwendet.

**3 Locations Fixed**:
- **Line 225**: `execute_stage2_with_optimization()` function
- **Line 548**: stage3-4 output pipeline handler
- **Line 731**: main `execute_pipeline()` function

**Change**:
```python
# BEFORE (broken):
from execution_history.tracker import NoOpTracker
tracker = NoOpTracker()

# AFTER (fixed):
# Use locally-defined NoOpTracker class (defined at top of file)
tracker = NoOpTracker()
```

**Result**: ✅ `/stage2` endpoint NOW WORKS!

**Test Result**:
```bash
curl -X POST "http://localhost:17802/api/schema/pipeline/stage2" -d '{...}'
# Returns:
{
  "success": true,
  "stage2_result": "Titanische Bergkolosse aus schier endlosem...",  # German output (correct!)
  "run_id": "uuid",
  "execution_time_ms": 14285
}
```

---

### Frontend Fixes (Youth Flow)

**File**: `public/ai4artsed-frontend/src/views/Phase2YouthFlowView.vue`

#### Fix 1: Endpoint Migration (Line 395)
```typescript
// BEFORE:
axios.post('http://localhost:17802/api/schema/pipeline/transform', {...})

// AFTER:
axios.post('http://localhost:17802/api/schema/pipeline/stage2', {...})
```

**Reason**: `/transform` deprecated and removed. Must use `/stage2`.

---

#### Fix 2: Response Field (Line 406)
```typescript
// BEFORE:
interceptionResult.value = response.data.transformed_prompt || ''

// AFTER:
interceptionResult.value = response.data.stage2_result || ''
```

**Reason**: `/stage2` returns `stage2_result` field, not `transformed_prompt`.

---

#### Fix 3: Dynamic Schema Routing (Lines 396, 453)
```typescript
// BEFORE:
schema: 'overdrive',  // Hardcoded!

// AFTER:
schema: pipelineStore.selectedConfig?.pipeline || 'overdrive',
```

**Applied to**:
- `runInterception()` - Line 396
- `executePipeline()` - Line 453

**Reason**: User selects 'dada' or 'bauhaus' in Phase1, but Youth Flow ignored it.

---

#### Fix 4: Context Loading in onMounted (Lines 352-356)
```typescript
// ADDED:
await pipelineStore.loadMetaPromptForLanguage('de')
console.log('[Youth Flow] Meta-prompt loaded:', pipelineStore.metaPrompt?.substring(0, 50))
contextPrompt.value = pipelineStore.metaPrompt || ''
```

**Reason**: Context needs to load from Phase1 config selection.

---

#### Fix 5: RAM-Proxy Context Editing System

**Template** (Line 31):
```vue
<textarea
  v-model="contextPrompt"
  @input="handleContextPromptEdit"  <!-- ADDED -->
/>
```

**Handler** (Lines 503-506):
```typescript
function handleContextPromptEdit() {
  pipelineStore.updateMetaPrompt(contextPrompt.value)
  console.log('[Youth Flow] Context prompt edited:', contextPrompt.value.substring(0, 50) + '...')
}
```

**Watcher** (Lines 508-514):
```typescript
watch(() => pipelineStore.metaPrompt, (newMetaPrompt) => {
  if (newMetaPrompt !== contextPrompt.value) {
    contextPrompt.value = newMetaPrompt || ''
    console.log('[Youth Flow] Meta-prompt synced from store')
  }
})
```

**Import** (Line 182):
```typescript
import { ref, computed, nextTick, onMounted, watch } from 'vue'  // Added 'watch'
```

---

## ❌ Was NICHT funktioniert (404 Bug)

### Problem: 404 nach Wahl von SD 3.5

**User Report**: "404 nach Wahl von SD3.5"

**Flow**:
1. User navigiert zu Youth Flow
2. Wählt Category "Bild"
3. Klickt auf SD 3.5 config
4. ❌ 404 Error

**Mögliche Ursachen**:

#### Hypothese 1: setConfig() schlägt fehl
```typescript
// In selectConfig():
selectedConfig.value = configId  // Local state: 'sd35_large'
await runInterception()

// In runInterception():
schema: pipelineStore.selectedConfig?.pipeline || 'overdrive'
```

**Problem**: `pipelineStore.selectedConfig` könnte null sein wenn `setConfig()` in onMounted fehlschlägt.

**Check needed**: Prüfen ob `setConfig('sd35_large')` die config lädt.

---

#### Hypothese 2: Frontend Vite Proxy Problem

Youth Flow verwendet:
```typescript
axios.post('http://localhost:17802/api/schema/pipeline/stage2', {...})
```

**Problem**: Hardcoded URL bypassed Vite proxy!

**Korrekt wäre** (siehe Kids Flow):
```typescript
axios.post('/api/schema/pipeline/stage2', {...})  // Relative URL → Vite proxy
```

**Vite Proxy Config** (vite.config.ts):
```typescript
proxy: {
  '/api': {
    target: 'http://localhost:17802',
    changeOrigin: true
  }
}
```

---

#### Hypothese 3: API Service Layer nicht verwendet

**Session 65 Plan empfahl**:
```typescript
// Use API service instead of raw axios
import { transformPrompt } from '@/services/api'

const response = await transformPrompt(requestData)
```

**Aktuell**: Raw axios mit hardcoded URL.

**Check needed**: Gibt es eine `/stage2` Funktion in `@/services/api.ts`?

---

## 🔍 Debug Steps für nächste Session

### 1. Browser Console prüfen
```
Network Tab → Failed Request → Response
→ Was ist der genaue 404 Error?
→ Welche URL wurde aufgerufen?
```

### 2. Backend Logs prüfen
```bash
# Check terminal window mit ./3_start_backend_dev.sh
# Suchen nach:
[STAGE2-ENDPOINT] Starting Stage 2 for schema '...'
# Oder error logs
```

### 3. Test Config Loading
```javascript
// In Browser Console:
const store = usePipelineExecutionStore()
await store.setConfig('sd35_large')
console.log(store.selectedConfig)  // Should NOT be null
```

---

## 🎯 Empfohlene Fixes für nächste Session

### Option A: Use Vite Proxy (Recommended)

**Change runInterception()**:
```typescript
// FROM:
axios.post('http://localhost:17802/api/schema/pipeline/stage2', {...})

// TO:
axios.post('/api/schema/pipeline/stage2', {...})  // Relative URL
```

**Same for executePipeline()**.

**Reason**:
- Vite proxy handles dev/prod URLs
- Consistent with Kids Flow
- No CORS issues

---

### Option B: Use API Service Layer

**1. Check if service exists**:
```bash
grep -n "stage2" public/ai4artsed-frontend/src/services/api.ts
```

**2. If exists, use it**:
```typescript
import { callStage2 } from '@/services/api'  // Example name

const response = await callStage2({
  schema: pipelineStore.selectedConfig?.pipeline || 'overdrive',
  input_text: inputText.value,
  // ...
})
```

**3. If not exists, create it**:
```typescript
// In api.ts:
export async function callStage2(data: any) {
  return apiClient.post('/api/schema/pipeline/stage2', data)
}
```

---

### Option C: Add Config Loading to selectConfig

**Current** (reverted):
```typescript
async function selectConfig(configId: string) {
  selectedConfig.value = configId
  await runInterception()
}
```

**Try adding** (was reverted because caused issues):
```typescript
async function selectConfig(configId: string) {
  selectedConfig.value = configId

  // Ensure config is loaded into store
  await pipelineStore.setConfig(configId)

  await runInterception()
}
```

**Reason**: `pipelineStore.selectedConfig?.pipeline` needs the config to be loaded.

**Question**: Why did this cause problems? Need to investigate.

---

## 📚 Reference Files

### Working Reference (Kids Flow):
`public/ai4artsed-frontend/src/views/Phase2CreativeFlowView.vue`

**Check**:
- How does Kids Flow call Stage 2?
- Does it use Vite proxy or hardcoded URL?
- How does it load configs?

### API Service:
`public/ai4artsed-frontend/src/services/api.ts`

**Check**:
- Is there a function for `/stage2`?
- What's the pattern for type-safe API calls?

### Store:
`public/ai4artsed-frontend/src/stores/pipelineExecution.ts`

**Check**:
- Does `setConfig()` work properly?
- What does it return?
- Does it handle errors?

---

## 📊 Session 66 Summary

### Backend Changes:
- ✅ Fixed 3 NoOpTracker import errors
- ✅ `/stage2` endpoint now works
- ✅ `/transform` endpoint removed (intentionally)

### Frontend Changes (Youth Flow):
- ✅ Migrated from `/transform` → `/stage2`
- ✅ Response field: `transformed_prompt` → `stage2_result`
- ✅ Dynamic schema: `'overdrive'` → `pipelineStore.selectedConfig?.pipeline`
- ✅ Context loading: Added `loadMetaPromptForLanguage('de')` in onMounted
- ✅ RAM-Proxy: Added context edit handler + watcher
- ✅ Import: Added `watch` to Vue imports
- ❌ 404 Error: Still present when selecting SD 3.5

### Files Modified:
1. `devserver/my_app/routes/schema_pipeline_routes.py` (3 locations)
2. `public/ai4artsed-frontend/src/views/Phase2YouthFlowView.vue` (8 locations)

---

## 🚨 Critical Issue for Next Session

**404 Error persists after config selection**

**Must investigate**:
1. Why does selecting SD 3.5 cause 404?
2. Is the URL correct (`/api/...` vs `http://localhost:17802/api/...`)?
3. Does `pipelineStore.selectedConfig` load properly?
4. Compare with Kids Flow implementation

**Likely culprit**: Hardcoded `http://localhost:17802` URLs bypassing Vite proxy.

**Recommended action**: Change to relative URLs (`/api/schema/pipeline/stage2`) to use Vite proxy.

---

## 🎯 Next Session Action Plan

1. **Debug 404**:
   - Check browser Network tab for exact failing URL
   - Check backend logs for request arrival
   - Verify Vite proxy is working

2. **Compare with Kids Flow**:
   - Read Phase2CreativeFlowView.vue
   - Check how it calls Stage 2
   - Check URL patterns (relative vs absolute)

3. **Fix URL to use Vite proxy**:
   - Change: `http://localhost:17802/api/...` → `/api/...`
   - Apply to both `runInterception()` and `executePipeline()`

4. **Test end-to-end**:
   - Navigate to `/youth-flow/dada`
   - Select SD 3.5
   - Verify interception works
   - Verify full pipeline works

---

**Session 66 Complete - Ready for Fresh Session**
**Next Session**: Fix 404 error (likely Vite proxy issue)
