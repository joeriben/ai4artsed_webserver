# Visual Design Patterns

**Version:** 1.0
**Date:** 2025-11-06
**Status:** Planning Document
**Parent:** FRONTEND_ARCHITECTURE_OVERVIEW.md

---

## Executive Summary

This document defines the **visual design language** for the AI4ArtsEd DevServer frontend, including color systems, typography, spacing, component styling, and the DX7-inspired flowchart symbolization. The goal is consistent, accessible, educational UI that makes complex pipeline flows understandable and engaging.

---

## Design Philosophy

### Core Principles

1. **Clarity Over Decoration:** Information hierarchy is paramount
2. **Educational Focus:** Designs support learning, not just task completion
3. **Accessible by Default:** WCAG 2.1 AA compliance minimum
4. **Playful but Professional:** Engaging for students, credible for educators
5. **Metadata-Driven:** Visuals adapt dynamically to config metadata

### Inspiration Sources

- **Yamaha DX7 Algorithm Display:** Clear flowcharts showing signal routing
- **Modern Educational UIs:** Khan Academy, Scratch, MIT Blocks
- **Data Visualization:** D3.js, Observable visualizations
- **Design Systems:** Material Design 3, Ant Design, Chakra UI

---

## Color System

### Palette

**Primary Colors:**
```
Primary (Brand):    #4A90E2  (Blue - Trustworthy, Educational)
Secondary (Accent): #F39C12  (Orange - Creative, Energetic)
```

**Grayscale:**
```
Black:     #1A1A1A
Dark Gray: #333333
Gray:      #666666
Light Gray:#AAAAAA
Off-White: #F5F5F5
White:     #FFFFFF
```

**Semantic Colors:**
```
Success:   #27AE60  (Green)
Warning:   #F39C12  (Orange)
Error:     #E74C3C  (Red)
Info:      #3498DB  (Blue)
```

**Status Colors (Pipeline Stages):**
```
Pending:     #CCCCCC  (Light Gray)
In Progress: #F39C12  (Orange - active, energetic)
Completed:   #27AE60  (Green - success)
Error:       #E74C3C  (Red)
```

**Category Colors (Phase 1):**
```
Art Movements:       #9B59B6  (Purple)
Media Generation:    #E74C3C  (Red)
Text Transformation: #3498DB  (Blue)
Experimental:        #F39C12  (Orange)
User Configs:        #1ABC9C  (Turquoise)
```

### Color Usage

**Backgrounds:**
```
Page Background:      #FFFFFF (White)
Card Background:      #F5F5F5 (Off-White)
Modal Overlay:        rgba(0,0,0,0.5)
Elevated Card:        #FFFFFF with shadow
```

**Text:**
```
Primary Text:    #1A1A1A (Black) on #FFFFFF
Secondary Text:  #666666 (Gray)
Muted Text:      #AAAAAA (Light Gray)
Inverse Text:    #FFFFFF on dark backgrounds
```

**Borders:**
```
Default Border:  #DDDDDD
Focus Border:    #4A90E2 (Primary)
Error Border:    #E74C3C
```

### Accessibility Requirements

**Contrast Ratios (WCAG 2.1 AA):**
- Normal text (18px): 4.5:1 minimum
- Large text (24px+): 3:1 minimum
- Interactive elements: 3:1 minimum

**Tested Combinations:**
- #1A1A1A on #FFFFFF: 16.9:1 ✓
- #4A90E2 on #FFFFFF: 3.4:1 (use for large text only)
- #FFFFFF on #4A90E2: 4.5:1 ✓

**Never Rely on Color Alone:**
- Status: Color + icon + text ("✓ Completed")
- Categories: Color + label ("Art Movements")

---

## Typography

### Font Families

**Primary Font (UI):**
```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
```

**Secondary Font (Headings - Optional):**
```css
font-family: 'Poppins', 'Inter', sans-serif;
```

**Monospace (Code/IDs):**
```css
font-family: 'Fira Code', 'Courier New', monospace;
```

### Type Scale

**Modular Scale (1.250 - Major Third):**

