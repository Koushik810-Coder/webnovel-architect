from enum import Enum

class GraduationLevel(str, Enum):
    EXTRA = "extra"
    EVOLVING = "evolving"
    MAIN_CAST = "main_cast"

def evaluate_graduation(confidence_score: float) -> GraduationLevel:
    if confidence_score < 0.25:
        return GraduationLevel.EXTRA
    elif confidence_score < 0.75:
        return GraduationLevel.EVOLVING
    else:
        return GraduationLevel.MAIN_CAST
