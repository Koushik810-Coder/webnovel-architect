from unittest.mock import patch, MagicMock

from adapters.llm_adapter import analyze_text, get_model_info
# Assuming tts_adapter has functions. If not, testing what is there or omit it.
try:
    from adapters.tts_adapter import generate_audio
except ImportError:
    generate_audio = None

def test_analyze_text_success():
    mock_litellm = MagicMock()
    mock_response = MagicMock()
    mock_message = MagicMock()
    mock_message.content = "Test analysis result"
    mock_response.choices = [MagicMock(message=mock_message)]
    mock_litellm.completion.return_value = mock_response

    with patch.dict('sys.modules', {'litellm': mock_litellm}):
        result = analyze_text("This is test text.", "test-model")
        assert result == "Test analysis result"
        mock_litellm.completion.assert_called_once()
        args, kwargs = mock_litellm.completion.call_args
        assert kwargs['model'] == "test-model"
        assert kwargs['messages'] == [{"role": "user", "content": "This is test text."}]

def test_analyze_text_failure():
    mock_litellm = MagicMock()
    mock_litellm.completion.side_effect = Exception("API error")
    
    with patch.dict('sys.modules', {'litellm': mock_litellm}):
        result = analyze_text("This is test text.", "test-model")
        assert result and "All LLM tiers exhausted" in result

def test_get_model_info():
    mock_litellm = MagicMock()
    mock_litellm.get_model_info.return_value = {"info": "some info"}
    
    with patch.dict('sys.modules', {'litellm': mock_litellm}):
        result = get_model_info("test-model")
        assert result == {"info": "some info"}
        mock_litellm.get_model_info.assert_called_once_with("test-model")

