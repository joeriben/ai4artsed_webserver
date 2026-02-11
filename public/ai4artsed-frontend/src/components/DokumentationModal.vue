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
              {{ currentLanguage === 'de' ? tab.labelDe : tab.labelEn }}
            </button>
          </div>

          <div class="modal-body">
            <!-- Welcome Tab -->
            <div v-if="activeTab === 'welcome'" class="tab-content">
              <section class="info-section">
                <h3>{{ currentLanguage === 'de' ? 'Was ist das UCDCAE AI LAB?' : 'What is the UCDCAE AI LAB?' }}</h3>
                <p>{{ currentLanguage === 'de'
                  ? 'Das UCDCAE AI LAB ist eine pädagogisch-künstlerische Experimentierplattform des UNESCO Chair in Digital Culture and Arts in Education. Sie wurde entwickelt, um den kritischen und kreativen Umgang mit generativer KI in der kulturell-ästhetischen Medienbildung zu erforschen.'
                  : 'The UCDCAE AI LAB is a pedagogical-artistic experimentation platform of the UNESCO Chair in Digital Culture and Arts in Education. It was developed to explore critical and creative engagement with generative AI in cultural-aesthetic media education.' }}</p>
              </section>

              <section class="info-section">
                <h3>{{ currentLanguage === 'de' ? 'Warum diese Plattform?' : 'Why this platform?' }}</h3>
                <p>{{ currentLanguage === 'de'
                  ? 'Generative KI-Modelle sind mächtige Werkzeuge, aber auch "Black Boxes". Wir wollen verstehen: Wie reagieren verschiedene Modelle auf unterschiedliche Eingaben? Was passiert, wenn wir nicht nur kurze, einfache Prompts eingeben, sondern ausführliche, differenzierte Beschreibungen? Wie können wir lernen, selbst zu verstehen worum es uns geht? Wie können wir unsere Bildidee aus vielen unterschiedlichen Blickwinkeln verstehen und verändern?'
                  : 'Generative AI models are powerful tools, but also "black boxes". We want to understand: How do different models react to different inputs? What happens when we don\'t just enter short, simple prompts, but detailed, nuanced descriptions? How can we learn to truly understand what we want? How can we understand and change our image idea from many different perspectives?' }}</p>
              </section>

              <section class="info-section">
                <h3>{{ currentLanguage === 'de' ? 'Das LLM als Co-Akteur' : 'The LLM as Co-Actor' }}</h3>
                <p>{{ currentLanguage === 'de'
                  ? 'Ein zentrales Konzept: Das Sprachmodell (LLM) ist hier nicht nur ein Werkzeug, sondern ein Co-Akteur im kreativen Prozess. Es verarbeitet deine Eingabe auf Basis seiner Trainingsdaten und erzeugt etwas Neues. Das ist faszinierend, aber auch nicht unproblematisch – denn wir wissen nicht genau, wie und warum das Modell bestimmte Entscheidungen trifft.'
                  : 'A central concept: The language model (LLM) is not just a tool here, but a co-actor in the creative process. It processes your input based on its training data and generates something new. This is fascinating, but also not unproblematic – because we don\'t know exactly how and why the model makes certain decisions.' }}</p>
              </section>

              <section class="info-section">
                <h3>{{ currentLanguage === 'de' ? 'Was passiert mit meinen Eingaben?' : 'What happens to my inputs?' }}</h3>
                <p>{{ currentLanguage === 'de'
                  ? 'Generierte Inhalte werden zu Forschungszwecken gespeichert – sie helfen uns, die Plattform zu verbessern. Hochgeladene Bilder werden nicht dauerhaft gespeichert. Es werden keine personenbezogenen Daten erfasst.'
                  : 'Generated content is saved for research purposes – it helps us improve the platform. Uploaded images are not permanently stored. No personal data is collected.' }}</p>
              </section>

              <section class="info-section contact-welcome">
                <h3>{{ currentLanguage === 'de' ? 'Kontakt' : 'Contact' }}</h3>
                <p>{{ currentLanguage === 'de'
                  ? 'Frag Träshy direkt in der Anwendung, oder schreibe an: '
                  : 'Ask Träshy directly in the application, or write to: ' }}<a href="mailto:vanessa.baumann@fau.de">vanessa.baumann@fau.de</a></p>

                <div class="disclaimer">
                  <p>{{ currentLanguage === 'de'
                    ? '📝 Diese Dokumentation wurde automatisch generiert (Claude Code, Januar 2026).'
                    : '📝 This documentation was automatically generated (Claude Code, January 2026).' }}</p>
                </div>
              </section>
            </div>

            <!-- Getting Started Tab -->
            <div v-if="activeTab === 'start'" class="tab-content">
              <section class="guide-section">
                <h2>{{ currentLanguage === 'de' ? 'Aufbau der Plattform' : 'Platform Structure' }}</h2>

                <div class="concept-card highlight">
                  <h3>{{ currentLanguage === 'de' ? 'Das Prinzip: WAS und WIE trennen' : 'The Principle: Separating WHAT and HOW' }}</h3>
                  <p>{{ currentLanguage === 'de'
                    ? 'Im Text-Modus arbeitest du mit zwei getrennten Eingaben: Deine Idee (WAS soll entstehen) und deine Regeln (WIE soll es umgesetzt werden). Es gibt vorgefertigte Konfigurationen als Hilfestellung – aber das Ziel ist, dass du lernst, eigene Regeln zu formulieren.'
                    : 'In text mode, you work with two separate inputs: Your idea (WHAT should be created) and your rules (HOW should it be realized). There are pre-made configurations as assistance – but the goal is for you to learn to formulate your own rules.' }}</p>
                  <div class="example-box">
                    <strong>{{ currentLanguage === 'de' ? 'Beispiel Regel:' : 'Example rule:' }}</strong>
                    <span>{{ currentLanguage === 'de' ? '"Beschreibe alles aus der Perspektive der Vögel auf den Bäumen"' : '"Describe everything from the perspective of the birds in the trees"' }}</span>
                  </div>
                </div>

                <div class="step-card">
                  <div class="step-header">
                    <h3>{{ currentLanguage === 'de' ? 'Regeln wählen' : 'Choose Rules' }}</h3>
                  </div>
                  <div class="step-image-display">
                    <svg xmlns="http://www.w3.org/2000/svg" height="60" viewBox="0 -960 960 960" width="60" fill="currentColor" class="select-vue-icon">
                      <path d="M480-60q-50 0-85-35t-35-85q0-50 35-85t85-35q50 0 85 35t35 85q0 50-35 85t-85 35Zm0-80q17 0 28.5-11.5T520-180q0-17-11.5-28.5T480-220q-17 0-28.5 11.5T440-180q0 17 11.5 28.5T480-140Zm-260-70q-50 0-85-35t-35-85q0-50 35-85t85-35q50 0 85 35t35 85q0 50-35 85t-85 35Zm520 0q-50 0-85-35t-35-85q0-50 35-85t85-35q50 0 85 35t35 85q0 50-35 85t-85 35Zm-520-80q17 0 28.5-11.5T260-330q0-17-11.5-28.5T220-370q-17 0-28.5 11.5T180-330q0 17 11.5 28.5T220-290Zm520 0q17 0 28.5-11.5T780-330q0-17-11.5-28.5T740-370q-17 0-28.5 11.5T700-330q0 17 11.5 28.5T740-290ZM220-510q-50 0-85-35t-35-85q0-50 35-85t85-35q50 0 85 35t35 85q0 50-35 85t-85 35Zm520 0q-50 0-85-35t-35-85q0-50 35-85t85-35q50 0 85 35t35 85q0 50-35 85t-85 35Zm-520-80q17 0 28.5-11.5T260-630q0-17-11.5-28.5T220-670q-17 0-28.5 11.5T180-630q0 17 11.5 28.5T220-590Zm520 0q17 0 28.5-11.5T780-630q0-17-11.5-28.5T740-670q-17 0-28.5 11.5T700-630q0 17 11.5 28.5T740-590Zm-260-70q-50 0-85-35t-35-85q0-50 35-85t85-35q50 0 85 35t35 85q0 50-35 85t-85 35Zm0-80q17 0 28.5-11.5T520-780q0-17-11.5-28.5T480-820q-17 0-28.5 11.5T440-780q0 17 11.5 28.5T480-740Z"/>
                    </svg>
                  </div>
                  <p>{{ currentLanguage === 'de'
                    ? 'Auf der Eingangsseite siehst du in der Mitte "Du bestimmst!" – das ist der Ausgangspunkt mit einer LEEREN Regel-Box. Alles drum herum sind Anregungen: vorgefertigte Regeln, die du als Inspiration nutzen oder direkt verwenden kannst. Die ausgewählten Regeln werden in alle drei Modi übernommen.'
                    : 'On the start page you see "Your Call!" in the center – this is the starting point with an EMPTY rules box. Everything around it are suggestions: pre-made rules you can use as inspiration or directly. The selected rules are applied to all three modes.' }}</p>
                  <p class="note">{{ currentLanguage === 'de'
                    ? 'Wichtig: Eine Text-KI wird später deine Idee (WAS) mit diesen Regeln (WIE) verarbeiten und einen erweiterten Prompt erzeugen. Das Ergebnis kannst du direkt in der Box verändern, durch erneutes "Start"-Klicken neu generieren lassen, oder per Copy & Paste in die Prompt-Box einfügen und von dort aus weiterarbeiten.'
                    : 'Important: A text AI will later process your idea (WHAT) with these rules (HOW) and create an expanded prompt. You can edit the result directly in the box, regenerate it by clicking "Start" again, or copy & paste it into the prompt box to continue working from there.' }}</p>
                </div>

                <div class="step-card">
                  <div class="step-header">
                    <span class="step-badge">2</span>
                    <h3>{{ currentLanguage === 'de' ? 'Vier Modi zur Auswahl' : 'Four Modes to Choose From' }}</h3>
                  </div>
                  <p>{{ currentLanguage === 'de'
                    ? 'In den ersten drei Modi gelten die gewählten Regeln. Der Unterschied liegt darin, WAS du eingibst:'
                    : 'In the first three modes, the selected rules apply. The difference is WHAT you input:' }}</p>

                  <div class="mode-list">
                    <div class="mode-item">
                      <div class="mode-item-header">
                        <svg xmlns="http://www.w3.org/2000/svg" height="20" viewBox="0 -960 960 960" width="20" fill="currentColor" class="mode-icon">
                          <path d="M160-200v-80h528l-42-42 56-56 138 138-138 138-56-56 42-42H160Zm116-200 164-440h80l164 440h-76l-38-112H392l-40 112h-76Zm138-176h132l-64-182h-4l-64 182Z"/>
                        </svg>
                        <strong>{{ currentLanguage === 'de' ? 'Text-Modus' : 'Text Mode' }}</strong>
                      </div>
                      <p>{{ currentLanguage === 'de'
                        ? 'Du gibst eine Idee als Text ein. Die Text-KI verarbeitet deine Idee zusammen mit den Regeln und erzeugt einen erweiterten Prompt.'
                        : 'You enter an idea as text. The text AI processes your idea together with the rules and creates an expanded prompt.' }}</p>
                    </div>
                    <div class="mode-item">
                      <div class="mode-item-header">
                        <svg xmlns="http://www.w3.org/2000/svg" height="20" viewBox="0 -960 960 960" width="20" fill="currentColor" class="mode-icon">
                          <path d="M200-120q-33 0-56.5-23.5T120-200v-560q0-33 23.5-56.5T200-840h560q33 0 56.5 23.5T840-760v560q0 33-23.5 56.5T760-120H200Zm0-80h560v-560H200v560Zm40-80h480L570-480 450-320l-90-120-120 160Zm-40 80v-560 560Z"/>
                        </svg>
                        <strong>{{ currentLanguage === 'de' ? 'Bild-Modus' : 'Image Mode' }}</strong>
                      </div>
                      <p>{{ currentLanguage === 'de'
                        ? 'Statt Text lädst du EIN Bild hoch. Das Bild ersetzt den Text-Prompt. Du beschreibst zusätzlich, was damit geschehen soll.'
                        : 'Instead of text, you upload ONE image. The image replaces the text prompt. You additionally describe what should happen to it.' }}</p>
                    </div>
                    <div class="mode-item">
                      <div class="mode-item-header">
                        <svg xmlns="http://www.w3.org/2000/svg" height="20" viewBox="0 -960 960 960" width="20" fill="currentColor" class="mode-icon">
                          <path d="M120-840h320v320H120v-320Zm80 80v160-160Zm320-80h320v320H520v-320Zm80 80v160-160ZM120-440h320v320H120v-320Zm80 80v160-160Zm440-80h80v120h120v80H720v120h-80v-120H520v-80h120v-120Zm-40-320v160h160v-160H600Zm-400 0v160h160v-160H200Zm0 400v160h160v-160H200Z"/>
                        </svg>
                        <strong>{{ currentLanguage === 'de' ? 'Multi-Bild-Modus' : 'Multi-Image Mode' }}</strong>
                      </div>
                      <p>{{ currentLanguage === 'de'
                        ? 'Du lädst bis zu DREI Bilder hoch, die zusammen den Prompt ersetzen. Du beschreibst, wie sie kombiniert werden sollen.'
                        : 'You upload up to THREE images that together replace the prompt. You describe how they should be combined.' }}</p>
                    </div>
                    <div class="mode-item">
                      <div class="mode-item-header">
                        <svg xmlns="http://www.w3.org/2000/svg" height="20" viewBox="0 0 24 24" width="20" fill="currentColor" class="mode-icon">
                          <path d="M22 11V3h-7v3H9V3H2v8h7V8h2v10h4v3h7v-8h-7v3h-2V8h2v3z"/>
                        </svg>
                        <strong>{{ currentLanguage === 'de' ? 'Canvas-Modus' : 'Canvas Mode' }}</strong>
                      </div>
                      <p>{{ currentLanguage === 'de'
                        ? 'Du baust einen visuellen Workflow aus Nodes. Hier gelten keine vorgewählten Regeln – du definierst den gesamten Prozess selbst, von der Eingabe über Transformationen bis zur Ausgabe.'
                        : 'You build a visual workflow from nodes. No pre-selected rules apply here – you define the entire process yourself, from input through transformations to output.' }}</p>
                    </div>
                  </div>
                </div>

                <div class="step-card">
                  <div class="step-header">
                    <span class="step-badge">3</span>
                    <h3>{{ currentLanguage === 'de' ? 'Medien und Modelle wählen' : 'Choose Media and Models' }}</h3>
                  </div>
                  <p>{{ currentLanguage === 'de'
                    ? 'Die Plattform ist multimodal: Du kannst nicht nur Bilder erzeugen, sondern auch Audio und Musik. Wähle ein Ausgabemedium und dann ein Modell. Das Spannende: Du kannst denselben Prompt mit verschiedenen Modellen ausprobieren – innerhalb eines Mediums oder sogar medienübergreifend. So lernst du, wie unterschiedlich Modelle auf dieselbe Eingabe reagieren.'
                    : 'The platform is multimodal: You can generate not only images, but also audio and music. Choose an output medium and then a model. The exciting part: You can try the same prompt with different models – within one medium or even across media. This way you learn how differently models react to the same input.' }}</p>
                </div>

                <div class="step-card">
                  <div class="step-header">
                    <span class="step-badge">4</span>
                    <h3>{{ currentLanguage === 'de' ? 'Modell-Adaption (je nach Modell)' : 'Model Adaption (depending on model)' }}</h3>
                  </div>
                  <p>{{ currentLanguage === 'de'
                    ? 'Nicht alle Modelle brauchen denselben Prompt-Stil:'
                    : 'Not all models need the same prompt style:' }}</p>
                  <div class="mode-list">
                    <div class="mode-item">
                      <strong>Stable Diffusion 3.5</strong>
                      <p>{{ currentLanguage === 'de'
                        ? 'BRAUCHT Adaption: Der Prompt wird in "klassischen" Prompt-Stil umgewandelt (Stichworte, Gewichtungen). Hier kannst du lernen, wie traditionelles Prompting funktioniert.'
                        : 'NEEDS adaption: The prompt is converted to "classic" prompt style (keywords, weightings). Here you can learn how traditional prompting works.' }}</p>
                    </div>
                    <div class="mode-item">
                      <strong>GPT Image, Gemini, QWEN</strong>
                      <p>{{ currentLanguage === 'de'
                        ? 'BRAUCHEN KEINE Adaption, weil sie selbst ein mächtiges Sprachmodul besitzen und natürliche Sprache direkt verstehen.'
                        : 'DON\'T NEED adaption because they have their own powerful language module and understand natural language directly.' }}</p>
                    </div>
                    <div class="mode-item">
                      <strong>{{ currentLanguage === 'de' ? 'Video- und Audio-Modelle' : 'Video and Audio Models' }}</strong>
                      <p>{{ currentLanguage === 'de'
                        ? 'Erhalten Adaption für szenische (Video) bzw. auditive (Sound/Musik) Beschreibungen.'
                        : 'Receive adaption for scenic (video) or auditive (sound/music) descriptions.' }}</p>
                    </div>
                    <div class="mode-item">
                      <strong>p5.js</strong>
                      <p>{{ currentLanguage === 'de'
                        ? 'Ein Sonderfall: Hier wird generativer Code erzeugt, keine Bilder. Die Adaption bereitet den Prompt für Code-Generierung vor.'
                        : 'A special case: Here generative code is created, not images. The adaption prepares the prompt for code generation.' }}</p>
                    </div>
                  </div>
                  <p class="note">{{ currentLanguage === 'de'
                    ? 'Wichtig: Auch hier kannst du alles verändern – der adaptierte Prompt ist nur ein Vorschlag.'
                    : 'Important: You can change everything here too – the adapted prompt is just a suggestion.' }}</p>
                </div>

                <div class="step-card">
                  <div class="step-header">
                    <span class="step-badge">5</span>
                    <h3>{{ currentLanguage === 'de' ? 'Übersetzung ins Englische' : 'Translation to English' }}</h3>
                  </div>
                  <p>{{ currentLanguage === 'de'
                    ? 'Am Ende wird dein Prompt ins Englische übersetzt (falls er es nicht schon ist). Warum? Weil generative KI-Modelle meist nur Englisch wirklich gut verstehen. Wir wollen aber, dass du in deiner Sprache arbeiten kannst – deshalb übernimmt das System die Übersetzung für dich. Dieser Schritt ist derzeit noch nicht sichtbar, wird aber im Hintergrund ausgeführt.'
                    : 'At the end, your prompt is translated into English (if it isn\'t already). Why? Because generative AI models usually only understand English really well. But we want you to be able to work in your language – so the system handles the translation for you. This step is currently not visible but is executed in the background.' }}</p>
                </div>

                <div class="concept-card highlight">
                  <h3>{{ currentLanguage === 'de' ? 'Zirkularität: Alles ist verbunden' : 'Circularity: Everything is Connected' }}</h3>
                  <p>{{ currentLanguage === 'de'
                    ? 'Auch wenn der Ablauf linear aussieht (von oben nach unten), ist die Plattform zirkulär gedacht: Du kannst jederzeit zurückgehen, jeden Text kopieren und woanders einfügen, erzeugte Bilder in den Bild-Modus oder Multi-Bild-Modus laden und weiterverarbeiten. Experimentiere!'
                    : 'Even though the flow looks linear (top to bottom), the platform is designed to be circular: You can go back at any time, copy any text and paste it elsewhere, load generated images into Image Mode or Multi-Image Mode and continue processing. Experiment!' }}</p>
                  <div class="example-box" style="flex-direction: column; align-items: flex-start;">
                    <strong>{{ currentLanguage === 'de' ? 'Beispiel:' : 'Example:' }}</strong>
                    <span>{{ currentLanguage === 'de'
                      ? 'Du kannst einen Prompt mit dem "Verniedlicher" verniedlichen, das Ergebnis wieder nach oben kopieren und dann über'
                      : 'You can make a prompt cute with the "Cutifier", copy the result back up and then via' }}
                      <svg xmlns="http://www.w3.org/2000/svg" height="16" viewBox="0 -960 960 960" width="16" fill="currentColor" style="vertical-align: middle; margin: 0 4px;">
                        <path d="M480-60q-50 0-85-35t-35-85q0-50 35-85t85-35q50 0 85 35t35 85q0 50-35 85t-85 35Zm0-80q17 0 28.5-11.5T520-180q0-17-11.5-28.5T480-220q-17 0-28.5 11.5T440-180q0 17 11.5 28.5T480-140Zm-260-70q-50 0-85-35t-35-85q0-50 35-85t85-35q50 0 85 35t35 85q0 50-35 85t-85 35Zm520 0q-50 0-85-35t-35-85q0-50 35-85t85-35q50 0 85 35t35 85q0 50-35 85t-85 35Zm-520-80q17 0 28.5-11.5T260-330q0-17-11.5-28.5T220-370q-17 0-28.5 11.5T180-330q0 17 11.5 28.5T220-290Zm520 0q17 0 28.5-11.5T780-330q0-17-11.5-28.5T740-370q-17 0-28.5 11.5T700-330q0 17 11.5 28.5T740-290ZM220-510q-50 0-85-35t-35-85q0-50 35-85t85-35q50 0 85 35t35 85q0 50-35 85t-85 35Zm520 0q-50 0-85-35t-35-85q0-50 35-85t85-35q50 0 85 35t35 85q0 50-35 85t-85 35Zm-520-80q17 0 28.5-11.5T260-630q0-17-11.5-28.5T220-670q-17 0-28.5 11.5T180-630q0 17 11.5 28.5T220-590Zm520 0q17 0 28.5-11.5T780-630q0-17-11.5-28.5T740-670q-17 0-28.5 11.5T700-630q0 17 11.5 28.5T740-590Zm-260-70q-50 0-85-35t-35-85q0-50 35-85t85-35q50 0 85 35t35 85q0 50-35 85t-85 35Zm0-80q17 0 28.5-11.5T520-780q0-17-11.5-28.5T480-820q-17 0-28.5 11.5T440-780q0 17 11.5 28.5T480-740Z"/>
                      </svg>
                      {{ currentLanguage === 'de'
                        ? 'eine ganz andere Regel anwenden, z.B. "Entkitscher", und dann dasselbe wieder mit "Übertreiber", und so weiter. Und zwischendurch kannst DU selbst immer wieder etwas verändern.'
                        : 'apply a completely different rule, e.g. "De-Kitschifier", and then the same again with "Exaggerator", and so on. And in between, YOU can always change something yourself.' }}</span>
                  </div>
                </div>

                <div class="disclaimer">
                  <p>{{ currentLanguage === 'de'
                    ? '📝 Diese Dokumentation wurde automatisch generiert (Claude Code, Januar 2026).'
                    : '📝 This documentation was automatically generated (Claude Code, January 2026).' }}</p>
                </div>
              </section>
            </div>

            <!-- Pedagogy Tab -->
            <div v-if="activeTab === 'pedagogy'" class="tab-content">
              <section class="concept-section">
                <h2>{{ currentLanguage === 'de' ? '8 Pädagogische Prinzipien' : '8 Pedagogical Principles' }}</h2>

                <div class="principle-card">
                  <div class="principle-header">
                    <span class="principle-number">1</span>
                    <h3>{{ currentLanguage === 'de' ? 'WAS/WIE-Trennung' : 'WHAT/HOW Separation' }}</h3>
                  </div>
                  <p>{{ currentLanguage === 'de'
                    ? 'Idee und Regeln werden getrennt eingegeben. Das WAS (deine Idee) und das WIE (die Regeln zur Verarbeitung) sind zwei verschiedene Dinge. Diese Trennung macht bewusst, welche Entscheidungen du triffst.'
                    : 'Idea and rules are entered separately. The WHAT (your idea) and the HOW (the rules for processing) are two different things. This separation makes you aware of what decisions you are making.' }}</p>
                  <div class="example-box">
                    <strong>{{ currentLanguage === 'de' ? 'Beispiel:' : 'Example:' }}</strong>
                    {{ currentLanguage === 'de'
                      ? 'WAS: "Ein Frühstückstisch" → WIE: "aus Kinderperspektive" vs. "im Bauhaus-Stil" → völlig unterschiedliche Ergebnisse'
                      : 'WHAT: "A breakfast table" → HOW: "from child\'s perspective" vs. "in Bauhaus style" → completely different results' }}
                  </div>
                </div>

                <div class="principle-card">
                  <div class="principle-header">
                    <span class="principle-number">2</span>
                    <h3>{{ currentLanguage === 'de' ? 'Prompt Interception: LLM als Co-Akteur' : 'Prompt Interception: LLM as Co-Actor' }}</h3>
                  </div>
                  <p>{{ currentLanguage === 'de'
                    ? 'Konventionelle KI-Interfaces machen Nutzende zu Befehlsgebenden, die zugleich der Maschinenlogik unterworfen sind. Prompt Interception bricht dieses Muster: Das LLM ist kein Werkzeug, das tut was du willst – es ist ein Co-Akteur, der Neues und Unwägbarkeiten in den Prozess einbringt. Es interpretiert, wählt aus, ergänzt. Das Ergebnis trägt deine Handschrift UND die des Modells. Die Maschine dient deinem kreativen Werden – nicht umgekehrt.'
                    : 'Conventional AI interfaces turn users into commanders who are simultaneously subjected to machine logic. Prompt Interception breaks this pattern: The LLM is not a tool that does what you want – it is a co-actor that introduces novelty and unpredictability into the process. It interprets, selects, adds. The result bears your signature AND that of the model. The machine serves your creative becoming – not vice versa.' }}</p>
                  <div class="tension-box">
                    <span class="tension-label">{{ currentLanguage === 'de' ? 'Spannung:' : 'Tension:' }}</span>
                    {{ currentLanguage === 'de'
                      ? 'Faszinierend, aber problematisch – wir wissen nicht, wie das Modell "entscheidet"'
                      : 'Fascinating, but problematic – we don\'t know how the model "decides"' }}
                  </div>
                </div>

                <div class="principle-card">
                  <div class="principle-header">
                    <span class="principle-number">3</span>
                    <h3>{{ currentLanguage === 'de' ? 'Kritisches Erkunden' : 'Critical Exploration' }}</h3>
                  </div>
                  <p>{{ currentLanguage === 'de'
                    ? 'Wie reagieren verschiedene Modelle? Wo liegen ihre Grenzen? Durch systematisches Experimentieren erforschst du die Fähigkeiten und Eigenheiten generativer KI.'
                    : 'How do different models react? Where are their limits? Through systematic experimentation, you explore the capabilities and peculiarities of generative AI.' }}</p>
                </div>

                <div class="principle-card">
                  <div class="principle-header">
                    <span class="principle-number">4</span>
                    <h3>{{ currentLanguage === 'de' ? 'Sichtbarkeit der Verarbeitung' : 'Visibility of Processing' }}</h3>
                  </div>
                  <p>{{ currentLanguage === 'de'
                    ? 'Jeder Zwischenschritt ist sichtbar: die transformierte Beschreibung, die Adaption, das Endergebnis. Du kannst eingreifen, verändern, zurückgehen. Die "Black Box" wird geöffnet.'
                    : 'Every intermediate step is visible: the transformed description, the adaption, the final result. You can intervene, change, go back. The "black box" is opened.' }}</p>
                </div>

                <div class="principle-card">
                  <div class="principle-header">
                    <span class="principle-number">5</span>
                    <h3>{{ currentLanguage === 'de' ? 'Zirkularität' : 'Circularity' }}</h3>
                  </div>
                  <p>{{ currentLanguage === 'de'
                    ? 'Ergebnisse können wieder als Eingabe dienen. Eine Beschreibung kann erneut transformiert werden. Ein Bild kann analysiert und neu interpretiert werden. Iteration statt linearer Produktion.'
                    : 'Results can become inputs again. A description can be transformed again. An image can be analyzed and reinterpreted. Iteration instead of linear production.' }}</p>
                  <div class="circularity-chain">
                    <span>{{ currentLanguage === 'de' ? 'Idee' : 'Idea' }}</span> →
                    <span>{{ currentLanguage === 'de' ? 'Beschreibung' : 'Description' }}</span> →
                    <span>{{ currentLanguage === 'de' ? 'Bild' : 'Image' }}</span> →
                    <span>{{ currentLanguage === 'de' ? 'Neue Idee' : 'New Idea' }}</span> → ...
                  </div>
                </div>

                <div class="principle-card">
                  <div class="principle-header">
                    <span class="principle-number">6</span>
                    <h3>{{ currentLanguage === 'de' ? 'Pädagogische Begleitung' : 'Pedagogical Guidance' }}</h3>
                  </div>
                  <p>{{ currentLanguage === 'de'
                    ? 'Die Plattform entfaltet ihren vollen Wert durch reflektierende Begleitung. Sie ist ein Werkzeug für Lernprozesse, kein Selbstläufer. Die Fragen, die beim Experimentieren entstehen, sind oft wichtiger als die Bilder.'
                    : 'The platform unfolds its full value through reflective guidance. It is a tool for learning processes, not self-running. The questions that arise during experimentation are often more important than the images.' }}</p>
                </div>

                <div class="principle-card">
                  <div class="principle-header">
                    <span class="principle-number">7</span>
                    <h3>{{ currentLanguage === 'de' ? 'Wissen über die Welt' : 'Knowledge About the World' }}</h3>
                  </div>
                  <p>{{ currentLanguage === 'de'
                    ? 'Künstlerische Prozesse erfordern nicht nur ästhetisches Wissen, sondern auch Wissen über Sachverhalte in der Welt. Die KI recherchiert während der Transformation auf Wikipedia, um faktische Informationen zu finden – in über 70 Sprachen, passend zum jeweiligen Thema.'
                    : 'Artistic processes require not only aesthetic knowledge, but also knowledge about facts in the world. The AI researches Wikipedia during transformation to find factual information – in over 70 languages, appropriate to each topic.' }}</p>
                  <div class="example-box">
                    <strong>{{ currentLanguage === 'de' ? 'Das Wikipedia-Badge (W):' : 'The Wikipedia Badge (W):' }}</strong>
                    {{ currentLanguage === 'de'
                      ? 'Zeigt alle Recherche-Versuche an: Gefundene Artikel erscheinen als anklickbare Links, nicht gefundene Begriffe werden grau angezeigt. So wird sichtbar, was die KI zu wissen meint – und was nicht.'
                      : 'Shows all research attempts: Found articles appear as clickable links, terms not found are shown in gray. This makes visible what the AI thinks it knows – and what it does not.' }}
                  </div>
                  <div class="tension-box">
                    <span class="tension-label">{{ currentLanguage === 'de' ? 'Einladung:' : 'Invitation:' }}</span>
                    {{ currentLanguage === 'de'
                      ? 'Die Wikipedia-Links laden ein, selbst mehr zu erfahren. Klicken Sie auf die Links, um die Quellen zu prüfen und Ihr eigenes Wissen zu erweitern.'
                      : 'The Wikipedia links invite you to learn more yourself. Click on the links to check the sources and expand your own knowledge.' }}
                  </div>
                </div>

                <div class="principle-card">
                  <div class="principle-header">
                    <span class="principle-number">8</span>
                    <h3>{{ currentLanguage === 'de' ? 'Zusammenarbeiten' : 'Collaboration' }}</h3>
                  </div>
                  <p>{{ currentLanguage === 'de'
                    ? 'Das Favoriten-System ermöglicht zwei Arbeitsmodi: "Meine" zeigt nur deine eigenen Favoriten – eine persönliche Arbeitsfläche zum Iterieren, Vergleichen und Auswählen zwischen Entwürfen. "Alle" zeigt die Favoriten aller Workshop-Teilnehmenden – ein kollektiver Pool zum Teilen von Bildern und Prompts, gegenseitigem Inspirieren und gemeinsamen Weiterentwickeln.'
                    : 'The favorites system enables two working modes: "Mine" shows only your own favorites – a personal workspace for iterating, comparing, and selecting between drafts. "All" shows favorites from all workshop participants – a collective pool for sharing images and prompts, mutual inspiration, and collaborative development.' }}</p>
                  <div class="example-box">
                    <strong>{{ currentLanguage === 'de' ? 'Persönlich:' : 'Personal:' }}</strong>
                    {{ currentLanguage === 'de'
                      ? 'Speichere mehrere Varianten eines Bildes, vergleiche sie, wähle die beste aus und arbeite daran weiter. Die Favoriten sind deine Werkbank.'
                      : 'Save multiple variations of an image, compare them, select the best one, and continue working on it. Favorites are your workbench.' }}
                  </div>
                  <div class="example-box">
                    <strong>{{ currentLanguage === 'de' ? 'Kollaborativ:' : 'Collaborative:' }}</strong>
                    {{ currentLanguage === 'de'
                      ? 'Sehe interessante Arbeiten von anderen, lade ihre kompletten Prompts und Einstellungen, verändere sie und entwickle eigene Varianten. Die "Wiederherstellen"-Funktion macht den kreativen Prozess transparent und teilbar.'
                      : 'See interesting work from others, load their complete prompts and settings, modify them, and develop your own variations. The "Restore" function makes the creative process transparent and shareable.' }}
                  </div>
                  <div class="tension-box">
                    <span class="tension-label">{{ currentLanguage === 'de' ? 'Workshop-Kontext:' : 'Workshop Context:' }}</span>
                    {{ currentLanguage === 'de'
                      ? 'Der Wechsel zwischen "Meine" und "Alle" macht die soziale Dimension kreativer KI-Arbeit sichtbar: Wann arbeite ich allein, wann teile ich? Diese bewusste Entscheidung ist pädagogisch wertvoll.'
                      : 'Switching between "Mine" and "All" makes the social dimension of creative AI work visible: When do I work alone, when do I share? This conscious choice has pedagogical value.' }}
                  </div>
                </div>

                <div class="disclaimer">
                  <p>{{ currentLanguage === 'de'
                    ? '📝 Diese Dokumentation wurde automatisch generiert (Claude Code, Januar 2026).'
                    : '📝 This documentation was automatically generated (Claude Code, January 2026).' }}</p>
                </div>
              </section>
            </div>

            <!-- Experiments Tab -->
            <div v-if="activeTab === 'experiments'" class="tab-content">
              <section class="experiments-section">
                <h2>{{ currentLanguage === 'de' ? 'Experimentelle Workflows' : 'Experimental Workflows' }}</h2>
                <p class="section-intro">{{ currentLanguage === 'de'
                  ? 'Diese Experimente arbeiten auf der mathematischen Ebene der KI-Modelle. Sie zeigen, wie Sprache und Bedeutung in Vektoren übersetzt werden – und was passiert, wenn wir diese Vektoren manipulieren.'
                  : 'These experiments work at the mathematical level of AI models. They show how language and meaning are translated into vectors – and what happens when we manipulate these vectors.' }}</p>

                <div class="experiment-card surrealizer">
                  <h3>Hallucinator</h3>
                  <div class="experiment-what">
                    <strong>{{ currentLanguage === 'de' ? 'Was passiert hier?' : 'What happens here?' }}</strong>
                    <p>{{ currentLanguage === 'de'
                      ? 'Dein Prompt wird von zwei verschiedenen KI-"Gehirnen" gelesen: CLIP-L (trainiert auf Bild-Text-Paaren, "denkt" visuell) und T5 (trainiert auf reinem Text, "denkt" sprachlich). Bei α=0 siehst du ein normales CLIP-Bild. Aber der Regler mischt nicht einfach zwischen beiden — er extrapoliert: Bei α=20 wird das Embedding 19× über die T5-Interpretation hinaus geschoben, in einen mathematischen Raum, den das Modell im Training nie gesehen hat.'
                      : 'Your prompt is read by two different AI "brains": CLIP-L (trained on image-text pairs, "thinks" visually) and T5 (trained on pure text, "thinks" linguistically). At α=0 you see a normal CLIP image. But the slider doesn\'t simply blend between them — it extrapolates: at α=20, the embedding is pushed 19× beyond T5\'s interpretation, into a mathematical space the model never encountered during training.' }}</p>
                  </div>
                  <div class="experiment-why">
                    <strong>{{ currentLanguage === 'de' ? 'Warum werden die Bilder surreal?' : 'Why do images become surreal?' }}</strong>
                    <p>{{ currentLanguage === 'de'
                      ? 'Das Modell muss Vektoren interpretieren, die weit außerhalb seiner Trainingsdaten liegen. Es "halluziniert" auf ästhetisch überraschende Weise — Formen, Farben und Strukturen entstehen, die kein direkter Prompt erzeugen könnte. Gleichzeitig bleiben die restlichen T5-Tokens (ab Token 78) unverändert und wirken als semantischer Anker: Das Bild bleibt mit deinem Text verbunden, auch wenn die visuelle Darstellung surreal wird.'
                      : 'The model must interpret vectors that lie far outside its training data. It "hallucinates" in aesthetically surprising ways — shapes, colors, and structures emerge that no direct prompt could produce. Meanwhile, the remaining T5 tokens (from token 78 onward) stay unchanged, acting as a semantic anchor: the image stays connected to your text even as the visual representation becomes surreal.' }}</p>
                  </div>
                  <div class="experiment-example">
                    <strong>{{ currentLanguage === 'de' ? 'Bereiche:' : 'Ranges:' }}</strong>
                    {{ currentLanguage === 'de'
                      ? 'α=0: normales Bild (nur CLIP-L) | α=1: reines T5 (noch normal) | α=15–35: surrealer Sweet Spot (Extrapolation) | α>50: extreme Verzerrung'
                      : 'α=0: normal image (CLIP-L only) | α=1: pure T5 (still normal) | α=15–35: surreal sweet spot (extrapolation) | α>50: extreme distortion' }}
                  </div>
                  <div class="experiment-negative">
                    <strong>{{ currentLanguage === 'de' ? 'Negative α — die Gegenrichtung:' : 'Negative α — the reverse direction:' }}</strong>
                    <p>{{ currentLanguage === 'de'
                      ? 'Bei negativem α wird CLIP-L verstärkt und T5 negiert. Bei α=-10 ergibt die Formel: 11·CLIP-L + (-10)·T5. Der Effekt geht tiefer als "weniger T5": Weil CLIP-L nur 768 von 4096 Dimensionen füllt (der Rest ist Nullen), werden in den oberen 3328 Dimensionen die T5-Vektoren invertiert. In der Cross-Attention des Transformers kehrt das die Aufmerksamkeitsmuster um — Textteile, die normalerweise am wichtigsten wären, werden ignoriert, unwichtige dominieren. Das Ergebnis: visuell getriebene Halluzinationen mit gestörter Semantik, qualitativ anders als positive Extrapolation.'
                      : 'With negative α, CLIP-L is amplified and T5 is negated. At α=-10 the formula yields: 11·CLIP-L + (-10)·T5. The effect goes deeper than "less T5": because CLIP-L only fills 768 of 4096 dimensions (the rest are zeros), the upper 3328 dimensions get inverted T5 vectors. In the transformer\'s cross-attention, this inverts the attention patterns — text tokens that would normally be most important are ignored, while insignificant ones dominate. The result: visually driven hallucinations with disrupted semantics, qualitatively different from positive extrapolation.' }}</p>
                  </div>

                  <!-- Deep Dive: Mathematics -->
                  <button class="deep-dive-toggle" @click="showHallucinatorMath = !showHallucinatorMath">
                    {{ currentLanguage === 'de' ? '📐 Die Mathematik im Detail' : '📐 The Mathematics in Detail' }}
                    <span class="toggle-arrow">{{ showHallucinatorMath ? '▲' : '▼' }}</span>
                  </button>

                  <div v-if="showHallucinatorMath" class="deep-dive-content">
                    <!-- Section 1: Two Worlds -->
                    <h4>{{ currentLanguage === 'de' ? 'CLIP-L vs T5-XXL: Zwei verschiedene "Welten"' : 'CLIP-L vs T5-XXL: Two Different "Worlds"' }}</h4>
                    <p>{{ currentLanguage === 'de'
                      ? 'Stell dir den Embedding-Raum als einen hochdimensionalen Raum vor. Jeder Encoder bildet denselben Text auf einen anderen Punkt in diesem Raum ab:'
                      : 'Imagine the embedding space as a high-dimensional space. Each encoder maps the same text to a different point in this space:' }}</p>
                    <pre class="math-diagram">Prompt: "Ein Haus am See"

