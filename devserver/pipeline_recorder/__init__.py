"""
Pipeline Recorder - Live stateful media recording system

Replaces:
- execution_history/tracker.py (ExecutionTracker)
- my_app/services/media_storage.py (MediaStorage)

One system that writes immediately, maintains state, and self-describes.
"""

from .recorder import LivePipelineRecorder, get_recorder, load_recorder

__all__ = ['LivePipelineRecorder', 'get_recorder', 'load_recorder']
