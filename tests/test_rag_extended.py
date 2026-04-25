"""
tests/test_rag_extended.py
====================================
Extended RAG tests covering:
  - query_story uses graph node aliases for entity matching
  - query_story fallback returns ≤15 most recent events when no entity found
  - query_character_profile returns relationships + new_timeline_events (C1 fix)
  - query_character_profile returns {} when character has no events
  - Time-CoT: all chapter ids appear in ascending order in the built prompt
"""

import pytest
from unittest.mock import patch, MagicMock

from adapters.graph_adapter import GraphProvider, _graph_instances


# ---------------------------------------------------------------------------
# Fixture: graph with aliases on nodes (A3 fix)
# ---------------------------------------------------------------------------

@pytest.fixture()
def alias_graph(tmp_path, monkeypatch):
    import app.core.story_manager as sm
    monkeypatch.setattr(sm.StoryManager, "DATA_DIR", str(tmp_path))
    _graph_instances.clear()

    gp = GraphProvider("rag_ext_story")
    # Node stored with an alias — simulates A3 fix
    gp.add_character("master_vael", {
        "display_name": "Master Vael",
        "aliases": ["Lord Vael", "the Shadow Master"],
    })
    gp.add_event(
        "ev1", "Master Vael emerges from darkness", ["master_vael"],
        chapter_id=1, location="Shadow Keep",
        pre_conditions="Night falls", post_conditions="City trembles",
    )
    yield gp
    _graph_instances.clear()


@pytest.fixture()
def multi_chapter_graph(tmp_path, monkeypatch):
    import app.core.story_manager as sm
    monkeypatch.setattr(sm.StoryManager, "DATA_DIR", str(tmp_path))
    _graph_instances.clear()

    gp = GraphProvider("rag_multi_story")
    gp.add_character("hero", {"display_name": "Hero"})

    # Add 20 events across 20 chapters
    for i in range(1, 21):
        gp.add_event(f"ev_{i}", f"Hero acts in chapter {i}", ["hero"],
                     chapter_id=i, location="Town")
    yield gp
    _graph_instances.clear()


# ---------------------------------------------------------------------------
# A3: RAG entity matching via graph node aliases
# ---------------------------------------------------------------------------

class TestRagAliasMatching:
    def test_query_with_alias_finds_character_events(self, alias_graph):
        """Querying by an alias ('Lord Vael') must retrieve that character's events."""
        captured = []

        def spy_analyze(prompt, model=None):
            captured.append(prompt)
            return "Lord Vael is dangerous."

        with patch("app.services.rag.get_graph_engine", return_value=alias_graph):
            with patch("app.services.rag.analyze_text", side_effect=spy_analyze):
                from app.services.rag import query_story
                query_story("rag_ext_story", "What did Lord Vael do?")

        assert captured, "analyze_text was never called"
        prompt = captured[0]
        # The event describing Vael must appear in the prompt
        assert "Master Vael emerges" in prompt, (
            "Event for Lord Vael (alias) should appear in prompt"
        )


# ---------------------------------------------------------------------------
# Fallback: ≤15 most-recent events when no entity found
# ---------------------------------------------------------------------------

class TestRagFallback:
    def test_general_fallback_caps_at_15_events(self, multi_chapter_graph):
        """When no entity found, fallback must use at most 15 recent events."""
        captured = []

        def spy_analyze(prompt, model=None):
            captured.append(prompt)
            return "General answer."

        with patch("app.services.rag.get_graph_engine", return_value=multi_chapter_graph):
            with patch("app.services.rag.analyze_text", side_effect=spy_analyze):
                from app.services.rag import query_story
                query_story("rag_multi_story", "What is happening in the world?")

        prompt = captured[0]
        # Count "Chapter X" occurrences — should be at most 15
        chapter_count = prompt.count("--- Chapter")
        assert chapter_count <= 15, f"Fallback retrieved {chapter_count} events (max is 15)"

    def test_general_fallback_uses_most_recent_chapters(self, multi_chapter_graph):
        """The fallback must prefer most-recent chapters (highest chapter_id)."""
        captured = []

        def spy_analyze(prompt, model=None):
            captured.append(prompt)
            return "."

        with patch("app.services.rag.get_graph_engine", return_value=multi_chapter_graph):
            with patch("app.services.rag.analyze_text", side_effect=spy_analyze):
                from app.services.rag import query_story
                query_story("rag_multi_story", "What is the latest development?")

        prompt = captured[0]
        # Chapter 20 (most recent) must appear; Chapter 1 (oldest) must NOT
        assert "Chapter 20" in prompt
        # Chapter 1 should be excluded (only top 15 by recency = chapters 6-20)
        assert "Chapter 1\n" not in prompt and "Chapter 1 " not in prompt


