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
        comparison: 'Ein durchschnittlicher Baum braucht {hours} Stunden, um diese CO₂-Menge zu absorbieren.',
        gpuPower: 'Stromverbrauch der Grafikkarte',
        gpuTemp: 'Temperatur der Grafikkarte',
        co2Info: 'CO₂-Emissionen durch Stromverbrauch (basierend auf deutschem Strommix)',
        drawAgain: 'Zeichne weitere Eisberge...'
      },
      pixel: {
        grafikkarte: 'Grafikkarte',
        energieverbrauch: 'Energieverbrauch',
        co2Menge: 'CO₂-Menge',
        smartphoneComparison: 'Du müsstest Dein Handy {minutes} Minuten ausgeschaltet lassen, um den CO₂-Verbrauch wieder auszugleichen!'
      }
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
        comparison: 'An average tree needs {hours} hours to absorb this amount of CO₂.',
        gpuPower: 'Graphics card power consumption',
        gpuTemp: 'Graphics card temperature',
        co2Info: 'CO₂ emissions from power consumption (based on German energy mix)',
        drawAgain: 'Draw more icebergs...'
      },
      pixel: {
        grafikkarte: 'Graphics Card',
        energieverbrauch: 'Energy Usage',
        co2Menge: 'CO₂ Amount',
        smartphoneComparison: 'You would need to keep your phone off for {minutes} minutes to offset this CO₂ usage!'
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
