# Youth Flow Context Integration - Session Handover

**Datum**: 2025-11-22
**Status**: 🟡 TEILWEISE IMPLEMENTIERT - Benötigt Fixes
**Backup**: `/tmp/Phase2YouthFlowView_backup_20251122_202732.vue`

---

## 🎯 Ursprüngliches Ziel

**User Request**: "der context müsste dann auch übernommen werden (vgl. alte Phase2-Code)"

Youth Flow (Phase2YouthFlowView.vue) soll:
1. Context/Meta-Prompt aus Phase1-Configs laden und anzeigen
2. Genau wie Kids Phase2 (Phase2CreativeFlowView.vue) es macht
3. Context in "Regeln"-Textarea anzeigen

---

## ✅ Was KORREKT implementiert wurde

### 1. Store Integration
```typescript
// Imports (Zeile 181-184)
import { watch } from 'vue'
import { usePipelineExecutionStore } from '@/stores/pipelineExecution'
import { useUserPreferencesStore } from '@/stores/userPreferences'

// Store Instances (Zeile 334-335)
const pipelineStore = usePipelineExecutionStore()
const userPreferences = useUserPreferencesStore()
```

### 2. OnMounted Context Loading
```typescript
// Zeilen 343-368
onMounted(async () => {
  const configId = route.params.configId as string

  if (configId) {
    // STEP 1: Load config
    await pipelineStore.setConfig(configId)

    // STEP 2: Load meta-prompt for language
    await pipelineStore.loadMetaPromptForLanguage(userPreferences.language)

    // STEP 3: Initialize contextPrompt
    contextPrompt.value = pipelineStore.metaPrompt || ''

    // STEP 4: Auto-select category + config
    // ... (category finding logic)
  }
})
```

### 3. Context Editing Handler
```typescript
// Template (Zeile 31)
<textarea v-model="contextPrompt" @input="handleContextPromptEdit" />

// Handler (Zeile 538-541)
function handleContextPromptEdit() {
  pipelineStore.updateMetaPrompt(contextPrompt.value)
  console.log('[Youth Flow] Context prompt edited:', contextPrompt.value.substring(0, 50) + '...')
}

// Watcher (Zeile 544-550)
watch(() => pipelineStore.metaPrompt, (newMetaPrompt) => {
  if (newMetaPrompt !== contextPrompt.value) {
    contextPrompt.value = newMetaPrompt || ''
    console.log('[Youth Flow] Meta-prompt synced from store')
  }
})
```

### 4. Korrekte API Endpoints

**Architecture Agent bestätigt**:
- ✅ `/api/schema/pipeline/stage2` für Interception (NICHT deprecated `/transform`)
- ✅ Response-Feld: `stage2_result` (NICHT `transformed_prompt`)

```typescript
// RunInterception (Zeile 437)
const response = await axios.post('http://localhost:17802/api/schema/pipeline/stage2', requestData)

if (response.data.success) {
  interceptionResult.value = response.data.stage2_result || ''
}
```

### 5. Dynamisches Schema (NICHT hardcoded 'overdrive')
```typescript
// Zeile 421 in runInterception()
schema: pipelineStore.selectedConfig?.pipeline || 'overdrive'

// Zeile 476 in executePipeline()
schema: pipelineStore.selectedConfig?.pipeline || 'overdrive'
```

**User-Bestätigung**: "overdrive war Provisorium" - ✅ Korrekt gefixt!

### 6. Conditional Context Sending (RAM-Proxy System)
```typescript
// Zeile 430-434 in runInterception()
if (pipelineStore.metaPromptModified) {
  requestData.context_prompt = pipelineStore.metaPrompt
  requestData.context_language = userPreferences.language
  console.log('[Youth Flow] Passing edited context to backend (RAM-Proxy)')
}
```

---

## ❌ Was FALSCH/PROBLEMATISCH ist

### 1. Conditional Interception Call
```typescript
// Zeile 413-415 - PROBLEMATISCH
if (inputText.value) {
  await runInterception()
}
```

**Problem**: Interception wird nur aufgerufen wenn `inputText` bereits vorhanden ist.
**Lösung unklar**: Sollte es immer aufgerufen werden? Oder anders getriggert?

### 2. User-Feedback: "Start-Button sofort aktiv"
**User sagt**: Start-Button wird sofort aktiv (sollte nicht sein)
**Ursache**: Unclear - `canStartPipeline` erfordert `interceptionResult`, sollte also nicht sofort aktiv sein

### 3. User-Feedback: "Prompt interception ist immer noch überbrückt"
**User sagt**: Interception ist bypassed
**Mögliche Ursache**: Conditional call in Zeile 413?

---

## 🔧 Was noch zu tun ist

### Option A: Vollständiges Rollback + Neustart
```bash
git checkout -- public/ai4artsed-frontend/src/views/Phase2YouthFlowView.vue
```
Dann neu implementieren mit klarem Plan.

### Option B: Nur Probleme fixen
1. `if (inputText.value)` Condition entfernen (Zeile 413)
2. Interception-Trigger anders lösen (z.B. watcher auf `inputText` + `selectedConfig`)
3. Testen warum Start-Button sofort aktiv wird

---

