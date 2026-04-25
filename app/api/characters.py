from fastapi import APIRouter
from pydantic import BaseModel
from app.services.characters import create_character

router = APIRouter(prefix="/characters", tags=["characters"])

class CharacterCreateRequest(BaseModel):
    story_uuid: str
    name: str
    short_description: str
    first_chapter: int

@router.post("/")
def create(payload: CharacterCreateRequest):
    """
    Manually creates a character.
    Useful for defining Protagonists before the first chapter is even written.
    """
    return create_character(
        story_uuid=payload.story_uuid,
        name=payload.name,
        short_description=payload.short_description,
        first_chapter=payload.first_chapter
    )
