from fastapi import APIRouter
from pydantic import BaseModel
from app.services.ingest import ingest_chapter

router = APIRouter(prefix="/chapters", tags=["chapters"])

class ChapterCreateRequest(BaseModel):
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
    return ingest_chapter(payload.title, payload.text)
