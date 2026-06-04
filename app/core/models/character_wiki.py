from pydantic import BaseModel, field_validator
from typing import List, Optional, Any, Dict

class CharacterWiki(BaseModel):
    """
    Reader-Facing Canon Data.
    Stored in Markdown files. Editable by humans.
    Contains "Lore" (Appearance, Role, Backstory).
    """
    character_id: str

    version: int = 1
    generated_at: Optional[str] = None
    graph_snapshot_id: Optional[str] = None

    display_name: str
    aliases: List[str] = []

    short_description: str
    long_description: Optional[str] = None

    role: Optional[str] = None
    affiliations: List[str] = []

    species: Optional[str] = None
    age: Optional[str | int] = None
    gender: Optional[str] = None

    personality_traits: List[str] = []
    notable_quirks: List[str] = []

    # Powers, skills, techniques the character has demonstrated
    abilities: List[str] = []

    # What the character wants, is working toward, or is driven by
    goals: List[str] = []

    # Known weaknesses, limitations, fears, or vulnerabilities
    weaknesses: List[str] = []

    # Catch-all for important story facts: backstory reveals, achievements, secrets, rank-ups, etc.
    key_facts: List[str] = []

    appearance: Optional[str] = None

    # Structured appearance traits — individual attributes for change-tracking
    # e.g. {"hair_color": "black", "eye_color": "amber", "height": "tall", "build": "lean"}
    appearance_traits: Dict[str, str] = {}

    # Appearance change log — records when a trait visibly changed in the story
    # Each entry: {"chapter": int, "trait": str, "old_value": str, "new_value": str, "note": str}
    appearance_history: List[Dict[str, Any]] = []

    metadata: dict[str, Any] = {}
    relationships: List[Dict[str, Optional[str]]] = []
    timeline: List[Dict[str, Any]] = []

    first_appearance_chapter: int
    status: Optional[str] = None

    last_updated_chapter: int
    confidence: float = 1.0
    voice_id: Optional[str] = None

    @field_validator('age', mode='before')
    @classmethod
    def coerce_age_to_str(cls, v: Any) -> Optional[str]:
        if v is not None:
            return str(v)
        return v

    @field_validator('relationships', mode='before')
    @classmethod
    def sanitize_relationships(cls, v: Any) -> List[Dict]:
        """Filter non-dict items and coerce any None string values to empty string."""
        if not isinstance(v, list):
            return []
        clean = []
        for item in v:
            if not isinstance(item, dict):
                continue
            # Coerce None string values to '' so Pydantic Optional[str] is satisfied
            sanitized = {k: (str(val) if val is not None else None) for k, val in item.items()}
            clean.append(sanitized)
        return clean

    @field_validator('timeline', 'appearance_history', mode='before')
    @classmethod
    def sanitize_timeline(cls, v: Any) -> List[Dict]:
        """Filter non-dict items from timeline and appearance_history."""
        if not isinstance(v, list):
            return []
        return [item for item in v if isinstance(item, dict)]

    @field_validator('appearance_traits', mode='before')
    @classmethod
    def sanitize_appearance_traits(cls, v: Any) -> Dict[str, str]:
        """Ensure appearance_traits is always a str->str dict."""
        if not isinstance(v, dict):
            return {}
        return {str(k): str(val) for k, val in v.items() if k is not None and val is not None}

    @field_validator('affiliations', 'personality_traits', 'notable_quirks', 'aliases',
                     'abilities', 'goals', 'weaknesses', 'key_facts', mode='before')
    @classmethod
    def sanitize_string_lists(cls, v: Any) -> List[str]:
        """Filter None and non-string items from string list fields."""
        if not isinstance(v, list):
            return []
        return [str(item) for item in v if item is not None]
