# Phase 1: Schema Selection Interface

**Version:** 1.0
**Date:** 2025-11-06
**Status:** Planning Document
**Parent:** FRONTEND_ARCHITECTURE_OVERVIEW.md

---

## Executive Summary

Phase 1 is the **dispositional pre-decision interface** where users discover and select schema-configs before entering the pipeline execution flow. Unlike Phase 2+3 which follows pipeline execution logic, Phase 1 follows **browsing and discovery logic** designed to help users find the right creative transformation approach.

### Key Innovation

**Three Full-Screen Visualization Modes** switchable via icons, each filling the entire screen with different organizational logic:

- **Mode A: Arranged Tiles** - Visual, card-based grid with icons and metadata
- **Mode B: List View** - Compact, table-based display for quick scanning
- **Mode C: LLM-Assisted Dialog** - Conversational interface for guided selection

---

## Design Philosophy

### Why Three Modes?

Different users have different mental models for discovery:

**Visual Thinkers (Mode A):**
- Browse by appearance, icon, visual symbolization
- Recognize patterns through spatial arrangement
- "I'll know it when I see it"

**Analytical Thinkers (Mode B):**
- Scan textual descriptions efficiently
- Sort/filter by attributes
- "I need to compare specifications"

**Exploratory Users (Mode C):**
- Uncertain what they need
- Benefit from guided questioning
- "Help me figure out what I want"

**All modes lead to same outcome:** Selected config + execution parameters

---

## Mode A: Arranged Tiles

### Visual Appearance

```
┌────────────────────────────────────────────────────────────┐
│  [Tile Icon] [List Icon] [LLM Icon]  🔍 Search  [Filter]  │  ← Mode Switcher Bar
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ╔═══════════════╗  ╔═══════════════╗  ╔═══════════════╗  │
│  ║     🎨        ║  ║     🏛️        ║  ║     🔊        ║  │
│  ║               ║  ║               ║  ║               ║  │
│  ║     Dada      ║  ║  Bauhaus      ║  ║  Sound Gen    ║  │
│  ║ Transformation║  ║  Composition  ║  ║   (SD Audio)  ║  │
│  ║               ║  ║               ║  ║               ║  │
│  ║ ⭐⭐⭐        ║  ║ ⭐⭐          ║  ║ ⭐⭐⭐⭐      ║  │
│  ║ [Select]      ║  ║ [Select]      ║  ║ [Select]      ║  │
│  ╚═══════════════╝  ╚═══════════════╝  ╚═══════════════╝  │
│                                                            │
│  ╔═══════════════╗  ╔═══════════════╗  ╔═══════════════╗  │
│  ║  [Flow Icon]  ║  ║     📝        ║  ║     🎭        ║  │
│  ║   ┌→┐         ║  ║               ║  ║               ║  │
│  ║   │ │→        ║  ║  Translation  ║  ║  Surrealism   ║  │
│  ║   └→┘         ║  ║   (EN→DE)     ║  ║ Transformation║  │
│  ║ Stillepost    ║  ║               ║  ║               ║  │
│  ║ ⭐⭐⭐        ║  ║ ⭐            ║  ║ ⭐⭐⭐        ║  │
│  ║ [Select]      ║  ║ [Select]      ║  ║ [Select]      ║  │
│  ╚═══════════════╝  ╚═══════════════╝  ╚═══════════════╝  │
│                                                            │
│                    [...more tiles...]                      │
└────────────────────────────────────────────────────────────┘
```

### Card Structure

Each tile displays:

```
┌─────────────────────┐
│   [Category Badge]  │  ← Color-coded category tag
│                     │
│    [Icon/Symbol]    │  ← Large, distinctive icon
│                     │     (DX7-style flowchart if applicable)
│                     │
│   Config Name       │  ← Clear, concise name
│   Short Description │  ← One-line summary
│                     │
│   ⭐⭐⭐☆☆        │  ← Difficulty rating (1-5 stars)
│                     │
│   [Pipeline Badge]  │  ← Pipeline type indicator
│   [Output Badge]    │  ← Output type (text/image/audio)
│                     │
│   [USER] (if user)  │  ← User config indicator
│                     │
│   [Select Button]   │  ← Primary action
└─────────────────────┘
```

### Grouping Strategy

**Default Grouping: By Category**

Categories displayed as sections with headers:

