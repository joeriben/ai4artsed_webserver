// AI4ArtsEd - Image Handler Module
import { ui } from './ui-elements.js';
import { setStatus, clearOutputDisplays, startProcessingDisplay, stopProcessingDisplay } from './ui-utils.js';

export let uploadedImageData = null;

export async function handleFile(file) {
    if (!file || !file.type.startsWith('image/')) {
        setStatus('Bitte laden Sie eine Bilddatei hoch.', 'warning');
        return;
    }
    
    const reader = new FileReader();
    reader.onload = async (e) => {
        uploadedImageData = e.target.result;
        ui.prompt.style.display = 'none';
        ui.addMediaBtn.style.display = 'none';
        ui.imagePreviewContainer.style.display = 'block';
        ui.imagePreview.src = uploadedImageData;
        
        clearOutputDisplays();
        startProcessingDisplay("Analysiere Bild...");

        let analysisTimer = null;
        try {
            const analysisDuration = 60000; // 60 seconds in ms
            const analysisStartTime = Date.now();
            analysisTimer = setInterval(() => {
                const elapsedTime = Date.now() - analysisStartTime;
                const progress = Math.min(100, Math.floor((elapsedTime / analysisDuration) * 100));
                ui.processingMessage.textContent = `Analysiere Bild... ${progress}%`;
                if (progress >= 100) clearInterval(analysisTimer);
            }, 500);

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
                ui.prompt.value = generatedText;
                
                ui.promptDisplayText.textContent = generatedText;
                ui.promptDisplay.style.display = 'block';
                
                setStatus('Bildanalyse abgeschlossen. Sie können jetzt generieren.', 'success');
            } else {
                setStatus('Keine Analyse erhalten', 'error');
            }

        } catch (err) {
            setStatus(`Fehler während der Analyse: ${err.message}`, 'error');
            removeImage();
        } finally {
            if (analysisTimer) clearInterval(analysisTimer);
            stopProcessingDisplay();
        }
    };
    reader.readAsDataURL(file);
}

export function removeImage() {
    uploadedImageData = null;
    ui.fileInput.value = '';
    ui.imagePreview.src = '';
    ui.prompt.style.display = 'block';
    ui.addMediaBtn.style.display = 'block';
    ui.imagePreviewContainer.style.display = 'none';
    ui.prompt.value = '';
    ui.promptDisplay.style.display = 'none';
}

export function setupImageHandlers() {
    ui.addMediaBtn.addEventListener('click', () => ui.fileInput.click());
    ui.fileInput.addEventListener('change', (e) => handleFile(e.target.files[0]));
    
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
    
    ui.removeImageBtn.addEventListener('click', e => { 
        e.stopPropagation(); 
        removeImage(); 
    });
}
