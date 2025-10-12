// AI4ArtsEd - Workflow Module
import { ui } from './ui-elements.js';
import { config } from './config.js';
import { uploadedImageData } from './image-handler.js';
import { setStatus, startProcessingDisplay, stopProcessingDisplay, clearOutputDisplays } from './ui-utils.js';
import { processAndDisplayResults } from './output-display.js';
import { currentSessionData, updateSessionData } from './session.js';
import { t, getCurrentLanguage } from './simple-translation.js';

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
        // Fetch workflow selection configuration first
        const configResponse = await fetch('/workflow_selection_config');
        let workflowConfig = null;
        if (configResponse.ok) {
            workflowConfig = await configResponse.json();
        }
        
        // Fetch metadata
        const metaResponse = await fetch('/workflow_metadata');
        if (metaResponse.ok) {
            workflowMetadata = await metaResponse.json();
        }
        
        // Handle different workflow selection modes
        if (workflowConfig && workflowConfig.mode !== "user") {
            handleNonUserMode(workflowConfig);
            return;
        }
        
        // DEVSERVER: Statisches Schema-Pipeline-Dropdown für Test-Zwecke
        ui.workflow.innerHTML = `
            <optgroup label="🧪 Schema-Pipeline Tests">
                <option value="dev/TEST_dadaismus">🎨 Dadaismus-Transformation</option>
                <option value="dev/jugendsprache">💬 UK Youth Slang</option>
            </optgroup>
            <optgroup label="Legacy Workflows (Auswahl)">
                <option value="aesthetics/ai4artsed_Impressionismus_2506220140.json">🖼️ Impressionismus</option>
                <option value="semantics/ai4artsed_Jugendsprache_2506122317.json">💭 Jugendsprache (Legacy)</option>
            </optgroup>
        `;
        
        // Auto-select TEST_dadaismus für sofortige Tests
        ui.workflow.value = "dev/TEST_dadaismus";
        
        // Add event listener for workflow selection
        ui.workflow.addEventListener('change', () => {
            checkWorkflowSafetyNode();
            updateWorkflowDescription();
        });
    } catch (error) {
        console.error('Failed to load workflows:', error);
    }
}

function handleNonUserMode(workflowConfig) {
    // Hide workflow dropdown and show info instead
    const workflowContainer = ui.workflow.parentElement;
    const label = workflowContainer.querySelector('label');
    
    // Clear the select dropdown
    ui.workflow.innerHTML = '';
    ui.workflow.style.display = 'none';
    
    // Remove any existing info div
    const existingInfo = document.getElementById('workflow-mode-info');
    if (existingInfo) {
        existingInfo.remove();
    }
    
    // Create info display
    const infoDiv = document.createElement('div');
    infoDiv.id = 'workflow-mode-info';
    infoDiv.className = 'workflow-mode-info';
    
    if (workflowConfig.mode === "fixed") {
        // Extract display name from fixed workflow
        const pathParts = workflowConfig.fixed_workflow.split('/');
        const workflowId = pathParts[pathParts.length - 1].replace('.json', '');
        
        let displayName = workflowConfig.fixed_workflow;
        if (workflowMetadata?.workflows?.[workflowId]) {
            const metadata = workflowMetadata.workflows[workflowId];
            displayName = metadata.name?.[currentLanguage] || 
                         metadata.name?.['de'] || 
                         workflowId.replace(/^ai4artsed_/, '').replace(/_\d+$/, '').replace(/_/g, ' ');
        }
        
        infoDiv.innerHTML = `
            <div class="mode-indicator fixed-mode">
                <strong>${t('workflow-fixed-mode')}</strong> ${displayName}
            </div>
            <div class="mode-description">
                ${t('workflow-fixed-description')}
            </div>
        `;
    } else if (workflowConfig.mode === "system") {
        const folderNames = workflowConfig.system_folders || [];
        
        // Get localized category names
        const localizedFolders = folderNames.map(folder => {
            if (workflowMetadata?.categories?.[folder]) {
                return workflowMetadata.categories[folder][currentLanguage] || 
                       workflowMetadata.categories[folder]['de'] || 
                       folder;
            }
            return folder;
        });
        
        infoDiv.innerHTML = `
            <div class="mode-indicator system-mode">
                <strong>${t('workflow-system-mode')}</strong> ${t('workflow-system-random')}
            </div>
            <div class="mode-description">
                ${t('workflow-system-description')} ${localizedFolders.join(', ')}
            </div>
        `;
    }
    
    // Insert after label
    label.insertAdjacentElement('afterend', infoDiv);
    
    // Update the label text to reflect the mode
    if (workflowConfig.mode === "fixed") {
        label.textContent = t('workflow-fixed-label');
    } else if (workflowConfig.mode === "system") {
        label.textContent = t('workflow-system-label');
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

// ====================================================================
// 🚨 DEPRECATED FUNCTION - MIGRATION TO WORKFLOW-STREAMING MODULE 🚨
// ====================================================================
// This function is deprecated as of 2025-08-16. All submit functionality
// has been consolidated into the workflow-streaming.js module for better
// code organization and to avoid duplication.
//
// DEPRECATION STRATEGY:
// - This function remains as a fallback with debug logging
// - It redirects to the active implementation in workflow-streaming.js
// - Debug messages help identify any remaining calls to this deprecated function
// - Once confirmed no calls exist, this function can be safely removed
//
// ACTIVE IMPLEMENTATION: submitPromptWithFastPolling() in workflow-streaming.js
// ====================================================================
export async function submitPrompt() {
    // Debug logging to identify deprecated function calls
    console.error('🚨 DEPRECATED: submitPrompt() from workflow.js called!');
    console.error('📍 Call stack:', new Error().stack);
    console.error('🔄 Auto-redirecting to submitPromptWithFastPolling from workflow-streaming.js');
    console.error('🛠️  Please update calling code to use the active implementation');
    
    try {
        // Dynamic import to avoid circular dependencies
        const { submitPromptWithFastPolling } = await import('./workflow-streaming.js');
        return await submitPromptWithFastPolling();
    } catch (error) {
        console.error('❌ Failed to redirect to active implementation:', error);
        setStatus('Fehler beim Laden der Workflow-Engine. Bitte Seite neu laden.', 'error');
        throw error;
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
