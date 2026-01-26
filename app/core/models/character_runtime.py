from pydantic import BaseModel
from typing import Dict, Set, Optional

class CharacterRuntime(BaseModel):
    """
    System-Facing Intelligence Data.
    Stored in Database/Memory. Managed by the Engine.
    Contains "Stats" (Confidence, Voice IDs, Counts).
    """
    character_id: str

    confidence_score: float = 0.0
    
    # Story Intelligence Metrics
    dialogue_count: int = 0
    mention_count: int = 0
    network_centrality: float = 0.0
    
    # Voice System
    vocal_traits: Dict[str, str] = {}
    voice_id: Optional[str] = None


    first_seen_chapter: int
    last_seen_chapter: int
