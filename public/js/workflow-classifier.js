// AI4ArtsEd - Workflow Classifier Module
// Handles classification of workflow types (inpainting vs standard)

export class WorkflowClassifier {
    /**
     * Check if a workflow is an inpainting workflow
     * @param {string} workflowName - Name of the workflow
     * @returns {Promise<boolean>} True if inpainting workflow, false otherwise
     */
    static async isInpaintingWorkflow(workflowName) {
        try {
            const response = await fetch(`/workflow-type/${encodeURIComponent(workflowName)}`);
            if (!response.ok) {
                console.error('Failed to check workflow type');
                return false;
            }
            
            const result = await response.json();
            return result.isInpainting || false;
        } catch (error) {
            console.error('Error checking workflow type:', error);
            return false;
        }
    }
    
    /**
     * Get workflow info including type and requirements
     * @param {string} workflowName - Name of the workflow
     * @returns {Promise<Object>} Workflow info object
     */
    static async getWorkflowInfo(workflowName) {
        try {
            const response = await fetch(`/workflow-info/${encodeURIComponent(workflowName)}`);
            if (!response.ok) {
                throw new Error('Failed to get workflow info');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error getting workflow info:', error);
            return {
                isInpainting: false,
                hasLoadImageNode: false,
                requiresBothInputs: false
            };
        }
    }
}
