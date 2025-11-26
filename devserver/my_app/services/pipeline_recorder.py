"""
LivePipelineRecorder - Stateful media recording system

Writes files immediately as entities appear, maintains state for frontend queries,
and self-describes expected outputs.

Replaces:
- execution_history/tracker.py (ExecutionTracker)
- my_app/services/media_storage.py (MediaStorage)

Migration Status (Session 37):
- Added download capabilities from MediaStorage (add_media_from_comfyui, add_media_from_url)
- Added utility methods (_detect_format_from_data, _get_image_dimensions)
- Now has complete media handling - no longer depends on MediaStorage for downloads
"""

import json
import logging
import requests
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from PIL import Image
from io import BytesIO

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
            # Binary content - detect format
            if metadata and "format" in metadata:
                ext = metadata["format"]
            else:
                # Auto-detect format from binary data
                # Extract media_type from entity_type ('output_video' → 'video')
                if entity_type.startswith('output_'):
                    media_type = entity_type.replace('output_', '')
                else:
                    media_type = 'image'  # Default for non-output entities

                ext = self._detect_format_from_data(content, media_type)
                logger.debug(f"[RECORDER] Auto-detected format '{ext}' for {entity_type} (media_type={media_type})")
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

    def save_prompt_id(self, prompt_id: str, media_type: str = 'image'):
        """
        Save ComfyUI prompt_id to metadata for SSE streaming.

        Args:
            prompt_id: ComfyUI prompt ID
            media_type: Type of media being generated
        """
        if 'comfyui_prompt_ids' not in self.metadata:
            self.metadata['comfyui_prompt_ids'] = []

        self.metadata['comfyui_prompt_ids'].append({
            'prompt_id': prompt_id,
            'media_type': media_type,
            'timestamp': datetime.now().isoformat()
        })

        self._save_metadata()
        logger.info(f"[RECORDER] Saved prompt_id {prompt_id} for {media_type}")

    def mark_complete(self):
        """Mark the pipeline run as complete."""
        self.set_state(5, "complete")
        logger.info(f"[RECORDER] Run {self.run_id} marked complete")

    async def download_and_save_from_comfyui(
        self,
        prompt_id: str,
        media_type: str,
        config: str,
        seed: Optional[int] = None
    ) -> Optional[str]:
        """
        Download media from ComfyUI and save as entity.

        Args:
            prompt_id: ComfyUI prompt ID
            media_type: Type of media ('image', 'audio', 'video')
            config: Output config name
            seed: Optional seed value used for generation

        Returns:
            Filename of saved entity, or None if failed
        """
        try:
            from my_app.services.comfyui_client import get_comfyui_client

            client = get_comfyui_client()

            # Check ComfyUI health before waiting
            is_healthy = await client.health_check()
            if not is_healthy:
                logger.error(f"[RECORDER] ✗ ComfyUI not responding before download attempt for {prompt_id}")
                return None

            # Wait for workflow completion (with polling + retry logic)
            # SD3.5 Large: ~18s, Flux1: ~25s on RTX 5090 → 90s timeout gives 3-5x headroom
            logger.info(f"[RECORDER] Waiting for ComfyUI workflow completion: {prompt_id}")
            history = await client.wait_for_completion(prompt_id, timeout=90)

            # Check if history was returned
            if not history:
                logger.error(f"[RECORDER] ✗ No history returned for {prompt_id} - workflow may have timed out or disappeared")
                return None

            # Get generated files
            if media_type == 'image':
                files = await client.get_generated_images(history)
            elif media_type in ['audio', 'music']:
                files = await client.get_generated_audio(history)
            elif media_type == 'video':
                files = await client.get_generated_video(history)
            elif media_type == '3d':
                files = await client.get_generated_3d(history)    
            else:
                logger.error(f"[RECORDER] ✗ Unsupported media type for ComfyUI: {media_type}")
                return None

            if not files:
                logger.error(f"[RECORDER] ✗ No {media_type} files found in ComfyUI history for {prompt_id}")
                logger.error(f"[RECORDER] History keys: {list(history.keys()) if history else 'None'}")
                return None

            # Download first file
            first_file = files[0]
            file_data = await client.get_image(
                filename=first_file['filename'],
                subfolder=first_file.get('subfolder', ''),
                folder_type=first_file.get('type', 'output')
            )

            if not file_data:
                logger.error(f"Failed to download {media_type} from ComfyUI: {prompt_id}")
                return None

            # Detect format
            file_format = self._detect_format_from_data(file_data, media_type)

            # Get dimensions for images
            metadata = {
                'config': config,
                'format': file_format,
                'backend': 'comfyui',
                'prompt_id': prompt_id
            }

            # Add seed if provided
            if seed is not None:
                metadata['seed'] = seed

            if media_type == 'image':
                width, height = self._get_image_dimensions_from_bytes(file_data)
                if width and height:
                    metadata['width'] = width
                    metadata['height'] = height

            # Save as entity
            filename = self.save_entity(
                entity_type=f'output_{media_type}',
                content=file_data,
                metadata=metadata
            )

            logger.info(f"[RECORDER] Downloaded and saved {media_type} from ComfyUI ({len(file_data)} bytes)")
            return filename

        except Exception as e:
            logger.error(f"[RECORDER] Error downloading from ComfyUI: {e}")
            return None

    async def download_and_save_from_swarmui(
        self,
        image_paths: list,
        media_type: str,
        config: str,
        seed: Optional[int] = None
    ) -> Optional[str]:
        """
        Download media from SwarmUI and save as entity.

        Args:
            image_paths: List of SwarmUI image paths (e.g., ["View/local/raw/2024-01-02/image.png"])
            media_type: Type of media ('image', 'audio', 'video')
            config: Output config name
            seed: Optional seed value used for generation

        Returns:
            Filename of saved entity, or None if failed
        """
        try:
            from my_app.services.swarmui_client import get_swarmui_client

            if not image_paths:
                logger.error(f"[RECORDER] ✗ No image paths provided for SwarmUI download")
                return None

            client = get_swarmui_client()

            # Download first image
            first_path = image_paths[0]
            logger.info(f"[RECORDER] Downloading from SwarmUI: {first_path}")

            file_data = await client.download_image(first_path)

            if not file_data:
                logger.error(f"Failed to download {media_type} from SwarmUI: {first_path}")
                return None

            # Detect format
            file_format = self._detect_format_from_data(file_data, media_type)

            # Get dimensions for images
            metadata = {
                'config': config,
                'format': file_format,
                'backend': 'swarmui',
                'image_path': first_path
            }

            # Add seed if provided
            if seed is not None:
                metadata['seed'] = seed

            if media_type == 'image':
                dims = self._get_image_dimensions_from_bytes(file_data)
                if dims[0] and dims[1]:
                    metadata['width'] = dims[0]
                    metadata['height'] = dims[1]

            # Save as entity
            filename = self.save_entity(
                entity_type=f"output_{media_type}",
                content=file_data,
                metadata=metadata
            )

            logger.info(f"[RECORDER] Downloaded and saved {media_type} from SwarmUI ({len(file_data)} bytes)")
            return filename

        except Exception as e:
            logger.error(f"[RECORDER] Error downloading from SwarmUI: {e}")
            return None

    async def download_and_save_from_url(
        self,
        url: str,
        media_type: str,
        config: str,
        seed: Optional[int] = None
    ) -> Optional[str]:
        """
        Download media from URL and save as entity.

        Args:
            url: URL to download from
            media_type: Type of media ('image', 'audio', 'video')
            config: Output config name
            seed: Optional seed value used for generation

        Returns:
            Filename of saved entity, or None if failed
        """
        try:
            # Download from URL
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            file_data = response.content

            # Detect backend from URL
            backend = 'api'
            if 'openrouter' in url or 'openai' in url:
                backend = 'gpt5'
            elif 'replicate' in url:
                backend = 'replicate'

            # Detect format
            file_format = self._detect_format_from_data(file_data, media_type)

            # Get dimensions for images
            metadata = {
                'config': config,
                'format': file_format,
                'backend': backend,
                'source_url': url
            }

            # Add seed if provided
            if seed is not None:
                metadata['seed'] = seed

            if media_type == 'image':
                width, height = self._get_image_dimensions_from_bytes(file_data)
                if width and height:
                    metadata['width'] = width
                    metadata['height'] = height

            # Save as entity
            filename = self.save_entity(
                entity_type=f'output_{media_type}',
                content=file_data,
                metadata=metadata
            )

            logger.info(f"[RECORDER] Downloaded and saved {media_type} from URL ({len(file_data)} bytes)")
            return filename

        except Exception as e:
            logger.error(f"[RECORDER] Error downloading from URL: {e}")
            return None

    def _detect_format_from_data(self, data: bytes, media_type: str) -> str:
        """
        Detect file format from binary data.

        Args:
            data: Binary file data
            media_type: Expected media type

        Returns:
            File format extension (e.g., 'png', 'jpg', 'mp3')
        """
        if media_type == 'image':
            try:
                img = Image.open(BytesIO(data))
                return img.format.lower() if img.format else 'png'
            except:
                return 'png'  # Default
        elif media_type in ['audio', 'music']:
            # Simple heuristic based on headers
            if data[:4] == b'RIFF':
                return 'wav'
            elif data[:3] == b'ID3' or data[:2] == b'\xff\xfb':
                return 'mp3'
            return 'wav'  # Default
        elif media_type == 'video':
            if data[:4] == b'RIFF' and data[8:12] == b'WEBP':
                return 'webp'
            elif len(data) >= 8 and data[4:8] == b'ftyp':
                return 'mp4'
            return 'mp4'  # Default
        else:
            return 'bin'  # Unknown

    def _get_image_dimensions_from_bytes(self, data: bytes) -> tuple[Optional[int], Optional[int]]:
        """
        Get image dimensions from binary data.

        Args:
            data: Binary image data

        Returns:
            (width, height) tuple, or (None, None) if unable to determine
        """
        try:
            img = Image.open(BytesIO(data))
            return img.width, img.height
        except:
            return None, None

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

    def save_workflow_json(self, workflow: Dict[str, Any], entity_type: str = 'workflow') -> str:
        """
        Save complete workflow JSON for reproducibility.

        This is used for legacy workflows to archive the complete workflow structure
        that was executed, enabling reproducibility and debugging.

        Args:
            workflow: Complete ComfyUI workflow JSON
            entity_type: Type of entity (default: 'workflow')

        Returns:
            Filename of saved workflow JSON
        """
        try:
            metadata = {
                'type': 'workflow_archive',
                'timestamp': datetime.now().isoformat(),
                'node_count': len(workflow) if isinstance(workflow, dict) else 0
            }

            filename = self.save_entity(
                entity_type=entity_type,
                content=workflow,  # save_entity handles dict → JSON conversion
                metadata=metadata
            )

            logger.info(f"[RECORDER] Saved workflow JSON with {metadata['node_count']} nodes")
            return filename

        except Exception as e:
            logger.error(f"[RECORDER] Error saving workflow JSON: {e}")
            raise

    # REMOVED: download_and_save_all_from_comfyui()
    # Legacy workflows now handled by legacy_workflow_service.py
    # Media files are downloaded by the service and passed as binary data to recorder


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
