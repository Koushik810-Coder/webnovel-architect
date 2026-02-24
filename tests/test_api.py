from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@patch('app.api.audio.build_narration_segments')
@patch('app.api.audio.render_segments')
def test_audio_preview(mock_render, mock_build):
    mock_build.return_value = [
        MagicMock(text="Test", character_id="char", voice_id="v1")
    ]
    # Mock render to return 2 dummy chunks
    mock_render.return_value = [b"chunk1", b"chunk2"]

    response = client.post("/audio/preview", json={"text": "Test"})
    
    assert response.status_code == 200
    data = response.json()
    assert "segments" in data
    assert "audio_chunks" in data
    assert data["audio_chunks"] == [6, 6] # len(b"chunk1") == 6
    mock_build.assert_called_once_with("Test")
    mock_render.assert_called_once()

@patch('app.api.chapters.ingest_chapter')
def test_create_chapter(mock_ingest):
    mock_chapter = MagicMock()
    mock_chapter.id = 1
    mock_chapter.title = "Chap 1"
    
    # Needs to be dict to serialize easily or we can mock dict return
    mock_ingest.return_value = {"id": 1, "title": "Chap 1"}
    
    response = client.post("/chapters/", json={"title": "Chap 1", "text": "Content"})
    
    assert response.status_code == 200
    assert response.json() == {"id": 1, "title": "Chap 1"}
    mock_ingest.assert_called_once_with("Chap 1", "Content")

@patch('app.api.characters.create_character')
def test_create_character(mock_create):
    mock_create.return_value = {"character_id": "hero_id"}
    
    response = client.post("/characters/", json={
        "name": "Hero",
        "short_description": "The chosen one",
        "first_chapter": 1
    })
    
    assert response.status_code == 200
    assert response.json() == {"character_id": "hero_id"}
    mock_create.assert_called_once_with(name="Hero", short_description="The chosen one", first_chapter=1)
