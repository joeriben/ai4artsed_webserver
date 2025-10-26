"""
Schema-Registry: Pipeline-Typen und Schema-Daten Management
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)

@dataclass
class PipelineType:
    """Pipeline-Typ Definition (wiederverwendbare Verarbeitungsfolge)"""
    name: str
    description: str
    chunks: List[str]
    required_configs: List[str]
    config_mappings: Dict[str, str]  # Placeholder-Mappings {{CONFIG}}
    meta: Dict[str, Any]

@dataclass
class SchemaData:
    """Schema-Daten (spezifische Konfiguration für Pipeline-Typ)"""
    name: str
    description: str
    pipeline_type: str
    config_mappings: Dict[str, str]  # Echte Config-Pfade
    meta: Dict[str, Any]

@dataclass 
class SchemaDefinition:
    """Vollständige Schema-Definition (PipelineType + SchemaData aufgelöst)"""
    name: str
    description: str
    pipeline_type: str
    chunks: List[str]
    config_mappings: Dict[str, str]  # Aufgelöste Config-Pfade pro Chunk
    meta: Dict[str, Any]

class SchemaRegistry:
    """Registry für Pipeline-Typen und Schema-Daten"""
    
    _instance: Optional['SchemaRegistry'] = None
    _initialized: bool = False
    
    def __new__(cls) -> 'SchemaRegistry':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.pipeline_types: Dict[str, PipelineType] = {}
            self.schema_data: Dict[str, SchemaData] = {}
            self.resolved_schemas: Dict[str, SchemaDefinition] = {}
            self.base_path: Optional[Path] = None
            SchemaRegistry._initialized = True
    
    def initialize(self, schemas_path: Path) -> None:
        """Registry initialisieren und alle Definitionen laden"""
        self.base_path = schemas_path
        self._load_pipeline_types()
        self._load_schema_data()
        self._resolve_schemas()
        logger.info(f"Schema-Registry initialisiert: {len(self.pipeline_types)} Pipeline-Typen, {len(self.schema_data)} Schema-Daten, {len(self.resolved_schemas)} aufgelöste Schemas")
    
    def _load_pipeline_types(self) -> None:
        """Pipeline-Typen laden"""
        if not self.base_path:
            logger.error("Schema-Registry nicht initialisiert")
            return
            
        pipeline_types_path = self.base_path / "workflow_types"
        if not pipeline_types_path.exists():
            logger.warning(f"Pipeline-Typen-Pfad nicht gefunden: {pipeline_types_path}")
            return
            
        for type_file in pipeline_types_path.glob("*.json"):
            try:
                pipeline_type = self._load_pipeline_type_file(type_file)
                if pipeline_type:
                    self.pipeline_types[pipeline_type.name] = pipeline_type
                    logger.debug(f"Pipeline-Typ geladen: {pipeline_type.name}")
            except Exception as e:
                logger.error(f"Fehler beim Laden von Pipeline-Typ {type_file}: {e}")
    
    def _load_pipeline_type_file(self, type_file: Path) -> Optional[PipelineType]:
        """Einzelne Pipeline-Typ-Datei laden"""
        try:
            with open(type_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return PipelineType(
                name=data.get('name', type_file.stem),
                description=data.get('description', ''),
                chunks=data.get('chunks', []),
                required_configs=data.get('required_configs', []),
                config_mappings=data.get('config_mappings', {}),
                meta=data.get('meta', {})
            )
        except Exception as e:
            logger.error(f"Fehler beim Parsen von Pipeline-Typ {type_file}: {e}")
            return None
    
    def _load_schema_data(self) -> None:
        """Schema-Daten laden"""
        if not self.base_path:
            logger.error("Schema-Registry nicht initialisiert")
            return
            
        schema_data_path = self.base_path / "schema_data"
        if not schema_data_path.exists():
            logger.warning(f"Schema-Daten-Pfad nicht gefunden: {schema_data_path}")
            return
            
        for data_file in schema_data_path.glob("*.json"):
            try:
                schema_data = self._load_schema_data_file(data_file)
                if schema_data:
                    self.schema_data[schema_data.name] = schema_data
                    logger.debug(f"Schema-Daten geladen: {schema_data.name}")
            except Exception as e:
                logger.error(f"Fehler beim Laden von Schema-Daten {data_file}: {e}")
    
    def _load_schema_data_file(self, data_file: Path) -> Optional[SchemaData]:
        """Einzelne Schema-Daten-Datei laden"""
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return SchemaData(
                name=data.get('name', data_file.stem),
                description=data.get('description', ''),
                pipeline_type=data.get('workflow_type', ''),  # workflow_type in JSON → pipeline_type in Code
                config_mappings=data.get('config_mappings', {}),
                meta=data.get('meta', {})
            )
        except Exception as e:
            logger.error(f"Fehler beim Parsen von Schema-Daten {data_file}: {e}")
            return None
    
    def _resolve_schemas(self) -> None:
        """Schema-Daten mit Pipeline-Typen zu ausführbaren Schemas auflösen"""
        for schema_name, schema_data in self.schema_data.items():
            pipeline_type = self.pipeline_types.get(schema_data.pipeline_type)
            if not pipeline_type:
                logger.error(f"Pipeline-Typ '{schema_data.pipeline_type}' für Schema '{schema_name}' nicht gefunden")
                continue
            
            # Config-Mappings auflösen
            resolved_config_mappings = {}
            for chunk in pipeline_type.chunks:
                # Finde entsprechende Config für diesen Chunk
                config_key = f"{chunk}_config"
                if config_key in schema_data.config_mappings:
                    resolved_config_mappings[chunk] = schema_data.config_mappings[config_key]
                else:
                    logger.warning(f"Config-Mapping für Chunk '{chunk}' in Schema '{schema_name}' fehlt")
            
            # Aufgelöste Schema-Definition erstellen
            resolved_schema = SchemaDefinition(
                name=schema_data.name,
                description=schema_data.description,
                pipeline_type=schema_data.pipeline_type,
                chunks=pipeline_type.chunks,
                config_mappings=resolved_config_mappings,
                meta={**pipeline_type.meta, **schema_data.meta}
            )
            
            self.resolved_schemas[schema_name] = resolved_schema
            logger.debug(f"Schema aufgelöst: {schema_name} → {pipeline_type.name}")
    
    def get_schema(self, name: str) -> Optional[SchemaDefinition]:
        """Aufgelöstes Schema nach Name abrufen"""
        return self.resolved_schemas.get(name)
    
    def list_schemas(self) -> List[str]:
        """Liste aller aufgelösten Schema-Namen"""
        return list(self.resolved_schemas.keys())
    
    def list_pipeline_types(self) -> List[str]:
        """Liste aller Pipeline-Typen"""
        return list(self.pipeline_types.keys())
    
    def get_pipeline_type(self, name: str) -> Optional[PipelineType]:
        """Pipeline-Typ nach Name abrufen"""
        return self.pipeline_types.get(name)
    
    def register_schema(self, schema: SchemaDefinition) -> None:
        """Schema manuell registrieren"""
        self.resolved_schemas[schema.name] = schema
        logger.info(f"Schema registriert: {schema.name}")
    
    def is_available(self, name: str) -> bool:
        """Prüfen ob Schema verfügbar ist"""
        return name in self.resolved_schemas

# Singleton-Instanz
registry = SchemaRegistry()
