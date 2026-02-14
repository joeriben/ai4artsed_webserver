<template>
  <section class="guide-section">
    <h2>{{ currentLanguage === 'de' ? 'Musikgenerierung' : 'Music Generation' }}</h2>

    <div class="concept-card highlight">
      <h3>{{ currentLanguage === 'de' ? 'KI-generierte Musik mit Tags und Lyrics' : 'AI-Generated Music with Tags and Lyrics' }}</h3>
      <p>{{ currentLanguage === 'de'
        ? 'Die Musikgenerierung arbeitet anders als die visuellen Modi: Statt eines Text-Prompts steuerst du die Musik über Stil-Tags und Lyrics. Tags definieren den musikalischen Stil, Lyrics den gesungenen Inhalt. Beides ist unabhängig voneinander experimentierbar.'
        : 'Music Generation works differently from the visual modes: Instead of a text prompt, you control the music through style tags and lyrics. Tags define the musical style, lyrics define the sung content. Both can be experimented with independently.' }}</p>
    </div>

    <div class="step-card">
      <div class="step-header">
        <span class="step-badge">1</span>
        <h3>{{ currentLanguage === 'de' ? 'Tags wählen' : 'Choose Tags' }}</h3>
      </div>
      <p>{{ currentLanguage === 'de'
        ? 'Tags beschreiben den musikalischen Stil in 8 Dimensionen:'
        : 'Tags describe the musical style across 8 dimensions:' }}</p>
      <div class="mode-list">
        <div class="mode-item">
          <strong>Genre</strong>
          <p>{{ currentLanguage === 'de' ? 'Pop, Rock, Jazz, Electronic, Hip-Hop, Classical ...' : 'Pop, Rock, Jazz, Electronic, Hip-Hop, Classical ...' }}</p>
        </div>
        <div class="mode-item">
          <strong>Mood</strong>
          <p>{{ currentLanguage === 'de' ? 'Happy, Melancholic, Energetic, Calm, Dark ...' : 'Happy, Melancholic, Energetic, Calm, Dark ...' }}</p>
        </div>
        <div class="mode-item">
          <strong>Instrument</strong>
          <p>{{ currentLanguage === 'de' ? 'Piano, Guitar, Synthesizer, Drums, Strings ...' : 'Piano, Guitar, Synthesizer, Drums, Strings ...' }}</p>
        </div>
        <div class="mode-item">
          <strong>{{ currentLanguage === 'de' ? 'Weitere Dimensionen' : 'More Dimensions' }}</strong>
          <p>{{ currentLanguage === 'de'
            ? 'Timbre (Klangfarbe), Gender (Stimme), Scene (Szene/Kontext), Region (Kulturkreis), Topic (Thema)'
            : 'Timbre (sound color), Gender (voice), Scene (context), Region (cultural sphere), Topic (theme)' }}</p>
        </div>
      </div>
    </div>

    <div class="step-card">
      <div class="step-header">
        <span class="step-badge">2</span>
        <h3>{{ currentLanguage === 'de' ? 'Lyrics eingeben oder generieren' : 'Enter or Generate Lyrics' }}</h3>
      </div>
      <p>{{ currentLanguage === 'de'
        ? 'Du kannst eigene Lyrics schreiben oder sie von der KI generieren lassen. Die Lyrics können in mehreren Sprachen verfasst werden: Deutsch, Englisch, Chinesisch, Japanisch, Koreanisch und Spanisch.'
        : 'You can write your own lyrics or have the AI generate them. Lyrics can be written in multiple languages: German, English, Chinese, Japanese, Korean, and Spanish.' }}</p>
    </div>

    <div class="step-card">
      <div class="step-header">
        <span class="step-badge">3</span>
        <h3>{{ currentLanguage === 'de' ? 'Song generieren' : 'Generate Song' }}</h3>
      </div>
      <p>{{ currentLanguage === 'de'
        ? 'Das Musikmodell erzeugt einen Song basierend auf deinen Tags und Lyrics. Die Generierung dauert etwas — das Modell arbeitet im Hintergrund.'
        : 'The music model generates a song based on your tags and lyrics. Generation takes a moment — the model works in the background.' }}</p>
    </div>

    <div class="concept-card highlight">
      <h3>{{ currentLanguage === 'de' ? 'Experimentier-Tipps' : 'Experimentation Tips' }}</h3>
      <p>{{ currentLanguage === 'de'
        ? 'Versuche gegensätzliche Tag-Kombinationen: "classical" + "electronic", "dark" + "happy". Oder ändere nur die Tags bei gleichen Lyrics — so hörst du, wie dieselben Worte in verschiedenen musikalischen Welten klingen. Tags und Lyrics sind zwei unabhängige Achsen, die du frei kombinieren kannst.'
        : 'Try contradictory tag combinations: "classical" + "electronic", "dark" + "happy". Or change only the tags with the same lyrics — to hear how the same words sound in different musical worlds. Tags and lyrics are two independent axes that you can freely combine.' }}</p>
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{ currentLanguage: string }>()
</script>
