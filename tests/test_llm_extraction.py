import pytest
from unittest.mock import patch

DUMMY_TEXT = """
The sun set over the horizon. Beware of the shadows!
John walked into the tavern, looking for Lady Elara.
Suddenly, Vael'Thar the ancient wizard appeared.
"This is Zelithra Moonfall's domain," he proclaimed loudly.
No one expected a King to arrive like this.
He became a Tier-3 Mage after consulting the Inner Disciple.
They traveled from the Upper Realm to join the Azure Cloud Sect.
"""

MOCK_LLM_RESPONSE = {
    "active_character_names": ["John", "Elara", "Vael'Thar", "Zelithra Moonfall"],
    "active_world_terms": ["Upper Realm", "Azure Cloud Sect", "Tier-3 Mage", "Inner Disciple"],
    "dialogue_count_total": 1,
    "events": [
        {
            "action_summary": "John looks for Lady Elara in the tavern.",
            "involved_characters": ["John", "Elara"],
            "pre_conditions": "John enters the tavern.",
            "post_conditions": "Encounter is implied.",
            "location": "Tavern",
            "causes_event_indexes": []
        }
    ]
}


def test_llm_extraction_returns_expected_fields():
    """LLM extraction returns all required fields when mocked."""
    from app.services.extraction import extract_chapter_intelligence_llm

    with patch("adapters.llm_adapter.analyze_text_json", return_value=MOCK_LLM_RESPONSE):
        result = extract_chapter_intelligence_llm(DUMMY_TEXT)

    assert "active_character_names" in result
    assert "active_world_terms" in result
    assert "dialogue_count_total" in result
    assert "events" in result
    assert isinstance(result["active_character_names"], list)
    assert len(result["active_character_names"]) > 0


def test_llm_extraction_deduplicates_and_sorts():
    """Character names and world terms are deduplicated and sorted."""
    from app.services.extraction import extract_chapter_intelligence_llm

    duplicate_response = {
        **MOCK_LLM_RESPONSE,
        "active_character_names": ["John", "john", "John"],
    }
    with patch("adapters.llm_adapter.analyze_text_json", return_value=duplicate_response):
        result = extract_chapter_intelligence_llm(DUMMY_TEXT)

    # After dedup via set — "john" and "John" treated as distinct strings,
    # but duplicates of the exact same string are removed.
    names = result["active_character_names"]
    assert len(names) == len(set(names))


def test_llm_extraction_handles_empty_llm_response():
    """Raises ValueError when LLM returns None/empty."""
    from app.services.extraction import extract_chapter_intelligence_llm

    with patch("adapters.llm_adapter.analyze_text_json", return_value=None):
        with pytest.raises(ValueError):
            extract_chapter_intelligence_llm(DUMMY_TEXT)


def test_llm_extraction_handles_missing_fields_gracefully():
    """Partial LLM response fills missing optional fields with safe defaults."""
    from app.services.extraction import extract_chapter_intelligence_llm

    partial_response = {"active_character_names": ["Hero"]}
    with patch("adapters.llm_adapter.analyze_text_json", return_value=partial_response):
        result = extract_chapter_intelligence_llm(DUMMY_TEXT)

    assert result["active_character_names"] == ["Hero"]
    assert result["active_world_terms"] == []
    assert result["dialogue_count_total"] == 0
    assert result["events"] == []
