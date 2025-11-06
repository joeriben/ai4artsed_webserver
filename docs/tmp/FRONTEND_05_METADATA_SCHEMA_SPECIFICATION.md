# Metadata Schema Specification

**Version:** 1.0
**Date:** 2025-11-06
**Status:** Planning Document
**Parent:** FRONTEND_ARCHITECTURE_OVERVIEW.md

---

## Executive Summary

This document defines the **required and optional metadata fields** that config files must expose to enable dynamic, metadata-driven frontend display. The specification ensures that configs (both system and user-created) can integrate seamlessly into Phase 1 visualization modes without frontend code changes.

---

## Core Design Principles

1. **Extensibility:** New configs appear automatically in frontend
2. **Self-Description:** Configs contain all display metadata within themselves
3. **Backward Compatibility:** Frontend gracefully handles missing optional fields
4. **Validation:** Clear rules for required vs optional fields
5. **Discoverability:** Metadata enables search, filter, categorization

---

## Config Metadata Structure

### Complete Schema

```json
{
  "id": "dada",
  "name": "Dada Transformation",
  "description": "Transform text using Dada art movement principles, creating nonsensical and unexpected word combinations that challenge conventional meaning.",
  "category": "art-movements",
  "icon": "🎨",
  "difficulty": 3,
  "tags": ["text", "transformation", "experimental", "art"],
  "input_requirements": {
    "type": "text",
    "max_length": 500,
    "min_length": 10,
    "accepts_multiline": true,
    "placeholder": "Enter creative text to transform..."
  },
  "output_types": ["text"],
  "pipeline": "text_transformation",
  "is_user_config": false,
  "author": {
    "name": "AI4ArtsEd Team",
    "email": "contact@example.com",
    "url": "https://ai4artsed.example.com"
  },
  "version": "1.2.0",
  "created_date": "2025-01-15",
  "last_modified": "2025-11-01",
  "example_inputs": [
    "A flower in the meadow",
    "The cat sat on the mat",
    "Dreams of electric sheep"
  ],
  "example_outputs": [
    "Meadow-flower chaos umbrella contradiction!",
    "Mat-cat nonsense spiral absurd",
    "Electric dream-sheep void paradox"
  ],
  "estimated_time": {
    "eco": 30,
    "fast": 12
  },
  "requires_api_credits": {
    "eco": false,
    "fast": true
  },
  "safety_compatible": ["kids", "youth"],
  "flowchart": {
    "type": "recursive",
    "iterations": 8,
    "style": "dx7",
    "svg_path": "/assets/flowcharts/dada.svg"
  },
  "educational_context": {
    "suitable_age": "12+",
    "learning_goals": [
      "Understand Dada art movement principles",
      "Explore meaning-making through nonsense",
      "Experience algorithmic creativity"
    ],
    "subject_areas": ["art", "literature", "history"]
  },
  "advanced": {
    "supports_batch": false,
    "max_concurrent_runs": 1,
    "requires_local_model": false,
    "gpu_recommended": false
  }
}
```

---

## Field Specifications

### Required Fields

These fields MUST be present for a config to be valid:

#### 1. `id` (string)

**Purpose:** Unique identifier for this config

**Requirements:**
- Lowercase, alphanumeric, underscores, hyphens only
- No spaces
- Unique across all configs (system + user)
- Immutable after creation

**Examples:**
- ✅ `dada`
- ✅ `stillepost`
- ✅ `sd35_large`
- ✅ `my_custom_flow_v2`
- ❌ `Dada Transformation` (spaces, caps)
- ❌ `my-config!` (special character)

**Validation:**
```regex
^[a-z0-9_-]+$
```

---

#### 2. `name` (string)

**Purpose:** Human-readable display name

**Requirements:**
- 1-50 characters
- Clear, descriptive
- Proper capitalization
- Displayed in tiles, lists, headers

**Examples:**
- ✅ `Dada Transformation`
- ✅ `SD3.5 Large Image Generation`
- ✅ `My Experimental Flow`
- ❌ `dada` (not descriptive enough)
- ❌ `This is a really really long name that goes on forever` (too long)

