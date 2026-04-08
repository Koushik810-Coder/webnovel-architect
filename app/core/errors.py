class WebnovelError(Exception):
    """Base exception for all webnovel architect errors."""
    pass

class ExtractionError(WebnovelError):
    """Raised when LLM data extraction fails or returns malformed results."""
    pass

class PipelineDependencyError(WebnovelError):
    """Raised when a pipeline step is executed out of order."""
    pass

class ExternalServiceError(WebnovelError):
    """Raised when an external service like TTS, LLM, or Scraper fails temporarily."""
    pass
