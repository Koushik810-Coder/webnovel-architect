import os
import json

def analyze_text(text: str, model: str = "gemini/gemini-2.5-flash"):
    """
    Analyzes text using the specified LLM model via LiteLLM.
    
    Args:
        text: The input text to analyze.
        model: The model identifier string (e.g., "gemini/gemini-2.5-flash", "ollama/llama3").
        
    Returns:
        The content of the response from the LLM.
    """
    try:
        import litellm # Lazy import for performance
        
        # Construct the message for the LLM
        messages = [{ "role": "user", "content": text }]
        
        # Call LiteLLM completion
        response = litellm.completion(
            model=model,
            messages=messages
        )
        
        # Extract and return the content
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error calling LLM {model}: {e}")
        return None

def analyze_text_json(text: str, model: str = "gemini/gemini-2.5-flash") -> dict:
    """
    Analyzes text using the specified LLM model and expects a JSON response.
    
    Args:
        text: The input text to analyze.
        model: The model identifier string.
        
    Returns:
        A dictionary parsed from the LLM's JSON response, or an empty dict on failure.
    """
    try:
        import litellm
        
        # Explicitly instruct the model to return ONLY JSON
        system_prompt = "You are a helpful assistant. You must respond ONLY with valid JSON. Do not include markdown formatting like ```json or any other text."
        messages = [
            { "role": "system", "content": system_prompt },
            { "role": "user", "content": text }
        ]
        
        # Some models support response_format={"type": "json_object"} natively via litellm
        # But for max compatibility, we'll try to parse the output directly.
        response = litellm.completion(
            model=model,
            messages=messages,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        
        # Attempt to clean up markdown if the model ignored instructions
        clean_content = content.replace("```json", "").replace("```", "").strip()
        
        return json.loads(clean_content)
        
    except Exception as e:
        print(f"Error calling LLM {model} for JSON: {e}")
        raise RuntimeError(f"LLM Extraction failed: {str(e)}")

def get_model_info(model: str):
    """
    Optional: Get information about the model if needed for debug/logging.
    """
    import litellm # Lazy import for performance
    return litellm.get_model_info(model)
