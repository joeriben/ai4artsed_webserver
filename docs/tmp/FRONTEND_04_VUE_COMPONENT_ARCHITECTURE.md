# Vue Component Architecture

**Version:** 1.0
**Date:** 2025-11-06
**Status:** Planning Document
**Parent:** FRONTEND_ARCHITECTURE_OVERVIEW.md

---

## Executive Summary

This document defines the Vue.js component hierarchy, state management strategy, and routing structure for the AI4ArtsEd DevServer frontend. The architecture follows Vue 3 Composition API patterns with TypeScript support, organized around the 3-phase user journey.

---

## Project Structure

```
frontend/
├── src/
│   ├── main.ts                    # App bootstrap
│   ├── App.vue                    # Root component
│   ├── router/
│   │   └── index.ts               # Vue Router configuration
│   ├── stores/
│   │   ├── configStore.ts         # Pinia store: Config selection
│   │   ├── pipelineStore.ts       # Pinia store: Execution state
│   │   └── userStore.ts           # Pinia store: User preferences
│   ├── services/
│   │   ├── api.ts                 # API client (Axios)
│   │   └── polling.ts             # Polling utilities
│   ├── composables/
│   │   ├── useConfigLoader.ts     # Composable: Load configs
│   │   ├── usePipelinePolling.ts  # Composable: Status polling
│   │   └── useMediaPlayer.ts      # Composable: Media playback
│   ├── types/
│   │   ├── config.ts              # TypeScript types: Config
│   │   ├── pipeline.ts            # TypeScript types: Pipeline
│   │   └── entity.ts              # TypeScript types: Entity
│   ├── views/
│   │   ├── Phase1View.vue         # Phase 1: Schema Selection
│   │   └── Phase2_3View.vue       # Phase 2+3: Flow Experience
│   ├── components/
│   │   ├── phase1/
│   │   │   ├── ConfigBrowser.vue
│   │   │   ├── TileView.vue
│   │   │   ├── ListView.vue
│   │   │   ├── LLMDialogView.vue
│   │   │   ├── ConfigCard.vue
│   │   │   ├── ConfigRow.vue
│   │   │   ├── ConfigModal.vue
│   │   │   ├── ModeSwitcher.vue
│   │   │   ├── SearchBar.vue
│   │   │   └── FilterPanel.vue
│   │   ├── phase2_3/
│   │   │   ├── PipelineFlow.vue
│   │   │   ├── PromptInput.vue
│   │   │   ├── StageBox.vue
│   │   │   ├── ConnectionLine.vue
│   │   │   ├── EntityTimeline.vue
│   │   │   ├── EntityViewer.vue
│   │   │   ├── OutputDisplay.vue
│   │   │   ├── ImageOutput.vue
│   │   │   ├── AudioOutput.vue
│   │   │   └── TextOutput.vue
│   │   ├── shared/
│   │   │   ├── AppHeader.vue
│   │   │   ├── ErrorAlert.vue
│   │   │   ├── LoadingSpinner.vue
│   │   │   └── ProgressBar.vue
│   │   └── icons/
│   │       ├── TileIcon.vue
│   │       ├── ListIcon.vue
│   │       └── LLMIcon.vue
│   ├── assets/
│   │   ├── styles/
│   │   │   ├── main.css
│   │   │   ├── phase1.css
│   │   │   └── phase2_3.css
│   │   └── images/
│   └── utils/
│       ├── format.ts              # Formatting utilities
│       └── validation.ts          # Input validation
├── public/
│   └── index.html
├── package.json
├── vite.config.ts                 # Vite configuration
├── tsconfig.json                  # TypeScript configuration
└── README.md
```

---

## Component Hierarchy

### Overall Application Structure

```
App.vue
├── AppHeader.vue (optional, global navigation)
└── RouterView
    ├── Phase1View.vue
    │   └── ConfigBrowser.vue
    │       ├── ModeSwitcher.vue
    │       ├── SearchBar.vue
    │       ├── FilterPanel.vue
    │       └── [Current Mode Component]
    │           ├── TileView.vue
    │           │   └── ConfigCard.vue
    │           │       └── ConfigModal.vue
    │           ├── ListView.vue
    │           │   ├── ConfigRow.vue
    │           │   └── ConfigDetailsPanel.vue
    │           └── LLMDialogView.vue
    │               └── ConfigRecommendation.vue
    │
    └── Phase2_3View.vue
        └── PipelineFlow.vue
            ├── PromptInput.vue
            ├── StageFlow.vue
            │   ├── StageBox.vue (x4)
            │   └── ConnectionLine.vue (x3-4)
            ├── EntityTimeline.vue
            │   └── EntityViewer.vue (modal)
            └── OutputDisplay.vue
                ├── ImageOutput.vue
                ├── AudioOutput.vue
                ├── MusicOutput.vue
                └── TextOutput.vue
```

