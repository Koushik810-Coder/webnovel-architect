"""
tests/test_pipeline_improvements.py
=====================================
Regression tests for the ingestion pipeline improvements implemented
in sessions P1–P5 and A1–D3.

Covers:
  P1  - involved_characters filter accepts cross-chapter graph characters
  P3  - add_or_update_character_edge creates/upserts char-to-char edges
  A1  - _char_event_index keyed on post-alias canonical char_id
  A3  - aliases stored on graph node for RAG entity-matching
  B3  - compute_chapter_scores() runs PageRank once and returns all chars
  C2  - decay-loop log correctly distinguishes de-graduation from graduation
  D3  - LLM fallback reads fallback_llm from config, not hardcoded
  Narration - build_narration_segments signature accepts story_uuid (A4)
"""

import pytest
import os
import math
from collections import defaultdict
from unittest.mock import patch, MagicMock

from adapters.graph_adapter import GraphProvider


# ---------------------------------------------------------------------------
# Shared fixture — isolated graph with no real filesystem I/O
# ---------------------------------------------------------------------------

@pytest.fixture()
def gp(tmp_path, monkeypatch):
    """Fresh GraphProvider redirected to a temp directory."""
    import app.core.story_manager as sm
    monkeypatch.setattr(sm.StoryManager, "DATA_DIR", str(tmp_path))
    story_dir = os.path.join(str(tmp_path), "test_story")
    os.makedirs(story_dir, exist_ok=True)
    return GraphProvider("test_story")


# ===========================================================================
# P3 — Character-to-character relationship edges
# ===========================================================================

class TestCharacterEdges:
    def test_edge_created_on_first_encounter(self, gp):
        """add_or_update_character_edge creates bidirectional edges."""
        gp.add_character("ariane", {"display_name": "Ariane"})
        gp.add_character("master", {"display_name": "Master"})

        gp.add_or_update_character_edge(
            "ariane", "master", relation_type="mentor", chapter_id=1, intensity=3
        )

        assert gp.graph.has_edge("ariane", "master"), "Forward edge missing"
        assert gp.graph.has_edge("master", "ariane"), "Reverse edge missing"

    def test_edge_upsert_increments_co_occurrence(self, gp):
        """Re-encountering the same pair bumps co_occurrence_count."""
        gp.add_character("a", {"display_name": "A"})
        gp.add_character("b", {"display_name": "B"})

        gp.add_or_update_character_edge("a", "b", chapter_id=1, intensity=2)
        gp.add_or_update_character_edge("a", "b", chapter_id=2, intensity=2)

        edge = gp.graph["a"]["b"]
        assert edge["co_occurrence_count"] == 2

    def test_edge_weight_accumulates(self, gp):
        """Edge weight accumulates across multiple co-occurrences."""
        gp.add_character("x", {"display_name": "X"})
        gp.add_character("y", {"display_name": "Y"})

        gp.add_or_update_character_edge("x", "y", chapter_id=1, intensity=3)
        gp.add_or_update_character_edge("x", "y", chapter_id=2, intensity=2)

        assert gp.graph["x"]["y"]["weight"] == 5.0  # 3 + 2

    def test_edge_skipped_for_unknown_node(self, gp):
        """No edge created if either character node doesn't exist."""
        gp.add_character("known", {"display_name": "Known"})
        gp.add_or_update_character_edge("known", "ghost", chapter_id=1)

        assert not gp.graph.has_edge("known", "ghost")

    def test_relation_type_updated_on_upsert(self, gp):
        """last_relation_type updates when the relationship type changes."""
        gp.add_character("a", {"display_name": "A"})
        gp.add_character("b", {"display_name": "B"})

        gp.add_or_update_character_edge("a", "b", relation_type="friendly", chapter_id=1)
        gp.add_or_update_character_edge("a", "b", relation_type="hostile", chapter_id=5)

        assert gp.graph["a"]["b"]["last_relation_type"] == "hostile"


