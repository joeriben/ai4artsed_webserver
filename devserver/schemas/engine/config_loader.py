"""
Config Loader - Replaces schema_registry.py
Loads configs (user-facing) + pipelines (structural templates)
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)

@dataclass
class Pipeline:
    """Pipeline definition (structural template - NO content)"""
    name: str
    description: str
    chunks: List[str]
    required_fields: List[str] = None
    defaults: Dict[str, Any] = None
    meta: Dict[str, Any] = None

@dataclass
class Config:
    """Config definition (user-facing content + metadata)"""
    name: str  # Internal name (filename without .json)
    pipeline: str  # Pipeline reference
    display_name: Dict[str, str]  # Multilingual names {"en": "...", "de": "..."}
    description: Dict[str, str]  # Multilingual descriptions
    category: Optional[Dict[str, str]] = None
    context: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    media_preferences: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = None

@dataclass
class ResolvedConfig:
    """Resolved config - pipeline + config merged for execution"""
    name: str
    display_name: Dict[str, str]
    description: Dict[str, str]
    pipeline_name: str
    chunks: List[str]
    context: Optional[str]
    parameters: Dict[str, Any]
    media_preferences: Optional[Dict[str, Any]]
    meta: Dict[str, Any]

class ConfigLoader:
    """
    Config Loader - Central registry for configs and pipelines
    Replaces SchemaRegistry with new architecture
    """

    _instance: Optional['ConfigLoader'] = None
    _initialized: bool = False

    def __new__(cls) -> 'ConfigLoader':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.pipelines: Dict[str, Pipeline] = {}
            self.configs: Dict[str, Config] = {}
            self.resolved_configs: Dict[str, ResolvedConfig] = {}
            self.base_path: Optional[Path] = None
            ConfigLoader._initialized = True

    def initialize(self, schemas_path: Path) -> None:
        """Initialize loader and load all definitions"""
        self.base_path = schemas_path
        self._load_pipelines()
        self._load_configs()
        self._resolve_configs()
        logger.info(f"ConfigLoader initialized: {len(self.pipelines)} pipelines, {len(self.configs)} configs, {len(self.resolved_configs)} resolved")

    def _load_pipelines(self) -> None:
        """Load pipeline definitions from pipelines/*.json"""
        if not self.base_path:
            logger.error("ConfigLoader not initialized")
            return

        pipelines_path = self.base_path / "pipelines"
        if not pipelines_path.exists():
            logger.warning(f"Pipelines path not found: {pipelines_path}")
            return

        for pipeline_file in pipelines_path.glob("*.json"):
            try:
                pipeline = self._load_pipeline_file(pipeline_file)
                if pipeline:
                    self.pipelines[pipeline.name] = pipeline
                    logger.debug(f"Pipeline loaded: {pipeline.name}")
            except Exception as e:
                logger.error(f"Error loading pipeline {pipeline_file}: {e}")

    def _load_pipeline_file(self, pipeline_file: Path) -> Optional[Pipeline]:
        """Load single pipeline file"""
        try:
            with open(pipeline_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            return Pipeline(
                name=data.get('name', pipeline_file.stem),
                description=data.get('description', ''),
                chunks=data.get('chunks', []),
                required_fields=data.get('required_fields', []),
                defaults=data.get('defaults', {}),
                meta=data.get('meta', {})
            )
        except Exception as e:
            logger.error(f"Error parsing pipeline {pipeline_file}: {e}")
            return None

    def _load_configs(self) -> None:
        """Load config definitions from configs/*.json"""
        if not self.base_path:
            logger.error("ConfigLoader not initialized")
            return

        # Try configs first (new architecture), fall back to old structure
        configs_path = self.base_path / "configs"
        if not configs_path.exists():
            # Fallback: try old schema_data directory
            configs_path = self.base_path / "schema_data"
            logger.warning(f"Using legacy schema_data directory: {configs_path}")

        if not configs_path.exists():
            logger.warning(f"Configs path not found: {configs_path}")
            return

        for config_file in configs_path.glob("*.json"):
            try:
                config = self._load_config_file(config_file)
                if config:
                    self.configs[config.name] = config
                    logger.debug(f"Config loaded: {config.name}")
            except Exception as e:
                logger.error(f"Error loading config {config_file}: {e}")

    def _load_config_file(self, config_file: Path) -> Optional[Config]:
        """Load single config file"""
        try:
            logger.debug(f"Loading config file: {config_file}")
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.debug(f"JSON loaded successfully from {config_file}")

            # Support both new format and legacy format
            # IMPORTANT: When "name" field is a dict (multilingual), use filename as internal name
            json_name_field = data.get('name')
            if isinstance(json_name_field, dict):
                # name is multilingual, use filename as internal name
                config_name = config_file.stem
                display_name = json_name_field
            else:
                # name is string or missing, use as internal name
                config_name = json_name_field or config_file.stem
                display_name = {'en': config_name, 'de': config_name}

            logger.debug(f"Config name: {config_name}, display_name: {display_name}")

            # New format: "pipeline" field
            pipeline = data.get('pipeline')

            # Legacy format fallback: "workflow_type" field
            if not pipeline:
                pipeline = data.get('workflow_type')
                if pipeline:
                    logger.warning(f"Config {config_name} uses legacy 'workflow_type' field, should use 'pipeline'")

            if not pipeline:
                logger.error(f"Config {config_name} missing 'pipeline' field")
                return None

            # Extract description
            json_desc = data.get('description')
            if isinstance(json_desc, dict):
                description = json_desc
            else:
                description = {'en': '', 'de': ''}

            logger.debug(f"Creating Config object for {config_name}")

            return Config(
                name=config_name,
                pipeline=pipeline,
                display_name=display_name,
                description=description,
                category=data.get('category'),
                context=data.get('context'),
                parameters=data.get('parameters'),
                media_preferences=data.get('media_preferences'),
                meta=data.get('meta', {})
            )
        except Exception as e:
            logger.error(f"Error parsing config {config_file}: {e}")
            import traceback
            logger.debug(f"Traceback: {traceback.format_exc()}")
            return None

    def _resolve_configs(self) -> None:
        """Resolve configs with pipelines to create executable definitions"""
        for config_name, config in self.configs.items():
            pipeline = self.pipelines.get(config.pipeline)
            if not pipeline:
                logger.error(f"Pipeline '{config.pipeline}' for config '{config_name}' not found")
                continue

            # Merge pipeline defaults + config overrides
            parameters = {}
            if pipeline.defaults and 'parameters' in pipeline.defaults:
                parameters.update(pipeline.defaults['parameters'])
            if config.parameters:
                parameters.update(config.parameters)

            # Create resolved config
            resolved = ResolvedConfig(
                name=config.name,
                display_name=config.display_name,
                description=config.description,
                pipeline_name=config.pipeline,
                chunks=pipeline.chunks,
                context=config.context,
                parameters=parameters,
                media_preferences=config.media_preferences,
                meta={**(pipeline.meta or {}), **(config.meta or {})}
            )

            self.resolved_configs[config_name] = resolved
            logger.debug(f"Config resolved: {config_name} → {config.pipeline}")

    def get_config(self, name: str) -> Optional[ResolvedConfig]:
        """Get resolved config by name"""
        return self.resolved_configs.get(name)

    def list_configs(self) -> List[str]:
        """List all resolved config names"""
        return list(self.resolved_configs.keys())

    def list_pipelines(self) -> List[str]:
        """List all pipeline names"""
        return list(self.pipelines.keys())

    def get_pipeline(self, name: str) -> Optional[Pipeline]:
        """Get pipeline by name"""
        return self.pipelines.get(name)

    def is_available(self, name: str) -> bool:
        """Check if config is available"""
        return name in self.resolved_configs

# Singleton instance
config_loader = ConfigLoader()
