"""Shared utility helpers used across adapters and services."""


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
