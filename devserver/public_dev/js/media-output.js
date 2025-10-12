/**
 * Media Output Manager
 * Handles display of different media types (image, audio, video)
 * Tag-based system: #image#, #music#, #audio#, #video#
 */

class MediaOutputManager {
    constructor() {
        this.supportedTypes = ['image', 'audio', 'music', 'video'];
    }
    
    /**
     * Detect media type from response or tags
     */
    detectMediaType(response) {
        // Check if response has media object
        if (response.media && response.media.type) {
            return response.media.type;
        }
        
        // Check for tags in output
        const output = response.final_output || response.translated_prompt || '';
        
        if (output.includes('#image#')) return 'image';
        if (output.includes('#music#')) return 'music';
        if (output.includes('#audio#')) return 'audio';
        if (output.includes('#video#')) return 'video';
        
        return 'text';
    }
    
    /**
     * Display media in container
     */
    display(response, container) {
        const mediaType = this.detectMediaType(response);
        
        if (mediaType === 'text' || !response.media) {
            // No media, just text
            return false;
        }
        
        const mediaUrl = response.media.url;
        const promptId = response.media.prompt_id;
        
        switch (mediaType) {
            case 'image':
                this.displayImage(mediaUrl, promptId, container);
                break;
            case 'audio':
            case 'music':
                this.displayAudio(mediaUrl, promptId, container);
                break;
            case 'video':
                this.displayVideo(mediaUrl, promptId, container);
                break;
            default:
                console.warn('Unknown media type:', mediaType);
                return false;
        }
        
        return true;
    }
    
    /**
     * Display image
     */
    displayImage(url, promptId, container) {
        const mediaDiv = document.createElement('div');
        mediaDiv.className = 'media-output media-image';
        mediaDiv.innerHTML = `
            <div class="media-container">
                <img src="${url}" alt="Generated Image" class="generated-image" />
                <div class="media-controls">
                    <a href="${url}" download="ai4artsed_${promptId}.png" class="btn-download">
                        Download
                    </a>
                </div>
            </div>
        `;
        
        container.appendChild(mediaDiv);
    }
    
    /**
     * Display audio/music
     */
    displayAudio(url, promptId, container) {
        const mediaDiv = document.createElement('div');
        mediaDiv.className = 'media-output media-audio';
        mediaDiv.innerHTML = `
            <div class="media-container">
                <audio controls class="generated-audio">
                    <source src="${url}" type="audio/mpeg">
                    Your browser does not support audio playback.
                </audio>
                <div class="media-controls">
                    <a href="${url}" download="ai4artsed_${promptId}.mp3" class="btn-download">
                        Download
                    </a>
                </div>
                <p class="media-notice">🎵 Audio generation coming soon</p>
            </div>
        `;
        
        container.appendChild(mediaDiv);
    }
    
    /**
     * Display video
     */
    displayVideo(url, promptId, container) {
        const mediaDiv = document.createElement('div');
        mediaDiv.className = 'media-output media-video';
        mediaDiv.innerHTML = `
            <div class="media-container">
                <video controls class="generated-video">
                    <source src="${url}" type="video/mp4">
                    Your browser does not support video playback.
                </video>
                <div class="media-controls">
                    <a href="${url}" download="ai4artsed_${promptId}.mp4" class="btn-download">
                        Download
                    </a>
                </div>
                <p class="media-notice">🎬 Video generation coming soon</p>
            </div>
        `;
        
        container.appendChild(mediaDiv);
    }
}

// Global instance
window.mediaOutputManager = new MediaOutputManager();
