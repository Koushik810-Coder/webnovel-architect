import os
import json
import time

from app.core.logger import get_logger
logger = get_logger(__name__)

def analyze_text(text: str, model: str = "groq/llama-3.1-8b-instant"):
    """
    Analyzes text using the specified LLM model via LiteLLM.
    
    Args:
        text: The input text to analyze.
        model: The model identifier string (e.g., "gemini/gemini-2.5-flash", "ollama/llama3").
        
    Returns:
        The content of the response from the LLM.
    """
    import litellm  # Lazy import for performance
    messages = [{ "role": "user", "content": text }]
    
    def _run_with_model(target_model, max_attempts=3):
        last_err = None
        for attempt in range(1, max_attempts + 1):
            try:
                response = litellm.completion(model=target_model, messages=messages)
                content = response.choices[0].message.content
                if content is None:
                    raise ValueError("LLM returned None content. Possible safety filter or empty response.")
                return True, content
            except Exception as e:
                last_err = e
                logger.error(f"Error calling LLM {target_model} (attempt {attempt}/{max_attempts}): {e}")
                if attempt < max_attempts:
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

    return f"API Fallback: I was unable to connect to the AI model ({model}) and its fallbacks. Please verify your API keys and network connection. Last known error: {str(result_or_err)}"


def analyze_text_json(text: str, model: str = "groq/llama-3.1-8b-instant") -> dict:
    """
    Analyzes text using the specified LLM model and expects a JSON response.
    
    Args:
        text: The input text to analyze.
        model: The model identifier string.
        
    Returns:
        A dictionary parsed from the LLM's JSON response, or an empty dict on failure.
    """
    import litellm
    system_prompt = "You are a helpful assistant. You must respond ONLY with valid JSON. Do not include markdown formatting like ```json or any other text."
    messages = [
        { "role": "system", "content": system_prompt },
        { "role": "user", "content": text }
    ]

    def _run_with_model(target_model, max_attempts=3):
        last_err = None
        for attempt in range(1, max_attempts + 1):
            try:
                response = litellm.completion(
                    model=target_model,
                    messages=messages,
                    response_format={"type": "json_object"}
                )
                content = response.choices[0].message.content
                if content is None:
                    raise ValueError("LLM returned None content. Possible safety filter or empty response.")
                clean_content = content.replace("```json", "").replace("```", "").strip()
                return True, json.loads(clean_content)
            except Exception as e:
                last_err = e
                logger.error(f"Error calling LLM {target_model} for JSON (attempt {attempt}/{max_attempts}): {e}")
                if attempt < max_attempts:
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

    logger.error(f"LLM Extraction failed after all attempts: {str(result_or_err)}")
    return {"error": f"API Fallback: ... {str(result_or_err)}"}

def get_model_info(model: str):
    """
    Optional: Get information about the model if needed for debug/logging.
    """
    import litellm # Lazy import for performance
    return litellm.get_model_info(model)
