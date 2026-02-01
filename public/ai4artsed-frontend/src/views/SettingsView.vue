<template>
  <!-- Authentication Modal -->
  <SettingsAuthModal v-model="showAuthModal" @authenticated="onAuthenticated" />

  <!-- Settings Content (only show if authenticated) -->
  <div v-if="authenticated" class="settings-container">
    <div class="settings-header">
      <h1>Administration</h1>
      <div class="tabs">
        <button
          :class="['tab-btn', { active: activeTab === 'export' }]"
          @click="activeTab = 'export'"
        >
          Session Export
        </button>
        <button
          :class="['tab-btn', { active: activeTab === 'config' }]"
          @click="activeTab = 'config'"
        >
          Configuration
        </button>
        <button
          :class="['tab-btn', { active: activeTab === 'matrix' }]"
          @click="activeTab = 'matrix'"
        >
          Model Matrix
        </button>
      </div>
    </div>

    <!-- Session Export Tab -->
    <div v-if="activeTab === 'export'">
      <SessionExportView />
    </div>

    <!-- Configuration Tab -->
    <div v-if="activeTab === 'config'">
      <div v-if="loading" class="loading">Loading settings...</div>
      <div v-else-if="error" class="error">Error: {{ error }}</div>

      <div v-else class="settings-content">
      <!-- Quick-Fill Hint -->
      <div class="section">
        <h2>Model Presets</h2>
        <p class="help">
          Use the <strong>Model Matrix</strong> tab to see all available presets and apply them with one click.
          <span v-if="gpuInfo.detected" class="gpu-detected" style="display: block; margin-top: 8px;">
            Detected: {{ gpuInfo.gpu_name }} ({{ gpuInfo.vram_gb }} GB)
          </span>
        </p>
        <button @click="activeTab = 'matrix'" class="action-btn" style="margin-top: 10px;">
          Open Model Matrix
        </button>
      </div>

      <!-- General Settings -->
      <div class="section">
        <h2>General Configuration</h2>
        <table class="config-table">
          <tbody>
            <tr>
              <td class="label-cell">UI Mode</td>
              <td class="value-cell">
                <select v-model="settings.UI_MODE">
                  <option value="kids">Kids (8-12)</option>
                  <option value="youth">Youth (13-17)</option>
                  <option value="expert">Expert</option>
                </select>
                <span class="help-text">Interface complexity level</span>
              </td>
            </tr>
            <tr>
              <td class="label-cell">Safety Level</td>
              <td class="value-cell">
                <select v-model="settings.DEFAULT_SAFETY_LEVEL">
                  <option value="kids">Kids</option>
                  <option value="youth">Youth</option>
                  <option value="adult">Adult</option>
                  <option value="off">Off</option>
                </select>
                <span class="help-text">Content filtering level</span>
              </td>
            </tr>
            <tr>
              <td class="label-cell">Default Language</td>
              <td class="value-cell">
                <select v-model="settings.DEFAULT_LANGUAGE">
                  <option value="de">German (de)</option>
                  <option value="en">English (en)</option>
                </select>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Model Configuration -->
      <div class="section">
        <h2>Model Configuration</h2>
        <p class="help">Model identifiers with provider prefix: local/, mistral/, anthropic/, openai/, openrouter/</p>
        <p class="help">Use of Model Matrix is advised. However, you may configure your settings here freely.</p>
        <p v-if="ollamaModels.length > 0" class="help" style="color: #4CAF50;">
          {{ ollamaModels.length }} Ollama models available (type or select from dropdown)
        </p>

        <table class="config-table">
          <tbody>
            <tr v-for="(label, key) in modelLabels" :key="key">
              <td class="label-cell">{{ label }}</td>
              <td class="value-cell">
                <input
                  type="text"
                  v-model="settings[key]"
                  class="text-input"
                  :list="'ollama-models-' + key"
                />
                <datalist :id="'ollama-models-' + key">
                  <option v-for="model in ollamaModels" :key="model.id" :value="model.id">
                    {{ model.name }} ({{ model.size }})
                  </option>
                </datalist>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- API Configuration -->
      <div class="section">
        <h2>API Configuration</h2>
        <table class="config-table">
          <tbody>
            <tr>
              <td class="label-cell">LLM Provider</td>
            <td class="value-cell">
              <select v-model="settings.LLM_PROVIDER">
                <option value="ollama">Ollama</option>
                <option value="lmstudio">LM Studio</option>
              </select>
              <span class="help-text">Local LLM framework</span>
            </td>
          </tr>
          <tr>
            <td class="label-cell">Ollama API URL</td>
            <td class="value-cell">
              <input type="text" v-model="settings.OLLAMA_API_BASE_URL" class="text-input" />
            </td>
          </tr>
          <tr>
            <td class="label-cell">LM Studio API URL</td>
            <td class="value-cell">
              <input type="text" v-model="settings.LMSTUDIO_API_BASE_URL" class="text-input" />
            </td>
          </tr>
          <tr>
            <td class="label-cell">External LLM Provider</td>
            <td class="value-cell">
              <select v-model="settings.EXTERNAL_LLM_PROVIDER">
                <option value="none">None (Local only, DSGVO)</option>
                <option value="mistral">Mistral AI (EU-based, DSGVO)</option>
                <option value="anthropic">Anthropic Direct API (NOT DSGVO)</option>
                <option value="openai">OpenAI Direct API (NOT DSGVO)</option>
                <option value="openrouter">OpenRouter (NOT DSGVO, EU routing available)</option>
              </select>
              <span class="help-text">Cloud LLM provider - requires API key</span>

              <!-- Provider info boxes -->
              <div v-if="settings.EXTERNAL_LLM_PROVIDER === 'mistral'" class="info-box info-box-success" style="margin-top: 12px;">
                <strong>Mistral AI (EU-based)</strong>
                <p>✅ DSGVO-compliant (EU infrastructure)</p>
                <p>API Base URL: https://api.mistral.ai/v1</p>
                <p>Get your API key at: <a href="https://console.mistral.ai/" target="_blank">console.mistral.ai</a></p>
              </div>

              <div v-if="settings.EXTERNAL_LLM_PROVIDER === 'anthropic'" class="info-box" style="margin-top: 12px; border-color: #ff9800;">
                <strong>Anthropic Direct API</strong>
                <p>⚠️ NOT DSGVO-compliant</p>
                <p>Data processed outside EU. Use only for non-educational contexts.</p>
              </div>

              <div v-if="settings.EXTERNAL_LLM_PROVIDER === 'openai'" class="info-box" style="margin-top: 12px; border-color: #ff9800;">
                <strong>OpenAI Direct API</strong>
                <p>⚠️ NOT DSGVO-compliant (US-based)</p>
                <p>Data processed in United States. Use only for non-educational contexts.</p>
              </div>

              <div v-if="settings.EXTERNAL_LLM_PROVIDER === 'openrouter'" class="info-box" style="margin-top: 12px; border-color: #ff9800;">
                <strong>OpenRouter</strong>
                <p>⚠️ NOT DSGVO-compliant (US company)</p>
                <p>EU server routing configurable in OpenRouter settings, but company is US-based.</p>
              </div>
            </td>
          </tr>
          <!-- API Key field - conditional based on selected provider -->
          <tr v-if="settings.EXTERNAL_LLM_PROVIDER === 'openrouter'">
            <td class="label-cell">OpenRouter API Key</td>
            <td class="value-cell">
              <input
                type="password"
                v-model="openrouterKey"
                placeholder="sk-or-v1-..."
                class="text-input"
              />
              <span class="help-text" v-if="openrouterKeyMasked">Current: {{ openrouterKeyMasked }}</span>
              <span class="help-text">Stored in devserver/openrouter.key</span>
            </td>
          </tr>

          <tr v-if="settings.EXTERNAL_LLM_PROVIDER === 'anthropic'">
            <td class="label-cell">Anthropic API Key</td>
            <td class="value-cell">
              <input
                type="password"
                v-model="anthropicKey"
                placeholder="sk-ant-api03-..."
                class="text-input"
              />
              <span class="help-text" v-if="anthropicKeyMasked">Current: {{ anthropicKeyMasked }}</span>
              <span class="help-text">Stored in devserver/anthropic.key</span>
            </td>
          </tr>

          <tr v-if="settings.EXTERNAL_LLM_PROVIDER === 'openai'">
            <td class="label-cell">OpenAI API Key</td>
            <td class="value-cell">
              <input
                type="password"
                v-model="openaiKey"
                placeholder="sk-proj-..."
                class="text-input"
              />
              <span class="help-text" v-if="openaiKeyMasked">Current: {{ openaiKeyMasked }}</span>
              <span class="help-text">Stored in devserver/openai.key</span>
            </td>
          </tr>

          <tr v-if="settings.EXTERNAL_LLM_PROVIDER === 'mistral'">
            <td class="label-cell">Mistral API Key</td>
            <td class="value-cell">
              <input
                type="password"
                v-model="mistralKey"
                placeholder="..."
                class="text-input"
              />
              <span class="help-text" v-if="mistralKeyMasked">Current: {{ mistralKeyMasked }}</span>
              <span class="help-text">Stored in devserver/mistral.key</span>
            </td>
          </tr>

          </tbody>
        </table>
      </div>

      <!-- Save & Apply Button -->
      <div class="button-row">
        <button @click="saveAndApply" class="save-btn" :disabled="saveInProgress">
          {{ saveInProgress ? 'Saving...' : 'Save & Apply' }}
        </button>
        <span v-if="saveMessage" :class="{'save-message': true, 'error-message': !saveSuccess}">
          {{ saveMessage }}
        </span>
      </div>
      </div>
    </div>

    <!-- Model Matrix Tab -->
    <div v-if="activeTab === 'matrix'">
      <div v-if="loading" class="loading">Loading settings...</div>
      <div v-else-if="error" class="error">Error: {{ error }}</div>
      <ModelMatrixTab
        v-else
        :matrix="matrix"
        :currentSettings="settings"
        :selectedProvider="settings.EXTERNAL_LLM_PROVIDER || 'none'"
        :detectedVramTier="gpuInfo.vram_tier || null"
        @apply-preset="handleMatrixPresetApply"
        @matrix-updated="loadSettings"
      />
    </div>
  </div>
