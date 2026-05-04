from pydantic import BaseModel, field_validator
from typing import List, Optional, Any


class LocationWiki(BaseModel):
    """
    Reader-facing wiki page for a story location.
    Aggregated from graph event nodes sharing the same location field.
    """
    location_id: str
    display_name: str
    description: str

    region: Optional[str] = None
    significance: Optional[str] = None

    events_occurred: List[str] = []         # event_id list
    characters_present: List[str] = []      # character_id list (derived from events)
    timeline: List[dict] = []               # [{"chapter": int, "note": str}]

    first_appearance_chapter: int = 0
    last_updated_chapter: int = 0

    @field_validator("events_occurred", "characters_present", mode="before")
    @classmethod
    def sanitize_string_lists(cls, v: Any) -> List[str]:
        if not isinstance(v, list):
            return []
        return [str(item) for item in v if item is not None]

    @field_validator("timeline", mode="before")
    @classmethod
    def sanitize_timeline(cls, v: Any) -> List[dict]:
        if not isinstance(v, list):
            return []
        return [item for item in v if isinstance(item, dict)]
