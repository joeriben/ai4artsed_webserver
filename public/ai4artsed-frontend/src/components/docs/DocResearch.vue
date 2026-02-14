<template>
  <section class="guide-section">
    <h2>{{ currentLanguage === 'de' ? 'Forschung' : 'Research' }}</h2>

    <div class="concept-card highlight">
      <h3>{{ currentLanguage === 'de' ? 'Wissenschaftliche Grundlagen' : 'Scientific Foundations' }}</h3>
      <p>{{ currentLanguage === 'de'
        ? 'Das UCDCAE AI LAB ist kein gewöhnliches Softwareprodukt. Es verkörpert bildungstheoretische Forschung im Kontext digitaler kultureller Bildung — insbesondere wissenschaftliche Erkenntnisse über den pädagogisch verantwortungsvollen Einsatz generativer KI.'
        : 'The UCDCAE AI LAB is not an ordinary software product. It embodies educational-theoretical research in the context of digital cultural education — specifically scientific insights on the pedagogically responsible use of generative AI.' }}</p>
    </div>

    <div class="step-card">
      <div class="step-header">
        <h3>{{ currentLanguage === 'de' ? 'Publikationen' : 'Publications' }}</h3>
      </div>
      <div class="mode-list">
        <div class="mode-item">
          <p>Jörissen, B. &amp; Baumann, V. (2026). Prompt Interception: Critical (Programming) Practice as Cultural Resilience in the Context of generative Artificial Intelligence. <em>MedienPädagogik</em> (in review).</p>
        </div>
        <div class="mode-item">
          <p>Jörissen, B. (2025). AI4ArtsEd-CESEM: A Software Framework for Critical Educational and Scientific Exploration and Manipulation of Generative AI. <a href="https://github.com/joeriben/ai4artsed" target="_blank" rel="noopener">github.com/joeriben/ai4artsed</a></p>
        </div>
        <div class="mode-item">
          <p>Jörissen, B. (2025). Digitalität im erziehungstheoretischen Blick: Strukturelle und epistemische Perspektiven. In: Fuchs, T. (Hrsg.), <em>Digitalität. Erziehungswissenschaftliche Erkundungen einer kulturellen Transformation</em>. Weinheim: Beltz Juventa.</p>
        </div>
        <div class="mode-item">
          <p>Jörissen, B., Klepacki, L., Flasche, V. &amp; Zahn, M. (2025). Wahrnehmungskrisen — „Generative Künstliche Intelligenz" als Herausforderung pädagogischer und erziehungswissenschaftlicher Wahrnehmungsweisen. In: Sturm, T. et al. (Hrsg.), <em>Krisen und Transformationen</em>. Verlag Barbara Budrich, 419–430.</p>
        </div>
        <div class="mode-item">
          <p>Jörissen, B. &amp; Klepacki, L. (2025). „Cultural Resilience" and the Cultivation of a Postdigital Planetary Dissensus. In: <em>Becoming Planetary</em> (accepted).</p>
        </div>
        <div class="mode-item">
          <p>Jörissen, B. (2022). Digitale Sympoiesis und kulturelle Resilienz: Alternative Perspektiven auf Digitalisierung im Anthropozän. <em>Vierteljahrsschrift für wissenschaftliche Pädagogik</em>, 98(4), 474–489.</p>
        </div>
      </div>
    </div>

    <div class="step-card">
      <div class="step-header">
        <h3>{{ currentLanguage === 'de' ? 'Die Plattform als Forschungsinstrument' : 'The Platform as Research Instrument' }}</h3>
      </div>
      <p>{{ currentLanguage === 'de'
        ? 'Die Architektur der Software — das pädagogische Sicherheitssystem, die Orchestrierungslogik und die Prompt-Interception-Architektur — basiert auf den publizierten wissenschaftlichen Erkenntnissen des Urhebers. Diese Architekturentscheidungen sind nicht beliebig oder austauschbar, sondern bilden die wissenschaftliche Substanz des Werkes.'
        : 'The architecture of the software — the pedagogical safety system, the orchestration logic, and the prompt interception architecture — is grounded in the author\'s published academic work. These architectural decisions are neither arbitrary nor interchangeable; they constitute the scientific substance of this work.' }}</p>
    </div>

    <div class="step-card">
      <div class="step-header">
        <h3>{{ currentLanguage === 'de' ? 'Forschungsmodus' : 'Research Mode' }}</h3>
      </div>
      <p>{{ currentLanguage === 'de'
        ? 'Der Forschungsmodus (Safety-Level "Forschung") deaktiviert alle Sicherheitsmechanismen und ist ausschließlich für autorisierte Forschungseinrichtungen bestimmt. Voraussetzungen: dokumentierter Forschungszweck, ethische Aufsicht, keine Exposition von Minderjährigen gegenüber ungefilterten Ausgaben.'
        : 'Research Mode (Safety Level "Research") disables all safety mechanisms and is intended exclusively for authorized research institutions. Requirements: documented research purpose, ethical oversight, no exposure of minors to unfiltered outputs.' }}</p>
      <p style="margin-top: 0.5rem;"><em>{{ currentLanguage === 'de'
        ? 'Details siehe LICENSE.md §3(e).'
        : 'See LICENSE.md Section 3(e) for details.' }}</em></p>
    </div>

    <div class="contact-box">
      <h3>{{ currentLanguage === 'de' ? 'Quellcode' : 'Source Code' }}</h3>
      <p><a href="https://github.com/joeriben/ai4artsed" target="_blank" rel="noopener">github.com/joeriben/ai4artsed</a></p>
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{ currentLanguage: string }>()
</script>
