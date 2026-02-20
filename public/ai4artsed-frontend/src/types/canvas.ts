/**
 * Canvas Workflow Types for AI4ArtsEd DevServer
 *
 * Defines types for the visual canvas workflow builder.
 * Supports parallel fan-out workflows with feedback loops.
 *
 * Session 129: Phase 1 Implementation
 */
import type { LocalizedString } from '@/i18n'

// ============================================================================
// NODE TYPES
// ============================================================================

/**
 * Available stage/node types in the canvas
 *
 * NOTE: Safety is NOT a user-visible node!
 * - Stage 1 Safety: Automatic in /pipeline/interception
 * - Stage 3 Safety: Automatic per output-config
 * DevServer handles all safety transparently.
 *
 * Session 134: Added evaluation/fork/display/loop nodes for decision logic
 */
export type StageType =
  | 'input'
  | 'image_input' // Session 152: Image upload as source
  | 'random_prompt' // Session 140: LLM-based random prompt generator with presets
  | 'interception'
  | 'translation'
  | 'model_adaption' // Session 145: Model-specific prompt adaption (CLIP/T5 encoder)
  | 'generation'
  | 'collector'
  // Session 134 Refactored: Unified evaluation node with optional branching
  | 'evaluation'
  // Session 152: Vision-LLM image analysis
  | 'image_evaluation'
  // Display node (visualization)
  | 'display'
  // Session 147: Multi-input comparison evaluator
  | 'comparison_evaluator'
  // Session 149: Seed control node for reproducible generation
  | 'seed'
  // Session 151: Parameter nodes for generation control
  | 'resolution'
  | 'quality'

// ============================================================================
// MODEL ADAPTION TYPES (Session 145)
// ============================================================================

/** Model Adaption Preset Types - adapts prompt for specific media models */
export type ModelAdaptionPreset =
  | 'none'      // No adaption (pass-through)
  | 'sd35'      // Stable Diffusion 3.5 (CLIP-style keywords)
  | 'flux'      // Flux (T5-style natural language)
  | 'video'     // Video models (scenic descriptions)
  | 'audio'     // Audio/Music models (auditive descriptions)

// ============================================================================
// INTERCEPTION PRESET TYPES (Session 146)
// ============================================================================

/** Interception Preset IDs - maps to Stage2 interception configs */
export type InterceptionPreset =
  | 'user_defined'              // Default - eigene Anweisung
  | 'analog_photography_1870s'  // Daguerreotype
  | 'analog_photography_1970s'  // Analog Photography
  | 'analogue_copy'             // Analogue Copy
  | 'bauhaus'                   // Bauhaus
  | 'clichefilter_v2'           // De-Kitsch (note: no accent in ID)
  | 'confucianliterati'         // Literati
  | 'cooked_negatives'          // Cooked Negatives
  | 'digital_photography'       // Digital Photography
  | 'forceful'                  // Forceful
  | 'hunkydoryharmonizer'       // Sweetener
  | 'jugendsprache'             // Slang
  | 'mad_world'                 // mad world
  | 'one_world'                 // One World
  | 'overdrive'                 // Amplifier
  | 'p5js_simplifier'           // Listifier
  | 'tonejs_composer'           // Music Composer
  | 'piglatin'                  // Word Game
  | 'planetarizer'              // Planetarizer
  | 'renaissance'               // Renaissance
  | 'sensitive'                 // Sensitive
  | 'stillepost'                // Telephone
  | 'technicaldrawing'          // Technical
  | 'tellastory'                // Your Story
  | 'theopposite'               // On the Contrary!

/** Interception Preset Config with labels */
export interface InterceptionPresetConfig {
  label: LocalizedString
}