```
h1: 48px / 3rem     (Page titles)
h2: 38px / 2.4rem   (Section headers)
h3: 30px / 1.9rem   (Subsection headers)
h4: 24px / 1.5rem   (Card headers)
h5: 19px / 1.2rem   (Small headers)
Body: 16px / 1rem   (Base size)
Small: 13px / 0.8rem (Metadata, captions)
```

### Font Weights

```
Regular: 400  (Body text)
Medium:  500  (Emphasis)
Semibold:600  (Headings)
Bold:    700  (Strong emphasis)
```

### Line Heights

```
Tight:   1.2  (Headings)
Normal:  1.5  (Body text)
Relaxed: 1.75 (Long-form content)
```

### Usage Examples

**Config Card Title:**
```css
font-size: 24px;
font-weight: 600;
line-height: 1.2;
color: #1A1A1A;
```

**Stage Box Status:**
```css
font-size: 19px;
font-weight: 500;
line-height: 1.5;
color: #333333;
```

**Metadata Label:**
```css
font-size: 13px;
font-weight: 400;
line-height: 1.5;
color: #666666;
```

---

## Spacing System

### Base Unit: 8px

**Scale (Multiples of 8):**
```
xs:   4px  (0.25rem)
sm:   8px  (0.5rem)
md:   16px (1rem)
lg:   24px (1.5rem)
xl:   32px (2rem)
2xl:  48px (3rem)
3xl:  64px (4rem)
```

### Component Spacing

**Config Card (Tile):**
```
Padding:        24px (lg)
Gap (between):  16px (md)
Margin (grid):  16px (md)
```

**Stage Box:**
```
Padding:        16px (md)
Gap (sections): 12px
Margin (flow):  24px (lg)
```

**Modal:**
```
Padding (content): 32px (xl)
Padding (mobile):  16px (md)
Gap (sections):    24px (lg)
```

### Layout Grids

**Phase 1 Tile Grid:**
```
Desktop (1920px+): 4 columns, 16px gap
Laptop (1280px+):  3 columns, 16px gap
Tablet (768px+):   2 columns, 16px gap
Mobile (<768px):   1 column
```

**Container Widths:**
```
Max Width:    1400px (centered)
Padding:      32px (xl) on desktop
              16px (md) on mobile
```

---

## Component Styles

### Config Card (Tile View)

**Dimensions:**
```
Width:  280px (fluid within grid)
Height: 360px (fixed)
```

**Structure:**
```
┌─────────────────────────┐
│  [Category Badge]       │  ← 8px padding
│                         │
│       [Icon]            │  ← 80x80px, centered
│                         │
│   Config Name           │  ← 24px font, 600 weight
│   Short description...  │  ← 16px font, 400 weight, gray
│                         │
│   ⭐⭐⭐☆☆            │  ← Difficulty (16px)
│                         │
│   [Output Badges]       │  ← Small pills
│                         │
│   [Select Button]       │  ← Full-width, primary
└─────────────────────────┘
```

**Styling:**
```css
.config-card {
  background: #FFFFFF;
  border: 1px solid #DDDDDD;
  border-radius: 12px;
  padding: 24px;
  transition: all 0.2s ease;
  cursor: pointer;
}

.config-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  transform: translateY(-4px);
  border-color: #4A90E2;
}

.config-card:focus {
  outline: 2px solid #4A90E2;
  outline-offset: 2px;
}

.config-card.user-config {
  border-left: 4px solid #1ABC9C;
}
```

**Category Badge:**
```css
.category-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 13px;
  font-weight: 500;
  background: rgba(74, 144, 226, 0.1);
  color: #4A90E2;
}
```

---

### Stage Box (Phase 2+3)

**Dimensions:**
```
Width:  200px
Height: 250px (flexible based on content)
```

**Structure:**
```
┌─────────────────────┐
│  Stage 2            │  ← Header (dark bg)
│  Interception       │
├─────────────────────┤
│                     │
│        ⟳            │  ← Status icon (48px)
│                     │
│  Iteration 5/8      │  ← Status text
│  ████████▒▒▒▒▒▒    │  ← Progress bar
│  ~15s remaining     │  ← Time estimate
│                     │
├─────────────────────┤
│ [Expand Details ▼]  │  ← Footer action
└─────────────────────┘
```

