<template>
  <div class="legal-page">
    <div class="legal-container">
      <h1>{{ $t('legal.privacy.title') }}</h1>

      <section>
        <h2>{{ $t('legal.privacy.section1.title') }}</h2>
        <p>{{ $t('legal.privacy.section1.content') }}</p>
      </section>

      <section>
        <h2>{{ $t('legal.privacy.section2.title') }}</h2>
        <p>{{ $t('legal.privacy.section2.content') }}</p>
      </section>

      <section>
        <h2>{{ $t('legal.privacy.section3.title') }}</h2>
        <p>{{ $t('legal.privacy.section3.content') }}</p>
      </section>

      <section>
        <h2>{{ $t('legal.privacy.fauReference.title') }}</h2>
        <p>
          {{ $t('legal.privacy.fauReference.content') }}<br>
          <a href="https://www.fau.de/datenschutz" target="_blank" rel="noopener noreferrer">
            www.fau.de/datenschutz
          </a>
        </p>
      </section>
    </div>
  </div>
</template>

<style scoped>
.legal-page {
  min-height: 100vh;
  background: #0a0a0a;
  padding: 2rem;
  color: #ffffff;
}

.legal-container {
  max-width: 900px;
  margin: 0 auto;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 2.5rem;
}

h1 {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 2rem;
  color: #ffffff;
  border-bottom: 2px solid rgba(76, 175, 80, 0.3);
  padding-bottom: 0.5rem;
}

h2 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-top: 2rem;
  margin-bottom: 0.75rem;
  color: rgba(255, 255, 255, 0.9);
}

section {
  margin-bottom: 1.5rem;
}

p {
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.8);
}

a {
  color: #4CAF50;
  text-decoration: none;
  transition: color 0.3s ease;
}

a:hover {
  color: #66BB6A;
  text-decoration: underline;
}

@media (max-width: 768px) {
  .legal-page {
    padding: 1rem;
  }

  .legal-container {
    padding: 1.5rem;
  }

  h1 {
    font-size: 1.5rem;
  }
}
</style>
