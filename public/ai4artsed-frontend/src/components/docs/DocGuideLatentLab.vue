<template>
  <section class="experiments-section">
    <h2>Latent Lab</h2>
    <p class="section-intro">{{ currentLanguage === 'de'
      ? 'Das Latent Lab arbeitet auf der mathematischen Ebene der KI-Modelle. Es zeigt, wie Sprache und Bedeutung in Vektoren übersetzt werden \u2013 und was passiert, wenn wir diese Vektoren manipulieren.'
      : 'The Latent Lab works at the mathematical level of AI models. It shows how language and meaning are translated into vectors \u2013 and what happens when we manipulate these vectors.' }}</p>
    <p class="section-intro" style="opacity: 0.7; font-style: italic;">{{ currentLanguage === 'de'
      ? 'Verfügbar nur bei Sicherheitsstufe "Erwachsene" oder "Forschung" \u2014 aus technischen Gründen sind Text- und Bildergebnisse unvorhersehbar. "Erwachsene" meint hier nicht "FSK 18", sondern verweist auf die Notwendigkeit mündiger Verantwortlichkeit der Bedienenden. Das kann auch bedeuten: zentral im Unterricht unter Aufsicht oder durch Lehrende bedient.'
      : 'Available only at Safety Level "Adult" or "Research" \u2014 for technical reasons, text and image results are unpredictable. "Adult" here does not mean age-restricted content, but refers to the need for responsible, informed operation. This can also mean: used centrally in class under supervision or operated by teachers.' }}</p>

    <!-- Hallucinator -->
    <div class="experiment-card surrealizer">
      <h3>Hallucinator</h3>
      <div class="experiment-what">
        <strong>{{ currentLanguage === 'de' ? 'Was passiert hier?' : 'What happens here?' }}</strong>
        <p>{{ currentLanguage === 'de'
          ? 'Dein Prompt wird von zwei verschiedenen KI-"Gehirnen" gelesen: CLIP-L (trainiert auf Bild-Text-Paaren, "denkt" visuell) und T5 (trainiert auf reinem Text, "denkt" sprachlich). Bei \u03b1=0 siehst du ein normales CLIP-Bild. Aber der Regler mischt nicht einfach zwischen beiden \u2014 er extrapoliert: Bei \u03b1=20 wird das Embedding 19\u00d7 \u00fcber die T5-Interpretation hinaus geschoben, in einen mathematischen Raum, den das Modell im Training nie gesehen hat.'
          : 'Your prompt is read by two different AI "brains": CLIP-L (trained on image-text pairs, "thinks" visually) and T5 (trained on pure text, "thinks" linguistically). At \u03b1=0 you see a normal CLIP image. But the slider doesn\'t simply blend between them \u2014 it extrapolates: at \u03b1=20, the embedding is pushed 19\u00d7 beyond T5\'s interpretation, into a mathematical space the model never encountered during training.' }}</p>
      </div>
      <div class="experiment-why">
        <strong>{{ currentLanguage === 'de' ? 'Warum werden die Bilder surreal?' : 'Why do images become surreal?' }}</strong>
        <p>{{ currentLanguage === 'de'
          ? 'Das Modell muss Vektoren interpretieren, die weit au\u00dferhalb seiner Trainingsdaten liegen. Es "halluziniert" auf \u00e4sthetisch \u00fcberraschende Weise \u2014 Formen, Farben und Strukturen entstehen, die kein direkter Prompt erzeugen k\u00f6nnte. Gleichzeitig bleiben die restlichen T5-Tokens (ab Token 78) unver\u00e4ndert und wirken als semantischer Anker: Das Bild bleibt mit deinem Text verbunden, auch wenn die visuelle Darstellung surreal wird.'
          : 'The model must interpret vectors that lie far outside its training data. It "hallucinates" in aesthetically surprising ways \u2014 shapes, colors, and structures emerge that no direct prompt could produce. Meanwhile, the remaining T5 tokens (from token 78 onward) stay unchanged, acting as a semantic anchor: the image stays connected to your text even as the visual representation becomes surreal.' }}</p>
      </div>
      <div class="experiment-example">
        <strong>{{ currentLanguage === 'de' ? 'Bereiche:' : 'Ranges:' }}</strong>
        {{ currentLanguage === 'de'
          ? '\u03b1=0: normales Bild (nur CLIP-L) | \u03b1=1: reines T5 (noch normal) | \u03b1=15\u201335: surrealer Sweet Spot (Extrapolation) | \u03b1>50: extreme Verzerrung'
          : '\u03b1=0: normal image (CLIP-L only) | \u03b1=1: pure T5 (still normal) | \u03b1=15\u201335: surreal sweet spot (extrapolation) | \u03b1>50: extreme distortion' }}
      </div>
      <div class="experiment-negative">
        <strong>{{ currentLanguage === 'de' ? 'Negative \u03b1 \u2014 die Gegenrichtung:' : 'Negative \u03b1 \u2014 the reverse direction:' }}</strong>
        <p>{{ currentLanguage === 'de'
          ? 'Bei negativem \u03b1 wird CLIP-L verst\u00e4rkt und T5 negiert. Bei \u03b1=-10 ergibt die Formel: 11\u00b7CLIP-L + (-10)\u00b7T5. Der Effekt geht tiefer als "weniger T5": Weil CLIP-L nur 768 von 4096 Dimensionen f\u00fcllt (der Rest ist Nullen), werden in den oberen 3328 Dimensionen die T5-Vektoren invertiert. In der Cross-Attention des Transformers kehrt das die Aufmerksamkeitsmuster um \u2014 Textteile, die normalerweise am wichtigsten w\u00e4ren, werden ignoriert, unwichtige dominieren. Das Ergebnis: visuell getriebene Halluzinationen mit gest\u00f6rter Semantik, qualitativ anders als positive Extrapolation.'
          : 'With negative \u03b1, CLIP-L is amplified and T5 is negated. At \u03b1=-10 the formula yields: 11\u00b7CLIP-L + (-10)\u00b7T5. The effect goes deeper than "less T5": because CLIP-L only fills 768 of 4096 dimensions (the rest are zeros), the upper 3328 dimensions get inverted T5 vectors. In the transformer\'s cross-attention, this inverts the attention patterns \u2014 text tokens that would normally be most important are ignored, while insignificant ones dominate. The result: visually driven hallucinations with disrupted semantics, qualitatively different from positive extrapolation.' }}</p>
      </div>

      <!-- Deep Dive: Mathematics -->
      <button class="deep-dive-toggle" @click="showHallucinatorMath = !showHallucinatorMath">
        {{ currentLanguage === 'de' ? '\ud83d\udcd0 Die Mathematik im Detail' : '\ud83d\udcd0 The Mathematics in Detail' }}
        <span class="toggle-arrow">{{ showHallucinatorMath ? '\u25b2' : '\u25bc' }}</span>
      </button>

      <div v-if="showHallucinatorMath" class="deep-dive-content">
        <!-- Section 1: Two Worlds -->
        <h4>{{ currentLanguage === 'de' ? 'CLIP-L vs T5-XXL: Zwei verschiedene "Welten"' : 'CLIP-L vs T5-XXL: Two Different "Worlds"' }}</h4>
        <p>{{ currentLanguage === 'de'
          ? 'Stell dir den Embedding-Raum als einen hochdimensionalen Raum vor. Jeder Encoder bildet denselben Text auf einen anderen Punkt in diesem Raum ab:'
          : 'Imagine the embedding space as a high-dimensional space. Each encoder maps the same text to a different point in this space:' }}</p>
        <pre class="math-diagram">Prompt: "Ein Haus am See"

