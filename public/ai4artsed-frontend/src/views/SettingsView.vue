<template>
  <div class="settings-container">
    <div class="settings-header">
      <h1>Configuration Settings</h1>
    </div>

    <div v-if="loading" class="loading">Loading settings...</div>
    <div v-else-if="error" class="error">Error: {{ error }}</div>

    <div v-else class="settings-content">
      <!-- Hardware Quick-Fill Section -->
      <div class="section">
        <h2>Hardware Quick-Fill (Optional)</h2>
        <p class="help">Select preset to auto-fill model fields based on your hardware</p>

        <table class="config-table">
          <tr>
            <td class="label-cell">Graphic Card Memory (VRAM)</td>
            <td class="value-cell">
              <select v-model="selectedVramTier">
                <option value="vram_96">96 GB</option>
                <option value="vram_32">32 GB</option>
                <option value="vram_24">24 GB</option>
                <option value="vram_16">16 GB</option>
                <option value="vram_8">8 GB</option>
              </select>
            </td>
          </tr>
          <tr>
            <td class="label-cell">DSGVO Mode</td>
            <td class="value-cell">
              <label><input type="radio" v-model="selectedDsgvoMode" value="dsgvo_compliant" /> DSGVO-compliant</label>
              <label><input type="radio" v-model="selectedDsgvoMode" value="non_dsgvo" /> Non-DSGVO (Cloud allowed)</label>
            </td>
          </tr>
          <tr>
            <td colspan="2" style="text-align: center; padding: 12px;">
              <button @click="fillFromPreset" class="action-btn">Fill Model Fields from Preset</button>
            </td>
          </tr>
        </table>
      </div>

      <!-- General Settings -->
      <div class="section">
        <h2>General Settings</h2>
        <table class="config-table">
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
        </table>
      </div>

      <!-- Server Settings -->
      <div class="section">
        <h2>Server Settings</h2>
        <table class="config-table">
          <tr>
            <td class="label-cell">Host</td>
            <td class="value-cell">
              <input type="text" v-model="settings.HOST" class="text-input" />
            </td>
          </tr>
          <tr>
            <td class="label-cell">Port</td>
            <td class="value-cell">
              <input type="number" v-model.number="settings.PORT" class="text-input" />
            </td>
          </tr>
          <tr>
            <td class="label-cell">Threads</td>
            <td class="value-cell">
              <input type="number" v-model.number="settings.THREADS" class="text-input" />
            </td>
          </tr>
        </table>
      </div>

      <!-- Model Configuration -->
      <div class="section">
        <h2>Model Configuration</h2>
        <p class="help">Model identifiers with provider prefix (ollama/, openrouter/, local/)</p>
        <table class="config-table">
          <tr v-for="(label, key) in modelLabels" :key="key">
            <td class="label-cell">{{ label }}</td>
            <td class="value-cell">
              <input type="text" v-model="settings[key]" class="text-input" />
            </td>
          </tr>
        </table>
      </div>

      <!-- API Configuration -->
      <div class="section">
        <h2>API Configuration</h2>
        <table class="config-table">
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
        </table>
      </div>

      <!-- Save Button -->
      <div class="button-row">
        <button @click="saveSettings" class="save-btn">Save Configuration</button>
        <span v-if="saveMessage" :class="{'save-message': true, 'error-message': !saveSuccess}">
          {{ saveMessage }}
        </span>
      </div>

      <div class="info-note">
        Note: Backend restart required after saving changes.
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const loading = ref(true)
const error = ref(null)
const settings = ref({})
const matrix = ref({})
const selectedVramTier = ref('vram_24')
const selectedDsgvoMode = ref('non_dsgvo')
const openrouterKey = ref('')
const openrouterKeyMasked = ref('')
const saveMessage = ref('')
const saveSuccess = ref(true)

const modelLabels = {
  'STAGE1_TEXT_MODEL': 'Stage 1 - Text Model',
  'STAGE1_VISION_MODEL': 'Stage 1 - Vision Model',
  'STAGE2_INTERCEPTION_MODEL': 'Stage 2 - Interception Model',
  'STAGE2_OPTIMIZATION_MODEL': 'Stage 2 - Optimization Model',
  'STAGE3_MODEL': 'Stage 3 - Translation/Safety Model',
  'STAGE4_LEGACY_MODEL': 'Stage 4 - Legacy Model',
  'CHAT_HELPER_MODEL': 'Chat Helper Model',
  'IMAGE_ANALYSIS_MODEL': 'Image Analysis Model'
}

async function loadSettings() {
  try {
    loading.value = true
    error.value = null

    // Load current settings and matrix
    const response = await fetch('/api/settings')
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    const data = await response.json()
    settings.value = data.current
    matrix.value = data.matrix

    // Load OpenRouter key status
    const keyResponse = await fetch('/api/settings/openrouter-key')
    if (keyResponse.ok) {
      const keyData = await keyResponse.json()
      if (keyData.exists) {
        openrouterKeyMasked.value = keyData.masked
      }
    }

  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

function fillFromPreset() {
  if (!matrix.value[selectedVramTier.value] || !matrix.value[selectedVramTier.value][selectedDsgvoMode.value]) {
    saveMessage.value = 'Preset not found'
    saveSuccess.value = false
    setTimeout(() => { saveMessage.value = '' }, 3000)
    return
  }

  const preset = matrix.value[selectedVramTier.value][selectedDsgvoMode.value]
  const presetModels = preset.models

  // Fill only model fields from preset
  Object.keys(modelLabels).forEach(key => {
    if (presetModels[key]) {
      settings.value[key] = presetModels[key]
    }
  })

  saveMessage.value = `✓ Filled from: ${preset.label}`
  saveSuccess.value = true
  setTimeout(() => { saveMessage.value = '' }, 3000)
}

async function saveSettings() {
  try {
    saveMessage.value = 'Saving...'
    saveSuccess.value = true

    // Build payload
    const payload = { ...settings.value }

    // Add OpenRouter key if provided
    if (openrouterKey.value) {
      payload.OPENROUTER_API_KEY = openrouterKey.value
    }

    const response = await fetch('/api/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    const data = await response.json()
    saveMessage.value = '✓ ' + data.message
    saveSuccess.value = true

    // Clear OpenRouter key input after successful save
    if (openrouterKey.value) {
      openrouterKey.value = ''
      // Reload to get new masked key
      const keyResponse = await fetch('/api/settings/openrouter-key')
      if (keyResponse.ok) {
        const keyData = await keyResponse.json()
        if (keyData.exists) {
          openrouterKeyMasked.value = keyData.masked
        }
      }
    }

    setTimeout(() => {
      saveMessage.value = ''
    }, 5000)

  } catch (e) {
    saveMessage.value = 'Error: ' + e.message
    saveSuccess.value = false
  }
}

onMounted(() => {
  loadSettings()
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
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
  color: #fff;
}

.settings-header {
  border-bottom: 2px solid #ccc;
  padding-bottom: 10px;
  margin-bottom: 20px;
  background: #fff;
  padding: 15px;
  border: 1px solid #ccc;
}

.settings-header h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #333;
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
</style>
