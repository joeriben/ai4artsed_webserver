// AI4ArtsEd - Output Display Module
import { ui } from './ui-elements.js';
import { config } from './config.js';
import { setStatus, stopProcessingDisplay } from './ui-utils.js';

export function processAndDisplayResults(outputs, workflowDef) {
    // Try chronological sorting first, fallback to simple display if it fails
    try {
        // Collect all outputs with their node information for chronological sorting
        const allOutputs = [];
        let hasAudio = false;
        
        for (const [nodeId, output] of Object.entries(outputs)) {
            const nodeTitle = workflowDef[nodeId]?._meta?.title;
            const nodeInfo = {
                nodeId: nodeId,
                title: nodeTitle || `Node ${nodeId}`,
                executionOrder: calculateNodeExecutionOrder(nodeId, workflowDef)
            };
            
            if (output.text) {
                allOutputs.push({
                    ...nodeInfo,
                    type: 'text',
                    content: output.text.join('\n')
                });
            }
            
            if (output.images) {
                output.images.forEach((img, index) => {
                    allOutputs.push({
                        ...nodeInfo,
                        type: 'image',
                        url: `/${config.comfyui_proxy_prefix}/view?filename=${encodeURIComponent(img.filename)}&subfolder=${encodeURIComponent(img.subfolder)}&type=${img.type}`,
                        imageIndex: index
                    });
                });
            }
            
            if (output.audio) {
                hasAudio = true;
                ui.audioPlayer.src = `/${config.comfyui_proxy_prefix}/view?filename=${encodeURIComponent(output.audio[0].filename)}&subfolder=${encodeURIComponent(output.audio[0].subfolder)}&type=${output.audio[0].type}`;
                allOutputs.push({
                    ...nodeInfo,
                    type: 'audio',
                    url: ui.audioPlayer.src
                });
            }
        }

        // Sort outputs by execution order
        allOutputs.sort((a, b) => a.executionOrder - b.executionOrder);

        // Display outputs in chronological order
        if (allOutputs.length > 0) {
            displayOutputsInOrder(allOutputs);
        } else {
            // Fallback to simple display if no outputs collected
            throw new Error("No outputs collected for chronological display");
        }
        
        if (hasAudio) ui.audioContainer.style.display = 'block';

        if (allOutputs.length === 0) {
            setStatus('Workflow abgeschlossen, aber keine nachverfolgbare Ausgabe gefunden.', 'warning');
        } else {
            setStatus('Generierung abgeschlossen!', 'success');
        }
        
    } catch (error) {
        console.warn('Chronological display failed, falling back to simple display:', error);
        displaySimpleResults(outputs, workflowDef);
    }
    
    stopProcessingDisplay();
}

function calculateNodeExecutionOrder(nodeId, workflowDef) {
    // Simple topological sort to determine execution order
    const visited = new Set();
    const visiting = new Set();
    let order = 0;
    
    function visit(id) {
        if (visiting.has(id)) return 0; // Circular dependency
        if (visited.has(id)) return 0;
        
        visiting.add(id);
        const node = workflowDef[id];
        if (node && node.inputs) {
            for (const input of Object.values(node.inputs)) {
                if (Array.isArray(input) && input.length > 0 && typeof input[0] === 'string') {
                    const depId = input[0];
                    if (workflowDef[depId]) {
                        visit(depId);
                    }
                }
            }
        }
        visiting.delete(id);
        visited.add(id);
        return ++order;
    }
    
    return visit(nodeId);
}

