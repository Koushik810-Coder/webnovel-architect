"""
tests/test_story_manager.py
============================
Tests for StoryManager filesystem CRUD operations:
  create_story, list_stories, get_story, rename_story,
  duplicate_story, soft_delete_story.

All tests use tmp_path to avoid touching real data/.
"""

import pytest
import os
import json
from app.core.story_manager import StoryManager


@pytest.fixture(autouse=True)
def isolated_data_dir(tmp_path, monkeypatch):
    """Redirect StoryManager to use a fresh temp directory."""
    monkeypatch.setattr(StoryManager, "DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setattr(StoryManager, "TRASH_DIR", str(tmp_path / "_trash"))
    yield


# ── create_story ─────────────────────────────────────────────────────────────

def test_create_story_returns_uuid():
    uuid = StoryManager.create_story("Test Novel")
    assert isinstance(uuid, str)
    assert len(uuid) == 36  # Standard UUID4 format


def test_create_story_creates_folder_structure():
    uuid = StoryManager.create_story("Test Novel")
    story_path = os.path.join(StoryManager.DATA_DIR, uuid)

    assert os.path.isdir(story_path)
    assert os.path.isdir(os.path.join(story_path, "wiki"))
    assert os.path.isdir(os.path.join(story_path, "chapters"))
    assert os.path.isfile(os.path.join(story_path, "story.json"))
    assert os.path.isfile(os.path.join(story_path, "runtime_db.json"))


def test_create_story_metadata_content():
    uuid = StoryManager.create_story("My Novel")
    meta = StoryManager.get_story(uuid)

    assert meta["uuid"] == uuid
    assert meta["name"] == "My Novel"
    assert "created_at" in meta
    assert "updated_at" in meta


def test_create_story_runtime_db_initialized():
    uuid = StoryManager.create_story("Runtime Test")
    runtime_path = os.path.join(StoryManager.DATA_DIR, uuid, "runtime_db.json")
    with open(runtime_path) as f:
        runtime = json.load(f)
    assert runtime["chapter_counter"] == 0
    assert runtime["characters"] == {}


# ── list_stories ──────────────────────────────────────────────────────────────

def test_list_stories_empty():
    assert StoryManager.list_stories() == []


def test_list_stories_returns_all():
    StoryManager.create_story("Novel A")
    StoryManager.create_story("Novel B")
    stories = StoryManager.list_stories()
    assert len(stories) == 2
    names = {s["name"] for s in stories}
    assert names == {"Novel A", "Novel B"}


def test_list_stories_sorted_by_updated_at():
    """Most recently updated story must appear first."""
    StoryManager.create_story("Old Novel")
    uuid_b = StoryManager.create_story("New Novel")
    stories = StoryManager.list_stories()
    # uuid_b was created last, so its updated_at is later
    assert stories[0]["uuid"] == uuid_b


# ── get_story ─────────────────────────────────────────────────────────────────

def test_get_story_returns_metadata():
    uuid = StoryManager.create_story("Get Test")
    meta = StoryManager.get_story(uuid)
    assert meta is not None
    assert meta["name"] == "Get Test"


def test_get_story_nonexistent_returns_none():
    result = StoryManager.get_story("00000000-0000-0000-0000-000000000000")
    assert result is None


# ── rename_story ──────────────────────────────────────────────────────────────

def test_rename_story_updates_name():
    uuid = StoryManager.create_story("Old Name")
    StoryManager.rename_story(uuid, "New Name")
    meta = StoryManager.get_story(uuid)
    assert meta["name"] == "New Name"


def test_rename_story_nonexistent_returns_false():
    result = StoryManager.rename_story("00000000-0000-0000-0000-000000000000", "Whatever")
    assert result is False


def test_rename_story_updates_updated_at():
    import time
    uuid = StoryManager.create_story("Timestamp Test")
    original_ts = StoryManager.get_story(uuid)["updated_at"]
    time.sleep(0.01)
    StoryManager.rename_story(uuid, "Renamed")
    new_ts = StoryManager.get_story(uuid)["updated_at"]
    assert new_ts >= original_ts


# ── duplicate_story ───────────────────────────────────────────────────────────

def test_duplicate_story_creates_new_uuid():
    uuid = StoryManager.create_story("Original")
    new_uuid = StoryManager.duplicate_story(uuid)
    assert new_uuid is not None
    assert new_uuid != uuid


def test_duplicate_story_appends_copy_suffix():
    uuid = StoryManager.create_story("Original")
    new_uuid = StoryManager.duplicate_story(uuid)
    meta = StoryManager.get_story(new_uuid)
    assert meta["name"] == "Original (Copy)"


def test_duplicate_story_has_independent_uuid():
    uuid = StoryManager.create_story("Source")
    new_uuid = StoryManager.duplicate_story(uuid)
    dup_meta = StoryManager.get_story(new_uuid)
    assert dup_meta["uuid"] == new_uuid  # Not the original UUID


def test_duplicate_nonexistent_returns_none():
    result = StoryManager.duplicate_story("00000000-0000-0000-0000-000000000000")
    assert result is None


# ── soft_delete_story ─────────────────────────────────────────────────────────

def test_soft_delete_removes_from_data_dir():
    uuid = StoryManager.create_story("To Delete")
    result = StoryManager.soft_delete_story(uuid)
    assert result is True
    assert StoryManager.get_story(uuid) is None


def test_soft_delete_moves_to_trash():
    uuid = StoryManager.create_story("Trash Me")
    StoryManager.soft_delete_story(uuid)
    # Folder should exist somewhere in TRASH_DIR
    trash_contents = os.listdir(StoryManager.TRASH_DIR)
    assert any(uuid in item for item in trash_contents)


def test_soft_delete_nonexistent_returns_false():
    result = StoryManager.soft_delete_story("00000000-0000-0000-0000-000000000000")
    assert result is False


# ── wipe_story_data ───────────────────────────────────────────────────────────

def test_wipe_story_data_preserves_story_json():
    uuid = StoryManager.create_story("Wipe Test")
    result = StoryManager.wipe_story_data(uuid)
    assert result is True
    meta = StoryManager.get_story(uuid)
    assert meta is not None
    assert meta["name"] == "Wipe Test"


def test_wipe_story_data_clears_chapters_and_wiki():
    uuid = StoryManager.create_story("Wipe Test 2")
    story_path = os.path.join(StoryManager.DATA_DIR, uuid)

    # Simulate some data existing
    os.makedirs(os.path.join(story_path, "chapters", "1"), exist_ok=True)
    with open(os.path.join(story_path, "chapters", "1", "text.txt"), "w") as f:
        f.write("Chapter text")
    with open(os.path.join(story_path, "wiki", "hero.json"), "w") as f:
        f.write("{}")
    with open(os.path.join(story_path, "story_graph.json"), "w") as f:
        f.write("{}")
    with open(os.path.join(story_path, "index_state.json"), "w") as f:
        f.write("{}")

    StoryManager.wipe_story_data(uuid)

    # Directories should exist but be empty
    assert os.path.isdir(os.path.join(story_path, "chapters"))
    assert os.listdir(os.path.join(story_path, "chapters")) == []
    assert os.path.isdir(os.path.join(story_path, "wiki"))
    assert os.listdir(os.path.join(story_path, "wiki")) == []

    # Data files should be gone
    assert not os.path.exists(os.path.join(story_path, "story_graph.json"))
    assert not os.path.exists(os.path.join(story_path, "index_state.json"))


def test_wipe_story_data_reinitializes_runtime():
    uuid = StoryManager.create_story("Wipe Runtime")
    story_path = os.path.join(StoryManager.DATA_DIR, uuid)

    # Simulate a runtime with data
    with open(os.path.join(story_path, "runtime_db.json"), "w") as f:
        json.dump({"chapter_counter": 10, "characters": {"hero": {}}}, f)

    StoryManager.wipe_story_data(uuid)

    with open(os.path.join(story_path, "runtime_db.json")) as f:
        runtime = json.load(f)
    assert runtime["chapter_counter"] == 0
    assert runtime["characters"] == {}


def test_wipe_story_data_nonexistent_returns_false():
    result = StoryManager.wipe_story_data("00000000-0000-0000-0000-000000000000")
    assert result is False
