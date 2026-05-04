import json
import time
import os
import itertools
import hashlib
import sqlite3
from typing import Any, Callable, Optional

from app.core.logger import get_logger
from app.core.config import get_llm_model
from app.core.utils import truncate_for_log as _truncate

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# 1.3 Persistent LLM prompt cache
# ---------------------------------------------------------------------------
# Cache location: $LLM_CACHE_DIR/llm_cache.db (defaults to project data dir)

def _get_cache_db_path() -> str:
    cache_dir = os.environ.get("LLM_CACHE_DIR", os.path.join("data", "_cache"))
    os.makedirs(cache_dir, exist_ok=True)
    return os.path.join(cache_dir, "llm_cache.db")


def _cache_key(prompt: str, model: str) -> str:
    return hashlib.sha256(f"{model}||{prompt}".encode()).hexdigest()


def _cache_get(key: str) -> "dict | None":
    """Return cached result or None.  Returns None immediately if LLM_CACHE_DIR is unset."""
    if "LLM_CACHE_DIR" not in os.environ:
        return None
    try:
        db = _get_cache_db_path()
        con = sqlite3.connect(db)
        con.execute(
            "CREATE TABLE IF NOT EXISTS llm_cache (key TEXT PRIMARY KEY, value TEXT)"
        )
        row = con.execute("SELECT value FROM llm_cache WHERE key=?", (key,)).fetchone()
        con.close()
        if row:
            return json.loads(row[0])
    except Exception as e:
        logger.debug(f"LLM cache read error (non-fatal): {e}")
    return None


def _cache_put(key: str, value: dict) -> None:
    """Write to cache.  No-op if LLM_CACHE_DIR is unset."""
    if "LLM_CACHE_DIR" not in os.environ:
        return
    try:
        db = _get_cache_db_path()
        con = sqlite3.connect(db)
        con.execute(
            "CREATE TABLE IF NOT EXISTS llm_cache (key TEXT PRIMARY KEY, value TEXT)"
        )
        con.execute(
            "INSERT OR REPLACE INTO llm_cache (key, value) VALUES (?, ?)",
            (key, json.dumps(value)),
        )
        con.commit()
        con.close()
    except Exception as e:
        logger.debug(f"LLM cache write error (non-fatal): {e}")

# --- API Key setup ---
# Groq key rotation (multiple keys supported via GROQ_API_KEY, GROQ_API_KEY_2, etc.)
_groq_keys = [v.strip() for k, v in os.environ.items() if k.startswith("GROQ_API_KEY") and v.strip()]
_groq_cycle = itertools.cycle(_groq_keys) if _groq_keys else None
if _groq_keys:
    logger.info(f"Initialized LLM Adapter with {len(_groq_keys)} Groq API keys for rotation.")

# NVIDIA NIM key (single key from env)
_nim_api_key = os.environ.get("NVIDIA_NIM_API_KEY", "").strip()
if _nim_api_key:
    logger.info("NVIDIA NIM API key found — NIM is available as primary LLM.")
else:
    logger.warning("NVIDIA_NIM_API_KEY not set — NIM calls will fail; Gemini/Groq will be used as fallback.")
# -------------------------



def _parse_json(content: str) -> dict:
    """Strip optional markdown fences and parse JSON. Raises on failure → triggers retry."""
    clean = content.replace("```json", "").replace("```", "").strip()
    return json.loads(clean)


def _run_with_retry(
    target_model: str,
    messages: list,
    max_attempts: int = 6,
    extra_kwargs: Optional[dict] = None,
    content_transform: Optional[Callable[[str], Any]] = None,
) -> tuple[bool, Any]:
    """
    Shared retry + Groq key-rotation core for all LLM calls.

    Args:
        target_model: LiteLLM model string (e.g. ``"groq/llama-3.1-8b-instant"``).
        messages: Chat messages list to send.
        max_attempts: Max total attempts before giving up.
        extra_kwargs: Additional kwargs forwarded to ``litellm.completion``.
        content_transform: Optional callable applied to the raw string content
            before returning. Raising inside it triggers a retry — useful so a
            malformed JSON response is retried rather than returned as garbage.

    Returns:
        ``(True, result)`` on success, ``(False, last_exception)`` on failure.
    """
    import litellm  # lazy import – keeps startup fast

    kwargs = dict(extra_kwargs or {})
    kwargs.setdefault("request_timeout", 180)
    kwargs.setdefault("timeout", 180)
    kwargs.setdefault("max_retries", 0)
    num_keys = max(1, len(_groq_keys)) if _groq_keys else 1
    last_err: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        try:
            logger.debug(
                f"LLM Request [{target_model}] Attempt {attempt}/{max_attempts}: "
                f"{messages[-1]['content'][:100]}..."
            )
            start_time = time.perf_counter()

            call_kwargs = dict(kwargs)
            if target_model.startswith("groq/") and _groq_cycle:
                call_kwargs["api_key"] = next(_groq_cycle)

            response = litellm.completion(model=target_model, messages=messages, **call_kwargs)

            duration = time.perf_counter() - start_time
            usage = getattr(response, "usage", None)
            tokens = f"{usage.total_tokens} tokens" if usage else "unknown tokens"

            content = response.choices[0].message.content
            if content is None:
                raise ValueError("LLM returned None content. Possible safety filter or empty response.")

            # Apply optional transform (e.g. JSON parsing). Raises → retry.
            result = content_transform(content) if content_transform else content

            logger.info(
                f"LLM Success [{target_model}] in {duration:.2f}s | {tokens} | Result: {_truncate(content)}"
            )
            return True, result

        except Exception as e:
            last_err = e
            logger.error(
                f"LLM Error [{target_model}] Attempt {attempt}/{max_attempts}: {type(e).__name__}: {e}"
            )
            if attempt < max_attempts:
                if any(x in type(e).__name__ for x in ["RateLimitError", "ServiceUnavailableError"]) or any(x in str(e) for x in ["429", "503", "queue full"]):
                    if attempt % num_keys == 0:
                        wait_time = 25
                        logger.warning(f"All keys exhausted or service overloaded. Waiting {wait_time}s before next cycle...")
                        time.sleep(wait_time)
                    else:
                        time.sleep(1)
                else:
                    time.sleep(2 ** attempt)

    return False, last_err


