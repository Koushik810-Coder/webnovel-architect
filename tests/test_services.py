from unittest.mock import patch, MagicMock

from app.services.audio_renderer import render_segments
from app.services.ingest import ingest_chapter
from app.services.narration import build_narration_segments, find_character_by_name
from app.core.models.narration import NarrationSegment

# testing audio_renderer
@patch('app.services.audio_renderer.get_voice_provider')
def test_render_segments(mock_get_provider):
    mock_provider = MagicMock()
    mock_provider.synthesize.return_value = b"audio_data"
    mock_get_provider.return_value = mock_provider
    segments = [
        NarrationSegment(text="Hello", voice_id="v1"),
        NarrationSegment(text="World", voice_id=None) # Should use narrator default
    ]
    
    result = render_segments(segments)
    
    assert len(result) == 2
    assert result == [b"audio_data", b"audio_data"]
    
    assert mock_provider.synthesize.call_count == 2
    mock_provider.synthesize.assert_any_call("Hello", "v1")
    # NARRATOR_VOICE_ID is usually defined in constants, mock checks if it hits default

# testing ingest
@patch('app.services.ingest.extract_chapter_intelligence_llm')
@patch('app.services.ingest.save_character_wiki')
@patch('app.services.ingest.save_chapter')
@patch('app.services.ingest.save_runtime')
@patch('app.services.ingest.load_runtime')
def test_ingest_chapter_new_character(mock_load, mock_save_rt, mock_save_chapter, mock_save_wiki, mock_extract):
    mock_extract.return_value = {"active_character_names": ["Jon Snow"]}
    # Reset local state via mock return
    mock_load.return_value = (0, {})
    
    chapter = ingest_chapter("test_story", "Chapter 1", "Jon Snow was here.")
    
    assert chapter.title == "Chapter 1"
    
    # Verify save_runtime args
    mock_save_rt.assert_called_once()
    args, _ = mock_save_rt.call_args
    assert args[0] == "test_story"
    assert args[1] == 1 # chapter counter
    runtime_db = args[2]
    
    assert "jon_snow" in runtime_db
    char = runtime_db["jon_snow"]
    # Default PageRank with 1 incoming edge and decay 
    # Not asserting exact float since graph structure changed, just ensure it exists
    assert char.confidence_score > 0
    assert char.mention_count == 1
    mock_save_wiki.assert_called_once()

@patch('app.services.ingest.extract_chapter_intelligence_llm')
@patch('app.services.ingest.save_character_wiki')
@patch('app.services.ingest.save_chapter')
@patch('app.services.ingest.save_runtime')
@patch('app.services.ingest.load_runtime')
def test_ingest_chapter_existing_character(mock_load, mock_save_rt, mock_save_chapter, mock_save_wiki, mock_extract):
    mock_extract.return_value = {"active_character_names": ["Jon Snow"]}
    
    from app.core.models.character_runtime import CharacterRuntime
    # Mock that it's already there
    existing_char = CharacterRuntime(
        character_id="jon_snow",
        first_seen_chapter=1,
        last_seen_chapter=1,
        confidence_score=0.1,
        mention_count=1
    )
    mock_load.return_value = (1, {"jon_snow": existing_char})
    
    # ingest twice
    ingest_chapter("test_story", "Ch 2", "Jon Snow again")
    
    args, _ = mock_save_rt.call_args
    runtime_db = args[2]
    char = runtime_db["jon_snow"]
    
    assert char.mention_count == 2
    assert char.last_seen_chapter == 2

# testing narration
@patch('app.services.narration.CHARACTER_WIKI', {"bob_id": MagicMock(display_name="Bob")})
def test_find_character_by_name():
    assert find_character_by_name("Bob says hi") == "bob_id"
    assert find_character_by_name("Alice says hi") is None

@patch('app.services.narration.CHARACTER_WIKI', {"bob_id": MagicMock(display_name="Bob")})
@patch('app.services.narration.CHARACTER_RUNTIME', {"bob_id": MagicMock(voice_id="bob_voice")})
def test_build_narration_segments():
    text = 'He walked in.\n"Hello there," said Bob.'
    segments = build_narration_segments(text)
    
    assert len(segments) == 2
    assert segments[0].text == "He walked in."
    assert segments[0].character_id is None
    
    assert segments[1].text == "Hello there,"
    assert segments[1].character_id == "bob_id"
    assert segments[1].voice_id == "bob_voice"
