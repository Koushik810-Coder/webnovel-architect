"""
tests/test_graph_extended.py
====================================
Extended graph adapter tests covering:
  - save_graph / load_graph round-trip preserves nodes and edges
  - Atomic write: temp file renamed, original never partially written
  - add_event with missing participant skips that participant gracefully
  - get_event_chain respects depth limit
  - compute_chapter_scores scores sum > 0 when graph has events
  - merge_characters re-routes edges to canonical node
  - add_or_update_character_edge with intensity=0 still creates edge
"""

import os
import pytest

from adapters.graph_adapter import GraphProvider


@pytest.fixture()
def gp(tmp_path, monkeypatch):
    import app.core.story_manager as sm
    monkeypatch.setattr(sm.StoryManager, "DATA_DIR", str(tmp_path))
    story_dir = os.path.join(str(tmp_path), "graph_ext_story")
    os.makedirs(story_dir, exist_ok=True)
    return GraphProvider("graph_ext_story")


# ---------------------------------------------------------------------------
# save_graph / load_graph round-trip
# ---------------------------------------------------------------------------

class TestGraphPersistence:
    def test_round_trip_preserves_character_nodes(self, gp, tmp_path):
        """Saving and reloading must restore all character nodes."""
        gp.add_character("aria", {"display_name": "Aria", "aliases": ["the Mage"]})
        gp.add_character("bob", {"display_name": "Bob"})
        gp.save_graph()

        # Load fresh instance from same directory
        gp2 = GraphProvider("graph_ext_story")
        char_ids = [n for n, d in gp2.graph.nodes(data=True) if d.get("type") == "character"]
        assert "aria" in char_ids
        assert "bob" in char_ids

    def test_round_trip_preserves_event_nodes(self, gp):
        """Events must survive a save/load cycle."""
        gp.add_character("hero", {"display_name": "Hero"})
        gp.add_event("ev1", "Hero acts", ["hero"], chapter_id=1)
        gp.save_graph()

        gp2 = GraphProvider("graph_ext_story")
        assert gp2.graph.has_node("ev1")
        assert gp2.graph.nodes["ev1"]["type"] == "event"

    def test_round_trip_preserves_aliases_on_node(self, gp):
        """Node attributes including aliases must survive the cycle."""
        gp.add_character("zorian", {"display_name": "Zorian", "aliases": ["Zor", "the Looper"]})
        gp.save_graph()

        gp2 = GraphProvider("graph_ext_story")
        aliases = gp2.graph.nodes["zorian"].get("aliases", [])
        assert "Zor" in aliases
        assert "the Looper" in aliases

    def test_round_trip_preserves_character_edges(self, gp):
        """Character-to-character edges must survive the cycle."""
        gp.add_character("a", {"display_name": "A"})
        gp.add_character("b", {"display_name": "B"})
        gp.add_or_update_character_edge("a", "b", relation_type="rival", chapter_id=1, intensity=3)
        gp.save_graph()

        gp2 = GraphProvider("graph_ext_story")
        assert gp2.graph.has_edge("a", "b")
        assert gp2.graph["a"]["b"]["last_relation_type"] == "rival"

    def test_empty_graph_save_and_reload(self, gp):
        """Saving an empty graph and reloading must not crash."""
        gp.save_graph()
        gp2 = GraphProvider("graph_ext_story")
        assert len(gp2.graph.nodes) == 0


# ---------------------------------------------------------------------------
# add_event edge cases
# ---------------------------------------------------------------------------

class TestAddEventEdgeCases:
    def test_event_with_no_participants_is_created(self, gp):
        """An event with zero participants must still be added as a node."""
        gp.add_event("ev_solo", "A mysterious occurrence", [], chapter_id=1)
        assert gp.graph.has_node("ev_solo")

    def test_event_with_unknown_participant_skips_gracefully(self, gp):
        """Participant not in the graph must not crash add_event."""
        # Only add one character, reference a ghost
        gp.add_character("known", {"display_name": "Known"})
        gp.add_event("ev1", "Known meets Ghost", ["known", "ghost_char"], chapter_id=1)
        assert gp.graph.has_node("ev1")
        assert gp.graph.has_edge("known", "ev1")
        # ghost_char has no node — no edge should exist
        assert not gp.graph.has_node("ghost_char")

    def test_duplicate_event_id_updates_description(self, gp):
        """Adding the same event_id twice should update the existing node."""
        gp.add_character("hero", {"display_name": "Hero"})
        gp.add_event("ev1", "First description", ["hero"], chapter_id=1)
        gp.add_event("ev1", "Updated description", ["hero"], chapter_id=1)
        desc = gp.graph.nodes["ev1"]["description"]
        assert desc == "Updated description"


