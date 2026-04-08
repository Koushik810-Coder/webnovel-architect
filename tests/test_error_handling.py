import pytest
import json
import os
from unittest.mock import MagicMock

# We will implement these in app/core/errors.py and app/core/retries.py
from app.core.errors import (
    WebnovelError, 
    ExtractionError, 
    PipelineDependencyError, 
    ExternalServiceError
)
from app.core.retries import with_retry

def test_retry_on_external_service_error_success():
    """Test that a transient ExternalServiceError is retried and succeeds eventually."""
    mock_operation = MagicMock()
    mock_operation.side_effect = [ExternalServiceError("API timeout"), "success"]
    
    @with_retry(max_retries=3, telemetry_path="test_telemetry.jsonl")
    def operation():
        return mock_operation()

    result = operation()
    
    assert result == "success"
    assert mock_operation.call_count == 2
    
    # Verify telemetry wasn't written since it succeeded before failing completely
    if os.path.exists("test_telemetry.jsonl"):
        with open("test_telemetry.jsonl", "r") as f:
            lines = f.readlines()
            assert len(lines) == 0

def test_retry_on_external_service_error_failure(tmp_path):
    """Test that it exhausts retries for ExternalServiceError and writes telemetry."""
    mock_operation = MagicMock()
    mock_operation.side_effect = ExternalServiceError("API down totally")
    
    telemetry_file = tmp_path / "telemetry_err.jsonl"
    
    @with_retry(max_retries=2, telemetry_path=str(telemetry_file), stage="extraction", chapter_id=5)
    def operation():
        return mock_operation()

    with pytest.raises(ExternalServiceError):
        operation()
        
    assert mock_operation.call_count == 3  # 1 initial + 2 retries
    
    # Assert telemetry is logged with structured data
    assert telemetry_file.exists()
    with open(telemetry_file, "r") as f:
        data = json.loads(f.readline())
        
    assert data["chapter_id"] == 5
    assert data["stage"] == "extraction"
    assert data["error_type"] == "ExternalServiceError"
    assert data["retry_count"] == 2

def test_no_retry_for_non_transient_errors():
    """Test that non-transient boundaries (e.g. ExtractionError) fail instantly."""
    mock_operation = MagicMock()
    mock_operation.side_effect = ExtractionError("Empty payload")

    @with_retry(max_retries=3, telemetry_path="test_telemetry_2.jsonl")
    def operation():
        return mock_operation()

    with pytest.raises(ExtractionError):
        operation()

    assert mock_operation.call_count == 1  # No retries!