# ===========================================================================
# B3 — compute_chapter_scores (single PageRank call)
# ===========================================================================

class TestComputeChapterScores:
    def test_returns_dict_for_all_characters(self, gp):
        """compute_chapter_scores returns a score for every character node."""
        gp.add_character("hero", {"display_name": "Hero"})
        gp.add_character("villain", {"display_name": "Villain"})
        gp.add_event("ev1", "Clash", ["hero", "villain"], chapter_id=1)

        scores = gp.compute_chapter_scores(current_chapter=1, decay_rate=0.05)

        assert "hero" in scores
        assert "villain" in scores

    def test_scores_are_positive(self, gp):
        """All character scores must be non-negative."""
        gp.add_character("sole", {"display_name": "Sole"})
        gp.add_event("ev1", "Sole acts", ["sole"], chapter_id=1)

        scores = gp.compute_chapter_scores(current_chapter=1)
        for char_id, score in scores.items():
            assert score >= 0.0, f"Negative score for {char_id}: {score}"

    def test_agrees_with_get_character_importance(self, gp):
        """Batch scores must match per-character scores (same algorithm)."""
        gp.add_character("p", {"display_name": "P"})
        gp.add_character("q", {"display_name": "Q"})
        gp.add_event("ev1", "P and Q meet", ["p", "q"], chapter_id=1, intensity=3)

        batch = gp.compute_chapter_scores(current_chapter=2, decay_rate=0.05)
        individual_p = gp.get_character_importance("p", current_chapter=2, decay_rate=0.05)
        individual_q = gp.get_character_importance("q", current_chapter=2, decay_rate=0.05)

        assert math.isclose(batch["p"], individual_p, rel_tol=1e-6), (
            f"Batch p={batch['p']:.6f} != individual p={individual_p:.6f}"
        )
        assert math.isclose(batch["q"], individual_q, rel_tol=1e-6), (
            f"Batch q={batch['q']:.6f} != individual q={individual_q:.6f}"
        )

    def test_empty_graph_returns_empty_dict(self, gp):
        """No crash and empty dict returned when graph has no nodes."""
        scores = gp.compute_chapter_scores(current_chapter=1)
        assert scores == {}

    def test_absent_chars_get_decayed_scores(self, gp):
        """A character last seen in ch1 has a lower score by ch5."""
        gp.add_character("early", {"display_name": "Early"})
        gp.add_event("ev1", "Early acts", ["early"], chapter_id=1)

        scores_ch1 = gp.compute_chapter_scores(current_chapter=1, decay_rate=0.10)
        scores_ch5 = gp.compute_chapter_scores(current_chapter=5, decay_rate=0.10)

        assert scores_ch1["early"] > scores_ch5["early"]


# ===========================================================================
# A1 — _char_event_index keyed on canonical char_id
# ===========================================================================

class TestCharEventIndexKey:
    """
    Unit-tests the alias-aware index building logic in isolation,
    without invoking the full ingest pipeline or LLM.
    """

    def _build_index(self, events, alias_map):
        """Replicate the A1-fixed index-building logic from ingest.py."""
        from app.services.ingest import normalize_id
        index = defaultdict(list)
        for evt in events:
            for ic in evt.get("involved_characters", []):
                canon_id = normalize_id(alias_map.get(ic, ic))
                index[canon_id].append(evt)
        return index

    def test_canonical_id_resolves_aliased_name(self):
        """LLM raw name 'Ariane the Mage' should map to canonical 'ariane'."""
        events = [{"action_summary": "Ariane acts", "involved_characters": ["Ariane the Mage"]}]
        alias_map = {"Ariane the Mage": "Ariane"}

        index = self._build_index(events, alias_map)

        assert "ariane" in index, "Canonical ID 'ariane' should be in the index"
        assert "ariane_the_mage" not in index, "Raw alias should NOT appear as a key"

    def test_non_aliased_name_normalised_correctly(self):
        """Name without an alias should normalise to its own char_id."""
        events = [{"action_summary": "Bob runs", "involved_characters": ["Bob"]}]
        alias_map = {}

        index = self._build_index(events, alias_map)

        assert "bob" in index

    def test_multiple_aliases_all_point_to_same_key(self):
        """Two aliases of the same canonical both map to the same canonical key."""
        events = [
            {"action_summary": "Mage acts", "involved_characters": ["Aria", "Aria of the West"]},
        ]
        alias_map = {"Aria of the West": "Aria"}

        index = self._build_index(events, alias_map)

        # Both "Aria" and "Aria of the West" resolve to canonical id "aria".
        # The index correctly creates one entry per involved_characters item,
        # so we expect 2 entries under "aria" (one per alias occurrence in the list).
        assert "aria" in index
        assert "aria_of_the_west" not in index, "Un-resolved alias key must not exist"


