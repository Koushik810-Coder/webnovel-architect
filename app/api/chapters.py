from fastapi import APIRouter
from pydantic import BaseModel
from app.services.ingest import ingest_chapter
from app.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/chapters", tags=["chapters"])

class ChapterCreateRequest(BaseModel):
    story_uuid: str
    title: str
    text: str

@router.post("/")
def create_chapter(payload: ChapterCreateRequest):
    """
    Ingests a new chapter. 
    Triggers the Story Intelligence Pipeline:
    - Extracts characters/dialogue.
    - Updates character confidence scores.
    - Creates/Updates Wiki entries.
    - Performs Voice Graduation checks.
    """
    logger.info(f"Ingesting chapter '{payload.title}' for story {payload.story_uuid}")
    try:
        result = ingest_chapter(payload.story_uuid, payload.title, payload.text)
        logger.info(f"Successfully ingested chapter '{payload.title}'")
        return result
    except Exception as e:
        logger.error(f"Failed to ingest chapter '{payload.title}': {e}")
        raise e
