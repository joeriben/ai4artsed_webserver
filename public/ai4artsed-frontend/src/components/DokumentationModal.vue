<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="modelValue" class="modal-overlay" @click="closeModal">
        <div class="modal-container" @click.stop>
          <div class="modal-header">
            <h1>{{ $t('docs.title') }}</h1>
            <button class="modal-close" @click="closeModal" :title="$t('common.back')">×</button>
          </div>

          <!-- Tab Navigation -->
          <div class="tab-nav">
            <button
              v-for="tab in tabs"
              :key="tab.id"
              :class="['tab-button', { active: activeTab === tab.id }]"
              @click="activeTab = tab.id"
            >
              <span class="tab-icon" v-html="tab.icon"></span>
              {{ currentLanguage === 'de' ? tab.labelDe : tab.labelEn }}
            </button>
          </div>

          <div class="modal-body">
            <!-- Welcome Tab -->
            <div v-if="activeTab === 'welcome'" class="tab-content">
              <section class="welcome-section">
                <div class="trashy-welcome">
                  <img :src="trashyIcon" alt="Träshy" class="trashy-icon-large" />
                  <div class="welcome-text">
                    <h2>{{ currentLanguage === 'de' ? 'Hallo, ich bin Träshy!' : 'Hello, I\'m Träshy!' }}</h2>
                    <p>{{ currentLanguage === 'de'
                      ? 'Dein KI-Helfer für kreative Experimente. Ich helfe dir dabei, mit künstlicher Intelligenz Kunst zu erschaffen.'
                      : 'Your AI helper for creative experiments. I help you create art with artificial intelligence.' }}</p>
                  </div>
                </div>
              </section>

              <section class="info-section">
                <h3>{{ currentLanguage === 'de' ? 'Was ist AI4ArtsEd?' : 'What is AI4ArtsEd?' }}</h3>
                <p>{{ currentLanguage === 'de'
                  ? 'AI4ArtsEd ist eine pädagogisch-künstlerische Experimentierplattform. Sie wurde entwickelt, um den kreativen Einsatz von KI in der kulturellen Bildung zu erforschen und zu ermöglichen.'
                  : 'AI4ArtsEd is a pedagogical-artistic experimentation platform. It was developed to explore and enable the creative use of AI in cultural education.' }}</p>
              </section>

              <section class="info-section">
                <h3>{{ currentLanguage === 'de' ? 'Wie funktioniert es?' : 'How does it work?' }}</h3>
                <div class="flow-diagram">
                  <div class="flow-step">
                    <span class="step-number">1</span>
                    <span class="step-text">{{ currentLanguage === 'de' ? 'Eingabe' : 'Input' }}</span>
                  </div>
                  <span class="flow-arrow">→</span>
                  <div class="flow-step">
                    <span class="step-number">2</span>
                    <span class="step-text">{{ currentLanguage === 'de' ? 'Transformation' : 'Transformation' }}</span>
                  </div>
                  <span class="flow-arrow">→</span>
                  <div class="flow-step">
                    <span class="step-number">3</span>
                    <span class="step-text">{{ currentLanguage === 'de' ? 'Optimierung' : 'Optimization' }}</span>
                  </div>
                  <span class="flow-arrow">→</span>
                  <div class="flow-step">
                    <span class="step-number">4</span>
                    <span class="step-text">{{ currentLanguage === 'de' ? 'Generierung' : 'Generation' }}</span>
                  </div>
                </div>
                <p class="flow-description">{{ currentLanguage === 'de'
                  ? 'Deine Idee wird durch mehrere Stufen transformiert und optimiert, bevor das finale Bild, Video oder Audio erstellt wird.'
                  : 'Your idea is transformed and optimized through multiple stages before the final image, video, or audio is created.' }}</p>
              </section>
            </div>

            <!-- Getting Started Tab -->
            <div v-if="activeTab === 'start'" class="tab-content">
              <section class="guide-section">
                <h2>{{ currentLanguage === 'de' ? 'Erste Schritte' : 'Getting Started' }}</h2>

                <div class="step-card">
                  <div class="step-header">
                    <span class="step-badge">1</span>
                    <h3>{{ currentLanguage === 'de' ? 'Eigenschaften wählen' : 'Choose Properties' }}</h3>
                  </div>
                  <p>{{ currentLanguage === 'de'
                    ? 'Wähle in den vier Quadranten die Eigenschaften, die dein Kunstwerk haben soll. Jeder Quadrant bietet verschiedene Stile und Herangehensweisen.'
                    : 'Choose properties in the four quadrants that your artwork should have. Each quadrant offers different styles and approaches.' }}</p>
                  <div class="property-preview">
                    <span class="property-tag">🎨 {{ currentLanguage === 'de' ? 'Ästhetik' : 'Aesthetics' }}</span>
                    <span class="property-tag">📐 {{ currentLanguage === 'de' ? 'Komposition' : 'Composition' }}</span>
                    <span class="property-tag">💭 {{ currentLanguage === 'de' ? 'Konzept' : 'Concept' }}</span>
                    <span class="property-tag">🎭 {{ currentLanguage === 'de' ? 'Emotion' : 'Emotion' }}</span>
                  </div>
                </div>

                <div class="step-card">
                  <div class="step-header">
                    <span class="step-badge">2</span>
                    <h3>{{ currentLanguage === 'de' ? 'Deine Idee eingeben' : 'Enter Your Idea' }}</h3>
                  </div>
                  <p>{{ currentLanguage === 'de'
                    ? 'Beschreibe WAS du erschaffen möchtest. Das kann ein Text sein, eine Szene, ein Gefühl – sei kreativ!'
                    : 'Describe WHAT you want to create. This can be text, a scene, a feeling – be creative!' }}</p>
                  <div class="example-box">
                    <strong>{{ currentLanguage === 'de' ? 'Beispiel:' : 'Example:' }}</strong>
                    <span>{{ currentLanguage === 'de' ? '"Ein Fest in meiner Straße mit bunten Luftballons"' : '"A festival in my street with colorful balloons"' }}</span>
                  </div>
                </div>

                <div class="step-card">
                  <div class="step-header">
                    <span class="step-badge">3</span>
                    <h3>{{ currentLanguage === 'de' ? 'Regeln definieren (optional)' : 'Define Rules (optional)' }}</h3>
                  </div>
                  <p>{{ currentLanguage === 'de'
                    ? 'Bestimme WIE deine Idee umgesetzt werden soll. Hier kannst du besondere Anweisungen oder Perspektiven angeben.'
                    : 'Determine HOW your idea should be implemented. Here you can specify special instructions or perspectives.' }}</p>
                  <div class="example-box">
                    <strong>{{ currentLanguage === 'de' ? 'Beispiel:' : 'Example:' }}</strong>
                    <span>{{ currentLanguage === 'de' ? '"Beschreibe alles so, wie es die Vögel auf den Bäumen wahrnehmen"' : '"Describe everything as the birds in the trees perceive it"' }}</span>
                  </div>
                </div>

                <div class="step-card">
                  <div class="step-header">
                    <span class="step-badge">4</span>
                    <h3>{{ currentLanguage === 'de' ? 'Transformation starten' : 'Start Transformation' }}</h3>
                  </div>
                  <p>{{ currentLanguage === 'de'
                    ? 'Klicke auf "Start!" und beobachte, wie die KI deine Eingabe in einen kreativen Prompt verwandelt.'
                    : 'Click "Start!" and watch how the AI transforms your input into a creative prompt.' }}</p>
                </div>

                <div class="step-card">
                  <div class="step-header">
                    <span class="step-badge">5</span>
                    <h3>{{ currentLanguage === 'de' ? 'Medium wählen und generieren' : 'Choose Medium and Generate' }}</h3>
                  </div>
                  <p>{{ currentLanguage === 'de'
                    ? 'Wähle ob du ein Bild, Video oder Audio erstellen möchtest und starte die Generierung.'
                    : 'Choose whether you want to create an image, video or audio and start the generation.' }}</p>
                </div>
              </section>
            </div>

            <!-- Workflows Tab -->
            <div v-if="activeTab === 'workflows'" class="tab-content">
              <section class="workflows-section">
                <h2>{{ currentLanguage === 'de' ? 'Verfügbare Workflows' : 'Available Workflows' }}</h2>

                <div class="workflow-card">
                  <div class="workflow-header">
                    <span class="workflow-icon">📝</span>
                    <h3>{{ currentLanguage === 'de' ? 'Text-Transformation' : 'Text Transformation' }}</h3>
                    <span class="workflow-tag main">{{ currentLanguage === 'de' ? 'Haupt' : 'Main' }}</span>
                  </div>
                  <p>{{ currentLanguage === 'de'
                    ? 'Der Standardworkflow: Dein Text wird durch KI künstlerisch transformiert und dann in ein Bild umgewandelt.'
                    : 'The standard workflow: Your text is artistically transformed by AI and then converted into an image.' }}</p>
                  <div class="workflow-flow">
                    <span>Text</span> → <span>Transformation</span> → <span>Optimierung</span> → <span>Bild</span>
                  </div>
                </div>

                <div class="workflow-card">
                  <div class="workflow-header">
                    <span class="workflow-icon">🖼️</span>
                    <h3>{{ currentLanguage === 'de' ? 'Bild-Transformation' : 'Image Transformation' }}</h3>
                    <span class="workflow-tag main">{{ currentLanguage === 'de' ? 'Haupt' : 'Main' }}</span>
                  </div>
                  <p>{{ currentLanguage === 'de'
                    ? 'Lade ein Bild hoch und beschreibe, wie du es verändern möchtest. Die KI interpretiert dein Bild neu.'
                    : 'Upload an image and describe how you want to change it. The AI reinterprets your image.' }}</p>
                  <div class="workflow-flow">
                    <span>Bild + Text</span> → <span>Vision-KI</span> → <span>Neues Bild</span>
                  </div>
                </div>

                <div class="workflow-card">
                  <div class="workflow-header">
                    <span class="workflow-icon">🎴</span>
                    <h3>{{ currentLanguage === 'de' ? 'Multi-Bild Fusion' : 'Multi-Image Fusion' }}</h3>
                    <span class="workflow-tag main">{{ currentLanguage === 'de' ? 'Haupt' : 'Main' }}</span>
                  </div>
                  <p>{{ currentLanguage === 'de'
                    ? 'Kombiniere bis zu 3 Bilder und beschreibe, wie sie verschmolzen werden sollen. Nutzt QWEN-2511 Vision.'
                    : 'Combine up to 3 images and describe how they should be merged. Uses QWEN-2511 Vision.' }}</p>
                  <div class="workflow-flow">
                    <span>3 Bilder</span> → <span>QWEN Vision</span> → <span>Fusioniertes Bild</span>
                  </div>
                </div>

                <h3 class="section-subtitle">{{ currentLanguage === 'de' ? 'Experimentelle Workflows' : 'Experimental Workflows' }}</h3>

                <div class="workflow-card legacy">
                  <div class="workflow-header">
                    <span class="workflow-icon">🌀</span>
                    <h3>Surrealizer</h3>
                    <span class="workflow-tag legacy">Legacy</span>
                  </div>
                  <p>{{ currentLanguage === 'de'
                    ? 'Dual-Encoder Fusion: Mischt CLIP und T5 Text-Encoder für surreale Ergebnisse.'
                    : 'Dual-Encoder Fusion: Mixes CLIP and T5 text encoders for surreal results.' }}</p>
                </div>

                <div class="workflow-card legacy">
                  <div class="workflow-header">
                    <span class="workflow-icon">⚡</span>
                    <h3>Split & Combine</h3>
                    <span class="workflow-tag legacy">Legacy</span>
                  </div>
                  <p>{{ currentLanguage === 'de'
                    ? 'Semantische Vektorfusion: Verschmilzt zwei Prompts auf mathematischer Ebene.'
                    : 'Semantic Vector Fusion: Merges two prompts at the mathematical level.' }}</p>
                </div>

                <div class="workflow-card legacy">
                  <div class="workflow-header">
                    <span class="workflow-icon">🔬</span>
                    <h3>Partial Elimination</h3>
                    <span class="workflow-tag legacy">Legacy</span>
                  </div>
                  <p>{{ currentLanguage === 'de'
                    ? 'Vektor-Dekonstruktion: Entfernt gezielt Teile des semantischen Vektors.'
                    : 'Vector Deconstruction: Specifically removes parts of the semantic vector.' }}</p>
                </div>
              </section>
            </div>

            <!-- What's New Tab -->
            <div v-if="activeTab === 'whatsNew'" class="tab-content">
              <section class="whats-new-section">
                <h2>{{ currentLanguage === 'de' ? 'Neu im Januar 2026' : 'New in January 2026' }}</h2>

                <div class="feature-card highlight">
                  <div class="feature-header">
                    <span class="feature-icon">🎨</span>
                    <h3>LoRA Training Studio</h3>
                  </div>
                  <p>{{ currentLanguage === 'de'
                    ? 'Trainiere deine eigenen künstlerischen Stile! Lade 5-20 Beispielbilder hoch, wähle ein Trigger-Wort, und die KI lernt deinen einzigartigen Stil.'
                    : 'Train your own artistic styles! Upload 5-20 example images, choose a trigger word, and the AI learns your unique style.' }}</p>
                </div>

                <div class="feature-card">
                  <div class="feature-header">
                    <span class="feature-icon">🖼️</span>
                    <h3>{{ currentLanguage === 'de' ? 'Multi-Bild Transformation' : 'Multi-Image Transformation' }}</h3>
                  </div>
                  <p>{{ currentLanguage === 'de'
                    ? 'Kombiniere bis zu 3 Bilder mit QWEN-2511 Vision. Beschreibe, wie die Bilder verschmolzen werden sollen.'
                    : 'Combine up to 3 images with QWEN-2511 Vision. Describe how the images should be merged.' }}</p>
                </div>

                <div class="feature-card">
                  <div class="feature-header">
                    <span class="feature-icon">✨</span>
                    <h3>{{ currentLanguage === 'de' ? 'Echtzeit Text-Streaming' : 'Real-time Text Streaming' }}</h3>
                  </div>
                  <p>{{ currentLanguage === 'de'
                    ? 'Sieh zu, wie die KI-Antworten Zeichen für Zeichen erscheinen - wie eine Schreibmaschine!'
                    : 'Watch AI responses appear character by character - like a typewriter!' }}</p>
                </div>

                <div class="feature-card">
                  <div class="feature-header">
                    <span class="feature-icon">🔄</span>
                    <h3>{{ currentLanguage === 'de' ? 'Automatische Wiederherstellung' : 'Automatic Recovery' }}</h3>
                  </div>
                  <p>{{ currentLanguage === 'de'
                    ? 'Das System startet die Bildgenerierung automatisch, wenn nötig. Keine manuellen Neustarts mehr!'
                    : 'The system automatically starts image generation when needed. No more manual restarts!' }}</p>
                </div>

                <div class="feature-card">
                  <div class="feature-header">
                    <span class="feature-icon">🎯</span>
                    <h3>{{ currentLanguage === 'de' ? 'Neue Icons' : 'New Icons' }}</h3>
                  </div>
                  <p>{{ currentLanguage === 'de'
                    ? 'Alle Emoji-Icons wurden durch einheitliche Material Design SVG-Icons ersetzt.'
                    : 'All emoji icons have been replaced with consistent Material Design SVG icons.' }}</p>
                </div>
              </section>
            </div>

            <!-- FAQ Tab -->
            <div v-if="activeTab === 'faq'" class="tab-content">
              <section class="faq-section">
                <h2>{{ currentLanguage === 'de' ? 'Häufige Fragen' : 'Frequently Asked Questions' }}</h2>

                <div class="faq-item">
                  <h3 class="faq-question">{{ currentLanguage === 'de' ? 'Warum dauert die Bildgenerierung so lange?' : 'Why does image generation take so long?' }}</h3>
                  <p class="faq-answer">{{ currentLanguage === 'de'
                    ? 'Die KI braucht etwa 30-60 Sekunden, um ein hochwertiges Bild zu erstellen. Das ist normal für SD3.5 Large, eines der besten verfügbaren Modelle.'
                    : 'The AI needs about 30-60 seconds to create a high-quality image. This is normal for SD3.5 Large, one of the best available models.' }}</p>
                </div>

                <div class="faq-item">
                  <h3 class="faq-question">{{ currentLanguage === 'de' ? 'Was bedeutet "Interception"?' : 'What does "Interception" mean?' }}</h3>
                  <p class="faq-answer">{{ currentLanguage === 'de'
                    ? 'Interception ist unsere pädagogische Transformation. Die KI verwandelt deinen einfachen Text in einen künstlerisch reichhaltigen Prompt - basierend auf den gewählten Eigenschaften.'
                    : 'Interception is our pedagogical transformation. The AI transforms your simple text into an artistically rich prompt - based on the selected properties.' }}</p>
                </div>

                <div class="faq-item">
                  <h3 class="faq-question">{{ currentLanguage === 'de' ? 'Kann ich eigene Stile trainieren?' : 'Can I train my own styles?' }}</h3>
                  <p class="faq-answer">{{ currentLanguage === 'de'
                    ? 'Ja! Mit dem LoRA Training Studio kannst du eigene Stile trainieren. Lade 5-20 Beispielbilder hoch und trainiere ein LoRA-Modell, das deinen Stil lernt.'
                    : 'Yes! With the LoRA Training Studio you can train your own styles. Upload 5-20 example images and train a LoRA model that learns your style.' }}</p>
                </div>

                <div class="faq-item">
                  <h3 class="faq-question">{{ currentLanguage === 'de' ? 'Was passiert mit meinen Bildern?' : 'What happens to my images?' }}</h3>
                  <p class="faq-answer">{{ currentLanguage === 'de'
                    ? 'Generierte Bilder werden zu Forschungszwecken gespeichert. Hochgeladene Bilder werden NICHT dauerhaft gespeichert. Es werden keine User- oder IP-Daten erfasst.'
                    : 'Generated images are saved for research purposes. Uploaded images are NOT permanently stored. No user or IP data is collected.' }}</p>
                </div>

                <div class="faq-item">
                  <h3 class="faq-question">{{ currentLanguage === 'de' ? 'Welche Sicherheitsstufen gibt es?' : 'What safety levels are there?' }}</h3>
                  <p class="faq-answer">{{ currentLanguage === 'de'
                    ? 'Es gibt drei Stufen: Kinder (streng gefiltert), Jugend (moderate Filter), und Erwachsene (Standard-Filter). Die Sicherheitsstufe bestimmt, welche Inhalte generiert werden können.'
                    : 'There are three levels: Kids (strictly filtered), Youth (moderate filters), and Adults (standard filters). The safety level determines what content can be generated.' }}</p>
                </div>

                <div class="contact-section">
                  <h3>{{ currentLanguage === 'de' ? 'Noch Fragen?' : 'Still have questions?' }}</h3>
                  <p>{{ currentLanguage === 'de'
                    ? 'Frag Träshy! Oder schreibe an: '
                    : 'Ask Träshy! Or write to: ' }}<a href="mailto:vanessa.baumann@fau.de">vanessa.baumann@fau.de</a></p>
                </div>
              </section>
            </div>
          </div>

        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import trashyIcon from '../assets/trashy-icon.png'

