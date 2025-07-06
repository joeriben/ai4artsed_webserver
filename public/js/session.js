// AI4ArtsEd - Session Management Module
export let currentSessionData = {
    promptId: null,
    workflowName: null,
    prompt: null
};

export function updateSessionData(data) {
    currentSessionData = { ...currentSessionData, ...data };
}

export async function downloadSession() {
    if (!currentSessionData.promptId) return;
    
    const downloadBtn = document.getElementById('downloadBtn');
    downloadBtn.disabled = true;
    downloadBtn.classList.add('processing');
    
    try {
        const response = await fetch('/api/download-session', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt_id: currentSessionData.promptId,
                user_id: 'DOE_J',
                workflow_name: currentSessionData.workflowName,
                prompt: currentSessionData.prompt
            })
        });
        
        if (!response.ok) {
            const result = await response.json();
            throw new Error(result.error || 'Download fehlgeschlagen');
        }
        
        // Download the ZIP file
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `ai4artsed_session_${currentSessionData.promptId.substring(0, 8)}.zip`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        // Status update handled by ui-utils
        const { setStatus } = await import('./ui-utils.js');
        setStatus('Download erfolgreich gestartet!', 'success');
        
    } catch (error) {
        const { setStatus } = await import('./ui-utils.js');
        setStatus(`Download-Fehler: ${error.message}`, 'error');
    } finally {
        downloadBtn.disabled = false;
        downloadBtn.classList.remove('processing');
    }
}

// Make downloadSession available globally for onclick handler
window.downloadSession = downloadSession;