CLIP-L → Punkt C = [0.3, -0.7, 0.1, ...]  (768 Dimensionen)
T5-XXL → Punkt T = [0.5, -0.2, 0.8, ...]  (4096 Dimensionen)</pre>
                    <p>{{ currentLanguage === 'de'
                      ? 'Warum sind die Punkte verschieden? CLIP-L wurde mit Bild-Text-Paaren trainiert (kontrastives Lernen). Es "denkt" visuell: "Was für ein Bild passt zu diesem Text?" T5-XXL wurde als Sprach-Modell trainiert. Es "denkt" semantisch-linguistisch: "Was bedeutet dieser Text?"'
                      : 'Why are the points different? CLIP-L was trained on image-text pairs (contrastive learning). It "thinks" visually: "What image fits this text?" T5-XXL was trained as a language model. It "thinks" semantically-linguistically: "What does this text mean?"' }}</p>
                    <p>{{ currentLanguage === 'de'
                      ? 'Dasselbe Wort "Haus" aktiviert in CLIP-L andere Neuronen als in T5. CLIP-L hat gelernt, dass "Haus" korreliert mit bestimmten visuellen Features (Dach-Form, Fenster, Wände). T5 hat gelernt, dass "Haus" in Beziehung steht zu "Gebäude", "Wohnung", "Heim", "Architektur".'
                      : 'The same word "house" activates different neurons in CLIP-L than in T5. CLIP-L learned that "house" correlates with certain visual features (roof shape, windows, walls). T5 learned that "house" relates to "building", "apartment", "home", "architecture".' }}</p>

                    <!-- Section 2: LERP Geometry -->
                    <h4>{{ currentLanguage === 'de' ? 'Die LERP-Formel geometrisch' : 'The LERP Formula Geometrically' }}</h4>
                    <pre class="math-diagram">fused(α) = (1 - α) · C + α · T</pre>
                    <p>{{ currentLanguage === 'de'
                      ? 'Das ist eine parametrische Gerade durch C und T im Embedding-Raum:'
                      : 'This is a parametric line through C and T in the embedding space:' }}</p>
                    <pre class="math-diagram">α = 0.0  →  Punkt C (reines CLIP-L, "visuell-literal")