const props = defineProps<{
  modelValue: boolean
}>()

const { locale } = useI18n()
const currentLanguage = computed(() => locale.value)

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const activeTab = ref('welcome')

const tabs = [
  { id: 'welcome', labelDe: 'Willkommen', labelEn: 'Welcome', icon: '👋' },
  { id: 'start', labelDe: 'Los geht\'s', labelEn: 'Get Started', icon: '🚀' },
  { id: 'workflows', labelDe: 'Workflows', labelEn: 'Workflows', icon: '⚡' },
  { id: 'whatsNew', labelDe: 'Was ist neu?', labelEn: 'What\'s New', icon: '✨' },
  { id: 'faq', labelDe: 'FAQ', labelEn: 'FAQ', icon: '❓' }
]

function closeModal() {
  emit('update:modelValue', false)
}

function handleEscape(event: KeyboardEvent) {
  if (event.key === 'Escape' && props.modelValue) {
    closeModal()
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleEscape)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleEscape)
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 1rem;
  overflow-y: auto;
}

.modal-container {
  background: #0a0a0a;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  max-width: 900px;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem 2rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  flex-shrink: 0;
}

.modal-header h1 {
  font-size: 1.75rem;
  font-weight: 700;
  color: #ffffff;
  margin: 0;
}

.modal-close {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.6);
  font-size: 2.5rem;
  line-height: 1;
  cursor: pointer;
  padding: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.modal-close:hover {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.9);
}