---

## Phase 1 Components

### Phase1View.vue (Route View)

**Purpose:** Container for entire Phase 1 (Schema Selection)

**Template:**
```vue
<template>
  <div class="phase1-view">
    <AppHeader title="Select Schema Configuration" />
    <ConfigBrowser />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useConfigStore } from '@/stores/configStore';
import ConfigBrowser from '@/components/phase1/ConfigBrowser.vue';

const configStore = useConfigStore();

onMounted(() => {
  configStore.loadConfigs();
});
</script>
```

**Responsibilities:**
- Load config metadata on mount
- Provide top-level layout
- Handle route params (if any)

---

### ConfigBrowser.vue (Parent Component)

**Purpose:** Orchestrate config selection experience

**Props:** None (reads from store)

**Template:**
```vue
<template>
  <div class="config-browser">
    <div class="toolbar">
      <ModeSwitcher v-model="currentMode" />
      <SearchBar v-model="searchQuery" />
      <FilterPanel v-model="activeFilters" />
    </div>

    <div class="config-display">
      <TileView v-if="currentMode === 'tiles'" :configs="filteredConfigs" />
      <ListView v-else-if="currentMode === 'list'" :configs="filteredConfigs" />
      <LLMDialogView v-else :configs="filteredConfigs" />
    </div>

    <ConfigModal
      v-if="selectedConfig"
      :config="selectedConfig"
      @close="selectedConfig = null"
      @confirm="handleConfirmSelection"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useConfigStore } from '@/stores/configStore';
import type { Config } from '@/types/config';

const router = useRouter();
const configStore = useConfigStore();

const currentMode = ref<'tiles' | 'list' | 'llm'>('tiles');
const searchQuery = ref('');
const activeFilters = ref({});
const selectedConfig = ref<Config | null>(null);

const filteredConfigs = computed(() => {
  return configStore.getFilteredConfigs(searchQuery.value, activeFilters.value);
});

function handleConfirmSelection(config: Config, params: ExecutionParams) {
  configStore.selectConfig(config, params);
  router.push({
    name: 'pipeline-flow',
    params: { configId: config.id }
  });
}
</script>
```

**Responsibilities:**
- Manage mode switching
- Coordinate search/filter
- Handle config selection
- Navigate to Phase 2+3

---

### ModeSwitcher.vue

**Purpose:** Icon-based switcher for three visualization modes

**Props:**
```typescript
defineProps<{
  modelValue: 'tiles' | 'list' | 'llm'
}>()

defineEmits<{
  (e: 'update:modelValue', value: 'tiles' | 'list' | 'llm'): void
}>()
```

**Template:**
```vue
<template>
  <div class="mode-switcher" role="radiogroup" aria-label="Visualization mode">
    <button
      v-for="mode in modes"
      :key="mode.value"
      :class="['mode-button', { active: modelValue === mode.value }]"
      :aria-checked="modelValue === mode.value"
      role="radio"
      @click="$emit('update:modelValue', mode.value)"
    >
      <component :is="mode.icon" />
      <span class="mode-label">{{ mode.label }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import TileIcon from '@/components/icons/TileIcon.vue';
import ListIcon from '@/components/icons/ListIcon.vue';
import LLMIcon from '@/components/icons/LLMIcon.vue';

const modes = [
  { value: 'tiles', label: 'Tiles', icon: TileIcon },
  { value: 'list', label: 'List', icon: ListIcon },
  { value: 'llm', label: 'AI Help', icon: LLMIcon }
];
</script>
```

---

### TileView.vue

**Purpose:** Grid-based card display

**Props:**
```typescript
defineProps<{
  configs: Config[]
}>()
```