/** Interception Presets - labels only, context loaded from backend on selection */
export const INTERCEPTION_PRESETS: Record<InterceptionPreset, InterceptionPresetConfig> = {
  user_defined: { label: { en: 'Your Call!', de: 'Du bestimmst!', tr: 'Sen Karar Ver!', ko: '자유 선택!' } },
  analog_photography_1870s: { label: { en: 'Daguerreotype', de: 'Daguerreotypie', tr: 'Dagerotipi', ko: '다게레오타입' } },
  analog_photography_1970s: { label: { en: 'Analog Photography', de: 'Analogfotografie', tr: 'Analog Fotoğrafçılık', ko: '아날로그 사진' } },
  analogue_copy: { label: { en: 'Analogue Copy', de: 'Analoge Kopie', tr: 'Analog Kopya', ko: '아날로그 복사' } },
  bauhaus: { label: { en: 'Bauhaus', de: 'Bauhaus', tr: 'Bauhaus', ko: '바우하우스' } },
  clichefilter_v2: { label: { en: 'De-Kitsch', de: 'Entkitscher', tr: 'Kiç Filtresi', ko: '키치 제거' } },
  confucianliterati: { label: { en: 'Literati', de: 'Literati', tr: 'Literati', ko: '문인화' } },
  cooked_negatives: { label: { en: 'Cooked Negatives', de: 'Gekochte Filmnegative', tr: 'Pişmiş Negatifler', ko: '가공된 네거티브' } },
  digital_photography: { label: { en: 'Digital Photography', de: 'Digitalfotografie', tr: 'Dijital Fotoğrafçılık', ko: '디지털 사진' } },
  forceful: { label: { en: 'Forceful', de: 'kraftvoll', tr: 'Güçlü', ko: '강렬한' } },
  hunkydoryharmonizer: { label: { en: 'Sweetener', de: 'Verniedlicher', tr: 'Tatlandırıcı', ko: '감미료' } },
  jugendsprache: { label: { en: 'Slang', de: 'Jugendslang', tr: 'Gençlik Argosu', ko: '청소년 은어' } },
  mad_world: { label: { en: 'mad world', de: 'verrückt', tr: 'çılgın dünya', ko: '미친 세상' } },
  one_world: { label: { en: 'One World', de: 'Eine Welt', tr: 'Tek Dünya', ko: '하나의 세계' } },
  overdrive: { label: { en: 'Amplifier', de: 'Übertreiber!', tr: 'Abartmacı!', ko: '증폭기!' } },
  p5js_simplifier: { label: { en: 'Listifier', de: 'Auflister', tr: 'Listeleyici', ko: '목록화' } },
  tonejs_composer: { label: { en: 'Music Composer', de: 'Musikkomponist', tr: 'Müzik Bestecisi', ko: '음악 작곡가' } },
  piglatin: { label: { en: 'Word Game', de: 'Sprachspiel', tr: 'Kelime Oyunu', ko: '말놀이' } },
  planetarizer: { label: { en: 'Planetarizer', de: 'Planetarisierer', tr: 'Gezegenleştirici', ko: '행성화' } },
  renaissance: { label: { en: 'Renaissance', de: 'Renaissance', tr: 'Rönesans', ko: '르네상스' } },
  sensitive: { label: { en: 'Sensitive', de: 'sensibel', tr: 'Duyarlı', ko: '섬세한' } },
  stillepost: { label: { en: 'Telephone', de: 'Stille Post', tr: 'Kulaktan Kulağa', ko: '전화 게임' } },
  technicaldrawing: { label: { en: 'Technical', de: 'Technisch', tr: 'Teknik', ko: '기술적' } },
  tellastory: { label: { en: 'Your Story', de: 'Deine Geschichte', tr: 'Senin Hikayen', ko: '너의 이야기' } },
  theopposite: { label: { en: 'On the Contrary!', de: 'Im Gegenteil!', tr: 'Tam Tersine!', ko: '정반대로!' } }
}

// ============================================================================
// IMAGE EVALUATION PRESET TYPES (Session 152)
// ============================================================================

/** Image Evaluation Preset Types - pedagogical analysis frameworks */
export type ImageEvaluationPreset =
  | 'bildwissenschaftlich'  // Panofsky - Art-historical analysis
  | 'bildungstheoretisch'   // Jörissen/Marotzki - Educational theory
  | 'ethisch'               // Ethical analysis
  | 'kritisch'              // Critical/Decolonial analysis
  | 'custom'                // Custom prompt

/** Image Evaluation Preset Config with labels */
export interface ImageEvaluationPresetConfig {
  label: LocalizedString
  description: LocalizedString
}

