from pydantic import BaseModel
from typing import Optional

class NarrationSegment(BaseModel):
    text: str
    character_id: Optional[str] = None
    voice_id: Optional[str] = None