```
════════════════════════════════════════
  ART MOVEMENTS (8 configs)
════════════════════════════════════════
[Dada]  [Bauhaus]  [Expressionism]  [Surrealism] ...

════════════════════════════════════════
  MEDIA GENERATION (6 configs)
════════════════════════════════════════
[SD3.5 Large]  [GPT-5 Image]  [Stable Audio] ...

════════════════════════════════════════
  TEXT TRANSFORMATION (12 configs)
════════════════════════════════════════
[Stillepost]  [Translation]  [Jugendsprache] ...

════════════════════════════════════════
  MY CONFIGS (User) (3 configs)
════════════════════════════════════════
[Custom Flow]  [Experimental Mix]  [Test Config] ...
```

**Alternative Groupings** (user-selectable):
- By Pipeline Type (text_transformation, media_generation, etc.)
- By Output Type (text, image, audio, video)
- By Difficulty (beginner, intermediate, advanced, expert)
- Alphabetical
- Recently Used

### DX7-Style Flowchart Icons

**Purpose:** Auxiliary symbolization showing pipeline structure

**Application:** Small stylized flowchart overlaid on or replacing standard icon

**Example: Stillepost (8-iteration recursive loop)**
```
Config Card for "Stillepost":

┌─────────────────────┐
│   TEXT TRANSFORM    │
│                     │
│      ┌──┐           │
│      │  │←┐         │  ← Shows recursive loop
│  ┌→──┤  │─┘         │     (8 iterations)
│  │   └──┘           │
│  └─────→ Output     │
│                     │
│   Stillepost        │
│   8-stage echo      │
│   ⭐⭐⭐          │
│   [Select]          │
└─────────────────────┘
```

**Example: Linear Flow (Translation)**
```
Config Card for "Translation":

┌─────────────────────┐
│   TEXT TRANSFORM    │
│                     │
│   Input → [T] → Out │  ← Simple linear flow
│                     │
│   Translation       │
│   German → English  │
│   ⭐              │
│   [Select]          │
└─────────────────────┘
```

**Example: Branching (Split & Combine)**
```
Config Card for "Split & Combine":

┌─────────────────────┐
│   TEXT TRANSFORM    │
│                     │
│      ┌─→ [A] ─┐     │  ← Shows parallel paths
│  In─→┤         ├→Out │     that recombine
│      └─→ [B] ─┘     │
│                     │
│   Split & Combine   │
│   Spherical blend   │
│   ⭐⭐⭐⭐        │
│   [Select]          │
└─────────────────────┘
```

**Design Constraints:**
- Icons must be recognizable at small size (150x150px)
- Maximum 3-4 boxes/nodes (avoid complexity)
- Clear directionality (arrows)
- Consistent visual style across all flowcharts

### Interaction Design

**Hover State:**
- Tile elevates (box-shadow)
- Description expands to full text
- Preview animation (if applicable)

**Click/Select:**
- Tile highlights with border
- Modal/drawer opens with:
  - Full config description
  - Example inputs/outputs
  - Execution parameters (eco/fast, safety level)
  - [Confirm Selection] button

**Keyboard Navigation:**
- Arrow keys move focus between tiles
- Enter opens selection modal
- Escape closes modal
- Tab/Shift+Tab for sequential navigation

### Search & Filter

**Search Bar (Top):**
- Real-time filtering by name, description, tags
- Highlights matching text in cards
- Shows match count: "8 configs match 'audio'"

**Filter Panel (Side or Dropdown):**
```
Filters:
☐ Text Output
☐ Image Output
☐ Audio Output
☐ Video Output

Pipeline Type:
☐ Text Transformation
☐ Media Generation
☐ Dual-Input

Difficulty:
☐ ⭐ Easy
☐ ⭐⭐ Medium
☐ ⭐⭐⭐ Advanced
☐ ⭐⭐⭐⭐ Expert

Source:
☐ System Configs
☑ User Configs

[Reset Filters]
```

### Responsive Layout

**Desktop (1920px+):**
- 4 tiles per row
- Large icons (150x150px)
- Full descriptions visible

**Laptop (1280px+):**
- 3 tiles per row
- Medium icons (120x120px)
- Truncated descriptions (expand on hover)

**Tablet (768px+):**
- 2 tiles per row
- Medium icons (120x120px)
- Truncated descriptions

---

## Mode B: List View

### Visual Appearance

