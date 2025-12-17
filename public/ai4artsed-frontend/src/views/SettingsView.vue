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
          <tr>
            <td class="label-cell">DSGVO Conformity</td>
            <td class="value-cell">
              <label style="display: flex; align-items: center; gap: 8px;">
                <input type="checkbox" v-model="settings.DSGVO_CONFORMITY" style="width: auto;" />
                <span><strong>Strenge Datenlokalisierung (nur lokale Modelle)</strong></span>
              </label>
              <div style="margin-top: 8px; padding: 8px; background: #f5f5f5; border-left: 3px solid #2196F3; font-size: 12px;">
                <p style="margin: 4px 0;"><strong>Wenn aktiviert:</strong></p>
                <ul style="margin: 6px 0 0 20px; padding: 0;">
                  <li>Alle Daten verbleiben auf Ihrem Server (lokale Modelle via Ollama)</li>
                  <li>Maximaler Datenschutz - keine externe Verarbeitung</li>
                  <li>Ideal für: Schulen, Behörden, sensible personenbezogene Daten</li>
                </ul>
                <p style="margin: 8px 0 4px 0;"><strong>Wenn deaktiviert:</strong></p>
                <ul style="margin: 6px 0 0 20px; padding: 0;">
                  <li>Cloud-Dienste erlaubt (OpenRouter, Anthropic EU, OpenAI)</li>
                  <li>Bessere Performance, aber Daten verlassen Ihren Server</li>
                  <li><em>Hinweis: DSGVO-konforme EU-Dienste wie Anthropic EU sind rechtlich zulässig</em></li>
                </ul>
                <p style="margin: 8px 0 0 0; font-size: 11px; color: #666;"><strong>Rechtlicher Hinweis:</strong> Diese Einstellung betrifft die technische Datenlokalisierung. DSGVO-Compliance erfordert zusätzliche organisatorische Maßnahmen (Verträge, Dokumentation, etc.).</p>
              </div>
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

        <!-- Data Localization Validation Warning -->
        <div v-if="settings.DSGVO_CONFORMITY && hasCloudModels" class="info-box" style="background: #fff3cd; border-color: #ff9800; border-left-color: #ff9800; margin-bottom: 15px;">
          <strong>⚠️ Datenlokalisierungs-Warnung</strong>
          <p>Sie haben <strong>"Strenge Datenlokalisierung"</strong> aktiviert, verwenden aber Cloud-Modelle in der Konfiguration.</p>
          <p><strong>Gefundene Cloud-Modelle:</strong></p>
          <ul style="margin: 8px 0; padding-left: 20px;">
            <li v-for="model in cloudModelsDetected" :key="model">{{ model }}</li>
          </ul>
          <p style="margin-top: 8px;"><strong>Optionen:</strong></p>
          <ol style="margin: 4px 0 0 20px; padding: 0;">
            <li>Ersetzen Sie diese durch lokale Modelle (Präfix: <code>local/</code>)</li>
            <li>ODER deaktivieren Sie "Strenge Datenlokalisierung", wenn Sie DSGVO-konforme Cloud-Dienste (z.B. Anthropic EU) verwenden möchten</li>
          </ol>
        </div>

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
            <td class="label-cell">External LLM Provider</td>
            <td class="value-cell">
              <select v-model="settings.EXTERNAL_LLM_PROVIDER">
                <option value="none">None (Local only)</option>
                <option value="openrouter">OpenRouter</option>
                <option value="anthropic">Anthropic (EU servers available)</option>
                <option value="openai">OpenAI</option>
              </select>
              <span class="help-text">Cloud-based LLM service (requires API key)</span>

              <!-- DSGVO-aware help text -->
              <div v-if="settings.DSGVO_CONFORMITY && settings.EXTERNAL_LLM_PROVIDER !== 'none'" class="info-box" style="margin-top: 12px;">
                <strong>💡 DSGVO-Hinweis:</strong>
                <p>Sie haben strenge Datenlokalisierung aktiviert, aber einen Cloud-Anbieter ausgewählt.</p>
                <div v-if="settings.EXTERNAL_LLM_PROVIDER === 'anthropic'">
                  <p><strong>Anthropic (Direkt-API):</strong> Bietet DSGVO-konforme EU-Server. Modell-Ersetzungen:</p>
                  <ul style="margin-left: 20px; margin-top: 8px;">
                    <li><strong>Vision:</strong> <code>local/llama3.2-vision:90b</code> → <code>anthropic/claude-3.5-sonnet</code> (hat Vision)</li>
                    <li><strong>Text:</strong> <code>local/llama3.1:70b</code> → <code>anthropic/claude-sonnet-4</code> (nur Text)</li>
                  </ul>
                </div>
                <div v-else-if="settings.EXTERNAL_LLM_PROVIDER === 'openrouter'">
                  <p><strong>OpenRouter (Proxy):</strong> Syntax mit Proxy-Präfix:</p>
                  <ul style="margin-left: 20px; margin-top: 8px;">
                    <li><strong>Vision:</strong> <code>local/llama3.2-vision:90b</code> → <code>openrouter/anthropic/claude-3.5-sonnet</code></li>
                    <li><strong>Text:</strong> <code>local/llama3.1:70b</code> → <code>openrouter/anthropic/claude-sonnet-4</code></li>
                  </ul>
                </div>
                <p style="margin-top: 8px;"><strong>Tipp:</strong> Ändern Sie die Modell-Strings in der "Model Configuration" Sektion.</p>
              </div>

              <div v-else-if="!settings.DSGVO_CONFORMITY && settings.EXTERNAL_LLM_PROVIDER !== 'none'" class="info-box" style="margin-top: 12px;">
                <strong>☁️ Cloud-Anbieter aktiv</strong>
                <p>Sie können lokale Modelle durch Cloud-Modelle ersetzen. <strong>Wichtig:</strong> Vision-Modelle nur durch Vision-fähige Modelle ersetzen!</p>
                <div v-if="settings.EXTERNAL_LLM_PROVIDER === 'anthropic'">
                  <p><strong>Anthropic Direkt-API (ohne Proxy):</strong></p>
                  <ul style="margin-left: 20px; margin-top: 8px;">
                    <li><strong>Vision:</strong> <code>local/llama3.2-vision:90b</code> → <code>anthropic/claude-3.5-sonnet</code></li>
                    <li><strong>Text:</strong> <code>local/llama3.1:70b</code> → <code>anthropic/claude-sonnet-4</code></li>
                  </ul>
                </div>
                <div v-else-if="settings.EXTERNAL_LLM_PROVIDER === 'openrouter'">
                  <p><strong>OpenRouter Proxy (alle Anbieter über OpenRouter):</strong></p>
                  <ul style="margin-left: 20px; margin-top: 8px;">
                    <li><strong>Vision:</strong> <code>local/llama3.2-vision:90b</code> → <code>openrouter/anthropic/claude-3.5-sonnet</code></li>
                    <li><strong>Text:</strong> <code>local/llama3.1:70b</code> → <code>openrouter/anthropic/claude-sonnet-4</code></li>
                  </ul>
                </div>
                <div v-else-if="settings.EXTERNAL_LLM_PROVIDER === 'openai'">
                  <p><strong>OpenAI Direkt-API:</strong></p>
                  <ul style="margin-left: 20px; margin-top: 8px;">
                    <li><strong>Vision:</strong> <code>local/llama3.2-vision:90b</code> → <code>openai/gpt-4-vision</code></li>
                    <li><strong>Text:</strong> <code>local/llama3.1:70b</code> → <code>openai/gpt-4-turbo</code></li>
                  </ul>
                </div>
              </div>

              <div v-else-if="settings.DSGVO_CONFORMITY && settings.EXTERNAL_LLM_PROVIDER === 'none'" class="info-box info-box-success" style="margin-top: 12px;">
                <strong>✓ DSGVO-konform</strong>
                <p>Alle Modelle laufen lokal über Ollama. Keine Daten verlassen Ihren Server.</p>
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
import { ref, computed, onMounted } from 'vue'