/** Image Evaluation Presets - labels only, prompts loaded from backend config.py */
export const IMAGE_EVALUATION_PRESETS: Record<ImageEvaluationPreset, ImageEvaluationPresetConfig> = {
  bildwissenschaftlich: {
    label: { en: 'Art Historical (Panofsky)', de: 'Kunsthistorisch (Panofsky)', tr: 'Sanat Tarihi (Panofsky)', ko: '미술사적 (파노프스키)' },
    description: { en: '4-stage iconological method', de: '4-stufige ikonologische Methode', tr: '4 aşamalı ikonolojik yöntem', ko: '4단계 도상학적 방법' }
  },
  bildungstheoretisch: {
    label: { en: 'Educational Theory', de: 'Bildungstheoretisch', tr: 'Eğitim Teorisi', ko: '교육 이론' },
    description: { en: 'Jörissen/Marotzki framework', de: 'Jörissen/Marotzki Framework', tr: 'Jörissen/Marotzki çerçevesi', ko: 'Jörissen/Marotzki 프레임워크' }
  },
  ethisch: {
    label: { en: 'Ethical', de: 'Ethisch', tr: 'Etik', ko: '윤리적' },
    description: { en: 'Ethical analysis', de: 'Ethische Analyse', tr: 'Etik analiz', ko: '윤리적 분석' }
  },
  kritisch: {
    label: { en: 'Critical/Decolonial', de: 'Kritisch/Dekolonial', tr: 'Eleştirel/Dekolonyal', ko: '비판적/탈식민주의' },
    description: { en: 'Critical media studies', de: 'Kritische Medienwissenschaft', tr: 'Eleştirel medya çalışmaları', ko: '비판적 미디어 연구' }
  },
  custom: {
    label: { en: 'Custom', de: 'Eigene Anweisung', tr: 'Özel Talimat', ko: '사용자 정의' },
    description: { en: 'Define your own analysis prompt', de: 'Eigenen Analyse-Prompt definieren', tr: 'Kendi analiz komutunuzu tanımlayın', ko: '나만의 분석 프롬프트 정의' }
  }
}

// ============================================================================
// RANDOM PROMPT TYPES
// ============================================================================

/** Random Prompt Preset Types */
export type RandomPromptPreset =
  | 'clean_image'  // Szenische Beschreibung (medienneutral)
  | 'photo'        // Fotografische Prompts mit Film-Typ
  | 'artform'      // Kunstform-Transformation
  | 'instruction'  // Kreative Transformation
  | 'language'     // Sprach-Vorschlag

/** Film types for photo preset */
export type PhotoFilmType =
  | 'random'
  | 'Kodachrome' | 'Ektachrome'
  | 'Portra 400' | 'Portra 800' | 'Ektar 100'
  | 'Fuji Pro 400H' | 'Fuji Superia' | 'CineStill 800T'
  | 'Ilford HP5' | 'Ilford Delta 400' | 'Ilford FP4' | 'Ilford Pan F' | 'Ilford XP2'
  | 'Tri-X 400'

/** Node type definition for the palette */
export interface NodeTypeDefinition {
  id: string
  type: StageType
  label: LocalizedString
  description: LocalizedString
  color: string
  icon: string
  /** Whether this node type allows multiple instances */
  allowMultiple: boolean
  /** Whether this node is mandatory in workflows */
  mandatory: boolean
}

/**
 * Predefined node types for the canvas
 *
 * Module Types:
 * - Input: Text input source
 * - Interception: LLM selection (primary!) + interception config (optional override)
 * - Translation: Translation prompt + LLM selection
 * - Generation: Output configs (sd35, qwen, flux2, etc.)
 * - Collector: Fan-in collector for parallel outputs (Media Collector)
 *
 * IMPORTANT: Safety is NOT a node!
 * DevServer handles Stage 1 + Stage 3 safety automatically.
 */
