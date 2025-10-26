// AI4ArtsEd - Streaming Workflow Module
// Alternative implementation using Server-Sent Events to prevent Cloudflare timeouts

import { ui } from './ui-elements.js';
import { config } from './config.js';
import { uploadedImageData, performImageAnalysis } from './image-handler.js';
import { setStatus, startProcessingDisplay, stopProcessingDisplay, clearOutputDisplays } from './ui-utils.js';
import { processAndDisplayResults } from './output-display.js';
import { currentSessionData, updateSessionData } from './session.js';

let eventSource = null;

export async function submitPromptWithStreaming() {
    // For now, just redirect to the fast polling method
    // The streaming implementation can be fixed later
    return submitPromptWithFastPolling();

}

// Alternative: Fast polling approach for environments where SSE doesn't work well
export async function submitPromptWithFastPolling() {
    if (ui.submitBtn.disabled) return;

    clearOutputDisplays();
    startProcessingDisplay("Generierung...");

    const workflowName = ui.workflow.value;
    console.log('[WORKFLOW-STREAMING] Workflow name from ui.workflow.value:', workflowName);

    const promptText = ui.prompt.value.trim();
    const selectedRadio = document.querySelector('input[name="aspectRatio"]:checked');
    const aspectRatio = selectedRadio ? selectedRadio.value : '1:1';
    const executionMode = document.querySelector('input[name="execution-mode"]:checked').value;
    const safetyLevel = document.querySelector('input[name="safety-level"]:checked').value;

    /*
    // Workflow validation removed: Backend now handles all workflow selection logic.
    // - USER mode + "random": Backend selects random workflow from all available workflows
    // - USER mode + specific workflow: Backend uses the selected workflow  
    // - FIXED mode: Backend always uses configured workflow (ignores frontend value)
    // - SYSTEM mode: Backend always uses random selection from defined categories
    // All modes now guarantee a valid workflow will be selected server-side, making
    // frontend validation obsolete and preventing false-positive error messages.
    if (!workflowName) {
        setStatus('Bitte wählen Sie einen Workflow aus.', 'warning');
        stopProcessingDisplay();
        return;
    }
    */

    // Determine input mode
    let inputMode = 'text_only';
    let finalPrompt = promptText;
    let sendImageData = null;
    
    // Check if this is an inpainting workflow
    const isInpaintingWorkflow = await checkIfInpaintingWorkflow(workflowName);
    
    if (isInpaintingWorkflow) {
        // Inpainting mode - requires both image and prompt
        inputMode = 'inpainting';
        if (!uploadedImageData || !promptText) {
            setStatus('Inpainting-Workflows erfordern sowohl ein Bild als auch einen Prompt.', 'warning');
            stopProcessingDisplay();
            return;
        }
        sendImageData = uploadedImageData;
        
    } else if (uploadedImageData) {
        // Standard workflow with image - perform analysis if needed
        inputMode = 'image_with_text';
        
        // Update status: Image analysis
        ui.processingMessage.textContent = 'Bild wird analysiert (ca. 60 sek.)...';
        
        // Perform image analysis as part of workflow (true = don't manage UI state)
        const analysisResult = await performImageAnalysis(true);
        if (!analysisResult) {
            setStatus('Bildanalyse fehlgeschlagen.', 'error');
            stopProcessingDisplay();
            return;
        }
        
        // Step 1: Translate user prompt first (if exists)
        let translatedUserPrompt = '';
        if (promptText) {
            ui.processingMessage.textContent = 'Prompt wird übersetzt...';
            
            // Call server to translate just the user prompt
            try {
                const translateResponse = await fetch('/validate-prompt', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: promptText })
                });
                
                if (translateResponse.ok) {
                    const translateResult = await translateResponse.json();
                    if (translateResult.success) {
                        translatedUserPrompt = translateResult.translated_prompt;
                    } else {
                        // Translation failed, use original
                        translatedUserPrompt = promptText;
                    }
                } else {
                    // Translation failed, use original
                    translatedUserPrompt = promptText;
                }
            } catch (e) {
                // Translation failed, use original
                console.error('Translation error:', e);
                translatedUserPrompt = promptText;
            }
        }
        
        // Step 2: Concatenate translated prompt with analysis
        if (translatedUserPrompt) {
            finalPrompt = `${translatedUserPrompt}. ${analysisResult}`;
        } else {
            finalPrompt = analysisResult;
        }
        
        // Display the analysis result in dedicated field
        ui.imageAnalysisText.textContent = analysisResult;
        ui.imageAnalysisDisplay.style.display = 'block';
        
    } else if (!promptText) {
        // No image and no prompt
        setStatus('Bitte geben Sie einen Prompt ein oder laden Sie ein Bild hoch.', 'warning');
        stopProcessingDisplay();
        return;
    }

    // Get seed control settings
    const seedMode = document.querySelector('input[name="seed-mode"]:checked').value;
    let customSeed = null;
    
    if (seedMode === 'fixed') {
        const lastSeed = localStorage.getItem('lastUsedSeed');
        if (lastSeed) {
            customSeed = parseInt(lastSeed);
        }
    }

    const payload = { 
        prompt: finalPrompt,
        workflow: workflowName, 
        aspectRatio: aspectRatio, 
        mode: executionMode,
        seedMode: seedMode,
        customSeed: customSeed,
        safetyLevel: safetyLevel,
        imageData: sendImageData,
        inputMode: inputMode,
        skipTranslation: inputMode === 'image_with_text'  // Skip translation for image+text as we already translated
    };

    try {
        // Update status for safety check and generation
        ui.processingMessage.textContent = 'Sicherheitsprüfung läuft...';
        
        // Submit workflow
        const response = await fetch('/run_workflow', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) {
            const result = await response.json();
            throw new Error(result.reason || result.error || 'Unbekannter Server-Fehler');
        }
        
        const result = await response.json();
        
        // CHECK: Schema-Pipeline (direkte Text-Ausgabe) vs Legacy-Workflow (ComfyUI-Polling)
        if (result.schema_pipeline && result.success) {
            // Schema-Pipeline - direkte Text-Ausgabe
            console.log('Schema-Pipeline Response:', result);
            
            // Update UI - show the translated prompt
            if (result.translated_prompt) {
                ui.promptDisplayText.textContent = result.translated_prompt;
            } else {
                ui.promptDisplayText.textContent = promptText;
            }
            ui.promptDisplay.style.display = 'block';
            
            // Schema-Pipeline-Ergebnis direkt anzeigen
            displaySchemaPipelineResult(result);
            
            updateSessionData({
                promptId: `schema_${Date.now()}`,  // Pseudo-ID für Session
                workflowName: workflowName,
                prompt: promptText,
                schemaPipeline: true
            });
            
            stopProcessingDisplay();
            return;
        }
        
        // Legacy-Workflow (ComfyUI)
        if (!result.prompt_id) throw new Error('Keine prompt_id vom Server erhalten.');
        
        // Update UI - show the translated prompt
        if (result.translated_prompt) {
            ui.promptDisplayText.textContent = result.translated_prompt;
        } else {
            ui.promptDisplayText.textContent = promptText;
        }
        ui.promptDisplay.style.display = 'block';
        
        updateSessionData({
            promptId: result.prompt_id,
            workflowName: workflowName,
            prompt: promptText
        });
        
        if (result.used_seed) {
            localStorage.setItem('lastUsedSeed', result.used_seed.toString());
            document.getElementById('last-seed-value').textContent = result.used_seed;
        }
        
        // Update status for generation
        ui.processingMessage.textContent = 'Generierung läuft...';
        
        // Start fast polling with shorter timeout
        startFastPolling(result.prompt_id);
        
    } catch (e) {
        setStatus(`Error: ${e.message}`, 'error');
        stopProcessingDisplay();
    }
}

