import os
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import chapters, appearances, characters
from app.api import narration
from app.api import audio
from app.api import stories
from app.api import story_detail
from app.api import rag
from app.core.story_manager import StoryManager
from app.core.logger import get_logger

logger = get_logger("app.main")

app = FastAPI(
    title="Webnovel Architect",
    description="""
    ## Story Intelligence Engine
    A backend system that converts ongoing web novels into consistent audio by:
    1. Ingesting Chapters
    2. Extracting Character Data
    3. Building a Living Wiki
    4. Auto-Graduating Characters to Locked Voice IDs
    """
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - {response.status_code} ({duration:.2f}s)")
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow Vite localhost
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure data directory exists for static mounting
os.makedirs(StoryManager.DATA_DIR, exist_ok=True)
app.mount("/data", StaticFiles(directory=StoryManager.DATA_DIR), name="data")

# Prefix all API routes with /api for UI compatibility
app.include_router(narration.router, prefix="/api")
app.include_router(audio.router, prefix="/api")
app.include_router(appearances.router, prefix="/api")
app.include_router(chapters.router, prefix="/api")
app.include_router(characters.router, prefix="/api")
app.include_router(stories.router, prefix="/api")
app.include_router(story_detail.router, prefix="/api")
app.include_router(rag.router, prefix="/api")

@app.get("/api/health")
def health_check():
    return {"status": "ok"}