**Validation:**
```typescript
name.length >= 1 && name.length <= 50
```

---

#### 3. `description` (string)

**Purpose:** Detailed explanation of what this config does

**Requirements:**
- 10-500 characters
- Complete sentences
- Explains purpose, not technical details
- Displayed in cards, modals

**Examples:**
```
✅ "Transform text using Dada art movement principles, creating nonsensical and unexpected word combinations that challenge conventional meaning."

❌ "Uses manipulate chunk with GPT-OSS backend" (too technical)

❌ "Transform text." (too short, not descriptive)
```

**Validation:**
```typescript
description.length >= 10 && description.length <= 500
```

---

#### 4. `category` (string)

**Purpose:** Grouping for organization in Phase 1

**Requirements:**
- Lowercase, hyphen-separated
- Use existing categories when possible
- New categories allowed (extensible)

**Common Categories:**
- `art-movements` (Dada, Bauhaus, Expressionism, etc.)
- `media-generation` (Image, audio, video outputs)
- `text-transformation` (Stillepost, translation, etc.)
- `experimental` (Quantum theory, cliché filter, etc.)
- `educational` (Teaching-focused configs)
- `user-configs` (User-created, auto-assigned)

**Examples:**
- ✅ `art-movements`
- ✅ `media-generation`
- ✅ `custom-experimental`
- ❌ `Art Movements` (caps, space)

**Validation:**
```regex
^[a-z0-9-]+$
```

---

#### 5. `icon` (string)

**Purpose:** Visual identifier displayed in tiles/lists

**Requirements:**
- Single emoji character (preferred)
- OR path to SVG file
- OR unicode character
- Displayed at various sizes (40px - 150px)

**Examples:**
- ✅ `🎨` (emoji)
- ✅ `/assets/icons/custom.svg` (SVG path)
- ✅ `🏛️`
- ❌ `icon.png` (PNG not supported, use SVG)

**Validation:**
```typescript
// Emoji (1-2 characters) or SVG path
icon.length <= 2 || icon.startsWith('/assets/icons/')
```

---

#### 6. `difficulty` (integer)

**Purpose:** Complexity rating for user guidance

**Requirements:**
- Integer: 1-5
- 1 = Beginner (simple, predictable)
- 2 = Easy (straightforward, few options)
- 3 = Intermediate (some complexity)
- 4 = Advanced (complex, many parameters)
- 5 = Expert (requires deep understanding)

**Display:**
- Rendered as ⭐⭐⭐ (filled stars)

**Examples:**
- `1` → Translation (simple, direct)
- `3` → Dada Transformation (moderate complexity)
- `4` → SD3.5 Large (many parameters)
- `5` → Split & Combine Spherical (advanced math)

**Validation:**
```typescript
difficulty >= 1 && difficulty <= 5 && Number.isInteger(difficulty)
```

---

#### 7. `output_types` (array of strings)

**Purpose:** Indicate what types of output this config produces

**Requirements:**
- Array with 1+ values
- Valid values: `"text"`, `"image"`, `"audio"`, `"music"`, `"video"`
- Used for filtering in Phase 1

**Examples:**
```json
["text"]                  // Text transformation only
["image"]                 // Image generation only
["audio"]                 // Audio generation only
["text", "image"]         // Both text and image
```

**Validation:**
```typescript
output_types.length > 0 &&
output_types.every(t => ['text', 'image', 'audio', 'music', 'video'].includes(t))
```

---

#### 8. `pipeline` (string)

**Purpose:** Backend pipeline type to execute

**Requirements:**
- Must match existing pipeline in `schemas/pipelines/`
- One of:
  - `text_transformation`
  - `single_text_media_generation`
  - `dual_text_media_generation`
  - `image_text_media_generation`

**Examples:**
```json
"text_transformation"              // Dada, Stillepost, etc.
"single_text_media_generation"     // SD3.5, GPT-5 Image, etc.
"dual_text_media_generation"       // ACE Step music
```