**Styling (Pending State):**
```css
.stage-box.pending {
  background: #F5F5F5;
  border: 2px solid #DDDDDD;
  opacity: 0.7;
}

.stage-box.pending .status-icon {
  color: #CCCCCC;
  font-size: 48px;
}
```

**Styling (In Progress State):**
```css
.stage-box.in-progress {
  background: #FFFFFF;
  border: 2px solid #F39C12;
  box-shadow: 0 4px 16px rgba(243, 156, 18, 0.3);
}

.stage-box.in-progress .status-icon {
  color: #F39C12;
  font-size: 48px;
  animation: spin 2s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
```

**Styling (Completed State):**
```css
.stage-box.completed {
  background: rgba(39, 174, 96, 0.05);
  border: 2px solid #27AE60;
}

.stage-box.completed .status-icon {
  color: #27AE60;
  font-size: 48px;
}
```

---

### Connection Lines (Phase 2+3)

**SVG Arrow:**
```html
<svg width="80" height="40" viewBox="0 0 80 40">
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7"
            refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#666666" />
    </marker>
  </defs>

  <line x1="0" y1="20" x2="70" y2="20"
        stroke="#666666" stroke-width="2"
        marker-end="url(#arrowhead)" />
</svg>
```

**States:**

**Inactive (Gray, Dashed):**
```css
.connection-line.inactive line {
  stroke: #CCCCCC;
  stroke-dasharray: 5, 5;
}
```

**Active (Orange, Animated):**
```css
.connection-line.active line {
  stroke: #F39C12;
  stroke-width: 3;
  stroke-dasharray: 10, 5;
  animation: flow 1s linear infinite;
}

@keyframes flow {
  from { stroke-dashoffset: 0; }
  to { stroke-dashoffset: 15; }
}
```

**Completed (Green, Solid):**
```css
.connection-line.completed line {
  stroke: #27AE60;
  stroke-width: 2;
}
```

---

### Buttons

**Primary Button:**
```css
.button-primary {
  background: #4A90E2;
  color: #FFFFFF;
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
}

.button-primary:hover {
  background: #357ABD;
}

.button-primary:focus {
  outline: 2px solid #4A90E2;
  outline-offset: 2px;
}

.button-primary:disabled {
  background: #CCCCCC;
  cursor: not-allowed;
}
```

**Secondary Button:**
```css
.button-secondary {
  background: transparent;
  color: #4A90E2;
  border: 2px solid #4A90E2;
  border-radius: 8px;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.button-secondary:hover {
  background: #4A90E2;
  color: #FFFFFF;
}
```

**Danger Button:**
```css
.button-danger {
  background: #E74C3C;
  color: #FFFFFF;
  /* ... same structure as primary ... */
}
```

---

### Modals

**Overlay:**
```css
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
```

**Modal Content:**
```css
.modal-content {
  background: #FFFFFF;
  border-radius: 16px;
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.3);
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

---

## DX7-Inspired Flowchart Symbolization

### Concept

The Yamaha DX7 synthesizer used **algorithm diagrams** to show how operators (sound generators) connect. We adapt this for showing pipeline structure in config icons/cards.

**Goals:**
- Visual differentiation between config types
- Immediate understanding of complexity
- Auxiliary symbolization (not primary navigation)

### Flowchart Types

#### 1. Linear Flow

**Use Case:** Simple transformations (translation, passthrough)

**Visual:**
```
 ┌───┐    ┌───┐    ┌───┐
 │ I │ → │ T │ → │ O │
 └───┘    └───┘    └───┘
  Input   Transform Output
```

**SVG Implementation:**
```html
<svg width="120" height="40" viewBox="0 0 120 40">
  <!-- Input Box -->
  <rect x="0" y="10" width="30" height="20" fill="#4A90E2" />
  <text x="15" y="24" fill="#FFF" font-size="12" text-anchor="middle">I</text>

  <!-- Arrow -->
  <line x1="30" y1="20" x2="45" y2="20" stroke="#666" stroke-width="2" marker-end="url(#arrow)" />

  <!-- Transform Box -->
  <rect x="45" y="10" width="30" height="20" fill="#F39C12" />
  <text x="60" y="24" fill="#FFF" font-size="12" text-anchor="middle">T</text>

  <!-- Arrow -->
  <line x1="75" y1="20" x2="90" y2="20" stroke="#666" stroke-width="2" marker-end="url(#arrow)" />

  <!-- Output Box -->
  <rect x="90" y="10" width="30" height="20" fill="#27AE60" />
  <text x="105" y="24" fill="#FFF" font-size="12" text-anchor="middle">O</text>
