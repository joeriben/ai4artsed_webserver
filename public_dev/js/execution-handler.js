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

        // SESSION 30: Start polling for pipeline status if run_id is present
        if (result.run_id) {
            pollPipelineStatus(result.run_id);
        }

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
        const output = result.media_output.output;
        const mediaType = result.media_output.media_type;

        // Check if output is a data URI (API-based) or prompt_id (ComfyUI-based)
        if (output.startsWith('data:')) {
            // Direct data URI from API (e.g., GPT-5 Image)
            setStatus(`${mediaType} erfolgreich generiert!`, 'success');
            displayDataUri(output, mediaType);
        } else {
            // Prompt ID from ComfyUI - needs polling
            setStatus(`Text-Transformation erfolgreich - ${mediaType} wird generiert...`, 'success');
            pollForMedia(output, mediaType);
        }
    } else {
        // Text-only result
        setStatus('Pipeline erfolgreich abgeschlossen!', 'success');
    }
}

/**
 * SESSION 30: Reset pipeline progress UI for new execution
 */
function resetPipelineProgress() {
    // Clear entity list
    const entityList = document.getElementById('pipeline-entity-list');
    if (entityList) {
        entityList.innerHTML = '';
    }

    // Reset progress bar
    const progressBar = document.getElementById('pipeline-progress-bar');
    if (progressBar) {
        progressBar.style.width = '0%';
    }

    // Reset progress text
    const progressText = document.getElementById('pipeline-progress-text');
    if (progressText) {
        progressText.textContent = '0%';
    }

    // Reset stage indicator
    const stageIndicator = document.getElementById('pipeline-stage-indicator');
    if (stageIndicator) {
        stageIndicator.textContent = 'Stage 0: Wird gestartet...';
    }

    // Hide error message
    const errorMsg = document.getElementById('pipeline-error-message');
    if (errorMsg) {
        errorMsg.style.display = 'none';
    }

    // Show progress container
    const container = document.getElementById('pipeline-progress-container');
    if (container) {
        container.style.display = 'block';
    }
}

/**
 * SESSION 30: Poll for pipeline status (LivePipelineRecorder integration)
 * Polls /api/pipeline/{run_id}/status every second to show real-time progress
 */
async function pollPipelineStatus(runId) {
    console.log(`[PIPELINE-POLLING] Starting poll for run_id: ${runId}`);

    // Reset UI for new pipeline
    resetPipelineProgress();

    // Error tracking for persistent retry with user feedback
    let errorCount = 0;
    let errorStartTime = null;
    const displayedEntities = new Set();  // Track which entities we've shown

    const pollInterval = setInterval(async () => {
        try {
            const response = await fetch(`/api/pipeline/${runId}/status`);

            if (!response.ok) {
                // Error occurred
                errorCount++;
                if (errorCount === 1) {
                    errorStartTime = Date.now();
                }

                const duration = Math.floor((Date.now() - errorStartTime) / 1000);
                console.log(`[PIPELINE-POLLING] Error ${errorCount}: ${response.status}, duration: ${duration}s`);

                // Show persistent "slow connection" message
                setStatus(`Verbindung langsam, Versuch läuft... (${duration}s)`, 'warning');

                // Show error message in progress container
                const errorMsg = document.getElementById('pipeline-error-message');
                if (errorMsg) {
                    errorMsg.textContent = `Verbindung langsam, Versuch läuft... (${duration}s)`;
                    errorMsg.style.display = 'flex';
                }

                return;  // Continue polling, don't give up
            }

            // Success - clear error state
            if (errorCount > 0) {
                console.log(`[PIPELINE-POLLING] Recovered after ${errorCount} errors`);
                errorCount = 0;
                errorStartTime = null;

                // Hide error message
                const errorMsg = document.getElementById('pipeline-error-message');
                if (errorMsg) {
                    errorMsg.style.display = 'none';
                }
            }

            const statusData = await response.json();
            console.log('[PIPELINE-POLLING] Status:', statusData);

            // Update UI with current state
            updatePipelineProgress(statusData);

            // Display new entities
            if (statusData.entities) {
                statusData.entities.forEach(entity => {
                    if (!displayedEntities.has(entity.type)) {
                        displayEntity(entity, runId);
                        displayedEntities.add(entity.type);
                    }
                });
            }

            // Check if pipeline is complete (stage 5 = complete)
            if (statusData.current_state && statusData.current_state.stage === 5) {
                clearInterval(pollInterval);
                console.log('[PIPELINE-POLLING] Pipeline completed');
                setStatus('Pipeline abgeschlossen!', 'success');
            }

        } catch (error) {
            // Network error
            errorCount++;
            if (errorCount === 1) {
                errorStartTime = Date.now();
            }

            const duration = Math.floor((Date.now() - errorStartTime) / 1000);
            console.error(`[PIPELINE-POLLING] Network error ${errorCount}:`, error, `duration: ${duration}s`);
            setStatus(`Verbindung langsam, Versuch läuft... (${duration}s)`, 'warning');

            // Show error message in progress container
            const errorMsg = document.getElementById('pipeline-error-message');
            if (errorMsg) {
                errorMsg.textContent = `Verbindung langsam, Versuch läuft... (${duration}s)`;
                errorMsg.style.display = 'flex';
            }

            // Continue polling, don't give up
        }
    }, 1000);  // Poll every second
}