**Validation:**
```typescript
['text_transformation', 'single_text_media_generation', 'dual_text_media_generation', 'image_text_media_generation'].includes(pipeline)
```

---

### Optional Fields (Recommended)

These fields are optional but enhance user experience:

#### 9. `tags` (array of strings)

**Purpose:** Keywords for search and discovery

**Requirements:**
- 0-10 tags
- Lowercase, hyphen-separated
- Supplement category for more specific search

**Examples:**
```json
["text", "transformation", "experimental", "art", "dada"]
["image", "generation", "sd35", "local", "fast"]
["audio", "music", "narrative", "dual-input"]
```

**Use Cases:**
- Search: User types "experimental" → Shows configs with that tag
- Related configs: "People who used this also liked..." (same tags)

---

#### 10. `input_requirements` (object)

**Purpose:** Define input constraints for validation

**Structure:**
```json
{
  "type": "text",              // Required: "text", "image", "dual-text"
  "max_length": 500,           // Optional: Max characters (text)
  "min_length": 10,            // Optional: Min characters (text)
  "accepts_multiline": true,   // Optional: Allow line breaks
  "placeholder": "Enter..."    // Optional: Input field placeholder
}
```

**Examples:**

**Text Input (Simple):**
```json
{
  "type": "text",
  "max_length": 200
}
```

**Text Input (Detailed):**
```json
{
  "type": "text",
  "max_length": 500,
  "min_length": 10,
  "accepts_multiline": true,
  "placeholder": "Describe a surreal landscape..."
}
```

**Dual-Text Input (Music):**
```json
{
  "type": "dual-text",
  "fields": [
    {
      "name": "tags",
      "label": "Music Tags",
      "placeholder": "upbeat, electronic, dreamy",
      "max_length": 100
    },
    {
      "name": "lyrics",
      "label": "Lyrics/Narrative",
      "placeholder": "Floating through space...",
      "max_length": 1000,
      "accepts_multiline": true
    }
  ]
}
```

---

#### 11. `is_user_config` (boolean)

**Purpose:** Distinguish user-created from system configs

**Requirements:**
- `true` for user-created configs
- `false` (or omitted) for system configs
- Displayed with badge in Phase 1

**Default:** `false`

**Display:**
- User configs show "USER" badge
- Can be filtered separately

---

#### 12. `author` (object)

**Purpose:** Attribution for user configs or system configs

