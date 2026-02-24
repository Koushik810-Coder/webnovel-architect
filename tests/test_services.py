import pytest
from unittest.mock import patch, MagicMock

from app.services.audio_renderer import render_segments
from app.services.ingest import ingest_chapter, normalize_id, _runtime_db
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
def test_normalize_id():
    assert normalize_id("Lord Stark") == "lord_stark"

@patch('app.services.ingest.extract_chapter_intelligence')
@patch('app.services.ingest.save_character_wiki')
def test_ingest_chapter_new_character(mock_save_wiki, mock_extract):
    mock_extract.return_value = {"active_character_names": ["Jon Snow"]}
    _runtime_db.clear() # clear global state for test
    
    chapter = ingest_chapter("Chapter 1", "Jon Snow was here.")
    
    assert chapter.title == "Chapter 1"
    assert "jon_snow" in _runtime_db
    char = _runtime_db["jon_snow"]
    assert char.confidence_score == 0.1
    assert char.mention_count == 1
    mock_save_wiki.assert_called_once()

@patch('app.services.ingest.extract_chapter_intelligence')
@patch('app.services.ingest.save_character_wiki')
def test_ingest_chapter_existing_character(mock_save_wiki, mock_extract):
    mock_extract.return_value = {"active_character_names": ["Jon Snow"]}
    _runtime_db.clear()
    import app.services.ingest
    app.services.ingest._chapter_counter = 0
    
    # ingest once
    ingest_chapter("Ch 1", "Jon Snow")
    
    # ingest twice
    ingest_chapter("Ch 2", "Jon Snow again")
    
    char = _runtime_db["jon_snow"]
    # should increase score
    assert pytest.approx(char.confidence_score) == 0.15
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
