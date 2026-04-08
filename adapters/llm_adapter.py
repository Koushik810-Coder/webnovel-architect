import json
import time
import os
import itertools

from app.core.logger import get_logger
from app.core.config import get_llm_model
logger = get_logger(__name__)

# --- Groq Key Rotation ---
_groq_keys = [v.strip() for k, v in os.environ.items() if k.startswith("GROQ_API_KEY") and v.strip()]
_groq_cycle = itertools.cycle(_groq_keys) if _groq_keys else None
if _groq_keys:
    logger.info(f"Initialized LLM Adapter with {_groq_keys.__len__()} Groq API keys for rotation.")
# -------------------------

def _truncate(text: str, limit: int = 150) -> str:
    """Helper to truncate text for logging."""
    if not text: return ""
    text = text.replace("\n", " ").strip()
    return (text[:limit] + "..") if len(text) > limit else text

def analyze_text(text: str, model: str = None):
    """
    Analyzes text using the specified LLM model via LiteLLM.
    """
    if not model:
        model = get_llm_model()
    import litellm  # Lazy import for performance
    messages = [{ "role": "user", "content": text }]
    
    def _run_with_model(target_model, max_attempts=6):
        last_err = None
        num_keys = max(1, len(_groq_keys)) if _groq_keys else 1
        for attempt in range(1, max_attempts + 1):
            try:
                logger.debug(f"LLM Request [{target_model}] Attempt {attempt}/{max_attempts}: {messages[0]['content'][:100]}...")
                start_time = time.perf_counter()
                
                kwargs = {}
                if target_model.startswith("groq/") and _groq_cycle:
                    kwargs["api_key"] = next(_groq_cycle)

                response = litellm.completion(model=target_model, messages=messages, **kwargs)
                
                duration = time.perf_counter() - start_time
                usage = getattr(response, 'usage', None)
                tokens = f"{usage.total_tokens} tokens" if usage else "unknown tokens"
                
                content = response.choices[0].message.content
                if content is None:
                    raise ValueError("LLM returned None content. Possible safety filter or empty response.")
                
                logger.info(f"LLM Success [{target_model}] in {duration:.2f}s | {tokens} | Result: {_truncate(content)}")
                return True, content
            except Exception as e:
                last_err = e
                logger.error(f"LLM Error [{target_model}] Attempt {attempt}/{max_attempts}: {type(e).__name__}: {str(e)}")
                if attempt < max_attempts:
                    if "RateLimitError" in type(e).__name__ or "429" in str(e):
                        if attempt % num_keys == 0:
                            wait_time = 25
                            logger.warning(f"All keys exhausted. Waiting {wait_time}s before next cycle...")
                            time.sleep(wait_time)
                        else:
                            # Immediately try the next key smoothly
                            time.sleep(1)
                    else:
                        time.sleep(2 ** attempt)
        return False, last_err

    success, result_or_err = _run_with_model(model)
    if success:
        return result_or_err
        
    fallback_model = "groq/llama-3.1-8b-instant"
    if not model.startswith("groq"):
        logger.warning(f"Primary model {model} failed. Falling back to Groq ({fallback_model}) as a safeguard...")
        success, result_or_err = _run_with_model(fallback_model, max_attempts=2)
        if success:
            return result_or_err

    error_msg = f"API Fallback: All attempts failed for {model}. Last error: {str(result_or_err)}"
    logger.critical(error_msg)
    return error_msg


def analyze_text_json(text: str, model: str = None) -> dict:
    """
    Analyzes text using the specified LLM model and expects a JSON response.
    """
    if not model:
        model = get_llm_model()
    import litellm
    system_prompt = "You are a helpful assistant. You must respond ONLY with valid JSON. Do not include markdown formatting like ```json or any other text."
    messages = [
        { "role": "system", "content": system_prompt },
        { "role": "user", "content": text }
    ]

    def _run_with_model(target_model, max_attempts=6):
        last_err = None
        num_keys = max(1, len(_groq_keys)) if _groq_keys else 1
        for attempt in range(1, max_attempts + 1):
            try:
                logger.debug(f"LLM JSON Request [{target_model}] Attempt {attempt}/{max_attempts}")
                start_time = time.perf_counter()

                kwargs = {"response_format": {"type": "json_object"}}
                if target_model.startswith("groq/") and _groq_cycle:
                    kwargs["api_key"] = next(_groq_cycle)

                response = litellm.completion(
                    model=target_model,
                    messages=messages,
                    **kwargs
                )
                
                duration = time.perf_counter() - start_time
                usage = getattr(response, 'usage', None)
                tokens = f"{usage.total_tokens} tokens" if usage else "unknown tokens"
                
                content = response.choices[0].message.content
                if content is None:
                    raise ValueError("LLM returned None content. Possible safety filter or empty response.")
                
                clean_content = content.replace("```json", "").replace("```", "").strip()
                data = json.loads(clean_content)
                
                logger.info(f"LLM JSON Success [{target_model}] in {duration:.2f}s | {tokens}")
                return True, data
            except Exception as e:
                last_err = e
                logger.error(f"LLM JSON Error [{target_model}] Attempt {attempt}/{max_attempts}: {type(e).__name__}: {str(e)}")
                if attempt < max_attempts:
                    if "RateLimitError" in type(e).__name__ or "429" in str(e):
                        if attempt % num_keys == 0:
                            wait_time = 25
                            logger.warning(f"All keys exhausted. Waiting {wait_time}s before next cycle...")
                            time.sleep(wait_time)
                        else:
                            # Immediately try the next key without huge delay
                            time.sleep(1)
                    else:
                        time.sleep(2 ** attempt)
        return False, last_err

    success, result_or_err = _run_with_model(model)
    if success:
        return result_or_err
        
    fallback_model = "groq/llama-3.1-8b-instant"
    if not model.startswith("groq"):
        logger.warning(f"Primary model {model} failed. Falling back to Groq ({fallback_model}) for JSON as a safeguard...")
        success, result_or_err = _run_with_model(fallback_model, max_attempts=2)
        if success:
            return result_or_err

    logger.critical(f"LLM Extraction failed after all attempts: {str(result_or_err)}")
    return {"error": f"API Fallback: Extraction failed. Last error: {str(result_or_err)}"}

def get_model_info(model: str):
    """
    Optional: Get information about the model if needed for debug/logging.
    """
    import litellm # Lazy import for performance
    return litellm.get_model_info(model)
