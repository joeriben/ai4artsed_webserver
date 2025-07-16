// AI4ArtsEd - Dual Input Handler Module
// Handles processing of combined prompt + image inputs based on workflow type

import { WorkflowClassifier } from './workflow-classifier.js';
import { uploadedImageData, performImageAnalysis } from './image-handler.js';
import { ui } from './ui-elements.js';
import { setStatus } from './ui-utils.js';

export class DualInputHandler {
    constructor(prompt, imageData, workflowName) {
        this.prompt = prompt;
        this.imageData = imageData;
        this.workflowName = workflowName;
    }
    
    /**
     * Process inputs based on workflow type
     * @returns {Promise<Object>} Processed input object ready for workflow submission
     */
    async process() {
        // Check workflow type
        const workflowInfo = await WorkflowClassifier.getWorkflowInfo(this.workflowName);
        
        if (workflowInfo.isInpainting) {
            return await this.processInpaintingInputs(workflowInfo);
        } else {
            return await this.processStandardInputs();
        }
    }
    
    /**
     * Process inputs for inpainting workflow
     * @param {Object} workflowInfo - Workflow information
     * @returns {Promise<Object>} Processed inputs for inpainting
     */
    async processInpaintingInputs(workflowInfo) {
        // Validate that both inputs are present
        if (!this.prompt || !this.imageData) {
            throw new Error('Inpainting-Workflows erfordern sowohl einen Prompt als auch ein Bild.');
        }
        
        return {
            mode: 'inpainting',
            prompt: this.prompt,
            imageData: this.imageData,
            requiresImageAnalysis: false
        };
    }
    
    /**
     * Process inputs for standard workflow
     * @returns {Promise<Object>} Processed inputs for standard workflow
     */
    async processStandardInputs() {
        // If only prompt, use as-is
        if (this.prompt && !this.imageData) {
            return {
                mode: 'standard',
                prompt: this.prompt,
                imageData: null,
                requiresImageAnalysis: false
            };
        }
        
        // If only image, need to analyze it
        if (!this.prompt && this.imageData) {
            // Analyze the image
            const analysisResult = await performImageAnalysis();
            if (!analysisResult) {
                throw new Error('Bildanalyse fehlgeschlagen.');
            }
            
            // Update UI to show the analysis result
            ui.prompt.value = analysisResult;
            ui.promptDisplayText.textContent = analysisResult;
            ui.promptDisplay.style.display = 'block';
            
            return {
                mode: 'standard',
                prompt: analysisResult,
                imageData: null,
                requiresImageAnalysis: false
            };
        }
        
        // If both prompt and image, concatenate
        if (this.prompt && this.imageData) {
            return {
                mode: 'standard_combined',
                prompt: this.prompt,
                imageData: this.imageData,
                requiresImageAnalysis: true
            };
        }
        
        // No inputs
        throw new Error('Bitte geben Sie einen Prompt ein oder laden Sie ein Bild hoch.');
    }
    
    /**
     * Validate inputs based on workflow requirements
     * @returns {boolean} True if inputs are valid
     */
    async validate() {
        try {
            await this.process();
            return true;
        } catch (error) {
            setStatus(error.message, 'warning');
            return false;
        }
    }
}

/**
 * Check if current inputs require dual processing
 * @returns {boolean} True if both prompt and image are present
 */
export function hasDualInputs() {
    const promptText = ui.prompt.value.trim();
    return promptText && uploadedImageData !== null;
}

/**
 * Get current input state
 * @returns {Object} Current input state
 */
export function getInputState() {
    const promptText = ui.prompt.value.trim();
    return {
        hasPrompt: !!promptText,
        hasImage: uploadedImageData !== null,
        isDual: promptText && uploadedImageData !== null,
        prompt: promptText,
        imageData: uploadedImageData
    };
}
