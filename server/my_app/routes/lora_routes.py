"""API endpoints that power the LoRA orchestration interface."""

from __future__ import annotations

from datetime import datetime
from http import HTTPStatus
from typing import Dict, List
from uuid import uuid4

from flask import Blueprint, current_app, jsonify, request
from werkzeug.exceptions import BadRequest
from werkzeug.utils import secure_filename

from my_app.services.lora_store import (
    dataset_info,
    default_output_dir,
    ensure_directories,
    list_datasets,
    load_jobs,
    resolve_dataset,
    save_dataset_archive,
    save_job,
)

lora_bp = Blueprint("lora", __name__, url_prefix="/api/lora")

PRESET_BASE_MODELS: List[Dict[str, str]] = [
    {"id": "runwayml/stable-diffusion-v1-5", "label": "Stable Diffusion 1.5"},
    {"id": "stabilityai/stable-diffusion-xl-base-1.0", "label": "Stable Diffusion XL Base 1.0"},
    {"id": "SG161222/Realistic_Vision_V5.1_noVAE", "label": "Realistic Vision V5.1"},
]

PRESET_SCHEDULERS = [
    "constant",
    "constant_with_warmup",
    "cosine",
    "cosine_with_restarts",
    "linear",
    "polynomial",
]

PRESET_PROFILES: List[Dict[str, object]] = [
    {
        "id": "photo_quickstart",
        "label": "Fotostudio – Schnellstart",
        "recommended_dataset_size": "10–30 Motive",
        "description": "Ideal für kleine Portrait- oder Objektserien, wenn schnelle Ergebnisse wichtig sind.",
        "notes": [
            "Mittlere Detailtiefe bei 12 GB VRAM in ca. 10–15 Minuten",
            "Trainiert ausschließlich den UNet-Teil für stabile Farben",
        ],
        "defaults": {
            "resolution": 512,
            "max_train_steps": 1200,
            "train_batch_size": 1,
            "gradient_accumulation_steps": 4,
            "learning_rate": 1e-4,
            "scheduler": "cosine_with_restarts",
            "network_rank": 8,
            "network_alpha": 16,
            "mixed_precision": "fp16",
            "use_8bit_adam": True,
            "train_text_encoder": False,
            "seed": 42,
        },
    },
    {
        "id": "studio_balanced",
        "label": "Atelier – Detailtreue",
        "recommended_dataset_size": "30–75 Aufnahmen",
        "description": "Für stilistisch konsistente Fotoserien oder Kunstreproduktionen mit feinerem Detailanspruch.",
        "notes": [
            "Mehr Trainingsschritte für saubere Lichteindrücke",
            "Behält moderate Lernrate für geringes Rauschen",
        ],
        "defaults": {
            "resolution": 576,
            "max_train_steps": 2200,
            "train_batch_size": 1,
            "gradient_accumulation_steps": 6,
            "learning_rate": 7.5e-5,
            "scheduler": "cosine",
            "network_rank": 16,
            "network_alpha": 24,
            "mixed_precision": "fp16",
            "use_8bit_adam": True,
            "train_text_encoder": False,
            "seed": 42,
        },
    },
    {
        "id": "gallery_high_fidelity",
        "label": "Galerie – Feinabstimmung",
        "recommended_dataset_size": "75–150 Werke",
        "description": "Maximale Detailtreue für kuratierte Kunstsammlungen. Benötigt eine GPU mit mindestens 16 GB VRAM.",
        "notes": [
            "Trainiert zusätzlich den Text-Encoder für präzise Prompts",
            "Längeres Training – plane 30–40 Minuten ein",
        ],
        "defaults": {
            "resolution": 640,
            "max_train_steps": 3000,
            "train_batch_size": 1,
            "gradient_accumulation_steps": 8,
            "learning_rate": 5e-5,
            "scheduler": "cosine",
            "network_rank": 32,
            "network_alpha": 32,
            "mixed_precision": "fp16",
            "use_8bit_adam": True,
            "train_text_encoder": True,
            "seed": 42,
        },
    },
]

DEFAULT_PROFILE_ID = PRESET_PROFILES[0]["id"]


