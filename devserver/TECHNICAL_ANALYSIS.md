# Vollständige technische Analyse: ChunkBuilder-System

## Architekturübersicht

Das `chunk_builder.py` Modul implementiert das Template+Config-System für die Schema-basierte Pipeline-Architektur. Es fungiert als zentrale Komponente zwischen JSON-Templates und Python-Konfigurationen.

## Klassen-Struktur

### 1. `ChunkTemplate` (@dataclass)
**Zweck**: Type-safe Definition eines Verarbeitungs-Templates
```python
@dataclass
class ChunkTemplate:
    name: str              # Template-Identifikator
    template: str          # Template-String mit {{PLACEHOLDER}}
    backend_type: str      # "ollama", "openrouter", "direct", "comfyui"
    model: str             # KI-Model-Name (z.B. "gemma2:9b")
    parameters: Dict       # Backend-spezifische Parameter
    placeholders: List[str] # Automatisch extrahierte Platzhalter
```
**Design-Pattern**: Immutable Data Transfer Object (DTO)

### 2. `ChunkConfig` (@dataclass)
**Zweck**: Konfigurationsdaten aus Python-Modulen
```python
@dataclass  
class ChunkConfig:
    instructions: str      # Manipulation-Instructions (aus INSTRUCTIONS)
    parameters: Dict       # Zusätzliche Parameter (aus PARAMETERS)
    metadata: Dict         # Metadaten (aus METADATA)
```
**Design-Pattern**: Configuration Object

### 3. `ChunkBuilder` (Hauptklasse)
**Zweck**: Template+Config→Backend-Request Builder
**Pattern**: Builder + Template Method + Factory

## Datenfluss-Analyse

### Initialisierung (`__init__`)
```
ChunkBuilder(schemas_path) 
→ _load_templates() → templates: Dict[str, ChunkTemplate]
→ _load_configs()   → configs: Dict[str, ChunkConfig]
```

### Template-Loading (`_load_templates()`)
```
/schemas/chunks/*.json 
→ _load_template_file()
→ JSON.parse()
→ regex.findall(r'\{\{([^}]+)\}\}') [Placeholder-Extraktion]
→ ChunkTemplate-Instanz
→ self.templates[name] = template
```
**Kritisch**: Automatische Placeholder-Erkennung durch Regex-Parsing

### Config-Loading (`_load_configs()`)
```
/schemas/configs/**/*.py (rekursiv)
→ _load_config_file()
→ importlib.util.spec_from_file_location() [Dynamischer Import]
→ getattr(module, 'INSTRUCTIONS'|'PARAMETERS'|'METADATA') 
→ ChunkConfig-Instanz
→ self.configs[relative_path] = config
```

**Fix**: Null-Check für `spec` und `spec.loader` hinzugefügt:
```python
if spec is None or spec.loader is None:
    logger.error(f"Kann Modul-Spec für {config_file} nicht erstellen")
    return None
```
**Problem behoben**: Pylance-Fehler durch fehlende Null-Checks

### Chunk-Erstellung (`build_chunk()`)
**Hauptmethode** - Template+Config→Backend-Request:
```
build_chunk(chunk_name, config_path, context)
→ template = self.templates.get(chunk_name)     [Template-Lookup]
→ config = self.configs.get(config_path)       [Config-Lookup]
→ _replace_placeholders(template, context, config) [String-Replacement]
→ chunk_request = {                            [Backend-Request Assembly]
    'backend_type': template.backend_type,
    'model': template.model,
    'prompt': processed_template,
    'parameters': merged_parameters,
    'metadata': merged_metadata
}
→ return chunk_request
```

### Placeholder-Replacement (`_replace_placeholders()`)
**Algorithmus**: String-basiertes Template-Processing
```python
replacements = {
    'INSTRUCTIONS': config.instructions,
    'INPUT_TEXT': context.get('input_text', ''),
    'PREVIOUS_OUTPUT': context.get('previous_output', ''),
    'USER_INPUT': context.get('user_input', ''),
    **context.get('custom_placeholders', {})
}

for placeholder, value in replacements.items():
    pattern = f'{{{{{placeholder}}}}}'  # {{PLACEHOLDER}}
    result = result.replace(pattern, str(value))
```

