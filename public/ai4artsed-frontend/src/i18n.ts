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
      retry: 'Erneut versuchen',
      cancel: 'Abbrechen'
    },
    gallery: {
      title: 'Meine Favoriten',
      empty: 'Noch keine Favoriten',
      favorite: 'Zu Favoriten',
      unfavorite: 'Aus Favoriten entfernen',
      continue: 'Weiterentwickeln',
      restore: 'Wiederherstellen'
    },
    settings: {
      authRequired: 'Authentifizierung erforderlich',
      authPrompt: 'Bitte geben Sie das Passwort ein, um auf die Einstellungen zuzugreifen:',
      passwordPlaceholder: 'Passwort eingeben...',
      authenticate: 'Anmelden',
      authenticating: 'Authentifiziere...'
    },
    pipeline: {
      yourInput: 'Dein Input',
      result: 'Ergebnis',
      generatedMedia: 'Erzeugtes Bild'
    },
    nav: {
      about: 'Über das Projekt',
      impressum: 'Impressum',
      privacy: 'Datenschutz',
      docs: 'Dokumentation',
      language: 'Sprache wechseln',
      settings: 'Einstellungen',
      canvas: 'Canvas Workflow'
    },
    canvas: {
      title: 'Canvas Workflow',
      newWorkflow: 'Neuer Workflow',
      importWorkflow: 'Importieren',
      exportWorkflow: 'Exportieren',
      execute: 'Ausführen',
      ready: 'Bereit',
      errors: 'Fehler',
      discardWorkflow: 'Aktuellen Workflow verwerfen?',
      importError: 'Fehler beim Importieren der Datei',
      selectTransformation: 'Transformation wählen',
      selectOutput: 'Ausgabe-Modell wählen',
      search: 'Suchen...',
      noResults: 'Keine Ergebnisse gefunden',
      dragHint: 'Klicke oder ziehe Module auf die Arbeitsfläche',
      editNameHint: '(doppelklicken zum Bearbeiten)'
    },
    about: {
      title: 'Über AI4ArtsEd',
      intro: 'AI4ArtsEd ist eine pädagogisch-künstlerische Experimentierplattform für den kreativen Einsatz von Künstlicher Intelligenz in der kulturellen Bildung.',
      project: {
        title: 'Das Projekt',
        description: 'KI verändert Gesellschaft und Arbeitswelt; sie wird zunehmend Thema der Bildung. Das Projekt sondiert Chancen, Bedingungen und Grenzen des pädagogischen Einsatzes künstlicher Intelligenz (KI) in kulturell diversitätssensiblen Settings der Kulturellen Bildung (KuBi).',
        paragraph2: 'In drei Teilprojekten – Allgemeinpädagogik (TPap), Informatik (TPinf) und Kunstpädagogik (TPkp) – greifen kreativitätsorientierte pädagogische KI-Praxisforschung und informatische KI-Konzeption und Programmierung in enger Kooperation ineinander. Das Projekt bezieht hierzu von Beginn an künstlerisch-pädagogische Praxisakteure in den Gestaltungsprozess systematisch ein; es agiert als Brücke zwischen der professionellen (qualitätsbezogenen, ästhetischen, ethischen und wertebezogenen) pädagogisch-praktischen Implementation einerseits und dem Umsetzungs- und Trainingsprozess des informatischen Teilprojekts andererseits.',
        paragraph3: 'Aus einem insgesamt ca. zweijährigen partizipativen Designprozess soll eine Opensource-KI-Technologie hervorgehen, die auslotet, inwieweit KI-Systeme unter günstigen Realbedingungen bereits auf ihrer Strukturebene künstlerisch-pädagogische Maßgaben einbeziehen können.',
        paragraph4: 'Dabei stehen a) die zukünftige Anwendbarkeit und der Mehrgewinn hochinnovativer Technologien für die Kulturelle Bildung im Zentrum, b) Reichweite und Grenzen der KI-Literacy von Lehrenden und Lernenden, sowie c) die übergreifende Frage nach der Bewertbarkeit und Bewertung der Transformation pädagogischer Settings durch komplexe nonhumane Akteure im Sinne einer pädagogischen Ethik und Technikfolgenabschätzung.',
        moreInfo: 'Weitere Informationen:'
      },
      subproject: {
        title: 'Teilprojekt "Allgemeine Pädagogik"',
        description: 'Das Teilprojekt "Allgemeine Pädagogik" beforscht im Rahmen der dem Verbundprojekt gemeinsamen Fragestellung Möglichkeiten und Grenzen eines auf partizipativer Praxisforschung aufsetzenden künstlerisch-pädagogischen KI-Designprozesses. Es führt zu diesem Zweck im ersten Projektjahr eine Serie von Recherchen, Analysen, Expert_innenworkshops und OpenSpaces durch. Die nachfolgende, in mehreren Zyklen als Feedback-Loop angelegte Projektphase erforscht den Einsatz eines Prototypen mit pädagogischen Prakter_innen und Artist-Educators v.a. der non-formalen kulturellen Bildung als relationalen und kollektiven transformativen Bildungsprozess.'
      },
      team: {
        title: 'Team',
        projectLead: 'Projektleitung',
        leadName: 'Prof. Dr. Benjamin Jörissen',
        leadInstitute: 'Institut für Pädagogik',
        leadChair: 'Lehrstuhl für Pädagogik mit dem Schwerpunkt Kultur und ästhetische Bildung',
        leadUnesco: 'UNESCO Chair in Digital Culture and Arts in Education',
        researcher: 'Wissenschaftliche Mitarbeiterin',
        researcherName: 'Vanessa Baumann',
        researcherInstitute: 'Institut für Pädagogik',
        researcherChair: 'Lehrstuhl für Pädagogik mit dem Schwerpunkt Kultur und ästhetische Bildung',
        researcherUnesco: 'UNESCO Chair in Digital Culture and Arts in Education'
      },
      funding: {
        title: 'Gefördert vom'
      }
    },
    legal: {
      impressum: {
        title: 'Impressum',
        publisher: 'Herausgeber',
        represented: 'Vertreten durch den Präsidenten',
        responsible: 'Inhaltlich verantwortlich gem. § 18 Abs. 2 MStV',
        authority: 'Zuständige Aufsichtsbehörde',
        moreInfo: 'Weitere Informationen',
        moreInfoText: 'Das vollständige Impressum der FAU:',
        funding: 'Gefördert vom'
      },
      privacy: {
        title: 'Datenschutzerklärung',
        notice: 'Hinweis: Generierte Inhalte werden zu Forschungszwecken auf dem Server gespeichert. Es werden keine User- oder IP-Daten erfasst. Hochgeladene Bilder werden nicht gespeichert.',
        usage: 'Die Nutzung dieser Plattform ist ausschließlich eingetragenen Kooperationspartnern des AI4ArtsEd-Projekts erlaubt. Es gelten die in diesem Rahmen vereinbarten datenschutzbezogenen Absprachen. Haben Sie hierzu Fragen, melden Sie sich bitte bei vanessa.baumann@fau.de.'
      }
    },
    docs: {
      title: 'Dokumentation & Anleitung',
      intro: {
        title: 'Willkommen',
        content: 'Kreative Experimente mit KI-Transformationen.'
      },
      gettingStarted: {
        title: 'Erste Schritte',
        step1: 'Eigenschaften aus Quadranten wählen',
        step2: 'Text oder Bild eingeben',
        step3: 'Transformation starten'
      },
      modes: {
        title: 'Modi',
        mode1: { name: 'Direkt', desc: 'Schnelle Experimente' },
        mode2: { name: 'Text', desc: 'Textbasierte Transformationen' },
        mode3: { name: 'Bild', desc: 'Bildbasierte Verfahren' }
      },
      support: {
        title: 'Unterstützung',
        content: 'Bei Fragen:'
      },
      wikipedia: {
        title: 'Wikipedia-Recherche',
        subtitle: 'Wissen über die Welt als Teil künstlerischer Prozesse',
        feature: 'Künstlerische Prozesse erfordern nicht nur ästhetisches Wissen, sondern auch Wissen über Sachverhalte in der Welt. Die KI recherchiert während der Transformation auf Wikipedia, um faktische Informationen zu finden.',
        languages: 'Über 70 Sprachen werden unterstützt',
        languagesDesc: 'Die KI wählt automatisch die passende sprachliche Wikipedia für das jeweilige Thema:',
        examples: {
          nigeria: 'Thema über Nigeria → Hausa, Yoruba, Igbo oder Englisch',
          india: 'Thema über Indien → Hindi, Tamil, Bengali oder andere regionale Sprachen',
          indigenous: 'Indigene Kulturen → Quechua, Māori, Inuktitut usw.'
        },
        why: 'Transparenz: Was weiß die KI?',
        whyDesc: 'Das System zeigt alle Recherche-Versuche an: Sowohl gefundene Artikel (als anklickbare Links) als auch Begriffe, zu denen nichts gefunden wurde. So wird sichtbar, was die KI zu wissen meint – und was nicht.',
        culturalRespect: 'Einladung zum Selbst-Recherchieren',
        culturalRespectDesc: 'Die angezeigten Wikipedia-Links sind eine Einladung, selbst mehr zu erfahren. Klicken Sie auf die Links, um die Quellen zu prüfen und Ihr eigenes Wissen zu erweitern.',
        limitations: 'Die KI-Recherche ist ein Hilfsmittel, kein Ersatz für eigene Auseinandersetzung mit dem Thema.'
      }
    },
    multiImage: {
      image1Label: 'Bild 1',
      image2Label: 'Bild 2 (optional)',
      image3Label: 'Bild 3 (optional)',
      contextLabel: 'Sage was Du mit den Bildern machen möchtest',
      contextPlaceholder: 'z.B. Füge das Haus aus Bild 2 und das Pferd aus Bild 3 in Bild 1 ein. Behalte Farben und Stil von Bild 1 bei.',
      modeTitle: 'Mehrere Bilder → Bild',
      selectConfig: 'Wähle dein Modell:',
      generating: 'Bilder werden fusioniert...'
    },
    imageTransform: {
      imageLabel: 'Dein Bild',
      contextLabel: 'Sage was Du an dem Bild verändern möchtest',
      contextPlaceholder: 'z.B. Verwandle es in ein Ölgemälde... Mache es bunter... Füge einen Sonnenuntergang hinzu...'
    },
    textTransform: {
      inputLabel: 'Deine Idee: Worum soll es gehen?',
      inputPlaceholder: 'z.B. Ein Fest in meiner Straße: ...',
      contextLabel: 'Bestimme Regeln, Material, Besonderheiten',
      contextPlaceholder: 'z.B. Beschreibe alles so, wie es die Vögel auf den Bäumen wahrnehmen!',
      resultLabel: 'Idee + Regeln = Prompt',
      resultPlaceholder: 'Prompt erscheint nach Start-Klick (oder eigenen Text eingeben)',
      optimizedLabel: 'Modell-Optimierter Prompt',
      optimizedPlaceholder: 'Der optimierte Prompt erscheint nach Modellauswahl.'
    },
    training: {
      info: {
        title: 'Hinweis zum LoRA-Training',
        description: 'Dieses eingebaute Training ist für schnelle Tests gedacht.',
        limitations: 'Einschränkungen',
        limitationDuration: 'Training dauert 1-3 Stunden',
        limitationBlocking: 'Blockiert die Bildgenerierung während des Trainings',
        limitationConfig: 'Begrenzte Konfigurationsmöglichkeiten',
        showMore: 'Mehr erfahren',
        showLess: 'Weniger anzeigen'
      }
    },
    splitCombine: {
      infoTitle: 'Split & Combine - Semantische Vektorfusion',
      infoDescription: 'Dieser Workflow fusioniert zwei Prompts auf der Ebene semantischer Vektoren. Das Ergebnis ist keine einfache Mischung, sondern eine tiefere mathematische Verbindung der Bedeutungsräume.',
      purposeTitle: 'Pädagogischer Zweck',
      purposeText: 'Erkunde, wie KI-Modelle Bedeutung als Zahlenräume repräsentieren. Was passiert, wenn wir verschiedene Konzepte mathematisch verschmelzen?',
      techTitle: 'Technische Details',
      techText: 'Modell: SD3.5 Large | Encoder: DualCLIP (CLIP-G + T5-XXL)'
    },
    partialElimination: {
      infoTitle: 'Partial Elimination - Vektor-Dekonstruktion',
      infoDescription: 'Dieser Workflow manipuliert gezielt Teile des semantischen Vektors. Durch das Eliminieren bestimmter Dimensionen können wir beobachten, welche Aspekte der Bedeutung verloren gehen.',
      purposeTitle: 'Pädagogischer Zweck',
      purposeText: 'Verstehe, wie Bedeutung in verschiedenen Dimensionen des Vektorraums kodiert ist. Was bleibt übrig, wenn wir Teile "ausschalten"?',
      techTitle: 'Technische Details',
      techText: 'Modell: SD3.5 Large | Encoder: TripleCLIP (CLIP-L + CLIP-G + T5-XXL)',
      encoderLabel: 'Text-Encoder',
      modeLabel: 'Eliminationsmodus',
      dimensionRange: 'Dimensions-Bereich',
      selected: 'Ausgewählt',
      dimensions: 'Dimensionen',
      emptyTitle: 'Warte auf Generierung...',
      emptySubtitle: 'Die Ergebnisse erscheinen hier',
      referenceLabel: 'Referenzbild',
      referenceDesc: 'Unmanipulierte Ausgabe (Original)',
      innerLabel: 'Innerer Bereich eliminiert',
      outerLabel: 'Äußerer Bereich eliminiert'
    },
    surrealizer: {
      infoTitle: 'Surrealizer - Dual-Encoder Fusion',
      infoDescription: 'Dieser Workflow nutzt zwei verschiedene Text-Encoder (CLIP und T5) und verschmilzt ihre Outputs. Jeder Encoder "versteht" Text anders - CLIP durch Bild-Text-Paare, T5 durch reine Sprachmodellierung.',
      purposeTitle: 'Pädagogischer Zweck',
      purposeText: 'Erkunde die verschiedenen "Weltbilder" unterschiedlicher KI-Architekturen. Wie verändert sich die visuelle Interpretation je nach Encoder-Gewichtung?',
      techTitle: 'Technische Details',
      techText: 'Modell: SD3.5 Large | Encoder: Separate CLIP-L + T5-XXL (für Dual-Fusion)'
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
      retry: 'Retry',
      cancel: 'Cancel'
    },
    gallery: {
      title: 'My Favorites',
      empty: 'No favorites yet',
      favorite: 'Add to favorites',
      unfavorite: 'Remove from favorites',
      continue: 'Continue editing',
      restore: 'Restore session'
    },
    settings: {
      authRequired: 'Authentication Required',
      authPrompt: 'Please enter the password to access settings:',
      passwordPlaceholder: 'Enter password...',
      authenticate: 'Sign In',
      authenticating: 'Authenticating...'
    },
    pipeline: {
      yourInput: 'Your input',
      result: 'Result',
      generatedMedia: 'Generated image'
    },
    nav: {
      about: 'About',
      impressum: 'Imprint',
      privacy: 'Privacy',
      docs: 'Documentation',
      language: 'Switch language',
      settings: 'Settings',
      canvas: 'Canvas Workflow'
    },
    canvas: {
      title: 'Canvas Workflow',
      newWorkflow: 'New Workflow',
      importWorkflow: 'Import',
      exportWorkflow: 'Export',
      execute: 'Execute',
      ready: 'Ready',
      errors: 'errors',
      discardWorkflow: 'Discard current workflow?',
      importError: 'Failed to import file',
      selectTransformation: 'Select Transformation',
      selectOutput: 'Select Output Model',
      search: 'Search...',
      noResults: 'No results found',
      dragHint: 'Click or drag modules onto the canvas',
      editNameHint: '(double-click to edit)'
    },
    about: {
      title: 'About AI4ArtsEd',
      intro: 'AI4ArtsEd is a pedagogical-artistic experimentation platform for the creative use of artificial intelligence in cultural education.',
      project: {
        title: 'The Project',
        description: 'AI is transforming society and the world of work; it is increasingly becoming a subject of education. The project explores opportunities, conditions, and limits of the pedagogical use of artificial intelligence (AI) in culturally diversity-sensitive settings of cultural education.',
        paragraph2: 'In three sub-projects – General Pedagogy (TPap), Computer Science (TPinf), and Art Education (TPkp) – creativity-oriented pedagogical AI practice research and computer science AI conception and programming interlock in close cooperation. From the outset, the project systematically involves artistic-pedagogical practitioners in the design process; it acts as a bridge between professional (quality-related, aesthetic, ethical, and value-based) pedagogical-practical implementation on the one hand and the implementation and training process of the computer science sub-project on the other.',
        paragraph3: 'A participatory design process spanning approximately two years aims to produce an open-source AI technology that explores the extent to which AI systems can already incorporate artistic-pedagogical principles at their structural level under favorable real-world conditions.',
        paragraph4: 'The focus is on a) the future applicability and added value of highly innovative technologies for cultural education, b) the scope and limits of AI literacy among teachers and learners, and c) the overarching question of the assessability and evaluation of the transformation of pedagogical settings by complex non-human actors in terms of pedagogical ethics and technology assessment.',
        moreInfo: 'More information:'
      },
      subproject: {
        title: 'Sub-project "General Pedagogy"',
        description: 'The sub-project "General Pedagogy" researches possibilities and limits of an artistic-pedagogical AI design process based on participatory practice research within the framework of the joint research question of the collaborative project. For this purpose, it conducts a series of research, analyses, expert workshops, and open spaces in the first project year. The subsequent project phase, designed as a feedback loop in several cycles, explores the use of a prototype with pedagogical practitioners and artist-educators, particularly in non-formal cultural education, as a relational and collective transformative educational process.'
      },
      team: {
        title: 'Team',
        projectLead: 'Project Lead',
        leadName: 'Prof. Dr. Benjamin Jörissen',
        leadInstitute: 'Institute of Education',
        leadChair: 'Chair of Education with Focus on Culture and Aesthetic Education',
        leadUnesco: 'UNESCO Chair in Digital Culture and Arts in Education',
        researcher: 'Research Associate',
        researcherName: 'Vanessa Baumann',
        researcherInstitute: 'Institute of Education',
        researcherChair: 'Chair of Education with Focus on Culture and Aesthetic Education',
        researcherUnesco: 'UNESCO Chair in Digital Culture and Arts in Education'
      },
      funding: {
        title: 'Funded by'
      }
    },
    legal: {
      impressum: {
        title: 'Imprint',
        publisher: 'Publisher',
        represented: 'Represented by the President',
        responsible: 'Responsible for content',
        authority: 'Supervisory Authority',
        moreInfo: 'Additional Information',
        moreInfoText: 'Complete imprint of FAU:',
        funding: 'Funded by'
      },
      privacy: {
        title: 'Privacy Policy',
        notice: 'Notice: Generated content is stored on the server for research purposes. No user or IP data is collected. Uploaded images are not stored.',
        usage: 'Use of this platform is exclusively permitted for registered cooperation partners of the AI4ArtsEd project. The data protection agreements made in this context apply. If you have any questions, please contact vanessa.baumann@fau.de.'
      }
    },
    docs: {
      title: 'Documentation & Guide',
      intro: {
        title: 'Welcome',
        content: 'Creative experiments with AI transformations.'
      },
      gettingStarted: {
        title: 'Getting Started',
        step1: 'Select properties from quadrants',
        step2: 'Enter text or image',
        step3: 'Start transformation'
      },
      modes: {
        title: 'Modes',
        mode1: { name: 'Direct', desc: 'Quick experiments' },
        mode2: { name: 'Text', desc: 'Text-based transformations' },
        mode3: { name: 'Image', desc: 'Image-based procedures' }
      },
      support: {
        title: 'Support',
        content: 'For questions:'
      },
      wikipedia: {
        title: 'Wikipedia Research',
        subtitle: 'Knowledge about the world as part of artistic processes',
        feature: 'Artistic processes require not only aesthetic knowledge, but also knowledge about facts in the world. The AI researches Wikipedia during transformation to find factual information.',
        languages: 'Over 70 languages are supported',
        languagesDesc: 'The AI automatically chooses the appropriate language Wikipedia for each topic:',
        examples: {
          nigeria: 'Topic about Nigeria → Hausa, Yoruba, Igbo, or English',
          india: 'Topic about India → Hindi, Tamil, Bengali, or other regional languages',
          indigenous: 'Indigenous cultures → Quechua, Māori, Inuktitut, etc.'
        },
        why: 'Transparency: What does the AI know?',
        whyDesc: 'The system shows all research attempts: Both found articles (as clickable links) and terms for which nothing was found. This makes visible what the AI thinks it knows – and what it does not.',
        culturalRespect: 'Invitation to research yourself',
        culturalRespectDesc: 'The displayed Wikipedia links are an invitation to learn more yourself. Click on the links to check the sources and expand your own knowledge.',
        limitations: 'AI research is an aid, not a substitute for your own engagement with the topic.'
      }
    },
    multiImage: {
      image1Label: 'Image 1',
      image2Label: 'Image 2 (optional)',
      image3Label: 'Image 3 (optional)',
      contextLabel: 'Describe what you want to do with the images',
      contextPlaceholder: 'e.g. Insert the house from image 2 and the horse from image 3 into image 1. Preserve colors and style from image 1.',
      modeTitle: 'Multiple Images → Image',
      selectConfig: 'Choose your model:',
      generating: 'Images are being fused...'
    },
    imageTransform: {
      imageLabel: 'Your Image',
      contextLabel: 'Describe what you want to change in the image',
      contextPlaceholder: 'e.g. Transform it into an oil painting... Make it more colorful... Add a sunset...'
    },
    textTransform: {
      inputLabel: 'Your Idea: What should this be about?',
      inputPlaceholder: 'e.g. A festival in my street: ...',
      contextLabel: 'Define rules, materials, special features',
      contextPlaceholder: 'e.g. Describe everything as the birds in the trees perceive it!',
      resultLabel: 'Idea + Rules = Prompt',
      resultPlaceholder: 'Prompt will appear after clicking start (or enter your own text)',
      optimizedLabel: 'Model-Optimized Prompt',
      optimizedPlaceholder: 'The optimized prompt will appear after model selection.'
    },
    training: {
      info: {
        title: 'About LoRA Training',
        description: 'This built-in training is designed for quick tests.',
        limitations: 'Limitations',
        limitationDuration: 'Training takes 1-3 hours',
        limitationBlocking: 'Blocks image generation during training',
        limitationConfig: 'Limited configuration options',
        showMore: 'Learn more',
        showLess: 'Show less'
      }
    },
    splitCombine: {
      infoTitle: 'Split & Combine - Semantic Vector Fusion',
      infoDescription: 'This workflow fuses two prompts at the semantic vector level. The result is not a simple blend, but a deeper mathematical connection of meaning spaces.',
      purposeTitle: 'Pedagogical Purpose',
      purposeText: 'Explore how AI models represent meaning as numerical spaces. What happens when we mathematically merge different concepts?',
      techTitle: 'Technical Details',
      techText: 'Model: SD3.5 Large | Encoder: DualCLIP (CLIP-G + T5-XXL)'
    },
    partialElimination: {
      infoTitle: 'Partial Elimination - Vector Deconstruction',
      infoDescription: 'This workflow specifically manipulates parts of the semantic vector. By eliminating certain dimensions, we can observe which aspects of meaning are lost.',
      purposeTitle: 'Pedagogical Purpose',
      purposeText: 'Understand how meaning is encoded across different dimensions of the vector space. What remains when we "switch off" parts?',
      techTitle: 'Technical Details',
      techText: 'Model: SD3.5 Large | Encoder: TripleCLIP (CLIP-L + CLIP-G + T5-XXL)',
      encoderLabel: 'Text Encoder',
      modeLabel: 'Elimination Mode',
      dimensionRange: 'Dimension Range',
      selected: 'Selected',
      dimensions: 'Dimensions',
      emptyTitle: 'Waiting for generation...',
      emptySubtitle: 'Results will appear here',
      referenceLabel: 'Reference Image',
      referenceDesc: 'Unmanipulated output (original)',
      innerLabel: 'Inner range eliminated',
      outerLabel: 'Outer range eliminated'
    },
    surrealizer: {
      infoTitle: 'Surrealizer - Dual-Encoder Fusion',
      infoDescription: 'This workflow uses two different text encoders (CLIP and T5) and fuses their outputs. Each encoder "understands" text differently - CLIP through image-text pairs, T5 through pure language modeling.',
      purposeTitle: 'Pedagogical Purpose',
      purposeText: 'Explore the different "worldviews" of different AI architectures. How does the visual interpretation change depending on encoder weighting?',
      techTitle: 'Technical Details',
      techText: 'Model: SD3.5 Large | Encoder: Separate CLIP-L + T5-XXL (for dual fusion)'
    }
  }
}

export default createI18n({
  legacy: false,
  locale: 'de', // Default to German
  fallbackLocale: 'en',
  messages
})