CLIP-L \u2192 Punkt C = [0.3, -0.7, 0.1, ...]  (768 Dimensionen)
T5-XXL \u2192 Punkt T = [0.5, -0.2, 0.8, ...]  (4096 Dimensionen)</pre>
        <p>{{ currentLanguage === 'de'
          ? 'Warum sind die Punkte verschieden? CLIP-L wurde mit Bild-Text-Paaren trainiert (kontrastives Lernen). Es "denkt" visuell: "Was f\u00fcr ein Bild passt zu diesem Text?" T5-XXL wurde als Sprach-Modell trainiert. Es "denkt" semantisch-linguistisch: "Was bedeutet dieser Text?"'
          : 'Why are the points different? CLIP-L was trained on image-text pairs (contrastive learning). It "thinks" visually: "What image fits this text?" T5-XXL was trained as a language model. It "thinks" semantically-linguistically: "What does this text mean?"' }}</p>
        <p>{{ currentLanguage === 'de'
          ? 'Dasselbe Wort "Haus" aktiviert in CLIP-L andere Neuronen als in T5. CLIP-L hat gelernt, dass "Haus" korreliert mit bestimmten visuellen Features (Dach-Form, Fenster, W\u00e4nde). T5 hat gelernt, dass "Haus" in Beziehung steht zu "Geb\u00e4ude", "Wohnung", "Heim", "Architektur".'
          : 'The same word "house" activates different neurons in CLIP-L than in T5. CLIP-L learned that "house" correlates with certain visual features (roof shape, windows, walls). T5 learned that "house" relates to "building", "apartment", "home", "architecture".' }}</p>

        <!-- Section 2: LERP Geometry -->
        <h4>{{ currentLanguage === 'de' ? 'Die LERP-Formel geometrisch' : 'The LERP Formula Geometrically' }}</h4>
        <pre class="math-diagram">fused(\u03b1) = (1 - \u03b1) \u00b7 C + \u03b1 \u00b7 T</pre>
        <p>{{ currentLanguage === 'de'
          ? 'Das ist eine parametrische Gerade durch C und T im Embedding-Raum:'
          : 'This is a parametric line through C and T in the embedding space:' }}</p>
        <pre class="math-diagram">\u03b1 = 0.0  \u2192  Punkt C (reines CLIP-L, "visuell-literal")
