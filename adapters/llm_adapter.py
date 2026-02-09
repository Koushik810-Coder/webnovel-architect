import os

def analyze_text(text: str, model: str = "gemini/gemini-1.5-flash"):
    """
    Analyzes text using the specified LLM model via LiteLLM.
    
    Args:
        text: The input text to analyze.
        model: The model identifier string (e.g., "gemini/gemini-1.5-flash", "ollama/llama3").
        
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

def get_model_info(model: str):
    """
    Optional: Get information about the model if needed for debug/logging.
    """
    import litellm # Lazy import for performance
    return litellm.get_model_info(model)
