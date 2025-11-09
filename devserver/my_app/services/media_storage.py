"""
MediaStorageService - Unified media storage for all backends

Handles downloading and storing media from:
- ComfyUI (via prompt_id)
- API URLs (GPT-5, Flux, etc.)
- Base64 data

All media is stored in atomic run folders with comprehensive metadata.

Structure:
exports/json/
├── run_uuid_001/
│   │   ├── metadata.json
│   │   ├── input_text.txt
│   │   ├── transformed_text.txt
│   │   └── output_image.png
│   ├── run_uuid_002/
│   │   ├── metadata.json
│   │   ├── input_text.txt
│   │   └── output_audio.wav
"""
import logging
import uuid
import base64
import requests
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass, asdict, field
import json
from PIL import Image
from io import BytesIO

logger = logging.getLogger(__name__)

@dataclass
class MediaOutput:
    """Metadata for a single media output"""
    type: str  # image, audio, video, model3d
    filename: str  # e.g., output_image.png
    backend: str  # comfyui, gpt5, api, replicate
    config: str  # Output config name
    file_size_bytes: int
    format: str  # PNG, JPG, MP3, WAV, MP4, etc.

    # Media-specific metadata
    width: Optional[int] = None  # For images
    height: Optional[int] = None  # For images
    duration_seconds: Optional[float] = None  # For audio/video

@dataclass
class RunMetadata:
    """Comprehensive metadata for one pipeline run (atomic research unit)"""
    run_id: str
    user_id: Optional[str]
    timestamp: str
    schema: str  # Schema/pipeline name (e.g., "dada", "gpt5_image")
    execution_mode: str  # eco, fast, ultra

    # Input/output text
    input_text: str
    transformed_text: Optional[str] = None

    # Media outputs (can be multiple)
    outputs: List[MediaOutput] = field(default_factory=list)

    # Source tracking (for debugging, NOT for research)
    _source_type: Optional[str] = None  # url, comfyui, base64 (internal only)
    _source_data: Optional[str] = None  # URL or prompt_id (internal only)


