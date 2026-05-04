from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Optional
from pydantic import BaseModel
from app.core.story_manager import StoryManager
from app.services.ingest import load_runtime, save_index_state, load_index_state, ingest_multiple_chapters
from app.services.scrapers.royalroad_scraper import RoyalRoadScraper
from app.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/stories", tags=["stories"])

# Default batch size for the initial import.
_DEFAULT_INITIAL_BATCH = 3

def _get_story_progress(story_uuid: str) -> Optional[Dict]:
    """Helper to get progress data from index state."""
    state = load_index_state(story_uuid)
    if not state:
        return None
        
    chapters = state.get("chapters", [])
    total_available = len(chapters)
    current = state.get("last_ingested_index", -1) + 1
    
    # Read strict status if set
    current_status = state.get("status")

    if current_status:
        final_status = current_status
    else:
        if current >= total_available:
            final_status = "completed"
        elif current == 0 and total_available > 0:
            final_status = "failed"
        else:
            final_status = "idle"
    
    return {
        "current": current,
        "total": current,
        "total_available": total_available,
        "status": final_status
    }


def _deduplicate_name(desired_name: str) -> str:
    """If a story with `desired_name` already exists, return 'Name 2', 'Name 3', etc."""
    existing_names = {s["name"] for s in StoryManager.list_stories()}
    if desired_name not in existing_names:
        return desired_name
    
    counter = 2
    while True:
        candidate = f"{desired_name} {counter}"
        if candidate not in existing_names:
            return candidate
        counter += 1


@router.get("/")
def get_stories():
    logger.info("Listing all stories")
    stories = StoryManager.list_stories()
    for s in stories:
        state = load_index_state(s["uuid"])
        if state and "metadata" in state:
            s["metadata"] = state["metadata"]
        s["progress"] = _get_story_progress(s["uuid"])
    return stories

@router.get("/{story_uuid}")
def get_story(story_uuid: str):
    logger.info(f"Fetching story details for UUID: {story_uuid}")
    story = StoryManager.get_story(story_uuid)
    if not story:
        logger.warning(f"Story not found: {story_uuid}")
        raise HTTPException(status_code=404, detail="Story not found")
        
    try:
        chapter_count, runtime_db = load_runtime(story_uuid)
    except Exception as e:
        logger.error(f"Failed to load runtime for story {story_uuid}: {e}")
        chapter_count = 0
        
    story["chapter_count"] = chapter_count
    
    state = load_index_state(story_uuid)
    if state and "metadata" in state:
        story["metadata"] = state["metadata"]
        
    story["progress"] = _get_story_progress(story_uuid)
    return story


# ── CRUD Payloads ──────────────────────────────────────────────────────────────

class ImportRequest(BaseModel):
    url: str

class CreateStoryRequest(BaseModel):
    name: str

class RenameRequest(BaseModel):
    name: str

class IngestMoreRequest(BaseModel):
    count: int = 5


# ── Story Management Endpoints ─────────────────────────────────────────────────

@router.post("/create")
def create_story(payload: CreateStoryRequest):
    """Create a blank story with a given name."""
    name = _deduplicate_name(payload.name.strip())
    new_uuid = StoryManager.create_story(name)
    logger.info(f"Created blank story '{name}' (UUID: {new_uuid})")
    return {"status": "success", "story_uuid": new_uuid, "name": name}


@router.put("/{story_uuid}/rename")
def rename_story(story_uuid: str, payload: RenameRequest):
    """Rename an existing story."""
    new_name = payload.name.strip()
    if not new_name:
        raise HTTPException(status_code=400, detail="Name cannot be empty")
    success = StoryManager.rename_story(story_uuid, new_name)
    if not success:
        raise HTTPException(status_code=404, detail="Story not found")
    return {"status": "success", "name": new_name}


@router.delete("/{story_uuid}")
def delete_story(story_uuid: str):
    """Soft-delete a story (moved to trash)."""
    success = StoryManager.soft_delete_story(story_uuid)
    if not success:
        raise HTTPException(status_code=404, detail="Story not found")
    return {"status": "success"}


@router.post("/{story_uuid}/wipe")
def wipe_story(story_uuid: str):
    """Wipe all generated data but keep the story shell."""
    success = StoryManager.wipe_story_data(story_uuid)
    if not success:
        raise HTTPException(status_code=404, detail="Story not found")
    return {"status": "success"}


# ── Import & Ingestion Flow ────────────────────────────────────────────────────

