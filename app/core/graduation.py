from enum import Enum

class GraduationLevel(str, Enum):
    EXTRA = "extra"         # Background/One-off. No persistent voice.
    EVOLVING = "evolving"   # Recurring but undecided. Tracked in Wiki.
    MAIN_CAST = "main_cast" # Permanent fixture. Has a LOCKED voice ID.

from app.core.models.character_runtime import CharacterRuntime
from app.services.voice_assignment import assign_voice

def evaluate_graduation(confidence_score: float) -> GraduationLevel:
    if confidence_score < 0.25:
        return GraduationLevel.EXTRA
    elif confidence_score < 0.75:
        return GraduationLevel.EVOLVING
    else:
        return GraduationLevel.MAIN_CAST

def check_graduation_status(character: CharacterRuntime) -> bool:
    """
    Checks if character should graduate to a new level.
    If graduating to MAIN_CAST, locks a voice ID.
    Returns True if state changed.
    """
    new_level = evaluate_graduation(character.confidence_score)
    
    # We don't store "current level" on Runtime yet, but we can infer or add it.
    # For now, the critical check is voice locking.
    
    if new_level == GraduationLevel.MAIN_CAST and character.voice_id is None:
        # GRADUATION EVENT!
        # Assign voice based on known traits
        # TODO: Pull traits from Wiki or Runtime.vocal_traits
        character.voice_id = assign_voice(character.vocal_traits)
        return True
        
    return False
