"""
Execution History Storage Service

Handles persistence of execution records to JSON files.

Storage Strategy:
- Format: JSON (human-readable, indented)
- Location: exports/pipeline_runs/
- Naming: exec_{timestamp}_{unique_id}.json
- Example: exec_20251103_143025_abc12345.json

Performance: All I/O happens AFTER pipeline completes (not during execution)

Created: 2025-11-03 (Session 20 - Phase 1)
Based on: docs/EXECUTION_TRACKER_ARCHITECTURE.md Section 5
"""

from pathlib import Path
import json
import logging
from typing import Optional, List

from .models import ExecutionRecord

logger = logging.getLogger(__name__)

# Storage directory
STORAGE_DIR = Path(__file__).parent.parent.parent / "exports" / "pipeline_runs"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def save_execution_record(record: ExecutionRecord):
    """
    Save execution record to JSON file

    File location: exports/pipeline_runs/{execution_id}.json
    Format: Human-readable JSON (indented, sorted keys)

    Args:
        record: ExecutionRecord to persist

    Raises:
        Exception: If file write fails (should be caught by tracker)
    """
    try:
        file_path = STORAGE_DIR / f"{record.execution_id}.json"

        # Convert to dict (dataclass → dict)
        record_dict = record.to_dict()

        # Write JSON (human-readable format)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(record_dict, f, indent=2, ensure_ascii=False, sort_keys=True)

        logger.info(f"[STORAGE] Saved execution record: {file_path}")
        logger.info(f"[STORAGE] Record contains {len(record.items)} items, {record.total_execution_time:.1f}s total")

    except Exception as e:
        logger.error(f"[STORAGE] Failed to save execution record {record.execution_id}: {e}")
        raise


def load_execution_record(execution_id: str) -> Optional[ExecutionRecord]:
    """
    Load execution record from JSON file

    Args:
        execution_id: Execution ID to load

    Returns:
        ExecutionRecord if found, None if not found

    Raises:
        Exception: If file read/parse fails
    """
    try:
        file_path = STORAGE_DIR / f"{execution_id}.json"

        if not file_path.exists():
            logger.warning(f"[STORAGE] Execution record not found: {execution_id}")
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            record_dict = json.load(f)

        # Convert dict → dataclass
        record = ExecutionRecord.from_dict(record_dict)

        logger.info(f"[STORAGE] Loaded execution record: {execution_id} ({len(record.items)} items)")
        return record

    except Exception as e:
        logger.error(f"[STORAGE] Failed to load execution record {execution_id}: {e}")
        return None


def list_execution_records(limit: int = 100, offset: int = 0) -> List[str]:
    """
    List execution IDs (sorted by creation time, newest first)

    Args:
        limit: Maximum number of IDs to return
        offset: Number of IDs to skip (for pagination)

    Returns:
        List of execution IDs
    """
    try:
        # Find all JSON files matching pattern
        files = sorted(
            STORAGE_DIR.glob("exec_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True  # Newest first
        )

        # Extract execution IDs (filename without .json)
        execution_ids = [f.stem for f in files[offset:offset+limit]]

        logger.info(f"[STORAGE] Listed {len(execution_ids)} execution records (limit={limit}, offset={offset})")
        return execution_ids

    except Exception as e:
        logger.error(f"[STORAGE] Failed to list execution records: {e}")
        return []


def delete_execution_record(execution_id: str) -> bool:
    """
    Delete execution record from storage

    Args:
        execution_id: Execution ID to delete

    Returns:
        True if deleted successfully, False otherwise
    """
    try:
        file_path = STORAGE_DIR / f"{execution_id}.json"

        if not file_path.exists():
            logger.warning(f"[STORAGE] Cannot delete, record not found: {execution_id}")
            return False

        file_path.unlink()
        logger.info(f"[STORAGE] Deleted execution record: {execution_id}")
        return True

    except Exception as e:
        logger.error(f"[STORAGE] Failed to delete execution record {execution_id}: {e}")
        return False


def get_storage_stats() -> dict:
    """
    Get storage statistics

    Returns:
        Dictionary with storage stats (total records, disk usage, etc.)
    """
    try:
        files = list(STORAGE_DIR.glob("exec_*.json"))
        total_size = sum(f.stat().st_size for f in files)

        return {
            'total_records': len(files),
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / 1024 / 1024, 2),
            'storage_dir': str(STORAGE_DIR)
        }

    except Exception as e:
        logger.error(f"[STORAGE] Failed to get storage stats: {e}")
        return {
            'total_records': 0,
            'total_size_bytes': 0,
            'total_size_mb': 0.0,
            'storage_dir': str(STORAGE_DIR),
            'error': str(e)
        }
