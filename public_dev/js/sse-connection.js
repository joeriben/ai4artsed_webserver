// Server-Sent Events connection for real-time updates
let eventSource = null;
let reconnectTimeout = null;
let reconnectAttempts = 0;
const maxReconnectAttempts = 10;
const reconnectDelay = 5000;

export function initSSEConnection() {
    if (eventSource) {
        return; // Already connected
    }
    
    try {
        eventSource = new EventSource('/sse/connect', {
            withCredentials: true
        });
        
        eventSource.addEventListener('connected', (event) => {
            const data = JSON.parse(event.data);
            console.log('SSE connected:', data);
            reconnectAttempts = 0;
            updateQueueStatus(data.queue_status);
        });
        
        eventSource.addEventListener('queue_update', (event) => {
            const data = JSON.parse(event.data);
            updateQueueStatus(data.queue_status);
        });
        
        eventSource.addEventListener('heartbeat', (event) => {
            // Heartbeat received - connection is alive
            // This helps prevent Cloudflare timeouts
        });
        
        eventSource.onerror = (error) => {
            console.error('SSE error:', error);
            handleConnectionError();
        };
        
        eventSource.onopen = () => {
            console.log('SSE connection opened');
            clearTimeout(reconnectTimeout);
        };
        
    } catch (error) {
        console.error('Failed to create SSE connection:', error);
        handleConnectionError();
    }
}

function handleConnectionError() {
    if (eventSource) {
        eventSource.close();
        eventSource = null;
    }
    
    if (reconnectAttempts < maxReconnectAttempts) {
        reconnectAttempts++;
        console.log(`Reconnecting SSE in ${reconnectDelay}ms (attempt ${reconnectAttempts}/${maxReconnectAttempts})`);
        
        reconnectTimeout = setTimeout(() => {
            initSSEConnection();
        }, reconnectDelay);
    } else {
        console.error('Max reconnection attempts reached');
        updateQueueStatus({ total: '?' });
    }
}

function updateQueueStatus(queueStatus) {
    const queueCountElement = document.getElementById('queue-count');
    if (queueCountElement && queueStatus) {
        const count = queueStatus.total || 0;
        queueCountElement.textContent = count;
        
        // Add or remove the 'has-queue' class based on count
        if (count > 0) {
            queueCountElement.classList.add('has-queue');
        } else {
            queueCountElement.classList.remove('has-queue');
        }
    }
}

// Function to send upload progress (helps keep connection alive during uploads)
export async function reportUploadProgress(progress, status = 'uploading') {
    try {
        const response = await fetch('/sse/upload-progress', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({
                progress: progress,
                status: status
            })
        });
        
        if (!response.ok) {
            console.error('Failed to report upload progress');
        }
    } catch (error) {
        console.error('Error reporting upload progress:', error);
    }
}

// Fallback: Poll for queue status if SSE fails
export async function pollQueueStatus() {
    try {
        const response = await fetch('/api/queue-status', {
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            updateQueueStatus(data);
        }
    } catch (error) {
        console.error('Error polling queue status:', error);
    }
}

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    if (eventSource) {
        eventSource.close();
    }
});
