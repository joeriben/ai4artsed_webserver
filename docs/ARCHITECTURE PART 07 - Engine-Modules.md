# DevServer Architecture

**Part 7: Engine Modules**

---


### Core Engine Architecture

```
schemas/engine/
├── config_loader.py          # Load configs and pipelines
├── chunk_builder.py           # Build chunks with placeholder replacement
├── pipeline_executor.py       # Execute complete pipelines
├── backend_router.py          # Route to appropriate backend
├── model_selector.py          # Task-based model selection
├── instruction_selector.py    # Instruction-type selection for 3-part prompts
├── comfyui_workflow_generator.py  # DEPRECATED - workflows now embedded in chunks
└── prompt_interception_engine.py  # DEPRECATED - replaced by pipeline system
```

---

### 1. config_loader.py

**Purpose:** Load and manage configs and pipelines

**Key Classes:**
```python
@dataclass
class Config:
    pipeline: str
    name: dict
    description: dict
    category: dict
    context: str              # Complete instruction text
    parameters: dict
    media_preferences: dict
    meta: dict
    display: dict
    tags: dict
    audience: dict

@dataclass
class Pipeline:
    name: str
    description: str
    chunks: List[str]
    required_configs: List[str]
    config_mappings: dict
    meta: dict

class ConfigLoader:
    def __init__(self, schemas_path: Path):
        self.configs: Dict[str, Config] = {}
        self.pipelines: Dict[str, Pipeline] = {}
        self._load_all()
```

**Key Methods:**
- `get_config(config_name: str) -> Config`
- `get_pipeline(pipeline_name: str) -> Pipeline`
- `list_configs() -> List[str]`
- `get_config_info(config_name: str) -> dict`

---

### 2. chunk_builder.py

**Purpose:** Build chunks with placeholder replacement

**Key Functionality:**
```python
class ChunkBuilder:
    def build_chunk(
        self,
        chunk_name: str,
        resolved_config: ResolvedConfig,
        context: dict
    ) -> ProcessedChunk:
        # 1. Get chunk template
        template = self.templates.get(chunk_name)

        # 2. Build replacement context
        instruction_text = resolved_config.context or ''
        replacement_context = {
            'INSTRUCTION': instruction_text,
            'INSTRUCTIONS': instruction_text,  # Backward compat
            'INPUT_TEXT': context.get('input_text', ''),
            'PREVIOUS_OUTPUT': context.get('previous_output', ''),
            'USER_INPUT': context.get('user_input', ''),
            **context.get('custom_placeholders', {})
        }

        # 3. Replace placeholders
        processed_template = self._replace_placeholders(
            template.template,
            replacement_context
        )

        # 4. Return processed chunk
        return ProcessedChunk(...)
```

**Note:** After consolidation, we removed `TASK` and `CONTEXT` placeholder aliases - they were redundant and caused duplication.

---

### 3. pipeline_executor.py

**Purpose:** Execute complete pipelines by orchestrating chunks

**Key Functionality:**
```python
class PipelineExecutor:
    async def execute_pipeline(
        self,
        config_name: str,
        input_text: str,
        user_input: str = None,
        mode: str = "eco"
    ) -> PipelineResult:
        # 1. Load config and pipeline
        config = self.config_loader.get_config(config_name)
        pipeline = self.config_loader.get_pipeline(config.pipeline)

        # 2. Execute chunks in sequence
        context = {'input_text': input_text, 'user_input': user_input or input_text}
        steps = []

        for i, chunk_name in enumerate(pipeline.chunks):
            # Build chunk
            chunk = self.chunk_builder.build_chunk(chunk_name, config, context)

            # Execute via backend router
            result = await self.backend_router.route(chunk, mode)

            # Update context for next chunk
            context['previous_output'] = result.output
            steps.append(result)

        # 3. Return complete result
        return PipelineResult(
            final_output=context['previous_output'],
            steps=steps,
            execution_time=...,
            metadata=...
        )
```

---

