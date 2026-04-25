from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Optional
from pydantic import BaseModel
from app.core.story_manager import StoryManager
from app.services.ingest import load_runtime, save_index_state, load_index_state, ingest_multiple_chapters
from app.services.scrapers.royalroad_scraper import RoyalRoadScraper
from app.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/stories", tags=["stories"])

# Demo ingestion limit — change here to update both the status display and the batch call.
_DEMO_CHAPTER_LIMIT = 3

def _get_story_progress(story_uuid: str) -> Optional[Dict]:
    """Helper to get progress data from index state."""
    state = load_index_state(story_uuid)
    if not state:
        return None
        
    chapters = state.get("chapters", [])
    total = min(len(chapters), _DEMO_CHAPTER_LIMIT)
    current = state.get("last_ingested_index", -1) + 1
    
    # Read strict status if set
    current_status = state.get("status")

    if current_status:
        # If explicitly recorded in state
        final_status = current_status
    else:
        # Legacy fallback
        if current >= total:
            final_status = "completed"
        elif current == 0 and total > 0:
            # Never started properly or aborted before first success
            final_status = "failed"
        else:
            # Previously paused/crashed mid-way
            final_status = "interrupted"
    
    return {
        "current": current,
        "total": total,
        "status": final_status
    }

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

class ImportRequest(BaseModel):
    url: str

def ingest_background(story_uuid: str, chapters: list):
    logger.info(f"Background ingest started for story {story_uuid} (chapters 1-3)")
    
    def progress_cb(current, total):
        state = load_index_state(story_uuid)
        if state:
            state["last_ingested_index"] = current - 1
            save_index_state(story_uuid, state)
            logger.debug(f"Progress update for {story_uuid}: {current}/{total}")

    try:
        # Mark as processing right as thread starts
        state = load_index_state(story_uuid)
        if state:
            state["status"] = "processing"
            save_index_state(story_uuid, state)

        ingest_multiple_chapters(
            story_uuid,
            chapters[:_DEMO_CHAPTER_LIMIT],
            extractor="spacy", 
            decay_rate=0.05,
            progress_callback=progress_cb
        )
        
        # Mark as completed
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
                
            story_name = chapters[0]['title'].split(" - ")[0] if " - " in chapters[0]['title'] else "Royal Road Novel"
            new_uuid = StoryManager.create_story(story_name)
            logger.info(f"Created new story '{story_name}' with UUID {new_uuid}")
            
            save_index_state(new_uuid, {
                "source_url": payload.url,
                "chapters": chapters,
                "metadata": metadata,
                "last_ingested_index": -1,
                "status": "processing" # Explicitly define status before background job starts
            })
            
            background_tasks.add_task(ingest_background, new_uuid, chapters)
            return {"status": "success", "story_uuid": new_uuid, "message": "Import started in background processing the first 3 chapters."}
        except Exception as e:
            logger.error(f"Failed to import from URL {payload.url}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    else:
        logger.warning(f"Invalid Royal Road Fiction URL provided: {payload.url}")
        raise HTTPException(status_code=400, detail="Invalid Royal Road Fiction URL")