def _ingest_background(story_uuid: str, chapters_slice: list, start_offset: int):
    """Generic background worker that ingests a slice of chapters.
    
    Args:
        story_uuid: Target story.
        chapters_slice: The list of chapter dicts to process (each has 'title' & 'url').
        start_offset: The 0-based global index of the first chapter in this batch
                      (used to correctly update last_ingested_index).
    """
    batch_count = len(chapters_slice)
    logger.info(f"Background ingest started for story {story_uuid}: "
                f"{batch_count} chapters starting at index {start_offset}")
    
    def progress_cb(current, total):
        state = load_index_state(story_uuid)
        if state:
            state["last_ingested_index"] = start_offset + current - 1
            save_index_state(story_uuid, state)
            logger.debug(f"Progress update for {story_uuid}: "
                         f"global index {start_offset + current - 1}, batch {current}/{total}")

    try:
        state = load_index_state(story_uuid)
        if state:
            state["status"] = "processing"
            save_index_state(story_uuid, state)

        ingest_multiple_chapters(
            story_uuid,
            chapters_slice,
            extractor="llm", 
            decay_rate=0.05,
            progress_callback=progress_cb
        )
        
        state = load_index_state(story_uuid)
        if state:
            state["status"] = "completed"
            save_index_state(story_uuid, state)
            
        logger.info(f"Background ingest completed for story {story_uuid}")
    except Exception as e:
        logger.error(f"Background ingest failed for story {story_uuid}: {e}")
        state = load_index_state(story_uuid)
        if state:
            state["status"] = "failed"
            state["error_message"] = str(e)
            save_index_state(story_uuid, state)


@router.post("/{story_uuid}/ingest_more")
def ingest_more_chapters(story_uuid: str, payload: IngestMoreRequest, background_tasks: BackgroundTasks):
    """Continue ingesting the next N chapters from the scraped index."""
    state = load_index_state(story_uuid)
    if not state or "chapters" not in state:
        raise HTTPException(status_code=400, detail="No chapter index found. Import a URL first.")
    
    if state.get("status") == "processing":
        raise HTTPException(status_code=409, detail="Ingestion already in progress.")
    
    all_chapters = state["chapters"]
    next_index = state.get("last_ingested_index", -1) + 1
    remaining = len(all_chapters) - next_index
    
    if remaining <= 0:
        raise HTTPException(status_code=400, detail="All chapters have already been ingested.")
    
    batch_count = min(payload.count, remaining)
    chapters_slice = all_chapters[next_index:next_index + batch_count]
    
    logger.info(f"Ingest more: story {story_uuid}, processing {batch_count} chapters "
                f"(index {next_index} to {next_index + batch_count - 1})")
    
    # Pre-set status to processing
    state["status"] = "processing"
    save_index_state(story_uuid, state)
    
    background_tasks.add_task(_ingest_background, story_uuid, chapters_slice, next_index)
    return {
        "status": "success",
        "batch_count": batch_count,
        "starting_at": next_index,
        "remaining_after": remaining - batch_count,
        "message": f"Processing {batch_count} more chapters in background."
    }


@router.post("/import_url")
def import_royalroad(payload: ImportRequest, background_tasks: BackgroundTasks):
    logger.info(f"Request to import Royal Road novel from: {payload.url}")
    scraper = RoyalRoadScraper()
    if scraper.can_handle_index_url(payload.url):
        try:
            chapters = scraper.scrape_index(payload.url)
            metadata = scraper.scrape_metadata(payload.url)
            if not chapters:
                logger.error(f"No chapters found at URL: {payload.url}")
                raise HTTPException(status_code=400, detail="No chapters found at URL")
            
            # Use the real fiction title from the page; fallback to chapter-title heuristic
            raw_name = metadata.get("title", "").strip()
            if not raw_name:
                raw_name = chapters[0]['title'].split(" - ")[0] if " - " in chapters[0]['title'] else "Royal Road Novel"
            
            story_name = _deduplicate_name(raw_name)
            new_uuid = StoryManager.create_story(story_name)
            logger.info(f"Created new story '{story_name}' with UUID {new_uuid}")
            
            initial_batch = min(_DEFAULT_INITIAL_BATCH, len(chapters))
            
            save_index_state(new_uuid, {
                "source_url": payload.url,
                "chapters": chapters,
                "metadata": metadata,
                "last_ingested_index": -1,
                "status": "processing"
            })
            
            background_tasks.add_task(_ingest_background, new_uuid, chapters[:initial_batch], 0)
            return {
                "status": "success",
                "story_uuid": new_uuid,
                "name": story_name,
                "total_available": len(chapters),
                "initial_batch": initial_batch,
                "message": f"Import started — processing the first {initial_batch} of {len(chapters)} chapters."
            }
        except Exception as e:
            logger.error(f"Failed to import from URL {payload.url}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    else:
        logger.warning(f"Invalid Royal Road Fiction URL provided: {payload.url}")
        raise HTTPException(status_code=400, detail="Invalid Royal Road Fiction URL")