# ---------------------------------------------------------------------------
# C1: query_character_profile schema includes relationships + timeline
# ---------------------------------------------------------------------------

class TestQueryCharacterProfileSchema:
    def test_profile_schema_prompt_includes_relationships(self, alias_graph):
        """The RAG profile enrichment prompt must ask for 'relationships'."""
        captured_prompts = []

        def spy_json(prompt, model=None):
            captured_prompts.append(prompt)
            return {}

        with patch("app.services.rag.get_graph_engine", return_value=alias_graph):
            with patch("adapters.llm_adapter.analyze_text_json", side_effect=spy_json):
                from app.services.rag import query_character_profile
                query_character_profile("rag_ext_story", "master_vael", "Master Vael")

        assert captured_prompts, "analyze_text_json was never called"
        prompt = captured_prompts[0]
        assert "relationships" in prompt.lower(), (
            "Prompt must request 'relationships' field (C1 fix)"
        )
        assert "new_timeline_events" in prompt.lower(), (
            "Prompt must request 'new_timeline_events' field (C1 fix)"
        )

    def test_profile_returns_empty_for_no_graph_events(self, tmp_path, monkeypatch):
        """query_character_profile returns {} when character has no events."""
        import app.core.story_manager as sm
        monkeypatch.setattr(sm.StoryManager, "DATA_DIR", str(tmp_path))
        _graph_instances.clear()

        gp = GraphProvider("empty_char_story")
        gp.add_character("ghost", {"display_name": "Ghost"})
        # No events added for ghost

        with patch("app.services.rag.get_graph_engine", return_value=gp):
            from app.services.rag import query_character_profile
            result = query_character_profile("empty_char_story", "ghost", "Ghost")

        assert result == {}, f"Expected empty dict, got {result}"
        _graph_instances.clear()


# ---------------------------------------------------------------------------
# Time-CoT: chronological ordering in prompt
# ---------------------------------------------------------------------------

class TestTimeCotOrdering:
    def test_multi_event_prompt_is_strictly_ascending(self, tmp_path, monkeypatch):
        """All chapter IDs in the constructed prompt must appear in ascending order."""
        import app.core.story_manager as sm
        monkeypatch.setattr(sm.StoryManager, "DATA_DIR", str(tmp_path))
        _graph_instances.clear()

        gp = GraphProvider("timecot_story")
        gp.add_character("hero", {"display_name": "Hero"})
        # Add events out-of-order to verify sorting
        for ch in [5, 1, 3, 2, 4]:
            gp.add_event(f"ev_{ch}", f"Event in chapter {ch}", ["hero"], chapter_id=ch)

        captured = []
        with patch("app.services.rag.get_graph_engine", return_value=gp):
            with patch("app.services.rag.analyze_text", side_effect=lambda p, model=None: captured.append(p) or ""):
                from app.services.rag import query_story
                query_story("timecot_story", "What did Hero do?")

        prompt = captured[0]
        positions = []
        for ch in [1, 2, 3, 4, 5]:
            pos = prompt.find(f"Chapter {ch}")
            assert pos != -1, f"Chapter {ch} missing from prompt"
            positions.append(pos)

        assert positions == sorted(positions), (
            "Chapters must appear in ascending chronological order in the prompt"
        )
        _graph_instances.clear()