</template>

<script setup>
import SessionExportView from '../components/SessionExportView.vue'
import SettingsAuthModal from '../components/SettingsAuthModal.vue'
import ModelMatrixTab from '../components/ModelMatrixTab.vue'
import { ref, computed, onMounted } from 'vue'

// Authentication state
const authenticated = ref(false)
const showAuthModal = ref(false)

const activeTab = ref('export')
const loading = ref(true)
const error = ref(null)
const settings = ref({})
const matrix = ref({})
const gpuInfo = ref({ detected: false, error: null })
const openrouterKey = ref('')
const openrouterKeyMasked = ref('')
const anthropicKey = ref('')
const anthropicKeyMasked = ref('')
const openaiKey = ref('')
const openaiKeyMasked = ref('')
const mistralKey = ref('')
const mistralKeyMasked = ref('')
const awsCredentialsConfigured = ref(false)
const saveMessage = ref('')
const saveSuccess = ref(true)
const saveInProgress = ref(false)
const ollamaModels = ref([])  // Session 133: Ollama model dropdown

const modelLabels = {
  'STAGE1_TEXT_MODEL': 'Stage 1 - Text Model',
  'STAGE1_VISION_MODEL': 'Stage 1 - Vision Model',
  'STAGE2_INTERCEPTION_MODEL': 'Stage 2 - Interception Model',
  'STAGE2_OPTIMIZATION_MODEL': 'Stage 2 - Optimization Model',
  'STAGE3_MODEL': 'Stage 3 - Translation/Safety Model',
  'STAGE4_LEGACY_MODEL': 'Stage 4 - Legacy Model',
  'CHAT_HELPER_MODEL': 'Chat Helper Model',
  'IMAGE_ANALYSIS_MODEL': 'Image Analysis Model',
  'CODING_MODEL': 'Code Generation (Tone.js, p5.js)'
}