```
┌──────────────────────────────────────────────────────────────────────┐
│  [Tile Icon] [List Icon] [LLM Icon]  🔍 Search  [Filter]  [Sort ▼]  │
├──────────────────────────────────────────────────────────────────────┤
│ Icon │ Name              │ Category       │ Output │ Difficulty │    │
├──────┼───────────────────┼────────────────┼────────┼────────────┼────┤
│  🎨  │ Dada Transform    │ Art Movements  │ Text   │ ⭐⭐⭐    │ → │
│  🏛️  │ Bauhaus Comp      │ Art Movements  │ Text   │ ⭐⭐      │ → │
│  🔊  │ Stable Audio      │ Media Gen      │ Audio  │ ⭐⭐⭐⭐  │ → │
│  📝  │ Translation EN    │ Text Transform │ Text   │ ⭐        │ → │
│  🎭  │ Surrealism        │ Art Movements  │ Text   │ ⭐⭐⭐    │ → │
│  ┌→┐ │ Stillepost        │ Text Transform │ Text   │ ⭐⭐⭐    │ → │
│  📷  │ SD3.5 Large       │ Media Gen      │ Image  │ ⭐⭐⭐⭐  │ → │
│  🎵  │ ACE Step Music    │ Media Gen      │ Music  │ ⭐⭐⭐⭐  │ → │
│  👤  │ My Custom Flow    │ User Config    │ Text   │ ⭐⭐      │ → │
│      │                   │                │        │            │    │
│                         [...more rows...]                            │
└──────────────────────────────────────────────────────────────────────┘
```

### Column Structure

**Essential Columns:**

1. **Icon** (40px) - Visual identifier
2. **Name** (200px) - Config name
3. **Description** (300px, truncated) - Brief summary
4. **Category** (150px) - Config category
5. **Output Type** (80px) - Text/Image/Audio/Video badge
6. **Difficulty** (100px) - Star rating
7. **Action** (40px) - Arrow/select button

**Optional Columns** (user-configurable):

8. **Pipeline Type** (150px) - text_transformation, etc.
9. **Input Type** (100px) - Text/Image/Dual
10. **Tags** (150px) - Comma-separated tags
11. **Last Modified** (120px) - Date (for user configs)

### Sorting Options

**Default Sort:** Category → Difficulty → Name

**User Sortable By:**
- Name (A-Z, Z-A)
- Category (grouped)
- Difficulty (easy first, hard first)
- Output Type (grouped)
- Recently Used (most recent first)
- Date Added (newest/oldest)

**Sort Indicator:**
- Column header with ▲▼ arrows
- Current sort highlighted

### Interaction Design

**Row Hover:**
- Background highlight
- Full description tooltip appears
- Action button becomes visible

**Row Click:**
- Selects row (highlight)
- Details panel slides from right (or modal)
- Shows full config info + execution parameters

**Double-Click:**
- Immediately opens config in Phase 2+3 with default parameters

**Keyboard Navigation:**
- Up/Down arrow keys navigate rows
- Enter selects/opens details
- Space toggles selection
- Home/End jump to first/last

### Details Panel

When row is clicked, right-side panel appears:

```
┌─────────────────────────────────────┐
│  [X Close]                          │
│                                     │
│  🎨 Dada Transformation             │
│  ═══════════════════════════════════│
│                                     │
│  Category: Art Movements            │
│  Pipeline: text_transformation      │
│  Output: Text                       │
│  Difficulty: ⭐⭐⭐               │
│                                     │
│  Description:                       │
│  Transforms input text using Dada   │
│  art movement principles, creating  │
│  nonsensical and unexpected word    │
│  combinations that challenge        │
│  conventional meaning.              │
│                                     │
│  Example Input:                     │
│  "A flower in the meadow"           │
│                                     │
│  Example Output:                    │
│  "Meadow-flower-chaos umbrella!"    │
│                                     │
│  ─────────────────────────────────  │
│                                     │
│  Execution Mode:                    │
│  ○ Eco (slower, local LLM)          │
│  ● Fast (faster, cloud API)         │
│                                     │
│  Safety Level:                      │
│  ● Kids (strict filtering)          │
│  ○ Youth (moderate filtering)       │
│                                     │
│  [Select & Continue to Phase 2+3]   │
└─────────────────────────────────────┘
```

### Compact Mode