/* Tab Navigation */
.tab-nav {
  display: flex;
  gap: 0.5rem;
  padding: 1rem 2rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  flex-shrink: 0;
  overflow-x: auto;
}

.tab-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
  font-size: 0.9rem;
}

.tab-button:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.3);
}

.tab-button.active {
  background: rgba(76, 175, 80, 0.2);
  border-color: #4CAF50;
  color: #4CAF50;
}

.tab-icon {
  font-size: 1.1rem;
}

/* Modal Body */
.modal-body {
  padding: 2rem;
  overflow-y: auto;
  flex: 1;
  color: #ffffff;
}

.tab-content {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Welcome Section */
.welcome-section {
  margin-bottom: 2rem;
}

.trashy-welcome {
  display: flex;
  align-items: center;
  gap: 2rem;
  padding: 2rem;
  background: linear-gradient(135deg, rgba(76, 175, 80, 0.1), rgba(76, 175, 80, 0.05));
  border-radius: 16px;
  border: 1px solid rgba(76, 175, 80, 0.3);
}

.trashy-icon-large {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
}

.welcome-text h2 {
  margin: 0 0 0.5rem 0;
  color: #4CAF50;
  font-size: 1.5rem;
}

.welcome-text p {
  margin: 0;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.6;
}

/* Info Sections */
.info-section {
  margin-bottom: 2rem;
}

.info-section h3 {
  color: #ffffff;
  font-size: 1.25rem;
  margin-bottom: 0.75rem;
}

.info-section p {
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.6;
}

/* Flow Diagram */
.flow-diagram {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  margin: 1rem 0;
  flex-wrap: wrap;
}

.flow-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.step-number {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #4CAF50;
  color: white;
  border-radius: 50%;
  font-weight: bold;
}

.step-text {
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.9rem;
}

.flow-arrow {
  color: rgba(255, 255, 255, 0.4);
  font-size: 1.5rem;
}

.flow-description {
  text-align: center;
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.9rem;
}

/* Step Cards */
.step-card {
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  margin-bottom: 1rem;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.step-badge {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #4CAF50;
  color: white;
  border-radius: 50%;
  font-weight: bold;
  font-size: 0.9rem;
}

.step-card h3 {
  margin: 0;
  color: #ffffff;
  font-size: 1.1rem;
}

.step-card p {
  margin: 0;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.6;
}

.property-preview {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-top: 1rem;
}

.property-tag {
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.9);
}

.example-box {
  display: flex;
  gap: 0.5rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  margin-top: 1rem;
  font-size: 0.9rem;
}

.example-box strong {
  color: #4CAF50;
}

.example-box span {
  color: rgba(255, 255, 255, 0.8);
  font-style: italic;
}

/* Workflow Cards */
.workflows-section h2 {
  margin-bottom: 1.5rem;
}

.section-subtitle {
  margin-top: 2rem;
  margin-bottom: 1rem;
  color: rgba(255, 255, 255, 0.7);
  font-size: 1rem;
  font-weight: 600;
}

.workflow-card {
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  margin-bottom: 1rem;
}

.workflow-card.legacy {
  opacity: 0.8;
  border-style: dashed;
}

.workflow-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.75rem;
}

