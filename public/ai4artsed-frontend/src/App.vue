<template>
  <div id="app">
    <header class="app-header">
      <h1>{{ $t('app.title') }}</h1>
      <p class="subtitle">{{ $t('app.subtitle') }}</p>
      <button @click="toggleLanguage" class="lang-toggle">
        {{ $t('language.switchTo') }}
      </button>
    </header>

    <main class="app-main">
      <form @submit.prevent="executePipeline" class="generation-form">
        <div class="form-group">
          <label>{{ $t('form.inputLabel') }}</label>
          <textarea
            v-model="formData.input_text"
            :placeholder="$t('form.inputPlaceholder')"
            rows="3"
            required
          ></textarea>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>{{ $t('form.schemaLabel') }}</label>
            <select v-model="formData.schema" required>
              <option value="dada">{{ $t('schemas.dada') }}</option>
              <option value="bauhaus">{{ $t('schemas.bauhaus') }}</option>
              <option value="stillepost">{{ $t('schemas.stillepost') }}</option>
            </select>
          </div>

          <div class="form-group">
            <label>{{ $t('form.executeModeLabel') }}</label>
            <select v-model="formData.execution_mode">
              <option value="eco">{{ $t('executionModes.eco') }}</option>
              <option value="fast">{{ $t('executionModes.fast') }}</option>
              <option value="best">{{ $t('executionModes.best') }}</option>
            </select>
          </div>

          <div class="form-group">
            <label>{{ $t('form.safetyLabel') }}</label>
            <select v-model="formData.safety_level">
              <option value="kids">{{ $t('safetyLevels.kids') }}</option>
              <option value="youth">{{ $t('safetyLevels.youth') }}</option>
              <option value="adult">{{ $t('safetyLevels.adult') }}</option>
            </select>
          </div>
        </div>

        <button type="submit" class="generate-btn" :disabled="isExecuting">
          {{ $t('form.generateButton') }}
        </button>
      </form>

      <WorkflowVisualization
        v-if="isExecuting || workflowStages.length > 0"
        :stages="workflowStages"
        :statusMessage="statusMessage"
        :statusType="statusType"
      />

      <div v-if="generatedImage" class="result-container">
        <h3>{{ $t('entities.media') }}</h3>
        <img :src="generatedImage" alt="Generated result" class="generated-image" />
      </div>
    </main>
  </div>
</template>

<script>
import WorkflowVisualization from './components/WorkflowVisualization.vue'
import { useI18n } from 'vue-i18n'

export default {
  name: 'App',
  components: {
    WorkflowVisualization
  },
  setup() {
    const { locale } = useI18n()
    return { locale }
  },
  data() {
    return {
      formData: {
        input_text: '',
        schema: 'dada',
        execution_mode: 'eco',
        safety_level: 'kids'
      },
      isExecuting: false,
      workflowStages: [],
      statusMessage: '',
      statusType: 'info',
      generatedImage: null,
      pollInterval: null,
      errorCount: 0,
      errorStartTime: null
    }
  },
  methods: {
    toggleLanguage() {
      this.locale = this.locale === 'de' ? 'en' : 'de'
    },

    async executePipeline() {
      this.isExecuting = true
      this.workflowStages = []
      this.statusMessage = ''
      this.generatedImage = null
      this.errorCount = 0
      this.errorStartTime = null

      try {
        const response = await fetch('/api/schema/pipeline/execute', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.formData)
        })

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`)
        }

        const result = await response.json()
        console.log('[EXECUTE] Result:', result)

        if (result.run_id) {
          this.startPolling(result.run_id)
        } else {
          this.statusMessage = this.$t('status.error')
          this.statusType = 'error'
          this.isExecuting = false
        }
      } catch (error) {
        console.error('[EXECUTE] Error:', error)
        this.statusMessage = this.$t('status.error')
        this.statusType = 'error'
        this.isExecuting = false
      }
    },

    startPolling(runId) {
      console.log(`[POLLING] Starting for run_id: ${runId}`)

      this.pollInterval = setInterval(async () => {
        try {
          const response = await fetch(`/api/pipeline/${runId}/status`)

          if (!response.ok) {
            this.handlePollError()
            return
          }

          if (this.errorCount > 0) {
            console.log(`[POLLING] Recovered after ${this.errorCount} errors`)
            this.errorCount = 0
            this.errorStartTime = null
            this.statusMessage = ''
          }

          const statusData = await response.json()
          this.updateWorkflow(statusData)

          if (statusData.current_state && statusData.current_state.stage === 'completed') {
            this.handleCompletion(runId)
          }
        } catch (error) {
          this.handlePollError()
        }
      }, 1000)
    },

    handlePollError() {
      this.errorCount++
      if (this.errorCount === 1) {
        this.errorStartTime = Date.now()
      }
      const duration = Math.floor((Date.now() - this.errorStartTime) / 1000)
      this.statusMessage = `${this.$t('status.connectionSlow')} (${duration}s)`
      this.statusType = 'warning'
    },

    updateWorkflow(statusData) {
      if (!statusData.current_state) return

      const currentStage = statusData.current_state.stage
      const currentStep = statusData.current_state.step
      const progress = statusData.current_state.progress

      const stageId = currentStage || 'pipeline_starting'

      const existingStage = this.workflowStages.find(s => s.id === stageId)
      if (!existingStage) {
        this.workflowStages.push({
          id: stageId,
          status: 'active',
          progress: progress
        })
      } else {
        existingStage.progress = progress
        existingStage.status = progress === 100 ? 'completed' : 'active'
      }

      this.workflowStages.forEach(stage => {
        if (stage.id !== stageId && stage.progress === 100) {
          stage.status = 'completed'
        }
      })
    },

    handleCompletion(runId) {
      clearInterval(this.pollInterval)
      this.isExecuting = false
      this.statusMessage = this.$t('status.completed')
      this.statusType = 'success'

      this.workflowStages.forEach(stage => {
        stage.status = 'completed'
        stage.progress = 100
      })

      this.fetchGeneratedImage(runId)
    },

    async fetchGeneratedImage(runId) {
      try {
        const response = await fetch(`/api/pipeline/${runId}/status`)
        const statusData = await response.json()

        if (statusData.entities) {
          const mediaEntity = statusData.entities.find(e => e.type === 'media')
          if (mediaEntity && mediaEntity.data && mediaEntity.data.prompt_id) {
            this.generatedImage = `/api/media/image/${mediaEntity.data.prompt_id}`
          }
        }
      } catch (error) {
        console.error('[FETCH-IMAGE] Error:', error)
      }
    }
  },

  beforeUnmount() {
    if (this.pollInterval) {
      clearInterval(this.pollInterval)
    }
  }
}
</script>

<style>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

#app {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

.app-header {
  text-align: center;
  color: white;
  margin-bottom: 2rem;
  position: relative;
}

.app-header h1 {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.subtitle {
  font-size: 1.1rem;
  opacity: 0.9;
}

.lang-toggle {
  position: absolute;
  top: 0;
  right: 0;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.lang-toggle:hover {
  background: rgba(255, 255, 255, 0.3);
}

.app-main {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
}

.generation-form {
  margin-bottom: 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #333;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 1rem;
  font-family: inherit;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: #667eea;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.generate-btn {
  width: 100%;
  padding: 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.generate-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.generate-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.result-container {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 2px solid #f0f0f0;
}

.result-container h3 {
  margin-bottom: 1rem;
  color: #333;
}

.generated-image {
  max-width: 100%;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
</style>
