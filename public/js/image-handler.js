// AI4ArtsEd - Image Handler Module
import { ui } from './ui-elements.js';
import { setStatus, clearOutputDisplays, startProcessingDisplay, stopProcessingDisplay } from './ui-utils.js';
import { reportUploadProgress } from './sse-connection.js';

export let uploadedImageData = null;

/**
 * Perform image analysis and return the generated text
 * @param {boolean} isPartOfWorkflow - If true, won't manage UI state
 * @returns {Promise<string|null>} The analysis result or null if failed
 */
export async function performImageAnalysis(isPartOfWorkflow = false) {
    if (!uploadedImageData) {
        return null;
    }
    
    // Only manage UI if not part of workflow
    if (!isPartOfWorkflow) {
        clearOutputDisplays();
        startProcessingDisplay("Analysiere Bild...");
    }

    let analysisTimer = null;
    let progressReportTimer = null;
    try {
        const analysisDuration = 60000; // 60 seconds in ms
        const analysisStartTime = Date.now();
        
        // Update UI progress - but only if not part of workflow
        if (!isPartOfWorkflow) {
            analysisTimer = setInterval(() => {
                const elapsedTime = Date.now() - analysisStartTime;
                const progress = Math.min(100, Math.floor((elapsedTime / analysisDuration) * 100));
                ui.processingMessage.textContent = `Analysiere Bild... ${progress}%`;
                if (progress >= 100) clearInterval(analysisTimer);
            }, 500);
        }
        
        // Report progress to server to keep connection alive (every 5 seconds)
        progressReportTimer = setInterval(async () => {
            const elapsedTime = Date.now() - analysisStartTime;
            const progress = Math.min(100, Math.floor((elapsedTime / analysisDuration) * 100));
            await reportUploadProgress(progress, 'analyzing');
        }, 5000);

        // Längerer Timeout für Bildanalyse (2 Minuten)
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 120000); // 2 Minuten
        
        const response = await fetch('/analyze_image', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: uploadedImageData }),
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Analyse fehlgeschlagen');
        }
        
        const generatedText = result.analysis || result.generated_prompt;
        
        if (generatedText) {
            return generatedText;
        } else {
            throw new Error('Keine Analyse erhalten');
        }

    } catch (err) {
        if (!isPartOfWorkflow) {
            setStatus(`Fehler während der Analyse: ${err.message}`, 'error');
        }
        return null;
    } finally {
        if (analysisTimer) clearInterval(analysisTimer);
        if (progressReportTimer) clearInterval(progressReportTimer);
        // Report completion
        await reportUploadProgress(100, 'completed');
        if (!isPartOfWorkflow) {
            stopProcessingDisplay();
        }
    }
}

export async function handleFile(file) {
    if (!file || !file.type.startsWith('image/')) {
        setStatus('Bitte laden Sie eine Bilddatei hoch.', 'warning');
        return;
    }
    
    const reader = new FileReader();
    reader.onload = async (e) => {
        uploadedImageData = e.target.result;
        
        // Show image preview inline with prompt field
        ui.addMediaBtn.style.display = 'none';
        ui.imagePreviewWrapper.style.display = 'block';
        ui.imagePreviewWrapper.classList.add('active');
        ui.imagePreview.src = uploadedImageData;
        ui.imageUploadArea.classList.add('has-image');
        
        // Keep prompt field visible so user can add text
        // ui.prompt.style.display remains as is
        
        // Update placeholder to indicate image will be analyzed
        ui.prompt.placeholder = 'Optionaler Text (wird mit Bildanalyse kombiniert)...';
        
        // Just show status, no automatic analysis
        setStatus('Bild hochgeladen. Sie können zusätzlichen Text eingeben. Klicken Sie auf "Generieren" um zu starten.', 'success');
    };
    reader.readAsDataURL(file);
}

export function removeImage() {
    uploadedImageData = null;
    ui.fileInput.value = '';
    ui.imagePreview.src = '';
    ui.prompt.style.display = 'block';
    ui.addMediaBtn.style.display = 'block';
    ui.imagePreviewWrapper.style.display = 'none';
    ui.imagePreviewWrapper.classList.remove('active');
    ui.imageUploadArea.classList.remove('has-image');
    // Don't clear prompt - user may have typed something
    // Restore original placeholder
    ui.prompt.placeholder = ui.prompt.getAttribute('data-original-placeholder') || 'z.B. Eine Calla-Lilie in Nahaufnahme...';
    ui.promptDisplay.style.display = 'none';
}

export function setupImageHandlers() {
    // Save original placeholder
    if (ui.prompt && !ui.prompt.hasAttribute('data-original-placeholder')) {
        ui.prompt.setAttribute('data-original-placeholder', ui.prompt.placeholder);
    }
    
    // Click handlers
    ui.addMediaBtn.addEventListener('click', () => ui.fileInput.click());
    ui.fileInput.addEventListener('change', (e) => handleFile(e.target.files[0]));
    
    // Drag and drop on prompt
    ui.prompt.addEventListener('dragover', e => { 
        e.preventDefault(); 
        ui.prompt.classList.add('drag-over'); 
    });
    
    ui.prompt.addEventListener('dragleave', () => ui.prompt.classList.remove('drag-over'));
    
    ui.prompt.addEventListener('drop', e => {
        e.preventDefault();
        ui.prompt.classList.remove('drag-over');
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFile(e.dataTransfer.files[0]);
        }
    });
    
    // Drag and drop on image upload area
    ui.imageUploadArea.addEventListener('dragover', e => { 
        e.preventDefault(); 
        ui.imageUploadArea.style.borderColor = 'var(--primary-color)';
        ui.imageUploadArea.style.backgroundColor = 'var(--hover-bg)';
    });
    
    ui.imageUploadArea.addEventListener('dragleave', () => {
        ui.imageUploadArea.style.borderColor = '';
        ui.imageUploadArea.style.backgroundColor = '';
    });
    
    ui.imageUploadArea.addEventListener('drop', e => {
        e.preventDefault();
        ui.imageUploadArea.style.borderColor = '';
        ui.imageUploadArea.style.backgroundColor = '';
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFile(e.dataTransfer.files[0]);
        }
    });
    
    ui.removeImageBtn.addEventListener('click', e => { 
        e.stopPropagation(); 
        removeImage(); 
    });
}
