from fastapi import FastAPI
from app.api import chapters, appearances, characters
from app.api import narration
from app.api import audio

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

app.include_router(narration.router)
app.include_router(audio.router)
app.include_router(appearances.router)
app.include_router(chapters.router)
app.include_router(characters.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
