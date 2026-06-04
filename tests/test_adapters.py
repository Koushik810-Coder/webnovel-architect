from unittest.mock import patch, MagicMock
import pytest

from adapters.llm_adapter import analyze_text
from adapters.tts_adapter import get_tts_engine, EdgeAdapter

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

def test_get_tts_engine_edge():
    engine = get_tts_engine("edge")
    assert isinstance(engine, EdgeAdapter)

def test_get_tts_engine_invalid():
    with pytest.raises(ValueError, match="Unknown TTS Engine"):
        get_tts_engine("unknown_engine_type")

@patch('adapters.tts_adapter.KokoroAdapter')
def test_get_tts_engine_kokoro_fallback(mock_kokoro_class):
    mock_instance = MagicMock()
    mock_instance.engine = None
    mock_kokoro_class.return_value = mock_instance

    engine = get_tts_engine("kokoro")
    assert isinstance(engine, EdgeAdapter)
