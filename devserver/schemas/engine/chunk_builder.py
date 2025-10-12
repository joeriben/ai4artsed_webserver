"""
Chunk-Builder: Template-System mit Placeholder-Replacement
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pathlib import Path
import json
import re
import logging

logger = logging.getLogger(__name__)

@dataclass
class ChunkTemplate:
    """Template für einen Verarbeitungs-Chunk"""
    name: str
    template: str
    backend_type: str
    model: str
    parameters: Dict[str, Any]
    placeholders: List[str]

@dataclass
class ChunkConfig:
    """Konfiguration für Chunk-Verarbeitung"""
    instructions: str
    parameters: Dict[str, Any]
    metadata: Dict[str, Any]
    # Prompt Interception Format
    task: str = ""
    context: str = ""

class ChunkBuilder:
    """Builder für Template-basierte Chunks mit Placeholder-Replacement"""
    
    def __init__(self, schemas_path: Path):
        self.schemas_path = schemas_path
        self.templates: Dict[str, ChunkTemplate] = {}
        self.configs: Dict[str, ChunkConfig] = {}
        self._load_templates()
        self._load_configs()
    
    def _load_templates(self) -> None:
        """Alle Chunk-Templates laden"""
        chunks_path = self.schemas_path / "chunks"
        if not chunks_path.exists():
            logger.warning(f"Chunks-Pfad nicht gefunden: {chunks_path}")
            return
        
        for template_file in chunks_path.glob("*.json"):
            try:
                template = self._load_template_file(template_file)
                if template:
                    self.templates[template.name] = template
                    logger.debug(f"Template geladen: {template.name}")
            except Exception as e:
                logger.error(f"Fehler beim Laden von Template {template_file}: {e}")
    
    def _load_template_file(self, template_file: Path) -> Optional[ChunkTemplate]:
        """Einzelnes Template-File laden"""
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Placeholders extrahieren
            template_str = data.get('template', '')
            placeholders = re.findall(r'\{\{([^}]+)\}\}', template_str)
            
            return ChunkTemplate(
                name=data.get('name', template_file.stem),
                template=template_str,
                backend_type=data.get('backend_type', 'ollama'),
                model=data.get('model', ''),
                parameters=data.get('parameters', {}),
                placeholders=placeholders
            )
            
        except Exception as e:
            logger.error(f"Fehler beim Parsen von {template_file}: {e}")
            return None
    
    def _load_configs(self) -> None:
        """Alle Konfigurationen laden"""
        configs_path = self.schemas_path / "configs"
        if not configs_path.exists():
            logger.warning(f"Configs-Pfad nicht gefunden: {configs_path}")
            return
        
        # Rekursiv alle Python-Module als Configs laden
        for config_file in configs_path.rglob("*.py"):
            if config_file.name == "__init__.py":
                continue
                
            try:
                config = self._load_config_file(config_file)
                if config:
                    config_key = str(config_file.relative_to(configs_path)).replace('.py', '').replace('/', '.')
                    self.configs[config_key] = config
                    logger.debug(f"Config geladen: {config_key}")
            except Exception as e:
                logger.error(f"Fehler beim Laden von Config {config_file}: {e}")
    
    def _load_config_file(self, config_file: Path) -> Optional[ChunkConfig]:
        """Einzelne Config-Datei laden"""
        try:
            # Python-Modul dynamisch importieren - mit Null-Check
            import importlib.util
            spec = importlib.util.spec_from_file_location("config_module", config_file)
            if spec is None or spec.loader is None:
                logger.error(f"Kann Modul-Spec für {config_file} nicht erstellen")
                return None
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Config-Daten extrahieren
            instructions = getattr(module, 'INSTRUCTIONS', '')
            parameters = getattr(module, 'PARAMETERS', {})
            metadata = getattr(module, 'METADATA', {})
            # Prompt Interception Format
            task = getattr(module, 'TASK', instructions)  # Fallback auf INSTRUCTIONS
            context = getattr(module, 'CONTEXT', '')
            
            return ChunkConfig(
                instructions=instructions,
                parameters=parameters,
                metadata=metadata,
                task=task,
                context=context
            )
            
        except Exception as e:
            logger.error(f"Fehler beim Importieren von {config_file}: {e}")
            return None
    
    def build_chunk(self, chunk_name: str, config_path: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Chunk mit Template und Config erstellen"""
        template = self.templates.get(chunk_name)
        if not template:
            raise ValueError(f"Template '{chunk_name}' nicht gefunden")
        
        config = self.configs.get(config_path)
        if not config:
            raise ValueError(f"Config '{config_path}' nicht gefunden")
        
        # Placeholder-Replacement
        processed_template = self._replace_placeholders(
            template.template,
            context,
            config
        )
        
        # Chunk-Request zusammenstellen
        chunk_request = {
            'backend_type': template.backend_type,
            'model': template.model,
            'prompt': processed_template,
            'parameters': {**template.parameters, **config.parameters},
            'metadata': {
                'chunk_name': chunk_name,
                'config_path': config_path,
                'template_placeholders': template.placeholders,
                **config.metadata
            }
        }
        
        logger.debug(f"Chunk erstellt: {chunk_name} mit Config {config_path}")
        return chunk_request
    
    def _replace_placeholders(self, template: str, context: Dict[str, Any], config: ChunkConfig) -> str:
        """Placeholder durch Werte ersetzen"""
        result = template
        
        # Standard-Replacements (Template + Prompt Interception)
        replacements = {
            'INSTRUCTIONS': config.instructions,
            'INPUT_TEXT': context.get('input_text', ''),
            'PREVIOUS_OUTPUT': context.get('previous_output', ''),
            'USER_INPUT': context.get('user_input', ''),
            # Prompt Interception Format
            'TASK': config.task,
            'CONTEXT': config.context,
            **context.get('custom_placeholders', {})
        }
        
        # Placeholder ersetzen
        for placeholder, value in replacements.items():
            pattern = f'{{{{{placeholder}}}}}'
            result = result.replace(pattern, str(value))
            
        # Überprüfung auf nicht ersetzte Placeholders
        remaining_placeholders = re.findall(r'\{\{([^}]+)\}\}', result)
        if remaining_placeholders:
            logger.warning(f"Nicht ersetzte Placeholders: {remaining_placeholders}")
        
        return result
    
    def get_available_templates(self) -> List[str]:
        """Liste aller verfügbaren Templates"""
        return list(self.templates.keys())
    
    def get_available_configs(self) -> List[str]:
        """Liste aller verfügbaren Configs"""
        return list(self.configs.keys())
    
    def get_template_placeholders(self, template_name: str) -> Optional[List[str]]:
        """Placeholders für ein Template abrufen"""
        template = self.templates.get(template_name)
        return template.placeholders if template else None

    def validate_chunk_request(self, chunk_name: str, config_path: str, context: Dict[str, Any]) -> List[str]:
        """Chunk-Request validieren und fehlende Daten auflisten"""
        errors = []
        
        template = self.templates.get(chunk_name)
        if not template:
            errors.append(f"Template '{chunk_name}' nicht gefunden")
            return errors
        
        config = self.configs.get(config_path)
        if not config:
            errors.append(f"Config '{config_path}' nicht gefunden")
            return errors
        
        # Required Placeholders prüfen
        required_context = ['input_text'] 
        for required in required_context:
            if required not in context:
                errors.append(f"Erforderlicher Context '{required}' fehlt")
        
        return errors
