import os
import pytest

from adapters.graph_adapter import GraphProvider
from app.services.arc_detector import detect_arcs

@pytest.fixture()
def gp(tmp_path, monkeypatch):
    import app.core.story_manager as sm
    monkeypatch.setattr(sm.StoryManager, "DATA_DIR", str(tmp_path))
    os.makedirs(os.path.join(str(tmp_path), "phase2_story"), exist_ok=True)
    return GraphProvider("phase2_story")

class TestArcDetector:
    def test_graph_add_arc_method_exists(self, gp):
        """graph.add_arc(...) method must exist on GraphProvider"""
        gp.add_arc(
            arc_id="arc_1",
            label="The Siege of Westhold",
            event_ids=["ev1", "ev2"],
            chapter_start=1,
            chapter_end=5
        )
        assert gp.graph.nodes["arc_1"]["type"] == "arc"
        assert gp.graph.nodes["arc_1"]["label"] == "The Siege of Westhold"
        assert gp.graph.nodes["arc_1"]["chapter_start"] == 1
        assert gp.graph.nodes["arc_1"]["chapter_end"] == 5
        assert gp.graph.nodes["arc_1"]["event_ids"] == ["ev1", "ev2"]
        
        # Test edges are created to the events
        # We need the events to exist to create edges correctly, though add_arc might create the edge if nodes exist
        gp.add_event("ev1", "event 1", ["hero"], chapter_id=1)
        gp.add_event("ev2", "event 2", ["hero"], chapter_id=2)
        
        # Call again to see if edges are added now that nodes exist
        gp.add_arc("arc_1", "The Siege of Westhold", ["ev1", "ev2"], 1, 5)
        assert gp.graph.has_edge("arc_1", "ev1")
        assert gp.graph["arc_1"]["ev1"]["relation"] == "contains"

    def test_detect_arcs_returns_list_of_arc_dicts(self, tmp_path, monkeypatch):
        """detect_arcs(story_uuid, every_n=5) returns a list of arc dicts"""
        # Mocking the LLM adapter inside detect_arcs so it doesn't make real calls
        import app.services.arc_detector as arc_detector
        monkeypatch.setattr(
            arc_detector, 
            "_call_llm_for_arcs", 
            lambda events_chunk: [
                {"label": "The Discovery", "event_ids": [e["id"] for e in events_chunk]}
            ]
        )
        
        gp = GraphProvider("phase2_story")
        gp.add_event("ev1", "Hero finds sword", ["hero"], chapter_id=1, location="Cave")
        gp.add_event("ev2", "Hero fights goblin", ["hero"], chapter_id=2, location="Cave")
        gp.save_graph()
        
        arcs = detect_arcs("phase2_story", every_n=5)
        assert isinstance(arcs, list)
        assert len(arcs) == 1
        assert "label" in arcs[0]
        assert "event_ids" in arcs[0]
        assert "ev1" in arcs[0]["event_ids"]

    def test_arc_detector_triggered_during_ingest_every_5_chapters(self, tmp_path, monkeypatch):
        """Trigger fires every 5 chapters during ingest"""
        import app.services.ingest as ingest
        
        call_count = {"n": 0}
        def fake_detect_arcs(story_uuid, every_n):
            call_count["n"] += 1
            return []
            
        monkeypatch.setattr(ingest, "detect_arcs", fake_detect_arcs, raising=False)
        monkeypatch.setattr(ingest, "extract_chapter_intelligence_llm", lambda text, **kwargs: {"active_character_names": ["Hero"], "events": []})
        monkeypatch.setattr(ingest, "update_character_profile", lambda *args: {})
        monkeypatch.setattr(ingest, "batch_update_character_profiles", lambda *args: {})
        
        story_uuid = "phase2_story"
        import app.core.story_manager as sm
        monkeypatch.setattr(sm.StoryManager, "DATA_DIR", str(tmp_path))
        
        for i in range(1, 6):
            ingest.ingest_chapter(story_uuid, f"Chapter {i}", f"Text {i}", extractor="llm")
            
        # Should be called once on chapter 5
        assert call_count["n"] == 1
        
        # Not called on chapter 6
        ingest.ingest_chapter(story_uuid, "Chapter 6", "Text 6", extractor="llm")
        assert call_count["n"] == 1
