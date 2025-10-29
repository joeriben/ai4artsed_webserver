"""
Chunk-Builder: Template-System mit Placeholder-Replacement
REFACTORED for new architecture (JSON configs)
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

class ChunkBuilder:
    """Builder für Template-basierte Chunks mit Placeholder-Replacement"""

    def __init__(self, schemas_path: Path):
        self.schemas_path = schemas_path
        self.templates: Dict[str, ChunkTemplate] = {}
        self._load_templates()

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

    def build_chunk(self,
                    chunk_name: str,
                    resolved_config: Any,  # ResolvedConfig from config_loader
                    context: Dict[str, Any],
                    execution_mode: str = 'eco') -> Dict[str, Any]:
        """
        Chunk mit Template und resolved config erstellen

        Args:
            chunk_name: Name of chunk template
            resolved_config: ResolvedConfig object from config_loader
            context: Execution context (input_text, previous_output, etc.)
            execution_mode: 'eco' (local) or 'fast' (cloud)
        """
        template = self.templates.get(chunk_name)
        if not template:
            raise ValueError(f"Template '{chunk_name}' nicht gefunden")

        # Get instruction text from config context (former metaprompt)
        instruction_text = resolved_config.context or ''

        # Build context for placeholder replacement
        replacement_context = {
            'INSTRUCTION': instruction_text,
            'INSTRUCTIONS': instruction_text,  # Backward compatibility alias
            'INPUT_TEXT': context.get('input_text', ''),
            'PREVIOUS_OUTPUT': context.get('previous_output', ''),
            'USER_INPUT': context.get('user_input', ''),
            **context.get('custom_placeholders', {}),
            **resolved_config.parameters  # Add config parameters for placeholder replacement
        }

        # Placeholder-Replacement in template
        processed_template = self._replace_placeholders(
            template.template,
            replacement_context
        )

        # Debug: Log the built prompt
        logger.debug(f"[CHUNK-BUILD] Chunk '{chunk_name}' prompt preview: {processed_template[:200]}...")

        # Model-Override: Check config.meta.model_override first, then template.model
        from .model_selector import model_selector
        base_model = resolved_config.meta.get('model_override') or template.model
        final_model = model_selector.select_model_for_mode(base_model, execution_mode)

        # Merge parameters: template params + config params (config overrides template)
        merged_parameters = {**template.parameters, **resolved_config.parameters}

        # Apply placeholder replacement to parameter values
        processed_parameters = self._replace_placeholders_in_dict(merged_parameters, replacement_context)

        # Chunk-Request zusammenstellen
        chunk_request = {
            'backend_type': template.backend_type,
            'model': final_model,
            'prompt': processed_template,
            'parameters': processed_parameters,
            'metadata': {
                'chunk_name': chunk_name,
                'config_name': resolved_config.name,
                'template_placeholders': template.placeholders,
                'execution_mode': execution_mode,
                'template_model': template.model,
                'final_model': final_model,
                **resolved_config.meta
            }
        }

        logger.debug(f"Chunk erstellt: {chunk_name} mit Config {resolved_config.name} (execution_mode: {execution_mode}, model: {final_model})")
        return chunk_request

    def _replace_placeholders(self, template: str, replacements: Dict[str, Any]) -> str:
        """Placeholder durch Werte ersetzen"""
        result = template

        # Placeholder ersetzen
        for placeholder, value in replacements.items():
            pattern = f'{{{{{placeholder}}}}}'
            result = result.replace(pattern, str(value))

        # Überprüfung auf nicht ersetzte Placeholders
        remaining_placeholders = re.findall(r'\{\{([^}]+)\}\}', result)
        if remaining_placeholders:
            logger.warning(f"Nicht ersetzte Placeholders: {remaining_placeholders}")

        return result

    def _replace_placeholders_in_dict(self, data: Dict[str, Any], replacements: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively replace placeholders in dictionary values"""
        result = {}

        for key, value in data.items():
            if isinstance(value, str):
                # Apply placeholder replacement to string values
                processed_value = value
                for placeholder, replacement in replacements.items():
                    pattern = f'{{{{{placeholder}}}}}'
                    processed_value = processed_value.replace(pattern, str(replacement))
                result[key] = processed_value
            elif isinstance(value, dict):
                # Recursively process nested dictionaries
                result[key] = self._replace_placeholders_in_dict(value, replacements)
            elif isinstance(value, list):
                # Process lists (in case there are string elements)
                result[key] = [
                    self._replace_placeholders(item, replacements) if isinstance(item, str) else item
                    for item in value
                ]
            else:
                # Keep non-string values as-is
                result[key] = value

        return result

    def get_available_templates(self) -> List[str]:
        """Liste aller verfügbaren Templates"""
        return list(self.templates.keys())

    def get_template_placeholders(self, template_name: str) -> Optional[List[str]]:
        """Placeholders für ein Template abrufen"""
        template = self.templates.get(template_name)
        return template.placeholders if template else None

    def validate_chunk_request(self, chunk_name: str, resolved_config: Any, context: Dict[str, Any]) -> List[str]:
        """Chunk-Request validieren und fehlende Daten auflisten"""
        errors = []

        template = self.templates.get(chunk_name)
        if not template:
            errors.append(f"Template '{chunk_name}' nicht gefunden")
            return errors

        # Required Placeholders prüfen
        required_context = ['input_text']
        for required in required_context:
            if required not in context:
                errors.append(f"Erforderlicher Context '{required}' fehlt")

        return errors
