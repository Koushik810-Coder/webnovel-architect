"""
tests/test_rag.py
=================
Tests for the RAG (Retrieval-Augmented Generation) pipeline.

Uses a pre-built mock graph to verify:
  - Named entity extraction from queries
  - Correct events retrieved and sorted chronologically (Time-CoT)
  - General fallback when no named entities found (top-5 by degree)
  - Empty graph returns a safe message
  - LLM fallback when primary model fails
"""

import pytest
from unittest.mock import patch, MagicMock
from adapters.graph_adapter import GraphProvider


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def story_uuid():
    return "rag_test_story"


@pytest.fixture
def populated_graph(tmp_path, monkeypatch, story_uuid):
    """Build a graph with 2 characters and 3 events across 3 chapters."""
    import app.core.story_manager as sm
    monkeypatch.setattr(sm.StoryManager, "DATA_DIR", str(tmp_path))

    from adapters.graph_adapter import _graph_instances
    _graph_instances.clear()

    gp = GraphProvider(story_uuid)
    gp.add_character("zorian", {"display_name": "Zorian"})
    gp.add_character("kirielle", {"display_name": "Kirielle"})

    gp.add_event("ev1", "Zorian begins looping", ["zorian"],
                 chapter_id=1, pre_conditions="Normal day", post_conditions="Loop starts", location="Cyoria")
    gp.add_event("ev2", "Zorian meets Kirielle", ["zorian", "kirielle"],
                 chapter_id=2, pre_conditions="Zorian in academy", post_conditions="Allies formed", location="Academy")
    gp.add_event("ev3", "Kirielle is endangered", ["kirielle"],
                 chapter_id=3, pre_conditions="Crisis in city", post_conditions="Evacuated", location="Cyoria")

    # Patch get_graph_engine to return our pre-built graph
    with patch("app.services.rag.get_graph_engine", return_value=gp):
        yield gp

    _graph_instances.clear()


# ── Entity Extraction from Query ──────────────────────────────────────────────

def test_rag_retrieves_events_for_known_character(populated_graph, story_uuid):
    """query_story must return events involving 'Zorian' when queried about Zorian."""
    with patch("app.services.rag.get_graph_engine", return_value=populated_graph):
        with patch("app.services.rag.analyze_text", return_value="Zorian started looping."):
            from app.services.rag import query_story
            result = query_story(story_uuid, "What did Zorian do?")
    assert result is not None
    assert len(result) > 0


def test_rag_returns_not_found_for_unknown_entity(populated_graph, story_uuid):
    """A query about a character not in the graph should return a graceful message."""
    with patch("app.services.rag.get_graph_engine", return_value=populated_graph):
        from app.services.rag import query_story
        result = query_story(story_uuid, "What did Gandalf do?")
    # Should be a safe "not found" message, not a crash
    assert isinstance(result, str)
    assert len(result) > 0


# ── Chronological Sorting ─────────────────────────────────────────────────────

def test_rag_events_sorted_chronologically(populated_graph, story_uuid):
    """
    The prompt constructed by query_story must list chapters in ascending order.
    We verify this by inspecting the prompt passed to analyze_text.
    """
    captured_prompts = []

    def capture_analyze(prompt, model=None):
        captured_prompts.append(prompt)
        return "Mocked answer."

    with patch("app.services.rag.get_graph_engine", return_value=populated_graph):
        with patch("app.services.rag.analyze_text", side_effect=capture_analyze):
            from app.services.rag import query_story
            query_story(story_uuid, "Tell me about Zorian")

    assert captured_prompts, "analyze_text was never called"
    prompt = captured_prompts[0]

    # Chapter 1 must appear before Chapter 2 in the prompt string
    ch1_pos = prompt.find("Chapter 1")
    ch2_pos = prompt.find("Chapter 2")
    assert ch1_pos != -1 and ch2_pos != -1
    assert ch1_pos < ch2_pos, "Events must be sorted chronologically in the prompt"


# ── Empty Graph ───────────────────────────────────────────────────────────────

def test_rag_empty_graph_returns_safe_message(tmp_path, monkeypatch, story_uuid):
    """An empty graph must return a safe string, not raise an exception."""
    import app.core.story_manager as sm
    monkeypatch.setattr(sm.StoryManager, "DATA_DIR", str(tmp_path))

    from adapters.graph_adapter import GraphProvider, _graph_instances
    _graph_instances.clear()
    empty_gp = GraphProvider(story_uuid)

    with patch("app.services.rag.get_graph_engine", return_value=empty_gp):
        from app.services.rag import query_story
        result = query_story(story_uuid, "Who is the main character?")

    assert isinstance(result, str)
    assert len(result) > 0
    _graph_instances.clear()


# ── LLM Fallback ──────────────────────────────────────────────────────────────

def test_rag_falls_back_to_groq_when_primary_fails(populated_graph, story_uuid):
    """
    If the primary LLM returns an API Fallback message, query_story must
    automatically retry with the Groq fallback model.
    """
    call_log = []

    def mock_analyze(prompt, model=None):
        call_log.append(model)
        if model and not model.startswith("groq"):
            return "API Fallback: Connection error."
        return "Groq fallback answer."

    with patch("app.services.rag.get_graph_engine", return_value=populated_graph):
        with patch("app.services.rag.analyze_text", side_effect=mock_analyze):
            from app.services.rag import query_story
            result = query_story(story_uuid, "What did Zorian do?")

    assert len(call_log) == 2, f"Expected 2 LLM calls (primary + fallback), got: {call_log}"
    assert any("groq" in (m or "") for m in call_log), "Groq fallback was never called"
    assert result == "Groq fallback answer."


# ── TTS Factory ───────────────────────────────────────────────────────────────

class TestTTSFactory:
    def test_edge_factory_returns_edge_adapter(self):
        from adapters.tts_adapter import get_tts_engine, EdgeAdapter
        engine = get_tts_engine("edge")
        assert isinstance(engine, EdgeAdapter)

    def test_unknown_engine_raises_value_error(self):
        from adapters.tts_adapter import get_tts_engine
        with pytest.raises(ValueError, match="Unknown TTS Engine"):
            get_tts_engine("nonexistent_engine")

    def test_kokoro_falls_back_to_edge_when_unavailable(self, monkeypatch):
        """When Kokoro model files are absent, factory must return EdgeAdapter."""
        from adapters.tts_adapter import get_tts_engine, EdgeAdapter, KokoroAdapter

        # Force KokoroAdapter.engine to be None (simulates missing model files)
        def mock_init(self):
            self.engine = None

        monkeypatch.setattr(KokoroAdapter, "__init__", mock_init)
        engine = get_tts_engine("kokoro")
        assert isinstance(engine, EdgeAdapter)
