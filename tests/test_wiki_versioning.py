"""
tests/test_wiki_versioning.py
==============================
Phase 2.6a — Wiki Page Versioning

Covers:
  - Meta fields (version, generated_at, graph_snapshot_id) on all Wiki models.
  - Deterministic hashing of a node's graph neighbourhood (graph_hasher.py).
  - Cache invalidation logic (skipping LLM call if graph hash hasn't changed).
"""

from unittest.mock import patch
import networkx as nx

from adapters.graph_adapter import GraphProvider
from app.core.models.character_wiki import CharacterWiki
from app.core.models.location_wiki import LocationWiki
from app.services.wiki_versioning import compute_node_hash

# ---------------------------------------------------------------------------
# Fixtures & Utilities
# ---------------------------------------------------------------------------

def make_test_graph():
    gp = GraphProvider.__new__(GraphProvider)
    gp.graph = nx.DiGraph()
    gp.story_uuid = "s1"
    gp.graph.add_node("char_alice", type="character", description="A brave knight.")
    gp.graph.add_node("char_bob", type="character", description="A rogue.")
    gp.graph.add_edge("char_alice", "char_bob", relation="trusts")
    return gp

# ---------------------------------------------------------------------------
# Model updates
# ---------------------------------------------------------------------------

def test_wiki_models_have_version_fields():
    cw = CharacterWiki(
        character_id="char_alice",
        display_name="Alice",
        short_description="A short desc.",
        first_appearance_chapter=1,
        last_updated_chapter=1
    )
    assert cw.version == 1
    assert cw.generated_at is None
    assert cw.graph_snapshot_id is None

    lw = LocationWiki(
        location_id="loc1",
        display_name="Loc1",
        description="A location.",
        first_appearance_chapter=1,
        last_updated_chapter=1
    )
    assert lw.version == 1
    assert lw.graph_snapshot_id is None

# ---------------------------------------------------------------------------
# Hashing logic
# ---------------------------------------------------------------------------

def test_compute_node_hash_determinism():
    gp1 = make_test_graph()
    hash1 = compute_node_hash(gp1.graph, "char_alice")

    gp2 = make_test_graph()
    hash2 = compute_node_hash(gp2.graph, "char_alice")

    assert hash1 == hash2

def test_compute_node_hash_changes_on_node_attr_update():
    gp = make_test_graph()
    hash1 = compute_node_hash(gp.graph, "char_alice")

    gp.graph.nodes["char_alice"]["description"] = "A very brave knight."
    hash2 = compute_node_hash(gp.graph, "char_alice")

    assert hash1 != hash2

def test_compute_node_hash_changes_on_edge_add():
    gp = make_test_graph()
    hash1 = compute_node_hash(gp.graph, "char_alice")

    gp.graph.add_node("event_1", type="event")
    gp.graph.add_edge("char_alice", "event_1", relation="involved_in")
    hash2 = compute_node_hash(gp.graph, "char_alice")

    assert hash1 != hash2

# ---------------------------------------------------------------------------
# Cache Invalidation logic
# ---------------------------------------------------------------------------

@patch("app.services.wiki.analyze_text_json")
def test_character_wiki_skips_llm_if_hash_unchanged(mock_analyze, tmp_path, monkeypatch):
    """
    If the graph snapshot ID matches, the generation function should return the existing wiki
    without invoking the LLM.
    """
    from app.core.story_manager import StoryManager
    from app.services.wiki import enrich_wiki_from_rag, save_character_wiki

    monkeypatch.setattr(StoryManager, "DATA_DIR", str(tmp_path))

    gp = make_test_graph()
    gp.save_path = str(tmp_path / "graph.json")

    current_hash = compute_node_hash(gp.graph, "char_alice")

    # Pre-save a wiki with matching hash
    existing_wiki = CharacterWiki(
        character_id="char_alice",
        display_name="Alice",
        short_description="A short desc.",
        long_description="Old summary.",
        first_appearance_chapter=1,
        last_updated_chapter=1,
        version=2,
        graph_snapshot_id=current_hash
    )
    save_character_wiki("s1", existing_wiki)

    # We patch get_graph_engine so it returns our test graph
    with patch("adapters.graph_adapter.get_graph_engine", return_value=gp):
        result = enrich_wiki_from_rag("s1", "char_alice")

    assert mock_analyze.call_count == 0
    assert result.version == 2
    assert result.long_description == "Old summary."

@patch("app.services.wiki.analyze_text_json")
def test_character_wiki_calls_llm_if_hash_changed(mock_analyze, tmp_path, monkeypatch):
    from app.core.story_manager import StoryManager
    from app.services.wiki import enrich_wiki_from_rag, save_character_wiki

    monkeypatch.setattr(StoryManager, "DATA_DIR", str(tmp_path))

    gp = make_test_graph()
    gp.save_path = str(tmp_path / "graph.json")

    # Pre-save a wiki with a DIFFERENT hash
    existing_wiki = CharacterWiki(
        character_id="char_alice",
        display_name="Alice",
        short_description="A short desc.",
        long_description="Old summary.",
        first_appearance_chapter=1,
        last_updated_chapter=1,
        version=2,
        graph_snapshot_id="old_hash_123"
    )
    save_character_wiki("s1", existing_wiki)

    mock_analyze.return_value = {
        "display_name": "Alice",
        "synopsis": "New summary.",
        "short_description": "A short desc.",
        "appearance": "",
        "personality_traits": [],
        "affiliations": [],
        "status": ""
    }

    with patch("adapters.graph_adapter.get_graph_engine", return_value=gp), \
         patch("app.services.rag.query_character_profile") as mock_rag:

        mock_rag.return_value = {
            "display_name": "Alice",
            "synopsis": "New summary.",
            "short_description": "A short desc.",
            "appearance": "",
            "personality_traits": [],
            "affiliations": [],
            "status": ""
        }

        result = enrich_wiki_from_rag("s1", "char_alice")

    assert result.version == 3  # Incremented
    assert result.long_description == "New summary."
    assert result.graph_snapshot_id == compute_node_hash(gp.graph, "char_alice")
    assert result.generated_at is not None