α = 0.5  →  Mittelpunkt zwischen C und T
α = 1.0  →  Punkt T (reines T5, "semantisch-linguistisch")

       C ────────────── T
       α=0    α=0.5    α=1</pre>
                    <p>{{ currentLanguage === 'de'
                      ? 'Bis hier ist es Interpolation — wir bleiben zwischen zwei bekannten Punkten. Das Modell hat für beide Punkte gelernt, sinnvolle Bilder zu produzieren. Die Ergebnisse sind "normal".'
                      : 'Up to here it\'s interpolation — we stay between two known points. The model learned to produce sensible images for both points. The results are "normal".' }}</p>

                    <!-- Section 3: Extrapolation -->
                    <h4>{{ currentLanguage === 'de' ? 'Was passiert bei α > 1? Extrapolation!' : 'What happens at α > 1? Extrapolation!' }}</h4>
                    <pre class="math-diagram">α = 20  →  fused = (1 - 20) · C + 20 · T = -19·C + 20·T</pre>
                    <p>{{ currentLanguage === 'de'
                      ? 'Geometrisch: Wir gehen durch T hindurch und 19× so weit darüber hinaus:'
                      : 'Geometrically: we pass through T and go 19× further beyond:' }}</p>
                    <pre class="math-diagram">   C ──────── T ──────────────────────────────────── α=20
   ← bekannt →←          terra incognita              →</pre>
                    <p>{{ currentLanguage === 'de'
                      ? 'Der Punkt bei α=20 liegt 19 Mal weiter von T entfernt als T von C. Dieses Gebiet hat das Diffusion-Modell während des Trainings nie gesehen. Es muss trotzdem etwas daraus generieren — und das Ergebnis ist surreal, weil:'
                      : 'The point at α=20 lies 19 times further from T than T is from C. The diffusion model never saw this region during training. It must still generate something from it — and the result is surreal because:' }}</p>
                    <div class="math-list">
                      <p>{{ currentLanguage === 'de'
                        ? '1. Feature-Verstärkung: Was T5 anders "sieht" als CLIP-L wird massiv verstärkt. Wenn T5 "Haus" stärker mit "Geborgenheit" assoziiert als CLIP-L, wird bei α=20 die Geborgenheits-Dimension 19× übertrieben.'
                        : '1. Feature amplification: What T5 "sees" differently from CLIP-L gets massively amplified. If T5 associates "house" more strongly with "coziness" than CLIP-L, the coziness dimension gets exaggerated 19×.' }}</p>
                      <p>{{ currentLanguage === 'de'
                        ? '2. Feature-Unterdrückung: Was CLIP-L betont und T5 nicht, wird negiert (Faktor -19). Visuelle Literalität wird aktiv unterdrückt.'
                        : '2. Feature suppression: What CLIP-L emphasizes and T5 doesn\'t gets negated (factor -19). Visual literalness is actively suppressed.' }}</p>
                      <p>{{ currentLanguage === 'de'
                        ? '3. Nicht-Linearität des Decoders: Der DiT-Decoder wurde trainiert, Embeddings in einem bestimmten Bereich zu verarbeiten. Out-of-distribution-Inputs erzeugen unvorhersehbare, aber kohärente Artefakte — ähnlich wie DeepDream, aber gesteuert.'
                        : '3. Decoder non-linearity: The DiT decoder was trained to process embeddings within a certain range. Out-of-distribution inputs produce unpredictable but coherent artifacts — similar to DeepDream, but steered.' }}</p>
                    </div>

                    <!-- Section 4: Token Level -->
                    <h4>{{ currentLanguage === 'de' ? 'Warum Token-Level statt Global?' : 'Why Token-Level Instead of Global?' }}</h4>
                    <p>{{ currentLanguage === 'de'
                      ? 'Die Fusion passiert pro Token, nicht über den ganzen Embedding-Vektor:'
                      : 'The fusion happens per token, not across the entire embedding vector:' }}</p>
                    <pre class="math-diagram">Token 1 ("Ein"):   fused[1] = (1-α)·CLIP_L[1] + α·T5[1]