**Structure:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "url": "https://johndoe.com"
}
```

**Use Cases:**
- User configs: Show creator name
- System configs: Show "AI4ArtsEd Team"
- Future: Community sharing, attribution

---

#### 13. `version` (string)

**Purpose:** Track config evolution

**Requirements:**
- Semantic versioning: `major.minor.patch`
- Increment on changes:
  - Major: Breaking changes (behavior fundamentally different)
  - Minor: New features (backward compatible)
  - Patch: Bug fixes, minor tweaks

**Examples:**
- `1.0.0` → Initial release
- `1.1.0` → Added new parameter
- `2.0.0` → Changed from text to image output (breaking)

---

#### 14. `created_date` (string)

**Purpose:** Track when config was created

**Requirements:**
- ISO 8601 date format: `YYYY-MM-DD`

**Examples:**
- `2025-01-15`
- `2024-11-06`

---

#### 15. `last_modified` (string)

**Purpose:** Track last update to config

**Requirements:**
- ISO 8601 date format: `YYYY-MM-DD`
- Auto-updated on save (if system supports)

**Use Cases:**
- "Updated 3 days ago" display
- Sort by recently updated
- Change tracking

---

#### 16. `example_inputs` (array of strings)

**Purpose:** Show users example prompts in Phase 2+3

**Requirements:**
- 1-5 example strings
- Realistic, diverse examples
- Appropriate for target audience

**Examples:**
```json
[
  "A flower in the meadow",
  "The cat sat on the mat",
  "Dreams of electric sheep"
]
```

**Display:**
- Show below prompt input field
- Clickable to auto-fill input

---

#### 17. `example_outputs` (array of strings)

**Purpose:** Preview what output looks like

**Requirements:**
- Correspond to `example_inputs` (same order)
- Show expected transformation

**Examples:**
```json
[
  "Meadow-flower chaos umbrella contradiction!",
  "Mat-cat nonsense spiral absurd",
  "Electric dream-sheep void paradox"
]
```

**Display:**
- Show in config modal/details panel
- Help users understand config behavior

---

#### 18. `estimated_time` (object)

**Purpose:** Set user expectations for execution time

**Structure:**
```json
{
  "eco": 30,      // Seconds (eco mode)
  "fast": 12      // Seconds (fast mode)
}
```

**Display:**
- "Estimated time: ~12 seconds (Fast)" in Phase 1
- "Estimated time: ~30 seconds (Eco)" in Phase 1

---

#### 19. `requires_api_credits` (object)

**Purpose:** Indicate if cloud API costs money

**Structure:**
```json
{
  "eco": false,    // Eco mode free (local)
  "fast": true     // Fast mode requires credits
}
```

**Display:**
- Show warning/info in Phase 1
- "Fast mode requires API credits" badge

---

#### 20. `safety_compatible` (array of strings)

**Purpose:** Indicate which safety levels work with this config

**Requirements:**
- Valid values: `"kids"`, `"youth"`
- Most configs support both
- Some might be youth-only (e.g., mature themes)

**Examples:**
```json
["kids", "youth"]    // Works with both
["youth"]            // Youth only (mature content)
```

**Display:**
- Disable incompatible safety levels in modal
- Show warning if selected safety not supported

---

#### 21. `flowchart` (object)

**Purpose:** Metadata for DX7-style flowchart visualization

**Structure:**
```json
{
  "type": "recursive",           // Type: "linear", "recursive", "branching", "complex"
  "iterations": 8,               // If recursive, how many?
  "style": "dx7",                // Visual style reference
  "svg_path": "/assets/flowcharts/dada.svg"  // Pre-rendered SVG (optional)
}
```

**Use Cases:**
- Generate flowchart programmatically from `type` and `iterations`
- OR load pre-rendered SVG from `svg_path`
- Display in Phase 1 card (small) or Phase 2+3 (large)

**Flowchart Types:**

**Linear:**
```
Input → Transform → Output
```

**Recursive (N iterations):**
```
Input → [Transform]×N → Output
```

**Branching (parallel paths):**
```
       ┌→ Path A ─┐
Input ─┤          ├→ Output
       └→ Path B ─┘
```

**Complex:**
```
Custom flowchart, requires SVG
```

---

#### 22. `educational_context` (object)

**Purpose:** Pedagogical metadata for classroom use

**Structure:**
```json
{
  "suitable_age": "12+",
  "learning_goals": [
    "Understand Dada art movement principles",
    "Explore meaning-making through nonsense",
    "Experience algorithmic creativity"
  ],
  "subject_areas": ["art", "literature", "history"]
}
```

**Use Cases:**
- Teachers filter by age appropriateness
- Curriculum integration (subject areas)
- Educational documentation export

---

#### 23. `advanced` (object)

**Purpose:** Technical metadata for power users/admins

**Structure:**
```json
{
  "supports_batch": false,        // Can run multiple inputs at once?
  "max_concurrent_runs": 1,       // How many simultaneous executions?
  "requires_local_model": false,  // Needs Ollama/local LLM?
  "gpu_recommended": false        // Benefits from GPU acceleration?
}
```

**Use Cases:**
- Admin dashboard shows resource requirements
- Frontend can warn "This config requires local setup"
- Future: Batch processing feature

---

## API Endpoint Specification

### GET /pipeline_configs_metadata

**Purpose:** Return all config metadata for Phase 1 display

**Response Structure:**
```json
{
  "configs": [
    {
      "id": "dada",
      "name": "Dada Transformation",
      "description": "...",
      "category": "art-movements",
      "icon": "🎨",
      "difficulty": 3,
      "tags": ["text", "transformation", "experimental"],
      "output_types": ["text"],
      "pipeline": "text_transformation",
      "is_user_config": false,
      ...
    },
    {
      "id": "sd35_large",
      ...
    }
  ],
  "total_count": 38,
  "system_count": 35,
  "user_count": 3,
  "categories": [
    { "name": "art-movements", "count": 8 },
    { "name": "media-generation", "count": 6 },
    { "name": "text-transformation", "count": 12 },
    { "name": "experimental", "count": 6 },
    { "name": "user-configs", "count": 3 }
  ]
}
```

**Caching:**
- Frontend caches response in localStorage (24h TTL)
- Invalidate on user config create/delete
- Check for updates via ETag or `If-Modified-Since` header

---

## Validation Rules

### Backend Validation (Python)

**Config files must pass validation before being loaded:**

```python
import jsonschema