// Check if any cloud models are being used
const cloudModelsDetected = computed(() => {
  const cloudModels = []
  Object.keys(modelLabels).forEach(key => {
    const modelValue = settings.value[key] || ''
    // Cloud models don't start with "local/"
    if (modelValue && !modelValue.startsWith('local/')) {
      cloudModels.push(`${modelLabels[key]}: ${modelValue}`)
    }
  })
  return cloudModels
})

const hasCloudModels = computed(() => {
  return cloudModelsDetected.value.length > 0
})

// Session 133: Load available Ollama models for dropdown
async function loadOllamaModels() {
  try {
    const response = await fetch('/api/settings/ollama-models')
    if (response.ok) {
      const data = await response.json()
      if (data.success && data.models) {
        ollamaModels.value = data.models
        console.log(`[Settings] Loaded ${data.models.length} Ollama models`)
      }
    }
  } catch (e) {
    console.warn('[Settings] Could not load Ollama models:', e)
  }
}

async function loadSettings() {
  try {
    loading.value = true
    error.value = null

    // Load current settings and matrix
    const response = await fetch('/api/settings/', {  // Trailing slash to match Flask route
      credentials: 'include'
    })
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    const data = await response.json()
    settings.value = data.current
    matrix.value = data.matrix

    // Load API key statuses
    const keyResponse = await fetch('/api/settings/openrouter-key', {
      credentials: 'include'
    })
    if (keyResponse.ok) {
      const keyData = await keyResponse.json()
      if (keyData.exists) {
        openrouterKeyMasked.value = keyData.masked
      }
    }

    const anthropicResponse = await fetch('/api/settings/anthropic-key', {
      credentials: 'include'
    })
    if (anthropicResponse.ok) {
      const anthropicData = await anthropicResponse.json()
      if (anthropicData.exists) {
        anthropicKeyMasked.value = anthropicData.masked
      }
    }

    const openaiResponse = await fetch('/api/settings/openai-key', {
      credentials: 'include'
    })
    if (openaiResponse.ok) {
      const openaiData = await openaiResponse.json()
      if (openaiData.exists) {
        openaiKeyMasked.value = openaiData.masked
      }
    }

    const mistralResponse = await fetch('/api/settings/mistral-key', {
      credentials: 'include'
    })
    if (mistralResponse.ok) {
      const mistralData = await mistralResponse.json()
      if (mistralData.exists) {
        mistralKeyMasked.value = mistralData.masked
      }
    }

  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function detectGpu() {
  try {
    const response = await fetch('/api/settings/gpu-info')
    if (response.ok) {
      const data = await response.json()
      gpuInfo.value = data

      if (data.detected && data.vram_tier) {
        console.log(`[Settings] GPU detected: ${data.gpu_name} (${data.vram_gb} GB) → ${data.vram_tier}`)
      }
    }
  } catch (e) {
    console.warn('[Settings] GPU detection failed:', e)
    gpuInfo.value = { detected: false, error: e.message }
  }
}

// fillFromPreset is now handled by handleMatrixPresetApply

// Handler for Matrix tab preset application (new structure)
async function handleMatrixPresetApply(provider) {
  try {
    // Fetch merged preset from backend
    const response = await fetch(`/api/settings/preset/${provider}`, {
      credentials: 'include'
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    const preset = await response.json()

    // Apply all model fields from preset
    Object.keys(modelLabels).forEach(key => {
      if (preset.models && preset.models[key]) {
        settings.value[key] = preset.models[key]
      }
    })

    // Apply provider setting
    settings.value.EXTERNAL_LLM_PROVIDER = preset.EXTERNAL_LLM_PROVIDER

    saveMessage.value = `✓ Applied preset: ${preset.label}`
    saveSuccess.value = true
    setTimeout(() => { saveMessage.value = '' }, 3000)

    // Switch to config tab to show filled values
    activeTab.value = 'config'

  } catch (e) {
    saveMessage.value = `Error applying preset: ${e.message}`
    saveSuccess.value = false
    setTimeout(() => { saveMessage.value = '' }, 5000)
  }
}

async function handleAwsCsvUpload(event) {
  const file = event.target.files[0]
  if (!file) return

  try {
    const text = await file.text()
    const formData = new FormData()
    formData.append('csv', file)

    const response = await fetch('/api/settings/aws-credentials', {
      method: 'POST',
      body: formData
    })

    const result = await response.json()

    if (response.ok) {
      awsCredentialsConfigured.value = true
      saveMessage.value = '✓ AWS credentials uploaded successfully. Click "Apply Settings" to activate.'
      saveSuccess.value = true
    } else {
      throw new Error(result.error || 'Upload failed')
    }
  } catch (err) {
    saveMessage.value = `Error uploading AWS credentials: ${err.message}`
    saveSuccess.value = false
  }

  setTimeout(() => { saveMessage.value = '' }, 5000)
}

async function saveAndApply() {
  try {
    saveInProgress.value = true
    saveMessage.value = 'Saving...'
    saveSuccess.value = true

    // Build payload
    const payload = { ...settings.value }

    // Add API keys if provided
    if (openrouterKey.value) {
      payload.OPENROUTER_API_KEY = openrouterKey.value
    }
    if (anthropicKey.value) {
      payload.ANTHROPIC_API_KEY = anthropicKey.value
    }
    if (openaiKey.value) {
      payload.OPENAI_API_KEY = openaiKey.value
    }
    if (mistralKey.value) {
      payload.MISTRAL_API_KEY = mistralKey.value
    }

    // Step 1: Save settings
    const saveResponse = await fetch('/api/settings/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(payload)
    })

    if (!saveResponse.ok) {
      throw new Error(`Save failed: HTTP ${saveResponse.status}`)
    }

    // Step 2: Apply settings (hot-reload)
    saveMessage.value = 'Applying...'
    const applyResponse = await fetch('/api/settings/reload-settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include'
    })

    if (!applyResponse.ok) {
      throw new Error(`Apply failed: HTTP ${applyResponse.status}`)
    }

    saveMessage.value = '✓ Settings saved and applied'
    saveSuccess.value = true

    // Clear API key inputs and reload masked versions after successful save
    if (openrouterKey.value) {
      openrouterKey.value = ''
      const keyResponse = await fetch('/api/settings/openrouter-key', {
        credentials: 'include'
      })
      if (keyResponse.ok) {
        const keyData = await keyResponse.json()
        if (keyData.exists) {
          openrouterKeyMasked.value = keyData.masked
        }
      }
    }

    if (anthropicKey.value) {
      anthropicKey.value = ''
      const anthropicResponse = await fetch('/api/settings/anthropic-key', {
        credentials: 'include'
      })
      if (anthropicResponse.ok) {
        const anthropicData = await anthropicResponse.json()
        if (anthropicData.exists) {
          anthropicKeyMasked.value = anthropicData.masked
        }
      }
    }

    if (openaiKey.value) {
      openaiKey.value = ''
      const openaiResponse = await fetch('/api/settings/openai-key', {
        credentials: 'include'
      })
      if (openaiResponse.ok) {
        const openaiData = await openaiResponse.json()
        if (openaiData.exists) {
          openaiKeyMasked.value = openaiData.masked
        }
      }
    }

    if (mistralKey.value) {
      mistralKey.value = ''
      const mistralResponse = await fetch('/api/settings/mistral-key', {
        credentials: 'include'
      })
      if (mistralResponse.ok) {
        const mistralData = await mistralResponse.json()
        if (mistralData.exists) {
          mistralKeyMasked.value = mistralData.masked
        }
      }
    }

    setTimeout(() => {
      saveMessage.value = ''
    }, 3000)

  } catch (e) {
    saveMessage.value = 'Error: ' + e.message
    saveSuccess.value = false
  } finally {
    saveInProgress.value = false
  }
}

async function checkAuth() {
  try {
    const response = await fetch('/api/settings/check-auth', {
      credentials: 'include'
    })
    if (response.ok) {
      const data = await response.json()
      authenticated.value = data.authenticated
      if (!authenticated.value) {
        showAuthModal.value = true
      } else {
        // Load settings only if authenticated
        loadSettings()
      }
    } else {
      showAuthModal.value = true
    }
  } catch (e) {
    console.error('Auth check failed:', e)
    showAuthModal.value = true
  }
}

function onAuthenticated() {
  authenticated.value = true
  showAuthModal.value = false
  // Load settings after authentication
  loadSettings()
  // Session 133: Load Ollama models for dropdown (no auth required)
  loadOllamaModels()
}

onMounted(() => {
  checkAuth()
  // Detect GPU immediately (no auth required)
  detectGpu()
})
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.settings-container {
  min-height: 100vh;
  background: #000;
  padding: 20px;
  padding-bottom: 120px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
  color: #fff;
}

.settings-header {
  border-bottom: 2px solid #ccc;
  margin-bottom: 20px;
  background: #fff;
  border: 1px solid #ccc;
}

.settings-header h1 {
  margin: 0;
  padding: 15px 15px 0 15px;
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.tabs {
  display: flex;
  gap: 0;
  padding: 0 15px;
  margin-top: 10px;
}

.tab-btn {
  padding: 10px 20px;
  background: #e0e0e0;
  border: 1px solid #ccc;
  border-bottom: none;
  cursor: pointer;
  font-size: 14px;
  color: #666;
  font-weight: 500;
  transition: all 0.2s;
}

.tab-btn:hover {
  background: #d0d0d0;
}

.tab-btn.active {
  background: #fff;
  color: #333;
  font-weight: 600;
  border-top: 3px solid #007bff;
  padding-top: 8px;
}

.loading, .error {
  padding: 15px;
  background: #fff;
  border: 1px solid #ccc;
  margin-bottom: 20px;
  color: #333;
}

.error {
  color: #c00;
}

.settings-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section {
  background: #fff;
  border: 1px solid #ccc;
  padding: 15px;
}

.section h2 {
  margin: 0 0 10px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.section .help {
  margin: 0 0 10px 0;
  font-size: 13px;
  color: #666;
}

.config-table {
  width: 100%;
  border-collapse: collapse;
  border: 1px solid #999;
}

.config-table tr {
  border-bottom: 1px solid #999;
}

.config-table tr:last-child {
  border-bottom: none;
}

.label-cell {
  width: 250px;
  padding: 8px 12px;
  background: #f0f0f0;
  font-weight: 500;
  font-size: 13px;
  color: #000;
  vertical-align: middle;
  text-align: left;
  border-right: 1px solid #999;
}

.value-cell {
  padding: 8px 12px;
  background: #fff;
  text-align: left;
  color: #000;
}

.value-cell select,
.value-cell input.text-input {
  padding: 6px 8px;
  border: 1px solid #ccc;
  font-size: 13px;
  font-family: monospace;
  background: white;
  color: #000;
  width: 100%;
  max-width: 600px;
}

.value-cell input[type="radio"] {
  margin-right: 5px;
}

.value-cell label {
  margin-right: 15px;
  color: #000;
}

.help-text {
  margin-left: 10px;
  color: #666;
  font-size: 12px;
}

.action-btn {
  background: #555;
  color: #fff;
  border: 1px solid #999;
  padding: 8px 16px;
  font-size: 13px;
  cursor: pointer;
  font-weight: 500;
}

.action-btn:hover {
  background: #777;
}

.button-row {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: #fff;
  border: 1px solid #ccc;
}

.save-btn {
  background: #666;
  color: #fff;
  border: 1px solid #999;
  padding: 8px 20px;
  font-size: 14px;
  cursor: pointer;
  font-weight: 500;
}

.save-btn:hover {
  background: #888;
}

.apply-btn {
  background: #4a90e2;
  color: #fff;
  border: 1px solid #3a7bc8;
  padding: 8px 20px;
  font-size: 14px;
  cursor: pointer;
  font-weight: 500;
  margin-left: 10px;
}

.apply-btn:hover:not(:disabled) {
  background: #3a7bc8;
}

.apply-btn:disabled {
  background: #999;
  cursor: not-allowed;
  opacity: 0.6;
}

.save-message {
  font-size: 13px;
  color: #333;
}

.error-message {
  color: #c00;
}

.info-note {
  padding: 10px 12px;
  background: #f0f0f0;
  border: 1px solid #999;
  font-size: 12px;
  color: #333;
}

.info-box {
  padding: 12px 15px;
  background: #fff4e6;
  border: 1px solid #ffa500;
  border-left: 4px solid #ffa500;
  border-radius: 4px;
  font-size: 13px;
  color: #333;
  line-height: 1.5;
}

.info-box-success {
  background: #e6f7e6;
  border-color: #4CAF50;
  border-left-color: #4CAF50;
}

.info-box strong {
  display: block;
  margin-bottom: 8px;
  color: #000;
  font-size: 14px;
}

.info-box p {
  margin: 6px 0;
}

.info-box code {
  background: rgba(0, 0, 0, 0.05);
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
}

.info-box ul {
  margin: 8px 0;
  padding-left: 20px;
}

.info-box li {
  margin: 4px 0;
}

.gpu-detected {
  color: #2e7d32 !important;
  font-weight: 500;
}

.gpu-error {
  color: #f57c00 !important;
}
</style>
