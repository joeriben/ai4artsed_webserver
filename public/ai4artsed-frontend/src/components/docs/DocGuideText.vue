<template>
  <section class="guide-section">
    <h2>{{ currentLanguage === 'de' ? 'Text-Transformation' : 'Text Transformation' }}</h2>

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
        <h3>{{ currentLanguage === 'de' ? 'Kreative Hilfestellung und Unterstützung' : 'Creative Guidance and Support' }}</h3>
      </div>
      <div class="step-image-display">
        <svg xmlns="http://www.w3.org/2000/svg" height="60" viewBox="0 -960 960 960" width="60" fill="currentColor" class="select-vue-icon">
          <path d="M480-60q-50 0-85-35t-35-85q0-50 35-85t85-35q50 0 85 35t35 85q0 50-35 85t-85 35Zm0-80q17 0 28.5-11.5T520-180q0-17-11.5-28.5T480-220q-17 0-28.5 11.5T440-180q0 17 11.5 28.5T480-140Zm-260-70q-50 0-85-35t-35-85q0-50 35-85t85-35q50 0 85 35t35 85q0 50-35 85t-85 35Zm520 0q-50 0-85-35t-35-85q0-50 35-85t85-35q50 0 85 35t35 85q0 50-35 85t-85 35Zm-520-80q17 0 28.5-11.5T260-330q0-17-11.5-28.5T220-370q-17 0-28.5 11.5T180-330q0 17 11.5 28.5T220-290Zm520 0q17 0 28.5-11.5T780-330q0-17-11.5-28.5T740-370q-17 0-28.5 11.5T700-330q0 17 11.5 28.5T740-290ZM220-510q-50 0-85-35t-35-85q0-50 35-85t85-35q50 0 85 35t35 85q0 50-35 85t-85 35Zm520 0q-50 0-85-35t-35-85q0-50 35-85t85-35q50 0 85 35t35 85q0 50-35 85t-85 35Zm-520-80q17 0 28.5-11.5T260-630q0-17-11.5-28.5T220-670q-17 0-28.5 11.5T180-630q0 17 11.5 28.5T220-590Zm520 0q17 0 28.5-11.5T780-630q0-17-11.5-28.5T740-670q-17 0-28.5 11.5T700-630q0 17 11.5 28.5T740-590Zm-260-70q-50 0-85-35t-35-85q0-50 35-85t85-35q50 0 85 35t35 85q0 50-35 85t-85 35Zm0-80q17 0 28.5-11.5T520-780q0-17-11.5-28.5T480-820q-17 0-28.5 11.5T440-780q0 17 11.5 28.5T480-740Z"/>
        </svg>
      </div>
      <p>{{ currentLanguage === 'de'
        ? 'In manchen Eingabefeldern siehst Du dieses Icon. Es führt Dich zu Inspirationen und Ideen für künstlerische Positionen und Materialien, Stimmungen, Verrücktheiten, und auch auf Nachhaltigkeit bezogenen Regeln zur Transformation von kreativen Ideen.'
        : 'In some input fields you will see this icon. It leads you to inspirations and ideas for artistic positions and materials, moods, craziness, and also sustainability-related rules for transforming creative ideas.' }}</p>
    </div>

    <div class="step-card">
      <div class="step-header">
        <span class="step-badge">2</span>
        <h3>{{ currentLanguage === 'de' ? 'Medien und Modelle wählen' : 'Choose Media and Models' }}</h3>
      </div>
      <p>{{ currentLanguage === 'de'
        ? 'Die Plattform ist multimodal: Du kannst nicht nur Bilder erzeugen, sondern auch Audio und Musik. Wähle ein Ausgabemedium und dann ein Modell. Das Spannende: Du kannst denselben Prompt mit verschiedenen Modellen ausprobieren – innerhalb eines Mediums oder sogar medienübergreifend. So lernst du, wie unterschiedlich Modelle auf dieselbe Eingabe reagieren.'
        : 'The platform is multimodal: You can generate not only images, but also audio and music. Choose an output medium and then a model. The exciting part: You can try the same prompt with different models – within one medium or even across media. This way you learn how differently models react to the same input.' }}</p>
    </div>

    <div class="step-card">
      <div class="step-header">
        <span class="step-badge">3</span>
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
        <span class="step-badge">4</span>
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
          ? 'Du kannst einen Prompt mit dem "Verniedlicher" verniedlichen, das Ergebnis wieder nach oben kopieren und dann eine ganz andere Regel anwenden, z.B. "Entkitscher", und dann dasselbe wieder mit "Übertreiber", und so weiter. Und zwischendurch kannst DU selbst immer wieder etwas verändern.'
          : 'You can make a prompt cute with the "Cutifier", copy the result back up and then apply a completely different rule, e.g. "De-Kitschifier", and then the same again with "Exaggerator", and so on. And in between, YOU can always change something yourself.' }}</span>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{ currentLanguage: string }>()
</script>