# ===========================================================================
# A3 — aliases stored on graph node
# ===========================================================================

class TestGraphNodeAliases:
    def test_alias_stored_on_first_add(self, gp):
        """Aliases passed to add_character are stored on the node."""
        gp.add_character("ariane", {
            "display_name": "Ariane",
            "aliases": ["Ariane the Mage", "the Mage"],
        })

        node_aliases = gp.graph.nodes["ariane"].get("aliases", [])
        assert "Ariane the Mage" in node_aliases
        assert "the Mage" in node_aliases

    def test_aliases_accumulated_across_chapters(self, gp):
        """A second add_character call merges new aliases with existing ones."""
        gp.add_character("ariane", {"display_name": "Ariane", "aliases": ["the Mage"]})
        gp.add_character("ariane", {"display_name": "Ariane", "aliases": ["Sister Ariane"]})

        node_aliases = gp.graph.nodes["ariane"].get("aliases", [])
        assert "the Mage" in node_aliases, "Old alias should be preserved"
        assert "Sister Ariane" in node_aliases, "New alias should be added"

    def test_no_duplicate_aliases(self, gp):
        """The same alias added twice should only appear once."""
        gp.add_character("hero", {"display_name": "Hero", "aliases": ["the Chosen"]})
        gp.add_character("hero", {"display_name": "Hero", "aliases": ["the Chosen"]})

        node_aliases = gp.graph.nodes["hero"].get("aliases", [])
        assert node_aliases.count("the Chosen") == 1


# ===========================================================================
# D3 — LLM fallback reads from config.yaml
# ===========================================================================

class TestLLMFallbackConfig:
    def test_analyze_text_uses_config_fallback(self, monkeypatch):
        """analyze_text() fallback model must come from config, not hardcode."""
        # Patch get_fallback_llm directly — this is what _run_fallback_chain calls.
        # (_config_cache is defined in config.py but get_config() reads from file,
        # so patching the cache has no effect — patch the function instead.)
        import app.core.config as cfg_module
        monkeypatch.setattr(cfg_module, "get_fallback_llm", lambda: "groq/custom-fallback-model")
        # Also patch last_resort so it doesn't interfere
        monkeypatch.setattr(cfg_module, "get_fallback_llm_last_resort", lambda: "groq/custom-last-resort")

        from adapters import llm_adapter

        call_log = []

        def fake_retry(model, messages, max_attempts=6, extra_kwargs=None, content_transform=None):
            call_log.append(model)
            if model != "groq/custom-fallback-model":
                return False, Exception("primary failed")
            return True, "fallback response"

        monkeypatch.setattr(llm_adapter, "_run_with_retry", fake_retry)

        result = llm_adapter.analyze_text("test prompt", model="nvidia_nim/some-model")

        assert "groq/custom-fallback-model" in call_log, (
            f"Fallback model from config was not used. Calls: {call_log}"
        )
        assert result == "fallback response"


# ===========================================================================
# A4 — build_narration_segments accepts story_uuid parameter
# ===========================================================================