def _job_store() -> Dict[str, Dict[str, object]]:
    """Return the Flask app's in-memory LoRA job store."""
    if not hasattr(current_app, "lora_jobs"):
        current_app.lora_jobs = load_jobs()
    return current_app.lora_jobs


@lora_bp.before_app_request
def _prepare_directories() -> None:
    ensure_directories()


@lora_bp.route("/presets", methods=["GET"])
def get_presets():
    """Return preset values for the UI."""
    base_defaults = {
        "resolution": 512,
        "max_train_steps": 2000,
        "train_batch_size": 1,
        "gradient_accumulation_steps": 4,
        "learning_rate": 1e-4,
        "network_rank": 16,
        "network_alpha": 16,
        "mixed_precision": "fp16",
        "seed": 42,
        "scheduler": "cosine",
    }

    presets = {
        "base_models": PRESET_BASE_MODELS,
        "schedulers": PRESET_SCHEDULERS,
        "profiles": PRESET_PROFILES,
        "defaults": {"profile_id": DEFAULT_PROFILE_ID, **base_defaults},
    }
    return jsonify(presets)


@lora_bp.route("/datasets", methods=["GET"])
def list_available_datasets():
    """List datasets that can be used for training."""
    datasets = list_datasets()
    return jsonify({"datasets": datasets})


@lora_bp.route("/datasets", methods=["POST"])
def upload_dataset():
    """Upload a zipped dataset."""
    if "dataset" not in request.files:
        raise BadRequest("No dataset file supplied")

    dataset_file = request.files["dataset"]
    dataset_name = request.form.get("dataset_name") or dataset_file.filename
    if not dataset_name:
        raise BadRequest("Dataset name missing")

    try:
        dataset = save_dataset_archive(dataset_file, dataset_name)
    except FileExistsError as exc:
        raise BadRequest(str(exc)) from exc
    except ValueError as exc:
        raise BadRequest(str(exc)) from exc

    return jsonify({"dataset": dataset}), HTTPStatus.CREATED


@lora_bp.route("/jobs", methods=["GET"])
def list_jobs():
    """Return the list of stored training jobs."""
    jobs = sorted(_job_store().values(), key=lambda item: item.get("created_at", ""), reverse=True)
    return jsonify({"jobs": jobs})


def _parse_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in {"1", "true", "yes", "on"}
    return False


def _parse_int(payload: Dict[str, object], field: str) -> int:
    try:
        return int(payload[field])
    except (TypeError, ValueError, KeyError) as exc:
        raise BadRequest(f"{field} must be an integer value") from exc


def _parse_float(payload: Dict[str, object], field: str) -> float:
    try:
        return float(payload[field])
    except (TypeError, ValueError, KeyError) as exc:
        raise BadRequest(f"{field} must be a floating point value") from exc


def _validate_positive_range(name: str, value: int | float, minimum: int | float, maximum: int | float | None = None) -> None:
    if value < minimum:
        raise BadRequest(f"{name} must be at least {minimum}")
    if maximum is not None and value > maximum:
        raise BadRequest(f"{name} must not exceed {maximum}")