**Template:**
```vue
<template>
  <div class="tile-view">
    <div
      v-for="category in groupedConfigs"
      :key="category.name"
      class="category-section"
    >
      <h2 class="category-header">{{ category.name }}</h2>
      <div class="tile-grid">
        <ConfigCard
          v-for="config in category.configs"
          :key="config.id"
          :config="config"
          @select="$emit('select', config)"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import ConfigCard from './ConfigCard.vue';
import type { Config } from '@/types/config';

const props = defineProps<{
  configs: Config[]
}>();

const emit = defineEmits<{
  (e: 'select', config: Config): void
}>();

const groupedConfigs = computed(() => {
  // Group configs by category
  const groups = new Map<string, Config[]>();
  props.configs.forEach(config => {
    const category = config.category || 'Other';
    if (!groups.has(category)) {
      groups.set(category, []);
    }
    groups.get(category)!.push(config);
  });

  return Array.from(groups.entries()).map(([name, configs]) => ({
    name,
    configs
  }));
});
</script>
```

---

### ConfigCard.vue

**Purpose:** Individual config tile with icon, metadata, and selection

**Props:**
```typescript
defineProps<{
  config: Config
}>()
```

**Template:**
```vue
<template>
  <div
    class="config-card"
    :class="{ 'user-config': config.is_user_config }"
    tabindex="0"
    @click="$emit('select', config)"
    @keydown.enter="$emit('select', config)"
  >
    <div class="card-header">
      <span v-if="config.is_user_config" class="user-badge">USER</span>
      <span class="category-badge">{{ config.category }}</span>
    </div>

    <div class="card-icon">
      {{ config.icon }}
      <!-- Or DX7-style flowchart SVG here -->
    </div>

    <h3 class="config-name">{{ config.name }}</h3>
    <p class="config-description">{{ config.description }}</p>

    <div class="card-meta">
      <div class="difficulty">
        <span v-for="i in 5" :key="i" class="star" :class="{ filled: i <= config.difficulty }">
          ⭐
        </span>
      </div>
      <div class="output-badges">
        <span v-for="type in config.output_types" :key="type" class="badge">
          {{ type }}
        </span>
      </div>
    </div>

    <button class="select-button">Select</button>
  </div>
</template>

<script setup lang="ts">
import type { Config } from '@/types/config';

defineProps<{
  config: Config
}>();

defineEmits<{
  (e: 'select', config: Config): void
}>();
</script>
```

---

### ListView.vue

**Purpose:** Table-based compact display

**Props:**
```typescript
defineProps<{
  configs: Config[]
}>()
```

**Template:**
```vue
<template>
  <div class="list-view">
    <table class="config-table">
      <thead>
        <tr>
          <th @click="sortBy('icon')">Icon</th>
          <th @click="sortBy('name')">Name</th>
          <th @click="sortBy('category')">Category</th>
          <th @click="sortBy('output')">Output</th>
          <th @click="sortBy('difficulty')">Difficulty</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <ConfigRow
          v-for="config in sortedConfigs"
          :key="config.id"
          :config="config"
          @select="$emit('select', config)"
        />
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import ConfigRow from './ConfigRow.vue';
import type { Config } from '@/types/config';

const props = defineProps<{
  configs: Config[]
}>();

const emit = defineEmits<{
  (e: 'select', config: Config): void
}>();

const sortField = ref<string>('name');
const sortDirection = ref<'asc' | 'desc'>('asc');

const sortedConfigs = computed(() => {
  return [...props.configs].sort((a, b) => {
    // Sorting logic
    const aVal = a[sortField.value];
    const bVal = b[sortField.value];
    return sortDirection.value === 'asc' ? aVal - bVal : bVal - aVal;
  });
});

function sortBy(field: string) {
  if (sortField.value === field) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortField.value = field;
    sortDirection.value = 'asc';
  }
}
</script>
```

---

### ConfigModal.vue

**Purpose:** Selection confirmation with execution parameters

**Props:**
```typescript
defineProps<{
  config: Config
}>()
```