</svg>
```

---

#### 2. Recursive Loop

**Use Case:** Iterative transformations (Stillepost 8 iterations)

**Visual:**
```
       ┌──┐
       │  │←┐
 I →──┤ T│─┘ (8×)
       └──┘
        ↓
        O
```

**SVG Implementation:**
```html
<svg width="100" height="100" viewBox="0 0 100 100">
  <!-- Input -->
  <circle cx="20" cy="50" r="10" fill="#4A90E2" />
  <text x="20" y="54" fill="#FFF" font-size="10" text-anchor="middle">I</text>

  <!-- Arrow to Transform -->
  <line x1="30" y1="50" x2="40" y2="50" stroke="#666" stroke-width="2" marker-end="url(#arrow)" />

  <!-- Transform Box -->
  <rect x="40" y="35" width="30" height="30" fill="#F39C12" />
  <text x="55" y="54" fill="#FFF" font-size="12" text-anchor="middle">T</text>

  <!-- Loop Back Arrow -->
  <path d="M 70 40 Q 80 30, 80 50 Q 80 70, 70 60" stroke="#666" stroke-width="2" fill="none" marker-end="url(#arrow)" />

  <!-- 8× Label -->
  <text x="85" y="50" fill="#666" font-size="10">8×</text>

  <!-- Arrow to Output -->
  <line x1="55" y1="65" x2="55" y2="80" stroke="#666" stroke-width="2" marker-end="url(#arrow)" />

  <!-- Output -->
  <circle cx="55" cy="90" r="10" fill="#27AE60" />
  <text x="55" y="94" fill="#FFF" font-size="10" text-anchor="middle">O</text>
</svg>
```

---

#### 3. Branching (Parallel Paths)

**Use Case:** Split & Combine configs

**Visual:**
```
       ┌─→ A ─┐
 I ───┤       ├→ O
       └─→ B ─┘
```

**SVG Implementation:**
```html
<svg width="150" height="80" viewBox="0 0 150 80">
  <!-- Input -->
  <circle cx="20" cy="40" r="10" fill="#4A90E2" />
  <text x="20" y="44" fill="#FFF" font-size="10" text-anchor="middle">I</text>

  <!-- Fork Point -->
  <circle cx="50" cy="40" r="3" fill="#666" />

  <!-- Branch to A -->
  <line x1="30" y1="40" x2="50" y2="40" stroke="#666" stroke-width="2" />
  <line x1="50" y1="40" x2="70" y2="20" stroke="#666" stroke-width="2" marker-end="url(#arrow)" />

  <!-- Branch to B -->
  <line x1="50" y1="40" x2="70" y2="60" stroke="#666" stroke-width="2" marker-end="url(#arrow)" />

  <!-- Transform A -->
  <rect x="70" y="10" width="25" height="20" fill="#F39C12" />
  <text x="82" y="24" fill="#FFF" font-size="10" text-anchor="middle">A</text>

  <!-- Transform B -->
  <rect x="70" y="50" width="25" height="20" fill="#F39C12" />
  <text x="82" y="64" fill="#FFF" font-size="10" text-anchor="middle">B</text>

  <!-- Join Point -->
  <circle cx="110" cy="40" r="3" fill="#666" />

  <!-- Join from A -->
  <line x1="95" y1="20" x2="110" y2="40" stroke="#666" stroke-width="2" />

  <!-- Join from B -->
  <line x1="95" y1="60" x2="110" y2="40" stroke="#666" stroke-width="2" />

  <!-- Arrow to Output -->
  <line x1="110" y1="40" x2="125" y2="40" stroke="#666" stroke-width="2" marker-end="url(#arrow)" />

  <!-- Output -->
  <circle cx="135" cy="40" r="10" fill="#27AE60" />
  <text x="135" y="44" fill="#FFF" font-size="10" text-anchor="middle">O</text>
