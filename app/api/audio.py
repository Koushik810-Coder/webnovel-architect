import os

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.narration import build_narration_segments
from app.services.audio_renderer import render_segments
from app.services.audiobook_generator import generate_chapter_audiobook
from app.core.story_manager import StoryManager
from app.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/audio", tags=["audio"])


class AudioPreviewRequest(BaseModel):
    text: str


@router.post("/preview")
def preview(payload: AudioPreviewRequest):
    logger.info("Request for audio preview")
    segments = build_narration_segments(payload.text)
    audio = render_segments(segments)
    return {
        "segments": segments,
        "audio_chunks": [len(chunk) for chunk in audio]
    }


@router.post("/{story_uuid}/chapter/{chapter_index}")
def render_chapter_audiobook(story_uuid: str, chapter_index: int):
    logger.info(f"Request to generate audiobook for story {story_uuid}, chapter {chapter_index}")
    try:
        # Explicit fast-path cache check before generation
        final_audio = os.path.join(
            StoryManager.DATA_DIR, story_uuid, "generated_audio",
            f"chapter_{chapter_index}_full.mp3"
        )
        final_vtt = os.path.join(
            StoryManager.DATA_DIR, story_uuid, "generated_audio",
            f"chapter_{chapter_index}_full.vtt"
        )

        if os.path.exists(final_audio) and os.path.exists(final_vtt):
            logger.info(f"Serving cached final audiobook for story {story_uuid}, chapter {chapter_index}")
            return {
                "status": "success",
                "audio_path": f"/data/{story_uuid}/generated_audio/chapter_{chapter_index}_full.mp3",
                "vtt_path": f"/data/{story_uuid}/generated_audio/chapter_{chapter_index}_full.vtt",
            }

        result = generate_chapter_audiobook(story_uuid, chapter_index)
        if result:
            logger.info(f"Successfully generated audiobook for story {story_uuid}, chapter {chapter_index}")
            return {
                "status": "success",
                "audio_path": f"/data/{story_uuid}/generated_audio/chapter_{chapter_index}_full.mp3",
                "vtt_path": f"/data/{story_uuid}/generated_audio/chapter_{chapter_index}_full.vtt",
            }
        else:
            logger.warning(f"Audiobook generation returned None for story {story_uuid}, chapter {chapter_index}")
            return {"status": "failed"}
    except Exception as e:
        logger.error(f"Failed to generate audiobook for story {story_uuid}, chapter {chapter_index}: {e}")
        return {"status": "error", "detail": str(e)}
