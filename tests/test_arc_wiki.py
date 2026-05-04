"""
tests/test_arc_wiki.py
=======================
Phase 2.5 — Arc Wiki Pages

Covers:
  - ArcWiki Pydantic model
  - save_arc_wiki / load_arc_wiki persistence
  - list_arc_wikis helper
  - render_arc_wiki Markdown renderer (theme, start event, escalation,
    turning point, resolution, characters, emotional/thematic evolution)
  - build_arc_page LLM page generator
"""

from unittest.mock import patch
import pytest

from app.core.models.arc_wiki import ArcWiki
from app.services.arc_wiki import (
    save_arc_wiki,
    load_arc_wiki,
    list_arc_wikis,
    render_arc_wiki,
    build_arc_page,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE = ArcWiki(
    arc_id="arc_awakening",
    display_name="The Awakening Arc",
    theme="Discovering hidden power and accepting one's true destiny.",
    summary="Ariane's journey from powerless scholar to awakened mage.",
    start_event_id="event_001",
    escalation_event_ids=["event_002", "event_003"],
    turning_point_event_id="event_004",
    resolution_event_id="event_005",
    participating_characters=["ariane", "master_vael", "high_elder"],
    emotional_evolution=[
        {"chapter": 3, "note": "Ariane is confused by her sudden power."},
        {"chapter": 5, "note": "Ariane embraces her new identity."},
    ],
    thematic_evolution=[
        {"chapter": 3, "note": "Theme of hidden potential emerges."},
        {"chapter": 7, "note": "Sacrifice vs. ambition tension peaks."},
    ],
    chapter_start=3,
    chapter_end=7,
)


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------

class TestArcWikiModel:
    def test_minimal_construction(self):
        arc = ArcWiki(
            arc_id="arc_min",
            display_name="Min Arc",
            theme="Survival.",
            summary="They survived.",
            chapter_start=1,
            chapter_end=2,
        )
        assert arc.arc_id == "arc_min"
        assert arc.escalation_event_ids == []
        assert arc.participating_characters == []
        assert arc.emotional_evolution == []
        assert arc.thematic_evolution == []
        assert arc.start_event_id is None
        assert arc.turning_point_event_id is None
        assert arc.resolution_event_id is None

    def test_full_construction(self):
        assert SAMPLE.theme == "Discovering hidden power and accepting one's true destiny."
        assert len(SAMPLE.escalation_event_ids) == 2
        assert "ariane" in SAMPLE.participating_characters
        assert SAMPLE.chapter_start == 3
        assert SAMPLE.chapter_end == 7

    def test_serialization_round_trip(self):
        data = SAMPLE.model_dump()
        restored = ArcWiki(**data)
        assert restored.arc_id == SAMPLE.arc_id
        assert restored.emotional_evolution == SAMPLE.emotional_evolution
        assert restored.thematic_evolution == SAMPLE.thematic_evolution


# ---------------------------------------------------------------------------
# Persistence tests
# ---------------------------------------------------------------------------

class TestArcWikiPersistence:
    def test_save_and_load(self, tmp_path, monkeypatch):
        from app.core.story_manager import StoryManager
        monkeypatch.setattr(StoryManager, "DATA_DIR", str(tmp_path))

        save_arc_wiki("story-1", SAMPLE)
        loaded = load_arc_wiki("story-1", "arc_awakening")

        assert loaded is not None
        assert loaded.display_name == "The Awakening Arc"
        assert len(loaded.emotional_evolution) == 2

    def test_load_nonexistent_returns_none(self, tmp_path, monkeypatch):
        from app.core.story_manager import StoryManager
        monkeypatch.setattr(StoryManager, "DATA_DIR", str(tmp_path))

        assert load_arc_wiki("no-story", "no-arc") is None

    def test_save_overwrites_on_update(self, tmp_path, monkeypatch):
        from app.core.story_manager import StoryManager
        monkeypatch.setattr(StoryManager, "DATA_DIR", str(tmp_path))

        save_arc_wiki("story-1", SAMPLE)
        updated = SAMPLE.model_copy(update={"theme": "Revised theme."})
        save_arc_wiki("story-1", updated)

        loaded = load_arc_wiki("story-1", "arc_awakening")
        assert loaded.theme == "Revised theme."

    def test_list_arc_wikis(self, tmp_path, monkeypatch):
        from app.core.story_manager import StoryManager
        monkeypatch.setattr(StoryManager, "DATA_DIR", str(tmp_path))

        arc2 = SAMPLE.model_copy(update={"arc_id": "arc_betrayal", "display_name": "The Betrayal Arc"})
        save_arc_wiki("story-1", SAMPLE)
        save_arc_wiki("story-1", arc2)

        ids = list_arc_wikis("story-1")
        assert "arc_awakening" in ids
        assert "arc_betrayal" in ids
        assert len(ids) == 2

    def test_list_arc_wikis_empty_story(self, tmp_path, monkeypatch):
        from app.core.story_manager import StoryManager
        monkeypatch.setattr(StoryManager, "DATA_DIR", str(tmp_path))
        assert list_arc_wikis("nonexistent-story") == []


# ---------------------------------------------------------------------------
# Renderer tests — spec: theme, start event, escalation, turning point,
#   resolution, characters, emotional/thematic evolution
# ---------------------------------------------------------------------------

class TestRenderArcWiki:
    def test_contains_display_name(self):
        md = render_arc_wiki(SAMPLE)
        assert "The Awakening Arc" in md

    def test_contains_theme(self):
        md = render_arc_wiki(SAMPLE)
        assert "hidden power" in md

    def test_contains_summary(self):
        md = render_arc_wiki(SAMPLE)
        assert "powerless scholar" in md

    def test_contains_start_event(self):
        md = render_arc_wiki(SAMPLE)
        assert "event_001" in md

    def test_contains_escalation_events(self):
        md = render_arc_wiki(SAMPLE)
        assert "event_002" in md
        assert "event_003" in md

    def test_contains_turning_point(self):
        md = render_arc_wiki(SAMPLE)
        assert "event_004" in md

    def test_contains_resolution(self):
        md = render_arc_wiki(SAMPLE)
        assert "event_005" in md

    def test_contains_participating_characters(self):
        md = render_arc_wiki(SAMPLE)
        assert "ariane" in md
        assert "master_vael" in md

    def test_contains_emotional_evolution(self):
        md = render_arc_wiki(SAMPLE)
        assert "confused" in md or "embraces" in md

    def test_contains_thematic_evolution(self):
        md = render_arc_wiki(SAMPLE)
        assert "hidden potential" in md or "Sacrifice" in md

    def test_contains_chapter_range(self):
        md = render_arc_wiki(SAMPLE)
        assert "3" in md   # chapter_start
        assert "7" in md   # chapter_end

    def test_minimal_arc_does_not_crash(self):
        minimal = ArcWiki(
            arc_id="bare_arc",
            display_name="Bare Arc",
            theme="Survival.",
            summary="They survived.",
            chapter_start=1,
            chapter_end=1,
        )
        md = render_arc_wiki(minimal)
        assert "Bare Arc" in md
        assert md


# ---------------------------------------------------------------------------
# build_arc_page — LLM generator
# ---------------------------------------------------------------------------

class TestBuildArcPage:
    def _make_graph(self, tmp_path):
        from adapters.graph_adapter import GraphProvider
        import networkx as nx

        gp = GraphProvider.__new__(GraphProvider)
        gp.graph = nx.DiGraph()
        gp.story_uuid = "s1"
        gp.save_path = str(tmp_path / "graph.json")
        gp.add_character("ariane", {"last_seen_chapter": 7})
        gp.add_character("master_vael", {"last_seen_chapter": 7})
        gp.add_event("event_001", "Ariane awakens.", ["ariane"], chapter_id=3)
        gp.add_event("event_002", "Ariane trains.", ["ariane", "master_vael"], chapter_id=4)
        gp.add_arc(
            "arc_awakening", "The Awakening Arc",
            event_ids=["event_001", "event_002"],
            chapter_start=3, chapter_end=7,
        )
        return gp

    def test_returns_arc_wiki_on_success(self, tmp_path, monkeypatch):
        from app.core.story_manager import StoryManager
        monkeypatch.setattr(StoryManager, "DATA_DIR", str(tmp_path))
        gp = self._make_graph(tmp_path)

        llm_resp = {
            "theme": "Discovery and self-acceptance.",
            "summary": "Ariane rises from powerless to awakened mage.",
            "start_event_id": "event_001",
            "escalation_event_ids": ["event_002"],
            "turning_point_event_id": None,
            "resolution_event_id": None,
            "emotional_evolution": [{"chapter": 3, "note": "Confusion."}],
            "thematic_evolution": [{"chapter": 3, "note": "Hidden potential theme."}],
        }
        with patch("app.services.arc_wiki.analyze_text_json", return_value=llm_resp):
            result = build_arc_page("s1", "arc_awakening", gp)

        assert isinstance(result, ArcWiki)
        assert result.arc_id == "arc_awakening"
        assert "discovery" in result.theme.lower()
        assert result.chapter_start == 3
        assert result.chapter_end == 7

    def test_persists_wiki_after_generation(self, tmp_path, monkeypatch):
        from app.core.story_manager import StoryManager
        monkeypatch.setattr(StoryManager, "DATA_DIR", str(tmp_path))
        gp = self._make_graph(tmp_path)

        llm_resp = {
            "theme": "Discovery.",
            "summary": "Ariane rises.",
            "start_event_id": "event_001",
            "escalation_event_ids": [],
            "turning_point_event_id": None,
            "resolution_event_id": None,
            "emotional_evolution": [],
            "thematic_evolution": [],
        }
        with patch("app.services.arc_wiki.analyze_text_json", return_value=llm_resp):
            build_arc_page("s1", "arc_awakening", gp)

        assert load_arc_wiki("s1", "arc_awakening") is not None

    def test_participating_characters_derived_from_graph(self, tmp_path, monkeypatch):
        """Characters from graph arc events should be in the wiki output."""
        from app.core.story_manager import StoryManager
        monkeypatch.setattr(StoryManager, "DATA_DIR", str(tmp_path))
        gp = self._make_graph(tmp_path)

        llm_resp = {
            "theme": "Discovery.",
            "summary": "Ariane rises.",
            "start_event_id": "event_001",
            "escalation_event_ids": [],
            "turning_point_event_id": None,
            "resolution_event_id": None,
            "emotional_evolution": [],
            "thematic_evolution": [],
        }
        with patch("app.services.arc_wiki.analyze_text_json", return_value=llm_resp):
            result = build_arc_page("s1", "arc_awakening", gp)

        assert "ariane" in result.participating_characters

    def test_returns_none_when_arc_not_in_graph(self, tmp_path, monkeypatch):
        from app.core.story_manager import StoryManager
        monkeypatch.setattr(StoryManager, "DATA_DIR", str(tmp_path))
        from adapters.graph_adapter import GraphProvider
        import networkx as nx

        gp = GraphProvider.__new__(GraphProvider)
        gp.graph = nx.DiGraph()
        gp.story_uuid = "s1"
        gp.save_path = str(tmp_path / "graph.json")

        result = build_arc_page("s1", "nonexistent_arc", gp)
        assert result is None

    def test_returns_none_on_llm_failure(self, tmp_path, monkeypatch):
        from app.core.story_manager import StoryManager
        monkeypatch.setattr(StoryManager, "DATA_DIR", str(tmp_path))
        gp = self._make_graph(tmp_path)

        with patch("app.services.arc_wiki.analyze_text_json", return_value=None):
            result = build_arc_page("s1", "arc_awakening", gp)

        assert result is None

    def test_graph_event_context_sent_to_llm(self, tmp_path, monkeypatch):
        """Arc event descriptions must appear in the LLM prompt."""
        from app.core.story_manager import StoryManager
        monkeypatch.setattr(StoryManager, "DATA_DIR", str(tmp_path))
        gp = self._make_graph(tmp_path)

        llm_resp = {
            "theme": "Discovery.",
            "summary": "Ariane rises.",
            "start_event_id": "event_001",
            "escalation_event_ids": [],
            "turning_point_event_id": None,
            "resolution_event_id": None,
            "emotional_evolution": [],
            "thematic_evolution": [],
        }
        with patch("app.services.arc_wiki.analyze_text_json", return_value=llm_resp) as mock_llm:
            build_arc_page("s1", "arc_awakening", gp)

        prompt_arg = mock_llm.call_args[0][0]
        assert "Ariane awakens" in prompt_arg or "event_001" in prompt_arg
