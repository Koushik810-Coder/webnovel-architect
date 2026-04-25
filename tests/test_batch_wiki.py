"""
tests/test_batch_wiki.py
====================================
Tests for batch_update_character_profiles() and _sequential_fallback() in wiki.py.
Covers:
  - Happy path: all chars returned in one batch call
  - Partial batch: missing char triggers sequential fallback for that char only
  - Non-dict response triggers full sequential fallback
  - Exception in batch triggers full sequential fallback
  - Empty input returns empty dict
  - _sequential_fallback calls update_character_profile per character
"""

import pytest
from unittest.mock import patch, MagicMock

from app.services.wiki import batch_update_character_profiles, _sequential_fallback


CHAR_A = {
    "name": "Ariane",
    "existing_wiki": "Ariane is a mage.",
    "new_events": "- Ariane cast a fireball\n- Ariane defeated the dragon",
}
CHAR_B = {
    "name": "Master Vael",
    "existing_wiki": "",
    "new_events": "- Vael appeared from shadows",
}

PAYLOAD = {"ariane": CHAR_A, "master_vael": CHAR_B}

GOOD_PROFILE = {
    "short_description": "A powerful mage.",
    "synopsis": "Ariane defeated a dragon.",
    "status": "Alive",
    "age": "25",
    "gender": "female",
    "species": None,
    "role": "Protagonist",
    "affiliations": ["Mage Guild"],
    "appearance": "Tall with silver hair.",
    "personality_traits": ["Brave", "Strategic"],
    "notable_quirks": ["Hums when casting"],
    "metadata": {},
    "relationships": [],
    "new_timeline_events": [{"chapter": 5, "event": "Defeated the dragon"}],
}


class TestBatchUpdateCharacterProfiles:
    def test_happy_path_returns_all_profiles(self):
        """All characters in payload are returned when batch call succeeds."""
        batch_result = {
            "ariane": {**GOOD_PROFILE},
            "master_vael": {**GOOD_PROFILE, "short_description": "A shadowy master."},
        }
        with patch("app.services.wiki.analyze_text_json", return_value=batch_result):
            result = batch_update_character_profiles(PAYLOAD)

        assert "ariane" in result
        assert "master_vael" in result
        assert result["ariane"]["short_description"] == "A powerful mage."

    def test_empty_payload_returns_empty_dict(self):
        """Empty input must return empty dict without any LLM call."""
        with patch("app.services.wiki.analyze_text_json") as mock_llm:
            result = batch_update_character_profiles({})
        mock_llm.assert_not_called()
        assert result == {}

    def test_non_dict_response_falls_back_to_sequential(self):
        """If LLM returns a list/string/None, falls back to sequential for all chars."""
        with patch("app.services.wiki.analyze_text_json", return_value="not a dict"):
            with patch("app.services.wiki._sequential_fallback", return_value={"ariane": GOOD_PROFILE}) as mock_seq:
                result = batch_update_character_profiles(PAYLOAD)
        mock_seq.assert_called_once()
        assert "ariane" in result

    def test_exception_in_batch_falls_back_to_sequential(self):
        """If the batch LLM call raises, sequential fallback handles all chars."""
        with patch("app.services.wiki.analyze_text_json", side_effect=Exception("timeout")):
            with patch("app.services.wiki._sequential_fallback", return_value={"ariane": GOOD_PROFILE}) as mock_seq:
                result = batch_update_character_profiles(PAYLOAD)
        mock_seq.assert_called_once()

    def test_partial_batch_falls_back_only_for_missing(self):
        """When batch misses one char, sequential fallback runs only for that char."""
        # Batch only returns ariane, not master_vael
        partial_result = {"ariane": {**GOOD_PROFILE}}

        vael_profile = {**GOOD_PROFILE, "short_description": "Vael via sequential."}

        with patch("app.services.wiki.analyze_text_json", return_value=partial_result):
            with patch("app.services.wiki._sequential_fallback", return_value={"master_vael": vael_profile}) as mock_seq:
                result = batch_update_character_profiles(PAYLOAD)

        # Sequential should be called only for the missing character
        mock_seq.assert_called_once()
        call_args = mock_seq.call_args[0][0]  # first positional arg = chars dict
        assert "master_vael" in call_args
        assert "ariane" not in call_args

        # Final result should have both
        assert "ariane" in result
        assert "master_vael" in result

    def test_batch_result_with_invalid_entry_triggers_fallback(self):
        """If a character's profile is not a dict (e.g. a string), fallback fires."""
        bad_result = {
            "ariane": GOOD_PROFILE,
            "master_vael": "just a string",  # not a dict
        }
        with patch("app.services.wiki.analyze_text_json", return_value=bad_result):
            with patch("app.services.wiki._sequential_fallback", return_value={"master_vael": GOOD_PROFILE}) as mock_seq:
                result = batch_update_character_profiles(PAYLOAD)
        mock_seq.assert_called_once()


class TestSequentialFallback:
    def test_calls_update_profile_per_character(self):
        """_sequential_fallback calls update_character_profile once per char."""
        with patch("app.services.wiki.update_character_profile", return_value=GOOD_PROFILE) as mock_upd:
            result = _sequential_fallback(PAYLOAD, model="groq/test")
        assert mock_upd.call_count == 2
        assert "ariane" in result
        assert "master_vael" in result

    def test_skips_chars_with_empty_profile_response(self):
        """Characters for which update_character_profile returns {} are excluded."""
        def mock_update(existing, events, name):
            if name == "Ariane":
                return {}  # simulate LLM returning nothing
            return GOOD_PROFILE

        with patch("app.services.wiki.update_character_profile", side_effect=mock_update):
            result = _sequential_fallback(PAYLOAD, model="groq/test")

        assert "ariane" not in result
        assert "master_vael" in result
