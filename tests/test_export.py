import os
import zipfile
import pytest

from app.core.story_manager import StoryManager
from app.services.export import get_audio_files, export_audiobook_zip, export_audiobook_html

@pytest.fixture
def mock_audio_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(StoryManager, "DATA_DIR", str(tmp_path))
    story_uuid = "test_story_export"
    audio_dir = os.path.join(tmp_path, story_uuid, "generated_audio")
    os.makedirs(audio_dir, exist_ok=True)
    
    # Create fake mp3 and vtt files for chapters 1 and 2
    for i in [1, 2]:
        with open(os.path.join(audio_dir, f"chapter_{i}_full.mp3"), "w") as f:
            f.write("fake mp3 data")
        with open(os.path.join(audio_dir, f"chapter_{i}_full.vtt"), "w") as f:
            f.write("WEBVTT\n\nfake vtt data")
            
    # Add some noise
    with open(os.path.join(audio_dir, "chapter_1_chunk_001.mp3"), "w") as f:
        f.write("chunk")
        
    return story_uuid, audio_dir

def test_get_audio_files(mock_audio_dir):
    story_uuid, _ = mock_audio_dir
    files = get_audio_files(story_uuid)
    
    assert len(files) == 2
    assert files[0][0] == 1
    assert files[1][0] == 2
    assert "chapter_1_full.mp3" in files[0][1]
    assert "chapter_1_full.vtt" in files[0][2]

def test_export_audiobook_zip(mock_audio_dir):
    story_uuid, _ = mock_audio_dir
    zip_path = export_audiobook_zip(story_uuid)
    
    assert os.path.exists(zip_path)
    assert zip_path.endswith(".zip")
    
    with zipfile.ZipFile(zip_path, 'r') as zf:
        names = zf.namelist()
        assert "chapter_1_full.mp3" in names
        assert "chapter_1_full.vtt" in names
        assert "chapter_2_full.mp3" in names
        assert "chapter_2_full.vtt" in names
        # Should not include chunks
        assert "chapter_1_chunk_001.mp3" not in names

def test_export_audiobook_html(mock_audio_dir):
    story_uuid, _ = mock_audio_dir
    zip_path = export_audiobook_html(story_uuid)
    
    assert os.path.exists(zip_path)
    
    with zipfile.ZipFile(zip_path, 'r') as zf:
        names = zf.namelist()
        assert "index.html" in names
        assert "audio/chapter_1_full.mp3" in names
        assert "audio/chapter_1_full.vtt" in names
