import pytest
import os
import shutil
from adapters.graph_adapter import GraphProvider

# Use a temporary directory for testing
TEST_UUID = "test_causal_edges_story"
TEST_DIR = os.path.join("data", TEST_UUID)

@pytest.fixture(autouse=True)
def setup_teardown():
    # Setup: Create fresh testing environment
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)

    yield

    # Teardown: Clean up testing environment
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)

def test_add_causal_edge():
    # Arrange
    graph_provider = GraphProvider(TEST_UUID)
    graph_provider.add_character("hero", {"display_name": "Hero"})
    graph_provider.add_event("event_1", "Hero finds sword", ["hero"], chapter_id=1)
    graph_provider.add_event("event_2", "Hero kills dragon", ["hero"], chapter_id=2)

    # Act
    graph_provider.add_causal_edge("event_1", "event_2")

    # Assert
    assert graph_provider.graph.has_edge("event_1", "event_2")
    assert graph_provider.graph.edges["event_1", "event_2"]["relation"] == "causes"

def test_get_character_events():
    # Arrange
    graph_provider = GraphProvider(TEST_UUID)
    graph_provider.add_character("hero", {"display_name": "Hero"})
    graph_provider.add_character("villain", {"display_name": "Villain"})
    graph_provider.add_event("event_1", "Hero finds sword", ["hero"], chapter_id=1)
    graph_provider.add_event("event_2", "Hero meets Villain", ["hero", "villain"], chapter_id=2)
    graph_provider.add_event("event_3", "Villain escapes", ["villain"], chapter_id=3)

    # Act
    hero_events = graph_provider.get_character_events("hero")
    villain_events = graph_provider.get_character_events("villain")

    # Assert
    assert len(hero_events) == 2
    assert hero_events[0]["id"] == "event_1"
    assert hero_events[1]["id"] == "event_2"

    assert len(villain_events) == 2
    assert villain_events[0]["id"] == "event_2"
    assert villain_events[1]["id"] == "event_3"

def test_get_event_chain():
    # Arrange
    graph_provider = GraphProvider(TEST_UUID)
    graph_provider.add_character("hero", {"display_name": "Hero"})
    graph_provider.add_event("event_1", "Hero finds map", ["hero"], chapter_id=1)
    graph_provider.add_event("event_2", "Hero finds treasure", ["hero"], chapter_id=2)
    graph_provider.add_event("event_3", "Hero buys castle", ["hero"], chapter_id=3)

    graph_provider.add_causal_edge("event_1", "event_2")
    graph_provider.add_causal_edge("event_2", "event_3")

    # Act
    chain = graph_provider.get_event_chain("event_1")

    # Assert
    assert len(chain) == 3
    assert chain[0]["id"] == "event_1"
    assert chain[1]["id"] == "event_2"
    assert chain[2]["id"] == "event_3"

def test_get_event_chain_cycle_prevention():
    # Arrange
    graph_provider = GraphProvider(TEST_UUID)
    graph_provider.add_character("hero", {"display_name": "Hero"})
    graph_provider.add_event("event_1", "A", ["hero"], chapter_id=1)
    graph_provider.add_event("event_2", "B", ["hero"], chapter_id=2)

    graph_provider.add_causal_edge("event_1", "event_2")
    graph_provider.add_causal_edge("event_2", "event_1")  # Cycle!

    # Act
    chain = graph_provider.get_event_chain("event_1")

    # Assert
    # Should not infinite loop and should stop before repeating
    assert len(chain) == 2
    assert chain[0]["id"] == "event_1"
    assert chain[1]["id"] == "event_2"
