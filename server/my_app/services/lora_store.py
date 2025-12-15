"""Utility helpers for persisting LoRA datasets and training jobs."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
from zipfile import BadZipFile, ZipFile

from werkzeug.utils import secure_filename

from config import LORA_DATASETS_DIR, LORA_JOBS_DIR, LORA_OUTPUTS_DIR, LORA_ROOT_DIR

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def ensure_directories() -> None:
    """Create all directories that are required for LoRA assets."""
    for directory in (LORA_ROOT_DIR, LORA_DATASETS_DIR, LORA_JOBS_DIR, LORA_OUTPUTS_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def _dataset_summary(dataset_dir: Path) -> Dict[str, object]:
    """Build a metadata summary for a dataset directory."""
    images_dir = dataset_dir / "images"
    if images_dir.is_dir():
        image_candidates = images_dir.rglob("*")
    else:
        image_candidates = dataset_dir.rglob("*")

    image_count = sum(1 for path in image_candidates if path.suffix.lower() in IMAGE_EXTENSIONS)
    metadata_file = dataset_dir / "metadata.jsonl"

    return {
        "id": dataset_dir.name,
        "path": str(dataset_dir.resolve()),
        "has_metadata": metadata_file.exists(),
        "image_count": image_count,
        "metadata_path": str(metadata_file.resolve()) if metadata_file.exists() else None,
        "created_at": datetime.fromtimestamp(dataset_dir.stat().st_ctime).isoformat(),
    }


def list_datasets() -> List[Dict[str, object]]:
    """Return all locally available LoRA datasets."""
    ensure_directories()
    datasets: List[Dict[str, object]] = []

    if not LORA_DATASETS_DIR.exists():
        return datasets

    for entry in sorted(LORA_DATASETS_DIR.iterdir()):
        if entry.is_dir():
            datasets.append(_dataset_summary(entry))
    return datasets


def save_dataset_archive(file_storage, dataset_name: str) -> Dict[str, object]:
    """Store an uploaded ZIP archive and extract it into the datasets directory."""
    ensure_directories()
    sanitized_name = secure_filename(dataset_name).lower()
    if not sanitized_name:
        raise ValueError("Dataset name must not be empty")

    target_dir = LORA_DATASETS_DIR / sanitized_name
    if target_dir.exists():
        raise FileExistsError(f"Dataset '{sanitized_name}' already exists")

    target_dir.mkdir(parents=True, exist_ok=False)

    suffix = Path(file_storage.filename or "").suffix.lower()
    if suffix != ".zip":
        target_dir.rmdir()
        raise ValueError("Only ZIP archives are supported for dataset uploads")

    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".zip")
    try:
        with os.fdopen(tmp_fd, "wb") as handle:
            shutil.copyfileobj(file_storage.stream, handle)

        try:
            with ZipFile(tmp_path) as archive:
                archive.extractall(target_dir)
        except BadZipFile as exc:
            target_dir.rmdir()
            raise ValueError("Uploaded file is not a valid ZIP archive") from exc
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    return _dataset_summary(target_dir)


def load_jobs() -> Dict[str, Dict[str, object]]:
    """Read job definitions from disk."""
    ensure_directories()
    jobs: Dict[str, Dict[str, object]] = {}

    if not LORA_JOBS_DIR.exists():
        return jobs

    for job_file in LORA_JOBS_DIR.glob("*.json"):
        with job_file.open("r", encoding="utf-8") as handle:
            job = json.load(handle)
            job_id = job.get("id") or job_file.stem
            job["id"] = job_id
            jobs[job_id] = job
    return jobs


def save_job(job: Dict[str, object]) -> None:
    """Persist a job definition to disk."""
    ensure_directories()
    job_id = job["id"]
    job_path = LORA_JOBS_DIR / f"{job_id}.json"
    with job_path.open("w", encoding="utf-8") as handle:
        json.dump(job, handle, indent=2, ensure_ascii=False)


def resolve_dataset(dataset_id: str) -> Tuple[str, Path]:
    """Resolve the dataset identifier to an absolute path."""
    ensure_directories()
    sanitized_id = secure_filename(dataset_id).lower()
    dataset_path = LORA_DATASETS_DIR / sanitized_id
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset '{sanitized_id}' not found")
    return sanitized_id, dataset_path


def dataset_info(dataset_id: str) -> Dict[str, object]:
    """Return metadata about a dataset and validate its presence."""
    ensure_directories()
    sanitized_id = secure_filename(dataset_id).lower()
    dataset_path = LORA_DATASETS_DIR / sanitized_id
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset '{sanitized_id}' not found")
    return _dataset_summary(dataset_path)


def default_output_dir(project_name: str) -> Path:
    """Return the default output directory for a LoRA project."""
    ensure_directories()
    sanitized = secure_filename(project_name).lower()
    return LORA_OUTPUTS_DIR / sanitized
