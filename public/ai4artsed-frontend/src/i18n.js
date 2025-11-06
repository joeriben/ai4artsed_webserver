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
    language: {
      switch: 'Sprache: Deutsch',
      switchTo: 'Switch to English'
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
    language: {
      switch: 'Language: English',
      switchTo: 'Zu Deutsch wechseln'
    }
  }
}

export default createI18n({
  legacy: false,
  locale: 'de', // Default to German
  fallbackLocale: 'en',
  messages
})
