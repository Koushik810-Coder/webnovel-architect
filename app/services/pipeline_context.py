import enum
from typing import Dict, Any
from app.core.logger import get_logger
from app.core.errors import PipelineDependencyError

logger = get_logger(__name__)

class PipelineState(enum.Enum):
    INITIAL = 0
    ALIASES_RESOLVED = 1
    GENDERS_MAPPED = 2
    VOICES_ASSIGNED = 3

class ChapterPipeline:
    """
    A strict state machine defining the sequence of data resolving blocks during ingestion
    and audio generation. Enforces that steps (alias resolution, gender mapping, voice
    assignment) happen sequentially.

    NOTE: This class is a structural scaffold and is **not currently wired into the
    production ingestion pipeline** (which handles these steps inline in ingest.py).
    It exists as a tested abstraction intended for a future refactor that centralises
    pipeline step ordering. See tests/test_pipeline_ordering.py.

    TODO: Wire into ingest.py once the step implementations are extracted here.
    """
    def __init__(self, chapter_id: int, intelligence: Dict[str, Any]):
        self.chapter_id = chapter_id
        self.intelligence = intelligence
        self.state = PipelineState.INITIAL

    def resolve_aliases(self) -> None:
        if self.state != PipelineState.INITIAL:
            raise PipelineDependencyError(f"Step already completed or invalid state: {self.state}")
            
        logger.info(f"[Chapter {self.chapter_id}] Transitioning to ALIASES_RESOLVED")
        # Logic to map aliases would go here
        
        self.state = PipelineState.ALIASES_RESOLVED

    def map_genders(self) -> None:
        if self.state != PipelineState.ALIASES_RESOLVED:
            raise PipelineDependencyError(f"Cannot map genders. Current state must be ALIASES_RESOLVED, but is {self.state}")
            
        logger.info(f"[Chapter {self.chapter_id}] Transitioning to GENDERS_MAPPED")
        # Logic to map genders
        
        self.state = PipelineState.GENDERS_MAPPED

    def assign_voices(self) -> None:
        if self.state != PipelineState.GENDERS_MAPPED:
            raise PipelineDependencyError(f"Cannot assign voices. Current state must be GENDERS_MAPPED, but is {self.state}")
            
        logger.info(f"[Chapter {self.chapter_id}] Transitioning to VOICES_ASSIGNED")
        # Logic to assign voices
        
        self.state = PipelineState.VOICES_ASSIGNED
