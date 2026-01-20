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
                <h3>{{ currentLanguage === 'de' ? 'Was ist AI4ArtsEd?' : 'What is AI4ArtsEd?' }}</h3>
                <p>{{ currentLanguage === 'de'
                  ? 'AI4ArtsEd ist eine pädagogisch-wissenschaftliche Experimentierplattform. Sie wurde entwickelt, um den kritischen und kreativen Umgang mit generativer KI in der kulturellen Bildung zu erforschen.'
                  : 'AI4ArtsEd is a pedagogical-scientific experimentation platform. It was developed to explore critical and creative engagement with generative AI in cultural education.' }}</p>
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
            </div>

            <!-- Getting Started Tab -->
            <div v-if="activeTab === 'start'" class="tab-content">
              <section class="guide-section">
                <h2>{{ currentLanguage === 'de' ? 'Aufbau der Plattform' : 'Platform Structure' }}</h2>

                <div class="step-card">
                  <div class="step-header">
                    <span class="step-badge">1</span>
                    <h3>{{ currentLanguage === 'de' ? 'Startseite: Regeln wählen' : 'Start Page: Choose Rules' }}</h3>
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
                    <h3>{{ currentLanguage === 'de' ? 'Drei Modi zur Auswahl' : 'Three Modes to Choose From' }}</h3>
                  </div>
                  <p>{{ currentLanguage === 'de'
                    ? 'In allen drei Modi gelten die gewählten Regeln. Der Unterschied liegt darin, WAS du eingibst:'
                    : 'In all three modes, the selected rules apply. The difference is WHAT you input:' }}</p>

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
                    <h3>{{ currentLanguage === 'de' ? 'Prompt-Optimierung (je nach Modell)' : 'Prompt Optimization (depending on model)' }}</h3>
                  </div>
                  <p>{{ currentLanguage === 'de'
                    ? 'Nicht alle Modelle brauchen denselben Prompt-Stil:'
                    : 'Not all models need the same prompt style:' }}</p>
                  <div class="mode-list">
                    <div class="mode-item">
                      <strong>Stable Diffusion 3.5</strong>
                      <p>{{ currentLanguage === 'de'
                        ? 'BRAUCHT Optimierung: Der Prompt wird in "klassischen" Prompt-Stil umgewandelt (Stichworte, Gewichtungen). Hier kannst du lernen, wie traditionelles Prompting funktioniert.'
                        : 'NEEDS optimization: The prompt is converted to "classic" prompt style (keywords, weightings). Here you can learn how traditional prompting works.' }}</p>
                    </div>
                    <div class="mode-item">
                      <strong>GPT Image, Gemini, QWEN</strong>
                      <p>{{ currentLanguage === 'de'
                        ? 'BRAUCHEN KEINE Optimierung, weil sie selbst ein mächtiges Sprachmodul besitzen und natürliche Sprache direkt verstehen.'
                        : 'DON\'T NEED optimization because they have their own powerful language module and understand natural language directly.' }}</p>
                    </div>
                    <div class="mode-item">
                      <strong>{{ currentLanguage === 'de' ? 'Video- und Audio-Modelle' : 'Video and Audio Models' }}</strong>
                      <p>{{ currentLanguage === 'de'
                        ? 'Erhalten Optimierung für szenische (Video) bzw. auditive (Sound/Musik) Beschreibungen.'
                        : 'Receive optimization for scenic (video) or auditive (sound/music) descriptions.' }}</p>
                    </div>
                    <div class="mode-item">
                      <strong>p5.js</strong>
                      <p>{{ currentLanguage === 'de'
                        ? 'Ein Sonderfall: Hier wird generativer Code erzeugt, keine Bilder. Die Optimierung bereitet den Prompt für Code-Generierung vor.'
                        : 'A special case: Here generative code is created, not images. The optimization prepares the prompt for code generation.' }}</p>
                    </div>
                  </div>
                  <p class="note">{{ currentLanguage === 'de'
                    ? 'Wichtig: Auch hier kannst du alles verändern – der optimierte Prompt ist nur ein Vorschlag.'
                    : 'Important: You can change everything here too – the optimized prompt is just a suggestion.' }}</p>
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

                <div class="concept-card">
                  <h3>{{ currentLanguage === 'de' ? 'Das Prinzip: WAS und WIE trennen' : 'The Principle: Separating WHAT and HOW' }}</h3>
                  <p>{{ currentLanguage === 'de'
                    ? 'Im Text-Modus arbeitest du mit zwei getrennten Eingaben: Deine Idee (WAS soll entstehen) und deine Regeln (WIE soll es umgesetzt werden). Es gibt vorgefertigte Konfigurationen als Hilfestellung – aber das Ziel ist, dass du lernst, eigene Regeln zu formulieren.'
                    : 'In text mode, you work with two separate inputs: Your idea (WHAT should be created) and your rules (HOW should it be realized). There are pre-made configurations as assistance – but the goal is for you to learn to formulate your own rules.' }}</p>
                  <div class="example-box">
                    <strong>{{ currentLanguage === 'de' ? 'Beispiel Regel:' : 'Example rule:' }}</strong>
                    <span>{{ currentLanguage === 'de' ? '"Beschreibe alles aus der Perspektive der Vögel auf den Bäumen"' : '"Describe everything from the perspective of the birds in the trees"' }}</span>
                  </div>
                </div>
              </section>
            </div>

            <!-- Pedagogy Tab -->
            <div v-if="activeTab === 'pedagogy'" class="tab-content">
              <section class="concept-section">
                <h2>{{ currentLanguage === 'de' ? '6 Pädagogische Prinzipien' : '6 Pedagogical Principles' }}</h2>

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
                    <h3>{{ currentLanguage === 'de' ? 'LLM als Co-Akteur' : 'LLM as Co-Actor' }}</h3>
                  </div>
                  <p>{{ currentLanguage === 'de'
                    ? 'Das Sprachmodell ist kein Werkzeug, das tut was du willst. Es ist ein Co-Akteur, der mitgestaltet. Es interpretiert, wählt aus, ergänzt. Das Ergebnis trägt deine Handschrift UND die des Modells.'
                    : 'The language model is not a tool that does what you want. It is a co-actor that participates in creation. It interprets, selects, adds. The result bears your signature AND that of the model.' }}</p>
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
                    ? 'Wie reagieren verschiedene Modelle? Wo liegen ihre Grenzen? Durch systematisches Experimentieren erforschst du die Fähigkeiten und Eigenheiten generativer KI – nicht um sie optimal zu nutzen, sondern um sie zu verstehen.'
                    : 'How do different models react? Where are their limits? Through systematic experimentation, you explore the capabilities and peculiarities of generative AI – not to use it optimally, but to understand it.' }}</p>
                </div>

                <div class="principle-card">
                  <div class="principle-header">
                    <span class="principle-number">4</span>
                    <h3>{{ currentLanguage === 'de' ? 'Sichtbarkeit der Verarbeitung' : 'Visibility of Processing' }}</h3>
                  </div>
                  <p>{{ currentLanguage === 'de'
                    ? 'Jeder Zwischenschritt ist sichtbar: die transformierte Beschreibung, die Optimierung, das Endergebnis. Du kannst eingreifen, verändern, zurückgehen. Die "Black Box" wird geöffnet.'
                    : 'Every intermediate step is visible: the transformed description, the optimization, the final result. You can intervene, change, go back. The "black box" is opened.' }}</p>
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
              </section>
            </div>

            <!-- Experiments Tab -->
            <div v-if="activeTab === 'experiments'" class="tab-content">
              <section class="experiments-section">
                <h2>{{ currentLanguage === 'de' ? 'Experimentelle Workflows' : 'Experimental Workflows' }}</h2>
                <p class="section-intro">{{ currentLanguage === 'de'
                  ? 'Diese experimentellen Ansätze machen die "Black Box" sichtbar, indem sie direkt auf der technischen Ebene arbeiten.'
                  : 'These experimental approaches make the "black box" visible by working directly at the technical level.' }}</p>

                <div class="experiment-card surrealizer">
                  <h3>Surrealizer</h3>
                  <p>{{ currentLanguage === 'de'
                    ? 'Nutzt zwei verschiedene Text-Encoder (CLIP und T5) und verschmilzt ihre Ergebnisse mit einstellbarer Gewichtung.'
                    : 'Uses two different text encoders (CLIP and T5) and merges their results with adjustable weighting.' }}</p>
                  <div class="tech-detail">
                    <strong>{{ currentLanguage === 'de' ? 'Technisch:' : 'Technical:' }}</strong>
                    {{ currentLanguage === 'de'
                      ? 'CLIP (Bilder+Text trainiert) vs. T5 (nur Text trainiert) "verstehen" denselben Prompt unterschiedlich. Die Mischung erzeugt unerwartete, oft surreale Ergebnisse.'
                      : 'CLIP (trained on images+text) vs. T5 (trained on text only) "understand" the same prompt differently. The mixture creates unexpected, often surreal results.' }}
                  </div>
                </div>

                <div class="experiment-card split-combine">
                  <h3>Split & Combine</h3>
                  <p>{{ currentLanguage === 'de'
                    ? 'Nimm zwei Konzepte, zerlege sie in ihre semantischen Vektoren, und kombiniere sie auf neue Weise.'
                    : 'Take two concepts, break them into their semantic vectors, and combine them in new ways.' }}</p>
                  <div class="tech-detail">
                    <strong>{{ currentLanguage === 'de' ? 'Technisch:' : 'Technical:' }}</strong>
                    {{ currentLanguage === 'de'
                      ? 'Semantische Vektoren sind mathematische Repräsentationen von Bedeutung. Was passiert, wenn wir "Katze" + "Architektur" auf Vektorebene verschmelzen?'
                      : 'Semantic vectors are mathematical representations of meaning. What happens when we merge "cat" + "architecture" at the vector level?' }}
                  </div>
                </div>

                <div class="experiment-card partial-elimination">
                  <h3>Partial Elimination</h3>
                  <p>{{ currentLanguage === 'de'
                    ? 'Entferne gezielt Teile eines semantischen Vektors und beobachte, was übrig bleibt.'
                    : 'Selectively remove parts of a semantic vector and observe what remains.' }}</p>
                  <div class="tech-detail">
                    <strong>{{ currentLanguage === 'de' ? 'Technisch:' : 'Technical:' }}</strong>
                    {{ currentLanguage === 'de'
                      ? 'Wenn du von "roter Apfel" die "Röte" entfernst – was bleibt? Diese Experimente zeigen, wie Bedeutung in KI-Modellen repräsentiert wird.'
                      : 'If you remove "redness" from "red apple" – what remains? These experiments show how meaning is represented in AI models.' }}
                  </div>
                </div>
              </section>
            </div>

            <!-- Workshop Tab -->
            <div v-if="activeTab === 'workshop'" class="tab-content">
              <section class="workshop-section">
                <h2>{{ currentLanguage === 'de' ? 'Für Pädagog:innen' : 'For Educators' }}</h2>

                <div class="workshop-intro">
                  <p>{{ currentLanguage === 'de'
                    ? 'AI4ArtsEd ist für den Einsatz in Workshops und Unterricht konzipiert. Hier einige Hinweise für die Begleitung.'
                    : 'AI4ArtsEd is designed for use in workshops and teaching. Here are some tips for facilitation.' }}</p>
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

                <div class="contact-box">
                  <h3>{{ currentLanguage === 'de' ? 'Kontakt' : 'Contact' }}</h3>
                  <p>{{ currentLanguage === 'de'
                    ? 'Für Fragen zur Nutzung in Bildungskontexten:'
                    : 'For questions about use in educational contexts:' }}</p>
                  <a href="mailto:vanessa.baumann@fau.de">vanessa.baumann@fau.de</a>
                </div>
              </section>
            </div>

            <!-- FAQ Tab -->
            <div v-if="activeTab === 'faq'" class="tab-content">
              <section class="faq-section">
                <h2>{{ currentLanguage === 'de' ? 'Häufige Fragen' : 'Frequently Asked Questions' }}</h2>

                <div class="faq-item">
                  <h3 class="faq-question">{{ currentLanguage === 'de' ? 'Wie lange dauert die Bildgenerierung?' : 'How long does image generation take?' }}</h3>
                  <p class="faq-answer">{{ currentLanguage === 'de'
                    ? 'Die Dauer hängt vom gewählten Modell und der Komplexität des Prompts ab. In der Regel dauert es zwischen 20 Sekunden und 2 Minuten. Während dieser Zeit kannst du den Fortschritt beobachten.'
                    : 'The duration depends on the selected model and the complexity of the prompt. Usually it takes between 20 seconds and 2 minutes. During this time you can observe the progress.' }}</p>
                </div>

                <div class="faq-item">
                  <h3 class="faq-question">{{ currentLanguage === 'de' ? 'Was passiert mit meinen Eingaben?' : 'What happens to my inputs?' }}</h3>
                  <p class="faq-answer">{{ currentLanguage === 'de'
                    ? 'Generierte Inhalte werden zu Forschungszwecken gespeichert – sie helfen uns, die Plattform zu verbessern. Hochgeladene Bilder werden nicht dauerhaft gespeichert. Es werden keine personenbezogenen Daten erfasst.'
                    : 'Generated content is saved for research purposes – it helps us improve the platform. Uploaded images are not permanently stored. No personal data is collected.' }}</p>
                </div>

                <div class="faq-item">
                  <h3 class="faq-question">{{ currentLanguage === 'de' ? 'Was sind die Sicherheitsstufen?' : 'What are the safety levels?' }}</h3>
                  <p class="faq-answer">{{ currentLanguage === 'de'
                    ? 'Es gibt drei Stufen: Kinder, Jugend und Erwachsene. Sie bestimmen, welche Inhalte generiert werden können. Die Stufe wird von der betreuenden Person eingestellt.'
                    : 'There are three levels: Kids, Youth, and Adults. They determine what content can be generated. The level is set by the supervising person.' }}</p>
                </div>

                <div class="faq-item">
                  <h3 class="faq-question">{{ currentLanguage === 'de' ? 'Kann ich eigene Stile trainieren?' : 'Can I train my own styles?' }}</h3>
                  <p class="faq-answer">{{ currentLanguage === 'de'
                    ? 'Ja, im LoRA Training Studio kannst du mit eigenen Beispielbildern einen Stil trainieren, der dann für die Bildgenerierung verfügbar ist.'
                    : 'Yes, in the LoRA Training Studio you can train a style with your own example images, which then becomes available for image generation.' }}</p>
                </div>

                <div class="contact-section">
                  <h3>{{ currentLanguage === 'de' ? 'Noch Fragen?' : 'Still have questions?' }}</h3>
                  <p>{{ currentLanguage === 'de'
                    ? 'Frag Träshy direkt in der Anwendung, oder schreibe an: '
                    : 'Ask Träshy directly in the application, or write to: ' }}<a href="mailto:vanessa.baumann@fau.de">vanessa.baumann@fau.de</a></p>
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

