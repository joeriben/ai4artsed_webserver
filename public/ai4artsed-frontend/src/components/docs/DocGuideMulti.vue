<template>
  <section class="guide-section">
    <h2>{{ currentLanguage === 'de' ? 'Bildfusion' : 'Image Fusion' }}</h2>

    <div class="concept-card highlight">
      <h3>{{ currentLanguage === 'de' ? 'Mehrere Bilder, ein neues Werk' : 'Multiple Images, One New Work' }}</h3>
      <p>{{ currentLanguage === 'de'
        ? 'Im Multi-Bild-Modus lädst du bis zu drei Bilder hoch, die zu einer neuen Komposition verschmolzen werden. Das Ergebnis ist keine Collage — die Bilder werden im Embedding-Raum der KI fusioniert, sodass etwas Neues entsteht, das Aspekte aller Eingaben in sich trägt.'
        : 'In Multi-Image Mode, you upload up to three images that are fused into a new composition. The result is not a collage — the images are fused in the AI\'s embedding space, creating something new that carries aspects of all inputs.' }}</p>
    </div>

    <div class="step-card">
      <div class="step-header">
        <span class="step-badge">1</span>
        <h3>{{ currentLanguage === 'de' ? 'Bilder hochladen (bis zu 3)' : 'Upload Images (up to 3)' }}</h3>
      </div>
      <p>{{ currentLanguage === 'de'
        ? 'Wähle bis zu drei Bilder aus. Je unterschiedlicher die Bilder, desto überraschender das Ergebnis. Probiere: ein Foto + eine Zeichnung + ein generiertes Bild.'
        : 'Select up to three images. The more different the images, the more surprising the result. Try: a photo + a drawing + a generated image.' }}</p>
    </div>

    <div class="step-card">
      <div class="step-header">
        <span class="step-badge">2</span>
        <h3>{{ currentLanguage === 'de' ? 'Beschreiben, was entstehen soll' : 'Describe What Should Emerge' }}</h3>
      </div>
      <p>{{ currentLanguage === 'de'
        ? 'Beschreibe, wie die Bilder kombiniert werden sollen. Du kannst auf Stimmung, Stil, Komposition oder Bedeutung eingehen. Die KI nutzt diese Beschreibung zusammen mit den Bildern als Ausgangspunkt.'
        : 'Describe how the images should be combined. You can address mood, style, composition, or meaning. The AI uses this description together with the images as a starting point.' }}</p>
    </div>

    <div class="step-card">
      <div class="step-header">
        <span class="step-badge">3</span>
        <h3>{{ currentLanguage === 'de' ? 'Regeln und Modell wählen' : 'Choose Rules and Model' }}</h3>
      </div>
      <p>{{ currentLanguage === 'de'
        ? 'Wie in den anderen Modi kannst du Regeln anwenden, die die Fusion beeinflussen. Das Modell bestimmt den visuellen Stil des Ergebnisses.'
        : 'As in the other modes, you can apply rules that influence the fusion. The model determines the visual style of the result.' }}</p>
    </div>

    <div class="concept-card highlight">
      <h3>{{ currentLanguage === 'de' ? 'Experimentier-Ideen' : 'Experiment Ideas' }}</h3>
      <p>{{ currentLanguage === 'de'
        ? 'Besonders spannend wird die Bildfusion, wenn die Quellbilder aus unterschiedlichen Kontexten stammen: ein Naturfoto mit einem abstrakten Gemälde, ein Selfie mit einer historischen Aufnahme, oder drei Bilder desselben Motivs aus verschiedenen Stilen. Die Spannung zwischen den Eingaben ist das, was die Fusion interessant macht.'
        : 'Image Fusion becomes particularly exciting when the source images come from different contexts: a nature photo with an abstract painting, a selfie with a historical photograph, or three images of the same subject in different styles. The tension between the inputs is what makes the fusion interesting.' }}</p>
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{ currentLanguage: string }>()
</script>