CONFIG_SCHEMA = {
    "type": "object",
    "required": ["id", "name", "description", "category", "icon", "difficulty", "output_types", "pipeline"],
    "properties": {
        "id": {
            "type": "string",
            "pattern": "^[a-z0-9_-]+$",
            "minLength": 1,
            "maxLength": 50
        },
        "name": {
            "type": "string",
            "minLength": 1,
            "maxLength": 50
        },
        "description": {
            "type": "string",
            "minLength": 10,
            "maxLength": 500
        },
        "category": {
            "type": "string",
            "pattern": "^[a-z0-9-]+$"
        },
        "icon": {
            "type": "string"
        },
        "difficulty": {
            "type": "integer",
            "minimum": 1,
            "maximum": 5
        },
        "output_types": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "string",
                "enum": ["text", "image", "audio", "music", "video"]
            }
        },
        "pipeline": {
            "type": "string",
            "enum": ["text_transformation", "single_text_media_generation", "dual_text_media_generation", "image_text_media_generation"]
        },
        "tags": {
            "type": "array",
            "maxItems": 10,
            "items": {"type": "string"}
        },
        "is_user_config": {
            "type": "boolean"
        }
        # ... additional optional fields
    }
}

def validate_config(config_data):
    jsonschema.validate(instance=config_data, schema=CONFIG_SCHEMA)
```

---

### Frontend Validation (TypeScript)

**Type guards for runtime validation:**

```typescript
import { z } from 'zod';

export const ConfigSchema = z.object({
  id: z.string().regex(/^[a-z0-9_-]+$/).min(1).max(50),
  name: z.string().min(1).max(50),
  description: z.string().min(10).max(500),
  category: z.string().regex(/^[a-z0-9-]+$/),
  icon: z.string(),
  difficulty: z.number().int().min(1).max(5),
  output_types: z.array(z.enum(['text', 'image', 'audio', 'music', 'video'])).min(1),
  pipeline: z.enum(['text_transformation', 'single_text_media_generation', 'dual_text_media_generation', 'image_text_media_generation']),
  tags: z.array(z.string()).max(10).optional(),
  is_user_config: z.boolean().optional(),
  // ... additional optional fields
});

export type Config = z.infer<typeof ConfigSchema>;

