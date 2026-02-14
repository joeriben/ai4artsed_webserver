<template>
  <section class="canvas-section">
    <div class="canvas-header">
      <svg xmlns="http://www.w3.org/2000/svg" height="48" viewBox="0 0 24 24" width="48" fill="currentColor" class="canvas-header-icon">
        <path d="M22 11V3h-7v3H9V3H2v8h7V8h2v10h4v3h7v-8h-7v3h-2V8h2v3z"/>
      </svg>
      <div>
        <h2>{{ currentLanguage === 'de' ? 'Canvas Workflow System' : 'Canvas Workflow System' }}</h2>
        <p class="section-intro">{{ currentLanguage === 'de'
          ? 'Canvas ist eine visuelle Forschungs-Workbench für die systematische Erkundung generativer KI.'
          : 'Canvas is a visual research workbench for systematic exploration of generative AI.' }}</p>
      </div>
    </div>

    <div class="canvas-card" style="border-left: 3px solid #06b6d4; margin-bottom: 1rem;">
      <p><em>{{ currentLanguage === 'de'
        ? 'Verfügbar ab Safety-Level "Erwachsene".'
        : 'Available from Safety Level "Adult".' }}</em></p>
    </div>

    <div class="canvas-card paradigm">
      <h3>{{ currentLanguage === 'de' ? 'Lehrforschung' : 'Exploratory Research' }}</h3>
      <p>{{ currentLanguage === 'de'
        ? 'Canvas ist für gemeinsames Erforschen in Workshops, Unterricht oder zur Professionalisierung konzipiert. Anders als technische Systeme wie ComfyUI oder Max/MSP verzichtet Canvas bewusst auf tiefe technische Parametrierung – dafür macht es strukturelle Komplexität sichtbar und erforschbar.'
        : 'Canvas is designed for collaborative exploration in workshops, teaching, or professional development. Unlike technical systems like ComfyUI or Max/MSP, Canvas deliberately avoids deep technical parameterization – instead, it makes structural complexity visible and explorable.' }}</p>
    </div>

    <div class="canvas-card interception">
      <h3>{{ currentLanguage === 'de' ? 'Prompt Interception' : 'Prompt Interception' }}</h3>
      <p>{{ currentLanguage === 'de'
        ? 'Konventionelle KI-Interfaces machen Nutzende zu Befehlsgebenden, die zugleich der Maschinenlogik unterworfen sind. Prompt Interception bricht dieses Muster auf: Das LLM bringt Neues und Unwägbarkeiten in den Prozess ein. Nutzende und KI erzeugen gemeinsam neue Feedback-Loops. Die Maschine dient dem kreativen Werden – nicht umgekehrt.'
        : 'Conventional AI interfaces turn users into commanders who are simultaneously subjected to machine logic. Prompt Interception breaks this pattern: The LLM introduces novelty and unpredictability into the process. Users and AI create new feedback loops together. The machine serves creative becoming – not vice versa.' }}</p>
      <p class="pragmatic-note">{{ currentLanguage === 'de'
        ? 'Pragmatisch ermöglicht Interception auch komplexere Prompts – wesentlich für echte KI-Erkundung. Einfache Prompts erzeugen notwendig klischeehafte Outputs. Erst mit angemessen komplexen Prompts lassen sich Biases, aber auch interessante Eigenheiten des Systems systematisch erfahren.'
        : 'Pragmatically, Interception also enables more complex prompts – essential for genuine AI exploration. Simple prompts necessarily produce clichéd outputs. Only with appropriately complex prompts can biases, but also interesting system characteristics, be systematically experienced.' }}</p>
    </div>

    <div class="canvas-card recursive">
      <h3>{{ currentLanguage === 'de' ? 'Rekursiv-reflexive Workflows' : 'Recursive-Reflexive Workflows' }}</h3>
      <p>{{ currentLanguage === 'de'
        ? 'Ein Novum, das wir von keiner anderen genAI-Plattform kennen: Evaluation-Nodes können Feedback an andere Nodes zurückgeben. Der Workflow wird rekursiv durchlaufen, bis nutzerdefinierte Kriterien erfüllt sind. So entstehen experimentelle Setups zur Erforschung von:'
        : 'A novelty we don\'t know from any other genAI platform: Evaluation nodes can feed back to other nodes. The workflow runs recursively until user-defined criteria are met. This enables experimental setups for researching:' }}</p>
      <ul>
        <li>{{ currentLanguage === 'de' ? 'Biases in Modellen' : 'Biases in models' }}</li>
        <li>{{ currentLanguage === 'de' ? 'Normiertheit vs. "Kreativität"' : 'Normativity vs. "creativity"' }}</li>
        <li>{{ currentLanguage === 'de' ? 'Ethische Bewertung von LLM-Outputs' : 'Ethical assessment of LLM outputs' }}</li>
        <li>{{ currentLanguage === 'de' ? 'Vergleichende Analysen mit Massenoutput' : 'Comparative analyses with mass output' }}</li>
      </ul>
    </div>

    <div class="canvas-card target-groups">
      <h3>{{ currentLanguage === 'de' ? 'Zielgruppen' : 'Target Groups' }}</h3>
      <p>{{ currentLanguage === 'de'
        ? 'Verfügbar nur bei Safety "Erwachsene" aufgrund — aus technischen Gründen — unvorhersehbarer Text- und Bildergebnisse. Verwendung mit Personen unter 18 auf eigenes Risiko und unter strenger Aufsicht.'
        : 'Available only at Safety "Adult" due to — for technical reasons — unpredictable text and image results. Use with persons under 18 at your own risk and under strict supervision.' }}</p>
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{ currentLanguage: string }>()
</script>
