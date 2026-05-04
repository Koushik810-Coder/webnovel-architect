from pydantic import BaseModel, field_validator
from typing import List, Optional, Any


class EventWiki(BaseModel):
    """
    Reader-facing wiki page for a story event.
    Renders the full causal chain, participant roles, pre/post conditions,
    and narrative vs story-time context — per the 2.5 spec.
    """
    event_id: str
    display_name: str
    summary: str

    cause: Optional[str] = None
    consequences: List[str] = []

    # Participants with roles: protagonist | antagonist | witness | cause | victim | bystander
    participants: List[dict] = []       # [{"character_id": str, "role": str}]

    location_id: Optional[str] = None
    arc_id: Optional[str] = None

    pre_conditions: Optional[str] = None
    post_conditions: Optional[str] = None

    before_events: List[str] = []      # event_id list (causal predecessors)
    after_events: List[str] = []       # event_id list (causal successors)

    chapter_id: int = 0
    narrative_order: int = 0

    # Dual-timeline fields (mirrors graph_adapter Phase 1.1)
    timeline_type: str = "present"     # present | flashback | memory | dream | rumor
    story_time_rank: Optional[int] = None

    # Spoiler / canonicity fields (Phase 1.2)
    spoiler_level: int = 0             # 0=safe, 1=mild, 2=major
    is_canonical: bool = True
    confidence: float = 1.0

    @field_validator("consequences", "before_events", "after_events", mode="before")
    @classmethod
    def sanitize_string_lists(cls, v: Any) -> List[str]:
        if not isinstance(v, list):
            return []
        return [str(item) for item in v if item is not None]

    @field_validator("participants", mode="before")
    @classmethod
    def sanitize_participants(cls, v: Any) -> List[dict]:
        if not isinstance(v, list):
            return []
        return [item for item in v if isinstance(item, dict)]