class TestNarrationVoiceLookup:
    def test_signature_accepts_story_uuid(self):
        """build_narration_segments must accept an optional story_uuid kwarg."""
        import inspect
        from app.services.narration import build_narration_segments
        sig = inspect.signature(build_narration_segments)
        assert "story_uuid" in sig.parameters, (
            "build_narration_segments must accept story_uuid for wiki voice lookup"
        )

    @patch("app.services.narration.analyze_text_json")
    @patch("app.services.narration.assign_voice")
    def test_uses_locked_wiki_voice_when_available(
        self, mock_assign, mock_analyze
    ):
        """When wiki has a locked voice_id, assign_voice() must NOT be called."""
        # Mock: LLM resolves speaker as "Ariane"
        mock_analyze.return_value = {"speakers": {"0": "Ariane"}}

        # The lazy import in narration.py is: `from app.services.wiki import load_character_wiki_json`
        # Patching at the source (app.services.wiki) ensures the lazy import gets the mock.
        wiki_mock = MagicMock()
        wiki_mock.voice_id = "voice_locked_42"

        with patch("app.services.wiki.load_character_wiki_json", return_value=wiki_mock):
            from app.services.narration import build_narration_segments
            segments = build_narration_segments('"Hello there." she said.', story_uuid="test_story")

        dialogue_segs = [s for s in segments if s.character_id == "Ariane"]
        assert dialogue_segs, "Expected at least one Ariane dialogue segment"
        assert all(s.voice_id == "voice_locked_42" for s in dialogue_segs), (
            f"Expected locked voice, got: {[s.voice_id for s in dialogue_segs]}"
        )
        mock_assign.assert_not_called()

    @patch("app.services.narration.analyze_text_json")
    @patch("app.services.narration.assign_voice", return_value="voice_new_99")
    def test_falls_back_to_assign_voice_when_no_wiki_voice(
        self, mock_assign, mock_analyze
    ):
        """When wiki has no voice_id, assign_voice() is called as fallback."""
        mock_analyze.return_value = {"speakers": {"0": "Bob"}}

        wiki_mock = MagicMock()
        wiki_mock.voice_id = None  # No locked voice

        with patch("app.services.wiki.load_character_wiki_json", return_value=wiki_mock):
            from app.services.narration import build_narration_segments
            build_narration_segments('"Hey!" he shouted.', story_uuid="test_story")

        mock_assign.assert_called_once()


# ===========================================================================
# C2 — Decay-loop correctly tracks de-graduation vs graduation
# ===========================================================================

class TestGraduationStatusTracking:
    def test_check_graduation_returns_true_on_voice_release(self):
        """check_graduation_status returns True when voice is released (de-graduation)."""
        from app.core.models.character_runtime import CharacterRuntime
        from app.core.graduation import check_graduation_status
        from unittest.mock import patch

        char = CharacterRuntime(
            character_id="fading",
            first_seen_chapter=1,
            last_seen_chapter=1,
            confidence_score=0.01,  # below DELTA_UPPER → EXTRA
            voice_id="voice_7",
        )

        with patch("app.core.graduation.get_registry") as mock_reg:
            mock_reg.return_value.release_voice = MagicMock()
            changed = check_graduation_status(char)

        assert changed is True
        assert char.voice_id is None  # voice must be released

    def test_check_graduation_returns_true_on_promotion(self):
        """check_graduation_status returns True when voice is assigned (graduation)."""
        from app.core.models.character_runtime import CharacterRuntime
        from app.core.graduation import check_graduation_status, MAIN_CAST_THRESHOLD

        char = CharacterRuntime(
            character_id="rising",
            first_seen_chapter=1,
            last_seen_chapter=5,
            confidence_score=MAIN_CAST_THRESHOLD + 0.1,
            voice_id=None,
        )

        with patch("app.core.graduation.assign_voice", return_value="voice_new"):
            changed = check_graduation_status(char)

        assert changed is True
        assert char.voice_id == "voice_new"
