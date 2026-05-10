"""Shared utility helpers used across adapters and services."""
import os

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
    def cancel_task(task_type: str, reason: str = "cancel"):
        try:
            with open(f"cancel_{task_type}.flag", "w") as f:
                f.write(reason)
        except OSError:
            pass

    @staticmethod
    def is_cancelled(task_type: str) -> bool:
        return os.path.exists(f"cancel_{task_type}.flag")

    @staticmethod
    def get_cancel_reason(task_type: str) -> str:
        try:
            with open(f"cancel_{task_type}.flag", "r") as f:
                return f.read().strip()
        except OSError:
            return ""

    @staticmethod
    def clear_cancel(task_type: str):
        try:
            if TaskStateManager.is_cancelled(task_type):
                os.remove(f"cancel_{task_type}.flag")
        except OSError:
            pass
