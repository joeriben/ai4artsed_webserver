// AI4ArtsEd - UI Elements Module
export const ui = {
    // Initialize UI elements after DOM is loaded
    init() {
        this.submitBtn = document.getElementById('submitBtn');
        this.status = document.getElementById('status');
        this.processingInfo = document.getElementById('processingInfo');
        this.processingMessage = document.querySelector('#processingInfo .message');
        this.processingTimer = document.querySelector('#processingInfo .timer');
        this.promptDisplay = document.getElementById('promptDisplay');
        this.promptDisplayText = document.getElementById('promptDisplayText');
        this.imageAnalysisDisplay = document.getElementById('imageAnalysisDisplay');
        this.imageAnalysisText = document.getElementById('imageAnalysisText');
        this.imageOutputs = document.getElementById('imageOutputs');
        this.imageOutputsContent = document.getElementById('imageOutputsContent');
        this.textOutputs = document.getElementById('textOutputs');
        this.textOutputsContent = document.getElementById('textOutputsContent');
        this.audioContainer = document.getElementById('audioContainer');
        this.audioPlayer = document.getElementById('audioPlayer');
        this.prompt = document.getElementById('prompt');
        this.addMediaBtn = document.getElementById('add-media-btn');
        this.fileInput = document.getElementById('fileInput');
        this.imageUploadArea = document.getElementById('image-upload-area');
        this.imagePreviewWrapper = document.getElementById('image-preview-wrapper');
        this.imagePreview = document.getElementById('image-preview');
        this.removeImageBtn = document.getElementById('remove-image-btn');
        this.workflow = document.getElementById('workflow');
        // aspectRatio is now accessed via radio buttons, not a single element
    }
};
