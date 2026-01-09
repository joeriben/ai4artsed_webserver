<template>
  <div class="training-container">
    <h1>LoRA Training Studio</h1>
    <p class="description">
      Train custom Styles for Stable Diffusion 3.5 Large. 
      Optimized for NVIDIA RTX 6000 Ada (96GB).
    </p>

    <div class="grid-layout">
      <!-- Config Column -->
      <div class="column config-column">
        <label>Project Name</label>
        <input v-model="project_name" placeholder="e.g. yoruba_heritage" :disabled="is_training" />

        <label>Trigger Word</label>
        <input v-model="trigger_word" placeholder="e.g. yoruba style" :disabled="is_training" />
        <small>The word you will use in prompts to activate this style.</small>

        <label>Training Images (10-50 recommended)</label>
        <div 
          class="drop-zone" 
          @dragover.prevent 
          @drop.prevent="handleDrop"
          @click="loadFileSelect"
          :class="{ 'has-files': images.length > 0 }"
        >
          <input type="file" ref="fileInput" multiple @change="handleFileSelect" style="display: none" accept="image/*" />
          <div v-if="images.length === 0">
            Click or Drop images here
          </div>
          <div v-else>
            {{ images.length }} images selected
          </div>
        </div>

        <div class="action-buttons">
          <button 
            class="start-btn" 
            @click="startTraining" 
            :disabled="is_training || !canStart"
            :class="{ 'is-loading': is_training }"
          >
            {{ is_training ? 'Training in Progress...' : 'Start Training' }}
          </button>
          
          <button 
            v-if="is_training" 
            class="stop-btn" 
            @click="stopTraining"
          >
            Stop
          </button>
        </div>

        <!-- GDPR Delete Logic -->
        <button 
          v-if="!is_training && project_name && !images.length" 
          class="delete-btn" 
          @click="deleteProject"
        >
          🗑️ Delete Project Files (GDPR)
        </button>
      </div>

      <!-- Log Column -->
      <div class="column log-column">
        <label>Training Logs</label>
        <div class="terminal" ref="logContainer" @scroll="handleScroll">
          <div v-for="(line, index) in logs" :key="index" class="log-line">
            {{ line }}
          </div>
          <div v-if="logs.length === 0" class="log-placeholder">
            Waiting for training to start...
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue';

const project_name = ref('');
const trigger_word = ref('');
const images = ref<File[]>([]);
const logs = ref<string[]>([]);
const is_training = ref(false);
const logContainer = ref<HTMLElement | null>(null);
const fileInput = ref<HTMLInputElement | null>(null);
let eventSource: EventSource | null = null;
let userHasScrolledUp = false;

const canStart = computed(() => {
  return project_name.value.length > 3 && images.value.length >= 5;
});

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:17802';

onMounted(() => {
  checkStatus();
});

onUnmounted(() => {
  if (eventSource) eventSource.close();
});

const loadFileSelect = () => {
  fileInput.value?.click();
};

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files) {
    addFiles(Array.from(target.files));
  }
};

const handleDrop = (event: DragEvent) => {
  if (event.dataTransfer?.files) {
    addFiles(Array.from(event.dataTransfer.files));
  }
};

const addFiles = (fileList: File[]) => {
  // Filter only images
  const imageFiles = fileList.filter(f => f.type.startsWith('image/'));
  images.value = [...images.value, ...imageFiles];
};

const checkStatus = async () => {
  try {
    const res = await fetch(`${API_BASE}/api/training/status`);
    const data = await res.json();
    if (data.is_training) {
      is_training.value = true;
      project_name.value = data.project_name || '';
      connectSSE();
    }
  } catch (e) {
    console.error("Failed to check status", e);
  }
};

const startTraining = async () => {
  if (!canStart.value) return;

  const formData = new FormData();
  formData.append('project_name', project_name.value);
  formData.append('trigger_word', trigger_word.value);
  images.value.forEach(img => {
    formData.append('images', img);
  });

  is_training.value = true;
  logs.value = ["Initiating upload..."];

  try {
    const res = await fetch(`${API_BASE}/api/training/start`, {
      method: 'POST',
      body: formData
    });
    
    if (!res.ok) {
      throw new Error((await res.json()).message);
    }
    
    logs.value.push("Upload complete. Starting Kohya process...");
    connectSSE();
    
  } catch (e: any) {
    logs.value.push(`Error: ${e.message}`);
    is_training.value = false;
  }
};

const stopTraining = async () => {
  try {
    await fetch(`${API_BASE}/api/training/stop`, { method: 'POST' });
    logs.value.push("Stop signal sent.");
  } catch (e) {
    console.error(e);
  }
};

