// AI4ArtsEd - UI Utilities Module
import { ui } from './ui-elements.js';

let timerInterval = null;

export function setStatus(message, type = 'info') {
    ui.status.textContent = message;
    ui.status.className = type;
}

export function startProcessingDisplay(message = "Verarbeitung...") {
    let startTime = Date.now();
    ui.submitBtn.disabled = true;
    ui.submitBtn.classList.add('processing');
    ui.processingMessage.textContent = message;
    ui.processingInfo.style.display = 'block';
    if (timerInterval) clearInterval(timerInterval);
    timerInterval = setInterval(() => {
        ui.processingTimer.textContent = `Verstrichene Zeit: ${Math.floor((Date.now() - startTime) / 1000)}s`;
    }, 1000);
}

export function stopProcessingDisplay() {
    ui.submitBtn.disabled = false;
    ui.submitBtn.classList.remove('processing');
    ui.processingInfo.style.display = 'none';
    if (timerInterval) clearInterval(timerInterval);
}

export function clearOutputDisplays() {
    setStatus('', '');
    ui.imageOutputs.style.display = 'none';
    ui.imageOutputsContent.innerHTML = '';
    ui.textOutputs.style.display = 'none';
    ui.textOutputsContent.innerHTML = '';
    ui.audioContainer.style.display = 'none';
    ui.audioPlayer.pause();
    ui.audioPlayer.removeAttribute('src');
    ui.imageAnalysisDisplay.style.display = 'none';
    ui.imageAnalysisText.textContent = '';
    
    // Remove any existing unified output containers
    const existingUnified = document.getElementById('unifiedOutputs');
    if (existingUnified) {
        existingUnified.remove();
    }
}

export function updateDimensions() {
    const selectedRadio = document.querySelector('input[name="aspectRatio"]:checked');
    const aspectRatio = selectedRadio ? selectedRadio.value : '1:1';
    const dims = calculateDimensions('1024', aspectRatio);
    document.getElementById('dimensionsDisplay').textContent = `Auflösung (ca.): ${dims.width} x ${dims.height}px`;
}

export function calculateDimensions(size, ratio) {
    const side = parseInt(size, 10), total = side * side, [w, h] = ratio.split(':').map(Number);
    const r = w / h; let width = Math.round(Math.sqrt(total * r)); let height = Math.round(width / r);
    return { width: Math.round(width / 8) * 8, height: Math.round(height / 8) * 8 };
}