Token 2 ("Haus"):  fused[2] = (1-α)·CLIP_L[2] + α·T5[2]
Token 3 ("am"):    fused[3] = (1-α)·CLIP_L[3] + α·T5[3]
Token 4 ("See"):   fused[4] = (1-α)·CLIP_L[4] + α·T5[4]
...
Token 78-512:      reines T5 (semantischer Anker)</pre>
                    <p>{{ currentLanguage === 'de'
                      ? 'Das ist entscheidend, weil jedes Token eine andere Diskrepanz zwischen CLIP und T5 hat: "Haus" → große Diskrepanz (visuell vs. semantisch sehr unterschiedlich) → starker Halluzinations-Effekt. "am" → kleine Diskrepanz (Funktionswort, beide Encoder ähnlich) → wenig Effekt.'
                      : 'This is crucial because each token has a different discrepancy between CLIP and T5: "house" → large discrepancy (visual vs. semantic very different) → strong hallucination effect. "at" → small discrepancy (function word, both encoders similar) → little effect.' }}</p>
                    <p>{{ currentLanguage === 'de'
                      ? 'Die Tokens 78–512 (reines T5) dienen als semantischer Anker — sie geben dem Modell genug "normalen" Kontext, damit das Bild nicht komplett ins Chaos abdriftet.'
                      : 'Tokens 78–512 (pure T5) serve as a semantic anchor — they give the model enough "normal" context so the image doesn\'t drift into complete chaos.' }}</p>

                    <!-- Section 5: Ranges -->
                    <h4>{{ currentLanguage === 'de' ? 'Die Grenzbereiche' : 'The Boundary Ranges' }}</h4>
                    <pre class="math-diagram">α &lt; -30     → Blackout (Embedding zu weit von allem → Rauschen)