**Template:**
```vue
<template>
  <teleport to="body">
    <div class="modal-overlay" @click="$emit('close')">
      <div class="modal-content" @click.stop>
        <header>
          <h2>{{ config.icon }} {{ config.name }}</h2>
          <button class="close-button" @click="$emit('close')">✕</button>
        </header>

        <main>
          <p class="description">{{ config.description }}</p>

          <div class="parameter-section">
            <h3>Execution Mode</h3>
            <label>
              <input type="radio" v-model="executionMode" value="eco" />
              Eco Mode (Local, slower, free)
            </label>
            <label>
              <input type="radio" v-model="executionMode" value="fast" />
              Fast Mode (Cloud, faster, requires credits)
            </label>
          </div>

          <div class="parameter-section">
            <h3>Safety Level</h3>
            <label>
              <input type="radio" v-model="safetyLevel" value="kids" />
              Kids (Strict filtering)
            </label>
            <label>
              <input type="radio" v-model="safetyLevel" value="youth" />
              Youth (Moderate filtering)
            </label>
          </div>
        </main>

        <footer>
          <button class="cancel-button" @click="$emit('close')">Cancel</button>
          <button class="confirm-button" @click="handleConfirm">
            Select & Continue
          </button>
        </footer>
      </div>
    </div>
  </teleport>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import type { Config } from '@/types/config';

const props = defineProps<{
  config: Config
}>();

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'confirm', config: Config, params: ExecutionParams): void
}>();

const executionMode = ref<'eco' | 'fast'>('fast');
const safetyLevel = ref<'kids' | 'youth'>('kids');

function handleConfirm() {
  emit('confirm', props.config, {
    execution_mode: executionMode.value,
    safety_level: safetyLevel.value
  });
}
</script>
```

---

## Phase 2+3 Components

### Phase2_3View.vue (Route View)

**Purpose:** Container for entire Phase 2+3 (Flow Experience)

**Template:**
```vue
<template>
  <div class="phase2-3-view">
    <AppHeader>
      <button @click="handleBack">← Back to Selection</button>
      <span>{{ selectedConfig?.name }}</span>
    </AppHeader>
    <PipelineFlow />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { useConfigStore } from '@/stores/configStore';
import PipelineFlow from '@/components/phase2_3/PipelineFlow.vue';

const router = useRouter();
const configStore = useConfigStore();

const selectedConfig = computed(() => configStore.selectedConfig);

function handleBack() {
  if (confirm('Return to config selection?')) {
    router.push({ name: 'phase1' });
  }
}
</script>
```

---

### PipelineFlow.vue (Parent Component)

**Purpose:** Orchestrate entire flow experience

**Template:**
```vue
<template>
  <div class="pipeline-flow">
    <PromptInput
      v-if="!runId"
      @submit="handleExecute"
    />

    <div v-else class="execution-display">
      <div class="prompt-display">
        <p>Your prompt: "{{ inputPrompt }}"</p>
        <button v-if="pipelineCompleted" @click="handleEditPrompt">
          Edit & Run Again
        </button>
      </div>

      <StageFlow
        :stages="stages"
        :current-stage="currentStage"
      />

      <EntityTimeline
        :entities="entities"
        @view-entity="handleViewEntity"
      />

      <OutputDisplay
        v-if="pipelineCompleted"
        :output="finalOutput"
        :config="selectedConfig"
      />
    </div>

    <EntityViewer
      v-if="viewingEntity"
      :entity="viewingEntity"
      :run-id="runId"
      @close="viewingEntity = null"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRoute } from 'vue-router';
import { useConfigStore } from '@/stores/configStore';
import { usePipelineStore } from '@/stores/pipelineStore';
import { usePipelinePolling } from '@/composables/usePipelinePolling';

const route = useRoute();
const configStore = useConfigStore();
const pipelineStore = usePipelineStore();

const selectedConfig = computed(() => configStore.selectedConfig);
const runId = computed(() => pipelineStore.runId);
const inputPrompt = computed(() => pipelineStore.inputPrompt);
const stages = computed(() => pipelineStore.stages);
const currentStage = computed(() => pipelineStore.currentStage);
const entities = computed(() => pipelineStore.entities);
const pipelineCompleted = computed(() => pipelineStore.status === 'completed');
const finalOutput = computed(() => pipelineStore.finalOutput);

const viewingEntity = ref(null);

const { startPolling, stopPolling } = usePipelinePolling(runId);

async function handleExecute(prompt: string) {
  await pipelineStore.executePipeline(
    selectedConfig.value!.id,
    prompt
  );
  startPolling();
}

function handleEditPrompt() {
  pipelineStore.reset();
}

function handleViewEntity(entity: Entity) {
  viewingEntity.value = entity;
}

onUnmounted(() => {
  stopPolling();
});
</script>
```

---

### PromptInput.vue

**Purpose:** Initial prompt input form

