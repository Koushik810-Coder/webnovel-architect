"""Shared utility helpers used across adapters and services."""
import os

# Absolute path to the project root (3 levels up from app/core/utils.py).
# Used to anchor cancel-flag files so they always land in the same place
# regardless of what CWD the process is launched from (Fix 10).
_PROJECT_ROOT: str = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)


def _flag_path(task_type: str) -> str:
    """Returns the absolute path for a cancel-flag file."""
    return os.path.join(_PROJECT_ROOT, f"cancel_{task_type}.flag")


def normalize_id(name: str) -> str:
    """
    Converts a display name (e.g., 'Lord Stark') to a graph node ID (e.g., 'lord_stark').

    Single source of truth — import from here instead of re-implementing inline.
    Used by ingest.py, rag.py, and anywhere else that builds character IDs.
    """
    return name.lower().replace(" ", "_")


def truncate_for_log(text: str, limit: int = 150) -> str:
    """
    Truncate *text* to *limit* characters for log output, stripping newlines.

    Used by both the LLM adapter and the TTS adapter so the helper lives in
    one place rather than being copy-pasted into each adapter module.
    """
    if not text:
        return ""
    text = text.replace("\n", " ").strip()
    return (text[:limit] + "..") if len(text) > limit else text


class TaskStateManager:
    """Centralizes flagfile management to prevent race conditions when cancelling async background UI tasks."""

    @staticmethod
    def cancel_task(task_type: str, reason: str = "cancel") -> None:
        try:
            with open(_flag_path(task_type), "w") as f:
                f.write(reason)
        except OSError:
            pass

    @staticmethod
    def is_cancelled(task_type: str) -> bool:
        return os.path.exists(_flag_path(task_type))

    @staticmethod
    def get_cancel_reason(task_type: str) -> str:
        try:
            with open(_flag_path(task_type), "r") as f:
                return f.read().strip()
        except OSError:
            return ""

    @staticmethod
    def clear_cancel(task_type: str) -> None:
        try:
            if TaskStateManager.is_cancelled(task_type):
                os.remove(_flag_path(task_type))
        except OSError:
            pass
