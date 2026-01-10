from fastapi import APIRouter
from pydantic import BaseModel
from app.services.appearances import register_appearance

router = APIRouter(prefix="/appearances", tags=["appearances"])

class AppearanceRequest(BaseModel):
    character_id: str
    chapter_id: int
    dialogue_lines: int = 0

@router.post("/")
def create(payload: AppearanceRequest):
    return register_appearance(
        character_id=payload.character_id,
        chapter_id=payload.chapter_id,
        dialogue_lines=payload.dialogue_lines
    )
