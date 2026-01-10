from pydantic import BaseModel

class CharacterAppearance(BaseModel):
    character_id: str
    chapter_id: int
    dialogue_lines: int = 0