// Validate at runtime
function validateConfig(data: unknown): Config {
  return ConfigSchema.parse(data);
}
```

---

## User Config Creation Workflow

### Step 1: User Initiates Creation

**Entry Points:**
- Phase 1: "Create New Config" button
- Phase 1: "Duplicate Config" on existing config

### Step 2: Guided Wizard

**Screen 1: Basic Info**
```
Name: [My Experimental Flow]
Description: [What does this config do?]
Category: [experimental ▼]
Icon: [🔬] (emoji picker)
Difficulty: ⭐⭐⭐☆☆
```

**Screen 2: Input/Output**
```
Input Type: [text ▼]
Max Input Length: [500]
Output Types: ☑ Text  ☐ Image  ☐ Audio
```

**Screen 3: Pipeline Config**
```
Pipeline Type: [text_transformation ▼]
LLM Context/Instruction: [Textarea with prompt]
```

**Screen 4: Review & Validate**
```
[Preview of config JSON]
[Validation status: ✓ All fields valid]
[Save Config] [Cancel]
```

### Step 3: Backend Saves Config

**POST /api/configs/create**

Request:
```json
{
  "id": "my_experimental_flow",
  "name": "My Experimental Flow",
  "description": "Custom flow combining...",
  "category": "user-configs",
  "icon": "🔬",
  "difficulty": 3,
  "output_types": ["text"],
  "pipeline": "text_transformation",
  "is_user_config": true,
  "author": {
    "name": "Current User",
    "email": "user@example.com"
  },
  "context": "LLM instruction here..."
}
```

Response:
```json
{
  "status": "success",
  "config_id": "my_experimental_flow",
  "file_path": "/schemas/configs/user/user123/my_experimental_flow.json"
}
```

### Step 4: Frontend Refreshes

- Invalidate config cache
- Reload config list
- Auto-navigate to new config in Phase 1

---

## Backward Compatibility

### Handling Missing Optional Fields

**Frontend Graceful Degradation:**

```typescript
// If 'tags' missing, use empty array
const tags = config.tags || [];

// If 'icon' missing, use default based on category
const icon = config.icon || getCategoryDefaultIcon(config.category);

// If 'difficulty' missing, assume medium (3)
const difficulty = config.difficulty || 3;

// If 'estimated_time' missing, don't show estimate
if (config.estimated_time) {
  showEstimate(config.estimated_time);
}
```

### Versioning Strategy

**Breaking Changes:**
- Bump `version` field (if present)
- Document migration path
- Frontend supports multiple schema versions simultaneously

**Non-Breaking Changes:**
- Add new optional fields freely
- Older configs without new fields still work

---

## Example Configs

### Minimal Valid Config (Text Transformation)

```json
{
  "id": "simple_reverse",
  "name": "Simple Reverse",
  "description": "Reverses the order of words in your input text. A simple demonstration of text transformation.",
  "category": "text-transformation",
  "icon": "↩️",
  "difficulty": 1,
  "output_types": ["text"],
  "pipeline": "text_transformation"
}
```

### Full-Featured Config (Image Generation)

```json
{
  "id": "sd35_large",
  "name": "Stable Diffusion 3.5 Large",
  "description": "Generate high-quality images using Stable Diffusion 3.5 Large model. Produces detailed, creative images from text descriptions with excellent prompt adherence.",
  "category": "media-generation",
  "icon": "🖼️",
  "difficulty": 4,
  "tags": ["image", "generation", "sd35", "local", "high-quality"],
  "input_requirements": {
    "type": "text",
    "max_length": 500,
    "min_length": 10,
    "placeholder": "Describe the image you want to create..."
  },
  "output_types": ["image"],
  "pipeline": "single_text_media_generation",
  "is_user_config": false,
  "author": {
    "name": "AI4ArtsEd Team",
    "url": "https://ai4artsed.example.com"
  },
  "version": "1.3.0",
  "created_date": "2024-09-15",
  "last_modified": "2025-11-01",
  "example_inputs": [
    "A majestic dragon flying over misty mountains at sunset",
    "A cozy coffee shop interior with warm lighting and books on shelves",
    "An astronaut planting flowers on Mars"
  ],
  "estimated_time": {
    "eco": 45,
    "fast": 15
  },
  "requires_api_credits": {
    "eco": false,
    "fast": false
  },
  "safety_compatible": ["kids", "youth"],
  "flowchart": {
    "type": "linear",
    "style": "dx7"
  },
  "educational_context": {
    "suitable_age": "10+",
    "learning_goals": [
      "Understand text-to-image AI generation",
      "Practice descriptive writing",
      "Explore creative visualization"
    ],
    "subject_areas": ["art", "technology", "language"]
  },
  "advanced": {
    "supports_batch": false,
    "max_concurrent_runs": 1,
    "requires_local_model": true,
    "gpu_recommended": true
  }
}
```

### User Config Example

```json
{
  "id": "my_surreal_mix",
  "name": "My Surreal Mix",
  "description": "Combines surrealism with scientific terminology to create uniquely strange descriptions. Personal experiment in hybrid prompting.",
  "category": "user-configs",
  "icon": "🌀",
  "difficulty": 3,
  "tags": ["text", "surreal", "science", "experimental", "custom"],
  "input_requirements": {
    "type": "text",
    "max_length": 300
  },
  "output_types": ["text"],
  "pipeline": "text_transformation",
  "is_user_config": true,
  "author": {
    "name": "Jane Doe",
    "email": "jane@example.com"
  },
  "version": "1.0.0",
  "created_date": "2025-11-05",
  "last_modified": "2025-11-05",
  "estimated_time": {
    "eco": 20,
    "fast": 8
  }
}
```

---

## Testing & Quality Assurance

### Validation Tests

**Test Suite: Config Metadata Validation**

```python
def test_required_fields_present():
    config = load_config("dada.json")
    assert "id" in config
    assert "name" in config
    assert "description" in config
    # ... all required fields

