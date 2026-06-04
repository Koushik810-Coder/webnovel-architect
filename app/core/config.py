"""
Central config loader for Webnovel Architect.
Reads config.yaml from the project root once and caches it.
All services should call get_config() instead of hardcoding models.
"""
import os
import threading
import yaml
from typing import Dict, Any

_config_cache: Dict[str, Any] = {}
_config_lock = threading.Lock()

_DEFAULTS = {
    # 3-tier fallback chain: NIM → Gemini → Groq
    "llm_model": "nvidia_nim/meta/llama-3.3-70b-instruct",
    "tts_engine": "edge",
    "fallback_tts": "edge",
    "fallback_llm": "gemini/gemini-2.5-flash",
    "fallback_llm_last_resort": "groq/llama-3.3-70b-versatile",
}


def get_config() -> Dict[str, Any]:
    """
    Returns the project config from config.yaml.
    Reads the file directly every time to pick up live edits.
    Falls back to safe defaults if the file is missing or malformed.
    """
    search_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = None
    for _ in range(5):  # walk up at most 5 levels
        candidate = os.path.join(search_dir, "config.yaml")
        if os.path.exists(candidate):
            config_path = candidate
            break
        parent = os.path.dirname(search_dir)
        if parent == search_dir:
            break
        search_dir = parent

    if config_path:
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                loaded = yaml.safe_load(f) or {}
            return {**_DEFAULTS, **loaded}
        except Exception:
            return dict(_DEFAULTS)

    return dict(_DEFAULTS)


def get_llm_model() -> str:
    """Shorthand: returns the configured primary LLM model string (nvidia_nim/meta/llama-3.3-70b-instruct by default)."""
    return get_config().get("llm_model", _DEFAULTS["llm_model"])


def get_fallback_llm() -> str:
    """Returns the tier-2 fallback model (Gemini)."""
    return get_config().get("fallback_llm", _DEFAULTS["fallback_llm"])


def get_fallback_llm_last_resort() -> str:
    """Returns the tier-3 last-resort fallback model (Groq)."""
    return get_config().get("fallback_llm_last_resort", _DEFAULTS["fallback_llm_last_resort"])
