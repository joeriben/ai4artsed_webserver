import { createI18n } from 'vue-i18n'

const messages = {
  de: {
    app: {
      title: 'UCDCAE AI LAB',
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
      adult: 'Erwachsene',
      research: 'Forschung'
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
      title: 'Favoriten',  // Session 145: "Meine" redundant mit Switch
      empty: 'Noch keine Favoriten',
      favorite: 'Zu Favoriten',
      unfavorite: 'Aus Favoriten entfernen',
      continue: 'Weiterentwickeln',
      restore: 'Wiederherstellen',
      viewMine: 'Meine Favoriten',  // Session 145
      viewAll: 'Alle Favoriten'  // Session 145
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
    landing: {
      subtitlePrefix: 'Pädagogisch-künstlerische Experimentierplattform des',
      subtitleSuffix: 'für den explorativen Einsatz von generativer KI in der kulturell-ästhetischen Medienbildung',
      research: '',
      features: {
        textTransformation: {
          title: 'Text-Transformation',
          description: 'Perspektivwechsel durch KI: Finde und verändere Deine Ideen durch künstlerische Haltungen und Verfremdungen.'
        },
        imageTransformation: {
          title: 'Bild-Transformation',
          description: 'Bilder durch verschiedene Modelle und Perspektiven in neue Bilder und Videos verwandeln.'
        },
        multiImage: {
          title: 'Bildfusion',
          description: 'Mehrere Bilder kombinieren und durch KI-Modelle zu neuen Bild-Kompositionen verschmelzen.'
        },
        canvas: {
          title: 'Canvas Workflow',
          description: 'Visuelle Workflow-Komposition — Module per Drag & Drop zu eigenen KI-Pipelines verbinden.'
        },
        music: {
          title: 'Musikgenerierung',
          description: 'Experimentiere mit Musik, Sound und Lyrics.'
        },
        latentLab: {
          title: 'Latent Lab',
          description: 'Vektorraum-Forschung — Surrealisierung, Dimensionselimination, Embedding-Interpolation.'
        }
      }
    },
    research: {
      locked: 'Nur im Forschungsmodus verfügbar',
      lockedHint: 'Erfordert Safety-Level „Erwachsene" oder „Forschung" (config.py)',
      complianceTitle: 'Hinweis zum Forschungsmodus',
      complianceWarning: 'Im Forschungsmodus sind keine Sicherheitsfilter für Prompts und generierte Bilder aktiv. Es können unerwartete oder unangemessene Ergebnisse entstehen.',
      complianceAge: 'Dieser Modus ist nicht empfohlen für Personen unter 16 Jahren.',
      complianceConfirm: 'Ich bestätige, dass ich die Hinweise verstanden habe',
      complianceCancel: 'Abbrechen',
      complianceProceed: 'Fortfahren'
    },
    presetOverlay: {
      title: 'Perspektive wählen',
      close: 'Schließen'
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
      title: 'Über das UCDCAE AI LAB',
      intro: 'Das UCDCAE AI LAB ist eine pädagogisch-künstlerische Experimentierplattform des UNESCO Chair in Digital Culture and Arts in Education für den explorativen Einsatz von generativer Künstlicher Intelligenz in der kulturell-ästhetischen Medienbildung. Es wurde im Rahmen der Projekte AI4ArtsEd und COMeARTS entwickelt.',
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
        usage: 'Die Nutzung dieser Plattform ist ausschließlich eingetragenen Kooperationspartnern des UCDCAE AI LAB erlaubt. Es gelten die in diesem Rahmen vereinbarten datenschutzbezogenen Absprachen. Haben Sie hierzu Fragen, melden Sie sich bitte bei vanessa.baumann@fau.de.'
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
    safetyBadges: {
      '§86a': '§86a',
      '86a_filter': '§86a',
      age_filter: 'Altersfilter',
      dsgvo_ner: 'DSGVO',
      dsgvo_llm: 'DSGVO',
      translation: '\u2192 EN',
      fast_filter: 'Inhalt',
      llm_context_check: 'Inhalt (LLM)',
      llm_safety_check: 'Jugendschutz',
      llm_check_failed: 'Pr\u00FCfung fehlgeschlagen',
      disabled: '\u2014'
    },
    safetyBlocked: {
      vlm: 'Dein Prompt war in Ordnung, aber das erzeugte Bild wurde von einer Bildanalyse-KI als ungeeignet eingestuft. Das kann passieren \u2014 die Bildgenerierung ist nicht immer vorhersagbar. Versuche es einfach nochmal, jede Generierung ist anders!',
      para86a: 'Dein Prompt wurde blockiert, weil er Symbole oder Begriffe enth\u00E4lt, die nach deutschem Recht (\u00A786a StGB) verboten sind. Diese Regel sch\u00FCtzt uns alle vor Hass und Gewalt. Versuche es mit einem anderen Thema!',
      dsgvo: 'Dein Prompt wurde blockiert, weil er pers\u00F6nliche Daten enth\u00E4lt (z.B. echte Namen oder Adressen). Das ist durch die Datenschutzgrundverordnung (DSGVO) gesch\u00FCtzt. Verwende stattdessen Phantasienamen!',
      kids: 'Dein Prompt wurde vom Kinder-Schutzfilter blockiert. Manche Begriffe sind f\u00FCr Kinder nicht geeignet, weil sie erschreckend oder verst\u00F6rend sein k\u00F6nnen. Versuche, deine Idee mit freundlicheren Worten zu beschreiben!',
      youth: 'Dein Prompt wurde vom Jugendschutzfilter blockiert. Manche Inhalte sind auch f\u00FCr Jugendliche nicht geeignet. Versuche, deine Idee anders zu formulieren!',
      generic: 'Dein Prompt wurde vom Sicherheitssystem blockiert. Das System sch\u00FCtzt dich vor ungeeigneten Inhalten. Versuche es mit einer anderen Formulierung!',
      inputImage: 'Das hochgeladene Bild wurde von einer Bildanalyse-KI als ungeeignet eingestuft. Bitte verwende ein anderes Bild.',
      vlmSaw: 'Die Bild-KI sah',
      systemUnavailable: 'Das Sicherheitssystem (Ollama) reagiert nicht, daher kann keine weitere Verarbeitung erfolgen. Bitte den Systemadministrator kontaktieren.'
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
      infoTitle: 'Hallucinator — Extrapolation jenseits des Bekannten',
      infoDescription: 'Zwei KI-"Gehirne" lesen deinen Text: CLIP-L versteht Sprache durch Bilder, T5 versteht sie rein sprachlich. Der Regler mischt nicht einfach zwischen beiden — er schiebt das Bild weit über das hinaus, was T5 allein erzeugen würde. Die KI muss dann Vektoren interpretieren, die sie im Training nie gesehen hat. Das Ergebnis: KI-Halluzinationen — Bilder, die kein Prompt direkt erzeugen könnte.',
      purposeTitle: 'Der Regler',
      purposeText: 'α < 0: CLIP-L wird verstärkt, T5 negiert — die oberen 3328 Dimensionen (wo CLIP-L nur Nullen hat) erhalten invertierte T5-Vektoren. Die Cross-Attention-Muster im Transformer kehren sich um: visuell getriebene Halluzinationen. ◆ α = 0: reines CLIP-L — normales Bild. ◆ α = 1: reines T5-XXL — noch normal, aber andere Qualität. ◆ α > 1: Extrapolation über T5 hinaus. Bei α = 20 schiebt die Formel das Embedding 19× über T5 hinweg in unerforschten Vektorraum — sprachlich getriebene Halluzinationen. ◆ Sweet Spot: α = 15–35.',
      techTitle: 'Wie es funktioniert',
      techText: 'Dein Prompt wird getrennt durch zwei Encoder geschickt: CLIP-L (visuell trainiert, 77 Tokens, 768 Dimensionen → aufgefüllt auf 4096) und T5-XXL (sprachlich trainiert, 512 Tokens, 4096 Dimensionen). Die ersten 77 Token-Positionen werden per Formel fusioniert: (1-α)·CLIP-L + α·T5. Die restlichen T5-Tokens (78–512) bleiben unverändert als semantischer Anker — sie halten das Bild an deinem Text fest, egal wie extrem α wird. Bei α > 1 entsteht keine Mischung, sondern Extrapolation: Vektoren, die kein Training je erzeugt hat. Bei α < 0 wird T5 negiert und CLIP-L verstärkt — qualitativ andere Halluzinationen, weil die Cross-Attention-Muster im Transformer invertiert werden.',
      sliderLabel: 'Extrapolation (α)',
      sliderNormal: 'normal',
      sliderWeird: 'weird',
      sliderCrazy: 'crazy',
      sliderExtremeWeird: 'super weird',
      sliderExtremeCrazy: 'super crazy',
      sliderHint: "α<0: über CLIP hinaus {'|'} α=0: reines CLIP {'|'} α=1: reines T5 {'|'} α>1: über T5 hinaus",
      expandLabel: 'Prompt für T5 erweitern',
      expandHint: 'Dein Prompt hat wenige Wörter (~{count} CLIP-Tokens). Für optimale Halluzinationen kann die KI den T5-Kontext narrativ erweitern.',
      expandActive: 'Erweitere Prompt...',
      expandResultLabel: 'T5-Erweiterung (nur für T5-Encoder)',
      advancedLabel: 'Weitere Einstellungen',
      negativeLabel: 'Negativ-Prompt',
      negativeHint: 'Wird mit gleichem α extrapoliert. Bestimmt, woVON das Bild weg-extrapoliert wird — verschiedene Negativ-Prompts erzeugen grundlegend verschiedene Bildästhetiken.',
      cfgLabel: 'CFG Scale',
      cfgHint: 'Classifier-Free Guidance: Stärke des Prompt-Einflusses. Höher = stärkerer Effekt, weniger Variation.'
    },
    musicGeneration: {
      infoTitle: 'Musik-Generierung',
      infoDescription: 'Erstelle Musik aus Texten und Style-Tags. Die KI generiert Melodien, Rhythmen und Harmonien basierend auf deinen Lyrics und Genre-Angaben.',
      purposeTitle: 'Pädagogischer Zweck',
      purposeText: 'Erkunde wie KI musikalische Konzepte interpretiert. Wie beeinflusst die Wortwahl in den Lyrics die Melodie?',
      lyricsLabel: 'Lyrics (Text)',
      lyricsPlaceholder: '[Verse]\nDeine Lyrics hier...\n\n[Chorus]\nRefrain...',
      tagsLabel: 'Style Tags',
      tagsPlaceholder: 'pop, piano, upbeat, female vocal, 120bpm',
      selectModel: 'Wähle ein Musik-Modell:',
      generate: 'Musik generieren',
      generating: 'Musik wird generiert...'
    },
    musicGen: {
      simpleMode: 'Einfach',
      advancedMode: 'Erweitert',
      lyricsLabel: 'Lyrics',
      lyricsPlaceholder: 'Schreibe deine Song-Lyrics mit Strukturmarkern wie [Verse], [Chorus], [Bridge]...\n\nBeispiel:\n[Verse]\nde doo doo doo\nde blaa blaa blaa\n\n[Chorus]\nis all I want to sing to you',
      tagsLabel: 'Style Tags',
      tagsPlaceholder: 'Genre, Stimmung, Instrumente...\n\nBeispiel: ska, aggressive, upbeat, high definition, bass and sax trio',
      refineButton: 'Lyrics & Tags verfeinern',
      refinedLyricsLabel: 'Verfeinerte Lyrics',
      refinedLyricsPlaceholder: 'Hier erscheinen deine verfeinerten Lyrics...',
      refiningLyricsMessage: 'Die KI verfeinert deine Lyrics...',
      refinedTagsLabel: 'Verfeinerte Tags',
      refinedTagsPlaceholder: 'Hier erscheinen die verfeinerten Style Tags...',
      refiningTagsMessage: 'Die KI generiert passende Style Tags...',
      selectModel: 'Wähle ein Musik-Modell',
      generateButton: 'Musik generieren',
      quality: 'Qualität'
    },
    musicGenV2: {
      lyricsWorkshop: 'Lyrics Workshop',
      lyricsInput: 'Dein Text',
      lyricsPlaceholder: 'Schreibe Lyrics, ein Thema, Stichworte oder eine Stimmung...',
      themeToLyrics: 'Stichworte zu Songtext',
      refineLyrics: 'Songtext strukturieren',
      resultLabel: 'Ergebnis',
      resultPlaceholder: 'Hier erscheinen deine Lyrics...',
      expandingTheme: 'Die KI schreibt einen Songtext aus deinen Stichworten...',
      refiningLyrics: 'Die KI strukturiert deinen Songtext...',
      soundExplorer: 'Sound Explorer',
      suggestFromLyrics: 'Aus Lyrics vorschlagen',
      suggestingTags: 'Die KI analysiert deine Lyrics...',
      mostImportant: 'wichtigste',
      dimGenre: 'Genre',
      dimTimbre: 'Klangfarbe',
      dimGender: 'Stimme',
      dimMood: 'Stimmung',
      dimInstrument: 'Instrumente',
      dimScene: 'Szene',
      dimRegion: 'Region (UNESCO)',
      dimTopic: 'Thema',
      audioLength: 'Audio-Länge',
      generateButton: 'Musik generieren',
      selectModel: 'Modell',
      customTags: 'Eigene Tags',
      customTagsPlaceholder: 'z.B. acoustic,dreamy,summer_vibes'
    },
    latentLab: {
      tabs: {
        attention: 'Attention Cartography',
        probing: 'Feature Probing',
        algebra: 'Concept Algebra',
        fusion: 'Encoder Fusion',
        archaeology: 'Denoising Archaeology'
      },
      comingSoon: 'Dieses Tool wird in einer zukünftigen Version implementiert.',
      attention: {
        headerTitle: 'Attention Cartography — Welches Wort steuert welche Bildregion?',
        headerSubtitle: 'Für jedes Wort im Prompt zeigt eine Heatmap-Überlagerung auf dem generierten Bild, WO im Bild dieses Wort den größten Einfluss hatte. So wird sichtbar, wie das Modell semantische Konzepte räumlich verteilt.',
        explanationToggle: 'Ausführliche Erklärung anzeigen',
        explainWhatTitle: 'Was zeigt dieses Tool?',
        explainWhatText: 'Wenn ein Diffusionsmodell ein Bild erzeugt, liest es den Prompt nicht Wort für Wort ab wie eine Bauanleitung. Stattdessen verteilt ein Mechanismus namens „Attention" den Einfluss jedes Wortes auf verschiedene Bildregionen. Das Wort „Haus" beeinflusst hauptsächlich die Region, in der das Haus entsteht — aber auch benachbarte Bereiche, weil das Modell den Kontext der gesamten Szene versteht. Dieses Tool macht diese Verteilung sichtbar: Klicke auf ein Wort und sieh, welche Bildregionen aufleuchten.',
        explainHowTitle: 'Wie lese ich die Heatmap?',
        explainHowText: 'Helle, intensive Farbe = starker Einfluss des Wortes auf diese Region. Dunkle oder fehlende Farbe = wenig Einfluss. Wenn du mehrere Wörter auswählst, erscheinen sie in verschiedenen Farben. Beachte: Die Karten sind NICHT perfekt scharf begrenzt — das ist kein Fehler, sondern zeigt, dass das Modell Konzepte kontextuell und nicht isoliert verarbeitet. Ein „Haus" in einer Bauernhof-Szene hat auch etwas Einfluss auf Tiere und Felder, weil das Modell die Szene als Ganzes versteht.',
        explainReadTitle: 'Was verraten die zwei Regler?',
        explainReadText: 'Der Entrauschungsschritt-Regler zeigt, WANN im 25-schrittigen Erzeugungsprozess du die Attention betrachtest. Frühe Schritte zeigen die grobe Layoutplanung, späte die Detailzuordnung. Der Netzwerktiefe-Regler zeigt, WO im Transformer die Attention gemessen wird: Flache Schichten (nahe am Eingang) zeigen globale Kompositionsplanung, mittlere die semantische Zuordnung, tiefe die Feinabstimmung. Beide Achsen sind unabhängig — es lohnt sich, systematisch verschiedene Kombinationen zu erkunden.',
        techTitle: 'Technische Details',
        techText: 'SD3.5 verwendet einen MMDiT (Multimodal Diffusion Transformer) mit Joint Attention: Bild- und Text-Tokens bearbeiten sich gegenseitig in 24 Transformer-Blöcken. Wir ersetzen den Standard-SDPA-Prozessor durch einen manuellen Softmax(QK^T/√d)-Prozessor an 3 ausgewählten Blöcken, um die Text→Bild-Attention-Submatrix zu extrahieren. Die Maps haben 64x64 Auflösung (Patch-Grid) und werden per bilinearer Interpolation auf die Bildauflösung hochskaliert. Die Tokenisierung nutzt CLIP-L BPE — Subwort-Tokens werden automatisch zu ganzen Wörtern zusammengefasst.',
        promptLabel: 'Prompt',
        promptPlaceholder: 'z.B. Ein Haus steht in einer Landschaft, umgeben von landwirtschaftlichen Flächen, Natur und Tieren. Es sind einige Menschen zu sehen.',
        generate: 'Generieren + Analyse',
        generating: 'Bild wird generiert und Attention wird extrahiert...',
        emptyHint: 'Gib einen Prompt ein und klicke auf Generieren, um die Attention-Karten des Modells zu visualisieren.',
        advancedLabel: 'Erweiterte Einstellungen',
        negativeLabel: 'Negativ-Prompt',
        stepsLabel: 'Steps',
        cfgLabel: 'CFG',
        seedLabel: 'Seed',
        tokensLabel: 'Tokens',
        tokensHint: 'Klicke auf ein oder mehrere Wörter. Subwort-Tokens (z.B. "Ku"+"gel") werden automatisch zusammengefasst. Mehrere Wörter erscheinen in verschiedenen Farben.',
        timestepLabel: 'Entrauschungsschritt',
        timestepHint: 'Diffusionsmodelle erzeugen Bilder in 25 Schritten vom Rauschen zum Bild. Frühe Schritte legen die grobe Struktur fest, späte verfeinern Details. Dieser Regler zeigt, worauf das Modell bei welchem Schritt achtet.',
        step: 'Schritt',
        layerLabel: 'Netzwerktiefe',
        layerHint: 'Bei jedem Entrauschungsschritt durchläuft das Signal alle 24 Schichten des Transformers. Flache Schichten (nahe am Eingang) erfassen globale Komposition, mittlere die semantische Zuordnung, tiefe (nahe am Ausgang) feine Details. Beide Regler sind unabhängig: Schritt = wann im Prozess, Tiefe = wo im Netzwerk.',
        layerEarly: 'Flach (Komposition)',
        layerMid: 'Mittel (Semantik)',
        layerLate: 'Tief (Detail)',
        opacityLabel: 'Heatmap',
        opacityHint: 'Stärke der farbigen Überlagerung auf dem Bild.',
        baseImageLabel: 'Basisbild',
        baseColor: 'Farbe',
        baseBW: 'S/W',
        baseOff: 'Aus',
        baseImageHint: 'Farbe zeigt das Originalbild. S/W entsättigt es, damit Heatmap-Farben klar erkennbar sind. Aus blendet das Bild aus und zeigt nur die Attention-Karte.',
        download: 'Bild herunterladen'
      },
      probing: {
        headerTitle: 'Feature Probing — Welche Dimensionen kodieren was?',
        headerSubtitle: 'Vergleiche zwei Prompts und finde heraus, welche Embedding-Dimensionen den semantischen Unterschied kodieren. Übertrage gezielt einzelne Dimensionen, um zu sehen, wie sie das Bild verändern.',
        explanationToggle: 'Ausführliche Erklärung anzeigen',
        explainWhatTitle: 'Was zeigt dieses Tool?',
        explainWhatText: 'Jedes Wort wird vom Text-Encoder in einen hochdimensionalen Vektor umgewandelt (z.B. 4096 Dimensionen bei T5). Wenn du ein Wort im Prompt änderst — z.B. „rotes" zu „blaues" — ändern sich bestimmte Dimensionen stärker als andere. Dieses Tool zeigt dir, WELCHE Dimensionen sich am meisten ändern und lässt dich gezielt einzelne Dimensionen von Prompt B in Prompt A übertragen.',
        explainHowTitle: 'Wie funktioniert die Übertragung?',
        explainHowText: 'Im Balkendiagramm siehst du alle Dimensionen sortiert nach Differenzgröße. Mit den Rang-Reglern (Von/Bis) wählst du einen Bereich aus — z.B. nur die Top-100 oder gezielt Rang 880–920. Beim Klick auf „Übertragen" wird das Bild mit denselben Einstellungen (gleicher Seed!) neu generiert — aber mit den ausgewählten Dimensionen aus Prompt B. So siehst du exakt, was diese Dimensionen „kodieren".',
        explainReadTitle: 'Wie lese ich das Balkendiagramm?',
        explainReadText: 'Jeder Balken repräsentiert eine Embedding-Dimension. Die Länge zeigt, wie stark sich diese Dimension zwischen Prompt A und B unterscheidet. Dimensionen mit großem Unterschied sind die wahrscheinlichsten Träger der semantischen Änderung. Aber: Embeddings sind verteilt — oft braucht es mehrere Dimensionen zusammen, um eine sichtbare Änderung zu bewirken.',
        techTitle: 'Technische Details',
        techText: 'SD3.5 verwendet drei Text-Encoder: CLIP-L (768d), CLIP-G (1280d) und T5-XXL (4096d). Du kannst jeden einzeln proben. Die Differenz wird als mittlere absolute Abweichung über alle Token-Positionen berechnet: mean(abs(B-A), dim=tokens). Die Übertragung ersetzt die ausgewählten Dimensionen in allen Token-Positionen gleichzeitig.',
        promptALabel: 'Prompt A (Original)',
        promptBLabel: 'Prompt B (Vergleich)',
        promptAPlaceholder: 'z.B. Ein rotes Haus am See',
        promptBPlaceholder: 'z.B. Ein blaues Haus am See',
        encoderLabel: 'Encoder',
        encoderAll: 'Alle (empfohlen)',
        encoderClipL: 'CLIP-L (768d)',
        encoderClipG: 'CLIP-G (1280d)',
        encoderT5: 'T5-XXL (4096d)',
        analyzeBtn: 'Analysieren',
        analyzing: 'Prompts werden kodiert und verglichen...',
        transferBtn: 'Übertrage die ausgewählten Vektor-Dimensionen von Prompt B in das erzeugte Bild',
        transferring: 'Bild mit modifiziertem Embedding wird erzeugt...',
        rankFromLabel: 'Von Rang',
        rankToLabel: 'Bis Rang',
        sliderLabel: 'Dimensionen von Prompt B auswählen',
        range1Label: 'Bereich 1',
        range2Label: 'Bereich 2',
        addRange: 'Bereich hinzufügen',
        selectionDesc: '{count} Dimensionen von Prompt B ausgewählt (Rang {ranges} von {total})',
        listTitle: 'Die {count} Dimensionen von Prompt B mit der größten Differenz zu Prompt A',
        sortAsc: 'Aufsteigend sortiert',
        sortDesc: 'Absteigend sortiert',
        originalLabel: 'Original (Prompt A)',
        modifiedLabel: 'Modifiziert (Transfer von Prompt B)',
        modifiedHint: 'Wähle unten einen Rangbereich und klicke „Übertragen" — hier erscheint dann Prompt A mit den übertragenen Dimensionen aus B (gleicher Seed).',
        noDifference: 'Die Embeddings sind identisch — ändere Prompt B.',
        advancedLabel: 'Erweiterte Einstellungen',
        negativeLabel: 'Negativ-Prompt',
        stepsLabel: 'Steps',
        cfgLabel: 'CFG',
        seedLabel: 'Seed',
        selectAll: 'Alle',
        selectNone: 'Keine',
        downloadOriginal: 'Original herunterladen',
        downloadModified: 'Modifiziert herunterladen'
      },
      algebra: {
        headerTitle: 'Concept Algebra \u2014 Vektor-Arithmetik auf Bild-Embeddings',
        headerSubtitle: 'Wende die ber\u00fchmte Word2Vec-Analogie auf Bildgenerierung an: K\u00f6nig \u2212 Mann + Frau \u2248 K\u00f6nigin. Drei Prompts werden kodiert und algebraisch kombiniert.',
        explanationToggle: 'Ausf\u00fchrliche Erkl\u00e4rung anzeigen',
        explainWhatTitle: 'Was zeigt dieses Tool?',
        explainWhatText: 'Mikolov zeigte 2013, dass Word-Embeddings semantische Beziehungen als lineare Richtungen kodieren: Der Vektor von \u201eK\u00f6nig\u201c minus \u201eMann\u201c plus \u201eFrau\u201c ergibt einen Vektor nahe \u201eK\u00f6nigin\u201c. Dieses Tool \u00fcbertr\u00e4gt diese Idee auf die Text-Encoder von SD3.5: Statt einzelner W\u00f6rter manipulierst du ganze Prompt-Embeddings. Das Ergebnis ist ein Bild, das das Konzept A enth\u00e4lt, aber B durch C ersetzt hat.',
        explainHowTitle: 'Wie funktioniert die Algebra \u2014 und warum nicht einfach ein Negativ-Prompt?',
        explainHowText: 'Du gibst drei Prompts ein: A (Basis), B (subtrahieren) und C (addieren). Die Formel ist: Ergebnis = A \u2212 Skalierung\u2081\u00d7B + Skalierung\u2082\u00d7C. Mit den Skalierungsreglern steuerst du die Intensit\u00e4t: Bei 1.0 wird B vollst\u00e4ndig subtrahiert und C vollst\u00e4ndig addiert. Bei 0.5 nur zur H\u00e4lfte. Werte \u00fcber 1.0 verst\u00e4rken den Effekt. \u2014 Warum nicht einfach \u201eA + C\u201c als Prompt und \u201eB\u201c als Negativ-Prompt verwenden? Weil das etwas fundamental anderes tut: Ein Negativ-Prompt steuert den Entrauschungsprozess bei JEDEM der 25 Schritte weg von B \u2014 das Modell entscheidet Schritt f\u00fcr Schritt, wie es \u201enicht B\u201c interpretiert. Concept Algebra dagegen berechnet einen neuen Vektor VOR der Bildgenerierung: Die Subtraktion passiert im Embedding-Raum, nicht im Diffusionsprozess. Das Ergebnis ist ein einziger Vektor, der \u201eA ohne B-heit plus C-heit\u201c direkt kodiert. Der Negativ-Prompt sagt \u201emach das nicht\u201c. Die Algebra sagt \u201enimm dieses Konzept heraus und setze jenes ein\u201c \u2014 eine chirurgische Operation im Bedeutungsraum statt einer schrittweisen Vermeidungsstrategie.',
        explainReadTitle: 'Was bedeuten die Ergebnisse?',
        explainReadText: 'Links siehst du das Referenzbild (nur Prompt A, gleicher Seed). Rechts das Ergebnis der Algebra. Wenn die Analogie funktioniert, sollte das rechte Bild das Konzept von A zeigen, aber mit der semantischen Ver\u00e4nderung B\u2192C. Beispiel: \u201eSonnenuntergang am Strand\u201c \u2212 \u201eStrand\u201c + \u201eBerge\u201c \u2248 \u201eSonnenuntergang \u00fcber Bergen\u201c. Die L2-Distanz zeigt, wie weit sich das Ergebnis vom Original entfernt hat. \u2014 Ist die Operation kommutativ? Nein. Die Subtraktion von B und die Addition von C finden relativ zum Vektor A statt. Die Richtung B\u2192C ist nur im Kontext von A sinnvoll: \u201eK\u00f6nig \u2212 Mann\u201c entfernt die \u201em\u00e4nnlichen\u201c Richtungen aus dem K\u00f6nig-Vektor, \u201e+ Frau\u201c erg\u00e4nzt die \u201eweiblichen\u201c Richtungen \u2014 das Ergebnis liegt nahe \u201eK\u00f6nigin\u201c. C wird dabei nicht gezielt an die Stelle von B gesetzt, sondern einfach addiert. Dass das trotzdem funktioniert, zeigt, dass semantische Beziehungen im Vektorraum als konsistente lineare Richtungen kodiert sind.',
        techTitle: 'Technische Details',
        techText: 'Die Algebra wird auf den gew\u00e4hlten Encoder-Embeddings durchgef\u00fchrt: CLIP-L (768d), CLIP-G (1280d), T5-XXL (4096d) oder alle zusammen (589 Tokens \u00d7 4096d). Dieselbe Operation wird auch auf die Pooled Embeddings (2048d) angewendet. Beide Bilder verwenden denselben Seed f\u00fcr faire Vergleichbarkeit.',
        promptALabel: 'Prompt A (Basis)',
        promptAPlaceholder: 'z.B. Sonnenuntergang am Strand mit Palmen',
        promptBLabel: 'Prompt B (Subtrahieren)',
        promptBPlaceholder: 'z.B. Strand mit Palmen',
        promptCLabel: 'Prompt C (Addieren)',
        promptCPlaceholder: 'z.B. Schneebedeckte Berge',
        formulaLabel: 'A \u2212 B + C = ?',
        encoderLabel: 'Encoder',
        encoderAll: 'Alle (empfohlen)',
        encoderClipL: 'CLIP-L (768d)',
        encoderClipG: 'CLIP-G (1280d)',
        encoderT5: 'T5-XXL (4096d)',
        generateBtn: 'Berechnen',
        generating: 'Embeddings werden berechnet und Bilder erzeugt...',
        referenceLabel: 'Referenz (Prompt A)',
        resultLabel: 'Ergebnis (A \u2212 B + C)',
        l2Label: 'L2-Distanz zum Original',
        advancedLabel: 'Erweiterte Einstellungen',
        negativeLabel: 'Negativ-Prompt',
        stepsLabel: 'Steps',
        cfgLabel: 'CFG',
        seedLabel: 'Seed',
        scaleSubLabel: 'Subtraktions-Skalierung',
        scaleAddLabel: 'Additions-Skalierung',
        downloadReference: 'Referenz herunterladen',
        downloadResult: 'Ergebnis herunterladen',
        resultHint: 'Gib drei Prompts ein und klicke auf Berechnen \u2014 hier erscheint das Ergebnis der Vektor-Arithmetik.'
      },
      archaeology: {
        headerTitle: 'Denoising Archaeology \u2014 Wie wird aus Rauschen ein Bild?',
        headerSubtitle: 'Beobachte jeden einzelnen Entrauschungsschritt. Diffusionsmodelle arbeiten nicht links-nach-rechts, sondern gleichzeitig \u00fcberall \u2014 von groben Formen zu feinen Details.',
        explanationToggle: 'Ausf\u00fchrliche Erkl\u00e4rung anzeigen',
        explainWhatTitle: 'Was zeigt dieses Tool?',
        explainWhatText: 'Ein Diffusionsmodell erzeugt ein Bild, indem es schrittweise Rauschen entfernt. Dabei entsteht das Bild nicht wie beim Zeichnen von links nach rechts \u2014 stattdessen arbeitet das Modell an ALLEN Bildregionen gleichzeitig. In den ersten Schritten entstehen grobe Strukturen: Wo ist oben, wo unten? Wo ist der Horizont? In den mittleren Schritten kommen semantische Inhalte: Objekte, Formen, Farben. Die letzten Schritte verfeinern Texturen und Details. Dieses Tool macht jeden einzelnen Schritt sichtbar.',
        explainHowTitle: 'Wie benutze ich das Tool?',
        explainHowText: 'Gib einen Prompt ein und klicke auf Generieren. Das Modell erzeugt 25 Zwischenbilder (eins pro Entrauschungsschritt). Diese erscheinen als Filmstreifen unten. Klicke auf ein Thumbnail oder benutze den Zeitregler, um jeden Schritt in voller Gr\u00f6\u00dfe zu betrachten. Vergleiche fr\u00fche und sp\u00e4te Schritte: Wann \u201ewei\u00df\u201c das Modell, was es zeichnet?',
        explainReadTitle: 'Was verraten die drei Phasen?',
        explainReadText: 'Fr\u00fche Schritte (1\u20138): Globale Komposition \u2014 Grundstruktur, Farbverteilung, Layoutplanung. Mittlere Schritte (9\u201317): Semantische Emergenz \u2014 Objekte werden erkennbar, Formen kristallisieren sich heraus. Sp\u00e4te Schritte (18\u201325): Detail-Verfeinerung \u2014 Texturen, Kanten, feine Muster. Die \u00dcberg\u00e4nge sind flie\u00dfend, aber die Phasen zeigen deutlich: Das Modell \u201eplant\u201c zuerst global und verfeinert dann lokal. Besonders aufschlussreich: Der allererste Schritt zeigt keine feink\u00f6rnigen Pixel, sondern farbige Flecken. Das liegt daran, dass das Rauschen im Latent-Raum (128\u00d7128 bei 16 Kan\u00e4len) erzeugt wird, nicht im Pixel-Raum. Der VAE \u00fcbersetzt jeden Latent-Pixel in einen ~8\u00d78-Pixel-Patch \u2014 selbst pures Gau\u00dfsches Rauschen wird dadurch zu zusammenh\u00e4ngenden Farbclustern. Das Modell \u201edenkt\u201c nie in einzelnen Pixeln, sondern immer in diesem komprimierten Raum.',
        techTitle: 'Technische Details',
        techText: 'SD3.5 Large verwendet Rectified Flow als Scheduler mit 25 Standardschritten. Bei jedem Schritt werden die aktuellen Latent-Vektoren durch den VAE dekodiert (1024\u00d71024 JPEG). Der VAE (Variational Autoencoder) \u00fcbersetzt den mathematischen Latent-Raum in Pixel. Die Latent-Darstellung ist 128\u00d7128 bei 16 Kan\u00e4len \u2014 jeder Latent-Pixel entspricht einem ~8\u00d78-Pixel-Patch im Bild. Deshalb zeigt schon der erste Schritt farbige Cluster statt feines Pixelrauschen: Der VAE interpretiert zuf\u00e4llige 16-dimensionale Vektoren als koh\u00e4rente Farbfl\u00e4chen.',
        promptLabel: 'Prompt',
        promptPlaceholder: 'z.B. Ein Marktplatz in einer mittelalterlichen Stadt mit Menschen, Geb\u00e4uden und einem Brunnen',
        generate: 'Generieren',
        generating: 'Bild wird generiert \u2014 jeder Schritt wird aufgezeichnet...',
        emptyHint: 'Gib einen Prompt ein und klicke auf Generieren, um den Entrauschungsprozess zu visualisieren.',
        advancedLabel: 'Erweiterte Einstellungen',
        negativeLabel: 'Negativ-Prompt',
        stepsLabel: 'Steps',
        cfgLabel: 'CFG',
        seedLabel: 'Seed',
        filmstripLabel: 'Entrauschungs-Filmstreifen',
        timelineLabel: 'Schritt',
        phaseEarly: 'Komposition',
        phaseMid: 'Semantik',
        phaseLate: 'Detail',
        phaseEarlyDesc: 'Globale Struktur und Farbverteilung entstehen',
        phaseMidDesc: 'Objekte und Formen werden erkennbar',
        phaseLateDesc: 'Texturen und feine Details werden gesch\u00e4rft',
        finalImageLabel: 'Finales Bild (volle Aufl\u00f6sung)',
        download: 'Bild herunterladen'
      }
    },
    edutainment: {
      ui: {
        didYouKnow: '🤔 Wusstest du?',
        learnMore: '📚 Mehr erfahren',
        currentlyHappening: '⚡ Gerade passiert:',
        energyUsed: 'Verbrauchte Energie',
        co2Produced: 'CO₂ produziert'
      },
      energy: {
        kids_1: '💡 KI-Bilder brauchen Strom – so viel wie dein Handy 3 Stunden laden!',
        kids_2: '🔌 Die GPU ist wie ein Super-Taschenrechner der sehr viel Strom frisst!',
        kids_3: '⚡ Jedes Bild braucht so viel Energie wie eine LED-Lampe 10 Minuten an!',
        youth_1: '⚡ Eine GPU braucht beim Generieren {watts}W – wie ein kleiner Heizlüfter!',
        youth_2: '🔋 Ein Bild verbraucht etwa 0.01-0.02 kWh – klingt wenig, summiert sich aber!',
        youth_3: '🌡️ Die GPU wird gerade {temp}°C heiß – deshalb braucht sie Kühlung!',
        expert_1: '📊 Echtzeit: {watts}W bei {util}% Auslastung = {kwh} kWh bisher',
        expert_2: '🔥 TDP-Limit: {tdp}W | Aktuell: {watts}W ({percent}% des Limits)',
        expert_3: '💾 VRAM: {used}/{total} GB ({percent}%) – Modell + Aktivierungen'
      },
      data: {
        kids_1: '🧮 Die GPU rechnet gerade 10 Milliarden mal – schneller als du zählen kannst!',
        kids_2: '🎨 Das Bild entsteht in 50 kleinen Schritten – wie ein Puzzle das sich selbst löst!',
        kids_3: '🧩 Millionen von Zahlen fliegen gerade durch die GPU!',
        youth_1: '🔄 Jedes Bild durchläuft ~50 "Denoising Steps" – 50 Runden Rauschen entfernen!',
        youth_2: '📐 8 Milliarden Parameter werden gerade abgefragt – pro Bild!',
        youth_3: '🧠 Die KI "denkt" in Vektoren mit tausenden Dimensionen – wie Koordinaten in einem Raum.',
        expert_1: '🔬 MMDiT: Multimodal Diffusion Transformer – Text + Bild in gemeinsamen Attention-Layern',
        expert_2: '📈 Self-Attention: O(n²) Komplexität – jedes Token "sieht" alle anderen',
        expert_3: '⚙️ Classifier-Free Guidance: Prompt-Einfluss vs. Kreativität-Balance'
      },
      model: {
        kids_1: '🎓 Das KI-Modell hat sich Millionen Bilder angeschaut um malen zu lernen!',
        kids_2: '🤖 Die KI ist wie ein Künstler der nie vergisst was er gesehen hat!',
        kids_3: '✨ 8 Milliarden Verbindungen im Modell – mehr als Sterne am Himmel die du sehen kannst!',
        youth_1: '🧠 SD3.5 Large hat 8 Milliarden Parameter – wie 8 Milliarden Entscheidungsknoten.',
        youth_2: '📚 3 Text-Encoder arbeiten zusammen: CLIP-L, CLIP-G und T5-XXL',
        youth_3: '🔢 Das Modell braucht {vram} GB VRAM nur um geladen zu werden!',
        expert_1: '🏗️ Architektur: Rectified Flow + MMDiT mit 38 Transformer-Blöcken',
        expert_2: '📊 FP16/FP8 Quantisierung: Präzision vs. VRAM-Trade-off',
        expert_3: '🔗 LoRA: Low-Rank Adaptation – nur 0.1% der Parameter neu trainiert'
      },
      ethics: {
        kids_1: '🌍 KI lernt von Bildern im Internet – deshalb ist es wichtig, fair mit Kunst anderer zu sein!',
        kids_2: '⚖️ Nicht alle Künstler wurden gefragt ob die KI von ihnen lernen darf.',
        kids_3: '🤝 Gute KI respektiert die Arbeit von Menschen!',
        youth_1: '📜 Trainingsdaten stammen oft aus dem Internet. Künstler diskutieren: Fair Use oder Kopieren?',
        youth_2: '🏛️ Der EU AI Act fordert Transparenz: Woher kommen die Trainingsdaten?',
        youth_3: '💭 Frage: Wem gehört ein KI-generiertes Bild eigentlich?',
        expert_1: '⚠️ LAION-5B wurde teils ohne Urheber-Zustimmung erstellt – rechtliche Grauzone.',
        expert_2: '📋 EU AI Act Art. 52: Kennzeichnungspflicht für KI-generierte Inhalte',
        expert_3: '🔍 Model Cards & Datasheets: Best Practice für ML-Transparenz'
      },
      environment: {
        kids_1: '☁️ Jedes KI-Bild produziert ein bisschen CO₂ – wie Autofahren, nur weniger!',
        kids_2: '🌱 Überlege: Ist dieses Bild den Strom wert?',
        kids_3: '🌞 Die Energie für KI kommt oft aus Kraftwerken – manche sauber, manche nicht.',
        youth_1: '🏭 Deutscher Strommix: ~400g CO₂ pro kWh – das addiert sich!',
        youth_2: '📈 {co2}g CO₂ für dieses Bild – bei 1000 Bildern wären das {totalKg} kg!',
        youth_3: '💡 Tipp: Weniger Bilder generieren, dafür bewusster – spart Energie und CO₂.',
        expert_1: '📊 Berechnung: {watts}W × {seconds}s ÷ 3600 × 400g/kWh = {co2}g CO₂',
        expert_2: '🔬 Scope 2 Emissionen: Standort des Rechenzentrums entscheidend',
        expert_3: '⚡ PUE (Power Usage Effectiveness): Zusätzlicher Energie-Overhead für Kühlung'
      },
      iceberg: {
        drawPrompt: 'KI-Generierung verbraucht viel Energie. Zeichne Eisberge und schau was geschieht...',
        redraw: 'Neu zeichnen',
        startMelting: 'Schmelzen starten',
        melting: 'Eisberg schmilzt...',
        melted: 'Geschmolzen!',
        meltedMessage: '{co2}g CO₂ produziert',
        comparison: 'Diese CO₂-Menge lässt etwa {volume} cm³ Arktis-Eis schmelzen.',
        comparisonInfo: '(Jede Tonne CO₂ = ca. 6m³ Meereis-Verlust)',
        gpuPower: 'Stromverbrauch der Grafikkarte',
        gpuTemp: 'Temperatur der Grafikkarte',
        co2Info: 'CO₂-Emissionen durch Stromverbrauch (basierend auf deutschem Strommix)',
        drawAgain: 'Zeichne weitere Eisberge...'
      },
      pixel: {
        grafikkarte: 'Grafikkarte',
        energieverbrauch: 'Energieverbrauch',
        co2Menge: 'CO₂-Menge',
        smartphoneComparison: 'Du müsstest Dein Handy {minutes} Minuten ausgeschaltet lassen, um den CO₂-Verbrauch wieder auszugleichen!',
        clickToProcess: 'Klicke auf die Daten-Pixel um ein Minibild zu generieren!'
      },
      forest: {
        trees: 'Bäume',
        clickToPlant: 'Klicke um Bäume zu pflanzen! Wo Du einen Baum pflanzt, wird die Fabrik verschwinden.',
        gameOver: 'Der Wald ist verloren!',
        treesPlanted: 'Du hast {count} Bäume gepflanzt.',
        complete: 'Generation abgeschlossen',
        comparison: 'Ein durchschnittlicher Baum braucht {minutes} Minuten, um diese CO₂-Menge zu absorbieren.'
      },
      rareearth: {
        clickToClean: 'Klicke auf den See um Giftschlamm zu entfernen!',
        sludgeRemoved: 'Schlamm entfernt',
        environmentHealth: 'Umwelt',
        gameOverInactive: 'Du hast aufgegeben... der Abbau geht weiter',
        infoBanner: 'Seltene Erden für GPU-Chips: Der Abbau hinterlässt Giftschlamm und zerstört Ökosysteme. Deine Aufräum-Arbeit kann die Geschwindigkeit des Abbaus nicht aufhalten.',
        instructionsCooldown: '⏳ {seconds}s',
        statsGpu: 'GPU',
        statsHealth: 'Umwelt',
        statsSludge: 'Schlamm entfernt'
      }
    }
  },
  en: {
    app: {
      title: 'UCDCAE AI LAB',
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
      adult: 'Adults',
      research: 'Research'
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
      title: 'Favorites',  // Session 145: "My" redundant with switch
      empty: 'No favorites yet',
      favorite: 'Add to favorites',
      unfavorite: 'Remove from favorites',
      continue: 'Continue editing',
      restore: 'Restore session',
      viewMine: 'My favorites',  // Session 145
      viewAll: 'All favorites'  // Session 145
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
    landing: {
      subtitlePrefix: 'Pedagogical-artistic experimentation platform of the',
      subtitleSuffix: 'for the explorative use of generative AI in cultural-aesthetic media education',
      research: '',
      features: {
        textTransformation: {
          title: 'Text Transformation',
          description: 'Perspective shift through AI — your prompt is transformed through artistic-pedagogical lenses into image, video, and sound.'
        },
        imageTransformation: {
          title: 'Image Transformation',
          description: 'Transform images through different models and perspectives into new images and videos.'
        },
        multiImage: {
          title: 'Image Fusion',
          description: 'Combine multiple images and merge them into new image compositions through AI models.'
        },
        canvas: {
          title: 'Canvas Workflow',
          description: 'Visual workflow composition — connect modules via drag & drop into custom AI pipelines.'
        },
        music: {
          title: 'Music Generation',
          description: 'AI-powered music creation with lyrics, tags, and stylistic control.'
        },
        latentLab: {
          title: 'Latent Lab',
          description: 'Vector space research — surrealization, dimension elimination, embedding interpolation.'
        }
      }
    },
    research: {
      locked: 'Only available in research mode',
      lockedHint: 'Requires safety level "Adult" or "Research" (config.py)',
      complianceTitle: 'Research Mode Notice',
      complianceWarning: 'In research mode, no safety filters are active for prompts or generated images. Unexpected or inappropriate results may occur.',
      complianceAge: 'This mode is not recommended for persons under 16 years of age.',
      complianceConfirm: 'I confirm that I have understood the notices',
      complianceCancel: 'Cancel',
      complianceProceed: 'Proceed'
    },
    presetOverlay: {
      title: 'Choose Perspective',
      close: 'Close'
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
      title: 'About the UCDCAE AI LAB',
      intro: 'The UCDCAE AI LAB is a pedagogical-artistic experimentation platform of the UNESCO Chair in Digital Culture and Arts in Education for the explorative use of generative artificial intelligence in cultural-aesthetic media education. It was developed within the AI4ArtsEd and COMeARTS projects.',
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
        usage: 'Use of this platform is exclusively permitted for registered cooperation partners of the UCDCAE AI LAB. The data protection agreements made in this context apply. If you have any questions, please contact vanessa.baumann@fau.de.'
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
    safetyBadges: {
      '§86a': '§86a',
      '86a_filter': '§86a',
      age_filter: 'Age Filter',
      dsgvo_ner: 'GDPR',
      dsgvo_llm: 'GDPR',
      translation: '\u2192 EN',
      fast_filter: 'Content',
      llm_context_check: 'Content (LLM)',
      llm_safety_check: 'Youth Protection',
      llm_check_failed: 'Check Failed',
      disabled: '\u2014'
    },
    safetyBlocked: {
      vlm: 'Your prompt was fine, but the generated image was flagged as unsuitable by an image analysis AI. This can happen \u2014 image generation is not always predictable. Just try again, every generation is different!',
      para86a: 'Your prompt was blocked because it contains symbols or terms that are prohibited under German law (\u00A786a StGB). This rule protects us all from hate and violence. Try a different topic!',
      dsgvo: 'Your prompt was blocked because it contains personal data (e.g. real names or addresses). This is protected by the General Data Protection Regulation (GDPR). Use fictional names instead!',
      kids: 'Your prompt was blocked by the child safety filter. Some terms are not suitable for children because they can be scary or disturbing. Try describing your idea with friendlier words!',
      youth: 'Your prompt was blocked by the youth protection filter. Some content is not suitable for teenagers either. Try rephrasing your idea!',
      generic: 'Your prompt was blocked by the safety system. The system protects you from unsuitable content. Try a different wording!',
      inputImage: 'The uploaded image was flagged as unsuitable by an image analysis AI. Please use a different image.',
      vlmSaw: 'The image AI saw',
      systemUnavailable: 'The safety system (Ollama) is not responding, so no further processing is possible. Please contact the system administrator.'
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
      infoTitle: 'Hallucinator — Extrapolation Beyond the Known',
      infoDescription: 'Two AI "brains" read your text: CLIP-L understands language through images, T5 understands it purely linguistically. The slider doesn\'t simply blend between them — it pushes the image far beyond what T5 alone would produce. The AI must then interpret vectors it has never encountered during training. The result: AI hallucinations — images that no prompt could directly produce.',
      purposeTitle: 'The Slider',
      purposeText: 'α < 0: CLIP-L amplified, T5 negated — the upper 3328 dimensions (where CLIP-L is zero-padded) receive inverted T5 vectors. Cross-attention patterns in the transformer flip: visually driven hallucinations. ◆ α = 0: pure CLIP-L — normal image. ◆ α = 1: pure T5-XXL — still normal, but different quality. ◆ α > 1: extrapolation past T5. At α = 20 the formula pushes the embedding 19× beyond T5 into unexplored vector space — linguistically driven hallucinations. ◆ Sweet spot: α = 15–35.',
      techTitle: 'How It Works',
      techText: 'Your prompt is sent through two encoders separately: CLIP-L (visually trained, 77 tokens, 768 dims → padded to 4096) and T5-XXL (linguistically trained, 512 tokens, 4096 dims). The first 77 token positions are fused: (1-α)·CLIP-L + α·T5. The remaining T5 tokens (78–512) stay unchanged as a semantic anchor — they keep the image tied to your text no matter how extreme α gets. At α > 1 this is not blending but extrapolation: vectors no training ever produced. At α < 0, T5 is negated and CLIP-L amplified — qualitatively different hallucinations because cross-attention patterns in the transformer are inverted.',
      sliderLabel: 'Extrapolation (α)',
      sliderNormal: 'normal',
      sliderWeird: 'weird',
      sliderCrazy: 'crazy',
      sliderExtremeWeird: 'super weird',
      sliderExtremeCrazy: 'super crazy',
      sliderHint: "α<0: past CLIP {'|'} α=0: pure CLIP {'|'} α=1: pure T5 {'|'} α>1: past T5",
      expandLabel: 'Expand prompt for T5',
      expandHint: 'Your prompt has few words (~{count} CLIP tokens). For optimal hallucinations, the AI can narratively expand the T5 context.',
      expandActive: 'Expanding prompt...',
      expandResultLabel: 'T5 expansion (T5 encoder only)',
      advancedLabel: 'Advanced Settings',
      negativeLabel: 'Negative Prompt',
      negativeHint: 'Extrapolated with the same α. Determines what the image extrapolates AWAY from — different negatives produce fundamentally different aesthetics.',
      cfgLabel: 'CFG Scale',
      cfgHint: 'Classifier-Free Guidance: strength of prompt influence. Higher = stronger effect, less variation.'
    },
    musicGeneration: {
      infoTitle: 'Music Generation',
      infoDescription: 'Create music from text and style tags. The AI generates melodies, rhythms, and harmonies based on your lyrics and genre specifications.',
      purposeTitle: 'Pedagogical Purpose',
      purposeText: 'Explore how AI interprets musical concepts. How does word choice in lyrics affect the melody?',
      lyricsLabel: 'Lyrics (Text)',
      lyricsPlaceholder: '[Verse]\nYour lyrics here...\n\n[Chorus]\nChorus...',
      tagsLabel: 'Style Tags',
      tagsPlaceholder: 'pop, piano, upbeat, female vocal, 120bpm',
      selectModel: 'Choose a music model:',
      generate: 'Generate Music',
      generating: 'Generating music...'
    },
    musicGen: {
      simpleMode: 'Simple',
      advancedMode: 'Advanced',
      lyricsLabel: 'Lyrics',
      lyricsPlaceholder: 'Write your song lyrics with structure markers like [Verse], [Chorus], [Bridge]...\n\nExample:\n[Verse]\nde doo doo doo\nde blaa blaa blaa\n\n[Chorus]\nis all I want to sing to you',
      tagsLabel: 'Style Tags',
      tagsPlaceholder: 'Genre, mood, instruments...\n\nExample: ska, aggressive, upbeat, high definition, bass and sax trio',
      refineButton: 'Refine Lyrics & Tags',
      refinedLyricsLabel: 'Refined Lyrics',
      refinedLyricsPlaceholder: 'Your refined lyrics will appear here...',
      refiningLyricsMessage: 'AI is refining your lyrics...',
      refinedTagsLabel: 'Refined Tags',
      refinedTagsPlaceholder: 'Refined style tags will appear here...',
      refiningTagsMessage: 'AI is generating matching style tags...',
      selectModel: 'Choose a Music Model',
      generateButton: 'Generate Music',
      quality: 'Quality'
    },
    musicGenV2: {
      lyricsWorkshop: 'Lyrics Workshop',
      lyricsInput: 'Your Text',
      lyricsPlaceholder: 'Write lyrics, a theme, keywords, or a mood...',
      themeToLyrics: 'Keywords to Song Lyrics',
      refineLyrics: 'Structure Song Lyrics',
      resultLabel: 'Result',
      resultPlaceholder: 'Your lyrics will appear here...',
      expandingTheme: 'AI is writing song lyrics from your keywords...',
      refiningLyrics: 'AI is structuring your song lyrics...',
      soundExplorer: 'Sound Explorer',
      suggestFromLyrics: 'Suggest from Lyrics',
      suggestingTags: 'AI is analyzing your lyrics...',
      mostImportant: 'most important',
      dimGenre: 'Genre',
      dimTimbre: 'Timbre',
      dimGender: 'Voice',
      dimMood: 'Mood',
      dimInstrument: 'Instruments',
      dimScene: 'Scene',
      dimRegion: 'Region (UNESCO)',
      dimTopic: 'Topic',
      audioLength: 'Audio Length',
      generateButton: 'Generate Music',
      selectModel: 'Model',
      customTags: 'Custom Tags',
      customTagsPlaceholder: 'e.g. acoustic,dreamy,summer_vibes'
    },
    latentLab: {
      tabs: {
        attention: 'Attention Cartography',
        probing: 'Feature Probing',
        algebra: 'Concept Algebra',
        fusion: 'Encoder Fusion',
        archaeology: 'Denoising Archaeology'
      },
      comingSoon: 'This tool will be implemented in a future version.',
      attention: {
        headerTitle: 'Attention Cartography — Which word steers which image region?',
        headerSubtitle: 'For each word in the prompt, a heatmap overlay on the generated image shows WHERE in the image that word had the most influence. This reveals how the model spatially distributes semantic concepts.',
        explanationToggle: 'Show detailed explanation',
        explainWhatTitle: 'What does this tool show?',
        explainWhatText: 'When a diffusion model generates an image, it does not read the prompt word by word like a set of instructions. Instead, a mechanism called "attention" distributes the influence of each word across different image regions. The word "house" mainly influences the region where the house appears — but also neighboring areas, because the model understands the context of the entire scene. This tool makes that distribution visible: click on a word and see which image regions light up.',
        explainHowTitle: 'How do I read the heatmap?',
        explainHowText: 'Bright, intense color = strong influence of the word on that region. Dark or absent color = little influence. If you select multiple words, they appear in different colors. Note: the maps are NOT perfectly sharp-edged — this is not a bug, but shows that the model processes concepts contextually, not in isolation. A "house" in a farm scene also has some influence on animals and fields, because the model understands the scene as a whole.',
        explainReadTitle: 'What do the two sliders reveal?',
        explainReadText: 'The denoising step slider shows WHEN in the 25-step generation process you are viewing attention. Early steps show rough layout planning, late steps show detail assignment. The network depth selector shows WHERE in the transformer attention is measured: shallow layers (near input) show global composition planning, middle layers semantic assignment, deep layers fine-tuning. Both axes are independent — it is worth systematically exploring different combinations.',
        techTitle: 'Technical details',
        techText: 'SD3.5 uses an MMDiT (Multimodal Diffusion Transformer) with joint attention: image and text tokens attend to each other across 24 transformer blocks. We replace the default SDPA processor with a manual softmax(QK^T/√d) processor at 3 selected blocks to extract the text→image attention submatrix. Maps are 64x64 resolution (patch grid), upscaled to image resolution via bilinear interpolation. Tokenization uses CLIP-L BPE — subword tokens are automatically combined into whole words.',
        promptLabel: 'Prompt',
        promptPlaceholder: 'e.g. A house stands in a landscape, surrounded by farmland, nature and animals. Some people can be seen.',
        generate: 'Generate + Analyze',
        generating: 'Generating image and extracting attention...',
        emptyHint: 'Enter a prompt and click Generate to visualize the model\'s attention maps.',
        advancedLabel: 'Advanced Settings',
        negativeLabel: 'Negative Prompt',
        stepsLabel: 'Steps',
        cfgLabel: 'CFG',
        seedLabel: 'Seed',
        tokensLabel: 'Tokens',
        tokensHint: 'Click one or more words. Subword tokens (e.g. "Ku"+"gel") are automatically combined. Multiple words appear in different colors.',
        timestepLabel: 'Denoising step',
        timestepHint: 'Diffusion models generate images in 25 steps from noise to image. Early steps establish rough structure, late steps refine details. This slider shows what the model attends to at each step.',
        step: 'Step',
        layerLabel: 'Network depth',
        layerHint: 'At every denoising step, the signal passes through all 24 transformer layers. Shallow layers (near input) capture global composition, middle layers semantic assignment, deep layers (near output) fine details. Both controls are independent: step = when in the process, depth = where in the network.',
        layerEarly: 'Shallow (Composition)',
        layerMid: 'Middle (Semantics)',
        layerLate: 'Deep (Detail)',
        opacityLabel: 'Heatmap',
        opacityHint: 'Strength of the colored overlay on the image.',
        baseImageLabel: 'Base image',
        baseColor: 'Color',
        baseBW: 'B/W',
        baseOff: 'Off',
        baseImageHint: 'Color shows the original image. B/W desaturates it so heatmap colors stand out. Off hides the image entirely and shows only the attention map.',
        download: 'Download Image'
      },
      probing: {
        headerTitle: 'Feature Probing — Which dimensions encode what?',
        headerSubtitle: 'Compare two prompts and discover which embedding dimensions encode the semantic difference. Selectively transfer individual dimensions to see how they affect the image.',
        explanationToggle: 'Show detailed explanation',
        explainWhatTitle: 'What does this tool show?',
        explainWhatText: 'Every word is converted by the text encoder into a high-dimensional vector (e.g. 4096 dimensions for T5). When you change a word in the prompt — e.g. "red" to "blue" — certain dimensions change more than others. This tool shows you WHICH dimensions change most and lets you selectively transfer individual dimensions from prompt B into prompt A.',
        explainHowTitle: 'How does the transfer work?',
        explainHowText: 'The bar chart shows all dimensions sorted by difference magnitude. Use the rank range controls (From/To) to select a window — e.g. just the top 100 or specifically ranks 880–920. Clicking "Transfer" regenerates the image with the same settings (same seed!) — but with selected dimensions from prompt B. This lets you see exactly what those dimensions "encode".',
        explainReadTitle: 'How do I read the bar chart?',
        explainReadText: 'Each bar represents one embedding dimension. The length shows how much that dimension differs between prompt A and B. Dimensions with large differences are the most likely carriers of the semantic change. But note: embeddings are distributed — often multiple dimensions together are needed to produce a visible change.',
        techTitle: 'Technical details',
        techText: 'SD3.5 uses three text encoders: CLIP-L (768d), CLIP-G (1280d) and T5-XXL (4096d). You can probe each individually. The difference is computed as mean absolute deviation across all token positions: mean(abs(B-A), dim=tokens). The transfer replaces selected dimensions across all token positions simultaneously.',
        promptALabel: 'Prompt A (Original)',
        promptBLabel: 'Prompt B (Comparison)',
        promptAPlaceholder: 'e.g. A red house by the lake',
        promptBPlaceholder: 'e.g. A blue house by the lake',
        encoderLabel: 'Encoder',
        encoderAll: 'All (recommended)',
        encoderClipL: 'CLIP-L (768d)',
        encoderClipG: 'CLIP-G (1280d)',
        encoderT5: 'T5-XXL (4096d)',
        analyzeBtn: 'Analyze',
        analyzing: 'Encoding and comparing prompts...',
        transferBtn: 'Transfer selected vector dimensions from Prompt B into the generated image',
        transferring: 'Generating image with modified embedding...',
        rankFromLabel: 'From rank',
        rankToLabel: 'To rank',
        sliderLabel: 'Select dimensions from Prompt B',
        range1Label: 'Range 1',
        range2Label: 'Range 2',
        addRange: 'Add range',
        selectionDesc: '{count} dimensions from Prompt B selected (rank {ranges} of {total})',
        listTitle: 'The {count} dimensions from Prompt B with the largest difference to Prompt A',
        sortAsc: 'Ascending',
        sortDesc: 'Descending',
        originalLabel: 'Original (Prompt A)',
        modifiedLabel: 'Modified (Transfer from Prompt B)',
        modifiedHint: 'Select a rank range below and click "Transfer" — this will show prompt A with the transferred dimensions from B (same seed).',
        noDifference: 'The embeddings are identical — change prompt B.',
        advancedLabel: 'Advanced Settings',
        negativeLabel: 'Negative Prompt',
        stepsLabel: 'Steps',
        cfgLabel: 'CFG',
        seedLabel: 'Seed',
        selectAll: 'All',
        selectNone: 'None',
        downloadOriginal: 'Download Original',
        downloadModified: 'Download Modified'
      },
      algebra: {
        headerTitle: 'Concept Algebra \u2014 Vector arithmetic on image embeddings',
        headerSubtitle: 'Apply the famous word2vec analogy to image generation: King \u2212 Man + Woman \u2248 Queen. Three prompts are encoded and algebraically combined.',
        explanationToggle: 'Show detailed explanation',
        explainWhatTitle: 'What does this tool show?',
        explainWhatText: 'In 2013, Mikolov showed that word embeddings encode semantic relationships as linear directions: the vector for "King" minus "Man" plus "Woman" yields a vector close to "Queen". This tool applies that idea to SD3.5\'s text encoders: instead of single words, you manipulate entire prompt embeddings. The result is an image that contains concept A but with B replaced by C.',
        explainHowTitle: 'How does the algebra work \u2014 and why not just use a negative prompt?',
        explainHowText: 'You enter three prompts: A (base), B (subtract), and C (add). The formula is: Result = A \u2212 Scale\u2081\u00d7B + Scale\u2082\u00d7C. The scale sliders control intensity: at 1.0, B is fully subtracted and C fully added. At 0.5, only half. Values above 1.0 amplify the effect. \u2014 Why not just use "A + C" as the prompt and "B" as the negative prompt? Because that does something fundamentally different: A negative prompt steers the denoising process away from B at EVERY one of the 25 steps \u2014 the model decides step by step how to interpret "not B". Concept Algebra instead computes a new vector BEFORE image generation: the subtraction happens in embedding space, not in the diffusion process. The result is a single vector that directly encodes "A without B-ness plus C-ness". The negative prompt says "don\'t do this". The algebra says "take this concept out and put that one in" \u2014 a surgical operation in meaning-space rather than a step-by-step avoidance strategy.',
        explainReadTitle: 'What do the results mean?',
        explainReadText: 'On the left you see the reference image (prompt A only, same seed). On the right, the algebra result. If the analogy works, the right image should show concept A but with the semantic change B\u2192C. Example: "Sunset at the beach" \u2212 "Beach" + "Mountains" \u2248 "Sunset over mountains". The L2 distance shows how far the result has moved from the original. \u2014 Is the operation commutative? No. Subtraction of B and addition of C happen relative to vector A. The direction B\u2192C only makes sense in the context of A: "King \u2212 Man" removes the "male" directions from the King vector, "+ Woman" adds the "female" directions \u2014 the result lands near "Queen". C is not surgically placed where B was removed; it is simply added. That this still works shows that semantic relationships are encoded as consistent linear directions in the vector space.',
        techTitle: 'Technical details',
        techText: 'The algebra is performed on the selected encoder embeddings: CLIP-L (768d), CLIP-G (1280d), T5-XXL (4096d), or all combined (589 tokens \u00d7 4096d). The same operation is also applied to pooled embeddings (2048d). Both images use the same seed for fair comparison.',
        promptALabel: 'Prompt A (Base)',
        promptAPlaceholder: 'e.g. Sunset at the beach with palm trees',
        promptBLabel: 'Prompt B (Subtract)',
        promptBPlaceholder: 'e.g. Beach with palm trees',
        promptCLabel: 'Prompt C (Add)',
        promptCPlaceholder: 'e.g. Snow-covered mountains',
        formulaLabel: 'A \u2212 B + C = ?',
        encoderLabel: 'Encoder',
        encoderAll: 'All (recommended)',
        encoderClipL: 'CLIP-L (768d)',
        encoderClipG: 'CLIP-G (1280d)',
        encoderT5: 'T5-XXL (4096d)',
        generateBtn: 'Compute',
        generating: 'Computing embeddings and generating images...',
        referenceLabel: 'Reference (Prompt A)',
        resultLabel: 'Result (A \u2212 B + C)',
        l2Label: 'L2 distance from original',
        advancedLabel: 'Advanced Settings',
        negativeLabel: 'Negative Prompt',
        stepsLabel: 'Steps',
        cfgLabel: 'CFG',
        seedLabel: 'Seed',
        scaleSubLabel: 'Subtraction scale',
        scaleAddLabel: 'Addition scale',
        downloadReference: 'Download Reference',
        downloadResult: 'Download Result',
        resultHint: 'Enter three prompts and click Compute \u2014 the result of the vector arithmetic will appear here.'
      },
      archaeology: {
        headerTitle: 'Denoising Archaeology \u2014 How does noise become an image?',
        headerSubtitle: 'Observe every single denoising step. Diffusion models don\'t draw left-to-right \u2014 they work everywhere simultaneously, from rough shapes to fine detail.',
        explanationToggle: 'Show detailed explanation',
        explainWhatTitle: 'What does this tool show?',
        explainWhatText: 'A diffusion model creates an image by progressively removing noise. Unlike drawing from left to right, the model works on ALL image regions simultaneously. In the first steps, rough structures emerge: Where is up, where is down? Where is the horizon? In the middle steps, semantic content appears: objects, shapes, colors. The final steps refine textures and details. This tool makes every single step visible.',
        explainHowTitle: 'How do I use this tool?',
        explainHowText: 'Enter a prompt and click Generate. The model produces 25 intermediate images (one per denoising step). These appear as a filmstrip below. Click a thumbnail or use the timeline slider to view each step at full size. Compare early and late steps: When does the model "know" what it is drawing?',
        explainReadTitle: 'What do the three phases reveal?',
        explainReadText: 'Early steps (1\u20138): Global composition \u2014 basic structure, color distribution, layout planning. Middle steps (9\u201317): Semantic emergence \u2014 objects become recognizable, shapes crystallize. Late steps (18\u201325): Detail refinement \u2014 textures, edges, fine patterns. The transitions are gradual, but the phases clearly show: the model first "plans" globally, then refines locally. Particularly revealing: The very first step does not show fine-grained pixels, but colorful patches. This is because the noise is generated in latent space (128\u00d7128 at 16 channels), not in pixel space. The VAE translates each latent pixel into an ~8\u00d78 pixel patch \u2014 even pure Gaussian noise becomes coherent color clusters. The model never "thinks" in individual pixels, but always in this compressed space.',
        techTitle: 'Technical details',
        techText: 'SD3.5 Large uses Rectified Flow as scheduler with 25 default steps. At each step, the current latent vectors are decoded through the VAE (1024\u00d71024 JPEG). The VAE (Variational Autoencoder) translates the mathematical latent space into pixels. The latent representation is 128\u00d7128 at 16 channels \u2014 each latent pixel corresponds to an ~8\u00d78 pixel patch in the image. This is why even the first step shows colorful clusters instead of fine pixel noise: the VAE interprets random 16-dimensional vectors as coherent color patches.',
        promptLabel: 'Prompt',
        promptPlaceholder: 'e.g. A marketplace in a medieval town with people, buildings and a fountain',
        generate: 'Generate',
        generating: 'Generating image \u2014 recording every step...',
        emptyHint: 'Enter a prompt and click Generate to visualize the denoising process.',
        advancedLabel: 'Advanced Settings',
        negativeLabel: 'Negative Prompt',
        stepsLabel: 'Steps',
        cfgLabel: 'CFG',
        seedLabel: 'Seed',
        filmstripLabel: 'Denoising Filmstrip',
        timelineLabel: 'Step',
        phaseEarly: 'Composition',
        phaseMid: 'Semantics',
        phaseLate: 'Detail',
        phaseEarlyDesc: 'Global structure and color distribution emerge',
        phaseMidDesc: 'Objects and shapes become recognizable',
        phaseLateDesc: 'Textures and fine details are sharpened',
        finalImageLabel: 'Final image (full resolution)',
        download: 'Download Image'
      }
    },
    edutainment: {
      ui: {
        didYouKnow: '🤔 Did you know?',
        learnMore: '📚 Learn more',
        currentlyHappening: '⚡ Currently happening:',
        energyUsed: 'Energy used',
        co2Produced: 'CO₂ produced'
      },
      energy: {
        kids_1: '💡 AI images need electricity – as much as charging your phone for 3 hours!',
        kids_2: '🔌 The GPU is like a super calculator that eats lots of power!',
        kids_3: '⚡ Each image needs as much energy as running an LED light for 10 minutes!',
        youth_1: '⚡ A GPU uses {watts}W while generating – like a small space heater!',
        youth_2: '🔋 One image uses about 0.01-0.02 kWh – sounds little, but adds up!',
        youth_3: '🌡️ The GPU is getting {temp}°C hot right now – that\'s why it needs cooling!',
        expert_1: '📊 Realtime: {watts}W at {util}% utilization = {kwh} kWh so far',
        expert_2: '🔥 TDP limit: {tdp}W | Current: {watts}W ({percent}% of limit)',
        expert_3: '💾 VRAM: {used}/{total} GB ({percent}%) – model + activations'
      },
      data: {
        kids_1: '🧮 The GPU is calculating 10 billion times right now – faster than you can count!',
        kids_2: '🎨 The image is created in 50 small steps – like a puzzle solving itself!',
        kids_3: '🧩 Millions of numbers are flying through the GPU right now!',
        youth_1: '🔄 Each image goes through ~50 "denoising steps" – 50 rounds of removing noise!',
        youth_2: '📐 8 billion parameters are being queried – per image!',
        youth_3: '🧠 The AI "thinks" in vectors with thousands of dimensions – like coordinates in a space.',
        expert_1: '🔬 MMDiT: Multimodal Diffusion Transformer – text + image in joint attention layers',
        expert_2: '📈 Self-Attention: O(n²) complexity – every token "sees" all others',
        expert_3: '⚙️ Classifier-Free Guidance: prompt influence vs. creativity balance'
      },
      model: {
        kids_1: '🎓 The AI model looked at millions of images to learn how to paint!',
        kids_2: '🤖 The AI is like an artist who never forgets what they\'ve seen!',
        kids_3: '✨ 8 billion connections in the model – more than stars you can see in the sky!',
        youth_1: '🧠 SD3.5 Large has 8 billion parameters – like 8 billion decision nodes.',
        youth_2: '📚 3 text encoders work together: CLIP-L, CLIP-G, and T5-XXL',
        youth_3: '🔢 The model needs {vram} GB VRAM just to be loaded!',
        expert_1: '🏗️ Architecture: Rectified Flow + MMDiT with 38 transformer blocks',
        expert_2: '📊 FP16/FP8 quantization: precision vs. VRAM trade-off',
        expert_3: '🔗 LoRA: Low-Rank Adaptation – only 0.1% of parameters retrained'
      },
      ethics: {
        kids_1: '🌍 AI learns from images on the internet – that\'s why it\'s important to be fair with other people\'s art!',
        kids_2: '⚖️ Not all artists were asked if the AI could learn from them.',
        kids_3: '🤝 Good AI respects people\'s work!',
        youth_1: '📜 Training data often comes from the internet. Artists debate: Fair Use or copying?',
        youth_2: '🏛️ The EU AI Act demands transparency: Where does the training data come from?',
        youth_3: '💭 Question: Who actually owns an AI-generated image?',
        expert_1: '⚠️ LAION-5B was partly created without creator consent – legal gray area.',
        expert_2: '📋 EU AI Act Art. 52: Labeling requirement for AI-generated content',
        expert_3: '🔍 Model Cards & Datasheets: Best practice for ML transparency'
      },
      environment: {
        kids_1: '☁️ Each AI image produces a bit of CO₂ – like driving a car, but less!',
        kids_2: '🌱 Think: Is this image worth the electricity?',
        kids_3: '🌞 Energy for AI often comes from power plants – some clean, some not.',
        youth_1: '🏭 German power grid: ~400g CO₂ per kWh – that adds up!',
        youth_2: '📈 {co2}g CO₂ for this image – with 1000 images that would be {totalKg} kg!',
        youth_3: '💡 Tip: Generate fewer images, but more thoughtfully – saves energy and CO₂.',
        expert_1: '📊 Calculation: {watts}W × {seconds}s ÷ 3600 × 400g/kWh = {co2}g CO₂',
        expert_2: '🔬 Scope 2 emissions: data center location is decisive',
        expert_3: '⚡ PUE (Power Usage Effectiveness): Additional energy overhead for cooling'
      },
      iceberg: {
        drawPrompt: 'AI generation uses a lot of energy. Draw icebergs and see what happens...',
        redraw: 'Redraw',
        startMelting: 'Start melting',
        melting: 'Iceberg melting...',
        melted: 'Melted!',
        meltedMessage: '{co2}g CO₂ produced',
        comparison: 'This CO₂ amount melts about {volume} cm³ of Arctic ice.',
        comparisonInfo: '(Each ton of CO₂ = approx. 6m³ sea ice loss)',
        gpuPower: 'Graphics card power consumption',
        gpuTemp: 'Graphics card temperature',
        co2Info: 'CO₂ emissions from power consumption (based on German energy mix)',
        drawAgain: 'Draw more icebergs...'
      },
      pixel: {
        grafikkarte: 'Graphics Card',
        energieverbrauch: 'Energy Usage',
        co2Menge: 'CO₂ Amount',
        smartphoneComparison: 'You would need to keep your phone off for {minutes} minutes to offset this CO₂ usage!',
        clickToProcess: 'Click on the data pixels to generate a mini image!'
      },
      forest: {
        trees: 'Trees',
        clickToPlant: 'Click to plant trees! Where you plant a tree, the factory will disappear.',
        gameOver: 'The forest is lost!',
        treesPlanted: 'You planted {count} trees.',
        complete: 'Generation complete',
        comparison: 'An average tree needs {minutes} minutes to absorb this amount of CO₂.'
      },
      rareearth: {
        clickToClean: 'Click the lake to remove toxic sludge!',
        sludgeRemoved: 'Sludge removed',
        environmentHealth: 'Environment',
        gameOverInactive: 'You gave up... mining continues',
        infoBanner: 'Rare earth mining for GPU chips leaves toxic sludge and destroys ecosystems. Your cleanup efforts cannot match the speed of extraction.',
        instructionsCooldown: '⏳ {seconds}s',
        statsGpu: 'GPU',
        statsHealth: 'Environment',
        statsSludge: 'Sludge removed'
      }
    }
  }
}

export default createI18n({
  legacy: false,
  locale: 'de', // Default to German
  fallbackLocale: 'en',
  messages
})
