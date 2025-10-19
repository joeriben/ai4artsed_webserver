# AI4ArtsEd DevServer Architecture Documentation
**For LLM Assistants and Programmers**

---

## Table of Contents
1. [Terminology](#terminology)
2. [Core Concepts](#core-concepts)
3. [System Layers](#system-layers)
4. [Instruction Types System](#instruction-types-system)
5. [Data Flow](#data-flow)
6. [File Structure](#file-structure)
7. [JSON Schemas](#json-schemas)
8. [Orchestration Layer](#orchestration-layer)
9. [Migration from Legacy](#migration-from-legacy)

---

## Terminology

### Reserved Terms

**Workflow** = Legacy ComfyUI API workflows only
- Format: JSON files with ComfyUI node structure
- Location: `/workflows/` directory (outside devserver)
- Purpose: Backward compatibility with legacy system
- **NEVER use "workflow" for devserver components**

### DevServer Terms

| Term | Definition | File Type | Example |
|------|-----------|-----------|---------|
| **Chunk** | Primitive operation (building block) | JSON | `translate.json`, `prompt_interception.json` |
| **Pipeline** | Sequence of chunks (structural template) | JSON | `simple_interception.json` |
| **Config** | User-facing content + metadata | JSON | `dada.json`, `overdrive.json` |
| **Instruction Type** | Reusable instruction template | JSON (registry) | `manipulation.creative`, `translation.standard` |

---

## Core Concepts

### The Three-Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Layer 3: CONFIGS                          │
│  (User-selectable, editable content + metadata)              │
│                                                               │
│  dada.json, overdrive.json, jugendsprache.json              │
│  - References a pipeline                                     │
│  - Contains context, parameters, metadata                    │
│  - Multilingual names/descriptions                           │
│  - Can override pipeline defaults                            │
└─────────────────────────────────────────────────────────────┘
                             │
                             ├─ references
                             ↓
┌─────────────────────────────────────────────────────────────┐
│                   Layer 2: PIPELINES                         │
│  (Reusable structural templates - NO content)                │
│                                                               │
│  simple_interception.json, image_generation.json            │
│  - Defines sequence of chunks                                │
│  - Declares required fields                                  │
│  - Sets defaults (instruction types, parameters)             │
│  - NEVER contains concrete content                           │
└─────────────────────────────────────────────────────────────┘
                             │
                             ├─ uses
                             ↓
┌─────────────────────────────────────────────────────────────┐
│                    Layer 1: CHUNKS                           │
│  (Primitive operations - building blocks)                    │
│                                                               │
│  translate.json, prompt_interception.json, manipulate.json  │
│  - Defines template with placeholders                        │
│  - Specifies backend type (ollama/openrouter/comfyui)       │
│  - Default model and parameters                              │
│  - Reusable across multiple pipelines                        │
└─────────────────────────────────────────────────────────────┘
```

### Design Principles

1. **Separation of Concerns**
   - Chunks = Technical implementation
   - Pipelines = Structural flow
   - Configs = User-facing content

2. **Reusability**
   - One chunk used by many pipelines
   - One pipeline used by many configs
   - One instruction type used by many configs

3. **No Content in Structure**
   - Pipelines NEVER contain concrete instructions
   - Chunks NEVER contain specific cultural context
   - Only configs contain actual content

4. **User-Friendly**
   - Configs are JSON (easy to edit)
   - Multilingual metadata
   - Visual editor support (future)

---

## System Layers

### Layer 1: Chunks (Primitives)

**Purpose:** Reusable building blocks that perform single operations

**Location:** `devserver/schemas/chunks/*.json`

**Structure:**
```json
{
  "name": "prompt_interception",
  "description": "Universal Prompt Interception - Task+Context+Prompt Format",
  "template": "Task:\n{{INSTRUCTION}}\n\nContext:\n{{CONTEXT}}\n\nPrompt:\n{{INPUT_TEXT}}",
  "backend_type": "ollama",
  "model": "gemma2:9b",
  "parameters": {
    "temperature": 0.7,
    "top_p": 0.9,
    "stream": false
  },
  "meta": {
    "chunk_type": "prompt_interception",
    "output_format": "text"
  }
}
```

**Key Fields:**
- `template`: String with `{{PLACEHOLDERS}}` (filled at runtime)
- `backend_type`: `"ollama"` | `"openrouter"` | `"comfyui"` | `"direct"`
- `model`: Default model (can be overridden)
- `parameters`: Backend-specific parameters
- `meta`: Metadata for system use

**Placeholders:**
- `{{INSTRUCTION}}` - Instruction text (from instruction_types.json)
- `{{CONTEXT}}` - Context information (from config)
- `{{INPUT_TEXT}}` - User's input text
- `{{PREVIOUS_OUTPUT}}` - Output from previous chunk in pipeline
- `{{USER_INPUT}}` - Original user input (before translation)

**Examples:**
- `translate.json` - Text translation
- `prompt_interception.json` - Universal prompt processing
- `manipulate.json` - Text manipulation
- `comfyui_image_generation.json` - Image generation via ComfyUI

---

### Layer 2: Pipelines (Structural Templates)

**Purpose:** Define sequence of chunks without concrete content

**Location:** `devserver/schemas/pipelines/*.json` (renamed from workflow_types)

**Structure:**
```json
{
  "name": "simple_interception",
  "description": "Basic text transformation pipeline",
  "chunks": [
    "prompt_interception"
  ],
  "required_fields": [
    "context",
    "instruction_type"
  ],
  "defaults": {
    "instruction_type": "manipulation.standard",
    "parameters": {
      "temperature": 0.7
    }
  },
  "meta": {
    "input_type": "text",
    "output_type": "text",
    "pre_processing": ["translation", "safety_check"],
    "supports_media_generation": true
  }
}
```

**Key Fields:**
- `chunks`: Array of chunk names (execution order)
- `required_fields`: Fields that configs MUST provide
- `defaults`: Default values (can be overridden by configs)
  - `instruction_type`: Default instruction (e.g., `"manipulation.standard"`)
  - `parameters`: Default parameters
- `meta.pre_processing`: Server-level operations before pipeline
  - `"translation"` - Auto-translate input to English
  - `"safety_check"` - Content safety validation

**Pipeline Examples:**

**Simple Interception:**
```
Input → [Server: Translation + Safety] → prompt_interception → Text Output
```

**Image Generation:**
```
Input → [Server: Translation] → prompt_optimization → image_generation → Image Output
```

**Multi-Step Manipulation:**
```
Input → [Server: Translation] → translate → manipulate → refine → Text Output
```

**Important:** Pipelines are **structural templates only**. They never contain:
- Specific instructions (e.g., Dada art context)
- Concrete cultural content
- User-facing descriptions (those go in configs)

---

### Layer 3: Configs (User-Facing Content)

**Purpose:** User-selectable, editable content + metadata

**Location:** `devserver/schemas/configs/*.json` (converted from .py files)

**Structure:**
```json
{
  "pipeline": "simple_interception",
  "name": {
    "en": "Dadaism",
    "de": "Dadaismus"
  },
  "description": {
    "en": "Transform text into Dadaist artwork concepts with mockery, irony, and provocation",
    "de": "Verwandle Text in dadaistische Kunstkonzepte mit Spott, Ironie und Provokation"
  },
  "category": {
    "en": "Art Movements",
    "de": "Kunstbewegungen"
  },
  "instruction_type": "manipulation.creative",
  "context": "Dadaism - An early 20th-century art movement characterized by mockery, irony, nonsense, chance, and provocation. Artists: Hugo Ball, Marcel Duchamp, Hannah Höch, Tristan Tzara.",
  "parameters": {
    "temperature": 0.8,
    "top_p": 0.9,
    "aspect_ratio": "1:1"
  },
  "media_preferences": {
    "default_output": "image",
    "supported_types": ["image", "audio", "video"]
  },
  "meta": {
    "art_movement": "dadaism",
    "time_period": "1916-1924",
    "artists": ["Hugo Ball", "Marcel Duchamp", "Hannah Höch", "Tristan Tzara"],
    "legacy_source": "workflows/arts_and_heritage/ai4artsed_Dada_2506220140.json"
  }
}
```

**Key Fields:**

**Required:**
- `pipeline`: Reference to pipeline name
- `name`: Multilingual display names (en, de)
- `description`: Multilingual descriptions

**Optional:**
- `instruction_type`: Override pipeline default (e.g., `"manipulation.creative"`)
- `context`: Context information for prompt processing
- `parameters`: Override default parameters
- `media_preferences`: Media generation settings
- `category`: For UI organization
- `meta`: Additional metadata (legacy sources, artists, etc.)

**Config Examples:**

**Dada (Art Movement):**
```json
{
  "pipeline": "simple_interception",
  "name": {"en": "Dadaism", "de": "Dadaismus"},
  "instruction_type": "manipulation.creative",
  "context": "Dadaism - mockery, irony, nonsense, chance, provocation",
  "parameters": {"temperature": 0.8}
}
```

**Overdrive (Text Manipulation):**
```json
{
  "pipeline": "simple_interception",
  "name": {"en": "Overdrive", "de": "Übertreiben"},
  "instruction_type": "manipulation.amplify",
  "context": "Exaggeration and amplification to extreme levels",
  "parameters": {"temperature": 0.9}
}
```

**UK Youth Slang (Translation):**
```json
{
  "pipeline": "simple_interception",
  "name": {"en": "UK Youth Slang", "de": "Britische Jugendsprache"},
  "instruction_type": "translation.culture_sensitive",
  "context": "UK youth culture - urban slang, Drill, Grime, Trap",
  "parameters": {"temperature": 0.7}
}
```

---

## Instruction Types System

### Purpose
Reusable instruction templates for different processing types. Pipelines set defaults, configs can override.

### Location
`devserver/schemas/instruction_types.json`

### Structure
```json
{
  "translation": {
    "standard": {
      "instruction": "Translate the following text to English. CRITICAL RULES:\n1. Preserve ALL brackets exactly as they appear\n2. Translate with maximal semantic preservation\n3. Do not paraphrase or interpret\n4. Output ONLY the translated text",
      "description": "Standard translation with structure preservation",
      "parameters": {
        "temperature": 0.1,
        "top_p": 0.9
      }
    },
    "culture_sensitive": {
      "instruction": "Translate considering cultural context and idiomatic expressions. Preserve cultural significance while making text accessible in English.",
      "description": "Translation that considers cultural nuances",
      "parameters": {
        "temperature": 0.3
      }
    },
    "rigid": {
      "instruction": "Translate literally word-by-word without interpretation. Maintain exact structure even if result sounds unnatural.",
      "description": "Literal word-for-word translation",
      "parameters": {
        "temperature": 0.05
      }
    }
  },

  "manipulation": {
    "standard": {
      "instruction": "Transform the text according to the given context. Maintain core meaning while adapting style and tone.",
      "description": "Standard text transformation",
      "parameters": {
        "temperature": 0.7
      }
    },
    "creative": {
      "instruction": "Creatively interpret and transform the text. Take artistic liberties while honoring the spirit of the context.",
      "description": "Creative interpretation and transformation",
      "parameters": {
        "temperature": 0.8
      }
    },
    "amplify": {
      "instruction": "Exaggerate and amplify all aspects of the text to extreme levels. Push boundaries of expression.",
      "description": "Extreme amplification and exaggeration",
      "parameters": {
        "temperature": 0.9
      }
    },
    "analytical": {
      "instruction": "Analyze and restructure the text with logical precision. Maintain objectivity and clarity.",
      "description": "Analytical restructuring",
      "parameters": {
        "temperature": 0.3
      }
    }
  },

  "security": {
    "standard": {
      "instruction": "Check for safety violations including violence, explicit content, hate speech, and illegal activities. Flag violations with explanation.",
      "description": "Standard content safety check",
      "parameters": {
        "temperature": 0.1
      }
    },
    "strict": {
      "instruction": "Apply strict content filtering. Flag any potentially problematic content including mild profanity or controversial topics.",
      "description": "Strict content filtering (DSGVO compliant)",
      "parameters": {
        "temperature": 0.05
      }
    }
  },

  "image_analysis": {
    "formal": {
      "instruction": "Provide formal art historical analysis following Panofsky's methodology:\n1. Pre-iconographic description\n2. Iconographic analysis\n3. Iconological interpretation\nState interpretations as facts, not possibilities.",
      "description": "Formal art historical analysis",
      "parameters": {
        "temperature": 0.3
      }
    },
    "descriptive": {
      "instruction": "Describe visual elements in detail: objects, colors, composition, spatial relationships, textures, lighting.",
      "description": "Detailed visual description",
      "parameters": {
        "temperature": 0.2
      }
    },
    "iconographic": {
      "instruction": "Interpret symbolic meanings and cultural references. Identify artistic traditions, motifs, and cultural significance.",
      "description": "Symbolic and cultural interpretation",
      "parameters": {
        "temperature": 0.4
      }
    }
  },

  "prompt_optimization": {
    "image_generation": {
      "instruction": "Optimize text for image generation. Extract visual elements, describe composition, specify style and mood. Output as comma-separated tags.",
      "description": "Optimization for Stable Diffusion",
      "parameters": {
        "temperature": 0.5
      }
    },
    "audio_generation": {
      "instruction": "Optimize text for audio generation. Describe soundscape, mood, instruments, tempo, and atmosphere.",
      "description": "Optimization for Stable Audio",
      "parameters": {
        "temperature": 0.5
      }
    }
  }
}
```

### Usage in Configs

**Pipeline sets default:**
```json
// pipelines/simple_interception.json
{
  "defaults": {
    "instruction_type": "manipulation.standard"
  }
}
```

**Config can override:**
```json
// configs/dada.json
{
  "pipeline": "simple_interception",
  "instruction_type": "manipulation.creative"  // Overrides default
}
```

### Instruction Type Naming Convention

Format: `<category>.<variant>`

Examples:
- `translation.standard`
- `translation.culture_sensitive`
- `manipulation.creative`
- `manipulation.amplify`
- `security.strict`
- `image_analysis.formal`

---

## Data Flow

### User Request Processing

```
┌─────────────────────────────────────────────────────────────────────┐
│  1. USER INPUT                                                       │
│     - Text: "Ein Kamel trinkt Tee"                                  │
│     - Selected Config: "dada"                                        │
│     - Execution Mode: "eco" (Ollama) or "fast" (OpenRouter)         │
└─────────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────────┐
│  2. FRONTEND → BACKEND                                               │
│     POST /api/run_workflow                                           │
│     {                                                                 │
│       "config": "dada",                                              │
│       "prompt": "Ein Kamel trinkt Tee",                             │
│       "mode": "eco"                                                  │
│     }                                                                 │
└─────────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────────┐
│  3. SERVER-LEVEL PRE-PROCESSING                                      │
│     a) Parse hidden commands (#notranslate#, #image#, #audio#)     │
│     b) Safety check (DSGVO-compliant, local only)                   │
│     c) Translation (German → English, unless #notranslate#)         │
│        "Ein Kamel trinkt Tee" → "A camel drinks tea"               │
└─────────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────────┐
│  4. CONFIG RESOLUTION                                                │
│     a) Load config: configs/dada.json                                │
│     b) Read pipeline reference: "simple_interception"                │
│     c) Load pipeline: pipelines/simple_interception.json             │
│     d) Merge defaults + config overrides                             │
│     e) Resolve instruction_type: "manipulation.creative"             │
│        → Fetch from instruction_types.json                           │
└─────────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────────┐
│  5. PIPELINE EXECUTION                                               │
│     Pipeline: simple_interception                                    │
│     Chunks: ["prompt_interception"]                                  │
│                                                                       │
│     For each chunk:                                                  │
│       a) Load chunk template (chunks/prompt_interception.json)      │
│       b) Replace placeholders:                                       │
│          {{INSTRUCTION}} → instruction_types.manipulation.creative   │
│          {{CONTEXT}} → "Dadaism - mockery, irony, nonsense..."      │
│          {{INPUT_TEXT}} → "A camel drinks tea"                      │
│       c) Build backend request                                       │
│       d) Route to backend (Ollama or OpenRouter)                    │
│       e) Get response                                                │
└─────────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────────┐
│  6. CHUNK PROCESSING                                                 │
│     Backend: Ollama (local, mode="eco")                             │
│     Model: gemma2:9b                                                 │
│     Prompt:                                                          │
│       "Task:                                                         │
│        Creatively interpret and transform the text...                │
│                                                                       │
│        Context:                                                      │
│        Dadaism - mockery, irony, nonsense, chance...                │
│                                                                       │
│        Prompt:                                                       │
│        A camel drinks tea"                                           │
│                                                                       │
│     Response:                                                        │
│       "Das hydraulische Kamel nippte an flüssiger Melancholie"     │
└─────────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────────┐
│  7. POST-PROCESSING (DevServer Orchestration)                        │
│     a) Check hidden commands from step 3                             │
│     b) Determine media output:                                       │
│        - #image# tag → Generate image                                │
│        - #audio# tag → Generate audio                                │
│        - No tag → Default to image (per config preference)           │
│     c) If media requested:                                           │
│        - Generate ComfyUI workflow                                   │
│        - Submit to ComfyUI backend                                   │
│        - Get prompt_id                                               │
└─────────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────────┐
│  8. RESPONSE TO FRONTEND                                             │
│     {                                                                 │
│       "success": true,                                               │
│       "final_output": "Das hydraulische Kamel nippte...",           │
│       "media": {                                                     │
│         "type": "image",                                             │
│         "prompt_id": "abc123",                                       │
│         "url": "/api/media/image/abc123"                            │
│       },                                                             │
│       "backend_info": {                                              │
│         "backend": "ollama",                                         │
│         "model": "gemma2:9b"                                         │
│       }                                                               │
│     }                                                                 │
└─────────────────────────────────────────────────────────────────────┘
```

### Placeholder Resolution Flow

```
Config (dada.json):
  instruction_type: "manipulation.creative"
  context: "Dadaism - mockery..."

         ↓

Instruction Types (instruction_types.json):
  manipulation.creative.instruction: "Creatively interpret..."

         ↓

Chunk Template (prompt_interception.json):
  template: "Task:\n{{INSTRUCTION}}\n\nContext:\n{{CONTEXT}}\n\nPrompt:\n{{INPUT_TEXT}}"

         ↓

Resolved Prompt:
  "Task:
   Creatively interpret and transform the text...

   Context:
   Dadaism - mockery, irony, nonsense...

   Prompt:
   A camel drinks tea"
```

---

## File Structure

### Current Structure (To Be Refactored)
```
devserver/
└── schemas/
    ├── chunks/                      # ✅ Correct
    │   ├── translate.json
    │   ├── manipulate.json
    │   ├── prompt_interception.json
    │   └── comfyui_image_generation.json
    │
    ├── configs/                     # ❌ Wrong (Python files)
    │   ├── translate/
    │   │   └── standard.py
    │   ├── manipulate/
    │   │   ├── TEST_dadaismus.py
    │   │   └── jugendsprache.py
    │   └── prompt_interception/
    │       └── translation_en.py
    │
    ├── workflow_types/              # ⚠️ Wrong name (should be "pipelines")
    │   ├── simple_interception.json
    │   ├── simple_manipulation.json
    │   └── image_generation.json
    │
    ├── schema_data/                 # ❌ Wrong (unnecessary layer)
    │   ├── TEST_dadaismus.json
    │   ├── jugendsprache.json
    │   └── translation_en.json
    │
    └── engine/
        ├── schema_registry.py
        ├── pipeline_executor.py
        └── chunk_builder.py
```

### Correct Target Structure
```
devserver/
└── schemas/
    ├── chunks/                      # ✅ Primitives
    │   ├── translate.json
    │   ├── manipulate.json
    │   ├── prompt_interception.json
    │   └── comfyui_image_generation.json
    │
    ├── pipelines/                   # ✅ Structural templates (renamed)
    │   ├── simple_interception.json
    │   ├── simple_manipulation.json
    │   ├── image_generation.json
    │   └── translation_only.json
    │
    ├── configs/                     # ✅ User-facing JSON configs
    │   ├── dada.json
    │   ├── overdrive.json
    │   ├── jugendsprache.json
    │   ├── expressionism.json
    │   ├── bauhaus.json
    │   └── translation_en.json
    │
    ├── instruction_types.json       # ✅ Central instruction registry
    │
    └── engine/
        ├── config_loader.py         # ✅ New: Load configs + pipelines
        ├── instruction_resolver.py  # ✅ New: Resolve instruction types
        ├── pipeline_executor.py     # ⚠️ Update for new architecture
        └── chunk_builder.py         # ⚠️ Update for JSON configs
```

---

## JSON Schemas

### Chunk Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["name", "description", "template", "backend_type", "model"],
  "properties": {
    "name": {
      "type": "string",
      "description": "Unique chunk identifier"
    },
    "description": {
      "type": "string",
      "description": "Human-readable description"
    },
    "template": {
      "type": "string",
      "description": "Template string with {{PLACEHOLDERS}}"
    },
    "backend_type": {
      "type": "string",
      "enum": ["ollama", "openrouter", "comfyui", "direct"]
    },
    "model": {
      "type": "string",
      "description": "Default model name"
    },
    "parameters": {
      "type": "object",
      "description": "Default parameters for backend"
    },
    "meta": {
      "type": "object",
      "description": "Metadata for system use"
    }
  }
}
```

### Pipeline Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["name", "description", "chunks"],
  "properties": {
    "name": {
      "type": "string",
      "description": "Unique pipeline identifier"
    },
    "description": {
      "type": "string",
      "description": "Human-readable description"
    },
    "chunks": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Ordered list of chunk names"
    },
    "required_fields": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Fields that configs must provide"
    },
    "defaults": {
      "type": "object",
      "properties": {
        "instruction_type": {
          "type": "string",
          "pattern": "^[a-z_]+\\.[a-z_]+$",
          "description": "Default instruction type (e.g., manipulation.standard)"
        },
        "parameters": {
          "type": "object",
          "description": "Default parameters"
        }
      }
    },
    "meta": {
      "type": "object",
      "properties": {
        "input_type": {"type": "string"},
        "output_type": {"type": "string"},
        "pre_processing": {
          "type": "array",
          "items": {"type": "string", "enum": ["translation", "safety_check"]}
        }
      }
    }
  }
}
```

### Config Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["pipeline", "name", "description"],
  "properties": {
    "pipeline": {
      "type": "string",
      "description": "Reference to pipeline name"
    },
    "name": {
      "type": "object",
      "required": ["en", "de"],
      "properties": {
        "en": {"type": "string"},
        "de": {"type": "string"}
      },
      "description": "Multilingual display names"
    },
    "description": {
      "type": "object",
      "required": ["en", "de"],
      "properties": {
        "en": {"type": "string"},
        "de": {"type": "string"}
      },
      "description": "Multilingual descriptions"
    },
    "category": {
      "type": "object",
      "properties": {
        "en": {"type": "string"},
        "de": {"type": "string"}
      },
      "description": "Category for UI organization (optional)"
    },
    "instruction_type": {
      "type": "string",
      "pattern": "^[a-z_]+\\.[a-z_]+$",
      "description": "Override pipeline default (e.g., manipulation.creative)"
    },
    "context": {
      "type": "string",
      "description": "Context information for processing"
    },
    "parameters": {
      "type": "object",
      "description": "Override default parameters"
    },
    "media_preferences": {
      "type": "object",
      "properties": {
        "default_output": {
          "type": "string",
          "enum": ["text", "image", "audio", "video"]
        },
        "supported_types": {
          "type": "array",
          "items": {"type": "string"}
        }
      }
    },
    "meta": {
      "type": "object",
      "description": "Additional metadata"
    }
  }
}
```

### Instruction Types Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "patternProperties": {
    "^[a-z_]+$": {
      "type": "object",
      "patternProperties": {
        "^[a-z_]+$": {
          "type": "object",
          "required": ["instruction", "description"],
          "properties": {
            "instruction": {
              "type": "string",
              "description": "Instruction text"
            },
            "description": {
              "type": "string",
              "description": "Human-readable description"
            },
            "parameters": {
              "type": "object",
              "description": "Default parameters for this instruction type"
            }
          }
        }
      }
    }
  }
}
```

---

## Orchestration Layer

### DevServer as Central Authority

The DevServer (`workflow_routes.py`) acts as the orchestrating authority with the following responsibilities:

#### 1. Pre-Pipeline Processing
```python
# Before pipeline execution:
1. Parse hidden commands (#notranslate#, #image#, #audio#, #video#)
2. Safety check (DSGVO-compliant, always local)
3. Translation (German → English, unless #notranslate#)
```

#### 2. Config & Pipeline Resolution
```python
# Load and merge configurations:
1. Load config JSON (e.g., dada.json)
2. Load referenced pipeline (e.g., simple_interception.json)
3. Merge pipeline defaults + config overrides
4. Resolve instruction_type from instruction_types.json
```

#### 3. Pipeline Execution
```python
# Execute pipeline chunks sequentially:
1. For each chunk in pipeline:
   a. Load chunk template
   b. Replace placeholders (INSTRUCTION, CONTEXT, INPUT_TEXT)
   c. Route to appropriate backend (Ollama/OpenRouter/ComfyUI)
   d. Collect response
   e. Pass to next chunk (if any)
```

#### 4. Post-Pipeline Processing
```python
# After pipeline completes:
1. Check hidden commands for media generation
2. Determine output type:
   - #image# → Generate image via ComfyUI
   - #audio# → Generate audio via ComfyUI
   - #video# → Generate video via ComfyUI
   - No tag → Use config's media_preferences.default_output
3. Generate ComfyUI workflow if media requested
4. Submit to ComfyUI backend
5. Return response with text + media info
```

#### 5. Backend Routing (Execution Modes)

**Eco Mode (Local):**
- Backend: Ollama
- Privacy: Full (DSGVO compliant)
- Cost: Free
- Speed: Medium
- Use case: Development, privacy-sensitive

**Fast Mode (Cloud):**
- Backend: OpenRouter
- Privacy: Limited (external API)
- Cost: Paid
- Speed: Fast
- Use case: Production, performance-critical

**Model Selection:**
Task-based intelligent routing (see `model_selector.py`):
- `task:translation` → Smaller, precise models
- `task:standard` → General-purpose models
- `task:creative` → Larger, creative models
- `task:vision` → Always local (privacy)
- `task:security` → Always local (DSGVO)

---

## Migration from Legacy

### Legacy Workflow Structure (DO NOT TOUCH)

**Location:** `/workflows/` (outside devserver)

**Structure:** ComfyUI node-based JSON
```json
{
  "3": {
    "inputs": {"seed": 279417516731492, "steps": 25, ...},
    "class_type": "KSampler"
  },
  "42": {
    "inputs": {"input_prompt": ["41", 0], "style_prompt": "Transform to Dada..."},
    "class_type": "ai4artsed_prompt_interception"
  }
}
```

**Categories:**
- `/workflows/arts_and_heritage/` - Art movements (Dada, Bauhaus, etc.)
- `/workflows/aesthetics/` - Aesthetic transformations (Overdrive, etc.)
- `/workflows/semantics/` - Language transformations (Youth slang, etc.)
- `/workflows/flow/` - Complex flows (loops, inpainting, etc.)
- `/workflows/sound/` - Audio generation
- `/workflows/LLM/` - LLM-specific

**Total:** 63 legacy workflows

### Migration Strategy

**Phase 1: Document Legacy Features** ✅
- Audit all 63 workflows
- Extract core functionalities
- Identify unique features

**Phase 2: Create Equivalent Configs** (Current)
- Convert legacy workflows to configs
- Example: `ai4artsed_Dada_2506220140.json` → `configs/dada.json`
- Preserve metadata in `meta.legacy_source`

**Phase 3: Validate Equivalence**
- Test configs produce similar outputs to legacy
- Verify all features preserved
- Document any differences

**Phase 4: Coexistence**
- Both systems run in parallel
- Frontend offers both: legacy workflows + new configs
- User choice preserved

**Phase 5: Future Migration** (Optional)
- Gradually deprecate legacy system
- Migrate users to new system
- Keep legacy for research/reference

### Migration Mapping

| Legacy Workflow | New Config | Pipeline | Notes |
|----------------|------------|----------|-------|
| `ai4artsed_Dada_2506220140.json` | `dada.json` | `simple_interception` | Node 42 → instruction_type |
| `ai4artsed_Jugendsprache_2506122317.json` | `jugendsprache.json` | `simple_interception` | Context → UK youth slang |
| `ai4artsed_Overdrive_2506152234.json` | `overdrive.json` | `simple_interception` | Amplification instructions |
| `ai4artsed_Bauhaus_2509071932.json` | `bauhaus.json` | `simple_interception` | Bauhaus art context |
| (Add more as migrated) | | | |

---

## Implementation Checklist

### Phase 1: Architecture Documentation ✅
- [x] Document terminology
- [x] Document three-layer system
- [x] Document instruction types
- [x] Document data flow
- [x] Create JSON schemas

### Phase 2: File Structure Refactoring
- [ ] Rename `workflow_types/` → `pipelines/`
- [ ] Create `instruction_types.json`
- [ ] Convert Python configs → JSON configs
- [ ] Remove `schema_data/` layer (merge into configs)

### Phase 3: Code Refactoring
- [ ] Create `config_loader.py` (load configs + pipelines)
- [ ] Create `instruction_resolver.py` (resolve instruction types)
- [ ] Update `pipeline_executor.py` (new config flow)
- [ ] Update `chunk_builder.py` (JSON config support)
- [ ] Update `workflow_routes.py` (new config loading)

### Phase 4: Testing
- [ ] Unit tests for config loading
- [ ] Unit tests for instruction resolution
- [ ] Integration tests for full pipeline
- [ ] Test all existing configs
- [ ] Validate equivalence with legacy

### Phase 5: Documentation
- [ ] Update README for end-users
- [ ] Create config editing guide
- [ ] Create pipeline creation guide
- [ ] Document API endpoints

---

## Best Practices for LLM Assistants

### When Working on DevServer

1. **Never use "workflow" for devserver components**
   - Use: Config, Pipeline, Chunk
   - "Workflow" = Legacy system only

2. **Configs are user-facing**
   - Use clear, descriptive names
   - Provide multilingual metadata (en, de)
   - Include helpful descriptions

3. **Pipelines have no content**
   - Only structure (chunk sequence)
   - Only defaults
   - Never concrete instructions

4. **Instruction types are reusable**
   - One instruction type = many configs
   - Pipelines set defaults, configs override
   - Keep instruction types generic

5. **Preserve legacy metadata**
   - Always include `meta.legacy_source` when migrating
   - Document art movements, artists, time periods
   - Link to original workflows

6. **Test before committing**
   - Validate JSON syntax
   - Test full pipeline execution
   - Verify backend routing works

7. **Follow naming conventions**
   - Configs: `lowercase.json` (e.g., `dada.json`)
   - Pipelines: `snake_case.json` (e.g., `simple_interception.json`)
   - Chunks: `snake_case.json` (e.g., `prompt_interception.json`)
   - Instruction types: `category.variant` (e.g., `manipulation.creative`)

---

## Glossary

- **Backend:** Processing system (Ollama, OpenRouter, ComfyUI)
- **Chunk:** Primitive operation (building block)
- **Config:** User-facing content + metadata (JSON file)
- **Context:** Cultural/semantic information for processing
- **Execution Mode:** Backend selection (eco=local, fast=cloud)
- **Hidden Command:** Special tag in input (e.g., #notranslate#)
- **Instruction Type:** Reusable instruction template
- **Legacy Workflow:** Original ComfyUI node-based JSON
- **Orchestration:** Server-level coordination of processing
- **Pipeline:** Sequence of chunks (structural template)
- **Placeholder:** Variable in template (e.g., {{INPUT_TEXT}})
- **Pre-processing:** Server operations before pipeline (translation, safety)
- **Post-processing:** Server operations after pipeline (media generation)
- **Schema:** ❌ Deprecated term, use "Config" instead

---

**Document Version:** 1.0
**Last Updated:** 2025-10-18
**Status:** Architecture defined, implementation pending
