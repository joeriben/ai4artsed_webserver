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
        ? 'Die Plattform ist multimodal: Du kannst nicht nur Bilder erzeugen, sondern auch Video, Audio, Musik und generativen Code. Wähle ein Ausgabemedium und dann ein Modell. Welche Modelle verfügbar sind, hängt vom jeweiligen System und den angebundenen Backends ab.'
        : 'The platform is multimodal: You can generate not only images, but also video, audio, music, and generative code. Choose an output medium and then a model. Which models are available depends on the specific system and its connected backends.' }}</p>
      <div class="mode-list">
        <div class="mode-item">
          <strong>{{ currentLanguage === 'de' ? 'Bildmodelle' : 'Image Models' }}</strong>
          <p>{{ currentLanguage === 'de'
            ? 'Z.B. Stable Diffusion 3.5 (lokal), GPT Image, Gemini, QWEN (Cloud-APIs). Verschiedene Modelle erzeugen aus demselben Prompt sehr unterschiedliche Ergebnisse – ein guter Ausgangspunkt für vergleichende Erkundung.'
            : 'E.g. Stable Diffusion 3.5 (local), GPT Image, Gemini, QWEN (cloud APIs). Different models produce very different results from the same prompt – a good starting point for comparative exploration.' }}</p>
        </div>
        <div class="mode-item">
          <strong>{{ currentLanguage === 'de' ? 'Video- und Audio-Modelle' : 'Video and Audio Models' }}</strong>
          <p>{{ currentLanguage === 'de'
            ? 'Erzeugen szenische Bewegtbilder bzw. Klänge und Musik aus Textbeschreibungen.'
            : 'Generate scenic moving images or sounds and music from text descriptions.' }}</p>
        </div>
        <div class="mode-item">
          <strong>p5.js / Tone.js</strong>
          <p>{{ currentLanguage === 'de'
            ? 'Hier erzeugt das LLM ausführbaren Code, der visuelle (p5.js) oder auditive (Tone.js) Ergebnisse generiert. Die Ergebnisse sind algorithmische Kompositionen: geometrische Formen, Muster, Animationen oder synthetische Klanglandschaften – in der Tradition generativer Computerkunst, wie sie seit den 1960er Jahren existiert. Der Unterschied: Statt den Code selbst zu schreiben, beschreibst du, was entstehen soll, und das LLM übersetzt deine Beschreibung in lauffähigen Code. Die Bilder und Klänge entstehen dann live im Browser.'
            : 'Here the LLM generates executable code that produces visual (p5.js) or auditive (Tone.js) results. The results are algorithmic compositions: geometric shapes, patterns, animations, or synthetic soundscapes – in the tradition of generative computer art, which has existed since the 1960s. The difference: instead of writing the code yourself, you describe what should emerge, and the LLM translates your description into runnable code. The images and sounds are then created live in the browser.' }}</p>
        </div>
      </div>
      <p class="note">{{ currentLanguage === 'de'
        ? 'Probiere denselben Prompt mit verschiedenen Modellen aus – innerhalb eines Mediums oder medienübergreifend. So lernst du, wie unterschiedlich Modelle auf dieselbe Eingabe reagieren.'
        : 'Try the same prompt with different models – within one medium or across media. This way you learn how differently models react to the same input.' }}</p>
    </div>

    <div class="step-card">
      <div class="step-header">
        <span class="step-badge">3</span>
        <h3>{{ currentLanguage === 'de' ? 'Modell-Adaption (je nach Modell)' : 'Model Adaption (depending on model)' }}</h3>
      </div>
      <p>{{ currentLanguage === 'de'
        ? 'Manche Modelle brauchen eine Adaption des Prompts, andere nicht. Das System erkennt das automatisch und zeigt dir den adaptierten Prompt an, wenn einer erzeugt wurde:'
        : 'Some models need a prompt adaption, others don\'t. The system detects this automatically and shows you the adapted prompt when one was generated:' }}</p>
      <div class="mode-list">
        <div class="mode-item">
          <strong>{{ currentLanguage === 'de' ? 'Mit Adaption' : 'With adaption' }}</strong>
          <p>{{ currentLanguage === 'de'
            ? 'Stable Diffusion 3.5 braucht "klassischen" Prompt-Stil (Stichworte, Gewichtungen). Video- und Audio-Modelle erhalten szenische bzw. auditive Beschreibungen. Schaue genau hin und passe sie an deine Vorstellungen an.'
            : 'Stable Diffusion 3.5 needs "classic" prompt style (keywords, weightings). Video and audio models receive scenic or auditive descriptions. Look closely and adjust them to match your vision.' }}</p>
        </div>
        <div class="mode-item">
          <strong>{{ currentLanguage === 'de' ? 'Ohne Adaption' : 'Without adaption' }}</strong>
          <p>{{ currentLanguage === 'de'
            ? 'GPT Image, Gemini, QWEN u.a. besitzen selbst ein mächtiges Sprachmodul und verstehen natürliche Sprache direkt.'
            : 'GPT Image, Gemini, QWEN and others have their own powerful language module and understand natural language directly.' }}</p>
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