**Validation**: Unverwendete Placeholders werden geloggt
```python
remaining_placeholders = re.findall(r'\{\{([^}]+)\}\}', result)
if remaining_placeholders:
    logger.warning(f"Nicht ersetzte Placeholders: {remaining_placeholders}")
```

## Methodenanalyse

### Public Interface
1. **`build_chunk()`** - Haupt-Factory-Methode
2. **`validate_chunk_request()`** - Pre-Build-Validation
3. **`get_available_templates()`** - Template-Discovery
4. **`get_available_configs()`** - Config-Discovery
5. **`get_template_placeholders()`** - Metadata-Extraction

### Private Implementation
1. **`_load_templates()`** - JSON-Template-Parser
2. **`_load_template_file()`** - Single-File-Parser
3. **`_load_configs()`** - Python-Module-Loader
4. **`_load_config_file()`** - Dynamic-Import-Handler
5. **`_replace_placeholders()`** - String-Template-Engine

## Error-Handling-Analyse

### Template-Loading-Errors
```python
try:
    template = self._load_template_file(template_file)
    # ...
except Exception as e:
    logger.error(f"Fehler beim Laden von Template {template_file}: {e}")
```

### Config-Loading-Errors  
```python
try:
    # Dynamic import...
except Exception as e:
    logger.error(f"Fehler beim Importieren von {config_file}: {e}")
    return None
```

### Build-Time-Errors
```python
if not template:
    raise ValueError(f"Template '{chunk_name}' nicht gefunden")
if not config:
    raise ValueError(f"Config '{config_path}' nicht gefunden")
```

## Performance-Charakteristika

### Initialization-Time
- **Templates**: O(n) JSON-Parsing + Regex-Processing
- **Configs**: O(n) Dynamic-Imports (I/O-intensiv)

### Runtime-Performance  
- **Template-Lookup**: O(1) Dictionary-Access
- **Config-Lookup**: O(1) Dictionary-Access  
- **Placeholder-Replacement**: O(m*k) String-Replace-Operations

### Memory-Usage
- **Templates**: In-Memory-Cache aller JSON-Templates
- **Configs**: Imported-Modules bleiben in sys.modules

## Integration-Points

### Input-Dependencies
- **Path**: `schemas_path` → chunks/, configs/ Ordner
- **Templates**: JSON-Files mit `{{PLACEHOLDER}}` Syntax
- **Configs**: Python-Module mit INSTRUCTIONS/PARAMETERS/METADATA

### Output-Interface  
- **Backend-Request**: Dict für BackendRouter.process_request()
```python
{
    'backend_type': str,    # BackendType-Enum-kompatibel
    'model': str,          # Model-Identifier  
    'prompt': str,         # Processed-Template
    'parameters': Dict,    # Merged-Parameters
    'metadata': Dict       # Tracking-Information
}
```

## Potential Issues & Improvements

### 1. Dynamic-Import-Sicherheit
**Problem**: `exec_module()` führt beliebigen Code aus
**Lösung**: Sandbox oder restricted-Execution-Context

### 2. Template-Caching
**Problem**: Templates werden bei jeder Instanz neu geladen  
**Lösung**: Singleton-Pattern oder externe Cache-Layer

### 3. Placeholder-Performance
**Problem**: String.replace() für jeden Placeholder
**Lösung**: Template-Engine (Jinja2) oder compiled-Templates

### 4. Error-Recovery
**Problem**: Partial-Failures führen zu leeren Dictionaries
**Lösung**: Retry-Logic oder Fallback-Templates

## Integrationstest-Scenarios

1. **Template+Config-Matching**: `translate`+`jugendsprache.py`
2. **Placeholder-Completion**: Alle {{PLACEHOLDER}} ersetzt
3. **Backend-Compatibility**: Output-Format für BackendRouter  
4. **Error-Propagation**: Missing-Templates/Configs handling

Das System implementiert erfolgreich das Template+Config-Pattern und bietet eine saubere Trennung zwischen Prompts (Templates) und Manipulations-Instructions (Configs).