</svg>
```

---

#### 4. Complex (Custom SVG)

**Use Case:** Multi-stage with sub-branches

For complex configs, designer creates custom SVG and includes path in metadata:

```json
{
  "flowchart": {
    "type": "complex",
    "svg_path": "/assets/flowcharts/quantum_theory.svg"
  }
}
```

---

### Integration in Phase 1

**Option 1: Overlay on Icon**
```html
<div class="config-card">
  <div class="card-icon">
    <span class="emoji-icon">🎨</span>
    <svg class="flowchart-overlay">
      <!-- Small flowchart (40x40px) -->
    </svg>
  </div>
  ...
</div>
```

**Option 2: Replace Icon**
```html
<div class="config-card">
  <div class="card-icon">
    <svg class="flowchart-icon" width="80" height="80">
      <!-- Flowchart as primary icon -->
    </svg>
  </div>
  ...
</div>
```

**Recommendation:** Option 1 (overlay) for Phase 1 tiles, Option 2 (replace) for Phase 2+3 header

---

### Programmatic Generation

**Vue Component: FlowchartIcon.vue**

```vue
<template>
  <svg :width="size" :height="size" :viewBox="`0 0 ${size} ${size}`">
    <defs>
      <marker id="arrow" markerWidth="10" markerHeight="7"
              refX="9" refY="3.5" orient="auto">
        <polygon points="0 0, 10 3.5, 0 7" :fill="arrowColor" />
      </marker>
    </defs>

    <component :is="flowchartComponent" :config="config" :size="size" />
  </svg>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import LinearFlowchart from './flowcharts/LinearFlowchart.vue';
import RecursiveFlowchart from './flowcharts/RecursiveFlowchart.vue';
import BranchingFlowchart from './flowcharts/BranchingFlowchart.vue';

const props = defineProps<{
  config: Config
  size?: number
}>();

const size = props.size || 80;

const flowchartComponent = computed(() => {
  const type = props.config.flowchart?.type || 'linear';

  switch (type) {
    case 'linear': return LinearFlowchart;
    case 'recursive': return RecursiveFlowchart;
    case 'branching': return BranchingFlowchart;
    default: return LinearFlowchart;
  }
});

const arrowColor = '#666666';
</script>
```

---

## Icons & Illustrations

### Icon System

**Preferred:** Emoji (built-in, universal, accessible)

**Fallback:** SVG icons from icon library

**Libraries to Consider:**
- [Lucide Icons](https://lucide.dev/) - Clean, consistent
- [Heroicons](https://heroicons.com/) - Tailwind-compatible
- [Phosphor Icons](https://phosphoricons.com/) - Playful

### Icon Sizes

```
xs: 16px  (Inline with text)
sm: 24px  (Buttons, small UI)
md: 32px  (Cards, prominent)
lg: 48px  (Stage status icons)
xl: 80px  (Config card main icon)
```

### Status Icons

**Mapping:**
```
Pending:     ○  (Circle outline)
In Progress: ⟳  (Rotating arrows)
Completed:   ✓  (Checkmark)
Error:       ✗  (X mark)
Warning:     ⚠️  (Warning triangle)
```

**Alternative (SVG Icons):**
- Pending: Spinner icon (static)
- In Progress: Spinner icon (animated)
- Completed: Check circle icon
- Error: X circle icon

---

## Animation Guidelines

### Micro-Interactions

**Hover Transitions:**
```css
transition: all 0.2s ease;
```

**Focus Indicators:**
```css
transition: outline 0.1s ease;
```

**Modal Entrance:**
```css
animation: slideUp 0.3s ease;
```

### Loading States

**Spinner (In-Progress Stages):**
```css
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.spinner {
  animation: spin 2s linear infinite;
}
```

**Pulsing (Active Elements):**
```css
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.stage-box.in-progress {
  animation: pulse 2s ease-in-out infinite;
}
```

**Flowing Data (Connection Lines):**
```css
@keyframes flow {
  from { stroke-dashoffset: 0; }
  to { stroke-dashoffset: 15; }
}

