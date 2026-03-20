import os
import json
import time

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
    last_error = None
    for attempt in range(1, 4):  # Retry up to 3 times
        try:
            response = litellm.completion(model=model, messages=messages)
            return response.choices[0].message.content
        except Exception as e:
            last_error = e
            print(f"Error calling LLM {model} (attempt {attempt}/3): {e}")
            if attempt < 3:
                time.sleep(2 ** attempt)  # Exponential backoff: 2s, 4s
    return f"API Fallback: I was unable to connect to the AI model ({model}) after 3 attempts. Please verify your API keys and network connection. Last known error: {str(last_error)}"
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

    last_error = None
    for attempt in range(1, 4):  # Retry up to 3 times
        try:
            response = litellm.completion(
                model=model,
                messages=messages,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            clean_content = content.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_content)
        except Exception as e:
            last_error = e
            print(f"Error calling LLM {model} for JSON (attempt {attempt}/3): {e}")
            if attempt < 3:
                time.sleep(2 ** attempt)  # Exponential backoff: 2s, 4s

    print(f"LLM Extraction failed after 3 attempts: {str(last_error)}")
    return {"error": f"API Fallback: The system was unable to extract events or dialogue because the LLM provider ({model}) could not be reached. Details: {str(last_error)}"}

def get_model_info(model: str):
    """
    Optional: Get information about the model if needed for debug/logging.
    """
    import litellm # Lazy import for performance
    return litellm.get_model_info(model)