function startFastPolling(promptId) {
    let pollAttempts = 0;
    const maxPollAttempts = 480; // 8 minutes at 1-second intervals
    let lastStatus = null;
    
    const pollInterval = setInterval(async () => {
        pollAttempts++;
        
        if (pollAttempts > maxPollAttempts) {
            clearInterval(pollInterval);
            setStatus('Timeout: Workflow dauert zu lange.', 'warning');
            stopProcessingDisplay();
            return;
        }
        
        try {
            // Use the fast polling endpoint
            const res = await fetch(`/workflow-status-poll/${promptId}`, {
                method: 'GET',
                headers: { 'Cache-Control': 'no-cache' }
            });
            
            if (!res.ok) {
                throw new Error(`HTTP ${res.status}`);
            }
            
            const data = await res.json();
            
            // Update status message periodically
            if (data.status === 'processing' && pollAttempts % 5 === 0) {
                const elapsed = Math.floor(pollAttempts);
                ui.processingMessage.textContent = `Workflow läuft... (${elapsed}s)`;
            }
            
            if (data.status === 'completed' && data.outputs) {
                clearInterval(pollInterval);
                // Fetch full history for complete data
                const historyRes = await fetch(`/${config.comfyui_proxy_prefix}/history/${promptId}`);
                if (historyRes.ok) {
                    const history = await historyRes.json();
                    if (history[promptId]?.outputs) {
                        processAndDisplayResults(history[promptId].outputs, history[promptId].prompt[2]);
                    }
                }
            }
            
            lastStatus = data.status;
            
        } catch(e) {
            // Don't stop on individual errors, just log them
            console.warn(`Fast polling error:`, e.message);
        }
    }, 1000); // Poll every second
}