/**
 * SESSION 30: Update UI with pipeline progress
 */
function updatePipelineProgress(statusData) {
    if (!statusData.current_state) return;

    const { stage, step, progress } = statusData.current_state;

    // Parse progress fraction (e.g., "4/6")
    let percentage = 0;
    if (progress && progress.includes('/')) {
        const [completed, total] = progress.split('/').map(Number);
        percentage = Math.floor((completed / total) * 100);
    }

    console.log(`[PIPELINE-PROGRESS] Stage ${stage}: ${step} (${percentage}%)`);

    // Show progress container
    const container = document.getElementById('pipeline-progress-container');
    if (container) {
        container.style.display = 'block';
    }

    // Update progress bar
    const progressBar = document.getElementById('pipeline-progress-bar');
    if (progressBar) {
        progressBar.style.width = `${percentage}%`;
    }

    // Update progress text
    const progressText = document.getElementById('pipeline-progress-text');
    if (progressText) {
        progressText.textContent = `${percentage}%`;
    }

    // Update stage indicator
    // TODO: i18n - These stage names should come from language config (see CLAUDE.md i18n requirements)
    const stageNames = {
        0: 'Pipeline-Start',
        1: 'Übersetzung & Sicherheit',
        2: 'Interception',
        3: 'Ausgabe-Sicherheit',
        4: 'Media-Generierung',
        5: 'Abgeschlossen'
    };

    const stageName = stageNames[stage] || `Stage ${stage}`;
    const stageIndicator = document.getElementById('pipeline-stage-indicator');
    if (stageIndicator) {
        stageIndicator.textContent = `${stageName}: ${step}`;
    }

    // Also update status text
    setStatus(`${stageName}: ${step} (${percentage}%)`, 'info');
}

/**
 * SESSION 30: Display individual entity in the UI
 */
function displayEntity(entity, runId) {
    console.log('[PIPELINE-ENTITY] New entity:', entity.type, entity.filename);

    const entityList = document.getElementById('pipeline-entity-list');
    if (!entityList) return;

    // Create entity list item
    const listItem = document.createElement('li');
    listItem.className = 'entity-item completed';
    listItem.dataset.entityType = entity.type;

    // Entity type label (translated)
    // TODO: i18n - Entity type labels should come from language config
    const entityLabels = {
        'input': 'Eingabe',
        'translation': 'Übersetzung',
        'safety': 'Sicherheitsprüfung',
        'interception': 'Prompt-Interception',
        'safety_pre_output': 'Ausgabe-Sicherheit',
        'output_image': 'Bild generiert',
        'output_audio': 'Audio generiert',
        'output_video': 'Video generiert',
        'error': 'Fehler'
    };

    const label = entityLabels[entity.type] || entity.type;

    // Format timestamp
    let timeStr = '';
    if (entity.timestamp) {
        const date = new Date(entity.timestamp);
        timeStr = date.toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    }

    // Build HTML
    listItem.innerHTML = `
        <span class="entity-label">${label}</span>
        ${timeStr ? `<span class="entity-timestamp">${timeStr}</span>` : ''}
    `;

    // Append to list
    entityList.appendChild(listItem);
}

/**
 * Display media from data URI (API-based generation like GPT-5)
 */
function displayDataUri(dataUri, mediaType) {
    if (mediaType === 'image') {
        const container = ui.imageOutputs;
        const content = ui.imageOutputsContent;

        content.innerHTML = '';

        // Create image element with data URI
        const imgElement = document.createElement('img');
        imgElement.src = dataUri;
        imgElement.alt = 'Generated Image';
        imgElement.style.maxWidth = '100%';
        imgElement.style.borderRadius = '8px';

        content.appendChild(imgElement);
        container.style.display = 'block';

        console.log('[DISPLAY] Image displayed from data URI');
    } else if (mediaType === 'audio') {
        // Future: Handle audio data URIs
        console.log('[DISPLAY] Audio data URI display not yet implemented');
    } else if (mediaType === 'video') {
        // Future: Handle video data URIs
        console.log('[DISPLAY] Video data URI display not yet implemented');
    } else {
        console.error('[DISPLAY] Unknown media type:', mediaType);
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
    const mediaType = mediaInfo.outputs?.[0]?.type;

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