\u03b1 = 0.5  \u2192  Mittelpunkt zwischen C und T
\u03b1 = 1.0  \u2192  Punkt T (reines T5, "semantisch-linguistisch")

       C \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500 T
       \u03b1=0    \u03b1=0.5    \u03b1=1</pre>
        <p>{{ currentLanguage === 'de'
          ? 'Bis hier ist es Interpolation \u2014 wir bleiben zwischen zwei bekannten Punkten. Das Modell hat f\u00fcr beide Punkte gelernt, sinnvolle Bilder zu produzieren. Die Ergebnisse sind "normal".'
          : 'Up to here it\'s interpolation \u2014 we stay between two known points. The model learned to produce sensible images for both points. The results are "normal".' }}</p>

        <!-- Section 3: Extrapolation -->
        <h4>{{ currentLanguage === 'de' ? 'Was passiert bei \u03b1 > 1? Extrapolation!' : 'What happens at \u03b1 > 1? Extrapolation!' }}</h4>
        <pre class="math-diagram">\u03b1 = 20  \u2192  fused = (1 - 20) \u00b7 C + 20 \u00b7 T = -19\u00b7C + 20\u00b7T</pre>
        <p>{{ currentLanguage === 'de'
          ? 'Geometrisch: Wir gehen durch T hindurch und 19\u00d7 so weit dar\u00fcber hinaus:'
          : 'Geometrically: we pass through T and go 19\u00d7 further beyond:' }}</p>
        <pre class="math-diagram">   C \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500 T \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500 \u03b1=20
   \u2190 bekannt \u2192\u2190          terra incognita              \u2192</pre>
        <p>{{ currentLanguage === 'de'
          ? 'Der Punkt bei \u03b1=20 liegt 19 Mal weiter von T entfernt als T von C. Dieses Gebiet hat das Diffusion-Modell w\u00e4hrend des Trainings nie gesehen. Es muss trotzdem etwas daraus generieren \u2014 und das Ergebnis ist surreal, weil:'
          : 'The point at \u03b1=20 lies 19 times further from T than T is from C. The diffusion model never saw this region during training. It must still generate something from it \u2014 and the result is surreal because:' }}</p>
        <div class="math-list">
          <p>{{ currentLanguage === 'de'
            ? '1. Feature-Verst\u00e4rkung: Was T5 anders "sieht" als CLIP-L wird massiv verst\u00e4rkt. Wenn T5 "Haus" st\u00e4rker mit "Geborgenheit" assoziiert als CLIP-L, wird bei \u03b1=20 die Geborgenheits-Dimension 19\u00d7 \u00fcbertrieben.'
            : '1. Feature amplification: What T5 "sees" differently from CLIP-L gets massively amplified. If T5 associates "house" more strongly with "coziness" than CLIP-L, the coziness dimension gets exaggerated 19\u00d7.' }}</p>
          <p>{{ currentLanguage === 'de'
            ? '2. Feature-Unterdr\u00fcckung: Was CLIP-L betont und T5 nicht, wird negiert (Faktor -19). Visuelle Literalit\u00e4t wird aktiv unterdr\u00fcckt.'
            : '2. Feature suppression: What CLIP-L emphasizes and T5 doesn\'t gets negated (factor -19). Visual literalness is actively suppressed.' }}</p>
          <p>{{ currentLanguage === 'de'
            ? '3. Nicht-Linearit\u00e4t des Decoders: Der DiT-Decoder wurde trainiert, Embeddings in einem bestimmten Bereich zu verarbeiten. Out-of-distribution-Inputs erzeugen unvorhersehbare, aber koh\u00e4rente Artefakte \u2014 \u00e4hnlich wie DeepDream, aber gesteuert.'
            : '3. Decoder non-linearity: The DiT decoder was trained to process embeddings within a certain range. Out-of-distribution inputs produce unpredictable but coherent artifacts \u2014 similar to DeepDream, but steered.' }}</p>
        </div>

        <!-- Section 4: Token Level -->
        <h4>{{ currentLanguage === 'de' ? 'Warum Token-Level statt Global?' : 'Why Token-Level Instead of Global?' }}</h4>
        <p>{{ currentLanguage === 'de'
          ? 'Die Fusion passiert pro Token, nicht \u00fcber den ganzen Embedding-Vektor:'
          : 'The fusion happens per token, not across the entire embedding vector:' }}</p>
        <pre class="math-diagram">Token 1 ("Ein"):   fused[1] = (1-\u03b1)\u00b7CLIP_L[1] + \u03b1\u00b7T5[1]
