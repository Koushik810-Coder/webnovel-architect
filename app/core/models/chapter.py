from pydantic import BaseModel
from datetime import datetime

class Chapter(BaseModel):
    id: int
    title: str
    raw_text: str
    created_at: datetime