class MediaStorageService:
    """Unified media storage service for all backends - Run-based atomic storage"""

    def __init__(self, storage_root: Path):
        """
        Initialize media storage service

        Args:
            storage_root: Root directory for media storage (e.g., BASE_DIR / "exports" / "json")
        """
        self.storage_root = Path(storage_root)
        self.storage_root.mkdir(exist_ok=True)

        # Flat run-based structure: runs go directly in storage_root
        # (no additional "runs" subdirectory - that was the OLD structure)
        self.runs_dir = self.storage_root

        logger.info(f"MediaStorageService initialized at {self.storage_root}")

    def _create_run_folder(self, run_id: str) -> Path:
        """Create a run folder and return its path"""
        run_folder = self.runs_dir / run_id
        run_folder.mkdir(exist_ok=True)
        return run_folder

    def _detect_format_from_data(self, data: bytes, media_type: str) -> str:
        """Detect file format from binary data"""
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
            if data[:4] == b'ftyp':
                return 'mp4'
            return 'mp4'  # Default
        else:
            return 'bin'  # Unknown

    def _get_image_dimensions(self, file_path: Path) -> tuple[Optional[int], Optional[int]]:
        """Get image dimensions if possible"""
        try:
            img = Image.open(file_path)
            return img.width, img.height
        except:
            return None, None

    def _save_text_file(self, run_folder: Path, filename: str, content: str):
        """Save text content to run folder"""
        file_path = run_folder / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    async def create_run(
        self,
        schema: str,
        execution_mode: str,
        input_text: str,
        transformed_text: Optional[str] = None,
        user_id: Optional[str] = None,
        run_id: Optional[str] = None
    ) -> RunMetadata:
        """
        Create a new pipeline run with atomic folder

        Args:
            schema: Schema/pipeline name
            execution_mode: eco, fast, or ultra
            input_text: Original input text
            transformed_text: Transformed text (if available yet)
            user_id: Optional user ID
            run_id: Optional run ID (otherwise generated)

        Returns:
            RunMetadata object
        """
        # Generate or use provided run_id
        if not run_id:
            run_id = str(uuid.uuid4())

        # Create run folder
        run_folder = self._create_run_folder(run_id)

        # Save text files
        self._save_text_file(run_folder, 'input_text.txt', input_text)
        if transformed_text:
            self._save_text_file(run_folder, 'transformed_text.txt', transformed_text)

        # Create metadata
        metadata = RunMetadata(
            run_id=run_id,
            user_id=user_id,
            timestamp=datetime.now().isoformat(),
            schema=schema,
            execution_mode=execution_mode,
            input_text=input_text,
            transformed_text=transformed_text
        )

        # Save metadata
        self._save_metadata(run_id, metadata)

        logger.info(f"Created run {run_id} ({schema}, {execution_mode})")
        return metadata

    async def add_media_from_comfyui(
        self,
        run_id: str,
        prompt_id: str,
        config: str,
        media_type: str = 'image'
    ) -> Optional[MediaOutput]:
        """
        Download media from ComfyUI and add to run

        Args:
            run_id: Run ID to add media to
            prompt_id: ComfyUI prompt ID
            config: Output config name
            media_type: Type of media

        Returns:
            MediaOutput if successful, None otherwise
        """
        try:
            from my_app.services.comfyui_client import get_comfyui_client

            client = get_comfyui_client()

            # Wait for workflow completion (with polling)
            logger.info(f"[MEDIA_STORAGE] Waiting for ComfyUI workflow completion: {prompt_id}")
            history = await client.wait_for_completion(prompt_id)

            # Get generated files
            if media_type == 'image':
                files = await client.get_generated_images(history)
            elif media_type in ['audio', 'music']:
                files = await client.get_generated_audio(history)
            else:
                logger.error(f"Unsupported media type for ComfyUI: {media_type}")
                return None

            if not files:
                logger.error(f"No {media_type} files found in ComfyUI history for {prompt_id}")
                return None

            # Download first file (TODO: Support multiple files)
            first_file = files[0]
            file_data = await client.get_image(
                filename=first_file['filename'],
                subfolder=first_file.get('subfolder', ''),
                folder_type=first_file.get('type', 'output')
            )

            if not file_data:
                logger.error(f"Failed to download {media_type} from ComfyUI: {prompt_id}")
                return None

            # Add media to run
            return await self._add_media_to_run(
                run_id=run_id,
                data=file_data,
                media_type=media_type,
                backend='comfyui',
                config=config,
                source_type='comfyui',
                source_data=prompt_id
            )

        except Exception as e:
            logger.error(f"Error adding ComfyUI media to run {run_id}: {e}")
            return None

    async def add_media_from_url(
        self,
        run_id: str,
        url: str,
        config: str,
        media_type: str = 'image'
    ) -> Optional[MediaOutput]:
        """
        Download media from URL and add to run

        Args:
            run_id: Run ID to add media to
            url: URL to download from
            config: Output config name
            media_type: Type of media

        Returns:
            MediaOutput if successful, None otherwise
        """
        try:
            # Download from URL
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            # Detect backend from URL
            backend = 'api'
            if 'openrouter' in url or 'openai' in url:
                backend = 'gpt5'
            elif 'replicate' in url:
                backend = 'replicate'

            return await self._add_media_to_run(
                run_id=run_id,
                data=response.content,
                media_type=media_type,
                backend=backend,
                config=config,
                source_type='url',
                source_data=url
            )

        except Exception as e:
            logger.error(f"Error adding URL media to run {run_id}: {e}")
            return None

    async def add_media_from_base64(
        self,
        run_id: str,
        base64_data: str,
        config: str,
        media_type: str = 'image',
        backend: str = 'api'
    ) -> Optional[MediaOutput]:
        """
        Decode base64 media and add to run

        Args:
            run_id: Run ID to add media to
            base64_data: Base64-encoded media
            config: Output config name
            media_type: Type of media
            backend: Backend name

        Returns:
            MediaOutput if successful, None otherwise
        """
        try:
            # Decode base64
            data = base64.b64decode(base64_data)

            return await self._add_media_to_run(
                run_id=run_id,
                data=data,
                media_type=media_type,
                backend=backend,
                config=config,
                source_type='base64',
                source_data='[base64 data]'
            )

        except Exception as e:
            logger.error(f"Error adding base64 media to run {run_id}: {e}")
            return None

    async def _add_media_to_run(
        self,
        run_id: str,
        data: bytes,
        media_type: str,
        backend: str,
        config: str,
        source_type: str,
        source_data: str
    ) -> Optional[MediaOutput]:
        """Internal method to add media to a run"""
        try:
            # Get run folder
            run_folder = self.runs_dir / run_id
            if not run_folder.exists():
                logger.error(f"Run folder not found: {run_id}")
                return None

            # Detect format
            file_format = self._detect_format_from_data(data, media_type)

            # Create filename (output_TYPE.format)
            filename = f"output_{media_type}.{file_format}"
            file_path = run_folder / filename

            # Write file
            with open(file_path, 'wb') as f:
                f.write(data)

            file_size = len(data)

            # Get dimensions for images
            width, height = None, None
            if media_type == 'image':
                width, height = self._get_image_dimensions(file_path)

            # Create media output metadata
            media_output = MediaOutput(
                type=media_type,
                filename=filename,
                backend=backend,
                config=config,
                file_size_bytes=file_size,
                format=file_format,
                width=width,
                height=height
            )

            # Load existing metadata
            metadata = self.get_metadata(run_id)
            if metadata:
                # Add to outputs list
                metadata.outputs.append(media_output)
                # Update source tracking
                metadata._source_type = source_type
                metadata._source_data = source_data
                # Save updated metadata
                self._save_metadata(run_id, metadata)

            logger.info(f"Added {media_type} to run {run_id} ({backend}, {file_size} bytes)")
            return media_output

        except Exception as e:
            logger.error(f"Error adding media to run {run_id}: {e}")
            return None

    def _save_metadata(self, run_id: str, metadata: RunMetadata):
        """Save metadata to run folder"""
        run_folder = self.runs_dir / run_id
        metadata_file = run_folder / 'metadata.json'

        # Convert to dict, filter out internal fields
        metadata_dict = {k: v for k, v in asdict(metadata).items() if not k.startswith('_')}

        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata_dict, f, indent=2, ensure_ascii=False)

    def get_metadata(self, run_id: str) -> Optional[RunMetadata]:
        """Get metadata for run"""
        metadata_file = self.runs_dir / run_id / 'metadata.json'
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Reconstruct MediaOutput objects
                outputs = [MediaOutput(**out) for out in data.get('outputs', [])]
                data['outputs'] = outputs
                return RunMetadata(**data)
        return None

    def get_media_path(self, run_id: str, filename: str) -> Optional[Path]:
        """Get file path for media in run"""
        file_path = self.runs_dir / run_id / filename
        if file_path.exists():
            return file_path
        return None

    def list_runs_by_user(self, user_id: str) -> list[RunMetadata]:
        """List all runs for a user"""
        results = []
        for run_folder in self.runs_dir.iterdir():
            if run_folder.is_dir():
                metadata = self.get_metadata(run_folder.name)
                if metadata and metadata.user_id == user_id:
                    results.append(metadata)
        return results


# Singleton instance
_media_storage_service: Optional[MediaStorageService] = None

def get_media_storage_service() -> MediaStorageService:
    """Get singleton media storage service"""
    global _media_storage_service
    if _media_storage_service is None:
        from config import JSON_STORAGE_DIR
        storage_root = JSON_STORAGE_DIR.parent / "json"  # exports/json
        _media_storage_service = MediaStorageService(storage_root)
    return _media_storage_service