**Template:**
```vue
<template>
  <div class="prompt-input">
    <h2>Enter your prompt</h2>

    <textarea
      v-model="prompt"
      :placeholder="examplePrompts[0]"
      :maxlength="maxLength"
      rows="5"
    />

    <div class="char-count">
      {{ prompt.length }} / {{ maxLength }}
    </div>

    <div class="example-prompts">
      <h3>Example prompts:</h3>
      <ul>
        <li v-for="example in examplePrompts" :key="example">
          {{ example }}
        </li>
      </ul>
    </div>

    <button
      class="execute-button"
      :disabled="!prompt.trim()"
      @click="$emit('submit', prompt)"
    >
      Execute Pipeline →
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useConfigStore } from '@/stores/configStore';

const configStore = useConfigStore();

const prompt = ref('');
const maxLength = computed(() => {
  return configStore.selectedConfig?.input_requirements?.max_length || 500;
});

const examplePrompts = [
  "A surreal landscape with floating islands",
  "An astronaut riding a bicycle through space",
  "A cozy cabin in a snowy forest at twilight"
];

defineEmits<{
  (e: 'submit', prompt: string): void
}>();
</script>
```

---

### StageFlow.vue

**Purpose:** Horizontal flow of 4 stage boxes with connections

**Props:**
```typescript
defineProps<{
  stages: Stage[]
  currentStage: number
}>()
```

**Template:**
```vue
<template>
  <div class="stage-flow">
    <div class="stages-container">
      <template v-for="(stage, index) in stages" :key="stage.number">
        <StageBox
          :stage="stage"
          :is-current="currentStage === stage.number"
          @expand="handleExpand(stage)"
        />

        <ConnectionLine
          v-if="index < stages.length - 1"
          :status="getConnectionStatus(stage, stages[index + 1])"
        />
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import StageBox from './StageBox.vue';
import ConnectionLine from './ConnectionLine.vue';
import type { Stage } from '@/types/pipeline';

defineProps<{
  stages: Stage[]
  currentStage: number
}>();

function getConnectionStatus(from: Stage, to: Stage) {
  if (from.status === 'completed' && to.status !== 'pending') {
    return 'active';
  } else if (from.status === 'completed') {
    return 'completed';
  }
  return 'inactive';
}

function handleExpand(stage: Stage) {
  // Emit event or use store to expand stage details
}
</script>
```

---

### StageBox.vue

**Purpose:** Individual stage visualization box

**Props:**
```typescript
defineProps<{
  stage: Stage
  isCurrent: boolean
}>()
```

**Template:**
```vue
<template>
  <div
    class="stage-box"
    :class="[stage.status, { current: isCurrent }]"
  >
    <header>
      <div class="stage-number">Stage {{ stage.number }}</div>
      <div class="stage-name">{{ stage.name }}</div>
    </header>

    <main class="stage-status">
      <div class="status-icon">
        <span v-if="stage.status === 'completed'">✓</span>
        <span v-else-if="stage.status === 'in_progress'" class="spinner">⟳</span>
        <span v-else>○</span>
      </div>

      <div class="status-text">
        <span v-if="stage.status === 'completed'">Completed</span>
        <span v-else-if="stage.status === 'in_progress'">
          {{ stage.step }}
        </span>
        <span v-else>Pending</span>
      </div>

      <div v-if="stage.progress" class="progress">
        {{ stage.progress }}
      </div>

      <div v-if="stage.status === 'completed' && stage.time" class="time">
        Time: {{ stage.time }}s
      </div>
    </main>

    <footer v-if="stage.status === 'completed'">
      <button class="expand-button" @click="$emit('expand', stage)">
        Expand Details ▼
      </button>
    </footer>
  </div>
</template>

<script setup lang="ts">
import type { Stage } from '@/types/pipeline';

defineProps<{
  stage: Stage
  isCurrent: boolean
}>();

defineEmits<{
  (e: 'expand', stage: Stage): void
}>();
</script>
```

---

### EntityTimeline.vue

**Purpose:** Vertical or horizontal timeline of all entities

**Props:**
```typescript
defineProps<{
  entities: Entity[]
}>()
```

