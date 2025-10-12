"""
Schema-basierte Pipeline-Architektur für AI4ArtsEd
"""
from .engine.schema_registry import SchemaRegistry
from .engine.chunk_builder import ChunkBuilder
from .engine.backend_router import BackendRouter
from .engine.pipeline_executor import PipelineExecutor

__all__ = [
    'SchemaRegistry',
    'ChunkBuilder',
    'BackendRouter',
    'PipelineExecutor'
]