### 4. backend_router.py

**Purpose:** Route chunks to appropriate backends (Ollama, ComfyUI, OpenRouter)

**Key Functionality:**
```python
class BackendRouter:
    async def route(
        self,
        chunk: ProcessedChunk,
        mode: str = "eco"
    ) -> ChunkResult:
        backend_type = chunk.backend_type

        if backend_type == "ollama":
            return await self._route_ollama(chunk, mode)
        elif backend_type == "comfyui":
            return await self._route_comfyui(chunk)
        elif backend_type == "openrouter":
            return await self._route_openrouter(chunk)
        else:
            raise ValueError(f"Unknown backend: {backend_type}")

    async def _route_ollama(self, chunk, mode):
        # Model selection based on task_type
        if chunk.model.startswith('task:'):
            task_name = chunk.model.split(':', 1)[1]
            model = self.model_selector.select_model(task_name, mode)
        else:
            model = chunk.model

        # Execute via Ollama service
        return await ollama_service.generate(model, chunk.prompt, chunk.parameters)
```

**Backend Types:**
- `ollama`: Local LLM server (mistral-nemo, llama3.2, gemma2, etc.)
- `comfyui`: Local ComfyUI server (SD3.5, Flux1, Stable Audio, AceStep)
- `openrouter`: Cloud API (Claude, GPT-4, Gemini, etc.)

---

### 5. model_selector.py

**Purpose:** Task-based model selection (eco vs fast modes)

**Task Categories:**
```python
def _define_task_categories(self) -> Dict[str, Dict[str, str]]:
    return {
        "security": {
            "eco": "local/llama-guard-3-8b",
            "fast": "local/llama-guard-3-8b",  # Always local
            "description": "Content moderation"
        },
        "vision": {
            "eco": "local/llava:13b",
            "fast": "local/llava:13b",  # Always local (DSGVO)
            "description": "Image analysis"
        },
        "translation": {
            "eco": "local/qwen2.5-translator",
            "fast": "openrouter/anthropic/claude-3.5-haiku",
            "description": "Language translation"
        },
        "standard": {
            "eco": "local/mistral-nemo",
            "fast": "openrouter/mistralai/mistral-nemo",
            "description": "General text tasks"
        },
        "advanced": {
            "eco": "local/mistral-small:24b",
            "fast": "openrouter/google/gemini-2.5-pro",
            "description": "Complex reasoning, creativity"
        },
        "data_extraction": {
            "eco": "local/gemma3:4b",
            "fast": "openrouter/google/gemma-3-4b-it",
            "description": "Structured data extraction"
        }
    }
```

**Usage in Chunks:**
```json
{
  "model": "task:translation",  // Uses task-based selection
  "meta": {
    "task_type": "translation"
  }
}
```

**Execution Modes:**
- `eco`: Free local models (slower, privacy-preserving, DSGVO-compliant)
- `fast`: Paid cloud APIs (faster, higher quality, requires API keys)

---

### 6. instruction_selector.py

**Purpose:** Instruction-type selection for Prompt Interception (3-part prompts)

**Location:** `devserver/schemas/engine/instruction_selector.py`

**Pedagogical Background:**
The original ComfyUI `ai4artsed_prompt_interception` custom node used a 3-part prompt structure:
```python
full_prompt = (
    f"Task:\n{style_prompt.strip()}\n\n"
    f"Context:\n{input_context.strip()}\nPrompt:\n{input_prompt.strip()}"
)
```

This has been restored in DevServer's `manipulate` chunk with proper instruction-type system.

