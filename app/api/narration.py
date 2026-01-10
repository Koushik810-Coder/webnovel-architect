from fastapi import APIRouter
from pydantic import BaseModel
from app.services.narration import build_narration_segments

router = APIRouter(prefix="/narration", tags=["narration"])

class NarrationRequest(BaseModel):
    text: str

@router.post("/preview")
def preview(payload: NarrationRequest):
    return build_narration_segments(payload.text)