function displayOutputsInOrder(outputs) {
    // Clear existing displays
    ui.imageOutputs.style.display = 'none';
    ui.imageOutputsContent.innerHTML = '';
    ui.textOutputs.style.display = 'none';
    ui.textOutputsContent.innerHTML = '';
    
    if (outputs.length === 0) return;

    // Create a unified output container
    const unifiedContainer = document.createElement('div');
    unifiedContainer.id = 'unifiedOutputs';
    unifiedContainer.innerHTML = '<h4>Workflow-Ausgaben (in Verarbeitungsreihenfolge):</h4>';
    
    const contentContainer = document.createElement('div');
    contentContainer.id = 'unifiedOutputsContent';
    
    outputs.forEach((output, index) => {
        const outputItem = document.createElement('div');
        outputItem.className = 'unified-output-item';
        outputItem.style.cssText = 'margin-bottom: 20px; padding: 12px; border: 1px solid #ddd; border-radius: 6px; background-color: #f9f9f9;';
        
        const headerDiv = document.createElement('div');
        headerDiv.className = 'output-header';
        headerDiv.style.cssText = 'font-weight: bold; color: #555; margin-bottom: 8px; font-size: 0.9em;';
        headerDiv.textContent = `${index + 1}. ${output.title} (${output.type.toUpperCase()})`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'output-content';
        
        if (output.type === 'image') {
            const imgContainer = document.createElement('div');
            imgContainer.className = 'result-image-container';
            imgContainer.style.cssText = 'position: relative; display: inline-block; width: 100%;';
            
            const img = document.createElement('img');
            img.src = output.url;
            img.className = 'result-image';
            img.style.cssText = 'width: 100%; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);';
            img.alt = 'Generated Image';
            
            // Add hover overlay with + button
            const overlay = document.createElement('div');
            overlay.className = 'image-hover-overlay';
            overlay.style.cssText = `
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                opacity: 0;
                transition: opacity 0.3s ease;
                border-radius: 8px;
                cursor: pointer;
            `;
            
            const plusButton = document.createElement('button');
            plusButton.className = 'use-as-input-btn';
            plusButton.style.cssText = `
                background: white;
                border: none;
                width: 48px;
                height: 48px;
                padding: 0;
                border-radius: 50%;
                cursor: pointer;
                box-shadow: 0 2px 8px rgba(0,0,0,0.3);
                transition: transform 0.2s ease;
                display: flex;
                align-items: center;
                justify-content: center;
            `;
            plusButton.innerHTML = '<img src="icons/redo-circle.svg" alt="Als Input verwenden" style="width: 24px; height: 24px;">';
            plusButton.title = 'Als Input verwenden';
            
            // Add click handler
            plusButton.addEventListener('click', async (e) => {
                e.stopPropagation();
                await useImageAsInput(output.url);
            });
            
            // Add hover effects
            imgContainer.addEventListener('mouseenter', () => {
                overlay.style.opacity = '1';
                plusButton.style.transform = 'scale(1.1)';
            });
            
            imgContainer.addEventListener('mouseleave', () => {
                overlay.style.opacity = '0';
                plusButton.style.transform = 'scale(1)';
            });
            
            overlay.appendChild(plusButton);
            imgContainer.appendChild(img);
            imgContainer.appendChild(overlay);
            contentDiv.appendChild(imgContainer);
        } else if (output.type === 'text') {
            const textContainer = document.createElement('div');
            textContainer.className = 'result-text-container';
            textContainer.style.cssText = 'position: relative;';
            
            const textDiv = document.createElement('div');
            textDiv.style.cssText = 'white-space: pre-wrap; word-wrap: break-word; font-family: monospace, monospace; background: white; padding: 8px; border-radius: 4px; border: 1px solid #ddd;';
            textDiv.textContent = output.content;
            
            // Add hover overlay with recycle button for text
            const overlay = document.createElement('div');
            overlay.className = 'text-hover-overlay';
            overlay.style.cssText = `
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                opacity: 0;
                transition: opacity 0.3s ease;
                border-radius: 4px;
                cursor: pointer;
            `;
            
            const recycleButton = document.createElement('button');
            recycleButton.className = 'use-as-input-btn';
            recycleButton.style.cssText = `
                background: white;
                border: none;
                width: 48px;
                height: 48px;
                padding: 0;
                border-radius: 50%;
                cursor: pointer;
                box-shadow: 0 2px 8px rgba(0,0,0,0.3);
                transition: transform 0.2s ease;
                display: flex;
                align-items: center;
                justify-content: center;
            `;
            recycleButton.innerHTML = '<img src="icons/redo-circle.svg" alt="Als Prompt verwenden" style="width: 24px; height: 24px;">';
            recycleButton.title = 'Als Prompt verwenden';
            
            // Add click handler for text
            recycleButton.addEventListener('click', async (e) => {
                e.stopPropagation();
                useTextAsInput(output.content);
            });
            
            // Add hover effects
            textContainer.addEventListener('mouseenter', () => {
                overlay.style.opacity = '1';
                recycleButton.style.transform = 'scale(1.1)';
            });
            
            textContainer.addEventListener('mouseleave', () => {
                overlay.style.opacity = '0';
                recycleButton.style.transform = 'scale(1)';
            });
            
            overlay.appendChild(recycleButton);
            textContainer.appendChild(textDiv);
            textContainer.appendChild(overlay);
            contentDiv.appendChild(textContainer);
        } else if (output.type === 'audio') {
            const audioNote = document.createElement('div');
            audioNote.style.cssText = 'font-style: italic; color: #666; padding: 8px; background: white; border-radius: 4px; border: 1px solid #ddd;';
            audioNote.textContent = 'Audio-Datei generiert (siehe Audio-Player unten)';
            contentDiv.appendChild(audioNote);
        }
        
        outputItem.appendChild(headerDiv);
        outputItem.appendChild(contentDiv);
        contentContainer.appendChild(outputItem);
    });
    
    unifiedContainer.appendChild(contentContainer);
    
    // Insert the unified container after promptDisplay
    const promptDisplay = ui.promptDisplay;
    promptDisplay.parentNode.insertBefore(unifiedContainer, promptDisplay.nextSibling);
    
    // Add export buttons
    addExportContainer(unifiedContainer);
}

