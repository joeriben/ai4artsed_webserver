// AI4ArtsEd - Workflow Module
import { ui } from './ui-elements.js';
import { config } from './config.js';
import { uploadedImageData } from './image-handler.js';
import { setStatus, startProcessingDisplay, stopProcessingDisplay, clearOutputDisplays } from './ui-utils.js';
import { processAndDisplayResults } from './output-display.js';
import { currentSessionData, updateSessionData } from './session.js';

let pollingInterval = null;

// Initialize seed control
document.addEventListener('DOMContentLoaded', () => {
    initializeSeedControl();
});

function initializeSeedControl() {
    const seedRadios = document.querySelectorAll('input[name="seed-mode"]');
    const seedInfo = document.getElementById('seed-info');
    const lastSeedSpan = document.getElementById('last-seed-value');
    
    // Load last seed from localStorage
    const lastSeed = localStorage.getItem('lastUsedSeed');
    if (lastSeed) {
        lastSeedSpan.textContent = lastSeed;
    }
    
    // Add event listeners to radio buttons
    seedRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            if (e.target.value === 'fixed' && lastSeed) {
                seedInfo.style.display = 'block';
            } else {
                seedInfo.style.display = 'none';
            }
        });
    });
}

export async function loadWorkflows() {
    try {
        const response = await fetch('/list_workflows');
        if (response.ok) {
            const result = await response.json();
            const workflows = result.workflows || [];
            ui.workflow.innerHTML = '<option value="">-- Workflow auswählen --</option>' + 
                workflows.map(wf => `<option value="${wf}">${wf.replace('.json', '').replace(/_/g, ' ')}</option>`).join('');
            
            // Add event listener for workflow selection
            ui.workflow.addEventListener('change', checkWorkflowSafetyNode);
        }
    } catch (error) {
        console.error('Failed to load workflows:', error);
    }
}

async function checkWorkflowSafetyNode() {
    const workflowName = ui.workflow.value;
    const safetyRadios = document.querySelectorAll('input[name="safety-level"]');
    const safetyLabels = document.querySelectorAll('input[name="safety-level"] + label');
    
    if (!workflowName) {
        // No workflow selected, disable safety controls
        setSafetyControlsEnabled(false);
        return;
    }
    
    try {
        const response = await fetch(`/workflow_has_safety_node/${encodeURIComponent(workflowName)}`);
        if (response.ok) {
            const result = await response.json();
            setSafetyControlsEnabled(result.has_safety_node);
        }
    } catch (error) {
        console.error('Failed to check workflow safety node:', error);
        setSafetyControlsEnabled(false);
    }
}

function setSafetyControlsEnabled(enabled) {
    const safetyRadios = document.querySelectorAll('input[name="safety-level"]');
    const safetyLabels = document.querySelectorAll('input[name="safety-level"] + label');
    
    // Find container by looking for the parent of the first safety radio
    const firstSafetyRadio = document.querySelector('input[name="safety-level"]');
    const safetyContainer = firstSafetyRadio ? firstSafetyRadio.closest('.mode-switch').parentElement : null;
    
    safetyRadios.forEach(radio => {
        radio.disabled = !enabled;
        if (!enabled && radio.value === 'off') {
            radio.checked = true; // Reset to "off" when disabled
        }
    });
    
    safetyLabels.forEach(label => {
        label.style.opacity = enabled ? '1' : '0.5';
        label.style.cursor = enabled ? 'pointer' : 'not-allowed';
    });
    
    // Update the container label as well
    if (safetyContainer) {
        const containerLabel = safetyContainer.querySelector('label:first-child');
        if (containerLabel && !containerLabel.hasAttribute('for')) {
            containerLabel.style.opacity = enabled ? '1' : '0.5';
        }
    }
}

export async function submitPrompt() {
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
        // Erhöhter Timeout für datenreiche Workflows (5 Minuten)
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 300000); // 5 Minuten
        
        const response = await fetch('/run_workflow', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            const result = await response.json();
            throw new Error(result.reason || result.error || 'Unbekannter Server-Fehler');
        }
        
        const result = await response.json();
        if (!result.prompt_id) throw new Error('Keine prompt_id vom Server erhalten.');
        
        if (result.status_updates && result.status_updates.length > 0) {
            let statusIndex = 0;
            const cycleStatus = () => {
                if (statusIndex < result.status_updates.length) {
                    ui.processingMessage.textContent = result.status_updates[statusIndex] + '...';
                    statusIndex++;
                    setTimeout(cycleStatus, 750);
                } else {
                    ui.processingMessage.textContent = 'Warte auf Generierungs-Engine...';
                }
            };
            cycleStatus();
        }

        // Bei Bildanalyse: Analysetext behalten (bereits gesetzt)
        if (isImageAnalysis && ui.promptDisplayText.textContent) {
            // Bildanalyse-Text ist bereits gesetzt, nichts ändern
        } else if (result.translated_prompt) {
            // Bei normalen Prompts: übersetzten Prompt anzeigen
            ui.promptDisplayText.textContent = result.translated_prompt;
        } else {
            // Fallback: ursprünglichen Prompt anzeigen
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
        
        startPollingForResult(result.prompt_id);
    } catch (e) {
        if (e.name === 'AbortError') {
            setStatus('Timeout: Der Workflow dauert zu lange. Versuchen Sie es mit einem einfacheren Prompt oder im Eco-Modus.', 'error');
        } else {
            setStatus(`Error: ${e.message}`, 'error');
        }
        stopProcessingDisplay();
    }
}

function startPollingForResult(promptId) {
    let pollAttempts = 0;
    const maxPollAttempts = 200; // 10 Minuten bei 3-Sekunden-Intervallen
    let consecutiveErrors = 0;
    const maxConsecutiveErrors = 5;
    
    pollingInterval = setInterval(async () => {
        pollAttempts++;
        
        if (pollAttempts > maxPollAttempts) {
            clearInterval(pollingInterval);
            setStatus('Timeout: Workflow dauert zu lange. Möglicherweise läuft er noch im Hintergrund.', 'warning');
            stopProcessingDisplay();
            return;
        }
        
        try {
            // Längerer Timeout für Polling-Requests
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 15000); // 15 Sekunden
            
            const res = await fetch(`/${config.comfyui_proxy_prefix}/history/${promptId}`, {
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            consecutiveErrors = 0; // Reset error counter on success
            
            if (!res.ok) {
                if (res.status === 404) {
                    // Workflow noch nicht fertig, weiter warten
                    return;
                }
                throw new Error(`HTTP ${res.status}`);
            }
            
            const history = await res.json();
            if (history[promptId]?.outputs) {
                clearInterval(pollingInterval);
                processAndDisplayResults(history[promptId].outputs, history[promptId].prompt[2]);
            }
        } catch(e) {
            consecutiveErrors++;
            console.warn(`Polling error ${consecutiveErrors}/${maxConsecutiveErrors}:`, e.message);
            
            if (consecutiveErrors >= maxConsecutiveErrors) {
                clearInterval(pollingInterval);
                if (e.name === 'AbortError') {
                    setStatus('Netzwerk-Timeout beim Abrufen der Ergebnisse. Versuchen Sie es später erneut.', 'error');
                } else {
                    setStatus(`Fehler beim Abrufen des Ergebnisses: ${e.message}`, 'error');
                }
                stopProcessingDisplay();
            }
            // Bei weniger als maxConsecutiveErrors einfach weiter versuchen
        }
    }, 3000);
}