export const NODE_TYPE_DEFINITIONS: NodeTypeDefinition[] = [
  {
    id: 'input',
    type: 'input',
    label: { en: 'Input Prompt', de: 'Eingabe-Prompt', tr: 'Giriş Komutu', ko: '입력 프롬프트' },
    description: { en: 'Text input source', de: 'Text-Eingabequelle', tr: 'Metin giriş kaynağı', ko: '텍스트 입력 소스' },
    color: '#3b82f6', // blue
    icon: 'edit_square_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg',
    allowMultiple: false,
    mandatory: true
  },
  // Session 152: Image Input Node
  {
    id: 'image_input',
    type: 'image_input',
    label: { en: 'Image Input', de: 'Bild-Eingabe', tr: 'Görsel Girişi', ko: '이미지 입력' },
    description: { en: 'Upload image as source', de: 'Bild als Quelle hochladen', tr: 'Kaynak olarak görsel yükle', ko: '소스로 이미지 업로드' },
    color: '#0ea5e9', // sky blue
    icon: 'add_photo_alternate_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg',
    allowMultiple: true,
    mandatory: false
  },
  // Session 140: Random Prompt Node with presets
  {
    id: 'random_prompt',
    type: 'random_prompt',
    label: { en: 'Random Prompt', de: 'Zufalls-Prompt', tr: 'Rastgele Komut', ko: '랜덤 프롬프트' },
    description: {
      en: 'Generate creative content via LLM with presets',
      de: 'Generiert kreative Inhalte via LLM mit Presets',
      tr: 'Ön ayarlarla LLM aracılığıyla yaratıcı içerik üret',
      ko: '프리셋으로 LLM을 통해 창의적 콘텐츠 생성'
    },
    color: '#ec4899', // pink
    icon: 'shuffle_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg',
    allowMultiple: true,
    mandatory: false
  },
  {
    id: 'interception',
    type: 'interception',
    label: { en: 'Interception', de: 'Interception', tr: 'Interception' },
    description: {
      en: 'Pedagogical transformation with LLM selection',
      de: 'Pädagogische Transformation mit LLM-Auswahl',
      tr: 'LLM seçimiyle pedagojik dönüşüm'
    },
    color: '#8b5cf6', // purple
    icon: 'cognition_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg',
    allowMultiple: true,
    mandatory: false
  },
  {
    id: 'translation',
    type: 'translation',
    label: { en: 'Translation', de: 'Übersetzung', tr: 'Çeviri' },
    description: {
      en: 'Language translation with custom prompt + LLM',
      de: 'Sprachübersetzung mit eigenem Prompt + LLM',
      tr: 'Özel komut + LLM ile dil çevirisi'
    },
    color: '#f59e0b', // amber
    icon: 'language_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg',
    allowMultiple: true,
    mandatory: false
  },
  // Session 145: Model Adaption Node - adapts prompt for specific media models
  {
    id: 'model_adaption',
    type: 'model_adaption',
    label: { en: 'Model Adaption', de: 'Modell-Adaption', tr: 'Model Adaptasyonu' },
    description: {
      en: 'Adapt prompt for media model (SD3.5, Flux, Video, Audio)',
      de: 'Prompt für Medienmodell anpassen (SD3.5, Flux, Video, Audio)',
      tr: 'Medya modeli için komutu uyarla (SD3.5, Flux, Video, Ses)'
    },
    color: '#14b8a6', // teal
    icon: 'tune_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg',
    allowMultiple: true,
    mandatory: false
  },
  {
    id: 'generation',
    type: 'generation',
    label: { en: 'Generation', de: 'Generierung', tr: 'Üretim' },
    description: {
      en: 'Media generation (image, audio, video)',
      de: 'Mediengenerierung (Bild, Audio, Video)',
      tr: 'Medya üretimi (görsel, ses, video)'
    },
    color: '#10b981', // emerald
    icon: 'brush_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg',
    allowMultiple: true,
    mandatory: true
  },
  {
    id: 'collector',
    type: 'collector',
    label: { en: 'Media Output', de: 'Medienausgabe', tr: 'Medya Çıktısı' },
    description: {
      en: 'Collects and displays outputs (media + text)',
      de: 'Sammelt und zeigt Ausgaben (Medien + Text)',
      tr: 'Çıktıları toplar ve gösterir (medya + metin)'
    },
    color: '#06b6d4', // cyan
    icon: 'gallery_thumbnail_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg',
    allowMultiple: false,
    mandatory: true
  },
  // Session 134 Refactored: Unified Evaluation Node (replaces 5 eval nodes + 2 fork nodes)
  {
    id: 'evaluation',
    type: 'evaluation',
    label: { en: 'Evaluation', de: 'Bewertung', tr: 'Değerlendirme' },
    description: {
      en: 'LLM-based evaluation with 3-way branching (pass/fail/commentary)',
      de: 'LLM-basierte Bewertung mit 3-Wege-Verzweigung (Pass/Fail/Kommentar)',
      tr: '3 yönlü dallanma ile LLM tabanlı değerlendirme (geçti/kaldı/yorum)'
    },
    color: '#f59e0b', // amber
    icon: 'checklist_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg',
    allowMultiple: true,
    mandatory: false
  },
  // Session 152: Image Evaluation Node (Vision-LLM analysis)
  {
    id: 'image_evaluation',
    type: 'image_evaluation',
    label: { en: 'Image Analysis', de: 'Bild-Analyse', tr: 'Görsel Analizi' },
    description: {
      en: 'Vision-LLM analysis of images',
      de: 'Vision-LLM Analyse von Bildern',
      tr: 'Görsellerin Vision-LLM analizi'
    },
    color: '#dc2626', // red
    icon: 'imagesmode_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg',
    allowMultiple: true,
    mandatory: false
  },
  // Session 135: Display Node (Terminal - no output)
  {
    id: 'display',
    type: 'display',
    label: { en: 'Preview', de: 'Vorschau', tr: 'Önizleme' },
    description: {
      en: 'Preview text or media inline (tap/observer, no output)',
      de: 'Vorschau von Text oder Medien inline (Tap/Observer, kein Output)',
      tr: 'Metin veya medyayı satır içi önizle (gözlemci, çıktı yok)'
    },
    color: '#10b981', // green
    icon: 'info_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg',
    allowMultiple: true,
    mandatory: false
  },
  // Session 147: Comparison Evaluator Node (Multi-input comparison)
  {
    id: 'comparison_evaluator',
    type: 'comparison_evaluator',
    label: { en: 'Comparison', de: 'Vergleich', tr: 'Karşılaştırma' },
    description: {
      en: 'Compare multiple text inputs with LLM analysis',
      de: 'Vergleiche mehrere Text-Inputs mit LLM-Analyse',
      tr: 'LLM analizi ile birden fazla metin girdisini karşılaştır'
    },
    color: '#f97316', // orange
    icon: 'analyze.svg',
    allowMultiple: true,
    mandatory: false
  },
  // Session 149: Seed Node for reproducible generation
  {
    id: 'seed',
    type: 'seed',
    label: { en: 'Seed', de: 'Seed', tr: 'Seed' },
    description: {
      en: 'Control seed for reproducible media generation',
      de: 'Seed für reproduzierbare Mediengenerierung',
      tr: 'Tekrarlanabilir medya üretimi için seed kontrolü'
    },
    color: '#6366f1', // indigo
    icon: 'potted_plant_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg',
    allowMultiple: true,
    mandatory: false
  },
  // Session 151: Resolution Node for width/height control
  {
    id: 'resolution',
    type: 'resolution',
    label: { en: 'Resolution', de: 'Auflösung', tr: 'Çözünürlük' },
    description: {
      en: 'Set width and height for image generation (ComfyUI only)',
      de: 'Breite und Höhe für Bildgenerierung (nur ComfyUI)',
      tr: 'Görsel üretimi için genişlik ve yükseklik ayarla (yalnızca ComfyUI)'
    },
    color: '#0ea5e9', // sky blue
    icon: 'display_settings_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg',
    allowMultiple: true,
    mandatory: false
  },
  // Session 151: Quality Node for steps/cfg control
  {
    id: 'quality',
    type: 'quality',
    label: { en: 'Quality', de: 'Qualität', tr: 'Kalite' },
    description: {
      en: 'Set steps and CFG for generation quality (ComfyUI only)',
      de: 'Steps und CFG für Generierungsqualität (nur ComfyUI)',
      tr: 'Üretim kalitesi için adım ve CFG ayarla (yalnızca ComfyUI)'
    },
    color: '#84cc16', // lime
    icon: 'display_settings_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg',
    allowMultiple: true,
    mandatory: false
  }
]

