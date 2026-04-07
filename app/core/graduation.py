from enum import Enum
from typing import Dict, Optional

from app.core.models.character_runtime import CharacterRuntime
from app.services.voice_assignment import assign_voice, get_registry

class GraduationLevel(str, Enum):
    EXTRA = "extra"         # Background/One-off. No persistent voice.
    EVOLVING = "evolving"   # Recurring but undecided. Tracked in Wiki.
    MAIN_CAST = "main_cast" # Permanent fixture. Has a LOCKED voice ID.

# Explicit thresholds adjusted for Weighted PageRank
DELTA_LOWER = 0.05
DELTA_UPPER = 0.15
MAIN_CAST_THRESHOLD = 0.50

def evaluate_graduation(confidence_score: float) -> GraduationLevel:
    if confidence_score < DELTA_UPPER:
        return GraduationLevel.EXTRA
    elif confidence_score < MAIN_CAST_THRESHOLD:
        return GraduationLevel.EVOLVING
    else:
        return GraduationLevel.MAIN_CAST

def check_graduation_status(character: CharacterRuntime, wiki_traits: Optional[Dict[str, str]] = None) -> bool:
    """
    Checks if character should graduate to a new level.
    If graduating to MAIN_CAST, locks a voice ID.
    Returns True if state changed.
    """
    new_level = evaluate_graduation(character.confidence_score)
    
    # We don't store "current level" on Runtime yet, but we can infer or add it.
    # For now, the critical check is voice locking and unlocking.
    
    if new_level == GraduationLevel.MAIN_CAST and character.voice_id is None:
        # GRADUATION EVENT!
        merged_traits = character.vocal_traits.copy()
        if wiki_traits:
            merged_traits.update(wiki_traits)
            
        character.voice_id = assign_voice(merged_traits)
        return True
        
    elif new_level != GraduationLevel.MAIN_CAST and character.voice_id is not None:
        # PROVISIONAL DE-GRADUATION (Decay below DELTA_UPPER after DPQ bootstrap)
        get_registry().release_voice(character.voice_id)
        character.voice_id = None
        return True
        
    return False