**Ultra-Compact List** (for 100+ configs):
- Smaller row height (40px vs 60px)
- Icon + Name + Output badge only
- Expand on click for full details
- Virtual scrolling for performance

---

## Mode C: LLM-Assisted Selection Dialog

### Visual Appearance

```
┌──────────────────────────────────────────────────────────────┐
│  [Tile Icon] [List Icon] [LLM Icon]  🔍 Direct Search        │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│                    🤖 AI Assistant                           │
│                                                              │
│  Let me help you find the right creative transformation!    │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Assistant: What would you like to create today?        │ │
│  │            • Transform text in an artistic way?        │ │
│  │            • Generate an image?                        │ │
│  │            • Create audio or music?                    │ │
│  │            • Something experimental?                   │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ You: I want to transform text in a creative way       │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Assistant: Great! Do you have a specific art style    │ │
│  │            in mind, or would you like me to suggest   │ │
│  │            something unexpected and experimental?     │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ [Type your response here...]                 [Send →] │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  Or skip the conversation:                                  │
│  [Show me all options]  [I'm feeling lucky]                │
└──────────────────────────────────────────────────────────────┘
```

### Conversational Flow

**Step 1: Intent Discovery**

Assistant asks: "What would you like to create today?"

**User Response Examples:**
- "I want to generate an image"
- "Transform my text into something weird"
- "Create background music for a video"
- "Something educational for kids"

**Step 2: Refinement Questions**

Based on intent, ask follow-up questions:

**For Text Transformation:**
- "Do you prefer established art styles (Dada, Bauhaus) or experimental approaches?"
- "Should it maintain meaning or prioritize creativity?"
- "Is this for education, entertainment, or experimentation?"

**For Media Generation:**
- "What kind of image/audio/music?"
- "Do you have a specific model preference (local vs cloud)?"
- "How much control do you want over the output?"

**Step 3: Recommendation**

```
┌────────────────────────────────────────────────────────────┐
│ Assistant: Based on your answers, I recommend:            │
│                                                            │
│  ╔═══════════════════════════════════════════════════╗    │
│  ║  🎨 Dada Transformation                          ║    │
│  ║                                                   ║    │
│  ║  Perfect for: Creative, unexpected text           ║    │
│  ║  transformations that challenge meaning           ║    │
│  ║                                                   ║    │
│  ║  Match Score: 95%                                 ║    │
│  ║                                                   ║    │
│  ║  [Select This]                                    ║    │
│  ╚═══════════════════════════════════════════════════╝    │
│                                                            │
│  Other good matches:                                       │
│  • Surrealism Transformation (87%)  [Select]              │
│  • Stillepost (recursive echo) (78%)  [Select]            │
│                                                            │
│  [Show me more options]  [Start over]                     │
└────────────────────────────────────────────────────────────┘
```

### LLM Integration Architecture

**Backend Endpoint:**
```
POST /api/llm/recommend_config
Body: {
  conversation_history: [
    { role: "assistant", content: "What would you like to create?" },
    { role: "user", content: "Transform text creatively" },
    { role: "assistant", content: "Art style or experimental?" },
    { role: "user", content: "Experimental" }
  ]
}

Response: {
  recommended_configs: [
    { config_id: "dada", match_score: 0.95, reason: "..." },
    { config_id: "surrealism", match_score: 0.87, reason: "..." }
  ],
  follow_up_question: "..." (if more info needed)
}
```

**LLM Model Selection:**

**Option 1: Local LLM (gpt-OSS via Ollama)**
- Pros: Privacy, no API costs, already available
- Cons: Slower, requires system resources

**Option 2: Cloud LLM (OpenRouter)**
- Pros: Fast, high quality
- Cons: API costs, requires internet

**Recommendation:** Start with local, allow admin to configure cloud option

### Prompt Engineering Strategy

**System Prompt:**
```
You are an AI assistant helping users discover the right creative
transformation pipeline for their needs. You have access to 40+ configs
ranging from art movement transformations to media generation.

Your goal is to:
1. Understand user's creative intent
2. Ask clarifying questions (max 2-3)
3. Recommend 1-3 best-matching configs with match scores
4. Explain WHY each config matches their needs

Available configs and their metadata:
[Inject full config metadata here]

Keep responses friendly, concise, and educational. Help users discover
unexpected creative possibilities.
```