α ≈ -4..-1  → Reines CLIP-L (T5-Einfluss ausgelöscht)
α ≈ 0..1    → Normaler Mix beider Encoder
α ≈ 2..7    → T5-dominant, beginnt "seltsam" zu werden
α ≈ 15..35  → Sweet Spot: Surreal, aber noch bildlich kohärent
α > 75      → Blackout (zu weit extrapoliert → numerischer Overflow)</pre>
                    <p>{{ currentLanguage === 'de'
                      ? 'Der Sweet Spot bei 15–35 entsteht, weil: Genug Struktur überlebt, um ein erkennbares Bild zu produzieren. Genug Verzerrung da ist, um unerwartete Assoziationen zu erzeugen. Und die T5-Tokens 78–512 als Stabilisator wirken.'
                      : 'The sweet spot at 15–35 exists because: enough structure survives to produce a recognizable image, enough distortion exists to create unexpected associations, and T5 tokens 78–512 act as a stabilizer.' }}</p>

                    <!-- Section 6: Analogy -->
                    <h4>{{ currentLanguage === 'de' ? 'Analogie' : 'Analogy' }}</h4>
                    <p>{{ currentLanguage === 'de'
                      ? 'Stell dir vor, du bittest zwei Künstler, "ein Haus am See" zu malen: CLIP-L malt ein fotografisch-realistisches Bild. T5 malt ein Bild, das die Bedeutung von "Haus am See" einfängt — Ruhe, Wasser, Schutz.'
                      : 'Imagine you ask two artists to paint "a house by a lake": CLIP-L paints a photographically realistic image. T5 paints an image that captures the meaning of "house by a lake" — tranquility, water, shelter.' }}</p>
                    <p>{{ currentLanguage === 'de'
                      ? 'Bei α=0 siehst du CLIP-Ls Bild. Bei α=1 siehst du T5s Bild. Bei α=20 extrapolierst du: "Wenn der Unterschied zwischen beiden SO ist, wie sähe es aus, wenn man diesen Unterschied 20× verstärkt?" — und bekommst etwas, das keiner der beiden Künstler je gemalt hätte.'
                      : 'At α=0 you see CLIP-L\'s painting. At α=1 you see T5\'s painting. At α=20 you extrapolate: "If the difference between both is THIS, what would it look like if you amplified that difference 20×?" — and you get something neither artist would ever have painted.' }}</p>
                  </div>
                </div>

                <div class="experiment-card split-combine">
                  <h3>Split & Combine</h3>
                  <div class="experiment-what">
                    <strong>{{ currentLanguage === 'de' ? 'Was passiert hier?' : 'What happens here?' }}</strong>
                    <p>{{ currentLanguage === 'de'
                      ? 'Jeder Begriff wird vom Text-Encoder in einen hochdimensionalen Vektor übersetzt (ca. 2000 Dimensionen). Diese Vektoren kann man mathematisch addieren, subtrahieren oder mischen. Split & Combine nimmt zwei Konzepte und verschmilzt ihre Vektoren.'
                      : 'Each concept is translated by the text encoder into a high-dimensional vector (about 2000 dimensions). These vectors can be mathematically added, subtracted, or mixed. Split & Combine takes two concepts and merges their vectors.' }}</p>
                  </div>
                  <div class="experiment-why">
                    <strong>{{ currentLanguage === 'de' ? 'Warum ist das interessant?' : 'Why is this interesting?' }}</strong>
                    <p>{{ currentLanguage === 'de'
                      ? 'Das Ergebnis ist NICHT dasselbe wie "Katze und Architektur" als Prompt zu schreiben. Bei der Vektormischung entstehen Hybride auf einer tieferen Bedeutungsebene – oft mit überraschenden, unmöglichen Kombinationen, die sprachlich nicht beschreibbar wären.'
                      : 'The result is NOT the same as writing "cat and architecture" as a prompt. Vector mixing creates hybrids at a deeper meaning level – often with surprising, impossible combinations that couldn\'t be described linguistically.' }}</p>
                  </div>
                  <div class="experiment-example">
                    <strong>{{ currentLanguage === 'de' ? 'Beispiel:' : 'Example:' }}</strong>
                    {{ currentLanguage === 'de'
                      ? '"Ozean" + "Wüste" auf Vektorebene ergibt nicht "Strand" – sondern visuelle Hybride aus Wellen und Sand, die keine reale Entsprechung haben.'
                      : '"Ocean" + "desert" at vector level doesn\'t yield "beach" – but visual hybrids of waves and sand that have no real-world equivalent.' }}
                  </div>
                </div>

                <div class="experiment-card partial-elimination">
                  <h3>Partial Elimination</h3>
                  <div class="experiment-what">
                    <strong>{{ currentLanguage === 'de' ? 'Was passiert hier?' : 'What happens here?' }}</strong>
                    <p>{{ currentLanguage === 'de'
                      ? 'Du gibst einen Begriff ein und wählst Dimensionen des Vektors aus, die auf Null gesetzt werden. Der Rest wird zur Bildgenerierung verwendet. So kannst du "Teile der Bedeutung" entfernen und beobachten, was übrig bleibt.'
                      : 'You enter a concept and select dimensions of the vector to set to zero. The rest is used for image generation. This way you can "remove parts of meaning" and observe what remains.' }}</p>
                  </div>
                  <div class="experiment-why">
                    <strong>{{ currentLanguage === 'de' ? 'Warum ist das interessant?' : 'Why is this interesting?' }}</strong>
                    <p>{{ currentLanguage === 'de'
                      ? 'Niemand weiß genau, was in welcher Dimension eines Vektors "gespeichert" ist. Durch systematisches Eliminieren kannst du entdecken: Welche Dimensionen sind für "Farbe" zuständig? Welche für "Form"? Die Ergebnisse sind oft überraschend und zeigen die Grenzen unseres Verständnisses.'
                      : 'Nobody knows exactly what\'s "stored" in which dimension of a vector. By systematically eliminating, you can discover: Which dimensions are responsible for "color"? Which for "shape"? The results are often surprising and show the limits of our understanding.' }}</p>
                  </div>
                  <div class="experiment-example">
                    <strong>{{ currentLanguage === 'de' ? 'Beispiel:' : 'Example:' }}</strong>
                    {{ currentLanguage === 'de'
                      ? 'Entferne Dimensionen 100-200 von "roter Apfel" – verliert er seine Röte? Seine Rundheit? Oder etwas ganz anderes? Das Experimentieren zeigt: Bedeutung ist nicht so organisiert, wie wir intuitiv annehmen.'
                      : 'Remove dimensions 100-200 from "red apple" – does it lose its redness? Its roundness? Or something completely different? Experimenting shows: Meaning is not organized the way we intuitively assume.' }}
                  </div>
                </div>

                <div class="disclaimer">
                  <p>{{ currentLanguage === 'de'
                    ? '📝 Diese Dokumentation wurde automatisch generiert (Claude Code, Januar 2026).'
                    : '📝 This documentation was automatically generated (Claude Code, January 2026).' }}</p>
                </div>
              </section>
            </div>

            <!-- Workshop Tab -->
            <div v-if="activeTab === 'workshop'" class="tab-content">
              <section class="workshop-section">
                <h2>{{ currentLanguage === 'de' ? 'Für Pädagog:innen' : 'For Educators' }}</h2>

                <div class="workshop-intro">
                  <p>{{ currentLanguage === 'de'
                    ? 'Das UCDCAE AI LAB ist für den Einsatz in Workshops und Unterricht konzipiert. Hier einige Hinweise für die Begleitung.'
                    : 'The UCDCAE AI LAB is designed for use in workshops and teaching. Here are some tips for facilitation.' }}</p>
                </div>

                <div class="workshop-card">
                  <h3>{{ currentLanguage === 'de' ? 'Was die Plattform KANN' : 'What the Platform CAN Do' }}</h3>
                  <ul>
                    <li>{{ currentLanguage === 'de' ? 'Kreative Prozesse sichtbar machen' : 'Make creative processes visible' }}</li>
                    <li>{{ currentLanguage === 'de' ? 'Zum Nachdenken über Gestaltungsentscheidungen anregen' : 'Encourage reflection on design decisions' }}</li>
                    <li>{{ currentLanguage === 'de' ? 'Die "Black Box" KI ein Stück öffnen' : 'Open the AI "black box" a little' }}</li>
                    <li>{{ currentLanguage === 'de' ? 'Experimentierräume für kritische Auseinandersetzung bieten' : 'Provide spaces for critical engagement' }}</li>
                  </ul>
                </div>

                <div class="workshop-card">
                  <h3>{{ currentLanguage === 'de' ? 'Was die Plattform NICHT KANN' : 'What the Platform CANNOT Do' }}</h3>
                  <ul>
                    <li>{{ currentLanguage === 'de' ? 'Die pädagogische Begleitung ersetzen' : 'Replace pedagogical guidance' }}</li>
                    <li>{{ currentLanguage === 'de' ? 'Von selbst zu kritischem Denken führen' : 'Automatically lead to critical thinking' }}</li>
                    <li>{{ currentLanguage === 'de' ? '"Bessere Bilder" garantieren' : 'Guarantee "better images"' }}</li>
                  </ul>
                </div>

                <div class="workshop-card">
                  <h3>{{ currentLanguage === 'de' ? 'Reflexionsfragen für Workshops' : 'Reflection Questions for Workshops' }}</h3>
                  <ul class="question-list">
                    <li>{{ currentLanguage === 'de' ? 'Warum hat das Modell diese Interpretation gewählt?' : 'Why did the model choose this interpretation?' }}</li>
                    <li>{{ currentLanguage === 'de' ? 'Was wäre, wenn wir andere Regeln verwendet hätten?' : 'What if we had used different rules?' }}</li>
                    <li>{{ currentLanguage === 'de' ? 'Wessen Handschrift trägt dieses Bild – deine oder die der KI?' : 'Whose signature does this image bear – yours or the AI\'s?' }}</li>
                    <li>{{ currentLanguage === 'de' ? 'Was hat dich überrascht? Was war erwartbar?' : 'What surprised you? What was predictable?' }}</li>
                  </ul>
                </div>

                <div class="workshop-card safety">
                  <h3>{{ currentLanguage === 'de' ? 'Sicherheitsstufen' : 'Safety Levels' }}</h3>
                  <p>{{ currentLanguage === 'de'
                    ? 'Es gibt drei Stufen: Kinder, Jugend und Erwachsene. Sie bestimmen, welche Inhalte generiert werden können. Die Stufe wird von der betreuenden Person in den Einstellungen festgelegt.'
                    : 'There are three levels: Kids, Youth, and Adults. They determine what content can be generated. The level is set by the supervising person in the settings.' }}</p>
                </div>

                <div class="workshop-card">
                  <h3>{{ currentLanguage === 'de' ? 'LLM-Konfiguration' : 'LLM Configuration' }}</h3>
                  <p>{{ currentLanguage === 'de'
                    ? 'In den Einstellungen können die verwendeten Sprachmodelle flexibel konfiguriert werden:'
                    : 'The language models used can be flexibly configured in the settings:' }}</p>
                  <ul>
                    <li>{{ currentLanguage === 'de' ? 'Lokale Modelle (Ollama) – volle Datenkontrolle' : 'Local models (Ollama) – full data control' }}</li>
                    <li>{{ currentLanguage === 'de' ? 'Externe Cloud-Anbieter – mehr Leistung' : 'External cloud providers – more performance' }}</li>
                    <li>{{ currentLanguage === 'de' ? 'DSGVO-konforme Optionen (Mistral, lokale Modelle)' : 'GDPR-compliant options (Mistral, local models)' }}</li>
                  </ul>
                </div>

                <div class="workshop-card license">
                  <h3>{{ currentLanguage === 'de' ? 'Lizenz und Urheberschaft' : 'License and Authorship' }}</h3>
                  <p>{{ currentLanguage === 'de'
                    ? 'Diese Software ist ein wissenschaftliches Werk von Prof. Dr. Benjamin Jörissen (UNESCO Chair in Digital Culture and Arts in Education, Friedrich-Alexander-Universität Erlangen-Nürnberg). Sie verkörpert bildungstheoretische Forschungsergebnisse in Software-Form.'
                    : 'This software is an academic work by Prof. Dr. Benjamin Jörissen (UNESCO Chair in Digital Culture and Arts in Education, Friedrich-Alexander-Universität Erlangen-Nürnberg). It embodies educational-theoretical research in software form.' }}</p>
                  <p><strong>{{ currentLanguage === 'de' ? 'Source Available' : 'Source Available' }}</strong> — {{ currentLanguage === 'de'
                    ? 'Der Quellcode ist frei einsehbar und die Software steht nicht-kommerziellen Bildungseinrichtungen kostenlos zur Verfügung. Modifikation und Redistribution bedürfen der schriftlichen Genehmigung des Urhebers. Kommerzielle Nutzung ist nach Vereinbarung möglich.'
                    : 'The source code is freely accessible and the software is available free of charge to non-commercial educational institutions. Modification and redistribution require the author\'s written permission. Commercial use is available by agreement.' }}</p>
                  <p>{{ currentLanguage === 'de'
                    ? 'Die vollständige Lizenz findet sich im Repository als LICENSE.md (UCDCAE AI Lab License v1.0).'
                    : 'The complete license can be found in the repository as LICENSE.md (UCDCAE AI Lab License v1.0).' }}</p>
                </div>

                <div class="workshop-card installation">
                  <h3>{{ currentLanguage === 'de' ? 'Installation und Betrieb' : 'Installation and Operation' }}</h3>
                  <p>{{ currentLanguage === 'de'
                    ? 'Das UCDCAE AI LAB ist ein komplexes System mit mehreren Komponenten (Backend, Frontend, LLM-Anbindung, Bildgenerierung, Sicherheitssystem). Die Installation erfordert Erfahrung mit Python, Node.js, GPU-Konfiguration und KI-Modellen.'
                    : 'The UCDCAE AI LAB is a complex system with multiple components (backend, frontend, LLM integration, image generation, safety system). Installation requires experience with Python, Node.js, GPU configuration, and AI models.' }}</p>
                  <p><strong>{{ currentLanguage === 'de'
                    ? 'Der Einsatz eines KI-Coding-Agenten (z.B. Claude Code) wird dringend empfohlen'
                    : 'The use of an AI coding agent (e.g. Claude Code) is highly recommended' }}</strong> — {{ currentLanguage === 'de'
                    ? 'sowohl für die initiale Installation als auch für Konfiguration und Wartung.'
                    : 'both for initial installation and for configuration and maintenance.' }}</p>
                </div>

                <div class="contact-box">
                  <h3>{{ currentLanguage === 'de' ? 'Kontakt' : 'Contact' }}</h3>
                  <p>{{ currentLanguage === 'de'
                    ? 'Für Fragen zur Nutzung in Bildungskontexten:'
                    : 'For questions about use in educational contexts:' }}</p>
                  <a href="mailto:vanessa.baumann@fau.de">vanessa.baumann@fau.de</a>
                  <p style="margin-top: 0.5rem">{{ currentLanguage === 'de'
                    ? 'Für Lizenzfragen, kommerzielle Anfragen und Autorisierungen:'
                    : 'For license inquiries, commercial requests, and authorizations:' }}</p>
                  <a href="mailto:benjamin.joerissen@fau.de">benjamin.joerissen@fau.de</a>
                </div>
              </section>
            </div>

            <!-- Canvas Tab -->
            <div v-if="activeTab === 'canvas'" class="tab-content">
              <section class="canvas-section">
                <div class="canvas-header">
                  <svg xmlns="http://www.w3.org/2000/svg" height="48" viewBox="0 0 24 24" width="48" fill="currentColor" class="canvas-header-icon">
                    <path d="M22 11V3h-7v3H9V3H2v8h7V8h2v10h4v3h7v-8h-7v3h-2V8h2v3z"/>
                  </svg>
                  <div>
                    <h2>{{ currentLanguage === 'de' ? 'Canvas Workflow System' : 'Canvas Workflow System' }}</h2>
                    <p class="section-intro">{{ currentLanguage === 'de'
                      ? 'Canvas ist eine visuelle Forschungs-Workbench für die systematische Erkundung generativer KI.'
                      : 'Canvas is a visual research workbench for systematic exploration of generative AI.' }}</p>
                  </div>
                </div>

                <div class="canvas-card paradigm">
                  <h3>{{ currentLanguage === 'de' ? 'Lehrforschung' : 'Exploratory Research' }}</h3>
                  <p>{{ currentLanguage === 'de'
                    ? 'Canvas ist für gemeinsames Erforschen in Workshops, Unterricht oder zur Professionalisierung konzipiert. Anders als technische Systeme wie ComfyUI oder Max/MSP verzichtet Canvas bewusst auf tiefe technische Parametrierung – dafür macht es strukturelle Komplexität sichtbar und erforschbar.'
                    : 'Canvas is designed for collaborative exploration in workshops, teaching, or professional development. Unlike technical systems like ComfyUI or Max/MSP, Canvas deliberately avoids deep technical parameterization – instead, it makes structural complexity visible and explorable.' }}</p>
                </div>

                <div class="canvas-card interception">
                  <h3>{{ currentLanguage === 'de' ? 'Prompt Interception' : 'Prompt Interception' }}</h3>
                  <p>{{ currentLanguage === 'de'
                    ? 'Konventionelle KI-Interfaces machen Nutzende zu Befehlsgebenden, die zugleich der Maschinenlogik unterworfen sind. Prompt Interception bricht dieses Muster auf: Das LLM bringt Neues und Unwägbarkeiten in den Prozess ein. Nutzende und KI erzeugen gemeinsam neue Feedback-Loops. Die Maschine dient dem kreativen Werden – nicht umgekehrt.'
                    : 'Conventional AI interfaces turn users into commanders who are simultaneously subjected to machine logic. Prompt Interception breaks this pattern: The LLM introduces novelty and unpredictability into the process. Users and AI create new feedback loops together. The machine serves creative becoming – not vice versa.' }}</p>
                  <p class="pragmatic-note">{{ currentLanguage === 'de'
                    ? 'Pragmatisch ermöglicht Interception auch komplexere Prompts – wesentlich für echte KI-Erkundung. Einfache Prompts erzeugen notwendig klischeehafte Outputs. Erst mit angemessen komplexen Prompts lassen sich Biases, aber auch interessante Eigenheiten des Systems systematisch erfahren.'
                    : 'Pragmatically, Interception also enables more complex prompts – essential for genuine AI exploration. Simple prompts necessarily produce clichéd outputs. Only with appropriately complex prompts can biases, but also interesting system characteristics, be systematically experienced.' }}</p>
                </div>

                <div class="canvas-card recursive">
                  <h3>{{ currentLanguage === 'de' ? 'Rekursiv-reflexive Workflows' : 'Recursive-Reflexive Workflows' }}</h3>
                  <p>{{ currentLanguage === 'de'
                    ? 'Ein Novum, das wir von keiner anderen genAI-Plattform kennen: Evaluation-Nodes können Feedback an andere Nodes zurückgeben. Der Workflow wird rekursiv durchlaufen, bis nutzerdefinierte Kriterien erfüllt sind. So entstehen experimentelle Setups zur Erforschung von:'
                    : 'A novelty we don\'t know from any other genAI platform: Evaluation nodes can feed back to other nodes. The workflow runs recursively until user-defined criteria are met. This enables experimental setups for researching:' }}</p>
                  <ul>
                    <li>{{ currentLanguage === 'de' ? 'Biases in Modellen' : 'Biases in models' }}</li>
                    <li>{{ currentLanguage === 'de' ? 'Normiertheit vs. "Kreativität"' : 'Normativity vs. "creativity"' }}</li>
                    <li>{{ currentLanguage === 'de' ? 'Ethische Bewertung von LLM-Outputs' : 'Ethical assessment of LLM outputs' }}</li>
                    <li>{{ currentLanguage === 'de' ? 'Vergleichende Analysen mit Massenoutput' : 'Comparative analyses with mass output' }}</li>
                  </ul>
                </div>

                <div class="canvas-card nodes">
                  <h3>{{ currentLanguage === 'de' ? 'Verfügbare Node-Typen' : 'Available Node Types' }}</h3>
                  <div class="node-grid">
                    <div class="node-item"><span class="node-color" style="background: #3b82f6;"></span><strong>Input</strong> – {{ currentLanguage === 'de' ? 'Texteingabe' : 'Text input' }}</div>
                    <div class="node-item"><span class="node-color" style="background: #8b5cf6;"></span><strong>Interception</strong> – {{ currentLanguage === 'de' ? 'Pädagogische Transformation' : 'Pedagogical transformation' }}</div>
                    <div class="node-item"><span class="node-color" style="background: #8b5cf6;"></span><strong>Random Prompt</strong> – {{ currentLanguage === 'de' ? 'LLM-generierte Inhalte' : 'LLM-generated content' }}</div>
                    <div class="node-item"><span class="node-color" style="background: #8b5cf6;"></span><strong>Translation</strong> – {{ currentLanguage === 'de' ? 'Sprachübersetzung' : 'Language translation' }}</div>
                    <div class="node-item"><span class="node-color" style="background: #8b5cf6;"></span><strong>Model Adaption</strong> – {{ currentLanguage === 'de' ? 'Prompt-Optimierung' : 'Prompt optimization' }}</div>
                    <div class="node-item"><span class="node-color" style="background: #10b981;"></span><strong>Generation</strong> – {{ currentLanguage === 'de' ? 'Medienerzeugung' : 'Media generation' }}</div>
                    <div class="node-item"><span class="node-color" style="background: #f97316;"></span><strong>Evaluation</strong> – {{ currentLanguage === 'de' ? 'LLM-Bewertung mit Verzweigung' : 'LLM evaluation with branching' }}</div>
                    <div class="node-item"><span class="node-color" style="background: #f97316;"></span><strong>Comparison</strong> – {{ currentLanguage === 'de' ? 'Vergleicht mehrere Inputs' : 'Compares multiple inputs' }}</div>
                    <div class="node-item"><span class="node-color" style="background: #06b6d4;"></span><strong>Preview</strong> – {{ currentLanguage === 'de' ? 'Zwischenergebnis-Vorschau' : 'Intermediate result preview' }}</div>
                    <div class="node-item"><span class="node-color" style="background: #06b6d4;"></span><strong>Collector</strong> – {{ currentLanguage === 'de' ? 'Sammelt alle Outputs' : 'Collects all outputs' }}</div>
                  </div>
                </div>

                <div class="canvas-card target-groups">
                  <h3>{{ currentLanguage === 'de' ? 'Zielgruppen' : 'Target Groups' }}</h3>
                  <ul>
                    <li><strong>{{ currentLanguage === 'de' ? 'Ältere Kinder (ab 12 J.)' : 'Older children (12+)' }}</strong> – {{ currentLanguage === 'de' ? 'Strukturierte KI-Erkundung in Bildungssettings' : 'Structured AI exploration in educational settings' }}</li>
                    <li><strong>{{ currentLanguage === 'de' ? 'Pädagog:innen' : 'Educators' }}</strong> – {{ currentLanguage === 'de' ? 'Professionalisierung durch Verständnis von genAI' : 'Professional development through understanding genAI' }}</li>
                    <li><strong>{{ currentLanguage === 'de' ? 'Forschende' : 'Researchers' }}</strong> – {{ currentLanguage === 'de' ? 'Systematische Untersuchung von Modellverhalten' : 'Systematic investigation of model behavior' }}</li>
                    <li><strong>{{ currentLanguage === 'de' ? 'Kulturelle Bildung' : 'Cultural education' }}</strong> – {{ currentLanguage === 'de' ? 'Workshop-Settings für kritische KI-Literacy' : 'Workshop settings for critical AI literacy' }}</li>
                  </ul>
                </div>

                <div class="disclaimer">
                  <p>{{ currentLanguage === 'de'
                    ? '📝 Diese Dokumentation wurde automatisch generiert (Claude Code, Januar 2026).'
                    : '📝 This documentation was automatically generated (Claude Code, January 2026).' }}</p>
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