.connection-line.active line {
  stroke-dasharray: 10, 5;
  animation: flow 1s linear infinite;
}
```

### Performance Considerations

**Use `transform` and `opacity` only for animations (GPU-accelerated):**
```css
/* Good */
.card:hover {
  transform: translateY(-4px);
  opacity: 0.9;
}

/* Bad (causes reflow) */
.card:hover {
  top: -4px;
  margin-top: 10px;
}
```

**Respect `prefers-reduced-motion`:**
```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Responsive Design Patterns

### Breakpoints

```css
/* Mobile First Approach */
/* Base styles: Mobile (< 768px) */

@media (min-width: 768px) {
  /* Tablet */
}

@media (min-width: 1024px) {
  /* Laptop */
}

@media (min-width: 1280px) {
  /* Desktop */
}

@media (min-width: 1920px) {
  /* Large Desktop */
}
```

### Phase 1 Responsive Behavior

**Tile Grid:**
```css
.tile-grid {
  display: grid;
  gap: 16px;

  /* Mobile: 1 column */
  grid-template-columns: 1fr;

  /* Tablet: 2 columns */
  @media (min-width: 768px) {
    grid-template-columns: repeat(2, 1fr);
  }

  /* Laptop: 3 columns */
  @media (min-width: 1024px) {
    grid-template-columns: repeat(3, 1fr);
  }

  /* Desktop: 4 columns */
  @media (min-width: 1280px) {
    grid-template-columns: repeat(4, 1fr);
  }
}
```

### Phase 2+3 Responsive Behavior

**Stage Flow:**
```css
.stage-flow {
  display: flex;

  /* Desktop: Horizontal */
  @media (min-width: 1024px) {
    flex-direction: row;
    align-items: center;
    gap: 24px;
  }

  /* Mobile/Tablet: Vertical */
  @media (max-width: 1023px) {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }
}
```

---

## Dark Mode Considerations (Future)

**Color Palette (Dark Mode):**
```
Background:       #1A1A1A
Card Background:  #2A2A2A
Text:             #FFFFFF
Muted Text:       #AAAAAA
Border:           #444444
```

**Implementation Strategy:**
```css
/* CSS Variables */
:root {
  --bg-primary: #FFFFFF;
  --bg-secondary: #F5F5F5;
  --text-primary: #1A1A1A;
  --text-secondary: #666666;
  --border-color: #DDDDDD;
}

[data-theme="dark"] {
  --bg-primary: #1A1A1A;
  --bg-secondary: #2A2A2A;
  --text-primary: #FFFFFF;
  --text-secondary: #AAAAAA;
  --border-color: #444444;
}

body {
  background: var(--bg-primary);
  color: var(--text-primary);
}
```

---

## Accessibility Patterns

### Focus Indicators

**Visible focus outlines on all interactive elements:**
```css
button:focus,
a:focus,
input:focus,
.config-card:focus {
  outline: 2px solid #4A90E2;
  outline-offset: 2px;
}
```

### Screen Reader Text

**Visually hidden but accessible to screen readers:**
```css
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
```

**Usage:**
```html
<button>
  <span class="icon">⟳</span>
  <span class="sr-only">Pipeline in progress, iteration 5 of 8</span>
</button>
```

### ARIA Live Regions

**Announce status changes:**
```html
<div role="status" aria-live="polite" aria-atomic="true" class="sr-only">
  {{ currentStatusMessage }}
</div>
```

**Example in Vue:**
```vue
<template>
  <div role="status" aria-live="polite" class="sr-only">
    {{ ariaStatusMessage }}
  </div>
</template>

<script setup>
const ariaStatusMessage = computed(() => {
  if (stage.status === 'in_progress') {
    return `Stage ${stage.number} in progress: ${stage.step}`;
  } else if (stage.status === 'completed') {
    return `Stage ${stage.number} completed in ${stage.time} seconds`;
  }
  return '';
});
</script>
```

---

## Wireframes

### Phase 1: Tile View (Desktop)

