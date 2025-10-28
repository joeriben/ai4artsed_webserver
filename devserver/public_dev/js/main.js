// AI4ArtsEd - Main Application Module (NEW Schema-Pipeline Architecture)
import { config, loadConfig } from './config.js';
import { ui } from './ui-elements.js';
import { setStatus, updateDimensions } from './ui-utils.js';
import { setupImageHandlers } from './image-handler.js';
import { initConfigBrowser } from './config-browser.js';
import { submitPrompt } from './execution-handler.js';
import { downloadSession } from './session.js';
import { initSSEConnection, pollQueueStatus } from './sse-connection.js';
import { initSimpleTranslation } from './simple-translation.js';

// Make functions available globally for onclick handlers
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

        // Initialize config browser (card-based UI)
        await initConfigBrowser();

        // Setup image handlers
        setupImageHandlers();

        // Initialize dimensions display
        updateDimensions();

        // Initialize SSE connection for real-time updates
        initSSEConnection();

        // Fallback: Poll queue status every 10 seconds if SSE fails
        setInterval(pollQueueStatus, 10000);

        console.log('[MAIN] Application initialized successfully');

    } catch (error) {
        console.error('[MAIN] Initialization error:', error);
        setStatus('Initialisierung fehlgeschlagen: ' + error.message, 'error');
    }
}

// Start the application when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeApp);
