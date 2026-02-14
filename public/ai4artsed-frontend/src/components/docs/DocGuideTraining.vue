<template>
  <section class="info-section">
    <h2>LoRA Training</h2>
    <p>{{ currentLanguage === 'de'
      ? 'Das LoRA Training Studio ermöglicht es, eigene Bildmodelle zu trainieren – direkt in der Plattform, ohne externe Tools. LoRA (Low-Rank Adaptation) ist ein Verfahren, das ein vorhandenes Bildgenerierungsmodell (hier: Stable Diffusion 3.5 Large) mit eigenen Bildern verfeinert, ohne das gesamte Modell neu zu trainieren.'
      : 'The LoRA Training Studio lets you train custom image models – directly in the platform, without external tools. LoRA (Low-Rank Adaptation) is a technique that fine-tunes an existing image generation model (here: Stable Diffusion 3.5 Large) with your own images, without retraining the entire model.' }}</p>

    <div class="step-card">
      <div class="step-header">
        <span class="step-badge">1</span>
        <h3>{{ currentLanguage === 'de' ? 'Eigene Bilder hochladen' : 'Upload your images' }}</h3>
      </div>
      <p>{{ currentLanguage === 'de'
        ? 'Du lädst eine Reihe eigener Bilder hoch – z.B. Zeichnungen, Fotos oder Collagen. Diese Bilder definieren, was das Modell lernen soll: eine bestimmte visuelle Qualität, ein Material, eine Handschrift.'
        : 'You upload a set of your own images – e.g. drawings, photos, or collages. These images define what the model should learn: a specific visual quality, a material, a handwriting.' }}</p>
    </div>

    <div class="step-card">
      <div class="step-header">
        <span class="step-badge">2</span>
        <h3>{{ currentLanguage === 'de' ? 'Training starten' : 'Start training' }}</h3>
      </div>
      <p>{{ currentLanguage === 'de'
        ? 'Das Training dauert je nach Bildanzahl 1–3 Stunden. Während des Trainings ist die Bildgenerierung blockiert, da die GPU vollständig ausgelastet ist.'
        : 'Training takes 1–3 hours depending on the number of images. During training, image generation is blocked as the GPU is fully utilized.' }}</p>
    </div>

    <div class="step-card">
      <div class="step-header">
        <span class="step-badge">3</span>
        <h3>{{ currentLanguage === 'de' ? 'Eigenes Modell nutzen' : 'Use your model' }}</h3>
      </div>
      <p>{{ currentLanguage === 'de'
        ? 'Das trainierte LoRA-Modell erscheint anschließend als eigene Modelloption in der Bildgenerierung. Es kann wie jedes andere Modell verwendet werden – mit dem Unterschied, dass es die visuelle Sprache deiner eigenen Bilder gelernt hat.'
        : 'The trained LoRA model then appears as a custom model option in image generation. It can be used like any other model – with the difference that it has learned the visual language of your own images.' }}</p>
    </div>

    <div class="concept-card">
      <h3>{{ currentLanguage === 'de' ? 'Warum ist das wichtig?' : 'Why does this matter?' }}</h3>
      <p>{{ currentLanguage === 'de'
        ? 'Generative Bildmodelle sind geschlossene Systeme: Ihr Training erfolgt durch große Unternehmen auf riesigen Datensätzen, die für Einzelne weder einsehbar noch beeinflussbar sind. Selbst Fachleute können diese Modelle nicht ohne Weiteres trainieren – die Kosten, Daten und Hardware übersteigen individuelle Möglichkeiten bei Weitem.'
        : 'Generative image models are closed systems: they are trained by large companies on massive datasets that are neither visible nor controllable by individuals. Even experts cannot easily train these models – the costs, data, and hardware far exceed individual capabilities.' }}</p>
      <p style="margin-top: 0.75rem;">{{ currentLanguage === 'de'
        ? 'LoRA öffnet hier einen Spalt: Es ermöglicht, eigene ästhetische und künstlerische Perspektiven in ein bestehendes Modell einzubringen – z.B. lebensweltliche Erfahrungen wie Fotos von Schulgebäuden, eigene Zeichnungen oder Materialstudien (natürlich ohne Personen). So können Lernende nicht nur mit dem Modell arbeiten, sondern ein Stück weit mitbestimmen, was es "sieht" und erzeugt.'
        : 'LoRA opens a crack here: it makes it possible to bring your own aesthetic and artistic perspectives into an existing model – e.g. real-world experiences like photos of school buildings, your own drawings, or material studies (without people, of course). This way, learners can not only work with the model, but also have a say in what it "sees" and generates.' }}</p>
      <p style="margin-top: 0.75rem;">{{ currentLanguage === 'de'
        ? 'Gleichzeitig wird sichtbar, wie Trainingsdaten die "Weltsicht" eines Modells formen – und wie begrenzt oder verzerrt diese sein kann. Die Frage, worauf ein Modell trainiert wurde, bestimmt fundamental, was es erzeugen kann.'
        : 'At the same time, it becomes visible how training data shapes a model\'s "worldview" – and how limited or biased it can be. The question of what a model was trained on fundamentally determines what it can generate.' }}</p>
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{ currentLanguage: string }>()
</script>