```
┌─────────────────────────────────────────────────────────────────┐
│  [🔲 Tiles] [📋 List] [🤖 AI]     🔍 Search...   [🔽 Filter]  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ════════════════════════════════════════                       │
│    ART MOVEMENTS (8)                                            │
│  ════════════════════════════════════════                       │
│                                                                 │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐          │
│  │  🎨     │  │  🏛️     │  │  🎭     │  │  🖼️     │          │
│  │         │  │         │  │         │  │         │          │
│  │  Dada   │  │ Bauhaus │  │Surreal  │  │ Expres. │          │
│  │         │  │         │  │         │  │         │          │
│  │⭐⭐⭐   │  │⭐⭐     │  │⭐⭐⭐   │  │⭐⭐⭐   │          │
│  │[Select] │  │[Select] │  │[Select] │  │[Select] │          │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘          │
│                                                                 │
│  ════════════════════════════════════════                       │
│    MEDIA GENERATION (6)                                         │
│  ════════════════════════════════════════                       │
│                                                                 │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐          │
│  │  📷     │  │  🔊     │  │  🎵     │  │  🎬     │          │
│  │         │  │         │  │         │  │         │          │
│  │ SD3.5   │  │ Stable  │  │   ACE   │  │ Video   │          │
│  │ Large   │  │  Audio  │  │  Step   │  │  Gen    │          │
│  │⭐⭐⭐⭐  │  │⭐⭐⭐⭐  │  │⭐⭐⭐⭐  │  │⭐⭐⭐⭐⭐ │          │
│  │[Select] │  │[Select] │  │[Select] │  │[Select] │          │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Phase 2+3: Pipeline Flow (Desktop)

```
┌─────────────────────────────────────────────────────────────────┐
│  ← Back     Config: Dada Transform │ Status: Running │ 00:23   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Your Prompt: "A beautiful flower in a sunny meadow"           │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐             │
│  │ Stage 1  │      │ Stage 2  │      │ Stage 3  │             │
│  │  Pre     │  →   │ Intercep │  →   │  Safety  │             │
│  │          │      │          │      │          │             │
│  │    ✓     │      │    ⟳     │      │    ○     │             │
│  │Completed │      │  3/8     │      │ Pending  │             │
│  └──────────┘      └──────────┘      └──────────┘             │
│                                                                 │
│                                ┌──────────┐                    │
│                                │ Stage 4  │                    │
│                            →   │  Media   │                    │
│                                │          │                    │
│                                │    ○     │                    │
│                                │ Pending  │                    │
│                                └──────────┘                    │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  Timeline:                                                      │
│  ✓ 01 • Input          [View]                                  │
│  ✓ 02 • Translation    [View]                                  │
│  ✓ 03 • Safety Check   [View]                                  │
│  ⟳ 04 • Interception   [View Progress]                         │
│  ○ 05 • Final Safety   [Waiting...]                            │
│  ○ 06 • Output Image   [Waiting...]                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## CSS Architecture

### Recommended Structure

**Using Vue Single-File Components (SFCs):**

```
/assets/styles/
├── main.css               # Global styles, CSS reset
├── variables.css          # CSS custom properties
├── typography.css         # Font definitions, type scale
├── utilities.css          # Utility classes (.mt-4, .flex, etc.)
├── phase1.css             # Phase 1 specific styles
└── phase2_3.css           # Phase 2+3 specific styles
```

**Scoped Component Styles:**
```vue
<template>
  <div class="config-card">...</div>
</template>

<style scoped>
.config-card {
  /* Component-specific styles */
  /* Scoped to this component only */
}
</style>
```

### CSS Methodology

**BEM (Block Element Modifier):**
```css
/* Block */
.config-card { }

/* Element */
.config-card__icon { }
.config-card__title { }
.config-card__button { }

/* Modifier */
.config-card--user { }
.config-card--selected { }
```

---

## Related Documentation

- `FRONTEND_ARCHITECTURE_OVERVIEW.md` - Overall architecture
- `PHASE_1_SCHEMA_SELECTION.md` - Phase 1 component specs
- `PHASE_2_3_FLOW_EXPERIENCE.md` - Phase 2+3 component specs
- `VUE_COMPONENT_ARCHITECTURE.md` - Component structure

---

**Document Status:** ✅ Complete
**Next Steps:** Begin implementation with design mockups
**Design Tools:** Figma, Sketch, Adobe XD recommended
**Last Updated:** 2025-11-06
