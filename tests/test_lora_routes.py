from pathlib import Path
import shutil
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))
sys.path.append(str(ROOT_DIR / "server"))

from server.config import LORA_DATASETS_DIR  # noqa: E402
from server.my_app import create_app  # noqa: E402


class LoraTestClient:
    def __init__(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def post_job(self, payload):
        return self.client.post("/api/lora/jobs", json=payload)


def _prepare_dataset(name: str, with_image: bool = True) -> Path:
    target = LORA_DATASETS_DIR / name
    if target.exists():
        shutil.rmtree(target)
    images_dir = target / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    if with_image:
        (images_dir / "sample.png").write_bytes(b"\x89PNG")
    return target


def _cleanup_dataset(name: str) -> None:
    target = LORA_DATASETS_DIR / name
    if target.exists():
        shutil.rmtree(target)


def _base_payload(dataset_id: str) -> dict:
    return {
        "project_name": "demo-project",
        "base_model": "runwayml/stable-diffusion-v1-5",
        "dataset_id": dataset_id,
        "resolution": 512,
        "max_train_steps": 1000,
        "train_batch_size": 1,
        "gradient_accumulation_steps": 4,
        "learning_rate": 0.0001,
        "scheduler": "cosine",
    }


def test_rejects_empty_dataset():
    dataset_name = "empty-dataset"
    _prepare_dataset(dataset_name, with_image=False)
    client = LoraTestClient()

    try:
        response = client.post_job(_base_payload(dataset_name))
        assert response.status_code == 400
        assert b"no images" in response.data.lower()
    finally:
        _cleanup_dataset(dataset_name)


def test_rejects_out_of_range_resolution():
    dataset_name = "valid-dataset"
    _prepare_dataset(dataset_name, with_image=True)
    client = LoraTestClient()
    payload = _base_payload(dataset_name)
    payload["resolution"] = 128  # below minimum

    try:
        response = client.post_job(payload)
        assert response.status_code == 400
        assert b"resolution" in response.data.lower()
    finally:
        _cleanup_dataset(dataset_name)
