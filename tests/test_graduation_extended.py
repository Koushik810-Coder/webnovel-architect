"""
tests/test_graduation_extended.py
====================================
Extended graduation logic tests covering:
  - All three GraduationLevel boundaries (EXTRA / EVOLVING / MAIN_CAST)
  - EVOLVING characters retain their voice_id (no de-graduation at mid-range)
  - Voice is released only when score drops fully below DELTA_UPPER
  - check_graduation_status is idempotent (no state change on second call)
  - Protagonist with max score always reaches MAIN_CAST
"""

from unittest.mock import patch, MagicMock

from app.core.graduation import (
    evaluate_graduation,
    check_graduation_status,
    GraduationLevel,
    DELTA_UPPER,
    MAIN_CAST_THRESHOLD,
)
from app.core.models.character_runtime import CharacterRuntime


# ---------------------------------------------------------------------------
# evaluate_graduation — pure boundary tests
# ---------------------------------------------------------------------------

class TestEvaluateGraduation:
    def test_score_zero_is_extra(self):
        assert evaluate_graduation(0.0) == GraduationLevel.EXTRA

    def test_score_just_below_delta_upper_is_extra(self):
        assert evaluate_graduation(DELTA_UPPER - 0.001) == GraduationLevel.EXTRA

    def test_score_exactly_delta_upper_is_evolving(self):
        assert evaluate_graduation(DELTA_UPPER) == GraduationLevel.EVOLVING

    def test_score_midrange_is_evolving(self):
        mid = (DELTA_UPPER + MAIN_CAST_THRESHOLD) / 2
        assert evaluate_graduation(mid) == GraduationLevel.EVOLVING

    def test_score_just_below_main_cast_is_evolving(self):
        assert evaluate_graduation(MAIN_CAST_THRESHOLD - 0.001) == GraduationLevel.EVOLVING

    def test_score_exactly_main_cast_is_main_cast(self):
        assert evaluate_graduation(MAIN_CAST_THRESHOLD) == GraduationLevel.MAIN_CAST

    def test_score_above_main_cast_is_main_cast(self):
        assert evaluate_graduation(1.0) == GraduationLevel.MAIN_CAST


# ---------------------------------------------------------------------------
# check_graduation_status — state transition tests
# ---------------------------------------------------------------------------

class TestCheckGraduationStatus:
    def _make_char(self, char_id="hero", score=0.0, voice_id=None):
        return CharacterRuntime(
            character_id=char_id,
            first_seen_chapter=1,
            last_seen_chapter=1,
            confidence_score=score,
            voice_id=voice_id,
        )

    # ── Graduation (None → voice) ───────────────────────────────────────────

    def test_graduation_assigns_voice(self):
        char = self._make_char(score=MAIN_CAST_THRESHOLD + 0.1)
        with patch("app.core.graduation.assign_voice", return_value="voice_99"):
            changed = check_graduation_status(char)
        assert changed is True
        assert char.voice_id == "voice_99"

    def test_graduation_uses_gender_from_wiki_traits(self):
        """The gender passed in wiki_traits must be forwarded to assign_voice."""
        char = self._make_char(score=MAIN_CAST_THRESHOLD + 0.1)
        captured = {}

        def spy_assign(char_id, traits=None):
            captured["traits"] = traits
            return "v1"

        with patch("app.core.graduation.assign_voice", side_effect=spy_assign):
            check_graduation_status(char, wiki_traits={"gender": "female"})

        assert captured.get("traits", {}).get("gender") == "female"

    # ── Idempotency ────────────────────────────────────────────────────────

    def test_already_graduated_no_second_voice_assignment(self):
        """A character who already has voice_id must not get a second assignment."""
        char = self._make_char(score=MAIN_CAST_THRESHOLD + 0.1, voice_id="voice_existing")
        with patch("app.core.graduation.assign_voice") as mock_assign:
            changed = check_graduation_status(char)
        mock_assign.assert_not_called()
        assert changed is False
        assert char.voice_id == "voice_existing"

    # ── EVOLVING retains voice ─────────────────────────────────────────────

    def test_evolving_score_retains_voice(self):
        """EVOLVING characters (score between thresholds) must NOT lose their voice."""
        mid = (DELTA_UPPER + MAIN_CAST_THRESHOLD) / 2
        char = self._make_char(score=mid, voice_id="voice_keep")
        with patch("app.core.graduation.get_registry") as mock_reg:
            changed = check_graduation_status(char)
        mock_reg.return_value.release_voice.assert_not_called()
        assert char.voice_id == "voice_keep"  # voice preserved
        assert changed is False

    # ── De-graduation (voice → None) ───────────────────────────────────────

    def test_de_graduation_releases_voice_below_extra(self):
        """Score dropping below DELTA_UPPER must release the voice."""
        char = self._make_char(score=DELTA_UPPER - 0.05, voice_id="voice_old")
        with patch("app.core.graduation.get_registry") as mock_reg:
            mock_reg.return_value.release_voice = MagicMock()
            changed = check_graduation_status(char)
        assert changed is True
        assert char.voice_id is None
        mock_reg.return_value.release_voice.assert_called_once_with("voice_old")

    def test_no_change_when_extra_and_no_voice(self):
        """EXTRA score + no voice = no state change."""
        char = self._make_char(score=0.0, voice_id=None)
        changed = check_graduation_status(char)
        assert changed is False

    # ── Edge: score exactly at boundaries ─────────────────────────────────

    def test_boundary_delta_upper_does_not_trigger_graduation(self):
        """Score == DELTA_UPPER is EVOLVING, not MAIN_CAST — no voice assigned."""
        char = self._make_char(score=DELTA_UPPER, voice_id=None)
        with patch("app.core.graduation.assign_voice") as mock_assign:
            check_graduation_status(char)
        mock_assign.assert_not_called()
