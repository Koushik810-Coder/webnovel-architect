import os
import json
import uuid
import shutil
from datetime import datetime, timezone
from typing import List, Dict, Optional

from app.core.logger import get_logger

logger = get_logger(__name__)

class StoryManager:
    """Manages isolated data directories for individual webnovels."""
    
    DATA_DIR = "data"
    TRASH_DIR = "_trash"

    @classmethod
    def _ensure_dirs(cls):
        os.makedirs(cls.DATA_DIR, exist_ok=True)
        os.makedirs(cls.TRASH_DIR, exist_ok=True)

    @classmethod
    def create_story(cls, name: str) -> str:
        cls._ensure_dirs()
        story_uuid = str(uuid.uuid4())
        story_path = os.path.join(cls.DATA_DIR, story_uuid)
        
        # Create folder structure
        os.makedirs(story_path)
        os.makedirs(os.path.join(story_path, "wiki"))
        os.makedirs(os.path.join(story_path, "chapters"))
        
        # Initialize metadata
        metadata = {
            "uuid": story_uuid,
            "name": name,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        with open(os.path.join(story_path, "story.json"), "w") as f:
            json.dump(metadata, f, indent=4)
            
        # Initialize empty runtime
        runtime = {
            "chapter_counter": 0,
            "characters": {}
        }
        with open(os.path.join(story_path, "runtime_db.json"), "w") as f:
            json.dump(runtime, f, indent=4)

        logger.info(f"Created new story: '{name}' (UUID: {story_uuid})")
        return story_uuid

    @classmethod
    def list_stories(cls) -> List[Dict]:
        cls._ensure_dirs()
        stories = []
        for folder in os.listdir(cls.DATA_DIR):
            story_path = os.path.join(cls.DATA_DIR, folder)
            if os.path.isdir(story_path):
                meta_path = os.path.join(story_path, "story.json")
                if os.path.exists(meta_path):
                    try:
                        with open(meta_path, "r") as f:
                            stories.append(json.load(f))
                    except Exception:
                        # Corrupt JSON, permission error, etc. — skip this entry
                        continue
                        
        # Sort by updated_at descending
        stories.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        return stories

    @classmethod
    def get_story(cls, story_uuid: str) -> Optional[Dict]:
        meta_path = os.path.join(cls.DATA_DIR, story_uuid, "story.json")
        if os.path.exists(meta_path):
            with open(meta_path, "r") as f:
                return json.load(f)
        return None

    @classmethod
    def _touch_updated_at(cls, story_uuid: str):
        meta_path = os.path.join(cls.DATA_DIR, story_uuid, "story.json")
        if os.path.exists(meta_path):
            with open(meta_path, "r") as f:
                meta = json.load(f)
            meta["updated_at"] = datetime.now(timezone.utc).isoformat()
            with open(meta_path, "w") as f:
                json.dump(meta, f, indent=4)

    @classmethod
    def rename_story(cls, story_uuid: str, new_name: str) -> bool:
        meta_path = os.path.join(cls.DATA_DIR, story_uuid, "story.json")
        if os.path.exists(meta_path):
            with open(meta_path, "r") as f:
                meta = json.load(f)
            meta["name"] = new_name
            meta["updated_at"] = datetime.now(timezone.utc).isoformat()
            with open(meta_path, "w") as f:
                json.dump(meta, f, indent=4)
            logger.info(f"Renamed story UUID {story_uuid} to '{new_name}'")
            return True
        return False

    @classmethod
    def duplicate_story(cls, story_uuid: str) -> Optional[str]:
        src_path = os.path.join(cls.DATA_DIR, story_uuid)
        if not os.path.exists(src_path):
            return None
            
        new_uuid = str(uuid.uuid4())
        dst_path = os.path.join(cls.DATA_DIR, new_uuid)
        
        # Copy entire directory tree
        shutil.copytree(src_path, dst_path)
        
        # Update metadata for the duplicate
        meta_path = os.path.join(dst_path, "story.json")
        if os.path.exists(meta_path):
            with open(meta_path, "r") as f:
                meta = json.load(f)
            meta["uuid"] = new_uuid
            meta["name"] = f"{meta['name']} (Copy)"
            meta["created_at"] = datetime.now(timezone.utc).isoformat()
            meta["updated_at"] = datetime.now(timezone.utc).isoformat()
            with open(meta_path, "w") as f:
                json.dump(meta, f, indent=4)
                
        logger.info(f"Duplicated story UUID {story_uuid} to new UUID {new_uuid}")
        return new_uuid

    @classmethod
    def soft_delete_story(cls, story_uuid: str) -> bool:
        cls._ensure_dirs()
        src_path = os.path.join(cls.DATA_DIR, story_uuid)
        if not os.path.exists(src_path):
            return False
            
        dst_path = os.path.join(cls.TRASH_DIR, f"{story_uuid}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}")
        shutil.move(src_path, dst_path)
        logger.info(f"Soft deleted story UUID {story_uuid} -> moved to trash")
        return True

    @classmethod
    def wipe_story_data(cls, story_uuid: str) -> bool:
        """Deletes all generated data (chapters, wiki, graph, runtime, index)
        while preserving story.json metadata.  Gives a clean slate for re-ingestion.

        Returns True if the wipe succeeded, False if the story folder doesn't exist.
        """
        story_path = os.path.join(cls.DATA_DIR, story_uuid)
        if not os.path.exists(story_path):
            return False

        # Directories to completely remove and recreate
        for subdir in ("chapters", "wiki", "generated_audio"):
            dirpath = os.path.join(story_path, subdir)
            if os.path.exists(dirpath):
                shutil.rmtree(dirpath)
            os.makedirs(dirpath, exist_ok=True)

        # Individual data files to remove
        for fname in ("runtime_db.json", "story_graph.json", "index_state.json"):
            fpath = os.path.join(story_path, fname)
            if os.path.exists(fpath):
                os.remove(fpath)

        # Re-initialize empty runtime so the system doesn't crash on load
        runtime = {"chapter_counter": 0, "characters": {}}
        with open(os.path.join(story_path, "runtime_db.json"), "w") as f:
            json.dump(runtime, f, indent=4)

        # Evict the cached graph instance so it reloads fresh
        from adapters.graph_adapter import _graph_instances
        _graph_instances.pop(story_uuid, None)

        logger.info(f"Wiped all data for story UUID {story_uuid} (story.json preserved)")
        return True