**Instruction Types:**
```python
INSTRUCTION_TYPES = {
    "artistic_transformation": {
        "description": "Transform prompt through artistic/cultural lens (Prompt Interception)",
        "default": """Transform the input_prompt into a description according to the instructions
defined in the input_context. Explicitely communicate the input_context as cultural cf. artistic
cf. intervening context. Also communicate genres/artistic traditions in a concrete way (i.e. is
it a dance, a photo, a painting, a song, a movie, a statue/sculpture? how should it be translated
into media?)

This is not a linguistic translation, but an aesthetic, semantic and structural transformation.
Be verbose!

Reconstruct all entities and their relations as specified, ensuring that:
- Each entity is retained – or respectively transformed – as instructed.
- Each relation is altered in line with the particular aesthetics, genre-typical traits, and logic
  of the "Context". Be explicit about visual aesthetics in terms of materials, techniques, composition,
  and overall atmosphere. Mention the input_context als cultural, cf. artistic, c.f intervening context
  in your OUTPUT explicitely.

Output only the transformed description as plain descriptive text. Be aware if the output is something
depicted (like a ritual or any situation) OR itself a cultural artefact (such as a specific drawing
technique). Describe accordingly. In your output, communicate which elements are most important for an
succeeding media generation.

DO NOT USE ANY META-TERMS, NO HEADERS, STRUCTURAL MARKERS WHATSOEVER. DO NOT EXPLAIN YOUR REASONING.
JUST PUT OUT THE TRANSFORMED DESCRIPTIVE TEXT."""
    },
    "passthrough": {
        "description": "No transformation - direct pass-through (for testing/debugging)",
        "default": """Output the input_prompt exactly as provided, with no modification or transformation."""
    }
}
```

**Usage in Pipelines:**
```json
{
  "name": "text_transformation",
  "instruction_type": "artistic_transformation",
  "chunks": ["manipulate"]
}
```

**Usage in Configs (Config-Level Override):**
```json
{
  "pipeline": "text_transformation",
  "instruction_type": "artistic_transformation",
  "context": "You are an artist working in the spirit of Dadaism...",
  "name": {"en": "Dadaism"}
}
```

**Priority System (Mirrors model_selector):**
1. **Config-level override**: `config.task_instruction` (custom instruction text)
2. **Pipeline-level default**: `pipeline.instruction_type` → looks up instruction in INSTRUCTION_TYPES
3. **System fallback**: "artistic_transformation"

**3-Part Prompt Structure:**
The `manipulate` chunk template implements the ComfyUI prompt_interception structure:
```
Task:
{{TASK_INSTRUCTION}}

Context:
{{CONTEXT}}

Prompt:
{{INPUT_TEXT}}
```

Where:
- `TASK_INSTRUCTION`: From instruction_selector (how to transform)
- `CONTEXT`: From config.context (artistic attitude/cultural background)
- `INPUT_TEXT`: User's input (the prompt to be transformed)

**Implementation:**
```python
# In chunk_builder.py
def _get_task_instruction(self, resolved_config, pipeline):
    from .instruction_selector import get_instruction

    # Check for custom override in config
    custom_instruction = getattr(resolved_config, 'task_instruction', None)

    # Get instruction_type from pipeline or config
    instruction_type = getattr(pipeline, 'instruction_type', 'artistic_transformation')

    return get_instruction(instruction_type, custom_instruction)
```

**Benefits:**
- **Transparency**: ENDUSER can see instruction in config/pipeline
- **Editability**: Configs can override instruction type
- **Consistency**: Mirrors model_selector architecture
- **Pedagogical**: Maintains original ComfyUI prompt_interception concept

---

### 7. comfyui_workflow_generator.py

**Status:** ⚠️ **DEPRECATED** - Will be removed in future cleanup

**Historical Purpose:** Generated ComfyUI workflows dynamically from Python templates

**Why Deprecated:**
- Output-Chunks now contain complete ComfyUI API workflows embedded in JSON
- No dynamic generation needed - server fills placeholders and submits directly
- Simplifies architecture - workflows are data, not code
- See "Output Chunk" documentation above for new approach

**Migration Path:**
- Extract workflows from `comfyui_workflow_generator.py` templates
- Convert to Output-Chunk JSON format with `input_mappings` and `output_mapping`
- Store in `schemas/chunks/output_*.json`
- Update backend_router to process Output-Chunks instead of calling generator

---