.workflow-icon {
  font-size: 1.5rem;
}

.workflow-header h3 {
  margin: 0;
  color: #ffffff;
  font-size: 1.1rem;
  flex: 1;
}

.workflow-tag {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.workflow-tag.main {
  background: rgba(76, 175, 80, 0.2);
  color: #4CAF50;
}

.workflow-tag.legacy {
  background: rgba(255, 193, 7, 0.2);
  color: #FFC107;
}

.workflow-card p {
  margin: 0 0 1rem 0;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.6;
}

.workflow-flow {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.7);
}

/* Feature Cards */
.whats-new-section h2 {
  margin-bottom: 1.5rem;
}

.feature-card {
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  margin-bottom: 1rem;
}

.feature-card.highlight {
  background: linear-gradient(135deg, rgba(76, 175, 80, 0.1), rgba(76, 175, 80, 0.05));
  border-color: rgba(76, 175, 80, 0.3);
}

.feature-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.75rem;
}

.feature-icon {
  font-size: 1.5rem;
}

.feature-header h3 {
  margin: 0;
  color: #ffffff;
  font-size: 1.1rem;
}

.feature-card p {
  margin: 0;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.6;
}

/* FAQ Section */
.faq-section h2 {
  margin-bottom: 1.5rem;
}

.faq-item {
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  margin-bottom: 1rem;
}

