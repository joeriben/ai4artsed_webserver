"""
Output-Config Selector: Select default Output-Config based on media type and execution mode

Architecture Principle: Separation of Concerns
- Pre-pipeline configs (dada.json) suggest media type via media_preferences.default_output
- Pre-pipeline configs DO NOT choose specific models
- This module provides centralized default mapping: media_type + execution_mode → output_config
"""

import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class MediaOutput:
    """Structured tracking of generated media"""
    media_type: str  # "image", "audio", "music", "video"
    prompt_id: str  # ComfyUI queue ID or API reference
    output_mapping: Dict[str, Any]  # How to extract media (from Output-Chunk)
    config_name: str  # Which output config was used
    status: str  # "queued", "generating", "completed", "failed"
    metadata: Optional[Dict[str, Any]] = None  # Additional info


@dataclass
class ExecutionContext:
    """Track expected and actual media throughout execution"""
    config_name: str
    execution_mode: str  # "eco" or "fast"
    expected_media_type: str  # From pre-pipeline config.media_preferences.default_output
    generated_media: list  # List[MediaOutput]
    text_outputs: list  # List[str] - track text at each pipeline step

    def add_media(self, media: MediaOutput):
        """Add generated media to context"""
        self.generated_media.append(media)
        logger.info(f"[EXECUTION-CONTEXT] Added {media.media_type} media: {media.prompt_id} (status: {media.status})")

    def add_text_output(self, text: str):
        """Add text output from pipeline step"""
        self.text_outputs.append(text)
        logger.debug(f"[EXECUTION-CONTEXT] Added text output: {text[:100]}...")

    def get_latest_media(self) -> Optional[MediaOutput]:
        """Get most recently generated media"""
        return self.generated_media[-1] if self.generated_media else None

    def get_latest_text(self) -> str:
        """Get most recent text output"""
        return self.text_outputs[-1] if self.text_outputs else ""


class OutputConfigSelector:
    """Select default Output-Config based on media type and execution mode"""

    def __init__(self, schemas_path: Path):
        self.schemas_path = schemas_path
        self.defaults: Dict[str, Dict[str, Optional[str]]] = {}
        self._load_defaults()

    def _load_defaults(self):
        """Load output_config_defaults.json"""
        defaults_path = self.schemas_path / "output_config_defaults.json"

        if not defaults_path.exists():
            logger.error(f"output_config_defaults.json not found at {defaults_path}")
            return

        try:
            with open(defaults_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Filter out metadata fields (start with _)
            self.defaults = {
                media_type: modes
                for media_type, modes in data.items()
                if not media_type.startswith('_')
            }

            logger.info(f"Loaded output_config_defaults: {len(self.defaults)} media types")
            for media_type, modes in self.defaults.items():
                eco = modes.get('eco')
                fast = modes.get('fast')
                logger.debug(f"  {media_type}: eco={eco}, fast={fast}")

        except Exception as e:
            logger.error(f"Error loading output_config_defaults.json: {e}")
            self.defaults = {}

    def select_output_config(self, media_type: str, execution_mode: str = 'eco') -> Optional[str]:
        """
        Select default Output-Config for given media type and execution mode

        Args:
            media_type: "image", "audio", "music", "video", "text"
            execution_mode: "eco" (local) or "fast" (cloud)

        Returns:
            Output-Config name (e.g., "sd35_large") or None if not available
        """
        if media_type not in self.defaults:
            logger.warning(f"Unknown media type: {media_type}")
            return None

        modes = self.defaults[media_type]
        output_config = modes.get(execution_mode)

        if output_config:
            logger.info(f"[OUTPUT-CONFIG-SELECTOR] {media_type} + {execution_mode} → {output_config}")
        else:
            logger.warning(f"[OUTPUT-CONFIG-SELECTOR] No default for {media_type} + {execution_mode}")

        return output_config

    def get_available_media_types(self) -> list:
        """Get list of supported media types"""
        return list(self.defaults.keys())

    def is_media_type_supported(self, media_type: str, execution_mode: str = 'eco') -> bool:
        """Check if media type is supported for given execution mode"""
        if media_type not in self.defaults:
            return False

        output_config = self.defaults[media_type].get(execution_mode)
        return output_config is not None

    def get_supported_modes_for_media(self, media_type: str) -> list:
        """Get list of supported execution modes for given media type"""
        if media_type not in self.defaults:
            return []

        modes = self.defaults[media_type]
        return [mode for mode, config in modes.items() if not mode.startswith('_') and config is not None]


# Singleton instance
_selector_instance = None


def get_output_config_selector(schemas_path: Path = None) -> OutputConfigSelector:
    """Get singleton OutputConfigSelector instance"""
    global _selector_instance

    if _selector_instance is None:
        if schemas_path is None:
            # Default to schemas/ relative to this file
            schemas_path = Path(__file__).parent.parent
        _selector_instance = OutputConfigSelector(schemas_path)

    return _selector_instance
