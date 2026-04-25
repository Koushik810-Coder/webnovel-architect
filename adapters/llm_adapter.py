import json
import time
import os
import itertools
from typing import Any, Callable, Optional

from app.core.logger import get_logger
from app.core.config import get_llm_model
from app.core.utils import truncate_for_log as _truncate

logger = get_logger(__name__)

# --- Groq Key Rotation ---
_groq_keys = [v.strip() for k, v in os.environ.items() if k.startswith("GROQ_API_KEY") and v.strip()]
_groq_cycle = itertools.cycle(_groq_keys) if _groq_keys else None
if _groq_keys:
    logger.info(f"Initialized LLM Adapter with {len(_groq_keys)} Groq API keys for rotation.")
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
    kwargs.setdefault("request_timeout", 60)
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
                if "RateLimitError" in type(e).__name__ or "429" in str(e):
                    if attempt % num_keys == 0:
                        wait_time = 25
                        logger.warning(f"All keys exhausted. Waiting {wait_time}s before next cycle...")
                        time.sleep(wait_time)
                    else:
                        time.sleep(1)
                else:
                    time.sleep(2 ** attempt)

    return False, last_err


def analyze_text(text: str, model: str = None) -> str:
    """
    Analyzes text using the specified LLM model via LiteLLM.
    """
    if not model:
        model = get_llm_model()
    messages = [{"role": "user", "content": text}]

    success, result = _run_with_retry(model, messages)
    if success:
        return result

    fallback_model = "groq/llama-3.1-8b-instant"
    if not model.startswith("groq"):
        logger.warning(f"Primary model {model} failed. Falling back to Groq ({fallback_model}) as a safeguard...")
        success, result = _run_with_retry(fallback_model, messages, max_attempts=2)
        if success:
            return result

    error_msg = f"API Fallback: All attempts failed for {model}. Last error: {str(result)}"
    logger.critical(error_msg)
    return error_msg


def analyze_text_json(text: str, model: str = None) -> dict:
    """
    Analyzes text using the specified LLM model and expects a JSON response.
    """
    if not model:
        model = get_llm_model()

    system_prompt = (
        "You are a helpful assistant. You must respond ONLY with valid JSON. "
        "Do not include markdown formatting like ```json or any other text."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text},
    ]
    extra_kwargs = {"response_format": {"type": "json_object"}}

    success, result = _run_with_retry(
        model, messages, extra_kwargs=extra_kwargs, content_transform=_parse_json
    )
    if success:
        return result

    fallback_model = "groq/llama-3.1-8b-instant"
    if not model.startswith("groq"):
        logger.warning(
            f"Primary model {model} failed. Falling back to Groq ({fallback_model}) for JSON as a safeguard..."
        )
        success, result = _run_with_retry(
            fallback_model, messages, max_attempts=2,
            extra_kwargs=extra_kwargs, content_transform=_parse_json,
        )
        if success:
            return result

    logger.critical(f"LLM JSON Extraction failed after all attempts: {str(result)}")
    return {"error": f"API Fallback: Extraction failed. Last error: {str(result)}"}


def get_model_info(model: str):
    """
    Optional: Get information about the model if needed for debug/logging.
    """
    import litellm  # lazy import for performance
    return litellm.get_model_info(model)