@lora_bp.route("/jobs", methods=["POST"])
def create_job():
    """Persist a new LoRA training job configuration."""
    payload = request.get_json(silent=True) or {}
    required_fields = [
        "project_name",
        "base_model",
        "dataset_id",
        "resolution",
        "max_train_steps",
        "train_batch_size",
        "gradient_accumulation_steps",
        "learning_rate",
    ]

    missing = [field for field in required_fields if field not in payload or payload[field] in (None, "")]
    if missing:
        raise BadRequest(f"Missing required fields: {', '.join(missing)}")

    project_name_raw = payload["project_name"].strip()
    project_name = secure_filename(project_name_raw).lower()
    if not project_name:
        raise BadRequest("Project name must contain alphanumeric characters")

    dataset_id = payload["dataset_id"]
    try:
        dataset_slug, dataset_path = resolve_dataset(dataset_id)
        dataset_meta = dataset_info(dataset_slug)
    except FileNotFoundError as exc:
        raise BadRequest(str(exc)) from exc
    if dataset_meta.get("image_count", 0) < 1:
        raise BadRequest("Dataset contains no images to train on")

    base_model = payload["base_model"].strip()
    instance_token = payload.get("instance_token", "").strip()

    resolution = _parse_int(payload, "resolution")
    max_train_steps = _parse_int(payload, "max_train_steps")
    train_batch_size = _parse_int(payload, "train_batch_size")
    gradient_accumulation_steps = _parse_int(payload, "gradient_accumulation_steps")
    learning_rate = _parse_float(payload, "learning_rate")

    _validate_positive_range("resolution", resolution, 256, 1536)
    _validate_positive_range("max_train_steps", max_train_steps, 1, 20000)
    _validate_positive_range("train_batch_size", train_batch_size, 1, 64)
    _validate_positive_range("gradient_accumulation_steps", gradient_accumulation_steps, 1, 128)
    _validate_positive_range("learning_rate", learning_rate, 1e-6, 1.0)

    network_rank = _parse_int({"network_rank": payload.get("network_rank", 16)}, "network_rank")
    network_alpha = _parse_int({"network_alpha": payload.get("network_alpha", network_rank)}, "network_alpha")
    mixed_precision = payload.get("mixed_precision", "fp16")
    scheduler = payload.get("scheduler") or "cosine"
    if scheduler not in PRESET_SCHEDULERS:
        raise BadRequest("Unknown scheduler; please pick one of the suggested options")
    seed = int(payload.get("seed", 42))
    validation_prompt = payload.get("validation_prompt", "").strip()
    use_8bit_adam = _parse_bool(payload.get("use_8bit_adam", True))
    train_text_encoder = _parse_bool(payload.get("train_text_encoder", False))

    output_dir_override = payload.get("output_dir")
    if output_dir_override:
        output_dir = default_output_dir(output_dir_override)
    else:
        output_dir = default_output_dir(project_name)

    command_parts = [
        "accelerate launch training/train_text_to_image_lora.py",
        f"  --pretrained_model_name_or_path=\"{base_model}\"",
        f"  --train_data_dir=\"{dataset_path}\"",
        f"  --resolution={resolution}",
        f"  --train_batch_size={train_batch_size}",
        f"  --gradient_accumulation_steps={gradient_accumulation_steps}",
        f"  --learning_rate={learning_rate}",
        f"  --lr_scheduler=\"{scheduler}\"",
        f"  --max_train_steps={max_train_steps}",
        f"  --output_dir=\"{output_dir}\"",
        f"  --rank={network_rank}",
        f"  --network_alpha={network_alpha}",
        f"  --mixed_precision={mixed_precision}",
        f"  --seed={seed}",
    ]

    if train_text_encoder:
        command_parts.append("  --train_text_encoder")
    if use_8bit_adam:
        command_parts.append("  --use_8bit_adam")
    if validation_prompt:
        command_parts.append(f"  --validation_prompt=\"{validation_prompt}\"")

    command = " \\\n".join(command_parts)

    job_id = uuid4().hex
    created_at = datetime.utcnow().isoformat() + "Z"

    job = {
        "id": job_id,
        "status": "pending",
        "display_name": project_name_raw,
        "project_name": project_name,
        "base_model": base_model,
        "dataset": {
            "id": dataset_slug,
            "path": str(dataset_path),
        },
        "resolution": resolution,
        "max_train_steps": max_train_steps,
        "train_batch_size": train_batch_size,
        "gradient_accumulation_steps": gradient_accumulation_steps,
        "learning_rate": learning_rate,
        "network_rank": network_rank,
        "network_alpha": network_alpha,
        "mixed_precision": mixed_precision,
        "scheduler": scheduler,
        "seed": seed,
        "instance_token": instance_token or None,
        "train_text_encoder": train_text_encoder,
        "use_8bit_adam": use_8bit_adam,
        "validation_prompt": validation_prompt or None,
        "output_dir": str(output_dir),
        "created_at": created_at,
        "command": command,
    }

    _job_store()[job_id] = job
    save_job(job)

    return jsonify({"job": job}), HTTPStatus.CREATED


@lora_bp.route("/jobs/<job_id>", methods=["GET"])
def get_job(job_id: str):
    """Return a single stored job."""
    job = _job_store().get(job_id)
    if job is None:
        raise BadRequest("Unknown job identifier")
    return jsonify(job)
