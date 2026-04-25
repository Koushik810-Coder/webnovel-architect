from fastapi import HTTPException
from app.services.ingest import load_runtime, save_runtime
from app.core.graduation import evaluate_graduation, GraduationLevel
from app.services.voice_assignment import assign_voice

def register_appearance(story_uuid: str, character_id: str, chapter_id: int, dialogue_lines: int = 0):
    chapter_count, runtime_db = load_runtime(story_uuid)
    runtime = runtime_db.get(character_id)

    if runtime is None:
        raise HTTPException(
            status_code=404,
            detail="Character not found in this story's runtime database."
        )

    # Update appearance data
    runtime.last_seen_chapter = chapter_id
    runtime.confidence_score += 0.1 + (dialogue_lines * 0.05)

    # Evaluate graduation
    graduation = evaluate_graduation(runtime.confidence_score)

    # Lock voice only once
    if graduation == GraduationLevel.MAIN_CAST and runtime.voice_id is None:
        runtime.voice_id = assign_voice(character_id, runtime.vocal_traits)

    save_runtime(story_uuid, chapter_count, runtime_db)
    return runtime