// Helper function to check if workflow is inpainting type
async function checkIfInpaintingWorkflow(workflowName) {
    try {
        const response = await fetch(`/workflow-type/${encodeURIComponent(workflowName)}`);
        if (response.ok) {
            const result = await response.json();
            return result.isInpainting === true;
        }
    } catch (error) {
        console.error('Failed to check workflow type:', error);
    }
    return false;
}

// Export function to determine which method to use
export function useStreamingWorkflow() {
    // Check if EventSource is supported
    if (typeof EventSource === 'undefined') {
        console.log('EventSource not supported, using fast polling');
        return false;
    }
    
    // Check if we're in an environment known to have issues with SSE
    const userAgent = navigator.userAgent.toLowerCase();
    if (userAgent.includes('edge/') && parseInt(userAgent.split('edge/')[1]) < 79) {
        console.log('Old Edge detected, using fast polling');
        return false;
    }
    
    return true;
}

// Schema-Pipeline Result Display (Text-Outputs ohne ComfyUI)
function displaySchemaPipelineResult(result) {
    console.log('Displaying Schema Pipeline Result:', result);
    
    // Clear existing outputs
    ui.imageOutputs.style.display = 'none';
    ui.imageOutputsContent.innerHTML = '';
    ui.textOutputs.style.display = 'none';
    ui.textOutputsContent.innerHTML = '';
    
    // Remove any existing unified containers
    document.querySelectorAll('#unifiedOutputs').forEach(el => el.remove());
    
    // Create unified output container für Schema-Pipeline
    const unifiedContainer = document.createElement('div');
    unifiedContainer.id = 'unifiedOutputs';
    unifiedContainer.innerHTML = '<h4>🎯 Schema-Pipeline Ergebnis:</h4>';
    
    const contentContainer = document.createElement('div');
    contentContainer.id = 'unifiedOutputsContent';
    
    // CHECK: Media-Output (Bild/Audio/Video) oder Text?
    if (result.media && result.media.prompt_id) {
        // Auto-generated media - need to poll for completion
        console.log(`[AUTO-MEDIA] Starting polling for ${result.media.type} generation:`, result.media.prompt_id);
        
        // Show pipeline info
            const pipelineInfo = document.createElement('div');
            pipelineInfo.style.cssText = 'margin-bottom: 15px; padding: 10px; border: 1px solid #007bff; border-radius: 6px; background-color: #e3f2fd;';
            
            let backendInfoHTML = '';
            if (result.backend_info && result.backend_info.length > 0) {
                backendInfoHTML = '<div style="font-size: 0.85em; color: #666; margin-top: 5px; border-top: 1px solid #ccc; padding-top: 5px;">';
                result.backend_info.forEach(info => {
                    const backendIcon = info.backend === 'ollama' ? '🏠' : '☁️';
                    backendInfoHTML += `<div>📡 ${info.step}: ${backendIcon} ${info.backend} → ${info.model}</div>`;
                });
                backendInfoHTML += '</div>';
            }
            
            pipelineInfo.innerHTML = `
                <div style="font-weight: bold; color: #0056b3; margin-bottom: 5px;">
                    🔀 Schema: ${result.schema_name}
                </div>
                <div style="font-size: 0.9em; color: #666;">
                    ⚡ ${result.steps_completed} Schritte in ${(result.execution_time || 0).toFixed(1)}s
                </div>
                <div style="font-size: 0.9em; color: #666; margin-top: 5px;">
                    🖼️ Media-Typ: ${result.media.type}
                </div>
                ${backendInfoHTML}
            `;
        contentContainer.appendChild(pipelineInfo);
        unifiedContainer.appendChild(contentContainer);
        ui.promptDisplay.parentNode.insertBefore(unifiedContainer, ui.promptDisplay.nextSibling);
        
        // Update status and start polling for media
        setStatus(`Schema-Pipeline '${result.schema_name}' erfolgreich - ${result.media.type} wird generiert...`, 'success');
        ui.processingMessage.textContent = `${result.media.type} wird generiert (ca. 20s)...`;
        
        // Update session data with media prompt_id
        updateSessionData({
            promptId: result.media.prompt_id,
            workflowName: `schema_${result.schema_name}`,
            prompt: result.original_prompt || '',
            schemaPipeline: true
        });
        
        // Start polling for the auto-generated media
        startFastPolling(result.media.prompt_id);
        return;
    }
    
    // Pipeline-Info anzeigen
    const pipelineInfo = document.createElement('div');
    pipelineInfo.style.cssText = 'margin-bottom: 15px; padding: 10px; border: 1px solid #007bff; border-radius: 6px; background-color: #e3f2fd;';
    pipelineInfo.innerHTML = `
        <div style="font-weight: bold; color: #0056b3; margin-bottom: 5px;">
            🔀 Schema: ${result.schema_name}
        </div>
        <div style="font-size: 0.9em; color: #666;">
            ⚡ ${result.steps_completed} Schritte in ${(result.execution_time || 0).toFixed(1)}s
        </div>
    `;
    contentContainer.appendChild(pipelineInfo);
    
    // Final Output anzeigen
    const outputItem = document.createElement('div');
    outputItem.className = 'unified-output-item';
    outputItem.style.cssText = 'margin-bottom: 20px; padding: 12px; border: 1px solid #28a745; border-radius: 6px; background-color: #f8fff8;';
    
    const headerDiv = document.createElement('div');
    headerDiv.className = 'output-header';
    headerDiv.style.cssText = 'font-weight: bold; color: #155724; margin-bottom: 8px; font-size: 1.0em;';
    headerDiv.textContent = `🎨 Final Output`;
    
    const textContainer = document.createElement('div');
    textContainer.className = 'result-text-container';
    textContainer.style.cssText = 'position: relative;';
    
    const textDiv = document.createElement('div');
    textDiv.style.cssText = 'white-space: pre-wrap; word-wrap: break-word; font-family: Georgia, serif; background: white; padding: 12px; border-radius: 4px; border: 1px solid #ddd; line-height: 1.5;';
    textDiv.textContent = result.final_output || 'Kein Output verfügbar';
    
    // Add recycle button for text reuse
    const overlay = document.createElement('div');
    overlay.className = 'text-hover-overlay';
    overlay.style.cssText = `
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        opacity: 0;
        transition: opacity 0.3s ease;
        border-radius: 4px;
        cursor: pointer;
        pointer-events: none;
    `;
    
    const recycleButton = document.createElement('button');
    recycleButton.className = 'use-as-input-btn';
    recycleButton.style.cssText = `
        background: white;
        border: none;
        width: 48px;
        height: 48px;
        padding: 0;
        border-radius: 50%;
        cursor: pointer;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        transition: transform 0.2s ease;
        display: flex;
        align-items: center;
        justify-content: center;
    `;
    recycleButton.innerHTML = '<img src="icons/redo-circle.svg" alt="Als Prompt verwenden" style="width: 24px; height: 24px;">';
    recycleButton.title = 'Als Prompt verwenden';
    
    // Click handler für Text-Wiederverwendung
    recycleButton.addEventListener('click', async (e) => {
        e.stopPropagation();
        useTextAsInput(result.final_output || '');
    });
    
    // Hover effects
    textContainer.addEventListener('mouseenter', () => {
        overlay.style.opacity = '1';
        overlay.style.pointerEvents = 'auto';
        recycleButton.style.transform = 'scale(1.1)';
    });

    textContainer.addEventListener('mouseleave', () => {
        overlay.style.opacity = '0';
        overlay.style.pointerEvents = 'none';
        recycleButton.style.transform = 'scale(1)';
    });
    
    overlay.appendChild(recycleButton);
    textContainer.appendChild(textDiv);
    textContainer.appendChild(overlay);
    
    outputItem.appendChild(headerDiv);
    outputItem.appendChild(textContainer);
    contentContainer.appendChild(outputItem);
    unifiedContainer.appendChild(contentContainer);
    
    // Insert after promptDisplay
    const promptDisplay = ui.promptDisplay;
    promptDisplay.parentNode.insertBefore(unifiedContainer, promptDisplay.nextSibling);
    
    // Success status
    setStatus(`Schema-Pipeline '${result.schema_name}' erfolgreich abgeschlossen!`, 'success');
}

// Helper function for text reuse
function useTextAsInput(text) {
    try {
        ui.prompt.value = text;
        setStatus('Text als Prompt gesetzt.', 'success');
        ui.prompt.scrollIntoView({ behavior: 'smooth', block: 'center' });
        ui.prompt.focus();
    } catch (error) {
        console.error('Error using text as input:', error);
        setStatus('Fehler: Text konnte nicht als Prompt verwendet werden', 'error');
    }
}
