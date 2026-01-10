from pydantic import BaseModel
from typing import Dict, Set, Optional

class CharacterRuntime(BaseModel):
    character_id: str

    confidence_score: float = 0.0
    traits: Set[str] = set()
    vocal_traits: Dict[str, str] = {}

    voice_id: Optional[str] = None

    first_seen_chapter: int
    last_seen_chapter: int