const loading = ref(true)
const error = ref(null)
const settings = ref({})
const matrix = ref({})
const selectedVramTier = ref('vram_24')
const selectedDsgvoMode = ref('non_dsgvo')
const openrouterKey = ref('')
const openrouterKeyMasked = ref('')
const anthropicKey = ref('')
const anthropicKeyMasked = ref('')
const openaiKey = ref('')
const openaiKeyMasked = ref('')
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

async function loadSettings() {
  try {
    loading.value = true
    error.value = null

    // Load current settings and matrix
    const response = await fetch('/api/settings', {
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

  // Fill model fields from preset
  Object.keys(modelLabels).forEach(key => {
    if (presetModels[key]) {
      settings.value[key] = presetModels[key]
    }
  })

  // Fill EXTERNAL_LLM_PROVIDER and DSGVO_CONFORMITY from preset
  if (preset.EXTERNAL_LLM_PROVIDER !== undefined) {
    settings.value.EXTERNAL_LLM_PROVIDER = preset.EXTERNAL_LLM_PROVIDER
  }
  if (preset.DSGVO_CONFORMITY !== undefined) {
    settings.value.DSGVO_CONFORMITY = preset.DSGVO_CONFORMITY
  }

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

    const response = await fetch('/api/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(payload)
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    const data = await response.json()
    saveMessage.value = '✓ ' + data.message
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
</style>
