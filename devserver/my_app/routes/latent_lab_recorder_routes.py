"""
Flask routes for Latent Lab recording.

Three endpoints:
  POST /api/latent-lab/record/start  — create a new run
  POST /api/latent-lab/record/save   — persist generation data
  POST /api/latent-lab/record/end    — finalize the run
"""

import logging
from flask import Blueprint, jsonify, request

from my_app.services.latent_lab_recorder import (
    create_lab_recorder,
    get_lab_recorder,
    cleanup_lab_recorder,
)

logger = logging.getLogger(__name__)

latent_lab_recorder_bp = Blueprint('latent_lab_recorder', __name__)


@latent_lab_recorder_bp.route('/api/latent-lab/record/start', methods=['POST'])
def start_recording():
    """
    Start a new Latent Lab recording run.

    Request JSON:
        latent_lab_tool: str  — tool identifier (e.g. "denoising_archaeology")
        device_id: str?       — browser device ID
    Response JSON:
        run_id: str
    """
    data = request.get_json(silent=True) or {}
    tool = data.get('latent_lab_tool')
    if not tool:
        return jsonify({"error": "latent_lab_tool is required"}), 400

    device_id = data.get('device_id')
    recorder = create_lab_recorder(latent_lab_tool=tool, device_id=device_id)

    logger.info(f"[LAB_RECORD] Started run {recorder.run_id} for {tool}")
    return jsonify({"run_id": recorder.run_id})


@latent_lab_recorder_bp.route('/api/latent-lab/record/save', methods=['POST'])
def save_recording():
    """
    Persist generation data for an active run.

    Request JSON:
        run_id: str
        parameters: dict      — generation parameters
        results: dict?         — result metadata (seed, timing)
        outputs: [{type, format, dataBase64}]?  — final media
        steps: [{format, dataBase64}]?          — intermediate steps
    """
    data = request.get_json(silent=True) or {}
    run_id = data.get('run_id')
    if not run_id:
        return jsonify({"error": "run_id is required"}), 400

    recorder = get_lab_recorder(run_id)
    if not recorder:
        return jsonify({"error": f"No active run: {run_id}"}), 404

    parameters = data.get('parameters', {})
    results = data.get('results')
    outputs = data.get('outputs')
    steps = data.get('steps')

    recorder.record(
        parameters=parameters,
        results=results,
        outputs=outputs,
        steps=steps,
    )

    return jsonify({
        "status": "saved",
        "entity_count": len(recorder.metadata["entities"]),
    })


@latent_lab_recorder_bp.route('/api/latent-lab/record/end', methods=['POST'])
def end_recording():
    """
    Finalize and clean up a recording run.

    Request JSON:
        run_id: str
    """
    data = request.get_json(silent=True) or {}
    run_id = data.get('run_id')
    if not run_id:
        return jsonify({"error": "run_id is required"}), 400

    recorder = get_lab_recorder(run_id)
    if not recorder:
        # Already cleaned up or never existed — not an error
        return jsonify({"status": "already_ended"})

    recorder.complete()
    cleanup_lab_recorder(run_id)

    logger.info(f"[LAB_RECORD] Ended run {run_id}")
    return jsonify({"status": "completed"})
