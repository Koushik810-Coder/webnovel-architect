import pytest
from app.core.graduation import evaluate_graduation, check_graduation_status, GraduationLevel
from app.core.models.character_runtime import CharacterRuntime

def test_evaluate_graduation():
    assert evaluate_graduation(0.1) == GraduationLevel.EXTRA
    assert evaluate_graduation(0.24) == GraduationLevel.EXTRA
    assert evaluate_graduation(0.25) == GraduationLevel.EVOLVING
    assert evaluate_graduation(0.5) == GraduationLevel.EVOLVING
    assert evaluate_graduation(0.74) == GraduationLevel.EVOLVING
    assert evaluate_graduation(0.75) == GraduationLevel.MAIN_CAST
    assert evaluate_graduation(0.9) == GraduationLevel.MAIN_CAST

def test_character_runtime_model():
    char = CharacterRuntime(character_id="hero", first_seen_chapter=1, last_seen_chapter=5)
    assert char.character_id == "hero"
    assert char.confidence_score == 0.0
    assert char.first_seen_chapter == 1

def test_check_graduation_status_no_change():
    char = CharacterRuntime(character_id="npc", confidence_score=0.1, first_seen_chapter=1, last_seen_chapter=1)
    # Should be EXTRA, won't assign voice
    assert not check_graduation_status(char)
    assert char.voice_id is None

def test_check_graduation_status_graduates():
    char = CharacterRuntime(
        character_id="hero", 
        confidence_score=0.8, 
        first_seen_chapter=1, 
        last_seen_chapter=1,
        vocal_traits={"gender": "male"}
    )
    # Should be MAIN_CAST, will assign voice
    # Since voice_assignment is currently a basic stub mapping
    assert check_graduation_status(char)
    assert char.voice_id is not None
