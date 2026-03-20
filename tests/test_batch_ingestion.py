import pytest
from unittest.mock import patch, MagicMock
from app.services.ingest import ingest_multiple_chapters

@patch('app.services.ingest.ingest_chapter')
@patch('app.services.scrapers.royalroad_scraper.RoyalRoadScraper.scrape_chapter')
def test_ingest_multiple_chapters_with_urls(mock_scrape, mock_ingest):
    # Mock data
    chapters_input = [
        {"title": "Chapter 1", "url": "http://rr.com/1"},
        {"title": "Chapter 2", "url": "http://rr.com/2"}
    ]
    
    mock_scrape.side_effect = [
        {"title": "Chapter 1", "text": "Content 1"},
        {"title": "Chapter 2", "text": "Content 2"}
    ]
    
    mock_chapter_obj = MagicMock()
    mock_ingest.return_value = mock_chapter_obj
    
    # Progress callback
    progress_calls = []
    def callback(curr, total):
        progress_calls.append((curr, total))
        
    results = ingest_multiple_chapters(
        "test_story", 
        chapters_input, 
        extractor="spacy", 
        progress_callback=callback
    )
    
    assert len(results) == 2
    assert mock_scrape.call_count == 2
    assert mock_ingest.call_count == 2
    assert progress_calls == [(1, 2), (2, 2)]

@patch('app.services.ingest.ingest_chapter')
def test_ingest_multiple_chapters_with_text(mock_ingest):
    chapters_input = [
        {"title": "Chapter 1", "text": "Content 1"},
        {"title": "Chapter 2", "text": "Content 2"}
    ]
    
    mock_ingest.return_value = MagicMock()
    
    results = ingest_multiple_chapters("test_story", chapters_input, extractor="spacy")
    
    assert len(results) == 2
    assert mock_ingest.call_count == 2
