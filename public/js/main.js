// AI4ArtsEd - Main Application Module
import { config, loadConfig } from './config.js';
import { ui } from './ui-elements.js';
import { setStatus, updateDimensions } from './ui-utils.js';
import { setupImageHandlers } from './image-handler.js';
import { loadWorkflows } from './workflow.js';
import { submitPromptWithFastPolling as submitPrompt } from './workflow-streaming.js';
import { downloadSession } from './session.js';

// Make submitPrompt available globally for onclick handler
window.submitPrompt = submitPrompt;
window.updateDimensions = updateDimensions;

// Initialize application
async function initializeApp() {
    // Initialize UI elements
    ui.init();
    
    try {
        // Load configuration
        await loadConfig();
        
        // Load workflows
        await loadWorkflows();
        
        // Setup image handlers
        setupImageHandlers();
        
        // Initialize dimensions display
        updateDimensions();
        
    } catch (error) {
        setStatus('Initialisierung fehlgeschlagen: ' + error.message, 'error');
    }
}

// Start the application when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeApp);
