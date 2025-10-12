// AI4ArtsEd - Main Application Module
import { config, loadConfig } from './config.js';
import { ui } from './ui-elements.js';
import { setStatus, updateDimensions } from './ui-utils.js';
import { setupImageHandlers } from './image-handler.js';
import { loadWorkflows } from './workflow.js';
import { submitPromptWithFastPolling as submitPrompt } from './workflow-streaming.js';
import { downloadSession } from './session.js';
import { initSSEConnection, pollQueueStatus } from './sse-connection.js';
import { initSimpleTranslation } from './simple-translation.js';
import './media-output.js'; // Media-Output-Manager für Bild/Audio/Video

// Make submitPrompt available globally for onclick handler
window.submitPrompt = submitPrompt;
window.updateDimensions = updateDimensions;

// Initialize application
async function initializeApp() {
    // Initialize UI elements
    ui.init();
    
    try {
        // Initialize simple translation for static UI elements
        initSimpleTranslation();
        
        // Load configuration
        await loadConfig();
        
        // Load workflows
        await loadWorkflows();
        
        // Setup image handlers
        setupImageHandlers();
        
        // Initialize dimensions display
        updateDimensions();
        
        // Initialize SSE connection for real-time updates
        initSSEConnection();
        
        // Fallback: Poll queue status every 10 seconds if SSE fails
        setInterval(pollQueueStatus, 10000);
        
    } catch (error) {
        setStatus('Initialisierung fehlgeschlagen: ' + error.message, 'error');
    }
}

// Start the application when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeApp);
