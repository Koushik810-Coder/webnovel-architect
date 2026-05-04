from pydantic import BaseModel, field_validator
from typing import List, Optional, Any


class ArcWiki(BaseModel):
    """
    Reader-facing wiki page for a narrative arc.
    Renders theme, start event, escalation, turning point, resolution,
    participating characters, and emotional/thematic evolution — per 2.5 spec.
    """
    arc_id: str
    display_name: str
    theme: str
    summary: str

    start_event_id: Optional[str] = None
    escalation_event_ids: List[str] = []
    turning_point_event_id: Optional[str] = None
    resolution_event_id: Optional[str] = None

    participating_characters: List[str] = []    # character_id list

    emotional_evolution: List[dict] = []        # [{"chapter": int, "note": str}]
    thematic_evolution: List[dict] = []         # [{"chapter": int, "note": str}]

    chapter_start: int = 0
    chapter_end: int = 0

    @field_validator("escalation_event_ids", "participating_characters", mode="before")
    @classmethod
    def sanitize_string_lists(cls, v: Any) -> List[str]:
        if not isinstance(v, list):
            return []
        return [str(item) for item in v if item is not None]

    @field_validator("emotional_evolution", "thematic_evolution", mode="before")
    @classmethod
    def sanitize_evolution_lists(cls, v: Any) -> List[dict]:
        if not isinstance(v, list):
            return []
        return [item for item in v if isinstance(item, dict)]
