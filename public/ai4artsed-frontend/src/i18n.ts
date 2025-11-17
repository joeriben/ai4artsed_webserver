import { createI18n } from 'vue-i18n'

const messages = {
  de: {
    app: {
      title: 'AI4ArtsEd DevServer',
      subtitle: 'Kreative KI-Transformationen'
    },
    form: {
      inputLabel: 'Dein Text',
      inputPlaceholder: 'z.B. Eine Blume auf der Wiese',
      schemaLabel: 'Transformationsstil',
      executeModeLabel: 'Ausführungsmodus',
      safetyLabel: 'Sicherheitsstufe',
      generateButton: 'Generieren'
    },
    schemas: {
      dada: 'Dada (Zufällig & Absurd)',
      bauhaus: 'Bauhaus (Geometrisch)',
      stillepost: 'Stille Post (Iterativ)'
    },
    executionModes: {
      eco: 'Eco (Schnell)',
      fast: 'Fast (Ausgewogen)',
      best: 'Best (Qualität)'
    },
    safetyLevels: {
      kids: 'Kinder',
      youth: 'Jugend',
      adult: 'Erwachsene'
    },
    stages: {
      pipeline_starting: 'Pipeline startet',
      translation_and_safety: 'Übersetzung & Sicherheit',
      interception: 'Transformation',
      pre_output_safety: 'Ausgabe-Sicherheit',
      media_generation: 'Bild-Generierung',
      completed: 'Abgeschlossen'
    },
    status: {
      idle: 'Bereit',
      executing: 'Pipeline läuft...',
      connectionSlow: 'Verbindung langsam, Versuch läuft...',
      completed: 'Pipeline abgeschlossen!',
      error: 'Fehler aufgetreten'
    },
    entities: {
      input: 'Eingabe',
      translation: 'Übersetzung',
      safety: 'Sicherheitscheck',
      interception: 'Transformation',
      safety_pre_output: 'Ausgabe-Sicherheit',
      media: 'Generiertes Bild'
    },
    properties: {
      chill: 'chillig',
      chaotic: 'wild',
      narrative: 'Geschichten erzählen',
      algorithmic: 'nach Regeln gehen',
      historical: 'Geschichte',
      contemporary: 'Gegenwart',
      explore: 'KI austesten',
      create: 'Kunst machen',
      playful: 'bisschen verrückt',
      serious: 'eher ernst'
    },
    language: {
      switch: 'Sprache: Deutsch',
      switchTo: 'Switch to English'
    },
    phase2: {
      title: 'Prompt-Eingabe',
      userInput: 'Dein Input',
      yourInput: 'Dein Input',
      yourIdea: 'Deine Idee: Um WAS soll es hier gehen?',
      rules: 'Deine Regeln: WIE soll Deine Idee umgesetzt werden?',
      yourInstructions: 'Deine Anweisungen',
      what: 'WAS',
      how: 'WIE',
      userInputPlaceholder: 'z.B. Eine Blume auf der Wiese',
      inputPlaceholder: 'Dein Text erscheint hier...',
      metaPrompt: 'Künstlerische Anweisung',
      instruction: 'Instruction',
      transformation: 'Künstlerische Transformation',
      metaPromptPlaceholder: 'Beschreibe die Transformation...',
      result: 'Ergebnis',
      expectedResult: 'Erwartetes Ergebnis',
      execute: 'Pipeline ausführen',
      executing: 'Läuft...',
      transforming: 'LLM transformiert...',
      startTransformation: 'Transformation starten',
      letsGo: 'Ok, leg los!',
      modified: 'Geändert',
      reset: 'Zurücksetzen',
      loadingConfig: 'Lade Konfiguration...',
      loadingMetaPrompt: 'Lade Meta-Prompt...',
      errorLoadingConfig: 'Fehler beim Laden der Konfiguration',
      errorLoadingMetaPrompt: 'Fehler beim Laden des Meta-Prompts',
      threeForces: '3 Kräfte wirken zusammen',
      twoForces: 'WAS + WIE → LLM → Ergebnis',
      yourPrompt: 'Dein Prompt:',
      writeYourText: 'Schreibe deinen Text...',
      examples: 'Beispiele',
      estimatedTime: '~12 Sekunden',
      stage12Time: '~5-10 Sekunden',
      willAppearAfterExecution: 'Wird nach Ausführung erscheinen...',
      back: 'Zurück',
      retry: 'Erneut versuchen',
      transformedPrompt: 'Transformierter Prompt',
      notYetTransformed: 'Noch nicht transformiert...',
      transform: 'Transformieren',
      reTransform: 'Noch mal anders',
      startAI: 'KI, bearbeite meine Eingabe',
      aiWorking: 'KI arbeitet...',
      continueToMedia: 'Weiter zum Bild generieren',
      readyForMedia: 'Bereit für Bildgenerierung',
      stage1: 'Stage 1: Übersetzung + Sicherheit...',
      stage2: 'Stage 2: Transformation...',
      selectMedia: 'Wähle dein Medium:',
      mediaImage: 'Bild',
      mediaAudio: 'Sound',
      mediaVideo: 'Video',
      media3D: '3D',
      comingSoon: 'Bald verfügbar',
      generateMedia: 'Start!'
    },
    phase3: {
      generating: 'Bild wird generiert...',
      generatingHint: '~30 Sekunden'
    },
    common: {
      back: 'Zurück',
      loading: 'Lädt...',
      error: 'Fehler',
      retry: 'Erneut versuchen'
    },
    pipeline: {
      yourInput: 'Dein Input',
      result: 'Ergebnis',
      generatedMedia: 'Erzeugtes Bild'
    }
  },
  en: {
    app: {
      title: 'AI4ArtsEd DevServer',
      subtitle: 'Creative AI Transformations'
    },
    form: {
      inputLabel: 'Your Text',
      inputPlaceholder: 'e.g. A flower in the meadow',
      schemaLabel: 'Transformation Style',
      executeModeLabel: 'Execution Mode',
      safetyLabel: 'Safety Level',
      generateButton: 'Generate'
    },
    schemas: {
      dada: 'Dada (Random & Absurd)',
      bauhaus: 'Bauhaus (Geometric)',
      stillepost: 'Stille Post (Iterative)'
    },
    executionModes: {
      eco: 'Eco (Fast)',
      fast: 'Fast (Balanced)',
      best: 'Best (Quality)'
    },
    safetyLevels: {
      kids: 'Kids',
      youth: 'Youth',
      adult: 'Adults'
    },
    stages: {
      pipeline_starting: 'Pipeline Starting',
      translation_and_safety: 'Translation & Safety',
      interception: 'Transformation',
      pre_output_safety: 'Output Safety',
      media_generation: 'Image Generation',
      completed: 'Completed'
    },
    status: {
      idle: 'Ready',
      executing: 'Pipeline running...',
      connectionSlow: 'Connection slow, retrying...',
      completed: 'Pipeline completed!',
      error: 'Error occurred'
    },
    entities: {
      input: 'Input',
      translation: 'Translation',
      safety: 'Safety Check',
      interception: 'Transformation',
      safety_pre_output: 'Output Safety',
      media: 'Generated Image'
    },
    properties: {
      chill: 'chill',
      chaotic: 'wild',
      narrative: 'tell stories',
      algorithmic: 'follow rules',
      historical: 'history',
      contemporary: 'present',
      explore: 'test AI',
      create: 'make art',
      playful: 'playful',
      serious: 'serious'
    },
    language: {
      switch: 'Language: English',
      switchTo: 'Zu Deutsch wechseln'
    },
    phase2: {
      title: 'Prompt Input',
      userInput: 'Your Input',
      yourInput: 'Your Input',
      yourIdea: 'Your Idea: WHAT should this be about?',
      rules: 'Your Rules: HOW should your idea be implemented?',
      yourInstructions: 'Your Instructions',
      what: 'WHAT',
      how: 'HOW',
      userInputPlaceholder: 'e.g. A flower in the meadow',
      inputPlaceholder: 'Your text appears here...',
      metaPrompt: 'Artistic Instruction',
      instruction: 'Instruction',
      transformation: 'Artistic Transformation',
      metaPromptPlaceholder: 'Describe the transformation...',
      result: 'Result',
      expectedResult: 'Expected Result',
      execute: 'Execute Pipeline',
      executing: 'Running...',
      transforming: 'LLM transforming...',
      startTransformation: 'Start Transformation',
      letsGo: 'Ok, let\'s go!',
      modified: 'Modified',
      reset: 'Reset',
      loadingConfig: 'Loading configuration...',
      loadingMetaPrompt: 'Loading meta-prompt...',
      errorLoadingConfig: 'Error loading configuration',
      errorLoadingMetaPrompt: 'Error loading meta-prompt',
      threeForces: '3 Forces Working Together',
      twoForces: 'WHAT + HOW → LLM → Result',
      yourPrompt: 'Your Prompt:',
      writeYourText: 'Write your text...',
      examples: 'Examples',
      estimatedTime: '~12 seconds',
      stage12Time: '~5-10 seconds',
      willAppearAfterExecution: 'Will appear after execution...',
      back: 'Back',
      retry: 'Retry',
      transformedPrompt: 'Transformed Prompt',
      notYetTransformed: 'Not yet transformed...',
      transform: 'Transform',
      reTransform: 'Try again differently',
      startAI: 'AI, process my input',
      aiWorking: 'AI is working...',
      continueToMedia: 'Continue to Image Generation',
      readyForMedia: 'Ready for Image Generation',
      stage1: 'Stage 1: Translation + Safety...',
      stage2: 'Stage 2: Transformation...',
      selectMedia: 'Choose your medium:',
      mediaImage: 'Image',
      mediaAudio: 'Audio',
      mediaVideo: 'Video',
      media3D: '3D',
      comingSoon: 'Coming soon',
      generateMedia: 'Start!'
    },
    phase3: {
      generating: 'Image is being generated...',
      generatingHint: '~30 seconds'
    },
    common: {
      back: 'Back',
      loading: 'Loading...',
      error: 'Error',
      retry: 'Retry'
    },
    pipeline: {
      yourInput: 'Your input',
      result: 'Result',
      generatedMedia: 'Generated image'
    }
  }
}

export default createI18n({
  legacy: false,
  locale: 'de', // Default to German
  fallbackLocale: 'en',
  messages
})
