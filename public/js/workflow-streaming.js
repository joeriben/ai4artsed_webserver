// AI4ArtsEd - Streaming Workflow Module
// Alternative implementation using Server-Sent Events to prevent Cloudflare timeouts

import { ui } from './ui-elements.js';
import { config } from './config.js';
import { uploadedImageData } from './image-handler.js';
import { setStatus, startProcessingDisplay, stopProcessingDisplay, clearOutputDisplays } from './ui-utils.js';
import { processAndDisplayResults } from './output-display.js';
import { currentSessionData, updateSessionData } from './session.js';

let eventSource = null;

export async function submitPromptWithStreaming() {
    if (ui.submitBtn.disabled) return;
    
    clearOutputDisplays();
    
    // Don't overwrite promptDisplay if it was already set by image analysis
    const isImageAnalysis = uploadedImageData !== null;
    if (!isImageAnalysis) {
        ui.promptDisplayText.textContent = ui.prompt.value;
        ui.promptDisplay.style.display = 'block';
    }
    
    startProcessingDisplay("Generierung...");

    const workflowName = ui.workflow.value;
    const promptText = ui.prompt.value.trim();
    const aspectRatio = ui.aspectRatio.value;
    const executionMode = document.querySelector('input[name="execution-mode"]:checked').value;
    const safetyLevel = document.querySelector('input[name="safety-level"]:checked').value;

    if (!workflowName) {
        setStatus('Bitte wählen Sie einen Workflow aus.', 'warning');
        stopProcessingDisplay();
        return;
    }
    if (!promptText) {
        setStatus('Prompt darf nicht leer sein.', 'warning');
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
        prompt: promptText, 
        workflow: workflowName, 
        aspectRatio: aspectRatio, 
        mode: executionMode,
        seedMode: seedMode,
        customSeed: customSeed,
        safetyLevel: safetyLevel
    };

    try {
        // Close any existing event source
        if (eventSource) {
            eventSource.close();
        }

        // First submit the workflow normally to get initial data
        const response = await fetch('/run_workflow_stream', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) {
            const result = await response.json();
            throw new Error(result.reason || result.error || 'Unbekannter Server-Fehler');
        }

        // Set up EventSource for streaming updates
        eventSource = new EventSource(`/run_workflow_stream`);
        
        eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                
                switch (data.status) {
                    case 'starting':
                    case 'processing':
                        // Update processing message
                        if (data.message) {
                            ui.processingMessage.textContent = data.message;
                        }
                        // Show keep-alive indicator
                        if (data.keepAlive) {
                            const dots = '.'.repeat((data.keepAlive % 4) + 1);
                            ui.processingMessage.textContent = data.message + dots;
                        }
                        break;
                        
                    case 'completed':
                        eventSource.close();
                        eventSource = null;
                        
                        const result = data.result;
                        
                        // Handle prompt display
                        if (isImageAnalysis && ui.promptDisplayText.textContent) {
                            // Keep image analysis text
                        } else if (result.translated_prompt) {
                            ui.promptDisplayText.textContent = result.translated_prompt;
                        } else {
                            ui.promptDisplayText.textContent = promptText;
                        }
                        ui.promptDisplay.style.display = 'block';
                        
                        // Update session data
                        updateSessionData({
                            promptId: result.prompt_id,
                            workflowName: workflowName,
                            prompt: promptText
                        });
                        
                        // Save used seed if returned
                        if (result.used_seed) {
                            localStorage.setItem('lastUsedSeed', result.used_seed.toString());
                            document.getElementById('last-seed-value').textContent = result.used_seed;
                        }
                        
                        // Display results
                        if (result.outputs) {
                            processAndDisplayResults(result.outputs, result.workflow_def || {});
                        }
                        break;
                        
                    case 'error':
                        eventSource.close();
                        eventSource = null;
                        throw new Error(data.error || 'Workflow-Fehler');
                        
                    case 'timeout':
                        eventSource.close();
                        eventSource = null;
                        setStatus('Timeout: Der Workflow dauert zu lange.', 'warning');
                        stopProcessingDisplay();
                        break;
                }
            } catch (e) {
                console.error('Error processing stream data:', e);
            }
        };
        
        eventSource.onerror = (error) => {
            console.error('EventSource error:', error);
            eventSource.close();
            eventSource = null;
            setStatus('Verbindungsfehler. Bitte versuchen Sie es erneut.', 'error');
            stopProcessingDisplay();
        };
        
    } catch (e) {
        setStatus(`Error: ${e.message}`, 'error');
        stopProcessingDisplay();
        if (eventSource) {
            eventSource.close();
            eventSource = null;
        }
    }
}

// Alternative: Fast polling approach for environments where SSE doesn't work well
export async function submitPromptWithFastPolling() {
    if (ui.submitBtn.disabled) return;
    
    clearOutputDisplays();
    
    const isImageAnalysis = uploadedImageData !== null;
    if (!isImageAnalysis) {
        ui.promptDisplayText.textContent = ui.prompt.value;
        ui.promptDisplay.style.display = 'block';
    }
    
    startProcessingDisplay("Generierung...");

    const workflowName = ui.workflow.value;
    const promptText = ui.prompt.value.trim();
    const aspectRatio = ui.aspectRatio.value;
    const executionMode = document.querySelector('input[name="execution-mode"]:checked').value;
    const safetyLevel = document.querySelector('input[name="safety-level"]:checked').value;

    if (!workflowName) {
        setStatus('Bitte wählen Sie einen Workflow aus.', 'warning');
        stopProcessingDisplay();
        return;
    }
    if (!promptText) {
        setStatus('Prompt darf nicht leer sein.', 'warning');
        stopProcessingDisplay();
        return;
    }

    const seedMode = document.querySelector('input[name="seed-mode"]:checked').value;
    let customSeed = null;
    
    if (seedMode === 'fixed') {
        const lastSeed = localStorage.getItem('lastUsedSeed');
        if (lastSeed) {
            customSeed = parseInt(lastSeed);
        }
    }

    const payload = { 
        prompt: promptText, 
        workflow: workflowName, 
        aspectRatio: aspectRatio, 
        mode: executionMode,
        seedMode: seedMode,
        customSeed: customSeed,
        safetyLevel: safetyLevel
    };

    try {
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
        
        // Update UI
        if (isImageAnalysis && ui.promptDisplayText.textContent) {
            // Keep image analysis text
        } else if (result.translated_prompt) {
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
