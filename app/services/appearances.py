from fastapi import HTTPException
from app.services.characters import CHARACTER_RUNTIME
from app.core.graduation import evaluate_graduation, GraduationLevel
from fastapi import HTTPException
from app.services.characters import CHARACTER_RUNTIME
from app.core.graduation import evaluate_graduation, GraduationLevel

from app.services.voice_casting import cast_voice



def register_appearance(character_id: str, chapter_id: int, dialogue_lines: int = 0):
    runtime = CHARACTER_RUNTIME.get(character_id)

    if runtime is None:
        raise HTTPException(
            status_code=404,
            detail="Character not found. Recreate character after server restart."
        )

    # Update appearance data
    runtime.last_seen_chapter = chapter_id
    runtime.confidence_score += 0.1 + (dialogue_lines * 0.05)

    # Evaluate graduation
    graduation = evaluate_graduation(runtime.confidence_score)

    # Lock voice only once
    if graduation == GraduationLevel.MAIN_CAST and runtime.voice_id is None:
        runtime.voice_id = cast_voice(runtime.vocal_traits)

    return runtime