// ============================================================================
// CANVAS NODE
// ============================================================================

/** A node instance on the canvas */
export interface CanvasNode {
  /** Unique node ID */
  id: string
  /** Node type (stage) */
  type: StageType
  /** X position on canvas */
  x: number
  /** Y position on canvas */
  y: number
  /** Node-specific configuration overrides */
  config: Record<string, unknown>

  // === Generation node config ===
  /** Selected output config ID for generation nodes (e.g., 'sd35_large', 'flux2_schnell') */
  configId?: string

  // === Interception node config ===
  /** Selected interception preset (Session 146) */
  interceptionPreset?: InterceptionPreset
  /** Selected LLM model ID (e.g., 'gpt-4o-mini', 'claude-3-haiku') */
  llmModel?: string
  /** Context/system prompt for the LLM (pedagogical transformation instructions) */
  contextPrompt?: string

  // === Translation node config ===
  /** Translation prompt/instructions */
  translationPrompt?: string

  // === Input node config ===
  /** User's prompt text (input node) */
  promptText?: string

  // === Display properties ===
  /** Custom width (optional, for resizable nodes like Collector) */
  width?: number
  /** Custom height (optional, for resizable nodes like Collector) */
  height?: number

  // === Session 134 Refactored: Unified Evaluation node config ===
  /** Evaluation type (pre-fills prompt template) */
  evaluationType?: 'fairness' | 'creativity' | 'bias' | 'quality' | 'custom'
  /** Evaluation prompt/criteria description */
  evaluationPrompt?: string
  /** Output type for evaluation results (controls if score is requested) */
  outputType?: 'commentary' | 'score' | 'all'

  // === Feedback config (for Interception/Translation nodes) ===
  /** Maximum feedback iterations (default: 3) */
  maxFeedbackIterations?: number

  // === Display node config ===
  /** Display mode for visualization */
  displayMode?: 'popup' | 'inline' | 'toast'
  /** Display title */
  title?: string

