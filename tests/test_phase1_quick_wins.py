"""
tests/test_phase1_quick_wins.py
================================
RED tests for Phase 1 quick-win items from Future_Ideas.md.
All tests MUST fail before any implementation is written.

Items covered:
  1.1  Dual-timeline fields on event nodes
  1.2  Spoiler & canonicity fields on event nodes
  1.3  Persistent LLM prompt cache (SQLite)
  1.4  Audio generation cache (disk-based mp3)
  1.5  Extraction pre-filtering (_prefilter_text helper)
  1.6  Character role on event edges
  1.7  Dynamic PageRank threshold scaling
  1.8  Conditional fixer pass
  1.9  Time-aware relationship edges (relation_history)
"""

import os
import pytest

from adapters.graph_adapter import GraphProvider


# ---------------------------------------------------------------------------
# Shared fixture
# ---------------------------------------------------------------------------

@pytest.fixture()
def gp(tmp_path, monkeypatch):
    import app.core.story_manager as sm
    monkeypatch.setattr(sm.StoryManager, "DATA_DIR", str(tmp_path))
    os.makedirs(os.path.join(str(tmp_path), "phase1_story"), exist_ok=True)
    return GraphProvider("phase1_story")


# ===========================================================================
# 1.1  Dual-Timeline Fields on Events
# ===========================================================================

class TestDualTimelineFields:
    """add_event must accept and persist timeline_type, narrative_order,
    story_time_rank, story_time_relative, and flashback_depth."""

    def _add_char_and_event(self, gp, **timeline_kwargs):
        gp.add_character("hero", {"display_name": "Hero"})
        gp.add_event(
            "ev1", "Hero remembers childhood", ["hero"],
            chapter_id=2,
            **timeline_kwargs,
        )

    def test_timeline_type_stored_on_event_node(self, gp):
        self._add_char_and_event(gp, timeline_type="flashback")
        assert gp.graph.nodes["ev1"]["timeline_type"] == "flashback"

    def test_narrative_order_stored(self, gp):
        self._add_char_and_event(gp, narrative_order=3)
        assert gp.graph.nodes["ev1"]["narrative_order"] == 3

    def test_story_time_rank_stored_when_provided(self, gp):
        self._add_char_and_event(gp, story_time_rank=7)
        assert gp.graph.nodes["ev1"]["story_time_rank"] == 7

    def test_story_time_rank_null_when_ambiguous(self, gp):
        self._add_char_and_event(gp, story_time_rank=None)
        assert gp.graph.nodes["ev1"]["story_time_rank"] is None

    def test_story_time_relative_stored(self, gp):
        self._add_char_and_event(gp, story_time_relative="before the siege")
        assert gp.graph.nodes["ev1"]["story_time_relative"] == "before the siege"

    def test_flashback_depth_stored(self, gp):
        self._add_char_and_event(gp, flashback_depth=2)
        assert gp.graph.nodes["ev1"]["flashback_depth"] == 2

    def test_present_event_defaults_to_zero_depth(self, gp):
        """An event with no explicit flashback_depth should default to 0."""
        self._add_char_and_event(gp)
        assert gp.graph.nodes["ev1"]["flashback_depth"] == 0

    def test_timeline_type_defaults_to_present(self, gp):
        self._add_char_and_event(gp)
        assert gp.graph.nodes["ev1"]["timeline_type"] == "present"

    def test_timeline_fields_survive_save_load(self, gp):
        self._add_char_and_event(
            gp, timeline_type="memory", narrative_order=1,
            story_time_rank=5, flashback_depth=1,
        )
        gp.save_graph()
        gp2 = GraphProvider("phase1_story")
        node = gp2.graph.nodes["ev1"]
        assert node["timeline_type"] == "memory"
        assert node["narrative_order"] == 1
        assert node["story_time_rank"] == 5
        assert node["flashback_depth"] == 1


# ===========================================================================
# 1.2  Spoiler & Canonicity Fields on Events
# ===========================================================================