**Few-Shot Examples:**
```
User: "I want something weird"
Assistant: "Weird in what way? Nonsensical text (like Dada),
surreal imagery, or experimental sound combinations?"

User: "Nonsensical text"
Assistant: "Perfect! I recommend Dada Transformation (95% match) -
it creates unexpected word combinations that defy logic. Also check
out Stillepost (85% match) - it's like telephone game with 8 recursive
transformations."
```

### Quick Actions

**"I'm Feeling Lucky" Button:**
- Selects random config
- Weighted toward popular/beginner-friendly configs
- Immediately jumps to Phase 2+3

**"Show Me All Options" Button:**
- Exits LLM mode
- Switches to Tile view (Mode A)
- Preserves any filtering from conversation

**"Start Over" Button:**
- Clears conversation history
- Resets to initial question
- Maintains mode (stays in LLM dialog)

### Accessibility Considerations

**Screen Reader Support:**
- Conversation history readable in order
- "New message from assistant" announcements
- "Recommendation card" structure properly labeled

**Keyboard Navigation:**
- Tab through recommended cards
- Enter to expand/select
- Escape to exit mode

**Visual Indicators:**
- Typing indicator when LLM is responding
- Clear distinction between user/assistant messages
- Progress indicator if response is slow (>2 seconds)

---

## Mode Switching Interface

### Mode Switcher Bar (Top)

```
┌──────────────────────────────────────────────────────────┐
│  [📱 Tiles] [📋 List] [🤖 AI Help]  │  🔍 [Search...]  │
│   Active     Inactive   Inactive    │   [🔽 Filter]    │
└──────────────────────────────────────────────────────────┘
```

**Icon Design:**
- Tiles Mode: Grid icon (4x4 squares)
- List Mode: Horizontal lines (list representation)
- LLM Mode: Chat bubble or robot icon

**State Indicators:**
- Active mode: Filled icon, underline, or background
- Inactive modes: Outline icon, clickable
- Hover: Icon animation (subtle pulse)

**Transition Animation:**
- Fade out current mode
- Fade in new mode
- Duration: 200ms
- Easing: ease-in-out

### State Preservation

**When Switching Modes:**

**Preserve:**
- Current search query (if applicable)
- Active filters
- Scroll position (within reason)
- Selected config (if any)

**Reset:**
- Mode-specific UI state (expanded panels, etc.)

**Example:**
```
User in Tile Mode:
- Filtered to "audio" output
- 6 configs visible
- Scrolled halfway down

User switches to List Mode:
→ Same 6 configs shown
→ Same filter applied
→ Top of list (reset scroll)
```

---

## Execution Parameter Selection

### When to Prompt for Parameters

**At Selection Time** (recommended):
- User clicks config → Modal/drawer opens
- Shows full config details
- Prompts for execution_mode and safety_level
- [Confirm Selection] → Proceeds to Phase 2+3

**After Phase Transition** (alternative):
- User clicks config → Immediately navigates to Phase 2+3
- Phase 2+3 shows parameter selection as first step
- More streamlined but less clear

**Recommendation:** Select at Phase 1 to make decision point explicit

### Parameter Selection UI

```
┌───────────────────────────────────────────────────┐
│  🎨 Dada Transformation                           │
│  ═════════════════════════════════════════════════│
│                                                   │
│  [Config description and details...]              │
│                                                   │
│  ─────────────────────────────────────────────────│
│                                                   │
│  Execution Mode:                                  │
│                                                   │
│  ○ Eco Mode                                       │
│    • Uses local LLMs (Ollama)                     │
│    • Slower (~30-60 seconds)                      │
│    • Free, unlimited usage                        │
│    • Privacy-friendly (no cloud)                  │
│                                                   │
│  ● Fast Mode (Recommended)                        │
│    • Uses cloud APIs (OpenRouter)                 │
│    • Faster (~10-20 seconds)                      │
│    • Requires API credits                         │
│    • Higher quality output                        │
│                                                   │
│  ─────────────────────────────────────────────────│
│                                                   │
│  Safety Level:                                    │
│                                                   │
│  ● Kids (Strict)                                  │
│    • Maximum content filtering                    │
│    • Blocks all potentially unsafe content        │
│    • Recommended for classroom use                │
│                                                   │
│  ○ Youth (Moderate)                               │
│    • Balanced filtering                           │
│    • Allows more creative freedom                 │
│    • For older students (13+)                     │
│                                                   │
│  ─────────────────────────────────────────────────│
│                                                   │
│  [Cancel]            [Select & Continue →]        │
└───────────────────────────────────────────────────┘
```

