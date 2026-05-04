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
    "llm_model": "nvidia_nim/meta/llama-3.1-70b-instruct",
    "tts_engine": "edge",
    "fallback_tts": "edge",
    "fallback_llm": "gemini/gemini-2.5-flash",
    "fallback_llm_last_resort": "groq/llama-3.1-8b-instant",
}


def get_config() -> Dict[str, Any]:
    """
    Returns the project config from config.yaml, cached after first load.
    Falls back to safe defaults if the file is missing or malformed.
    Thread-safe: uses double-checked locking so concurrent callers don't
    each attempt to read the file.
    """
    global _config_cache
    if _config_cache:
        return _config_cache

    with _config_lock:
        # Second check inside the lock (double-checked locking pattern)
        if _config_cache:
            return _config_cache

        # Search for config.yaml starting from this file's location upwards
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
                _config_cache = {**_DEFAULTS, **loaded}
            except Exception:
                _config_cache = dict(_DEFAULTS)
        else:
            _config_cache = dict(_DEFAULTS)

    return _config_cache


def get_llm_model() -> str:
    """Shorthand: returns the configured primary LLM model string (NVIDIA NIM)."""
    return get_config().get("llm_model", _DEFAULTS["llm_model"])


def get_fallback_llm() -> str:
    """Returns the tier-2 fallback model (Gemini)."""
    return get_config().get("fallback_llm", _DEFAULTS["fallback_llm"])


def get_fallback_llm_last_resort() -> str:
    """Returns the tier-3 last-resort fallback model (Groq)."""
    return get_config().get("fallback_llm_last_resort", _DEFAULTS["fallback_llm_last_resort"])
