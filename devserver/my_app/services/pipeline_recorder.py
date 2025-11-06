"""
LivePipelineRecorder - Stateful media recording system

Writes files immediately as entities appear, maintains state for frontend queries,
and self-describes expected outputs.

Replaces:
- execution_history/tracker.py (ExecutionTracker)
- my_app/services/media_storage.py (MediaStorage)
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class LivePipelineRecorder:
    """
    Live stateful recorder that writes pipeline artifacts immediately to disk.

    Key features:
    1. Writes files immediately (not retroactively)
    2. Maintains current state for frontend queries
    3. Self-describes expected outputs upfront
    4. One folder per run with numbered files
    5. Single metadata.json with complete state
    """

    def __init__(
        self,
        run_id: str,
        config_name: str,
        execution_mode: str,
        safety_level: str,
        user_id: str = 'anonymous',
        base_path: Optional[Path] = None
    ):
        """
        Initialize recorder and create run folder.

        Args:
            run_id: Unique identifier for this pipeline run
            config_name: Schema/config name (e.g., "dada", "stillepost")
            execution_mode: Execution mode (e.g., "eco", "fast")
            safety_level: Safety level (e.g., "kids", "teens")
            user_id: User identifier
            base_path: Base directory for pipeline_runs/ (defaults to current dir)
        """
        self.run_id = run_id
        self.config_name = config_name
        self.execution_mode = execution_mode
        self.safety_level = safety_level
        self.user_id = user_id

        # Setup folder structure
        if base_path is None:
            base_path = Path.cwd()
        self.base_path = Path(base_path)
        self.run_folder = self.base_path / run_id
        self.run_folder.mkdir(parents=True, exist_ok=True)

        # Initialize state
        self.current_stage = 0
        self.current_step = "initialized"
        self.sequence_number = 0

        # Expected outputs based on standard pipeline
        self.expected_outputs = [
            "input",
            "translation",
            "safety",
            "interception",
            "safety_pre_output",
            "output_image"
        ]

        # Initialize metadata
        self.metadata = {
            "run_id": run_id,
            "timestamp": datetime.now().isoformat(),
            "config_name": config_name,
            "execution_mode": execution_mode,
            "safety_level": safety_level,
            "user_id": user_id,
            "expected_outputs": self.expected_outputs,
            "current_state": {
                "stage": self.current_stage,
                "step": self.current_step,
                "progress": "0/6"
            },
            "entities": []
        }

        # Write initial metadata
        self._save_metadata()

        logger.info(f"[RECORDER] Initialized run {run_id} in {self.run_folder}")

    def set_state(self, stage: int, step: str):
        """
        Update current pipeline state.

        Args:
            stage: Current stage number (1-5)
            step: Human-readable step description
        """
        self.current_stage = stage
        self.current_step = step

        # Update progress
        completed = len(self.metadata["entities"])
        total = len(self.expected_outputs)
        progress = f"{completed}/{total}"

        self.metadata["current_state"] = {
            "stage": stage,
            "step": step,
            "progress": progress
        }

        self._save_metadata()
        logger.info(f"[RECORDER] State updated: Stage {stage} - {step} ({progress})")

    def save_entity(
        self,
        entity_type: str,
        content: Union[str, bytes, dict],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Save an entity to disk immediately and update metadata.

        Args:
            entity_type: Type of entity (e.g., "input", "translation", "output_image")
            content: Entity content (text, bytes, or dict)
            metadata: Optional metadata about this entity

        Returns:
            Filename of saved entity
        """
        self.sequence_number += 1

        # Determine file extension based on content type
        if isinstance(content, bytes):
            # Binary content (image)
            ext = "png"  # Default to PNG for images
            if metadata and "format" in metadata:
                ext = metadata["format"]
        elif isinstance(content, dict):
            ext = "json"
        else:
            ext = "txt"

        # Create numbered filename
        filename = f"{self.sequence_number:02d}_{entity_type}.{ext}"
        filepath = self.run_folder / filename

        # Write file
        self._write_file(filepath, content)

        # Add to metadata
        entity_record = {
            "sequence": self.sequence_number,
            "type": entity_type,
            "filename": filename,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.metadata["entities"].append(entity_record)

        # Update progress in current_state
        completed = len(self.metadata["entities"])
        total = len(self.expected_outputs)
        self.metadata["current_state"]["progress"] = f"{completed}/{total}"

        self._save_metadata()

        logger.info(f"[RECORDER] Saved entity {self.sequence_number}: {entity_type} -> {filename}")
        return filename

    def save_error(
        self,
        stage: int,
        error_type: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Save an error entity.

        Args:
            stage: Stage where error occurred
            error_type: Type of error (e.g., "safety_blocked", "api_error")
            message: Error message
            details: Additional error details

        Returns:
            Filename of saved error entity
        """
        error_data = {
            "stage": stage,
            "error_type": error_type,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }

        return self.save_entity(
            entity_type="error",
            content=error_data,
            metadata={"stage": stage, "error_type": error_type}
        )

    def get_status(self) -> Dict[str, Any]:
        """
        Get current status for frontend queries.

        Returns:
            Status dictionary with current state and completed outputs
        """
        # Defensive: ensure entities field exists (backward compatibility)
        entities = self.metadata.get("entities", [])
        completed_outputs = [e["type"] for e in entities]

        # Determine next expected output
        next_expected = None
        for expected in self.expected_outputs:
            if expected not in completed_outputs:
                next_expected = expected
                break

        # Defensive: ensure current_state exists
        current_state = self.metadata.get("current_state", {
            "stage": 0,
            "step": "unknown",
            "progress": "0/0"
        })

        return {
            "run_id": self.run_id,
            "current_state": current_state,
            "expected_outputs": self.expected_outputs,
            "completed_outputs": completed_outputs,
            "next_expected": next_expected,
            "entities": entities
        }

    def get_entity_path(self, entity_type: str) -> Optional[Path]:
        """
        Get filesystem path for a specific entity type.

        Args:
            entity_type: Type of entity to find

        Returns:
            Path to entity file, or None if not found
        """
        for entity in self.metadata["entities"]:
            if entity["type"] == entity_type:
                return self.run_folder / entity["filename"]
        return None

    def mark_complete(self):
        """Mark the pipeline run as complete."""
        self.set_state(5, "complete")
        logger.info(f"[RECORDER] Run {self.run_id} marked complete")

    def _write_file(self, filepath: Path, content: Union[str, bytes, dict]):
        """
        Write content to file with appropriate encoding.

        Args:
            filepath: Path to write to
            content: Content to write
        """
        try:
            if isinstance(content, bytes):
                # Binary content (images)
                filepath.write_bytes(content)
            elif isinstance(content, dict):
                # JSON content
                filepath.write_text(json.dumps(content, indent=2, ensure_ascii=False))
            else:
                # Text content
                filepath.write_text(str(content), encoding='utf-8')
        except Exception as e:
            logger.error(f"[RECORDER] Failed to write {filepath}: {e}")
            raise

    def _save_metadata(self):
        """Save metadata.json to disk immediately."""
        metadata_path = self.run_folder / "metadata.json"
        try:
            metadata_path.write_text(
                json.dumps(self.metadata, indent=2, ensure_ascii=False),
                encoding='utf-8'
            )
        except Exception as e:
            logger.error(f"[RECORDER] Failed to save metadata: {e}")
            raise


# Singleton management
_active_recorders: Dict[str, LivePipelineRecorder] = {}


def get_recorder(
    run_id: str,
    config_name: Optional[str] = None,
    execution_mode: Optional[str] = None,
    safety_level: Optional[str] = None,
    user_id: str = 'anonymous',
    base_path: Optional[Path] = None
) -> LivePipelineRecorder:
    """
    Get or create a recorder for a specific run.

    Args:
        run_id: Unique run identifier
        config_name: Schema/config name (required for new recorders)
        execution_mode: Execution mode (required for new recorders)
        safety_level: Safety level (required for new recorders)
        user_id: User identifier
        base_path: Base directory for pipeline_runs/

    Returns:
        LivePipelineRecorder instance
    """
    if run_id in _active_recorders:
        return _active_recorders[run_id]

    if config_name is None or execution_mode is None or safety_level is None:
        raise ValueError("config_name, execution_mode, and safety_level required for new recorder")

    recorder = LivePipelineRecorder(
        run_id=run_id,
        config_name=config_name,
        execution_mode=execution_mode,
        safety_level=safety_level,
        user_id=user_id,
        base_path=base_path
    )
    _active_recorders[run_id] = recorder
    return recorder


def load_recorder(run_id: str, base_path: Optional[Path] = None) -> Optional[LivePipelineRecorder]:
    """
    Load an existing recorder from disk.

    Args:
        run_id: Run identifier to load
        base_path: Base directory for pipeline_runs/

    Returns:
        LivePipelineRecorder instance, or None if not found
    """
    if run_id in _active_recorders:
        return _active_recorders[run_id]

    if base_path is None:
        base_path = Path.cwd()

    metadata_path = Path(base_path) / run_id / "metadata.json"

    if not metadata_path.exists():
        logger.warning(f"[RECORDER] No metadata found for run {run_id}")
        return None

    try:
        metadata = json.loads(metadata_path.read_text())

        # Backward compatibility: handle old metadata format
        # Old format used "schema" instead of "config_name"
        config_name = metadata.get("config_name") or metadata.get("schema", "unknown")

        # Old format might not have safety_level
        safety_level = metadata.get("safety_level", "kids")

        # Old format should have execution_mode, but provide fallback
        execution_mode = metadata.get("execution_mode", "eco")

        # Recreate recorder from metadata
        recorder = LivePipelineRecorder(
            run_id=metadata["run_id"],
            config_name=config_name,
            execution_mode=execution_mode,
            safety_level=safety_level,
            user_id=metadata.get("user_id", "anonymous"),
            base_path=base_path
        )

        # Restore state (handle both old and new formats)
        # Ensure critical fields exist in metadata for backward compatibility
        if "entities" not in metadata:
            metadata["entities"] = []

        if "current_state" not in metadata:
            metadata["current_state"] = {
                "stage": 0,
                "step": "completed",
                "progress": "0/0"
            }

        if "expected_outputs" not in metadata:
            metadata["expected_outputs"] = recorder.expected_outputs

        # Now it's safe to restore metadata
        recorder.metadata = metadata

        # Restore internal state
        recorder.sequence_number = len(metadata["entities"])
        recorder.current_stage = metadata["current_state"].get("stage", 0)
        recorder.current_step = metadata["current_state"].get("step", "initialized")

        _active_recorders[run_id] = recorder
        logger.info(f"[RECORDER] Loaded existing run {run_id}")
        return recorder

    except Exception as e:
        logger.error(f"[RECORDER] Failed to load run {run_id}: {e}")
        return None