### Default Values

**Execution Mode:**
- Default: `fast` (better UX)
- Override: Admin config can set `eco` as default

**Safety Level:**
- Default: `kids` (safest)
- Override: User preference can be remembered

**Persistence:**
- Remember last-used values per user
- Show as "Your usual: Fast + Kids" hint

---

## User Config Integration

### Displaying User Configs

**Visual Differentiation:**
- Badge: "USER" or custom icon (👤)
- Color accent: Different border/background
- Separate category: "My Configs" section
- Can be mixed with system configs or isolated

**User Config Actions:**

**In Tile/List:**
- Standard selection (same as system configs)
- Context menu (right-click or ⋮ icon):
  - Edit Config
  - Duplicate Config
  - Delete Config
  - Export Config (download JSON)
  - Share Config (generate link/code)

**In Details Panel:**
```
┌─────────────────────────────────────┐
│  👤 My Custom Dada Flow             │
│  ═══════════════════════════════════│
│                                     │
│  [Config details...]                │
│                                     │
│  ─────────────────────────────────  │
│                                     │
│  This is your custom config         │
│  Created: 2025-11-05                │
│  Last used: Yesterday               │
│                                     │
│  [✏️ Edit]  [🗑️ Delete]  [📤 Share] │
│                                     │
│  [Select & Continue]                │
└─────────────────────────────────────┘
```

### Creating User Configs

**Entry Points:**

1. **"Create New" Button (Phase 1 toolbar)**
   - Opens config creation wizard
   - Step-by-step guided creation

2. **"Duplicate & Modify" (from system config)**
   - Starts with system config as template
   - User customizes parameters

3. **"Import Config" (from file/code)**
   - Upload JSON file
   - Paste config code
   - Validates and imports

**Quick Creation Flow:**
```
Step 1: Basic Info
  Name: [My Experimental Flow]
  Description: [What does it do?]
  Icon: [🔬] (emoji picker or upload)

Step 2: Pipeline Selection
  Pipeline Type: [text_transformation ▼]
  Base Template: [Choose starting point...]

Step 3: Configuration
  [Pipeline-specific settings...]
  Context: [LLM instruction text...]

Step 4: Test & Save
  Test Input: [Enter test text...]
  [Run Test]
  → Shows output
  [Save Config]  [Cancel]
```

### Config Management

**User Config Library:**
- Accessible via Phase 1 menu: "Manage My Configs"
- Grid/list of user configs
- Sorting: Date created, last used, alphabetical
- Bulk actions: Export all, delete multiple

**Import/Export:**
- Export format: JSON file
- Import validation: Schema check before accepting
- Version compatibility warnings

**Sharing:**
- Generate shareable code (base64 encoded JSON)
- Copy to clipboard
- Other users can import via "Import from Code"

---

## Search & Discovery Features

### Global Search (Across All Modes)

**Search Bar Behavior:**

**Real-Time Filtering:**
- As user types, results update immediately
- Search in: name, description, tags, category
- Fuzzy matching: "surrel" matches "surrealism"
- Highlight matching text in results

**Search Operators:**
```
Basic:        "audio"           → Matches any field
Quoted:       "stable audio"    → Exact phrase
Category:     cat:art-movements → Filter by category
Output:       out:image         → Filter by output type
Difficulty:   diff:3            → Filter by star rating
User configs: is:user           → Only user configs
System:       is:system         → Only system configs
```

**Search Results Display:**

**In Tile/List Mode:**
- Matching configs shown
- Non-matching configs hidden
- Match count: "12 configs match 'audio'"

**In LLM Mode:**
- Exits LLM conversation
- Shows direct search results
- Option to "Ask AI about these results"

### Advanced Filters

**Filter Panel (Collapsible Sidebar or Modal):**

