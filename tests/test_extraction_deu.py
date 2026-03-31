import pytest
from unittest.mock import patch
from typing import Dict, Any
from app.services.extraction import extract_chapter_intelligence_llm

def test_extract_chapter_intelligence_llm_deu_format():
    # Arrange
    dummy_text = "Lucian explored the Ancient Ruins and found the artifact."
    
    mock_llm_response = {
        "active_character_names": ["Lucian"],
        "active_world_terms": ["Ancient Ruins", "Artifact"],
        "dialogue_count_total": 0,
        "events": [
            {
                "action_summary": "Lucian finds the artifact in the Ancient Ruins.",
                "involved_characters": ["Lucian"],
                "pre_conditions": "Lucian is exploring the ruins.",
                "post_conditions": "Lucian discovers the artifact.",
                "location": "Ancient Ruins"
            }
        ]
    }
    
    with patch('adapters.llm_adapter.analyze_text_json') as mock_analyze:
        mock_analyze.return_value = mock_llm_response
        
        # Act
        result = extract_chapter_intelligence_llm(dummy_text)
        
        # Assert
        assert "events" in result
        events = result["events"]
        assert len(events) == 1
        
        event = events[0]
        assert "pre_conditions" in event
        assert "post_conditions" in event
        assert "location" in event
        
        assert event["pre_conditions"] == "Lucian is exploring the ruins."
        assert event["post_conditions"] == "Lucian discovers the artifact."
        assert event["location"] == "Ancient Ruins"
