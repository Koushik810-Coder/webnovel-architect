"""
tests/test_location_wiki.py
============================
Phase 2.5 — Location Wiki Pages

Covers:
  - LocationWiki Pydantic model
  - save_location_wiki / load_location_wiki persistence
  - list_location_wikis helper
  - render_location_wiki Markdown renderer
  - build_location_page LLM page generator (aggregates events at a location)
"""

from unittest.mock import patch

from app.core.models.location_wiki import LocationWiki
from app.services.location_wiki import (
    save_location_wiki,
    load_location_wiki,
    list_location_wikis,
    render_location_wiki,
    build_location_page,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE = LocationWiki(
    location_id="crystal_cave",
    display_name="Crystal Cave",
    description="A vast underground cavern filled with luminous crystals.",
    region="Northern Mountains",
    significance="Sacred site where the Sword of Dawn was forged.",
    events_occurred=["event_001", "event_003"],
    characters_present=["ariane", "master_vael"],
    timeline=[
        {"chapter": 3, "note": "Ariane discovers the cave entrance."},
        {"chapter": 7, "note": "Master Vael seals the cave with dark magic."},
    ],
    first_appearance_chapter=3,
    last_updated_chapter=7,
)


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------

class TestLocationWikiModel:
    def test_minimal_construction(self):
        loc = LocationWiki(
            location_id="loc_01",
            display_name="Test Place",
            description="A test location.",
            first_appearance_chapter=1,
            last_updated_chapter=1,
        )
        assert loc.location_id == "loc_01"
        assert loc.events_occurred == []
        assert loc.characters_present == []
        assert loc.timeline == []
        assert loc.region is None
        assert loc.significance is None

    def test_full_construction(self):
        assert SAMPLE.region == "Northern Mountains"
        assert len(SAMPLE.events_occurred) == 2
        assert "ariane" in SAMPLE.characters_present

    def test_serialization_round_trip(self):
        data = SAMPLE.model_dump()
        restored = LocationWiki(**data)
        assert restored.location_id == SAMPLE.location_id
        assert restored.timeline == SAMPLE.timeline


# ---------------------------------------------------------------------------
# Persistence tests
# ---------------------------------------------------------------------------

class TestLocationWikiPersistence:
    def test_save_and_load(self, tmp_path, monkeypatch):
        from app.core.story_manager import StoryManager
        monkeypatch.setattr(StoryManager, "DATA_DIR", str(tmp_path))

        save_location_wiki("story-1", SAMPLE)
        loaded = load_location_wiki("story-1", "crystal_cave")

        assert loaded is not None
        assert loaded.display_name == "Crystal Cave"
        assert len(loaded.timeline) == 2

    def test_load_nonexistent_returns_none(self, tmp_path, monkeypatch):
        from app.core.story_manager import StoryManager
        monkeypatch.setattr(StoryManager, "DATA_DIR", str(tmp_path))

        assert load_location_wiki("no-story", "no-loc") is None

    def test_save_overwrites_on_update(self, tmp_path, monkeypatch):
        from app.core.story_manager import StoryManager
        monkeypatch.setattr(StoryManager, "DATA_DIR", str(tmp_path))

        save_location_wiki("story-1", SAMPLE)
        updated = SAMPLE.model_copy(update={"description": "Updated desc."})
        save_location_wiki("story-1", updated)

        loaded = load_location_wiki("story-1", "crystal_cave")
        assert loaded.description == "Updated desc."

    def test_list_location_wikis(self, tmp_path, monkeypatch):
        from app.core.story_manager import StoryManager
        monkeypatch.setattr(StoryManager, "DATA_DIR", str(tmp_path))

        loc2 = SAMPLE.model_copy(update={"location_id": "dark_forest", "display_name": "Dark Forest"})
        save_location_wiki("story-1", SAMPLE)
        save_location_wiki("story-1", loc2)

        ids = list_location_wikis("story-1")
        assert "crystal_cave" in ids
        assert "dark_forest" in ids
        assert len(ids) == 2

    def test_list_location_wikis_empty_story(self, tmp_path, monkeypatch):
        from app.core.story_manager import StoryManager
        monkeypatch.setattr(StoryManager, "DATA_DIR", str(tmp_path))
        assert list_location_wikis("nonexistent-story") == []


# ---------------------------------------------------------------------------
# Renderer tests
# ---------------------------------------------------------------------------

class TestRenderLocationWiki:
    def test_contains_display_name(self):
        md = render_location_wiki(SAMPLE)
        assert "Crystal Cave" in md

    def test_contains_description(self):
        md = render_location_wiki(SAMPLE)
        assert "luminous crystals" in md

    def test_contains_region(self):
        md = render_location_wiki(SAMPLE)
        assert "Northern Mountains" in md

    def test_contains_significance(self):
        md = render_location_wiki(SAMPLE)
        assert "Sword of Dawn" in md

    def test_contains_timeline_entries(self):
        md = render_location_wiki(SAMPLE)
        assert "Ch. 3" in md or "Chapter 3" in md
        assert "Ariane discovers" in md

    def test_contains_characters(self):
        md = render_location_wiki(SAMPLE)
        assert "ariane" in md or "Ariane" in md

    def test_minimal_location_does_not_crash(self):
        minimal = LocationWiki(
            location_id="bare_loc",
            display_name="Bare Place",
            description="Nothing here.",
            first_appearance_chapter=1,
            last_updated_chapter=1,
        )
        md = render_location_wiki(minimal)
        assert "Bare Place" in md
        assert md  # non-empty


# ---------------------------------------------------------------------------
# build_location_page — LLM generator
# ---------------------------------------------------------------------------

class TestBuildLocationPage:
    def _make_graph(self, tmp_path):
        from adapters.graph_adapter import GraphProvider
        import networkx as nx

        gp = GraphProvider.__new__(GraphProvider)
        gp.graph = nx.DiGraph()
        gp.story_uuid = "s1"
        gp.save_path = str(tmp_path / "graph.json")
        gp.add_character("ariane", {"last_seen_chapter": 3})
        gp.add_event(
            "event_001", "Ariane awakens.", ["ariane"],
            chapter_id=3, location="crystal_cave",
        )
        return gp

    def test_returns_location_wiki_on_success(self, tmp_path, monkeypatch):
        from app.core.story_manager import StoryManager
        monkeypatch.setattr(StoryManager, "DATA_DIR", str(tmp_path))
        gp = self._make_graph(tmp_path)

        llm_resp = {
            "description": "A cave full of glowing crystals.",
            "region": "North",
            "significance": "Sacred forge site.",
            "timeline": [{"chapter": 3, "note": "Ariane visits."}],
        }
        with patch("app.services.location_wiki.analyze_text_json", return_value=llm_resp):
            result = build_location_page("s1", "crystal_cave", gp)

        assert isinstance(result, LocationWiki)
        assert result.location_id == "crystal_cave"
        assert "crystal" in result.description.lower()
        assert "ariane" in result.characters_present
        assert "event_001" in result.events_occurred

    def test_persists_wiki_after_generation(self, tmp_path, monkeypatch):
        from app.core.story_manager import StoryManager
        monkeypatch.setattr(StoryManager, "DATA_DIR", str(tmp_path))
        gp = self._make_graph(tmp_path)

        llm_resp = {
            "description": "Glowing cave.", "region": "North",
            "significance": "Sacred.", "timeline": [],
        }
        with patch("app.services.location_wiki.analyze_text_json", return_value=llm_resp):
            build_location_page("s1", "crystal_cave", gp)

        assert load_location_wiki("s1", "crystal_cave") is not None

    def test_returns_none_when_location_has_no_events(self, tmp_path, monkeypatch):
        from app.core.story_manager import StoryManager
        monkeypatch.setattr(StoryManager, "DATA_DIR", str(tmp_path))
        from adapters.graph_adapter import GraphProvider
        import networkx as nx

        gp = GraphProvider.__new__(GraphProvider)
        gp.graph = nx.DiGraph()
        gp.story_uuid = "s1"
        gp.save_path = str(tmp_path / "graph.json")

        result = build_location_page("s1", "void_realm", gp)
        assert result is None

    def test_returns_none_on_llm_failure(self, tmp_path, monkeypatch):
        from app.core.story_manager import StoryManager
        monkeypatch.setattr(StoryManager, "DATA_DIR", str(tmp_path))
        gp = self._make_graph(tmp_path)

        with patch("app.services.location_wiki.analyze_text_json", return_value=None):
            result = build_location_page("s1", "crystal_cave", gp)

        assert result is None

    def test_chapter_range_in_generated_wiki(self, tmp_path, monkeypatch):
        """first/last chapter should be derived from actual graph events."""
        from app.core.story_manager import StoryManager
        monkeypatch.setattr(StoryManager, "DATA_DIR", str(tmp_path))
        gp = self._make_graph(tmp_path)
        gp.add_character("vael", {"last_seen_chapter": 7})
        gp.add_event(
            "event_007", "Vael seals the cave.", ["vael"],
            chapter_id=7, location="crystal_cave",
        )

        llm_resp = {
            "description": "Cave.", "region": "North",
            "significance": "Sacred.", "timeline": [],
        }
        with patch("app.services.location_wiki.analyze_text_json", return_value=llm_resp):
            result = build_location_page("s1", "crystal_cave", gp)

        assert result.first_appearance_chapter == 3
        assert result.last_updated_chapter == 7
