"""
tests/test_sliding_window.py
==============================
RED tests for Phase 2.1 Sliding-Window Chapter Ingestion.
"""

from unittest.mock import patch, MagicMock
from app.services.ingest import ingest_chapter

@patch("app.services.ingest.extract_chapter_intelligence_llm")
@patch("app.services.ingest.get_graph_engine")
def test_sliding_window_context_passed_to_extraction(mock_get_graph_engine, mock_extract):
    """
    When ingesting chapter N, the final paragraphs of chapter N-1 
    should be passed to the extraction layer as previous_context.
    """
    mock_gp = MagicMock()
    mock_gp.graph.nodes = lambda data: []
    mock_get_graph_engine.return_value = mock_gp

    mock_extract.return_value = {"events": []}

    chapter_1_text = "Intro.\n\nMid.\n\nFinal paragraph 1.\n\nFinal paragraph 2."
    chapter_2_text = "Next chapter starts here."

    import uuid
    story_uuid = f"test_story_{uuid.uuid4().hex}"

    # Ingest chapter 1
    ingest_chapter(story_uuid, "Title 1", chapter_1_text, extractor="llm")

    # Ingest chapter 2
    ingest_chapter(story_uuid, "Title 2", chapter_2_text, extractor="llm")

    assert mock_extract.call_count == 2

    # The second call is for chapter 2
    call_args, call_kwargs = mock_extract.call_args_list[1]

    assert "previous_context" in call_kwargs
    context = call_kwargs["previous_context"]
    assert context is not None
    assert "Final paragraph 1." in context
    assert "Final paragraph 2." in context
    assert "Intro." not in context