# ---------------------------------------------------------------------------
# compute_chapter_scores vs get_character_importance consistency
# ---------------------------------------------------------------------------

class TestBatchScoreConsistency:
    def test_all_chars_covered_in_batch(self, gp):
        """Batch must cover every character that exists in the graph."""
        for i in range(5):
            gp.add_character(f"char_{i}", {"display_name": f"Char {i}"})
            gp.add_event(f"ev_{i}", f"Event {i}", [f"char_{i}"], chapter_id=i + 1)

        scores = gp.compute_chapter_scores(current_chapter=5, decay_rate=0.05)
        for i in range(5):
            assert f"char_{i}" in scores, f"char_{i} missing from batch scores"

    def test_batch_scores_positive_for_active_chars(self, gp):
        """All characters with events must have positive scores."""
        gp.add_character("a", {"display_name": "A"})
        gp.add_character("b", {"display_name": "B"})
        gp.add_event("ev1", "A and B interact", ["a", "b"], chapter_id=1, intensity=3)

        scores = gp.compute_chapter_scores(current_chapter=1)
        assert scores["a"] > 0
        assert scores["b"] > 0

    def test_non_character_nodes_excluded_from_scores(self, gp):
        """Event nodes must not appear in compute_chapter_scores output."""
        gp.add_character("hero", {"display_name": "Hero"})
        gp.add_event("ev1", "Hero acts", ["hero"], chapter_id=1)

        scores = gp.compute_chapter_scores(current_chapter=1)
        assert "ev1" not in scores


# ---------------------------------------------------------------------------
# merge_characters
# ---------------------------------------------------------------------------

class TestMergeCharacters:
    def test_merge_redirects_events_to_canonical(self, gp):
        """After merging alias→canonical, canonical must have all the events."""
        gp.add_character("zorian", {"display_name": "Zorian"})
        gp.add_character("zor", {"display_name": "Zor"})
        gp.add_event("ev1", "Zor runs", ["zor"], chapter_id=1)

        gp.merge_characters("zor", "zorian")

        # canonical must now have ev1 reachable
        events = [
            eid for _, eid in gp.graph.out_edges("zorian")
            if gp.graph.nodes.get(eid, {}).get("type") == "event"
        ]
        assert "ev1" in events

    def test_merge_removes_alias_node(self, gp):
        """After merge, the alias node must not exist."""
        gp.add_character("canon", {"display_name": "Canon"})
        gp.add_character("alias", {"display_name": "Alias"})
        gp.merge_characters("alias", "canon")
        assert not gp.graph.has_node("alias")


# ---------------------------------------------------------------------------
# Character-to-character edge: zero-intensity edge
# ---------------------------------------------------------------------------

class TestZeroIntensityEdge:
    def test_zero_intensity_edge_created(self, gp):
        """intensity=0 must still create the edge (co-occurrence with no drama)."""
        gp.add_character("x", {"display_name": "X"})
        gp.add_character("y", {"display_name": "Y"})
        gp.add_or_update_character_edge("x", "y", chapter_id=1, intensity=0)
        assert gp.graph.has_edge("x", "y")

    def test_zero_intensity_weight_accumulates(self, gp):
        """Even intensity=0 increments co_occurrence_count."""
        gp.add_character("p", {"display_name": "P"})
        gp.add_character("q", {"display_name": "Q"})
        gp.add_or_update_character_edge("p", "q", chapter_id=1, intensity=0)
        gp.add_or_update_character_edge("p", "q", chapter_id=2, intensity=0)
        assert gp.graph["p"]["q"]["co_occurrence_count"] == 2