```
┌─────────────────────────────────┐
│  Filters                  [X]  │
│  ─────────────────────────────  │
│                                 │
│  Output Type:                   │
│  ☑ Text                        │
│  ☐ Image                       │
│  ☑ Audio                       │
│  ☐ Video                       │
│  ☐ Music                       │
│                                 │
│  Pipeline Type:                 │
│  ☑ Text Transformation         │
│  ☐ Single Media Generation     │
│  ☐ Dual-Input Generation       │
│                                 │
│  Category:                      │
│  ☐ Art Movements               │
│  ☑ Experimental                │
│  ☐ Educational                 │
│  ☐ Media Generation            │
│  ☐ User Configs                │
│                                 │
│  Difficulty:                    │
│  Range: ⭐ ═▓▓▓▓══ ⭐⭐⭐⭐⭐ │
│  (1-4 stars selected)           │
│                                 │
│  ─────────────────────────────  │
│  [Reset All]     [Apply]        │
└─────────────────────────────────┘
```

**Filter Persistence:**
- Saved to localStorage
- Applied across sessions
- "Clear all filters" option always visible

### Recommendations

**"For You" Section (Optional Enhancement):**

Based on:
- Most used configs
- Recently used configs
- Configs similar to favorites
- Trending (if multi-user system)

**Display:**
```
════════════════════════════════════
  RECOMMENDED FOR YOU
════════════════════════════════════
[Config A]  [Config B]  [Config C]
```

---

## Performance Optimization

### Data Loading Strategy

**Initial Load:**
```javascript
// Fetch config metadata (lightweight)
const configs = await api.get('/pipeline_configs_metadata');
// ~20KB for 40 configs

// Lazy load icons/images
configs.forEach(config => {
  config.iconUrl = `/api/config/${config.id}/icon`;
  // Load on viewport intersection (lazy loading)
});
```

**Caching:**
- Cache config metadata in localStorage (24-hour TTL)
- Check for updates via ETag or version header
- Invalidate cache when user creates/deletes config

### Virtual Scrolling

**For Large Config Lists (100+):**

**Tile Mode:**
- Render only visible tiles + buffer (20 tiles)
- As user scrolls, render new tiles, unrender off-screen

**List Mode:**
- Render only visible rows + buffer (50 rows)
- Much smoother for 100+ configs

**Library:** Use `vue-virtual-scroller` or custom implementation

### Search Performance

**Debouncing:**
```javascript
// Wait 300ms after user stops typing before searching
const debouncedSearch = debounce((query) => {
  this.searchConfigs(query);
}, 300);
```

**Client-Side vs Server-Side:**
- Client-side: Fast, works offline, limited to metadata fields
- Server-side: Slower, requires request, can search config content
- **Hybrid:** Client-side first, server-side if no results or advanced query

---

## Error Handling

### Config Loading Errors

**API Failure:**
```
Error Message:
"Unable to load available schemas. Please refresh the page."

Actions:
[Retry]  [Use Cached Configs]  [Contact Support]
```

**Empty Config List:**
```
Message:
"No schemas available. This might be a configuration issue."

Actions:
[Reload]  [Check Server Status]
```

### User Config Errors

**Invalid Config:**
```
Error:
"This config file is invalid or incompatible."

Details:
• Missing required field: "pipeline"
• Unknown pipeline type: "custom_flow"

Actions:
[Edit & Fix]  [Cancel Import]
```

**Duplicate Name:**
```
Warning:
"A config named 'My Custom Flow' already exists."

Actions:
[Rename New Config]  [Overwrite Existing]  [Cancel]
```

---

## Accessibility (WCAG 2.1 AA)

### Keyboard Navigation

**Global:**
- Tab/Shift+Tab: Navigate between modes, search, filters, configs
- Escape: Close modals, clear search, deselect

**Tile Mode:**
- Arrow keys: Navigate grid (up/down/left/right)
- Enter: Open selection modal
- Space: Quick-select (skip modal)

**List Mode:**
- Up/Down arrows: Navigate rows
- Enter: Open details panel
- Space: Toggle selection

**LLM Mode:**
- Tab: Focus input field, then navigate buttons
- Enter: Send message

### Screen Reader Support

**ARIA Labels:**
```html
<button aria-label="Switch to tile view mode">
  [Tile Icon]
</button>

<div role="grid" aria-label="Available schema configurations">
  <!-- Tiles -->
</div>

<div role="article" aria-label="Dada Transformation config">
  <!-- Card content -->
</div>
```

**Live Regions:**
```html
<div aria-live="polite" aria-atomic="true">
  12 configs match "audio"
</div>

<div aria-live="assertive" role="alert">
  Error loading configs. Please retry.
</div>
```

### Visual Accessibility

**Color Contrast:**
- Card text: 7:1 ratio (AAA)
- Icon + text combos (never icon alone)
- Focus indicators: 3:1 contrast minimum