## 📚 Wichtige Referenzen

### Korrekte Endpoints (Architecture Agent):
- **Interception**: `/api/schema/pipeline/stage2` (NICHT `/transform` - deprecated!)
- **Execution**: `/api/schema/pipeline/execute`

### Request Format für /stage2:
```typescript
{
  "schema": pipelineStore.selectedConfig?.pipeline,  // z.B. "dada", "bauhaus"
  "input_text": "...",
  "user_language": "de",
  "execution_mode": "eco",
  "safety_level": "youth",
  "output_config": "sd35_large",  // Wichtig für media optimization!
  "context_prompt": "...",  // Optional, nur wenn user edited
  "context_language": "de"  // Optional, nur wenn user edited
}
```

### Response Format:
```typescript
{
  "success": true,
  "stage2_result": "...",  // Das transformed prompt (auf DEUTSCH!)
  "run_id": "...",
  "execution_time_ms": 1234
}
```

---

## 🚨 User-Probleme die auftraten

1. **"bauhaus wurde übernommen"** → War weil `schema: 'overdrive'` hardcoded war ✅ GEFIXT
2. **"intercepted prompt ist auf englisch"** → Deprecated `/transform` endpoint ✅ GEFIXT zu `/stage2`
3. **"transform ist deprecated"** → ✅ GEFIXT zu `/stage2`
4. **"404 bei Modellwahl"** → `pipelineStore.selectedConfig` war null ✅ GEFIXT mit `setConfig()` call
5. **"Start-Button sofort aktiv"** → ❌ NOCH OFFEN
6. **"prompt interception ist überbrückt"** → ❌ NOCH OFFEN

---

## 🎯 Nächste Schritte

### Entscheidung benötigt:
**User muss wählen**:
- A) Vollständiges Rollback + sauberer Neustart
- B) Nur die verbleibenden Probleme (#5, #6) fixen

### Bei Option B - Zu fixen:
1. **Interception Call Logik**: Wann genau soll `runInterception()` getriggert werden?
   - Option 1: Immer wenn Config gewählt wird (auch ohne Input)
   - Option 2: Nur wenn Input + Config beide vorhanden
   - Option 3: Mit dediziertem Button/Trigger

2. **Start-Button Problem**: Warum ist er sofort aktiv?
   - Debug: Console logs prüfen
   - Check: Sind alle Conditions (input, config, interception) erfüllt?

---

## 📝 Vollständige Änderungsliste

### Template:
- Zeile 31: `@input="handleContextPromptEdit"` hinzugefügt

### Script Setup - Imports:
- Zeile 181: `watch` import hinzugefügt
- Zeile 184: `useUserPreferencesStore` import hinzugefügt
- Zeile 335: `userPreferences` Store-Instanz hinzugefügt

### OnMounted (Zeilen 343-386):
- Config loading mit `pipelineStore.setConfig()`
- Meta-prompt loading mit `loadMetaPromptForLanguage()`
- Error handling hinzugefügt
- Console logs hinzugefügt

### SelectConfig (Zeilen 400-416):
- `pipelineStore.setConfig(configId)` hinzugefügt
- `loadMetaPromptForLanguage()` hinzugefügt
- Context initialization hinzugefügt
- **PROBLEMATISCH**: `if (inputText.value) { await runInterception() }`

### RunInterception (Zeilen 418-450):
- **Endpoint**: `/stage2` statt `/transform`
- **Schema**: `pipelineStore.selectedConfig?.pipeline` statt `'overdrive'`
- **Language**: `userPreferences.language` statt hardcoded `'de'`
- **Response**: `stage2_result` statt `transformed_prompt`
- Conditional context sending mit `metaPromptModified`

### ExecutePipeline (Zeilen 474-504):
- **Schema**: `pipelineStore.selectedConfig?.pipeline` statt `'overdrive'`
- Conditional context sending mit `metaPromptModified`
- `user_language` bleibt hardcoded `'de'` (OK für Youth Flow)

### Neue Functions (Zeilen 538-550):
- `handleContextPromptEdit()` - Store update bei Context-Editing
- Watcher für `pipelineStore.metaPrompt` - Store-Sync

---

## 🔍 Debugging Tipps

### Browser Console prüfen:
```
[Youth Flow] Received configId from Phase1: ...
[Youth Flow] Loading config...
[Youth Flow] Loading meta-prompt for language: de
[Youth Flow] Meta-prompt loaded: ...
[Youth Flow] Context prompt edited: ...
[Youth Flow] Passing edited context to backend (RAM-Proxy)
```

### Backend Logs prüfen:
```
[DEPRECATED] /pipeline/transform endpoint called - use /pipeline/stage2 instead!
```
Wenn diese Warnung erscheint → `/transform` wird noch verwendet!

### Test-Request:
```bash
curl -X POST "http://localhost:17802/api/schema/pipeline/stage2" \
  -H "Content-Type: application/json" \
  -d '{
    "schema": "dada",
    "input_text": "Ein Bild mit Blumen",
    "user_language": "de",
    "execution_mode": "eco",
    "safety_level": "youth",
    "output_config": "sd35_large"
  }'
```

---

**Ende Handover - Bereit für /clear + Neustart**
