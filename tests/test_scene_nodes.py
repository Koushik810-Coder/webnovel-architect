import os
import pytest
from adapters.graph_adapter import GraphProvider

@pytest.fixture()
def gp(tmp_path, monkeypatch):
    import app.core.story_manager as sm
    monkeypatch.setattr(sm.StoryManager, "DATA_DIR", str(tmp_path))
    os.makedirs(os.path.join(str(tmp_path), "phase2_story"), exist_ok=True)
    return GraphProvider("phase2_story")

class TestSceneNodes:
    def test_add_scene_stores_scene_node(self, gp):
        """GraphProvider.add_scene stores a type='scene' node"""
        gp.add_scene(scene_id="s1", chapter_id=1, location="The Inn", summary="Characters meet at the inn.")
        assert gp.graph.nodes["s1"]["type"] == "scene"
        assert gp.graph.nodes["s1"]["chapter_id"] == 1
        assert gp.graph.nodes["s1"]["location"] == "The Inn"
        assert gp.graph.nodes["s1"]["summary"] == "Characters meet at the inn."

    def test_add_event_to_scene_adds_edge(self, gp):
        """GraphProvider.add_event_to_scene adds OCCURS_IN edge"""
        gp.add_scene(scene_id="s1", chapter_id=1, location="The Inn", summary="Meeting")
        gp.add_event("ev1", "Hero arrives", ["hero"], chapter_id=1)
        gp.add_event_to_scene("ev1", "s1")

        assert gp.graph.has_edge("ev1", "s1")
        assert gp.graph["ev1"]["s1"]["relation"] == "OCCURS_IN"

    def test_extraction_schema_includes_scene_id(self, monkeypatch):
        """Extraction prompt returns a scene_id grouping field"""
        import app.services.extraction as ext
        import adapters.llm_adapter as llm

        call_args = {}
        def mock_analyze(prompt, *args, **kwargs):
            call_args["prompt"] = prompt
            return {
                "active_character_names": ["Hero"],
                "events": [{"id": "ev1", "scene_id": "s1", "action_summary": "Hero arrives"}]
            }

        monkeypatch.setattr(llm, "analyze_text_json", mock_analyze)

        res = ext.extract_chapter_intelligence_llm("The hero arrived at the inn.")

        # Check if the prompt instructs about scene_id
        assert "scene_id" in call_args["prompt"]

        # Check if result structure includes scene_id
        assert res["events"][0]["scene_id"] == "s1"

    def test_ingest_writes_scene_nodes_before_events(self, tmp_path, monkeypatch):
        """Update ingest.py to write scene nodes before events"""
        import app.services.ingest as ingest

        story_uuid = "phase2_story"
        import app.core.story_manager as sm
        monkeypatch.setattr(sm.StoryManager, "DATA_DIR", str(tmp_path))

        def mock_extract(text, previous_context=None):
            return {
                "active_character_names": ["Hero"],
                "events": [
                    {"id": "ev1", "scene_id": "s1", "action_summary": "Hero arrives", "location": "The Inn", "involved_characters": ["Hero"]}
                ]
            }
        monkeypatch.setattr(ingest, "extract_chapter_intelligence_llm", mock_extract)
        monkeypatch.setattr(ingest, "update_character_profile", lambda *args: {})
        monkeypatch.setattr(ingest, "batch_update_character_profiles", lambda *args: {})

        # Run ingest
        ingest.ingest_chapter(story_uuid, "Chapter 1", "Hero arrived at the inn.", extractor="llm")

        # Check if graph has the scene node and the event and edge
        gp = GraphProvider(story_uuid)
        scene_id = "chapter_1_scene_s1"
        event_id = "chapter_1_event_0"

        assert gp.graph.has_node(scene_id)
        assert gp.graph.nodes[scene_id]["type"] == "scene"
        assert gp.graph.has_edge(event_id, scene_id)
        assert gp.graph[event_id][scene_id]["relation"] == "OCCURS_IN"

    def test_rag_retrieves_by_scene_when_query_location_specific(self, monkeypatch):
        """RAG retrieves by scene when query is location-specific"""
        import app.services.rag as rag

        # Mock LLM calls
        calls = {"intent": 0, "query": 0}

        def mock_analyze_json(prompt, *args, **kwargs):
            if "Extract the core entities" in prompt:
                calls["intent"] += 1
                return {"characters": [], "locations": ["The Inn"], "concepts": []}
            return {}

        def mock_analyze(prompt, *args, **kwargs):
            if "Based on ALL of the above events" in prompt or "Use the provided chronological timeline" in prompt:
                calls["query"] += 1
                return "The characters met at the inn."
            return ""

        monkeypatch.setattr(rag, "analyze_text_json", mock_analyze_json)
        monkeypatch.setattr(rag, "analyze_text", mock_analyze)

        # Setup graph with scenes
        gp = GraphProvider("rag_story")
        gp.add_scene("s1", 1, "The Inn", "A detailed meeting at the inn.")
        gp.add_event("e1", "Hero talks", ["hero"], chapter_id=1)
        gp.add_event_to_scene("e1", "s1")
        gp.save_graph()

        res = rag.query_story("rag_story", "What happened at The Inn?")
        assert res == "The characters met at the inn."
        assert calls["intent"] == 1
        assert calls["query"] == 1
