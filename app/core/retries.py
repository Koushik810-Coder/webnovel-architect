import functools
import json
import time
from app.core.errors import ExternalServiceError

def with_retry(max_retries: int = 3, telemetry_path: str = "telemetry.jsonl", stage: str = "unknown", chapter_id: int = -1):
    """
    Retry decorator specifically for ExternalServiceErrors.
    If the function continues to fail after exhausted retries, 
    it writes structured telemetry to a JSONL file before re-raising.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts <= max_retries:
                try:
                    return func(*args, **kwargs)
                except ExternalServiceError as e:
                    if attempts >= max_retries:
                        # Serialize and dump telemetry
                        telemetry_data = {
                            "chapter_id": chapter_id,
                            "stage": stage,
                            "error_type": "ExternalServiceError",
                            "error_msg": str(e),
                            "retry_count": attempts
                        }
                        with open(telemetry_path, "a", encoding="utf-8") as f:
                            f.write(json.dumps(telemetry_data) + "\n")
                        raise
                    attempts += 1
            raise RuntimeError("Unreachable loop")
        return wrapper
    return decorator
