from datetime import datetime
from app.core.models.chapter import Chapter

_chapter_counter = 0

def ingest_chapter(title: str, text: str) -> Chapter:
    global _chapter_counter
    _chapter_counter += 1

    return Chapter(
        id=_chapter_counter,
        title=title,
        raw_text=text,
        created_at=datetime.utcnow()
    )