Token 2 ("Haus"):  fused[2] = (1-\u03b1)\u00b7CLIP_L[2] + \u03b1\u00b7T5[2]
Token 3 ("am"):    fused[3] = (1-\u03b1)\u00b7CLIP_L[3] + \u03b1\u00b7T5[3]
Token 4 ("See"):   fused[4] = (1-\u03b1)\u00b7CLIP_L[4] + \u03b1\u00b7T5[4]
...
Token 78-512:      reines T5 (semantischer Anker)</pre>
        <p>{{ currentLanguage === 'de'
          ? 'Das ist entscheidend, weil jedes Token eine andere Diskrepanz zwischen CLIP und T5 hat: "Haus" \u2192 gro\u00dfe Diskrepanz (visuell vs. semantisch sehr unterschiedlich) \u2192 starker Halluzinations-Effekt. "am" \u2192 kleine Diskrepanz (Funktionswort, beide Encoder \u00e4hnlich) \u2192 wenig Effekt.'
          : 'This is crucial because each token has a different discrepancy between CLIP and T5: "house" \u2192 large discrepancy (visual vs. semantic very different) \u2192 strong hallucination effect. "at" \u2192 small discrepancy (function word, both encoders similar) \u2192 little effect.' }}</p>
        <p>{{ currentLanguage === 'de'
          ? 'Die Tokens 78\u2013512 (reines T5) dienen als semantischer Anker \u2014 sie geben dem Modell genug "normalen" Kontext, damit das Bild nicht komplett ins Chaos abdriftet.'
          : 'Tokens 78\u2013512 (pure T5) serve as a semantic anchor \u2014 they give the model enough "normal" context so the image doesn\'t drift into complete chaos.' }}</p>

        <!-- Section 5: Ranges -->
        <h4>{{ currentLanguage === 'de' ? 'Die Grenzbereiche' : 'The Boundary Ranges' }}</h4>
        <pre class="math-diagram">α &lt; -30     → Blackout (Embedding zu weit von allem → Rauschen)
