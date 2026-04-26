import os
import json

from fastapi import APIRouter, HTTPException
from app.core.story_manager import StoryManager
from app.services.ingest import load_runtime
from app.services.wiki import load_character_wiki_json, get_wiki_dir, enrich_wiki_from_rag
from app.core.graduation import MAIN_CAST_THRESHOLD
from app.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/stories", tags=["stories-extended"])


@router.get("/{story_uuid}/chapters")
def list_chapters(story_uuid: str):
    """Returns list of chapters with titles and metadata."""
    chapters_dir = os.path.join(StoryManager.DATA_DIR, story_uuid, "chapters")
    if not os.path.isdir(chapters_dir):
        return []

    result = []
    for folder in sorted(os.listdir(chapters_dir), key=lambda x: int(x) if x.isdigit() else 0):
        meta_path = os.path.join(chapters_dir, folder, "metadata.json")
        if os.path.exists(meta_path):
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                text_path = os.path.join(chapters_dir, folder, "text.txt")
                word_count = 0
                if os.path.exists(text_path):
                    with open(text_path, "r", encoding="utf-8") as f:
                        word_count = len(f.read().split())
                meta["word_count"] = word_count
                result.append(meta)
            except Exception:
                continue
    return result


@router.get("/{story_uuid}/chapters/{chapter_index}")
def get_chapter(story_uuid: str, chapter_index: int):
    """Returns full chapter text and metadata."""
    chapter_dir = os.path.join(StoryManager.DATA_DIR, story_uuid, "chapters", str(chapter_index))
    if not os.path.isdir(chapter_dir):
        raise HTTPException(status_code=404, detail="Chapter not found")

    text_path = os.path.join(chapter_dir, "text.txt")
    meta_path = os.path.join(chapter_dir, "metadata.json")

    text = ""
    if os.path.exists(text_path):
        with open(text_path, "r", encoding="utf-8") as f:
            text = f.read()

    meta = {}
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)

    return {**meta, "text": text, "word_count": len(text.split())}


@router.get("/{story_uuid}/cast")
def get_cast(story_uuid: str):
    """Returns all characters with scores, voice IDs, graduation status."""
    try:
        chapter_counter, runtime_db = load_runtime(story_uuid)
    except Exception as e:
        logger.error(f"Failed to load runtime for cast: {e}")
        return []

    wiki_dir = get_wiki_dir(story_uuid)
    result = []

    for char_id, char in runtime_db.items():
        graduated = char.confidence_score >= MAIN_CAST_THRESHOLD or char.voice_id is not None
        entry = {
            "character_id": char_id,
            "display_name": char_id.replace("_", " ").title(),
            "confidence_score": round(char.confidence_score, 4),
            "mention_count": char.mention_count,
            "first_seen": char.first_seen_chapter,
            "last_seen": char.last_seen_chapter,
            "voice_id": char.voice_id,
            "graduated": graduated,
            "short_description": None,
        }

        wiki = load_character_wiki_json(story_uuid, char_id)
        if wiki:
            entry["display_name"] = wiki.display_name or entry["display_name"]
            entry["short_description"] = wiki.short_description

        result.append(entry)

    result.sort(key=lambda x: x["confidence_score"], reverse=True)
    return result


@router.get("/{story_uuid}/wiki/{character_id}")
def get_wiki_entry(story_uuid: str, character_id: str):
    """Returns structured wiki data for a character."""
    wiki = load_character_wiki_json(story_uuid, character_id)
    if not wiki:
        raise HTTPException(status_code=404, detail="Character wiki not found")
    return wiki.model_dump()


@router.post("/{story_uuid}/wiki/{character_id}/enrich")
def enrich_wiki(story_uuid: str, character_id: str):
    """Enriches a character wiki using RAG."""
    result = enrich_wiki_from_rag(story_uuid, character_id)
    if result:
        return {"status": "success"}
    raise HTTPException(status_code=500, detail="Enrichment failed or no events found")