**Template:**
```vue
<template>
  <div class="entity-timeline">
    <h3>Pipeline Outputs</h3>

    <div class="timeline-items">
      <div
        v-for="entity in entities"
        :key="entity.sequence"
        class="timeline-item"
        :class="entity.available ? 'available' : 'pending'"
      >
        <div class="status-indicator">
          <span v-if="entity.available">✓</span>
          <span v-else-if="entity.in_progress">⟳</span>
          <span v-else>○</span>
        </div>

        <div class="entity-info">
          <div class="entity-type">
            {{ formatEntityType(entity.type) }}
          </div>
          <div v-if="entity.available" class="entity-preview">
            {{ getPreview(entity) }}
          </div>
        </div>

        <button
          v-if="entity.available"
          class="view-button"
          @click="$emit('view-entity', entity)"
        >
          View
        </button>
        <span v-else class="waiting">Waiting...</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Entity } from '@/types/entity';

defineProps<{
  entities: Entity[]
}>();

defineEmits<{
  (e: 'view-entity', entity: Entity): void
}>();

function formatEntityType(type: string): string {
  const map = {
    'input': '01 • Input',
    'translation': '02 • Translation',
    'safety': '03 • Safety Check',
    'interception': '04 • Interception',
    'safety_pre_output': '05 • Final Safety',
    'output_image': '06 • Output Image'
  };
  return map[type] || type;
}

function getPreview(entity: Entity): string {
  // Return first 50 chars of content
  return entity.preview || '(View full content)';
}
</script>
```

---

### OutputDisplay.vue

**Purpose:** Display final media output based on type

**Props:**
```typescript
defineProps<{
  output: Output
  config: Config
}>()
```

**Template:**
```vue
<template>
  <div class="output-display">
    <h2>Final Output</h2>

    <ImageOutput v-if="output.type === 'image'" :output="output" />
    <AudioOutput v-else-if="output.type === 'audio'" :output="output" />
    <MusicOutput v-else-if="output.type === 'music'" :output="output" />
    <TextOutput v-else-if="output.type === 'text'" :output="output" />

    <div class="output-actions">
      <button @click="handleDownload">💾 Download</button>
      <button @click="handleShare">🔗 Share</button>
      <button @click="handleGenerateAgain">🔄 Generate Again</button>
      <button @click="handleNewConfig">⚙️ New Config</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import ImageOutput from './ImageOutput.vue';
import AudioOutput from './AudioOutput.vue';
import MusicOutput from './MusicOutput.vue';
import TextOutput from './TextOutput.vue';

const router = useRouter();

const props = defineProps<{
  output: Output
  config: Config
}>();

function handleDownload() {
  // Download logic
}

function handleShare() {
  // Share logic
}

function handleGenerateAgain() {
  // Reset pipeline, keep same config
}

function handleNewConfig() {
  router.push({ name: 'phase1' });
}
</script>
```

---

## State Management (Pinia)

### configStore.ts

**Purpose:** Manage config metadata and selection

**Store Structure:**
```typescript
import { defineStore } from 'pinia';
import type { Config, ExecutionParams } from '@/types/config';
import { apiClient } from '@/services/api';

export const useConfigStore = defineStore('config', {
  state: () => ({
    configs: [] as Config[],
    selectedConfig: null as Config | null,
    executionParams: null as ExecutionParams | null,
    loading: false,
    error: null as string | null
  }),

  getters: {
    getFilteredConfigs: (state) => (query: string, filters: any) => {
      return state.configs.filter(config => {
        // Apply search query
        const matchesQuery = query === '' ||
          config.name.toLowerCase().includes(query.toLowerCase()) ||
          config.description.toLowerCase().includes(query.toLowerCase());

        // Apply filters
        const matchesFilters = Object.entries(filters).every(([key, value]) => {
          if (!value) return true;
          return config[key] === value;
        });

        return matchesQuery && matchesFilters;
      });
    }
  },

  actions: {
    async loadConfigs() {
      this.loading = true;
      this.error = null;

      try {
        const response = await apiClient.get('/pipeline_configs_metadata');
        this.configs = response.data.configs;
      } catch (error) {
        this.error = 'Failed to load configurations';
        console.error(error);
      } finally {
        this.loading = false;
      }
    },

    selectConfig(config: Config, params: ExecutionParams) {
      this.selectedConfig = config;
      this.executionParams = params;
    },

    clearSelection() {
      this.selectedConfig = null;
      this.executionParams = null;
    }
  }
});
```

---

### pipelineStore.ts

**Purpose:** Manage pipeline execution state