class TestSpoilerCanonicity:
    """add_event must accept and persist reveal_point, spoiler_level,
    is_canonical, and confidence."""

    def _add(self, gp, **kwargs):
        gp.add_character("ravi", {"display_name": "Ravi"})
        gp.add_event("evS", "Ravi betrays Alice", ["ravi"], chapter_id=18, **kwargs)

    def test_reveal_point_stored(self, gp):
        self._add(gp, reveal_point=20)
        assert gp.graph.nodes["evS"]["reveal_point"] == 20

    def test_spoiler_level_stored(self, gp):
        self._add(gp, spoiler_level=2)
        assert gp.graph.nodes["evS"]["spoiler_level"] == 2

    def test_is_canonical_false_stored(self, gp):
        self._add(gp, is_canonical=False)
        assert gp.graph.nodes["evS"]["is_canonical"] is False

    def test_confidence_stored(self, gp):
        self._add(gp, confidence=0.4)
        assert abs(gp.graph.nodes["evS"]["confidence"] - 0.4) < 1e-9

    def test_defaults_are_safe(self, gp):
        """Default: reveal_point=0, spoiler_level=0, is_canonical=True, confidence=1.0"""
        self._add(gp)
        node = gp.graph.nodes["evS"]
        assert node["reveal_point"] == 0
        assert node["spoiler_level"] == 0
        assert node["is_canonical"] is True
        assert node["confidence"] == 1.0


# ===========================================================================
# 1.3  Persistent LLM Prompt Cache
# ===========================================================================

class TestLLMPromptCache:
    """analyze_text_json must read from / write to a SQLite cache keyed on
    hash(prompt + model).  A cache hit must return the same result without
    calling litellm."""

    def test_cache_hit_returns_same_result(self, tmp_path, monkeypatch):
        from adapters import llm_adapter

        call_count = {"n": 0}
        fake_result = {"active_character_names": ["Alice"]}

        def fake_run_with_retry(*args, **kwargs):
            call_count["n"] += 1
            return True, fake_result

        monkeypatch.setattr(llm_adapter, "_run_with_retry", fake_run_with_retry)
        monkeypatch.setenv("LLM_CACHE_DIR", str(tmp_path))

        prompt = "unique test prompt abc123"
        r1 = llm_adapter.analyze_text_json(prompt, model="groq/llama-3.1-8b-instant")
        r2 = llm_adapter.analyze_text_json(prompt, model="groq/llama-3.1-8b-instant")

        assert r1 == r2
        # Second call must be served from cache — no extra LLM hit
        assert call_count["n"] == 1

    def test_different_model_is_separate_cache_entry(self, tmp_path, monkeypatch):
        from adapters import llm_adapter

        results = {"a": {"model": "A"}, "b": {"model": "B"}}
        call_seq = iter([results["a"], results["b"]])

        def fake_run_with_retry(*args, **kwargs):
            return True, next(call_seq)

        monkeypatch.setattr(llm_adapter, "_run_with_retry", fake_run_with_retry)
        monkeypatch.setenv("LLM_CACHE_DIR", str(tmp_path))

        prompt = "same prompt"
        r_a = llm_adapter.analyze_text_json(prompt, model="groq/model-a")
        r_b = llm_adapter.analyze_text_json(prompt, model="groq/model-b")
        assert r_a != r_b

    def test_cache_persists_across_calls(self, tmp_path, monkeypatch):
        """Cache must be written to disk so a new process would hit it."""
        from adapters import llm_adapter

        call_count = {"n": 0}

        def fake_run(*args, **kwargs):
            call_count["n"] += 1
            return True, {"hit": True}

        monkeypatch.setattr(llm_adapter, "_run_with_retry", fake_run)
        monkeypatch.setenv("LLM_CACHE_DIR", str(tmp_path))

        llm_adapter.analyze_text_json("persist-test", model="groq/x")
        # Simulate cache being present for a second import by calling again
        llm_adapter.analyze_text_json("persist-test", model="groq/x")
        assert call_count["n"] == 1


# ===========================================================================
# 1.4  Audio Generation Cache
# ===========================================================================

class TestAudioGenerationCache:
    """get_tts_engine(...).generate_audio must skip synthesis when the output
    file already exists in the on-disk cache for the same (voice_id, text)."""

    def test_cache_hit_skips_engine_call(self, tmp_path, monkeypatch):
        from adapters.tts_adapter import CachedTTSAdapter

        real_calls = {"n": 0}

        class FakeInner:
            def generate_audio(self, text, voice_id, output_path, **kw):
                real_calls["n"] += 1
                pathlib.Path(output_path).write_bytes(b"fake-mp3")

        import pathlib
        adapter = CachedTTSAdapter(FakeInner(), cache_dir=str(tmp_path))
        out1 = str(tmp_path / "out1.mp3")
        adapter.generate_audio("Hello world", "af_sarah", out1)
        adapter.generate_audio("Hello world", "af_sarah", out1)

        assert real_calls["n"] == 1

    def test_different_text_is_not_cached(self, tmp_path, monkeypatch):
        from adapters.tts_adapter import CachedTTSAdapter
        import pathlib

        real_calls = {"n": 0}

        class FakeInner:
            def generate_audio(self, text, voice_id, output_path, **kw):
                real_calls["n"] += 1
                pathlib.Path(output_path).write_bytes(b"fake")

        adapter = CachedTTSAdapter(FakeInner(), cache_dir=str(tmp_path))
        adapter.generate_audio("Hello world", "af_sarah", str(tmp_path / "a.mp3"))
        adapter.generate_audio("Goodbye world", "af_sarah", str(tmp_path / "b.mp3"))
        assert real_calls["n"] == 2