def test_id_format():
    config = load_config("dada.json")
    assert config["id"].islower()
    assert " " not in config["id"]
    assert re.match(r'^[a-z0-9_-]+$', config["id"])

def test_difficulty_range():
    config = load_config("dada.json")
    assert 1 <= config["difficulty"] <= 5

def test_output_types_valid():
    config = load_config("dada.json")
    valid = ["text", "image", "audio", "music", "video"]
    for output in config["output_types"]:
        assert output in valid
```

### Frontend Integration Tests

```typescript
describe('Config Metadata Loading', () => {
  it('loads all configs successfully', async () => {
    const response = await api.get('/pipeline_configs_metadata');
    expect(response.data.configs).toBeInstanceOf(Array);
    expect(response.data.configs.length).toBeGreaterThan(0);
  });

  it('all configs have required fields', async () => {
    const response = await api.get('/pipeline_configs_metadata');
    response.data.configs.forEach(config => {
      expect(config).toHaveProperty('id');
      expect(config).toHaveProperty('name');
      expect(config).toHaveProperty('description');
      expect(config).toHaveProperty('category');
      expect(config).toHaveProperty('icon');
      expect(config).toHaveProperty('difficulty');
      expect(config).toHaveProperty('output_types');
      expect(config).toHaveProperty('pipeline');
    });
  });

  it('handles missing optional fields gracefully', () => {
    const minimalConfig = {
      id: 'test',
      name: 'Test',
      description: 'Test config with no optional fields',
      category: 'test',
      icon: '🧪',
      difficulty: 1,
      output_types: ['text'],
      pipeline: 'text_transformation'
    };

    const card = mount(ConfigCard, { props: { config: minimalConfig } });
    expect(card.exists()).toBe(true);
  });
});
```

---

## Migration Guide

### Adding New Metadata Fields

**Process:**
1. Add field to specification (this document)
2. Mark as optional (don't break existing configs)
3. Update validation schemas (backend + frontend)
4. Update UI to display new field (if applicable)
5. Document in changelog

**Example: Adding `last_used_date` field**

```json
{
  "last_used_date": "2025-11-06",  // New optional field
  ...
}
```

Update schema:
```typescript
export const ConfigSchema = z.object({
  ...existing fields,
  last_used_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/).optional()
});
```

Frontend handles missing field:
```typescript
const lastUsed = config.last_used_date
  ? formatDate(config.last_used_date)
  : 'Never used';
```

---

## Related Documentation

- `FRONTEND_ARCHITECTURE_OVERVIEW.md` - Overall architecture
- `PHASE_1_SCHEMA_SELECTION.md` - How metadata is displayed
- `VUE_COMPONENT_ARCHITECTURE.md` - Component consumption of metadata
- `/docs/ARCHITECTURE PART 11 - API-Routes.md` - API endpoint details

---

**Document Status:** ✅ Complete
**Next Steps:** Define visual design patterns
**Last Updated:** 2025-11-06