**Store Structure:**
```typescript
import { defineStore } from 'pinia';
import type { Stage, Entity, Output } from '@/types/pipeline';
import { apiClient } from '@/services/api';

export const usePipelineStore = defineStore('pipeline', {
  state: () => ({
    runId: null as string | null,
    inputPrompt: '',
    status: 'idle' as 'idle' | 'running' | 'completed' | 'error',
    currentStage: 0,
    currentStep: '',
    progress: '',
    stages: [] as Stage[],
    entities: [] as Entity[],
    finalOutput: null as Output | null,
    elapsedTime: 0,
    error: null as string | null
  }),

  actions: {
    async executePipeline(configId: string, prompt: string) {
      this.inputPrompt = prompt;
      this.status = 'running';

      try {
        const response = await apiClient.post('/api/schema/pipeline/execute', {
          schema: configId,
          input_text: prompt,
          execution_mode: 'fast',  // From configStore
          safety_level: 'kids'
        });

        this.runId = response.data.run_id;
        this.initializeStages();
      } catch (error) {
        this.status = 'error';
        this.error = 'Failed to start pipeline execution';
        console.error(error);
      }
    },

    updateFromPollStatus(statusData: any) {
      this.currentStage = statusData.current_state.stage;
      this.currentStep = statusData.current_state.step;
      this.progress = statusData.current_state.progress;
      this.elapsedTime = statusData.elapsed_time;
      this.entities = statusData.entities;

      // Update stage states
      this.updateStageStates();

      // Check completion
      if (statusData.status === 'completed') {
        this.status = 'completed';
        this.loadFinalOutput();
      } else if (statusData.status === 'error') {
        this.status = 'error';
        this.error = statusData.error;
      }
    },

    updateStageStates() {
      // Mark stages as completed/in-progress/pending based on currentStage
      this.stages.forEach((stage, index) => {
        if (index + 1 < this.currentStage) {
          stage.status = 'completed';
        } else if (index + 1 === this.currentStage) {
          stage.status = 'in_progress';
          stage.step = this.currentStep;
          stage.progress = this.progress;
        } else {
          stage.status = 'pending';
        }
      });
    },

    initializeStages() {
      this.stages = [
        { number: 1, name: 'Pre-Processing', status: 'pending' },
        { number: 2, name: 'Interception', status: 'pending' },
        { number: 3, name: 'Safety Check', status: 'pending' },
        { number: 4, name: 'Media Output', status: 'pending' }
      ];
    },

    async loadFinalOutput() {
      // Fetch final output entity
      const outputEntity = this.entities.find(e =>
        e.type.startsWith('output_')
      );

      if (outputEntity) {
        this.finalOutput = {
          type: outputEntity.type.replace('output_', ''),
          url: `/api/pipeline/${this.runId}/entity/${outputEntity.type}`,
          mime_type: outputEntity.mime_type
        };
      }
    },

    reset() {
      this.runId = null;
      this.status = 'idle';
      this.currentStage = 0;
      this.stages = [];
      this.entities = [];
      this.finalOutput = null;
    }
  }
});
```

---

## Composables

### usePipelinePolling.ts

**Purpose:** Reusable polling logic

**Composable:**
```typescript
import { ref, computed } from 'vue';
import { usePipelineStore } from '@/stores/pipelineStore';
import { apiClient } from '@/services/api';

export function usePipelinePolling(runId: Ref<string | null>) {
  const pipelineStore = usePipelineStore();
  const isPolling = ref(false);
  const pollInterval = ref<number | null>(null);

  async function startPolling() {
    if (!runId.value) return;

    isPolling.value = true;
    pollInterval.value = setInterval(async () => {
      try {
        const response = await apiClient.get(`/api/pipeline/${runId.value}/status`);
        pipelineStore.updateFromPollStatus(response.data);

        if (response.data.status === 'completed' || response.data.status === 'error') {
          stopPolling();
        }
      } catch (error) {
        console.error('Polling error:', error);
        // Implement retry logic or stop after X failures
      }
    }, 1000);  // Poll every 1 second
  }

  function stopPolling() {
    if (pollInterval.value) {
      clearInterval(pollInterval.value);
      pollInterval.value = null;
      isPolling.value = false;
    }
  }

  return {
    isPolling: computed(() => isPolling.value),
    startPolling,
    stopPolling
  };
}
```

---

## Router Configuration

### router/index.ts