const props = defineProps<{
  modelValue: boolean
}>()

const { locale } = useI18n()
const currentLanguage = computed(() => locale.value)

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const activeTab = ref('welcome')
const showHallucinatorMath = ref(false)

const tabs = [
  { id: 'welcome', labelDe: 'Willkommen', labelEn: 'Welcome' },
  { id: 'start', labelDe: 'Anleitung', labelEn: 'Guide' },
  { id: 'pedagogy', labelDe: 'Pädagogik', labelEn: 'Pedagogy' },
  { id: 'workshop', labelDe: 'Praxis', labelEn: 'Practice' },
  { id: 'experiments', labelDe: 'Experimente', labelEn: 'Experiments' },
  { id: 'canvas', labelDe: 'Canvas', labelEn: 'Canvas' }
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
  max-width: 800px;
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
  font-size: 1.5rem;
  font-weight: 700;
  color: #ffffff;
  margin: 0;
}

.modal-close {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.6);
  font-size: 2rem;
  line-height: 1;
  cursor: pointer;
  padding: 0;
  width: 36px;
  height: 36px;
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
  padding: 0.6rem 1.2rem;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
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

/* Info Sections */
.info-section {
  margin-bottom: 1.5rem;
}

.info-section h3 {
  color: #ffffff;
  font-size: 1.1rem;
  margin-bottom: 0.5rem;
}

