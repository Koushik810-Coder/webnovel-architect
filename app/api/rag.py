from fastapi import APIRouter
from pydantic import BaseModel
from app.services.rag import query_story
from app.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/stories", tags=["rag"])


class QuestionRequest(BaseModel):
    query: str


@router.post("/{story_uuid}/ask")
def ask_question(story_uuid: str, payload: QuestionRequest):
    """Runs RAG Q&A query against the story graph."""
    logger.info(f"Q&A query for story {story_uuid}: {payload.query[:80]}")
    try:
        answer = query_story(story_uuid, payload.query)
        return {"answer": answer}
    except Exception as e:
        logger.error(f"Q&A failed: {e}")
        return {"answer": f"Sorry, I couldn't process that question: {str(e)}"}