**Router Setup:**
```typescript
import { createRouter, createWebHistory } from 'vue-router';
import Phase1View from '@/views/Phase1View.vue';
import Phase2_3View from '@/views/Phase2_3View.vue';

const routes = [
  {
    path: '/',
    redirect: '/select'
  },
  {
    path: '/select',
    name: 'phase1',
    component: Phase1View,
    meta: { title: 'Select Configuration' }
  },
  {
    path: '/pipeline/:configId',
    name: 'pipeline-flow',
    component: Phase2_3View,
    meta: { title: 'Pipeline Execution' },
    beforeEnter: (to, from, next) => {
      const configStore = useConfigStore();
      if (!configStore.selectedConfig) {
        // No config selected, redirect to Phase 1
        next({ name: 'phase1' });
      } else {
        next();
      }
    }
  },
  {
    path: '/view/:runId',
    name: 'view-run',
    component: () => import('@/views/ViewRunView.vue'),
    meta: { title: 'View Pipeline Run' }
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
```

---

## TypeScript Types

### types/config.ts

```typescript
export interface Config {
  id: string;
  name: string;
  description: string;
  category: string;
  icon: string;
  difficulty: number;  // 1-5
  tags: string[];
  input_requirements: {
    type: 'text' | 'image' | 'dual-text';
    max_length?: number;
  };
  output_types: ('text' | 'image' | 'audio' | 'music' | 'video')[];
  pipeline: string;
  is_user_config: boolean;
}

export interface ExecutionParams {
  execution_mode: 'eco' | 'fast';
  safety_level: 'kids' | 'youth';
}
```

### types/pipeline.ts

```typescript
export interface Stage {
  number: number;
  name: string;
  status: 'pending' | 'in_progress' | 'completed' | 'error';
  step?: string;
  progress?: string;
  time?: number;
}

export interface Entity {
  sequence: number;
  type: string;
  filename: string;
  available: boolean;
  in_progress?: boolean;
  mime_type?: string;
  size?: number;
  preview?: string;
}

export interface Output {
  type: 'text' | 'image' | 'audio' | 'music';
  url: string;
  mime_type: string;
  content?: string;
}
```

---

## Build Configuration

### vite.config.ts

```typescript
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:17801',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: '../devserver/public',
    emptyOutDir: true
  }
});
```

---

## Testing Strategy

### Unit Tests (Vitest)

**Example: ConfigCard.spec.ts**
```typescript
import { mount } from '@vue/test-utils';
import { describe, it, expect } from 'vitest';
import ConfigCard from '@/components/phase1/ConfigCard.vue';

describe('ConfigCard', () => {
  it('renders config name and description', () => {
    const config = {
      id: 'test',
      name: 'Test Config',
      description: 'Test description',
      icon: '🎨',
      difficulty: 3
    };

    const wrapper = mount(ConfigCard, {
      props: { config }
    });

    expect(wrapper.text()).toContain('Test Config');
    expect(wrapper.text()).toContain('Test description');
  });

  it('emits select event on click', async () => {
    const config = { id: 'test', name: 'Test' };
    const wrapper = mount(ConfigCard, {
      props: { config }
    });

    await wrapper.trigger('click');
    expect(wrapper.emitted('select')).toBeTruthy();
  });
});
```

### Integration Tests

**Example: Phase1 Flow**
```typescript
import { mount } from '@vue/test-utils';
import { createPinia } from 'pinia';
import Phase1View from '@/views/Phase1View.vue';

describe('Phase 1 Integration', () => {
  it('loads configs and displays them', async () => {
    const pinia = createPinia();
    const wrapper = mount(Phase1View, {
      global: {
        plugins: [pinia]
      }
    });

    // Wait for configs to load
    await wrapper.vm.$nextTick();

    expect(wrapper.findAll('.config-card').length).toBeGreaterThan(0);
  });
});
```

---

## Related Documentation

- `FRONTEND_ARCHITECTURE_OVERVIEW.md` - Overall architecture
- `PHASE_1_SCHEMA_SELECTION.md` - Phase 1 detailed specs
- `PHASE_2_3_FLOW_EXPERIENCE.md` - Phase 2+3 detailed specs
- `METADATA_SCHEMA_SPECIFICATION.md` - Config metadata structure

---

**Document Status:** ✅ Complete
**Next Steps:** Define metadata schema specification
**Estimated Implementation:** 4-6 weeks for MVP