# ===========================================================================
# 1.5  Extraction Pre-filtering
# ===========================================================================

class TestExtractionPrefilter:
    """_prefilter_text must return only event-dense paragraphs and reduce
    the total character count compared to the original text."""

    def test_prefilter_reduces_length(self):
        from app.services.extraction import _prefilter_text

        boring = "\n\n".join(["The sky was blue." * 10] * 5)
        action = "\n\nSuddenly Alice attacked Bob with a fierce blow!\n"
        text = boring + action + boring

        filtered = _prefilter_text(text)
        assert len(filtered) < len(text)

    def test_prefilter_keeps_action_paragraphs(self):
        from app.services.extraction import _prefilter_text

        action_para = "Alice struck Bob and he fell to the ground crying out."
        filler_para = "The weather was pleasant and nothing happened that day."
        text = filler_para + "\n\n" + action_para + "\n\n" + filler_para

        filtered = _prefilter_text(text)
        assert action_para in filtered

    def test_prefilter_returns_string(self):
        from app.services.extraction import _prefilter_text
        assert isinstance(_prefilter_text("Some text."), str)

    def test_prefilter_empty_input(self):
        from app.services.extraction import _prefilter_text
        assert _prefilter_text("") == ""


# ===========================================================================
# 1.6  Character Role on Event Edges
# ===========================================================================

class TestCharacterRoleOnEdges:
    """add_event must accept a character_roles dict and store the role on
    the Character→Event edge."""

    def test_role_stored_on_edge(self, gp):
        gp.add_character("alice", {"display_name": "Alice"})
        gp.add_character("ravi", {"display_name": "Ravi"})
        gp.add_event(
            "evR", "Alice is hurt by Ravi",
            ["alice", "ravi"], chapter_id=5,
            character_roles={"alice": "victim", "ravi": "cause"},
        )
        assert gp.graph["alice"]["evR"]["role"] == "victim"
        assert gp.graph["ravi"]["evR"]["role"] == "cause"

    def test_no_roles_defaults_to_participant(self, gp):
        gp.add_character("hero", {"display_name": "Hero"})
        gp.add_event("evD", "Hero wanders", ["hero"], chapter_id=1)
        assert gp.graph["hero"]["evD"].get("role", "participant") == "participant"

    def test_role_survives_save_load(self, gp):
        gp.add_character("bob", {"display_name": "Bob"})
        gp.add_event(
            "evPersist", "Bob witnesses event",
            ["bob"], chapter_id=3,
            character_roles={"bob": "witness"},
        )
        gp.save_graph()
        gp2 = GraphProvider("phase1_story")
        assert gp2.graph["bob"]["evPersist"]["role"] == "witness"


# ===========================================================================
# 1.7  Dynamic PageRank Threshold Scaling
# ===========================================================================

class TestDynamicThresholdScaling:
    """compute_chapter_scores should use a dynamic MAIN_CAST threshold that
    scales with total node count (M_base / N), so late-series characters
    can still graduate."""

    def test_dynamic_threshold_exposed(self):
        """GraphProvider must expose get_dynamic_main_cast_threshold(node_count)."""
        from adapters.graph_adapter import GraphProvider
        # Just needs to exist and be callable
        gp = GraphProvider.__new__(GraphProvider)
        gp.graph = __import__("networkx").DiGraph()
        result = GraphProvider.get_dynamic_main_cast_threshold(100)
        assert isinstance(result, float)
        assert result > 0.0

    def test_threshold_decreases_as_graph_grows(self):
        """Threshold with 10 nodes > threshold with 100 nodes."""
        from adapters.graph_adapter import GraphProvider
        small = GraphProvider.get_dynamic_main_cast_threshold(10)
        large = GraphProvider.get_dynamic_main_cast_threshold(100)
        assert small > large

    def test_threshold_never_below_delta_upper(self):
        """Even with 10 000 nodes, threshold must stay >= DELTA_UPPER."""
        from adapters.graph_adapter import GraphProvider
        from app.core.graduation import DELTA_UPPER
        t = GraphProvider.get_dynamic_main_cast_threshold(10_000)
        assert t >= DELTA_UPPER