  // === Random Prompt node config (Session 140) ===
  /** Selected preset (determines system prompt) */
  randomPromptPreset?: RandomPromptPreset
  /** LLM model for generation */
  randomPromptModel?: string
  /** Film type (only for 'photo' preset) */
  randomPromptFilmType?: PhotoFilmType

  // === Model Adaption node config (Session 145) ===
  /** Adaption preset (CLIP, T5, or none) */
  modelAdaptionPreset?: ModelAdaptionPreset

  // === Comparison Evaluator node config (Session 147) ===
  /** LLM model for comparison analysis */
  comparisonLlmModel?: string
  /** Evaluation criteria/goals for comparison */
  comparisonCriteria?: string

  // === Seed node config (Session 149) ===
  /** Seed mode: fixed value, random per execution, or increment for batch */
  seedMode?: 'fixed' | 'random' | 'increment'
  /** Fixed seed value (only used when seedMode is 'fixed') */
  seedValue?: number
  /** Base seed for increment mode (batch execution adds run_index) */
  seedBase?: number

  // === Resolution node config (Session 151) ===
  /** Image width in pixels */
  resolutionWidth?: number
  /** Image height in pixels */
  resolutionHeight?: number
  /** Resolution preset (square, portrait, landscape, custom) */
  resolutionPreset?: 'square_1024' | 'portrait_768x1344' | 'landscape_1344x768' | 'custom'

  // === Quality node config (Session 151) ===
  /** Number of inference steps */
  qualitySteps?: number
  /** CFG scale value */
  qualityCfg?: number

  // === Image Input node config (Session 152) ===
  /** Uploaded image data */
  imageData?: {
    image_id: string
    image_path: string
    preview_url: string
    original_size: [number, number]
    resized_size: [number, number]
  }

  // === Image Evaluation node config (Session 152) ===
  /** Vision model for image analysis (local Ollama only) */
  visionModel?: string
  /** Image evaluation preset (pedagogical framework) */
  imageEvaluationPreset?: 'bildwissenschaftlich' | 'bildungstheoretisch' | 'ethisch' | 'kritisch' | 'custom'
  /** Custom evaluation prompt (only if preset is 'custom') */
  imageEvaluationPrompt?: string
}

// ============================================================================
// CONNECTION
// ============================================================================

/** A connection between two nodes */
export interface CanvasConnection {
  /** Source node ID */
  sourceId: string
  /** Target node ID */
  targetId: string
  /** Session 134: Label for fork branches (e.g., 'true', 'false', 'approved', 'rejected') */
  label?: string
  /** Session 134: Active state for conditional execution (managed by execution engine) */
  active?: boolean
}

// ============================================================================
// WORKFLOW
// ============================================================================

/** Loop configuration for feedback workflows */
export interface LoopConfig {
  enabled: boolean
  maxIterations: number
  /** Node ID to collect feedback from */
  feedbackFrom?: string
  /** Node ID to feed back into */
  feedbackTo?: string
  /** Conditional termination expression (future) */
  condition?: string
}

/** Automation settings */
export interface AutomationConfig {
  /** Seed control: 'global' applies same seed to all generation nodes, 'per-node' allows individual seeds */
  seedControl: 'global' | 'per-node'
  /** Global seed value (when seedControl is 'global') */
  globalSeed?: number
  /** Whether to automatically apply LoRA automation */
  loraInjection: boolean
}

/** Complete canvas workflow definition */
export interface CanvasWorkflow {
  /** Workflow ID */
  id: string
  /** Workflow name */
  name: string
  /** Workflow description */
  description?: string
  /** Workflow type identifier */
  type: 'canvas_workflow'
  /** All nodes in the workflow */
  nodes: CanvasNode[]
  /** All connections between nodes */
  connections: CanvasConnection[]
  /** Loop/feedback configuration */
  loops?: LoopConfig
  /** Automation settings */
  automation?: AutomationConfig
  /** Creation timestamp */
  createdAt?: string
  /** Last modified timestamp */
  updatedAt?: string
}

// ============================================================================
// EXECUTION
// ============================================================================

/** Execution status for a node */
export type NodeExecutionStatus = 'pending' | 'running' | 'completed' | 'failed' | 'skipped'

/** Execution state for a single node */
export interface NodeExecutionState {
  nodeId: string
  status: NodeExecutionStatus
  output?: unknown
  error?: string
  startTime?: number
  endTime?: number
  durationMs?: number
}

/** Overall workflow execution state */
export interface WorkflowExecutionState {
  workflowId: string
  status: 'idle' | 'running' | 'completed' | 'failed' | 'interrupted'
  currentIteration: number
  totalIterations: number
  nodeStates: Map<string, NodeExecutionState>
  startTime?: number
  endTime?: number
}

