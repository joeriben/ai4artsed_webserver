"""
LatentLabRecorder - Lightweight recording for Latent Lab experiments

Frontend-primary hybrid: Frontend POSTs parameter + result data after each
generation; this recorder writes to disk using the same folder structure
as LivePipelineRecorder / CanvasRecorder (exports/json/YYYY-MM-DD/device_id/run_xxx/).

Phase 1: Write to exports/json/ (consistent with Canvas).
Phase 2 (future): QDA-compatible research format in exports/research/.
"""

import base64
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class LatentLabRecorder:
    """
    Lightweight recorder for Latent Lab tool experiments.

    Key differences from LivePipelineRecorder:
    - No stage tracking, no expected_outputs, no progress
    - Receives pre-built data from frontend (parameters, results, base64 outputs)
    - One run per tab lifecycle (start on mount, end on unmount)
    """

    def __init__(
        self,
        run_id: str,
        latent_lab_tool: str,
        device_id: Optional[str] = None,
        user_id: str = 'anonymous',
        base_path: Optional[Path] = None,
    ):
        import uuid as uuid_module

        self.run_id = run_id
        self.latent_lab_tool = latent_lab_tool
        self.user_id = user_id
        self.device_id = device_id or f"lab_{uuid_module.uuid4().hex[:12]}"

        if base_path is None:
            from config import JSON_STORAGE_DIR
            base_path = JSON_STORAGE_DIR
        self.base_path = Path(base_path)

        # exports/json/YYYY-MM-DD/device_id/run_xxx/
        date_folder = datetime.now().strftime('%Y-%m-%d')
        self.run_folder = self.base_path / date_folder / self.device_id / run_id
        self.run_folder.mkdir(parents=True, exist_ok=True)

        # Subfolders
        self.final_folder = self.run_folder / "final"
        self.final_folder.mkdir(parents=True, exist_ok=True)
        self.prompting_folder = self.run_folder / "prompting_process"

        # Counters
        self.entity_sequence = 0
        self.prompting_sequence = 0

        # Metadata
        self.metadata: Dict[str, Any] = {
            "run_id": run_id,
            "timestamp": datetime.now().isoformat(),
            "type": "latent_lab",
            "latent_lab_tool": latent_lab_tool,
            "device_id": self.device_id,
            "user_id": user_id,
            "entities": [],
        }
        self._save_metadata()

        logger.info(f"[LAB_RECORDER] Initialized {latent_lab_tool} run {run_id}")

    def record(
        self,
        parameters: Dict[str, Any],
        results: Optional[Dict[str, Any]] = None,
        outputs: Optional[List[Dict[str, Any]]] = None,
        steps: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """
        Record one generation cycle.

        Args:
            parameters: Generation parameters (prompt, seed, cfg, etc.)
            results: Result metadata (seed, timing, statistics)
            outputs: Final outputs [{type, format, dataBase64}]
            steps: Intermediate steps [{format, dataBase64}] (e.g. denoising steps)
        """
        self.prompting_folder.mkdir(parents=True, exist_ok=True)

        # 1) Save parameters as JSON in prompting_process/
        self.prompting_sequence += 1
        params_filename = f"{self.prompting_sequence:03d}_parameters.json"
        params_path = self.prompting_folder / params_filename
        params_content = {
            "parameters": parameters,
            "results": results or {},
            "timestamp": datetime.now().isoformat(),
        }
        params_path.write_text(
            json.dumps(params_content, indent=2, ensure_ascii=False),
            encoding='utf-8',
        )

        # Track in entities
        self.entity_sequence += 1
        self.metadata["entities"].append({
            "sequence": self.entity_sequence,
            "type": "latent_lab_params",
            "filename": f"prompting_process/{params_filename}",
            "timestamp": datetime.now().isoformat(),
            "metadata": parameters,
        })

        # 2) Save intermediate steps in prompting_process/
        if steps:
            step_base = self.prompting_sequence
            for idx, step_data in enumerate(steps):
                fmt = step_data.get("format", "jpg")
                raw = base64.b64decode(step_data["dataBase64"])
                step_filename = f"{step_base + 1:03d}_step_{idx + 1:02d}.{fmt}"
                step_path = self.prompting_folder / step_filename
                step_path.write_bytes(raw)

                self.entity_sequence += 1
                self.metadata["entities"].append({
                    "sequence": self.entity_sequence,
                    "type": "latent_lab_step",
                    "filename": f"prompting_process/{step_filename}",
                    "timestamp": datetime.now().isoformat(),
                    "metadata": {"step_index": idx},
                })

            # Bump prompting_sequence past the step block
            self.prompting_sequence += 1

        # 3) Save final outputs in final/
        if outputs:
            for out in outputs:
                media_type = out.get("type", "image")
                fmt = out.get("format", "png")
                raw = base64.b64decode(out["dataBase64"])

                self.entity_sequence += 1
                out_filename = f"{self.entity_sequence:02d}_output_{media_type}.{fmt}"
                out_path = self.final_folder / out_filename
                out_path.write_bytes(raw)

                self.metadata["entities"].append({
                    "sequence": self.entity_sequence,
                    "type": f"output_{media_type}",
                    "filename": out_filename,
                    "timestamp": datetime.now().isoformat(),
                    "metadata": {"format": fmt},
                })

        self._save_metadata()
        logger.info(
            f"[LAB_RECORDER] Recorded generation "
            f"({len(steps or [])} steps, {len(outputs or [])} outputs)"
        )

    def complete(self) -> None:
        """Mark run as complete."""
        self.metadata["completed_at"] = datetime.now().isoformat()
        self.metadata["total_entities"] = len(self.metadata["entities"])
        self._save_metadata()
        logger.info(f"[LAB_RECORDER] Run {self.run_id} completed with {self.entity_sequence} entities")

    def _save_metadata(self) -> None:
        metadata_path = self.run_folder / "metadata.json"
        metadata_path.write_text(
            json.dumps(self.metadata, indent=2, ensure_ascii=False),
            encoding='utf-8',
        )


# ---------------------------------------------------------------------------
# Run ID generation (same pattern as pipeline_recorder.py)
# ---------------------------------------------------------------------------

def generate_run_id() -> str:
    """Chronologically sortable run ID."""
    return f"run_{int(time.time() * 1000)}_{os.urandom(3).hex()}"


# ---------------------------------------------------------------------------
# Active recorder registry
# ---------------------------------------------------------------------------

_active_recorders: Dict[str, LatentLabRecorder] = {}


def get_lab_recorder(run_id: str) -> Optional[LatentLabRecorder]:
    """Get an existing recorder by run_id."""
    return _active_recorders.get(run_id)


def create_lab_recorder(
    latent_lab_tool: str,
    device_id: Optional[str] = None,
    user_id: str = 'anonymous',
) -> LatentLabRecorder:
    """Create and register a new recorder."""
    run_id = generate_run_id()
    recorder = LatentLabRecorder(
        run_id=run_id,
        latent_lab_tool=latent_lab_tool,
        device_id=device_id,
        user_id=user_id,
    )
    _active_recorders[run_id] = recorder
    return recorder


def cleanup_lab_recorder(run_id: str) -> None:
    """Remove recorder from active registry."""
    if run_id in _active_recorders:
        del _active_recorders[run_id]
        logger.info(f"[LAB_RECORDER] Cleaned up recorder for {run_id}")