# ===========================================================================
# 1.8  Conditional Fixer Pass
# ===========================================================================

class TestConditionalFixerPass:
    """_check_fixer_triggers must flag deterministically-detectable issues
    without making any LLM call."""

    def test_flags_conflicting_story_time_rank(self):
        from app.services.ingest import _check_fixer_triggers

        events = [
            {"id": "e1", "story_time_rank": 10, "narrative_order": 1, "timeline_type": "flashback"},
            {"id": "e2", "story_time_rank": 5,  "narrative_order": 2, "timeline_type": "present"},
        ]
        # e1 is a flashback (rank 10) but appears before e2 (rank 5, present).
        # A flashback should have a lower story_time_rank than the surrounding present.
        flags = _check_fixer_triggers(events)
        assert any(f["event_id"] == "e1" and "story_time_rank" in f["reason"] for f in flags)

    def test_flags_missing_timeline_type(self):
        from app.services.ingest import _check_fixer_triggers

        events = [{"id": "eX", "timeline_type": None, "narrative_order": 1}]
        flags = _check_fixer_triggers(events)
        assert any(f["event_id"] == "eX" for f in flags)

    def test_no_flags_on_clean_events(self):
        from app.services.ingest import _check_fixer_triggers

        events = [
            {"id": "e1", "story_time_rank": 1, "narrative_order": 1, "timeline_type": "present"},
            {"id": "e2", "story_time_rank": 2, "narrative_order": 2, "timeline_type": "present"},
        ]
        flags = _check_fixer_triggers(events)
        assert flags == []

    def test_returns_list(self):
        from app.services.ingest import _check_fixer_triggers
        assert isinstance(_check_fixer_triggers([]), list)


# ===========================================================================
# 1.9  Time-Aware Character Relationship Edges (relation_history)
# ===========================================================================

class TestRelationHistory:
    """add_or_update_character_edge must append to relation_history instead of
    overwriting relation_type, so full arc evolution is preserved."""

    def test_first_encounter_creates_history_entry(self, gp):
        gp.add_character("alice", {"display_name": "Alice"})
        gp.add_character("ravi", {"display_name": "Ravi"})
        gp.add_or_update_character_edge("alice", "ravi", relation_type="trusts", chapter_id=3)
        history = gp.graph["alice"]["ravi"]["relation_history"]
        assert history == [{"chapter": 3, "relation": "trusts"}]

    def test_second_encounter_appends_not_overwrites(self, gp):
        gp.add_character("alice", {"display_name": "Alice"})
        gp.add_character("ravi", {"display_name": "Ravi"})
        gp.add_or_update_character_edge("alice", "ravi", relation_type="trusts", chapter_id=3)
        gp.add_or_update_character_edge("alice", "ravi", relation_type="distrusts", chapter_id=8)
        history = gp.graph["alice"]["ravi"]["relation_history"]
        assert len(history) == 2
        assert history[0] == {"chapter": 3, "relation": "trusts"}
        assert history[1] == {"chapter": 8, "relation": "distrusts"}

    def test_betrayal_arc_visible_in_history(self, gp):
        """Key scenario from Future_Ideas: the betrayal arc must NOT be invisible."""
        gp.add_character("alice", {"display_name": "Alice"})
        gp.add_character("ravi", {"display_name": "Ravi"})
        for ch, rel in [(3, "trusts"), (5, "trusts"), (8, "distrusts")]:
            gp.add_or_update_character_edge("alice", "ravi", relation_type=rel, chapter_id=ch)
        history = gp.graph["alice"]["ravi"]["relation_history"]
        relations = [e["relation"] for e in history]
        assert "trusts" in relations
        assert "distrusts" in relations

    def test_relation_history_survives_save_load(self, gp):
        gp.add_character("x", {"display_name": "X"})
        gp.add_character("y", {"display_name": "Y"})
        gp.add_or_update_character_edge("x", "y", relation_type="ally", chapter_id=1)
        gp.add_or_update_character_edge("x", "y", relation_type="enemy", chapter_id=9)
        gp.save_graph()
        gp2 = GraphProvider("phase1_story")
        history = gp2.graph["x"]["y"]["relation_history"]
        assert len(history) == 2