**Focus Styles:**
- Visible focus ring (2px solid, high contrast)
- Skip links for keyboard users
- Focus trap in modals

**Motion:**
```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Testing Strategy

### Unit Tests

**Config Card Component:**
- Renders metadata correctly
- Shows/hides user badge based on is_user_config
- Difficulty stars render correctly (1-5)
- Click handler fires with config_id

**Search Component:**
- Filters configs by query
- Handles empty results
- Debounces input correctly

**Filter Component:**
- Applies multiple filters (AND logic)
- Reset clears all filters
- Persists to localStorage

### Integration Tests

**Mode Switching:**
- Switch from Tiles → List preserves search query
- Switch from List → LLM clears selection
- Mode state persists across page refresh

**LLM Dialog:**
- Conversation history maintained
- Recommendations display correctly
- Selection from LLM proceeds to Phase 2+3

### E2E Tests

**User Flows:**

1. **Browse & Select (Tiles):**
   - Load Phase 1 → See tiles
   - Search "audio" → See filtered tiles
   - Click tile → See modal
   - Select execution params → Proceed to Phase 2+3

2. **Browse & Select (List):**
   - Switch to list mode
   - Sort by difficulty
   - Click row → See details panel
   - Select config → Proceed to Phase 2+3

3. **LLM-Assisted Selection:**
   - Switch to LLM mode
   - Type intent → See follow-up question
   - Type response → See recommendations
   - Select recommendation → Proceed to Phase 2+3

4. **User Config Management:**
   - Create new user config
   - See it appear in "My Configs" section
   - Edit config → Changes saved
   - Delete config → Removed from list

---

## Open Questions & Decisions Needed

### 1. LLM Mode Implementation

**Question:** Which LLM for Mode C recommendations?

**Options:**
- A) Local gpt-OSS (Ollama) - Free, private, slower
- B) Cloud OpenRouter - Fast, costs money
- C) Hybrid: Cloud with local fallback
- D) Simple rule-based (no LLM) - Keyword matching

**Recommendation:** Start with D (rule-based), upgrade to A (local LLM) in V1.0

### 2. User Config Storage

**Question:** Where to store user-created configs?

**Options:**
- A) File system: `/devserver/schemas/configs/user/{user_id}/`
- B) Database: SQLite/PostgreSQL
- C) LocalStorage: Frontend-only (no server persistence)

**Recommendation:** Start with A (file system), consider B for multi-user

### 3. Config Icon Strategy

**Question:** How to handle DX7-style flowchart icons?

**Options:**
- A) Generate SVG flowcharts programmatically from pipeline structure
- B) Designer creates custom icon for each config
- C) Use emoji + small static flowchart overlay
- D) Icon library (FontAwesome, etc.) + category colors

**Recommendation:** Start with D (icon library), enhance with B (custom icons) later

### 4. Mode Persistence

**Question:** Should mode selection persist across sessions?

**Options:**
- A) Always start in Tiles mode
- B) Remember last-used mode (localStorage)
- C) Admin-configurable default mode

**Recommendation:** B (remember last mode) - better UX

### 5. Category Taxonomy

**Question:** Who defines categories? How are they maintained?

**Options:**
- A) Hardcoded in frontend (limited flexibility)
- B) Backend provides category list via API (dynamic)
- C) Configs self-categorize, frontend extracts unique categories

**Recommendation:** C (self-categorization) - most flexible, no central management

---

## Related Documentation

**Parent Document:**
- `FRONTEND_ARCHITECTURE_OVERVIEW.md` - Overall 3-phase structure

**Sibling Documents:**
- `PHASE_2_3_FLOW_EXPERIENCE.md` - Next phase after selection

**Implementation Documents:**
- `VUE_COMPONENT_ARCHITECTURE.md` - Component hierarchy for Phase 1
- `METADATA_SCHEMA_SPECIFICATION.md` - Required config metadata fields
- `VISUAL_DESIGN_PATTERNS.md` - Icon, flowchart, card design specs

**Backend Integration:**
- `/docs/ARCHITECTURE PART 11 - API-Routes.md` - API endpoints
- `/docs/README.md` - System overview

---

**Document Status:** ✅ Complete
**Next Steps:** Define Phase 2+3 specification
**Estimated Implementation:** MVP (1-2 weeks) → Full (3-4 weeks)
