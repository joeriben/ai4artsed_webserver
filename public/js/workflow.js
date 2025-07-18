// AI4ArtsEd - Workflow Module
import { ui } from './ui-elements.js';
import { config } from './config.js';
import { uploadedImageData } from './image-handler.js';
import { setStatus, startProcessingDisplay, stopProcessingDisplay, clearOutputDisplays } from './ui-utils.js';
import { processAndDisplayResults } from './output-display.js';
import { currentSessionData, updateSessionData } from './session.js';

let pollingInterval = null;
let workflowMetadata = null;
let currentLanguage = 'de'; // Default to German

// Initialize seed control
document.addEventListener('DOMContentLoaded', () => {
    initializeSeedControl();
    initializeLanguageSelector();
    detectLanguage();
});

function detectLanguage() {
    // Check localStorage first
    const savedLang = localStorage.getItem('selectedLanguage');
    if (savedLang) {
        currentLanguage = savedLang;
    } else {
        // Detect browser language
        const browserLang = navigator.language || navigator.userLanguage;
        currentLanguage = browserLang.startsWith('de') ? 'de' : 'en';
    }
    
    // Update active language button
    updateLanguageButtons();
}

function initializeLanguageSelector() {
    const langButtons = document.querySelectorAll('.lang-btn');
    langButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const newLang = e.target.dataset.lang;
            if (newLang !== currentLanguage) {
                currentLanguage = newLang;
                localStorage.setItem('selectedLanguage', newLang);
                updateLanguageButtons();
                loadWorkflows(); // Reload workflows with new language
                updateWorkflowDescription(); // Update description if workflow selected
            }
        });
    });
}

function updateLanguageButtons() {
    const langButtons = document.querySelectorAll('.lang-btn');
    langButtons.forEach(btn => {
        if (btn.dataset.lang === currentLanguage) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
}

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
        // Fetch metadata first
        const metaResponse = await fetch('/workflow_metadata');
        if (metaResponse.ok) {
            workflowMetadata = await metaResponse.json();
        }
        
        // Then fetch workflows list
        const response = await fetch('/list_workflows');
        if (response.ok) {
            const result = await response.json();
            const workflows = result.workflows || [];
            
            // Build dropdown with categories
            let optionsHtml = '';
            
            // Get localized UI text
            const selectText = workflowMetadata?.ui?.selectWorkflow?.[currentLanguage] || 
                              workflowMetadata?.ui?.selectWorkflow?.['de'] || 
                              '-- Workflow auswählen --';
            
            optionsHtml += `<option value="">${selectText}</option>`;
            
            // Group workflows by category
            const workflowsByCategory = {};
            const uncategorized = [];
            
            workflows.forEach(filename => {
                // Extract category from path (e.g., "aesthetics/workflow.json" -> "aesthetics")
                const pathParts = filename.split('/');
                let category = null;
                let workflowId = null;
                
                if (pathParts.length > 1) {
                    // Has category folder
                    category = pathParts[0];
                    workflowId = pathParts[pathParts.length - 1].replace('.json', '');
                } else {
                    // No category folder
                    workflowId = filename.replace('.json', '');
                }
                
                const metadata = workflowMetadata?.workflows?.[workflowId];
                
                if (category && workflowMetadata?.categories?.[category]) {
                    if (!workflowsByCategory[category]) {
                        workflowsByCategory[category] = [];
                    }
                    workflowsByCategory[category].push({filename, metadata});
                } else {
                    uncategorized.push({filename, metadata: metadata || null});
                }
            });
            
            // Add categorized workflows
            Object.keys(workflowsByCategory).sort().forEach(category => {
                const categoryName = workflowMetadata.categories[category][currentLanguage] || 
                                   workflowMetadata.categories[category]['de'] || 
                                   category;
                
                optionsHtml += `<optgroup label="${categoryName}">`;
                
                workflowsByCategory[category].forEach(({filename, metadata}) => {
                    const displayName = metadata?.name?.[currentLanguage] || 
                                      metadata?.name?.['de'] || 
                                      filename.replace('.json', '')
                                              .replace(/^ai4artsed_/, '')
                                              .replace(/_\d+$/, '')
                                              .replace(/_/g, ' ');
                    
                    optionsHtml += `<option value="${filename}">${displayName}</option>`;
                });
                
                optionsHtml += '</optgroup>';
            });
            
            // Add uncategorized workflows
            if (uncategorized.length > 0) {
                const otherText = workflowMetadata?.ui?.noCategory?.[currentLanguage] || 
                                workflowMetadata?.ui?.noCategory?.['de'] || 
                                'Andere';
                                
                optionsHtml += `<optgroup label="${otherText}">`;
                
                uncategorized.forEach(({filename}) => {
                    const displayName = filename.replace('.json', '')
                                              .replace(/^ai4artsed_/, '')
                                              .replace(/_\d+$/, '')
                                              .replace(/_/g, ' ');
                    optionsHtml += `<option value="${filename}">${displayName}</option>`;
                });
                
                optionsHtml += '</optgroup>';
            }
            
            ui.workflow.innerHTML = optionsHtml;
            
            // Add event listener for workflow selection
            ui.workflow.addEventListener('change', () => {
                checkWorkflowSafetyNode();
                updateWorkflowDescription();
            });
        }
    } catch (error) {
        console.error('Failed to load workflows:', error);
    }
}

function updateWorkflowDescription() {
    const workflowName = ui.workflow.value;
    
    // Remove any existing description
    const existingDesc = document.getElementById('workflow-description');
    if (existingDesc) {
        existingDesc.remove();
    }
    
    if (!workflowName || !workflowMetadata) return;
    
    // Extract workflow ID from path (e.g., "aesthetics/workflow.json" -> "workflow")
    const pathParts = workflowName.split('/');
    const workflowId = pathParts[pathParts.length - 1].replace('.json', '');
    
    const metadata = workflowMetadata.workflows[workflowId];
    if (!metadata?.description) return;
    
    const description = metadata.description[currentLanguage] || metadata.description['de'];
    if (!description) return;
    
    // Create and insert description element
    const descDiv = document.createElement('div');
    descDiv.id = 'workflow-description';
    descDiv.className = 'workflow-description';
    descDiv.textContent = description;
    
    // Insert after workflow select
    ui.workflow.parentElement.insertBefore(descDiv, ui.workflow.nextSibling);
}

async function checkWorkflowSafetyNode() {
    const workflowName = ui.workflow.value;
    const safetyPlusIndicator = document.getElementById('safety-plus-indicator');
    
    if (!workflowName) {
        // No workflow selected, hide Safety+ indicator
        if (safetyPlusIndicator) {
            safetyPlusIndicator.style.display = 'none';
        }
        return;
    }
    
    try {
        const response = await fetch(`/workflow_has_safety_node/${encodeURIComponent(workflowName)}`);
        if (response.ok) {
            const result = await response.json();
            // Show/hide Safety+ indicator based on whether workflow has safety node
            if (safetyPlusIndicator) {
                safetyPlusIndicator.style.display = result.has_safety_node ? 'inline' : 'none';
            }
        }
    } catch (error) {
        console.error('Failed to check workflow safety node:', error);
        if (safetyPlusIndicator) {
            safetyPlusIndicator.style.display = 'none';
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
    const selectedRadio = document.querySelector('input[name="aspectRatio"]:checked');
    const aspectRatio = selectedRadio ? selectedRadio.value : '1:1';
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
