# TODO: Auto-Media-Generation Debugging

## Problem
Auto-Media-Generation für Schema-Pipelines funktioniert noch nicht vollständig.

**Symptome**:
- Backend queued Image-Generation erfolgreich (Logs zeigen prompt_id)
- Frontend soll für Completion pollen, aber zeigt Bild nicht an

## Backend-Status
✅ **Funktioniert**:
- `detect_output_type()` - Erkennt "image" korrekt
- `generate_image_from_text()` - Generiert Workflow, submitted zu ComfyUI
- Auto-Post-Processing triggert nach Pipeline-Completion
- Server-Logs zeigen: `[AUTO-MEDIA] Image generation queued: {prompt_id}`

## Frontend-Status
❓ **Zu debuggen**:
- `displaySchemaPipelineResult()` soll `startFastPolling()` aufrufen
- Polling soll auf ComfyUI-Completion warten
- Image soll nach Completion angezeigt werden

## Debug-Schritte

1. **Browser Console checken**:
   ```javascript
   // Nach Schema-Pipeline-Completion:
   console.log("[AUTO-MEDIA] Starting polling for...");
   ```
   - Wird diese Nachricht angezeigt?
   - Wird `startFastPolling()` aufgerufen?

2. **Network Tab checken**:
   - Werden `/workflow-status-poll/{prompt_id}` Requests gesendet?
   - Response: `{"status": "processing"}` oder `{"status": "completed"}`?

3. **Media-Output checken**:
   - Wird `processAndDisplayResults()` aufgerufen nach Completion?
   - Werden Bilder korrekt aus ComfyUI geholt?

## Mögliche Ursachen

### Hypothese 1: Polling wird nicht gestartet
**Check**: `workflow-streaming.js` Line ~380
```javascript
if (result.media && result.media.prompt_id) {
    console.log(`[AUTO-MEDIA] Starting polling...`);
    startFastPolling(result.media.prompt_id);
}
```
**Fix**: Console-Log hinzufügen, verifizieren dass Code erreicht wird

### Hypothese 2: Polling endpoint fehlt
**Check**: Gibt es `/workflow-status-poll/{prompt_id}` Route?
**Wahrscheinlich**: Muss `/workflow-status/{prompt_id}` sein statt `-poll`

### Hypothese 3: Display-Function fehlt
**Check**: `startFastPolling()` ruft nach Completion korrekt auf
**Erwartung**: Sollte `processAndDisplayResults()` oder `mediaOutputManager.display()` aufrufen

## Test-Plan

1. Schema-Pipeline starten: `dev/TEST_dadaismus`
2. Browser DevTools öffnen (Console + Network)
3. Prompt senden: "Ein Kamel fliegt über den Schwarzwald"
4. Logs beobachten:
   - Server: `[AUTO-MEDIA] Image generation queued: ...`
   - Browser: `[AUTO-MEDIA] Starting polling for...`
   - Network: GET requests zu `/workflow-status/...`
5. Nach ~25s: Bild sollte erscheinen

## Quick-Fix Vorschlag

Falls Polling nicht startet, einfacher Fallback:
```javascript
// In displaySchemaPipelineResult():
if (result.media && result.media.prompt_id) {
    // Update UI mit "Bild wird generiert..."
    setStatus(`Bild wird generiert...`, 'success');
    
    // Start polling wie bei Legacy-Workflows
    updateSessionData({
        promptId: result.media.prompt_id,
        workflowName: `schema_${result.schema_name}`,
        prompt: result.original_prompt
    });
    
    startFastPolling(result.media.prompt_id);
    return; // Don't stopProcessingDisplay yet!
}
```

## Priorität
**Medium** - Feature ist implementiert, aber debugging needed
- Nicht kritisch für Core-Functionality
- Kann später gefixt werden
- Workaround: Manueller Refresh nach ~30s

## Estimated Debug Time
1-2 Stunden mit Browser DevTools und Server-Logs
