// AI4ArtsEd - Execution Handler (NEW Schema-Pipeline Architecture)
// Handles execution via /api/schema/pipeline/execute

import { getSelectedConfigId } from './config-browser.js';
import { ui } from './ui-elements.js';
import { setStatus } from './ui-utils.js';
import { config } from './config.js';

/**
 * Submit prompt for execution
 */
export async function submitPrompt() {
    const configId = getSelectedConfigId();
    const promptText = ui.prompt.value.trim();

    // Validation
    if (!configId) {
        setStatus('Bitte wähle zuerst eine Config aus.', 'warning');
        return;
    }

    if (!promptText) {
        setStatus('Bitte gib einen Prompt ein.', 'warning');
        return;
    }

    // Get aspect ratio
    const aspectRatio = document.querySelector('input[name="aspectRatio"]:checked')?.value || '1:1';

    // Get execution mode
    const executionMode = document.querySelector('input[name="execution-mode"]:checked')?.value || 'eco';

    // Build payload (NEW API format)
    const payload = {
        schema: configId,           // Config ID (e.g., "dada")
        input_text: promptText,     // User prompt
        execution_mode: executionMode,  // "eco" or "fast"
        aspect_ratio: aspectRatio    // For image generation
    };

    console.log('[EXECUTION] Submitting:', payload);

    try {
        // Show processing UI
        ui.submitBtn.classList.add('loading');
        setStatus('Pipeline wird ausgeführt...', 'info');

        // Call NEW API
        const response = await fetch('/api/schema/pipeline/execute', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Unbekannter Fehler');
        }

        const result = await response.json();
        console.log('[EXECUTION] Result:', result);

        // Display result
        displayResult(result);

    } catch (error) {
        console.error('[EXECUTION] Error:', error);
        setStatus(`Fehler: ${error.message}`, 'error');
    } finally {
        ui.submitBtn.classList.remove('loading');
    }
}

/**
 * Display execution result
 */
function displayResult(result) {
    // Check status (Backend sends "status": "success", not "success": true)
    if (result.status === 'error') {
        setStatus(`Fehler: ${result.error}`, 'error');
        return;
    }

    // Show transformed text
    if (result.final_output) {
        ui.promptDisplayText.textContent = result.final_output;
        ui.promptDisplay.style.display = 'block';
    }

    // Check if media was generated
    if (result.media_output) {
        // Backend sends prompt_id in media_output.output (not media_output.prompt_id)
        const promptId = result.media_output.output;
        const mediaType = result.media_output.media_type;

        setStatus(`Text-Transformation erfolgreich - ${mediaType} wird generiert...`, 'success');

        // Start polling for media
        pollForMedia(promptId, mediaType);
    } else {
        // Text-only result
        setStatus('Pipeline erfolgreich abgeschlossen!', 'success');
    }
}

/**
 * Poll for media generation completion (NEW: via Backend API)
 */
async function pollForMedia(promptId, mediaType) {
    const maxAttempts = 120;  // 120 seconds timeout (SD3.5 can take 20-30s)
    let attempts = 0;

    console.log(`[POLLING] Starting poll for ${mediaType}: ${promptId}`);

    const pollInterval = setInterval(async () => {
        attempts++;

        if (attempts > maxAttempts) {
            clearInterval(pollInterval);
            setStatus('Timeout: Media-Generierung dauert zu lange.', 'warning');
            console.error('[POLLING] Timeout after 120 seconds');
            return;
        }

        try {
            // NEW: Poll via Backend API (not ComfyUI directly)
            const response = await fetch(`/api/media/info/${promptId}`);

            if (response.ok) {
                // Media is ready!
                const info = await response.json();
                clearInterval(pollInterval);

                console.log('[POLLING] Media ready:', info);

                // Display media using Backend API
                displayMediaFromBackend(promptId, info);
                setStatus('Media erfolgreich generiert!', 'success');

            } else if (response.status === 404) {
                // Not ready yet, continue polling
                console.log(`[POLLING] Attempt ${attempts}/120: Not ready yet...`);
            } else {
                // Error
                clearInterval(pollInterval);
                const error = await response.json();
                setStatus(`Media-Abruf fehlgeschlagen: ${error.error}`, 'error');
            }

        } catch (error) {
            console.error('[POLLING] Error:', error);
        }
    }, 1000);  // Poll every second
}

/**
 * Display media from Backend API (NEW Architecture)
 */
function displayMediaFromBackend(promptId, mediaInfo) {
    const mediaType = mediaInfo.type;

    if (mediaType === 'image') {
        displayImageFromBackend(promptId);
    } else if (mediaType === 'audio') {
        displayAudioFromBackend(promptId);
    } else if (mediaType === 'video') {
        displayVideoFromBackend(promptId);
    } else {
        console.error('[DISPLAY] Unknown media type:', mediaType);
    }
}

/**
 * Display image via Backend API
 */
function displayImageFromBackend(promptId) {
    const container = ui.imageOutputs;
    const content = ui.imageOutputsContent;

    content.innerHTML = '';

    // Create image element pointing to Backend API
    const imgElement = document.createElement('img');
    imgElement.src = `/api/media/image/${promptId}`;
    imgElement.alt = 'Generated Image';
    imgElement.style.maxWidth = '100%';
    imgElement.style.borderRadius = '8px';

    content.appendChild(imgElement);
    container.style.display = 'block';

    console.log('[DISPLAY] Image displayed from Backend API:', promptId);
}

/**
 * Display audio via Backend API
 */
function displayAudioFromBackend(promptId) {
    const container = document.getElementById('audioContainer');
    const player = document.getElementById('audioPlayer');

    if (!container || !player) {
        console.error('[DISPLAY] Audio container/player not found');
        return;
    }

    player.src = `/api/media/audio/${promptId}`;
    container.style.display = 'block';

    console.log('[DISPLAY] Audio displayed from Backend API:', promptId);
}

/**
 * Display video via Backend API
 */
function displayVideoFromBackend(promptId) {
    // TODO: Implement when video support is added
    console.log('[DISPLAY] Video display not yet implemented:', promptId);
}