// ============================================================================
// CONFIG SELECTION
// ============================================================================

/** Available LLM model for interception/translation nodes */
export interface LLMModelSummary {
  /** Model ID (e.g., 'gpt-4o-mini', 'claude-3-haiku') */
  id: string
  /** Display name */
  name: string
  /** Provider (openai, anthropic, google, local) */
  provider: string
  /** Model capabilities/description */
  description?: string
  /** Whether this is the default/recommended model */
  isDefault?: boolean
}

/** Output/generation config summary (for palette selection) */
export interface OutputConfigSummary {
  id: string
  name: LocalizedString
  description: LocalizedString
  icon: string
  color: string
  mediaType: 'image' | 'audio' | 'video' | 'music' | 'text'
  backend: string
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Get node type definition by type
 */
export function getNodeTypeDefinition(type: StageType): NodeTypeDefinition | undefined {
  return NODE_TYPE_DEFINITIONS.find(n => n.type === type)
}

/**
 * Check if a connection is valid between two node types
 *
 * Simplified validation - only structural constraints:
 * 1. Terminal nodes (collector, display) have no output
 * 2. Source nodes (input) have no input
 * 3. Seed nodes can only connect to generation nodes
 * 4. No self-loops
 *
 * Data type compatibility (text vs image) is checked at runtime by the backend.
 */
export function isValidConnection(sourceType: StageType, targetType: StageType): boolean {
  // Terminal nodes have no output connector
  const terminalNodes: StageType[] = ['collector', 'display']
  if (terminalNodes.includes(sourceType)) return false

  // Source nodes have no input connector
  const sourceNodes: StageType[] = ['input', 'image_input']
  if (sourceNodes.includes(targetType)) return false

  // Session 149: Seed nodes can only connect to generation nodes
  if (sourceType === 'seed' && targetType !== 'generation') return false

  // Session 151: Resolution and Quality nodes can only connect to generation nodes
  if (sourceType === 'resolution' && targetType !== 'generation') return false
  if (sourceType === 'quality' && targetType !== 'generation') return false

  // No self-loops (same node type connecting to itself is allowed, just not same instance)
  // This is handled elsewhere - same type is fine

  return true
}

/**
 * Generate a unique node ID
 */
export function generateNodeId(type: StageType): string {
  return `${type}_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`
}

/**
 * Create a default canvas workflow
 *
 * Default structure: Input → (user adds interception/generation) → Collector
 * Safety is handled automatically by DevServer.
 */
export function createDefaultWorkflow(): CanvasWorkflow {
  const inputNode: CanvasNode = {
    id: generateNodeId('input'),
    type: 'input',
    x: 100,
    y: 200,
    config: { source: 'text' }
  }

  const collectorNode: CanvasNode = {
    id: generateNodeId('collector'),
    type: 'collector',
    x: 900,
    y: 200,
    config: {}
  }

  return {
    id: `workflow_${Date.now()}`,
    name: 'New Workflow',
    type: 'canvas_workflow',
    nodes: [inputNode, collectorNode],
    connections: [],
    automation: {
      seedControl: 'global',
      loraInjection: true
    }
  }
}

// ============================================================================
// RANDOM PROMPT PRESETS (Session 140)
// ============================================================================

/** Preset configuration for Random Prompt node */
export interface RandomPromptPresetConfig {
  label: LocalizedString
  systemPrompt: string
  userPromptTemplate: string
}

/** Random Prompt Presets with system prompts */
export const RANDOM_PROMPT_PRESETS: Record<RandomPromptPreset, RandomPromptPresetConfig> = {
  clean_image: {
    label: { en: 'Scenic Description', de: 'Szenische Beschreibung', tr: 'Sahne Açıklaması' },
    systemPrompt: `You are an inventive creative. Your task is to invent a vivid, detailed image prompt.

IMPORTANT - Generate CLEAN, MEDIA-NEUTRAL images:
- NO camera or photographic references (no film, no camera, no lens)
- NO optical effects (no wide-angle, no telephoto, no macro)
- NO depth of field or bokeh
- NO motion blur or any blur effects
- NO "retro", "vintage", or nostalgic styling
- NO film grain, vignette, or post-processing artifacts

Think globally. Avoid cultural clichés.
Subject matter: scenes, objects, animals, nature, technology, culture, people, homes, family, work, holiday, urban, rural, trivia, intricate details.
Be verbose, provide rich visual details about colors, lighting, textures, composition, atmosphere.
Transform the prompt strictly following the context if provided.
NO META-COMMENTS, TITLES, Remarks, dialogue WHATSOEVER.`,
    userPromptTemplate: 'Generate a creative image prompt.'
  },
  photo: {
    label: { en: 'Photo Prompt', de: 'Foto-Prompt', tr: 'Fotoğraf Komutu' },
    systemPrompt: `You are an inventive creative. Your task is to invent a REALISTIC photographic image prompt.

Think globally. Avoid cultural clichés. Avoid "retro" style descriptions.
Describe contemporary everyday motives: scenes, objects, animals, nature, tech, culture, people, homes, family, work, holiday, urban, rural, trivia, details.
Choose either unlikely, untypical or typical photographical sujets. Be verbose, provide intricate details.
Always begin your output with: "{film_description} of".
Transform the prompt strictly following the context if provided.
NO META-COMMENTS, TITLES, Remarks, dialogue WHATSOEVER.`,
    userPromptTemplate: 'Generate a creative photographic image prompt.'
  },
  artform: {
    label: { en: 'Artform Transformation', de: 'Kunstform-Transformation', tr: 'Sanat Formu Dönüşümü' },
    systemPrompt: `You generate artform transformation instructions from an artist practice perspective.

IMPORTANT: NEVER use "in the style of" - instead frame as artistic practice, technique, or creative process.

Good examples:
- "Render this as a Japanese Noh theatre performance"
- "Transform this into a Yoruba praise poem"
- "Compose this as a Maori chant"
- "Frame this message through Cubist fragmentation"
- "Present this as an Afro-futurist myth"
- "Choreograph this as a Bharatanatyam narrative"
- "Inscribe this as Egyptian hieroglyphics"
- "Express this through Aboriginal dot painting technique"

Think globally across all cultures and art practices.
Focus on the DOING - the artistic practice, not imitation.
Output ONLY the transformation instruction, nothing else.`,
    userPromptTemplate: 'Generate a creative artform transformation instruction.'
  },
  instruction: {
    label: { en: 'Creative Instruction', de: 'Kreative Anweisung', tr: 'Yaratıcı Talimat' },
    systemPrompt: `You generate creative transformation instructions.
Your output is a single instruction that transforms content in an unusual, creative way.
Examples: nature language, theatrical play, nostalgic robot voice, rhythmic rap, animal fable, alien explanation, philosophical versions (Wittgenstein, Heidegger, Adorno), ancient manuscript, bedtime story for post-human child, internal monologue of a tree, forgotten folk song lyrics, spy messages, protest chant, underwater civilization dialect, extinct animal conversation, dream sequence, poetic weather forecast, love letter to future generation, etc.
Be wildly creative and unexpected.
Output ONLY the transformation instruction, nothing else.`,
    userPromptTemplate: 'Generate a creative transformation instruction.'
  },
  language: {
    label: { en: 'Language Suggestion', de: 'Sprach-Vorschlag', tr: 'Dil Önerisi' },
    systemPrompt: `You suggest a random language from around the world.
Choose from major world languages, regional languages, or less common languages.
Consider: European, Asian, African, Indigenous American, Pacific languages.
Output ONLY the language name in English, nothing else.
Example outputs: "Swahili", "Bengali", "Quechua", "Welsh", "Tagalog"`,
    userPromptTemplate: 'Suggest a random language.'
  }
}

/** Photo film type descriptions */
export const PHOTO_FILM_TYPES: Record<PhotoFilmType, string> = {
  random: '', // Will be selected at runtime
  'Kodachrome': 'a Kodachrome film slide',
  'Ektachrome': 'an Ektachrome film slide',
  'Portra 400': 'a Kodak Portra 400 color negative',
  'Portra 800': 'a Kodak Portra 800 color negative',
  'Ektar 100': 'a Kodak Ektar 100 color negative',
  'Fuji Pro 400H': 'a Fujifilm Pro 400H color negative',
  'Fuji Superia': 'a Fujifilm Superia color negative',
  'CineStill 800T': 'a CineStill 800T tungsten-balanced color negative',
  'Ilford HP5': 'an Ilford HP5 Plus black and white negative',
  'Ilford Delta 400': 'an Ilford Delta 400 black and white negative',
  'Ilford FP4': 'an Ilford FP4 Plus black and white negative',
  'Ilford Pan F': 'an Ilford Pan F Plus 50 black and white negative',
  'Ilford XP2': 'an Ilford XP2 Super chromogenic black and white negative',
  'Tri-X 400': 'a Kodak Tri-X 400 black and white negative'
}
