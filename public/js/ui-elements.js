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
        this.imageOutputs = document.getElementById('imageOutputs');
        this.imageOutputsContent = document.getElementById('imageOutputsContent');
        this.textOutputs = document.getElementById('textOutputs');
        this.textOutputsContent = document.getElementById('textOutputsContent');
        this.audioContainer = document.getElementById('audioContainer');
        this.audioPlayer = document.getElementById('audioPlayer');
        this.prompt = document.getElementById('prompt');
        this.addMediaBtn = document.getElementById('add-media-btn');
        this.fileInput = document.getElementById('fileInput');
        this.imagePreviewContainer = document.getElementById('image-preview-container');
        this.imagePreview = document.getElementById('image-preview');
        this.removeImageBtn = document.getElementById('remove-image-btn');
        this.workflow = document.getElementById('workflow');
        this.aspectRatio = document.getElementById('aspectRatio');
    }
};