.info-section p {
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.7;
  margin: 0;
}

/* Concept Cards */
.concept-card {
  padding: 1.25rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  margin-bottom: 1.5rem;
}

.concept-card.highlight {
  background: linear-gradient(135deg, rgba(76, 175, 80, 0.08), rgba(76, 175, 80, 0.03));
  border-color: rgba(76, 175, 80, 0.25);
}

.concept-card h3 {
  margin: 0 0 0.75rem 0;
  color: #ffffff;
  font-size: 1.1rem;
}

.concept-card p {
  margin: 0;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.7;
}

/* Step Cards */
.step-card {
  padding: 1.25rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  margin-bottom: 1rem;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}


.step-view-icon {
  flex-shrink: 0;
  opacity: 0.85;
  color: rgba(255, 255, 255, 0.9);
}

.step-badge {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #4CAF50;
  color: white;
  border-radius: 50%;
  font-weight: bold;
  font-size: 0.85rem;
  flex-shrink: 0;
}

.step-card h3 {
  margin: 0;
  color: #ffffff;
  font-size: 1rem;
}

.step-card p {
  margin: 0;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.6;
}

.step-card p.note {
  margin-top: 0.75rem;
  padding: 0.5rem 0.75rem;
  background: rgba(76, 175, 80, 0.1);
  border-radius: 4px;
  font-size: 0.9rem;
  color: #4CAF50;
}