α ≈ -4..-1  → Reines CLIP-L (T5-Einfluss ausgelöscht)
α ≈ 0..1    → Normaler Mix beider Encoder
α ≈ 2..7    → T5-dominant, beginnt "seltsam" zu werden
α ≈ 15..35  → Sweet Spot: Surreal, aber noch bildlich kohärent
α > 75      → Blackout (zu weit extrapoliert → numerischer Overflow)</pre>
        <p>{{ currentLanguage === 'de'
          ? 'Der Sweet Spot bei 15\u201335 entsteht, weil: Genug Struktur \u00fcberlebt, um ein erkennbares Bild zu produzieren. Genug Verzerrung da ist, um unerwartete Assoziationen zu erzeugen. Und die T5-Tokens 78\u2013512 als Stabilisator wirken.'
          : 'The sweet spot at 15\u201335 exists because: enough structure survives to produce a recognizable image, enough distortion exists to create unexpected associations, and T5 tokens 78\u2013512 act as a stabilizer.' }}</p>

        <!-- Section 6: Analogy -->
        <h4>{{ currentLanguage === 'de' ? 'Analogie' : 'Analogy' }}</h4>
        <p>{{ currentLanguage === 'de'
          ? 'Stell dir vor, du bittest zwei K\u00fcnstler, "ein Haus am See" zu malen: CLIP-L malt ein fotografisch-realistisches Bild. T5 malt ein Bild, das die Bedeutung von "Haus am See" einf\u00e4ngt \u2014 Ruhe, Wasser, Schutz.'
          : 'Imagine you ask two artists to paint "a house by a lake": CLIP-L paints a photographically realistic image. T5 paints an image that captures the meaning of "house by a lake" \u2014 tranquility, water, shelter.' }}</p>
        <p>{{ currentLanguage === 'de'
          ? 'Bei \u03b1=0 siehst du CLIP-Ls Bild. Bei \u03b1=1 siehst du T5s Bild. Bei \u03b1=20 extrapolierst du: "Wenn der Unterschied zwischen beiden SO ist, wie s\u00e4he es aus, wenn man diesen Unterschied 20\u00d7 verst\u00e4rkt?" \u2014 und bekommst etwas, das keiner der beiden K\u00fcnstler je gemalt h\u00e4tte.'
          : 'At \u03b1=0 you see CLIP-L\'s painting. At \u03b1=1 you see T5\'s painting. At \u03b1=20 you extrapolate: "If the difference between both is THIS, what would it look like if you amplified that difference 20\u00d7?" \u2014 and you get something neither artist would ever have painted.' }}</p>
      </div>
    </div>

    <!-- Attention Cartography -->
    <div class="experiment-card attention-cartography">
      <h3>Attention Cartography</h3>
      <div class="experiment-what">
        <strong>{{ currentLanguage === 'de' ? 'Was passiert hier?' : 'What happens here?' }}</strong>
        <p>{{ currentLanguage === 'de'
          ? 'Das Modell liest den Prompt nicht wie eine Bauanleitung ab. Stattdessen verteilt ein Mechanismus namens "Attention" den Einfluss jedes Wortes auf verschiedene Bildregionen. Dieses Tool macht diese Verteilung sichtbar: Klicke auf ein Wort und eine Heatmap zeigt, welche Bildregionen dieses Wort am st\u00e4rksten beeinflusst hat.'
          : 'The model does not read the prompt like a set of instructions. Instead, a mechanism called "attention" distributes the influence of each word across different image regions. This tool makes that distribution visible: click on a word and a heatmap shows which image regions that word influenced most.' }}</p>
      </div>
      <div class="experiment-why">
        <strong>{{ currentLanguage === 'de' ? 'Warum ist das aufschlussreich?' : 'Why is this revealing?' }}</strong>
        <p>{{ currentLanguage === 'de'
          ? 'Ein "Haus" in einer Bauernhof-Szene beeinflusst nicht nur die Haus-Region, sondern auch Tiere und Felder \u2014 das Modell versteht die Szene als Ganzes. Die Heatmaps sind absichtlich nicht scharf begrenzt: Das zeigt, dass das Modell Konzepte kontextuell verarbeitet, nicht isoliert.'
          : 'A "house" in a farm scene influences not just the house region, but also animals and fields \u2014 the model understands the scene as a whole. The heatmaps are intentionally not sharp-edged: this shows that the model processes concepts contextually, not in isolation.' }}</p>
      </div>
      <div class="experiment-example">
        <strong>{{ currentLanguage === 'de' ? 'Zwei unabh\u00e4ngige Achsen:' : 'Two independent axes:' }}</strong>
        {{ currentLanguage === 'de'
          ? 'Entrauschungsschritt (WANN: fr\u00fch = grobe Layoutplanung, sp\u00e4t = Detailzuordnung) und Netzwerktiefe (WO im Transformer: flach = Komposition, mittel = Semantik, tief = Feinabstimmung). Systematisch verschiedene Kombinationen erkunden!'
          : 'Denoising step (WHEN: early = rough layout planning, late = detail assignment) and network depth (WHERE in the transformer: shallow = composition, middle = semantics, deep = fine-tuning). Systematically explore different combinations!' }}
      </div>

      <button class="deep-dive-toggle" @click="showAttentionMath = !showAttentionMath">
        {{ currentLanguage === 'de' ? '\ud83d\udcd0 Technische Details' : '\ud83d\udcd0 Technical Details' }}
        <span class="toggle-arrow">{{ showAttentionMath ? '\u25b2' : '\u25bc' }}</span>
      </button>

      <div v-if="showAttentionMath" class="deep-dive-content">
        <h4>{{ currentLanguage === 'de' ? 'MMDiT Joint Attention' : 'MMDiT Joint Attention' }}</h4>
        <p>{{ currentLanguage === 'de'
          ? 'SD3.5 verwendet einen MMDiT (Multimodal Diffusion Transformer) mit Joint Attention: Bild- und Text-Tokens bearbeiten sich gegenseitig in 24 Transformer-Bl\u00f6cken. Wir ersetzen den Standard-SDPA-Prozessor durch einen manuellen Softmax(QK^T/\u221ad)-Prozessor an 3 ausgew\u00e4hlten Bl\u00f6cken, um die Text\u2192Bild-Attention-Submatrix zu extrahieren.'
          : 'SD3.5 uses an MMDiT (Multimodal Diffusion Transformer) with joint attention: image and text tokens attend to each other across 24 transformer blocks. We replace the default SDPA processor with a manual softmax(QK^T/\u221ad) processor at 3 selected blocks to extract the text\u2192image attention submatrix.' }}</p>

        <h4>{{ currentLanguage === 'de' ? 'Aufl\u00f6sung und Tokenisierung' : 'Resolution and Tokenization' }}</h4>
        <p>{{ currentLanguage === 'de'
          ? 'Die Attention-Maps haben 64\u00d764 Aufl\u00f6sung (Patch-Grid des DiT) und werden per bilinearer Interpolation auf die Bildaufl\u00f6sung (1024\u00d71024) hochskaliert. Die Tokenisierung nutzt CLIP-L BPE \u2014 Subwort-Tokens werden automatisch zu ganzen W\u00f6rtern zusammengefasst, damit die Darstellung intuitiv bleibt.'
          : 'Attention maps are 64\u00d764 resolution (DiT patch grid), upscaled to image resolution (1024\u00d71024) via bilinear interpolation. Tokenization uses CLIP-L BPE \u2014 subword tokens are automatically combined into whole words for intuitive display.' }}</p>
      </div>
    </div>

    <!-- Feature Probing -->
    <div class="experiment-card feature-probing">
      <h3>Feature Probing</h3>
      <div class="experiment-what">
        <strong>{{ currentLanguage === 'de' ? 'Was passiert hier?' : 'What happens here?' }}</strong>
        <p>{{ currentLanguage === 'de'
          ? 'Vergleiche zwei Prompts (z.B. "rotes Haus" vs. "blaues Haus") und finde heraus, welche Embedding-Dimensionen den semantischen Unterschied kodieren. Ein Balkendiagramm zeigt die Dimensionen sortiert nach Differenzgr\u00f6\u00dfe. Dann kannst du gezielt einzelne Dimensionen von Prompt B in Prompt A \u00fcbertragen \u2014 mit dem gleichen Seed, f\u00fcr einen fairen Vergleich.'
          : 'Compare two prompts (e.g. "red house" vs. "blue house") and discover which embedding dimensions encode the semantic difference. A bar chart shows dimensions sorted by difference magnitude. Then you can selectively transfer individual dimensions from prompt B into prompt A \u2014 with the same seed, for a fair comparison.' }}</p>
      </div>
      <div class="experiment-why">
        <strong>{{ currentLanguage === 'de' ? 'Warum ist das aufschlussreich?' : 'Why is this revealing?' }}</strong>
        <p>{{ currentLanguage === 'de'
          ? 'Niemand wei\u00df, was in Dimension 742 "gespeichert" ist. Durch die gezielte \u00dcbertragung einzelner Dimensionen wird sichtbar, was sie kodieren \u2014 Farbe? Form? Abstrakte Konzepte? Aber Vorsicht: Embeddings sind verteilt \u2014 oft braucht es mehrere Dimensionen zusammen, um eine sichtbare \u00c4nderung zu bewirken.'
          : 'Nobody knows what\'s "stored" in dimension 742. By selectively transferring individual dimensions, you can see what they encode \u2014 color? Shape? Abstract concepts? But note: embeddings are distributed \u2014 often multiple dimensions together are needed to produce a visible change.' }}</p>
      </div>
      <div class="experiment-example">
        <strong>{{ currentLanguage === 'de' ? 'Encoder w\u00e4hlbar:' : 'Encoder selectable:' }}</strong>
        {{ currentLanguage === 'de'
          ? 'CLIP-L (768 Dimensionen, visuell trainiert), CLIP-G (1280 Dim., visuell-semantisch) oder T5-XXL (4096 Dim., rein sprachlich). Jeder Encoder kodiert andere Aspekte \u2014 die gleiche Dimension kann in verschiedenen Encodern v\u00f6llig unterschiedliche Semantik tragen.'
          : 'CLIP-L (768 dimensions, visually trained), CLIP-G (1280 dims, visual-semantic) or T5-XXL (4096 dims, purely linguistic). Each encoder encodes different aspects \u2014 the same dimension can carry completely different semantics in different encoders.' }}
      </div>

      <button class="deep-dive-toggle" @click="showProbingMath = !showProbingMath">
        {{ currentLanguage === 'de' ? '\ud83d\udcd0 Technische Details' : '\ud83d\udcd0 Technical Details' }}
        <span class="toggle-arrow">{{ showProbingMath ? '\u25b2' : '\u25bc' }}</span>
      </button>

      <div v-if="showProbingMath" class="deep-dive-content">
        <h4>{{ currentLanguage === 'de' ? 'Drei Text-Encoder' : 'Three Text Encoders' }}</h4>
        <p>{{ currentLanguage === 'de'
          ? 'SD3.5 nutzt drei parallele Text-Encoder: CLIP-L (768d, kontrastiv auf Bild-Text-Paaren trainiert), CLIP-G (1280d, visuell-semantisch, OpenCLIP ViT-bigG) und T5-XXL (4096d, rein sprachlich). Du kannst jeden einzeln proben oder alle zusammen.'
          : 'SD3.5 uses three parallel text encoders: CLIP-L (768d, contrastively trained on image-text pairs), CLIP-G (1280d, visual-semantic, OpenCLIP ViT-bigG) and T5-XXL (4096d, purely linguistic). You can probe each individually or all together.' }}</p>

        <h4>{{ currentLanguage === 'de' ? 'Differenz-Berechnung' : 'Difference Computation' }}</h4>
        <pre class="math-diagram">diff[d] = mean(abs(B[t,d] - A[t,d]), dim=tokens)</pre>
        <p>{{ currentLanguage === 'de'
          ? 'Die Differenz wird als mittlere absolute Abweichung \u00fcber alle Token-Positionen berechnet. Die \u00dcbertragung ersetzt die ausgew\u00e4hlten Dimensionen in ALLEN Token-Positionen gleichzeitig \u2014 nicht nur an einer Stelle.'
          : 'The difference is computed as mean absolute deviation across all token positions. The transfer replaces selected dimensions across ALL token positions simultaneously \u2014 not just at one position.' }}</p>
      </div>
    </div>

    <!-- Concept Algebra -->
    <div class="experiment-card concept-algebra">
      <h3>Concept Algebra</h3>
      <div class="experiment-what">
        <strong>{{ currentLanguage === 'de' ? 'Was passiert hier?' : 'What happens here?' }}</strong>
        <p>{{ currentLanguage === 'de'
          ? 'Vektor-Arithmetik auf Bild-Embeddings: A \u2212 B + C = ? Inspiriert von der ber\u00fchmten Word2Vec-Analogie (K\u00f6nig \u2212 Mann + Frau \u2248 K\u00f6nigin), aber auf ganze Prompt-Embeddings und Bildgenerierung \u00fcbertragen. Drei Prompts werden kodiert und algebraisch kombiniert.'
          : 'Vector arithmetic on image embeddings: A \u2212 B + C = ? Inspired by the famous word2vec analogy (King \u2212 Man + Woman \u2248 Queen), but applied to entire prompt embeddings and image generation. Three prompts are encoded and algebraically combined.' }}</p>
      </div>
      <div class="experiment-why">
        <strong>{{ currentLanguage === 'de' ? 'Warum ist das anders als ein Negativ-Prompt?' : 'Why is this different from a negative prompt?' }}</strong>
        <p>{{ currentLanguage === 'de'
          ? 'Fundamental anders! Ein Negativ-Prompt steuert den Entrauschungsprozess bei JEDEM der 25 Schritte weg von B \u2014 das Modell entscheidet schrittweise, wie es "nicht B" interpretiert. Concept Algebra dagegen berechnet einen neuen Vektor VOR der Bildgenerierung: Die Subtraktion passiert im Embedding-Raum, nicht im Diffusionsprozess. Eine chirurgische Operation im Bedeutungsraum statt einer schrittweisen Vermeidungsstrategie.'
          : 'Fundamentally different! A negative prompt steers the denoising process away from B at EVERY one of the 25 steps \u2014 the model decides step by step how to interpret "not B". Concept Algebra instead computes a new vector BEFORE image generation: the subtraction happens in embedding space, not in the diffusion process. A surgical operation in meaning-space rather than a step-by-step avoidance strategy.' }}</p>
      </div>
      <div class="experiment-example">
        <strong>{{ currentLanguage === 'de' ? 'Beispiel:' : 'Example:' }}</strong>
        {{ currentLanguage === 'de'
          ? '"Sonnenuntergang am Strand" \u2212 "Strand" + "Berge" \u2248 "Sonnenuntergang \u00fcber Bergen". Skalierungsregler steuern die Intensit\u00e4t der Subtraktion und Addition (0\u20133). Die L2-Distanz zeigt, wie weit sich das Ergebnis vom Original entfernt hat.'
          : '"Sunset at the beach" \u2212 "Beach" + "Mountains" \u2248 "Sunset over mountains". Scale sliders control the intensity of subtraction and addition (0\u20133). The L2 distance shows how far the result has moved from the original.' }}
      </div>

      <button class="deep-dive-toggle" @click="showAlgebraMath = !showAlgebraMath">
        {{ currentLanguage === 'de' ? '\ud83d\udcd0 Die Mathematik im Detail' : '\ud83d\udcd0 The Mathematics in Detail' }}
        <span class="toggle-arrow">{{ showAlgebraMath ? '\u25b2' : '\u25bc' }}</span>
      </button>

      <div v-if="showAlgebraMath" class="deep-dive-content">
        <h4>{{ currentLanguage === 'de' ? 'Die Formel' : 'The Formula' }}</h4>
        <pre class="math-diagram">Ergebnis = A − Skalierung₁ × B + Skalierung₂ × C</pre>
        <p>{{ currentLanguage === 'de'
          ? 'Bei Skalierung 1.0 wird B vollst\u00e4ndig subtrahiert und C vollst\u00e4ndig addiert. Bei 0.5 nur zur H\u00e4lfte. Werte \u00fcber 1.0 verst\u00e4rken den Effekt. Die Operation wird auf den gew\u00e4hlten Encoder-Embeddings durchgef\u00fchrt: CLIP-L (768d), CLIP-G (1280d), T5-XXL (4096d) oder alle zusammen (589 Tokens \u00d7 4096d). Dieselbe Operation wird auch auf die Pooled Embeddings (2048d) angewendet.'
          : 'At scale 1.0, B is fully subtracted and C fully added. At 0.5, only half. Values above 1.0 amplify the effect. The operation is performed on the selected encoder embeddings: CLIP-L (768d), CLIP-G (1280d), T5-XXL (4096d), or all combined (589 tokens \u00d7 4096d). The same operation is also applied to pooled embeddings (2048d).' }}</p>

        <h4>{{ currentLanguage === 'de' ? 'Ist die Operation kommutativ?' : 'Is the operation commutative?' }}</h4>
        <p>{{ currentLanguage === 'de'
          ? 'Nein. Die Subtraktion von B und die Addition von C finden relativ zum Vektor A statt. "K\u00f6nig \u2212 Mann" entfernt die "m\u00e4nnlichen" Richtungen aus dem K\u00f6nig-Vektor, "+ Frau" erg\u00e4nzt die "weiblichen" Richtungen \u2014 das Ergebnis liegt nahe "K\u00f6nigin". Dass das funktioniert, zeigt: Semantische Beziehungen sind im Vektorraum als konsistente lineare Richtungen kodiert.'
          : 'No. Subtraction of B and addition of C happen relative to vector A. "King \u2212 Man" removes the "male" directions from the King vector, "+ Woman" adds the "female" directions \u2014 the result lands near "Queen". That this works shows: semantic relationships are encoded as consistent linear directions in vector space.' }}</p>
      </div>
    </div>

    <!-- Denoising Archaeology -->
    <div class="experiment-card denoising-archaeology">
      <h3>Denoising Archaeology</h3>
      <div class="experiment-what">
        <strong>{{ currentLanguage === 'de' ? 'Was passiert hier?' : 'What happens here?' }}</strong>
        <p>{{ currentLanguage === 'de'
          ? 'Jeder der 25 Entrauschungsschritte wird als Bild sichtbar gemacht. Ein Filmstreifen zeigt die komplette Entstehung, ein Timeline-Regler erm\u00f6glicht das Durchbl\u00e4ttern. Diffusionsmodelle arbeiten nicht links-nach-rechts wie ein Zeichner \u2014 sie arbeiten \u00fcberall gleichzeitig, von groben Strukturen zu feinen Details.'
          : 'Every one of the 25 denoising steps is made visible as an image. A filmstrip shows the complete creation process, a timeline slider allows browsing. Diffusion models don\'t work left-to-right like a drawer \u2014 they work everywhere simultaneously, from rough structures to fine details.' }}</p>
      </div>
      <div class="experiment-why">
        <strong>{{ currentLanguage === 'de' ? 'Was verraten die drei Phasen?' : 'What do the three phases reveal?' }}</strong>
        <p>{{ currentLanguage === 'de'
          ? 'Fr\u00fche Schritte (1\u20138): Globale Komposition \u2014 Grundstruktur, Farbverteilung, Layoutplanung. Mittlere Schritte (9\u201317): Semantische Emergenz \u2014 Objekte werden erkennbar, Formen kristallisieren sich heraus. Sp\u00e4te Schritte (18\u201325): Detail-Verfeinerung \u2014 Texturen, Kanten, feine Muster. Das Modell "plant" zuerst global und verfeinert dann lokal.'
          : 'Early steps (1\u20138): Global composition \u2014 basic structure, color distribution, layout planning. Middle steps (9\u201317): Semantic emergence \u2014 objects become recognizable, shapes crystallize. Late steps (18\u201325): Detail refinement \u2014 textures, edges, fine patterns. The model first "plans" globally, then refines locally.' }}</p>
      </div>
      <div class="experiment-example">
        <strong>{{ currentLanguage === 'de' ? '\u00dcberraschend:' : 'Surprising:' }}</strong>
        {{ currentLanguage === 'de'
          ? 'Der allererste Schritt zeigt keine feinen Pixel, sondern farbige Cluster. Das liegt daran, dass das Rauschen im Latent-Raum (128\u00d7128 bei 16 Kan\u00e4len) erzeugt wird, nicht im Pixel-Raum. Der VAE \u00fcbersetzt jeden Latent-Pixel in einen ~8\u00d78-Pixel-Patch \u2014 selbst pures Gau\u00dfsches Rauschen wird dadurch zu zusammenh\u00e4ngenden Farbclustern.'
          : 'The very first step shows not fine pixels, but colorful clusters. This is because the noise is generated in latent space (128\u00d7128 at 16 channels), not in pixel space. The VAE translates each latent pixel into an ~8\u00d78 pixel patch \u2014 even pure Gaussian noise becomes coherent color clusters.' }}
      </div>

      <button class="deep-dive-toggle" @click="showArchaeologyMath = !showArchaeologyMath">
        {{ currentLanguage === 'de' ? '\ud83d\udcd0 Technische Details' : '\ud83d\udcd0 Technical Details' }}
        <span class="toggle-arrow">{{ showArchaeologyMath ? '\u25b2' : '\u25bc' }}</span>
      </button>

      <div v-if="showArchaeologyMath" class="deep-dive-content">
        <h4>{{ currentLanguage === 'de' ? 'Rectified Flow' : 'Rectified Flow' }}</h4>
        <p>{{ currentLanguage === 'de'
          ? 'SD3.5 Large verwendet Rectified Flow als Scheduler mit 25 Standardschritten. Bei jedem Schritt werden die aktuellen Latent-Vektoren durch den VAE dekodiert (1024\u00d71024 JPEG). Der VAE (Variational Autoencoder) \u00fcbersetzt den mathematischen Latent-Raum in Pixel.'
          : 'SD3.5 Large uses Rectified Flow as scheduler with 25 default steps. At each step, the current latent vectors are decoded through the VAE (1024\u00d71024 JPEG). The VAE (Variational Autoencoder) translates the mathematical latent space into pixels.' }}</p>

        <h4>{{ currentLanguage === 'de' ? 'Latent-Raum' : 'Latent Space' }}</h4>
        <p>{{ currentLanguage === 'de'
          ? 'Die Latent-Darstellung ist 128\u00d7128 bei 16 Kan\u00e4len \u2014 jeder Latent-Pixel entspricht einem ~8\u00d78-Pixel-Patch im Bild. Das Modell "denkt" nie in einzelnen Pixeln, sondern immer in diesem komprimierten Raum. Deshalb zeigt schon der erste Schritt koh\u00e4rente Farbfl\u00e4chen statt feines Pixelrauschen.'
          : 'The latent representation is 128\u00d7128 at 16 channels \u2014 each latent pixel corresponds to an ~8\u00d78 pixel patch in the image. The model never "thinks" in individual pixels, but always in this compressed space. This is why even the first step shows coherent color patches instead of fine pixel noise.' }}</p>
      </div>
    </div>

  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{ currentLanguage: string }>()

const showHallucinatorMath = ref(false)
const showAttentionMath = ref(false)
const showProbingMath = ref(false)
const showAlgebraMath = ref(false)
const showArchaeologyMath = ref(false)
</script>