const deleteProject = async () => {
  if (!confirm(`Are you sure you want to delete all data for project '${project_name.value}'? This cannot be undone.`)) return;
  
  try {
    const res = await fetch(`${API_BASE}/api/training/delete`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ project_name: project_name.value })
    });
    
    if (res.ok) {
      alert("Project files deleted.");
      images.value = []; // Clear local
    } else {
      alert("Failed to delete files.");
    }
  } catch (e) {
    console.error(e);
  }
};

const connectSSE = () => {
  if (eventSource) eventSource.close();
  
  console.log("Connecting to Event Stream...");
  eventSource = new EventSource(`${API_BASE}/api/training/events`);
  
  eventSource.onmessage = (e) => {
      // General keepalive or ping
  };

  eventSource.addEventListener('log', (e) => {
    const newLogs = JSON.parse(e.data);
    logs.value.push(...newLogs);
    if (!userHasScrolledUp) {
      scrollToBottom();
    }
  });
  
  eventSource.addEventListener('status', (e) => {
    const status = JSON.parse(e.data);
    is_training.value = status.is_training;
    if (!status.is_training && eventSource) {
      eventSource.close();
      eventSource = null;
    }
  });
  
  eventSource.addEventListener('done', () => {
    eventSource?.close();
    is_training.value = false;
  });

  eventSource.onerror = (err) => {
    console.error("SSE Error (Timeout?):", err);
    eventSource?.close();
    
    // Auto-Reconnect Logic if we think training is still running
    if (is_training.value) {
        setTimeout(() => {
            console.log("Attempting reconnect...");
            connectSSE();
        }, 3000);
    }
  };
};

const scrollToBottom = () => {
  nextTick(() => {
    if (logContainer.value) {
      logContainer.value.scrollTop = logContainer.value.scrollHeight;
    }
  });
};

const handleScroll = () => {
  if (!logContainer.value) return;
  const { scrollTop, scrollHeight, clientHeight } = logContainer.value;
  // If user scrolls up (is not at bottom), stop autoscrolling
  // Tolerance of 50px
  if (scrollTop + clientHeight < scrollHeight - 50) {
    userHasScrolledUp = true;
  } else {
    userHasScrolledUp = false;
  }
};
</script>

<style scoped>
.training-container {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  color: var(--text-color);
  height: calc(100vh - 60px);
  display: flex;
  flex-direction: column;
}

h1 {
  font-size: 2rem;
  margin-bottom: 0.5rem;
  background: linear-gradient(90deg, #ff00ff, #00ffff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.description {
  margin-bottom: 2rem;
  opacity: 0.8;
}

.grid-layout {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 2rem;
  flex: 1;
  min-height: 0; /* Important for scroll */
}

.column {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

label {
  font-weight: bold;
  margin-bottom: -0.5rem;
}

input {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 0.8rem;
  border-radius: 4px;
  color: white;
  font-size: 1rem;
}

.drop-zone {
  border: 2px dashed rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: 3rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.drop-zone:hover, .drop-zone.has-files {
  border-color: #00ffff;
  background: rgba(0, 255, 255, 0.05);
}

.action-buttons {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.start-btn {
  flex: 1;
  background: #00ffff;
  color: black;
  border: none;
  padding: 1rem;
  font-weight: bold;
  font-size: 1.1rem;
  cursor: pointer;
  border-radius: 4px;
  transition: transform 0.1s;
}

.start-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.stop-btn {
  flex: 0.3;
  background: #ff0055;
  color: white;
  border: none;
  padding: 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

.delete-btn {
  margin-top: 2rem;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.6);
  padding: 0.8rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s;
}

.delete-btn:hover {
  border-color: #ff0055;
  color: #ff0055;
  background: rgba(255, 0, 85, 0.1);
}

.terminal {
  flex: 1;
  background: #0a0a0a;
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 4px;
  padding: 1rem;
  font-family: 'Consolas', 'Monaco', monospace;
  overflow-y: auto;
  font-size: 0.85rem;
  line-height: 1.4;
  color: #00ff00; /* Matrix green style for better readability */
  box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
}

/* Custom Scrollbar */
.terminal::-webkit-scrollbar {
  width: 10px;
}

.terminal::-webkit-scrollbar-track {
  background: #1a1a1a;
  border-radius: 4px;
}

.terminal::-webkit-scrollbar-thumb {
  background: #333;
  border-radius: 4px;
  border: 2px solid #1a1a1a;
}

.terminal::-webkit-scrollbar-thumb:hover {
  background: #555;
}

.log-line {
  margin-bottom: 2px;
  word-break: break-all;
}

.log-placeholder {
  color: #666;
  font-style: italic;
}
</style>