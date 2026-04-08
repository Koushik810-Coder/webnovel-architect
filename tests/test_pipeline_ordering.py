import pytest
from app.core.errors import PipelineDependencyError
# We will implement this in app/services/pipeline_context.py
from app.services.pipeline_context import ChapterPipeline, PipelineState

def test_pipeline_valid_full_execution():
    """Test the happy path of the state machine."""
    pipeline = ChapterPipeline(chapter_id=1, intelligence={"active_character_names": ["Aria", "Duke Aria"]})
    
    assert pipeline.state == PipelineState.INITIAL
    
    pipeline.resolve_aliases()
    assert pipeline.state == PipelineState.ALIASES_RESOLVED
    
    pipeline.map_genders()
    assert pipeline.state == PipelineState.GENDERS_MAPPED
    
    pipeline.assign_voices()
    assert pipeline.state == PipelineState.VOICES_ASSIGNED

def test_pipeline_invalid_order_genders_before_aliases():
    """Test that mapping genders before alias resolution raises a dependency error."""
    pipeline = ChapterPipeline(chapter_id=1, intelligence={})
    
    with pytest.raises(PipelineDependencyError, match="Cannot map genders. Current state must be ALIASES_RESOLVED"):
        pipeline.map_genders()
        
def test_pipeline_invalid_order_voices_before_genders():
    """Test that voice assignment fails if gender mapping never happened."""
    pipeline = ChapterPipeline(chapter_id=1, intelligence={})
    pipeline.resolve_aliases()
    
    with pytest.raises(PipelineDependencyError, match="Cannot assign voices. Current state must be GENDERS_MAPPED"):
        pipeline.assign_voices()

def test_pipeline_repeated_step_is_noop():
    """Test that repeating a valid step deterministically raises or no-ops without state corruption."""
    pipeline = ChapterPipeline(chapter_id=1, intelligence={})
    
    pipeline.resolve_aliases()
    with pytest.raises(PipelineDependencyError, match="Step already completed"):
        pipeline.resolve_aliases()  # Should fail fast if repeated incorrectly
