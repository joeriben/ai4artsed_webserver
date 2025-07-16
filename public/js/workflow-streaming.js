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
    const promptText = ui.prompt.value.trim();
    const selectedRadio = document.querySelector('input[name="aspectRatio"]:checked');
    const aspectRatio = selectedRadio ? selectedRadio.value : '1:1';
    const executionMode = document.querySelector('input[name="execution-mode"]:checked').value;
    const safetyLevel = document.querySelector('input[name="safety-level"]:checked').value;

    if (!workflowName) {
        setStatus('Bitte wählen Sie einen Workflow aus.', 'warning');
        stopProcessingDisplay();
        return;
    }

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
