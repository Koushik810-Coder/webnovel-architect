"""
tests/test_services.py
======================
Integration-level tests for audio_renderer and ingest.

NOTE: The legacy `build_narration_segments` / `find_character_by_name` API was replaced
by `parse_chapter_to_script_blocks` / `resolve_dialogue_speakers` in narration.py.
Those are covered by test_narration.py. The NarrationSegment model is kept for audio_renderer.
"""

from unittest.mock import patch, MagicMock

from app.services.audio_renderer import render_segments
from app.services.ingest import ingest_chapter
from app.core.models.narration import NarrationSegment
from app.core.constants import NARRATOR_VOICE_ID


# ── audio_renderer ────────────────────────────────────────────────────────────

@patch('app.services.audio_renderer.get_voice_provider')
def test_render_segments(mock_get_provider):
    mock_provider = MagicMock()
    mock_provider.synthesize.return_value = b"audio_data"
    mock_get_provider.return_value = mock_provider

    segments = [
        NarrationSegment(text="Hello", voice_id="v1"),
        NarrationSegment(text="World", voice_id=None),  # Should use narrator default
    ]

    result = render_segments(segments)

    assert len(result) == 2
    assert result == [b"audio_data", b"audio_data"]
    assert mock_provider.synthesize.call_count == 2
    # First segment uses the explicit voice
    mock_provider.synthesize.assert_any_call("Hello", "v1")
    # Second segment (voice_id=None) must fall back to the narrator default
    mock_provider.synthesize.assert_any_call("World", NARRATOR_VOICE_ID)


# ── ingest ────────────────────────────────────────────────────────────────────

@patch('app.services.ingest.extract_chapter_intelligence_llm')
@patch('app.services.ingest.save_character_wiki')
@patch('app.services.ingest.save_chapter')
@patch('app.services.ingest.save_runtime')
@patch('app.services.ingest.load_runtime')
def test_ingest_chapter_new_character(
    mock_load, mock_save_rt, mock_save_chapter, mock_save_wiki, mock_extract
):
    mock_extract.return_value = {"active_character_names": ["Jon Snow"]}
    mock_load.return_value = (0, {})

    chapter = ingest_chapter("test_story", "Chapter 1", "Jon Snow was here.")

    assert chapter.title == "Chapter 1"

    mock_save_rt.assert_called_once()
    args, _ = mock_save_rt.call_args
    assert args[0] == "test_story"
    assert args[1] == 1  # chapter counter
    runtime_db = args[2]

    assert "jon_snow" in runtime_db
    char = runtime_db["jon_snow"]
    assert char.confidence_score > 0
    assert char.mention_count == 1
    mock_save_wiki.assert_called_once()


@patch('app.services.ingest.extract_chapter_intelligence_llm')
@patch('app.services.ingest.save_character_wiki')
@patch('app.services.ingest.save_chapter')
@patch('app.services.ingest.save_runtime')
@patch('app.services.ingest.load_runtime')
def test_ingest_chapter_existing_character(
    mock_load, mock_save_rt, mock_save_chapter, mock_save_wiki, mock_extract
):
    mock_extract.return_value = {"active_character_names": ["Jon Snow"]}

    from app.core.models.character_runtime import CharacterRuntime
    existing_char = CharacterRuntime(
        character_id="jon_snow",
        first_seen_chapter=1,
        last_seen_chapter=1,
        confidence_score=0.1,
        mention_count=1,
    )
    mock_load.return_value = (1, {"jon_snow": existing_char})

    ingest_chapter("test_story", "Ch 2", "Jon Snow again")

    args, _ = mock_save_rt.call_args
    runtime_db = args[2]
    char = runtime_db["jon_snow"]

    assert char.mention_count == 2
    assert char.last_seen_chapter == 2