def _try_model(
    model: str,
    messages: list,
    max_attempts: int,
    extra_kwargs: Optional[dict] = None,
    content_transform: Optional[Callable[[str], Any]] = None,
) -> tuple[bool, Any]:
    """Thin wrapper: injects provider-specific API keys before calling _run_with_retry."""
    kw = dict(extra_kwargs or {})
    # Inject NVIDIA NIM key if this is a NIM call
    if model.startswith("nvidia_nim/") and _nim_api_key:
        kw["api_key"] = _nim_api_key
    return _run_with_retry(model, messages, max_attempts=max_attempts, extra_kwargs=kw, content_transform=content_transform)


def analyze_text(text: str, model: str = None, temperature: float = 0.1, chat_history: Optional[list] = None) -> str:
    """
    Analyzes text using the specified LLM model via LiteLLM.
    Uses a low temperature (default 0.1) for consistent prose generation.

    Fallback chain: NIM (primary) → Gemini (tier-2) → Groq (tier-3).
    """
    if not model:
        model = get_llm_model()
        
    messages = []
    if chat_history:
        messages.extend(chat_history)
        
    messages.append({"role": "user", "content": text})
    extra_kwargs = {"temperature": temperature}

    # Tier 1: Primary model (NVIDIA NIM)
    success, result = _try_model(model, messages, max_attempts=2, extra_kwargs=extra_kwargs)
    if success:
        return result

    from app.core.config import get_fallback_llm, get_fallback_llm_last_resort
    fallback_model = get_fallback_llm()
    last_resort_model = get_fallback_llm_last_resort()

    # Tier 2: Gemini
    if model != fallback_model:
        logger.warning(f"Primary model {model} failed. Trying tier-2 fallback: {fallback_model}")
        success, result = _try_model(fallback_model, messages, max_attempts=3, extra_kwargs=extra_kwargs)
        if success:
            return result

    # Tier 3: Groq (last resort)
    if model != last_resort_model and fallback_model != last_resort_model:
        logger.warning(f"Tier-2 fallback {fallback_model} failed. Trying last-resort: {last_resort_model}")
        success, result = _try_model(last_resort_model, messages, max_attempts=2, extra_kwargs=extra_kwargs)
        if success:
            return result

    error_msg = f"All LLM tiers exhausted. Last error: {str(result)}"
    logger.critical(error_msg)
    return error_msg


def analyze_text_json(text: str, model: str = None, temperature: float = 0.0) -> dict:
    """
    Analyzes text using the specified LLM model and expects a JSON response.
    Uses temperature=0 by default for fully deterministic, reproducible outputs.

    Fallback chain: NIM (primary) → Gemini (tier-2) → Groq (tier-3).
    Results are cached in a local SQLite DB keyed on hash(model + prompt) so
    reprocessing identical chapters costs $0.00 and completes in microseconds.
    """
    if not model:
        model = get_llm_model()

    # 1.3: Check cache before hitting the API
    cache_key = _cache_key(text, model)
    cached = _cache_get(cache_key)
    if cached is not None:
        logger.debug(f"LLM cache HIT [{model}] key={cache_key[:12]}...")
        return cached

    system_prompt = (
        "You are a helpful assistant. You must respond ONLY with valid JSON. "
        "Do not include markdown formatting like ```json or any other text."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text},
    ]
    extra_kwargs = {"response_format": {"type": "json_object"}, "temperature": temperature}

    from app.core.config import get_fallback_llm, get_fallback_llm_last_resort
    fallback_model = get_fallback_llm()
    last_resort_model = get_fallback_llm_last_resort()

    # Tier 1: Primary model (NVIDIA NIM)
    success, result = _try_model(model, messages, max_attempts=2, extra_kwargs=extra_kwargs, content_transform=_parse_json)
    if success:
        _cache_put(cache_key, result)
        return result

    # Tier 2: Gemini
    if model != fallback_model:
        logger.warning(f"Primary model {model} failed. Trying tier-2 fallback: {fallback_model}")
        success, result = _try_model(fallback_model, messages, max_attempts=3, extra_kwargs=extra_kwargs, content_transform=_parse_json)
        if success:
            _cache_put(cache_key, result)
            return result

    # Tier 3: Groq (last resort)
    if model != last_resort_model and fallback_model != last_resort_model:
        logger.warning(f"Tier-2 fallback {fallback_model} failed. Trying last-resort: {last_resort_model}")
        success, result = _try_model(last_resort_model, messages, max_attempts=2, extra_kwargs=extra_kwargs, content_transform=_parse_json)
        if success:
            _cache_put(cache_key, result)
            return result

    logger.critical(f"All LLM tiers exhausted for JSON extraction. Last error: {str(result)}")
    return {"error": f"All LLM tiers exhausted. Last error: {str(result)}"}


def get_model_info(model: str):
    """
    Optional: Get information about the model if needed for debug/logging.
    """
    import litellm  # lazy import for performance
    return litellm.get_model_info(model)