const tabs = [
  { id: 'welcome', labelDe: 'Willkommen', labelEn: 'Welcome' },
  { id: 'start', labelDe: 'Anleitung', labelEn: 'Guide' },
  { id: 'pedagogy', labelDe: 'Pädagogik', labelEn: 'Pedagogy' },
  { id: 'experiments', labelDe: 'Experimente', labelEn: 'Experiments' },
  { id: 'workshop', labelDe: 'Workshop', labelEn: 'Workshop' },
  { id: 'faq', labelDe: 'Fragen', labelEn: 'FAQ' }
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

/* FAQ Section */
.faq-section h2 {
  margin-bottom: 1.25rem;
}

.faq-item {
  padding: 1.25rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  margin-bottom: 0.75rem;
}

.faq-question {
  margin: 0 0 0.5rem 0;
  color: #4CAF50;
  font-size: 0.95rem;
}

.faq-answer {
  margin: 0;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.6;
  font-size: 0.95rem;
}

.contact-section {
  margin-top: 1.5rem;
  padding: 1.25rem;
  background: rgba(76, 175, 80, 0.1);
  border-radius: 10px;
  text-align: center;
}

.contact-section h3 {
  margin: 0 0 0.5rem 0;
  color: #ffffff;
  font-size: 1rem;
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
