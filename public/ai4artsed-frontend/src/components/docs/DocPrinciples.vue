<template>
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
          ? 'WAS: "Ein Baum" → WIE: "aus der Perspektive seiner Wurzeln, das Verborgene sichtbar machend" vs. "nur durch Licht und Schatten im Gegenlicht beschrieben" → dasselbe Thema, völlig andere Bilder'
          : 'WHAT: "A tree" → HOW: "from the perspective of its roots, making the hidden visible" vs. "described only through light and shadow in backlight" → same subject, completely different images' }}
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
        ? 'Jeder Zwischenschritt ist sichtbar: die transformierte Beschreibung, die Adaption, das Endergebnis. Du kannst eingreifen, verändern, zurückgehen.'
        : 'Every intermediate step is visible: the transformed description, the adaption, the final result. You can intervene, change, go back.' }}</p>
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
        <h3>{{ currentLanguage === 'de' ? 'Pädagogische Einbindung' : 'Pedagogical Integration' }}</h3>
      </div>
      <p>{{ currentLanguage === 'de'
        ? 'Die Plattform ist als Teil pädagogischer und künstlerischer Prozesse gedacht, nicht notwendig als deren Zentrum. Sie will vielfältige Zugänge ermöglichen, nicht kanalisieren – ob im Unterricht, im Workshop, in der freien Projektarbeit oder im Selbststudium.'
        : 'The platform is designed as part of pedagogical and artistic processes, not necessarily as their center. It aims to enable diverse approaches, not to channel them – whether in class, in workshops, in independent project work, or in self-study.' }}</p>
    </div>

    <div class="principle-card">
      <div class="principle-header">
        <span class="principle-number">7</span>
        <h3>{{ currentLanguage === 'de' ? 'Wissen über die Welt' : 'Knowledge About the World' }}</h3>
      </div>
      <p>{{ currentLanguage === 'de'
        ? 'Künstlerische Prozesse erfordern nicht nur ästhetisches Wissen, sondern auch Wissen über Sachverhalte in der Welt. Die KI recherchiert auf Wikipedia, um Informationen zu finden wenn sie über diese nicht selbst in hinreichendem Maße verfügt. Dieses Feature ist experimentell, aber interessant. Bisweilen wird der Prompt von der Recherche stark, manchmal kaum beeindruckt sein.'
        : 'Artistic processes require not only aesthetic knowledge, but also knowledge about facts in the world. The AI researches Wikipedia to find information when it does not have sufficient knowledge of its own. This feature is experimental, but interesting. Sometimes the prompt will be strongly influenced by the research, sometimes barely at all.' }}</p>
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
        ? 'Das Favoriten-System am unteren Rand des Fensters ermöglicht zwei Arbeitsmodi: "Meine" zeigt nur deine eigenen Favoriten – eine persönliche Arbeitsfläche zum Iterieren, Vergleichen und Auswählen zwischen Entwürfen. Die individuellen "Mein"-Favoriten werden nach 24 Stunden gelöscht. "Alle" zeigt die Favoriten aller Workshop-Teilnehmenden – ein kollektiver Pool zum Teilen von Bildern und Prompts, gegenseitigem Inspirieren und gemeinsamen Weiterentwickeln.'
        : 'The favorites system at the bottom of the window enables two working modes: "Mine" shows only your own favorites – a personal workspace for iterating, comparing, and selecting between drafts. Individual "Mine" favorites are deleted after 24 hours. "All" shows favorites from all workshop participants – a collective pool for sharing images and prompts, mutual inspiration, and collaborative development.' }}</p>
      <div class="example-box">
        <strong>{{ currentLanguage === 'de' ? 'Persönlich:' : 'Personal:' }}</strong>
        {{ currentLanguage === 'de'
          ? 'Speichere mehrere Varianten eines Bildes, vergleiche sie, wähle die beste aus und arbeite daran weiter. Die Favoriten sind deine Werkbank.'
          : 'Save multiple variations of an image, compare them, select the best one, and continue working on it. Favorites are your workbench.' }}
      </div>
      <div class="example-box">
        <strong>{{ currentLanguage === 'de' ? 'Kollaborativ:' : 'Collaborative:' }}</strong>
        {{ currentLanguage === 'de'
          ? 'Sieh dir interessante Arbeiten von anderen, lade ihre kompletten Prompts und Einstellungen, verändere sie und entwickle eigene Varianten. Die "Wiederherstellen"-Funktion macht den kreativen Prozess transparent und teilbar.'
          : 'See interesting work from others, load their complete prompts and settings, modify them, and develop your own variations. The "Restore" function makes the creative process transparent and shareable.' }}
      </div>
      <div class="tension-box">
        <span class="tension-label">{{ currentLanguage === 'de' ? 'Workshop-Kontext:' : 'Workshop Context:' }}</span>
        {{ currentLanguage === 'de'
          ? 'Der Wechsel zwischen "Meine" und "Alle" macht die soziale Dimension kreativer KI-Arbeit sichtbar: Wann arbeite ich allein, wann teile ich? Diese bewusste Entscheidung ist pädagogisch wertvoll.'
          : 'Switching between "Mine" and "All" makes the social dimension of creative AI work visible: When do I work alone, when do I share? This conscious choice has pedagogical value.' }}
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{ currentLanguage: string }>()
</script>
