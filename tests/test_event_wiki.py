"""
tests/test_event_wiki.py
=========================
Phase 2.5 — Event Wiki Pages

Covers:
  - EventWiki Pydantic model
  - save_event_wiki / load_event_wiki persistence
  - list_event_wikis helper
  - render_event_wiki Markdown renderer (causal chain, participants with roles,
    pre/post conditions, narrative vs story-time context)
  - build_event_page LLM page generator
"""

from unittest.mock import patch

from app.core.models.event_wiki import EventWiki
from app.services.event_wiki import (
    save_event_wiki,
    load_event_wiki,
    list_event_wikis,
    render_event_wiki,
    build_event_page,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE = EventWiki(
    event_id="event_001",
    display_name="Ariane's Awakening",
    summary="Ariane discovers her latent mana core activates inside the Crystal Cave.",
    cause="Contact with the cave's resonant crystal energy.",
    consequences=["Ariane gains mana core", "Cave becomes unstable"],
    participants=[
        {"character_id": "ariane", "role": "protagonist"},
        {"character_id": "master_vael", "role": "witness"},
    ],
    location_id="crystal_cave",
    arc_id="arc_awakening",
    pre_conditions="Ariane had been mana-deaf since birth.",
    post_conditions="Ariane can now cast basic spells.",
    before_events=[],
    after_events=["event_002"],
    chapter_id=3,
    narrative_order=2,
    timeline_type="present",
    story_time_rank=2,
    spoiler_level=1,
    is_canonical=True,
    confidence=0.92,
)


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------

class TestEventWikiModel:
    def test_minimal_construction(self):
        ev = EventWiki(
            event_id="ev_min",
            display_name="Min Event",
            summary="Minimal event.",
            chapter_id=1,
        )
        assert ev.event_id == "ev_min"
        assert ev.participants == []
        assert ev.before_events == []
        assert ev.after_events == []
        assert ev.consequences == []
        assert ev.is_canonical is True
        assert ev.spoiler_level == 0
        assert ev.timeline_type == "present"

    def test_full_construction(self):
        assert SAMPLE.location_id == "crystal_cave"
        assert SAMPLE.arc_id == "arc_awakening"
        assert len(SAMPLE.participants) == 2
        assert SAMPLE.participants[0]["role"] == "protagonist"
        assert SAMPLE.confidence == 0.92

    def test_serialization_round_trip(self):
        data = SAMPLE.model_dump()
        restored = EventWiki(**data)
        assert restored.event_id == SAMPLE.event_id
        assert restored.consequences == SAMPLE.consequences
        assert restored.participants == SAMPLE.participants


# ---------------------------------------------------------------------------
# Persistence tests
# ---------------------------------------------------------------------------

class TestEventWikiPersistence:
    def test_save_and_load(self, tmp_path, monkeypatch):
        from app.core.story_manager import StoryManager
        monkeypatch.setattr(StoryManager, "DATA_DIR", str(tmp_path))

        save_event_wiki("story-1", SAMPLE)
        loaded = load_event_wiki("story-1", "event_001")

        assert loaded is not None
        assert loaded.display_name == "Ariane's Awakening"
        assert len(loaded.participants) == 2

    def test_load_nonexistent_returns_none(self, tmp_path, monkeypatch):
        from app.core.story_manager import StoryManager
        monkeypatch.setattr(StoryManager, "DATA_DIR", str(tmp_path))

        assert load_event_wiki("no-story", "no-event") is None

    def test_save_overwrites_on_update(self, tmp_path, monkeypatch):
        from app.core.story_manager import StoryManager
        monkeypatch.setattr(StoryManager, "DATA_DIR", str(tmp_path))

        save_event_wiki("story-1", SAMPLE)
        updated = SAMPLE.model_copy(update={"summary": "Revised summary."})
        save_event_wiki("story-1", updated)

        loaded = load_event_wiki("story-1", "event_001")
        assert loaded.summary == "Revised summary."

    def test_list_event_wikis(self, tmp_path, monkeypatch):
        from app.core.story_manager import StoryManager
        monkeypatch.setattr(StoryManager, "DATA_DIR", str(tmp_path))

        ev2 = SAMPLE.model_copy(update={"event_id": "event_002", "display_name": "Second Event"})
        save_event_wiki("story-1", SAMPLE)
        save_event_wiki("story-1", ev2)

        ids = list_event_wikis("story-1")
        assert "event_001" in ids
        assert "event_002" in ids
        assert len(ids) == 2

    def test_list_event_wikis_empty_story(self, tmp_path, monkeypatch):
        from app.core.story_manager import StoryManager
        monkeypatch.setattr(StoryManager, "DATA_DIR", str(tmp_path))
        assert list_event_wikis("nonexistent-story") == []


# ---------------------------------------------------------------------------
# Renderer tests — causal chain + participant roles per spec
# ---------------------------------------------------------------------------

class TestRenderEventWiki:
    def test_contains_display_name(self):
        md = render_event_wiki(SAMPLE)
        assert "Ariane's Awakening" in md

    def test_contains_summary(self):
        md = render_event_wiki(SAMPLE)
        assert "mana core" in md

    def test_contains_cause(self):
        md = render_event_wiki(SAMPLE)
        assert "resonant crystal energy" in md

    def test_contains_consequences(self):
        md = render_event_wiki(SAMPLE)
        assert "Cave becomes unstable" in md

    def test_contains_participant_roles(self):
        """Spec: render participant roles (protagonist, witness, cause, victim)."""
        md = render_event_wiki(SAMPLE)
        assert "protagonist" in md
        assert "witness" in md
        assert "ariane" in md.lower()

    def test_contains_pre_post_conditions(self):
        md = render_event_wiki(SAMPLE)
        assert "mana-deaf" in md
        assert "basic spells" in md

    def test_contains_narrative_vs_story_time(self):
        """Spec: narrative vs story-time context must appear."""
        md = render_event_wiki(SAMPLE)
        # chapter_id=3 (narrative) and story_time_rank=2 should both be surfaced
        assert "3" in md   # chapter reference
        assert "2" in md   # story_time_rank

    def test_contains_spoiler_level(self):
        md = render_event_wiki(SAMPLE)
        assert "spoiler" in md.lower() or "1" in md

    def test_contains_after_events(self):
        md = render_event_wiki(SAMPLE)
        assert "event_002" in md

    def test_contains_arc_reference(self):
        md = render_event_wiki(SAMPLE)
        assert "arc_awakening" in md

    def test_minimal_event_does_not_crash(self):
        minimal = EventWiki(
            event_id="bare_ev",
            display_name="Nothing Event",
            summary="Nothing happened.",
            chapter_id=1,
        )
        md = render_event_wiki(minimal)
        assert "Nothing Event" in md
        assert md


# ---------------------------------------------------------------------------
# build_event_page — LLM generator
# ---------------------------------------------------------------------------

class TestBuildEventPage:
    def _make_graph(self, tmp_path):
        from adapters.graph_adapter import GraphProvider
        import networkx as nx

        gp = GraphProvider.__new__(GraphProvider)
        gp.graph = nx.DiGraph()
        gp.story_uuid = "s1"
        gp.save_path = str(tmp_path / "graph.json")
        gp.add_character("ariane", {"last_seen_chapter": 3})
        gp.add_character("master_vael", {"last_seen_chapter": 3})
        gp.add_event(
            "event_001", "Ariane's mana core activates.", ["ariane", "master_vael"],
            chapter_id=3, location="crystal_cave",
            pre_conditions="mana-deaf", post_conditions="can cast spells",
            character_roles={"ariane": "protagonist", "master_vael": "witness"},
        )
        return gp

    def test_returns_event_wiki_on_success(self, tmp_path, monkeypatch):
        from app.core.story_manager import StoryManager
        monkeypatch.setattr(StoryManager, "DATA_DIR", str(tmp_path))
        gp = self._make_graph(tmp_path)

        llm_resp = {
            "display_name": "Ariane's Awakening",
            "summary": "Her mana core activated inside the cave.",
            "cause": "Crystal resonance triggered her dormant core.",
            "consequences": ["Mana core unlocked", "Cave destabilised"],
            "participants": [
                {"character_id": "ariane", "role": "protagonist"},
                {"character_id": "master_vael", "role": "witness"},
            ],
            "before_events": [],
            "after_events": ["event_002"],
        }
        with patch("app.services.event_wiki.analyze_text_json", return_value=llm_resp):
            result = build_event_page("s1", "event_001", gp)

        assert isinstance(result, EventWiki)
        assert result.event_id == "event_001"
        assert "mana" in result.summary.lower()
        assert result.chapter_id == 3
        assert result.location_id == "crystal_cave"

    def test_persists_wiki_after_generation(self, tmp_path, monkeypatch):
        from app.core.story_manager import StoryManager
        monkeypatch.setattr(StoryManager, "DATA_DIR", str(tmp_path))
        gp = self._make_graph(tmp_path)

        llm_resp = {
            "display_name": "Ariane's Awakening",
            "summary": "Core activated.",
            "cause": "Crystals.",
            "consequences": [],
            "participants": [],
            "before_events": [],
            "after_events": [],
        }
        with patch("app.services.event_wiki.analyze_text_json", return_value=llm_resp):
            build_event_page("s1", "event_001", gp)

        assert load_event_wiki("s1", "event_001") is not None

    def test_participant_roles_populated_from_graph(self, tmp_path, monkeypatch):
        """Roles stored on graph edges should seed the LLM prompt and appear in result."""
        from app.core.story_manager import StoryManager
        monkeypatch.setattr(StoryManager, "DATA_DIR", str(tmp_path))
        gp = self._make_graph(tmp_path)

        llm_resp = {
            "display_name": "Ariane's Awakening",
            "summary": "Core activated.",
            "cause": "Crystals.",
            "consequences": [],
            "participants": [
                {"character_id": "ariane", "role": "protagonist"},
                {"character_id": "master_vael", "role": "witness"},
            ],
            "before_events": [],
            "after_events": [],
        }
        with patch("app.services.event_wiki.analyze_text_json", return_value=llm_resp) as mock_llm:
            result = build_event_page("s1", "event_001", gp)

        # Roles should be present in the final wiki
        roles = {p["character_id"]: p["role"] for p in result.participants}
        assert roles.get("ariane") == "protagonist"
        assert roles.get("master_vael") == "witness"
        # The LLM must have been called with graph context that includes the roles
        prompt_arg = mock_llm.call_args[0][0]
        assert "protagonist" in prompt_arg or "ariane" in prompt_arg

    def test_causal_chain_included_in_prompt(self, tmp_path, monkeypatch):
        """Pre/post conditions from graph must appear in the LLM prompt."""
        from app.core.story_manager import StoryManager
        monkeypatch.setattr(StoryManager, "DATA_DIR", str(tmp_path))
        gp = self._make_graph(tmp_path)

        llm_resp = {
            "display_name": "Ariane's Awakening",
            "summary": "Core activated.",
            "cause": "Crystals.",
            "consequences": [],
            "participants": [],
            "before_events": [],
            "after_events": [],
        }
        with patch("app.services.event_wiki.analyze_text_json", return_value=llm_resp) as mock_llm:
            build_event_page("s1", "event_001", gp)

        prompt_arg = mock_llm.call_args[0][0]
        assert "mana-deaf" in prompt_arg or "can cast spells" in prompt_arg

    def test_returns_none_when_event_not_in_graph(self, tmp_path, monkeypatch):
        from app.core.story_manager import StoryManager
        monkeypatch.setattr(StoryManager, "DATA_DIR", str(tmp_path))
        from adapters.graph_adapter import GraphProvider
        import networkx as nx

        gp = GraphProvider.__new__(GraphProvider)
        gp.graph = nx.DiGraph()
        gp.story_uuid = "s1"
        gp.save_path = str(tmp_path / "graph.json")

        result = build_event_page("s1", "nonexistent_event", gp)
        assert result is None

    def test_returns_none_on_llm_failure(self, tmp_path, monkeypatch):
        from app.core.story_manager import StoryManager
        monkeypatch.setattr(StoryManager, "DATA_DIR", str(tmp_path))
        gp = self._make_graph(tmp_path)

        with patch("app.services.event_wiki.analyze_text_json", return_value=None):
            result = build_event_page("s1", "event_001", gp)

        assert result is None