function displaySimpleResults(outputs, workflowDef) {
    // Fallback to simple display logic
    const imageNodes = [], textNodes = [];
    for (const [nodeId, output] of Object.entries(outputs)) {
        const nodeTitle = workflowDef[nodeId]?._meta?.title;
        if (output.text) textNodes.push({ label: nodeTitle || `Node ${nodeId}`, content: output.text.join('\n') });
        if (output.images) imageNodes.push(...output.images.map(img => `/${config.comfyui_proxy_prefix}/view?filename=${encodeURIComponent(img.filename)}&subfolder=${encodeURIComponent(img.subfolder)}&type=${img.type}`));
        if (output.audio) ui.audioPlayer.src = `/${config.comfyui_proxy_prefix}/view?filename=${encodeURIComponent(output.audio[0].filename)}&subfolder=${encodeURIComponent(output.audio[0].subfolder)}&type=${output.audio[0].type}`;
    }

    if (imageNodes.length > 0) {
        ui.imageOutputsContent.innerHTML = '';
        imageNodes.forEach(url => {
            const imgContainer = document.createElement('div');
            imgContainer.className = 'result-image-container';
            imgContainer.style.cssText = 'position: relative; display: inline-block; width: 100%; margin-bottom: 10px;';
            
            const img = document.createElement('img');
            img.src = url;
            img.className = 'result-image';
            img.alt = 'Generated Image';
            img.style.cssText = 'width: 100%; display: block;';
            
            // Add hover overlay with + button
            const overlay = document.createElement('div');
            overlay.className = 'image-hover-overlay';
            overlay.style.cssText = `
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                opacity: 0;
                transition: opacity 0.3s ease;
                cursor: pointer;
            `;
            
            const plusButton = document.createElement('button');
            plusButton.className = 'use-as-input-btn';
            plusButton.style.cssText = `
                background: white;
                border: none;
                width: 48px;
                height: 48px;
                padding: 0;
                border-radius: 50%;
                cursor: pointer;
                box-shadow: 0 2px 8px rgba(0,0,0,0.3);
                transition: transform 0.2s ease;
                display: flex;
                align-items: center;
                justify-content: center;
            `;
            plusButton.innerHTML = '<img src="icons/redo-circle.svg" alt="Als Input verwenden" style="width: 24px; height: 24px;">';
            plusButton.title = 'Als Input verwenden';
            
            // Add click handler
            plusButton.addEventListener('click', async (e) => {
                e.stopPropagation();
                await useImageAsInput(url);
            });
            
            // Add hover effects
            imgContainer.addEventListener('mouseenter', () => {
                overlay.style.opacity = '1';
                plusButton.style.transform = 'scale(1.1)';
            });
            
            imgContainer.addEventListener('mouseleave', () => {
                overlay.style.opacity = '0';
                plusButton.style.transform = 'scale(1)';
            });
            
            overlay.appendChild(plusButton);
            imgContainer.appendChild(img);
            imgContainer.appendChild(overlay);
            ui.imageOutputsContent.appendChild(imgContainer);
        });
        ui.imageOutputs.style.display = 'block';
    }
    
    if (textNodes.length > 0) {
        ui.textOutputsContent.innerHTML = '';
        textNodes.forEach(node => {
            const itemDiv = document.createElement('div');
            itemDiv.className = 'text-output-item';
            itemDiv.style.cssText = 'position: relative; margin-bottom: 10px;';
            
            const labelDiv = document.createElement('div');
            labelDiv.className = 'text-output-label';
            labelDiv.textContent = node.label;
            
            const textContainer = document.createElement('div');
            textContainer.className = 'result-text-container';
            textContainer.style.cssText = 'position: relative;';
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'text-output-content';
            contentDiv.textContent = node.content;
            
            // Add hover overlay with recycle button for text
            const overlay = document.createElement('div');
            overlay.className = 'text-hover-overlay';
            overlay.style.cssText = `
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                opacity: 0;
                transition: opacity 0.3s ease;
                cursor: pointer;
            `;
            
            const recycleButton = document.createElement('button');
            recycleButton.className = 'use-as-input-btn';
            recycleButton.style.cssText = `
                background: white;
                border: none;
                width: 48px;
                height: 48px;
                padding: 0;
                border-radius: 50%;
                cursor: pointer;
                box-shadow: 0 2px 8px rgba(0,0,0,0.3);
                transition: transform 0.2s ease;
                display: flex;
                align-items: center;
                justify-content: center;
            `;
            recycleButton.innerHTML = '<img src="icons/redo-circle.svg" alt="Als Prompt verwenden" style="width: 24px; height: 24px;">';
            recycleButton.title = 'Als Prompt verwenden';
            
            // Add click handler for text
            recycleButton.addEventListener('click', async (e) => {
                e.stopPropagation();
                useTextAsInput(node.content);
            });
            
            // Add hover effects
            textContainer.addEventListener('mouseenter', () => {
                overlay.style.opacity = '1';
                recycleButton.style.transform = 'scale(1.1)';
            });
            
            textContainer.addEventListener('mouseleave', () => {
                overlay.style.opacity = '0';
                recycleButton.style.transform = 'scale(1)';
            });
            
            overlay.appendChild(recycleButton);
            textContainer.appendChild(contentDiv);
            textContainer.appendChild(overlay);
            
            itemDiv.appendChild(labelDiv);
            itemDiv.appendChild(textContainer);
            ui.textOutputsContent.appendChild(itemDiv);
        });
        ui.textOutputs.style.display = 'block';
    }

    if (ui.audioPlayer.src) ui.audioContainer.style.display = 'block';

    if (imageNodes.length === 0 && textNodes.length === 0 && !ui.audioPlayer.src) {
        setStatus('Workflow abgeschlossen, aber keine nachverfolgbare Ausgabe gefunden.', 'warning');
    } else {
        setStatus('Generierung abgeschlossen! (Einfache Anzeige)', 'success');
    }
}