.step-image-display {
  display: flex;
  justify-content: center;
  padding: 1rem 0;
  margin-bottom: 0.5rem;
}

.preview-image {
  max-width: 280px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.example-box {
  display: flex;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 6px;
  margin-top: 0.75rem;
  font-size: 0.9rem;
}

.example-box strong {
  color: #4CAF50;
  flex-shrink: 0;
}

.example-box span {
  color: rgba(255, 255, 255, 0.8);
  font-style: italic;
}

/* Mode List */
.mode-list {
  margin-top: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.mode-item {
  padding: 0.75rem 1rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 6px;
  border-left: 3px solid #4CAF50;
}

.mode-item-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.mode-item-header .mode-icon {
  color: #4CAF50;
  flex-shrink: 0;
}

.mode-item strong {
  color: #ffffff;
  font-size: 0.95rem;
}

.mode-item p {
  margin: 0.25rem 0 0 0;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
}

/* Info Cards */
.info-card {
  padding: 1rem 1.25rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  margin-bottom: 0.75rem;
}

.info-card h4 {
  margin: 0 0 0.5rem 0;
  color: #4CAF50;
  font-size: 0.95rem;
}

.info-card p {
  margin: 0;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.6;
  font-size: 0.95rem;
}

/* Concept Section */
.concept-section h2 {
  margin-bottom: 1rem;
}

.concept-section h3 {
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
  color: rgba(255, 255, 255, 0.9);
  font-size: 1rem;
}

/* Contact in Welcome */
.contact-welcome a {
  color: #4CAF50;
  text-decoration: none;
}

.contact-welcome a:hover {
  text-decoration: underline;
}

/* Principle Cards (Pedagogy Tab) */
.principle-card {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 10px;
  padding: 1.25rem;
  margin-bottom: 1rem;
  border-left: 3px solid #4CAF50;
}

.principle-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.principle-number {
  width: 28px;
  height: 28px;
  background: #4CAF50;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 0.9rem;
  flex-shrink: 0;
}

.principle-card h3 {
  margin: 0;
  font-size: 1.1rem;
  color: #ffffff;
}

.principle-card p {
  margin: 0;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.6;
}

.tension-box {
  margin-top: 0.75rem;
  padding: 0.75rem;
  background: rgba(255, 152, 0, 0.15);
  border-radius: 6px;
  border-left: 3px solid #FF9800;
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.9rem;
}

.tension-label {
  color: #FF9800;
  font-weight: 600;
  margin-right: 0.5rem;
}

.circularity-chain {
  margin-top: 0.75rem;
  padding: 0.75rem;
  background: rgba(33, 150, 243, 0.1);
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
  color: #2196F3;
  font-weight: 500;
}

/* Experiments Tab */
.experiments-section .section-intro {
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 1.5rem;
  font-size: 1rem;
}

.experiment-card {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 10px;
  padding: 1.25rem;
  margin-bottom: 1rem;
}

.experiment-card.surrealizer {
  border-left: 3px solid #9C27B0;
}

.experiment-card.split-combine {
  border-left: 3px solid #2196F3;
}

.experiment-card.partial-elimination {
  border-left: 3px solid #FF5722;
}

.experiment-card h3 {
  margin: 0 0 0.5rem 0;
  color: #ffffff;
  font-size: 1.1rem;
}

.experiment-card p {
  margin: 0;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.5;
}

.tech-detail {
  margin-top: 0.75rem;
  padding: 0.75rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 6px;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
}

.tech-detail strong {
  color: rgba(255, 255, 255, 0.9);
}

/* Workshop Tab */
.workshop-intro {
  margin-bottom: 1.5rem;
  color: rgba(255, 255, 255, 0.8);
  font-size: 1rem;
}

.workshop-card {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 10px;
  padding: 1.25rem;
  margin-bottom: 1rem;
}

.workshop-card h3 {
  margin: 0 0 0.75rem 0;
  color: #ffffff;
  font-size: 1rem;
}

.workshop-card ul {
  margin: 0;
  padding-left: 1.25rem;
  color: rgba(255, 255, 255, 0.8);
}

.workshop-card li {
  margin-bottom: 0.5rem;
  line-height: 1.5;
}

/* Canvas Tab */
.canvas-section {
  padding: 0.5rem;
}

.canvas-header {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.canvas-header-icon {
  flex-shrink: 0;
  color: #10b981;
  opacity: 0.9;
}

.canvas-header h2 {
  margin: 0 0 0.5rem 0;
}

.canvas-header .section-intro {
  margin: 0;
}

.canvas-card {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 10px;
  padding: 1.25rem;
  margin-bottom: 1rem;
}

.canvas-card.paradigm {
  border-left: 3px solid #3b82f6;
}

.canvas-card.interception {
  border-left: 3px solid #8b5cf6;
}

.canvas-card.recursive {
  border-left: 3px solid #f59e0b;
}

.canvas-card.nodes {
  border-left: 3px solid #10b981;
}

.canvas-card.target-groups {
  border-left: 3px solid #06b6d4;
}

.canvas-card h3 {
  margin: 0 0 1rem 0;
  color: #ffffff;
  font-size: 1.1rem;
}

.canvas-card p {
  margin: 0 0 0.75rem 0;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.5;
}

.canvas-card p:last-child {
  margin-bottom: 0;
}

.canvas-card .pragmatic-note {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
  font-style: italic;
}

.canvas-card ul {
  margin: 0.5rem 0 0 0;
  padding-left: 1.25rem;
  color: rgba(255, 255, 255, 0.8);
}

.canvas-card li {
  margin-bottom: 0.5rem;
  line-height: 1.5;
}

.node-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0.5rem;
}

.node-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 6px;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.8);
}

.node-color {
  width: 12px;
  height: 12px;
  border-radius: 3px;
  flex-shrink: 0;
}

.node-item strong {
  color: #ffffff;
}

.question-list li {
  font-style: italic;
  color: rgba(255, 255, 255, 0.9);
}

.contact-box {
  margin-top: 1.5rem;
  padding: 1.25rem;
  background: rgba(76, 175, 80, 0.1);
  border-radius: 10px;
  text-align: center;
}

.contact-box h3 {
  margin: 0 0 0.5rem 0;
  color: #ffffff;
  font-size: 1rem;
}

.contact-box p {
  margin: 0 0 0.5rem 0;
  color: rgba(255, 255, 255, 0.8);
}

.contact-box a {
  color: #4CAF50;
  text-decoration: none;
  font-weight: 500;
}

.contact-box a:hover {
  text-decoration: underline;
}

/* Experiment Card Details */
.experiment-what,
.experiment-why {
  margin-top: 0.75rem;
}

.experiment-what strong,
.experiment-why strong {
  display: block;
  color: #4CAF50;
  font-size: 0.9rem;
  margin-bottom: 0.25rem;
}

.experiment-what p,
.experiment-why p {
  margin: 0;
  color: rgba(255, 255, 255, 0.85);
  line-height: 1.6;
  font-size: 0.95rem;
}

.experiment-example {
  margin-top: 0.75rem;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 6px;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.8);
  font-style: italic;
}

.experiment-example strong {
  color: #81C784;
  font-style: normal;
  margin-right: 0.5rem;
}

.experiment-negative {
  margin-top: 0.75rem;
  padding: 0.75rem;
  background: rgba(147, 51, 234, 0.1);
  border-left: 3px solid rgba(147, 51, 234, 0.5);
  border-radius: 6px;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.8);
}

.experiment-negative strong {
  color: rgba(180, 130, 240, 0.95);
  display: block;
  margin-bottom: 0.25rem;
}

.experiment-negative p {
  margin: 0;
  line-height: 1.6;
}

/* Deep Dive Toggle */
.deep-dive-toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  margin-top: 1rem;
  padding: 0.75rem 1rem;
  background: rgba(59, 130, 246, 0.15);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 8px;
  color: rgba(59, 130, 246, 0.95);
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.deep-dive-toggle:hover {
  background: rgba(59, 130, 246, 0.25);
}

.toggle-arrow {
  font-size: 0.8rem;
  opacity: 0.7;
}

/* Deep Dive Content */
.deep-dive-content {
  margin-top: 0.75rem;
  padding: 1.25rem;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 8px;
}

.deep-dive-content h4 {
  color: rgba(59, 130, 246, 0.95);
  font-size: 1rem;
  margin: 1.25rem 0 0.5rem 0;
}

.deep-dive-content h4:first-child {
  margin-top: 0;
}

.deep-dive-content p {
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.7;
  font-size: 0.9rem;
  margin: 0.5rem 0;
}

.math-diagram {
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  padding: 0.75rem 1rem;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 0.8rem;
  color: rgba(180, 220, 255, 0.9);
  overflow-x: auto;
  white-space: pre;
  margin: 0.5rem 0;
  line-height: 1.5;
}

.math-list {
  padding-left: 0.5rem;
  border-left: 2px solid rgba(59, 130, 246, 0.3);
  margin: 0.5rem 0;
}

.math-list p {
  font-size: 0.85rem;
  margin: 0.4rem 0;
}

/* Disclaimer */
.disclaimer {
  margin-top: 2rem;
  padding: 0.75rem;
  text-align: center;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.disclaimer p {
  margin: 0;
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.8rem;
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
    font-size: 1.25rem;
  }

  .tab-nav {
    padding: 0.75rem 1rem;
  }

  .tab-button {
    padding: 0.5rem 0.75rem;
    font-size: 0.85rem;
  }

  .modal-body {
    padding: 1.5rem;
  }
}
</style>
