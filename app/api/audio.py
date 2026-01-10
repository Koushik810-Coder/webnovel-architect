from fastapi import APIRouter
from pydantic import BaseModel
from app.services.narration import build_narration_segments
from app.services.audio_renderer import render_segments

router = APIRouter(prefix="/audio", tags=["audio"])

class AudioPreviewRequest(BaseModel):
    text: str

@router.post("/preview")
def preview(payload: AudioPreviewRequest):
    segments = build_narration_segments(payload.text)
    audio = render_segments(segments)
    return {
        "segments": segments,
        "audio_chunks": [len(chunk) for chunk in audio]
    }