function addExportContainer(container) {
    // Add export buttons after the outputs
    const exportContainer = document.createElement('div');
    exportContainer.id = 'exportContainer';
    exportContainer.style.cssText = 'margin-top: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 6px; background-color: #f8f9fa;';
    
    exportContainer.innerHTML = `
        <h4 style="margin-top: 0; margin-bottom: 12px; color: #333;">Session exportieren</h4>
        <div style="display: flex; gap: 10px; flex-wrap: wrap;">
            <button id="downloadBtn" onclick="window.downloadSession()" style="background-color: #17a2b8; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-size: 14px;">
                Lokaler Download<span class="spinner"></span>
            </button>
        </div>
        <div style="font-size: 0.8em; color: #666; margin-top: 8px;">
            <strong>Automatischer Server-Export:</strong> Wird automatisch für Forschungszwecke gespeichert.<br>
            <strong>Lokaler Download:</strong> Lädt ZIP-Datei auf Ihren Computer herunter.
        </div>
    `;
    
    container.appendChild(exportContainer);
}

// Function to use a generated image as input
async function useImageAsInput(imageUrl) {
    try {
        // Show loading status
        setStatus('Lade Bild...', 'info');
        
        // Fetch the image
        const response = await fetch(imageUrl);
        if (!response.ok) {
            throw new Error('Fehler beim Laden des Bildes');
        }
        
        // Convert to blob
        const blob = await response.blob();
        
        // Convert blob to base64
        const reader = new FileReader();
        reader.onload = function(e) {
            // Import the image-handler module dynamically
            import('./image-handler.js').then(module => {
                // Update the uploadedImageData through the setter function
                module.setUploadedImageData(e.target.result);
                
                // Update UI elements
                ui.addMediaBtn.style.display = 'none';
                ui.imagePreviewWrapper.style.display = 'block';
                ui.imagePreviewWrapper.classList.add('active');
                ui.imagePreview.src = e.target.result;
                ui.imageUploadArea.classList.add('has-image');
                
                // Update placeholder
                ui.prompt.placeholder = 'Optionaler Text (wird mit Bildanalyse kombiniert)...';
                
                // Show success status
                setStatus('Bild als Input gesetzt. Sie können zusätzlichen Text eingeben und auf "Generieren" klicken.', 'success');
                
                // Scroll to input area
                ui.prompt.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }).catch(error => {
                console.error('Error importing image-handler:', error);
                setStatus('Fehler beim Setzen des Bildes als Input', 'error');
            });
        };
        
        reader.onerror = function() {
            setStatus('Fehler beim Verarbeiten des Bildes', 'error');
        };
        
        reader.readAsDataURL(blob);
        
    } catch (error) {
        console.error('Error using image as input:', error);
        setStatus('Fehler: Bild konnte nicht als Input verwendet werden', 'error');
    }
}

// Function to use generated text as input
function useTextAsInput(text) {
    try {
        // Update the prompt field with the text
        ui.prompt.value = text;
        
        // Show success status
        setStatus('Text als Prompt gesetzt. Sie können auf "Generieren" klicken.', 'success');
        
        // Scroll to input area and focus
        ui.prompt.scrollIntoView({ behavior: 'smooth', block: 'center' });
        ui.prompt.focus();
        
    } catch (error) {
        console.error('Error using text as input:', error);
        setStatus('Fehler: Text konnte nicht als Prompt verwendet werden', 'error');
    }
}