.faq-question {
  margin: 0 0 0.75rem 0;
  color: #4CAF50;
  font-size: 1rem;
}

.faq-answer {
  margin: 0;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.6;
}

.contact-section {
  margin-top: 2rem;
  padding: 1.5rem;
  background: rgba(76, 175, 80, 0.1);
  border-radius: 12px;
  text-align: center;
}

.contact-section h3 {
  margin: 0 0 0.5rem 0;
  color: #ffffff;
}

.contact-section p {
  margin: 0;
  color: rgba(255, 255, 255, 0.8);
}

.contact-section a {
  color: #4CAF50;
  text-decoration: none;
}

.contact-section a:hover {
  text-decoration: underline;
}

/* Modal Fade Transition */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-active .modal-container,
.modal-fade-leave-active .modal-container {
  transition: transform 0.3s ease;
}

.modal-fade-enter-from .modal-container,
.modal-fade-leave-to .modal-container {
  transform: scale(0.95);
}

/* Responsive */
@media (max-width: 768px) {
  .modal-container {
    max-height: 95vh;
  }

  .modal-header {
    padding: 1rem 1.5rem;
  }

  .modal-header h1 {
    font-size: 1.5rem;
  }

  .tab-nav {
    padding: 0.75rem 1rem;
    gap: 0.25rem;
  }

  .tab-button {
    padding: 0.5rem 0.75rem;
    font-size: 0.8rem;
  }

  .modal-body {
    padding: 1.5rem;
  }

  .trashy-welcome {
    flex-direction: column;
    text-align: center;
    gap: 1rem;
    padding: 1.5rem;
  }

  .flow-diagram {
    flex-direction: column;
    gap: 1rem;
  }

  .flow-arrow {
    transform: rotate(90deg);
  }
}
</style>
