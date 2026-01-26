from pydantic import BaseModel
from typing import List, Optional

class CharacterWiki(BaseModel):
    """
    Reader-Facing Canon Data.
    Stored in Markdown files. Editable by humans.
    Contains "Lore" (Appearance, Role, Backstory).
    """
    character_id: str

    display_name: str
    aliases: List[str] = []

    short_description: str
    long_description: Optional[str] = None

    role: Optional[str] = None
    affiliations: List[str] = []

    species: Optional[str] = None
    age: Optional[str] = None

    personality_traits: List[str] = []
    notable_quirks: List[str] = []

    appearance: Optional[str] = None

    first_appearance_chapter: int
    status: Optional[str] = None

    last_updated_chapter: int
    confidence: float = 1.0
