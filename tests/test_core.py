from app.core.graduation import evaluate_graduation, check_graduation_status, GraduationLevel
from app.core.models.character_runtime import CharacterRuntime

def test_evaluate_graduation():
    assert evaluate_graduation(0.1) == GraduationLevel.EXTRA
    assert evaluate_graduation(0.14) == GraduationLevel.EXTRA
    assert evaluate_graduation(0.15) == GraduationLevel.EVOLVING
    assert evaluate_graduation(0.3) == GraduationLevel.EVOLVING
    assert evaluate_graduation(0.49) == GraduationLevel.EVOLVING
    assert evaluate_graduation(0.50) == GraduationLevel.MAIN_CAST
    assert evaluate_graduation(0.8) == GraduationLevel.MAIN_CAST

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
        confidence_score=0.6, 
        first_seen_chapter=1, 
        last_seen_chapter=1,
        vocal_traits={"gender": "male"}
    )
    # Should be MAIN_CAST, will assign voice
    # Since voice_assignment is currently a basic stub mapping
    assert check_graduation_status(char)
    assert char.voice_id is not None

def test_check_graduation_status_with_wiki_traits(mocker):
    # Mock assign_voice to verify traits are passed
    mock_assign = mocker.patch("app.core.graduation.assign_voice", return_value="v1")
    char = CharacterRuntime(
        character_id="hero", 
        confidence_score=0.6, 
        first_seen_chapter=1, 
        last_seen_chapter=1,
        vocal_traits={"base_pitch": "high"}
    )
    wiki_traits = {"gender": "female", "personality": "bold"}
    
    assert check_graduation_status(char, wiki_traits=wiki_traits)
    assert char.voice_id == "v1"
    
    # Assert assign_voice was called with the merged traits
    expected_traits = {"base_pitch": "high", "gender": "female", "personality": "bold"}
    mock_assign.assert_called_once_with(expected_traits)
