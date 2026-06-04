from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseScraper(ABC):
    """
    Abstract base class for novel chapter scrapers.
    Based on the provider pattern from QuickNovel.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """The distinct name of the provider (e.g., 'Royal Road')."""
        pass

    @property
    @abstractmethod
    def base_url(self) -> str:
        """The base URL of the provider."""
        pass

    @abstractmethod
    def can_handle_url(self, url: str) -> bool:
        """Returns True if this scraper can handle the given URL."""
        pass

    @abstractmethod
    def scrape_chapter(self, url: str) -> Dict[str, Any]:
        """
        Scrapes a chapter URL and returns the title and raw text.
        Returns:
            Dict containing 'title' (str) and 'text' (str).
        """
        pass

    @abstractmethod
    def can_handle_index_url(self, url: str) -> bool:
        """Returns True if this scraper can handle the given index/fiction URL."""
        pass

    def fetch_with_retry(self, url: str, headers: dict = None, timeout: int = 15, max_retries: int = 3):
        """Helper method to fetch a URL with retry logic for resilience."""
        import requests
        import time
        last_exception = None
        for attempt in range(1, max_retries + 1):
            try:
                response = requests.get(url, headers=headers, timeout=timeout)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                last_exception = e
                if attempt < max_retries:
                    time.sleep(2 ** attempt)  # Exponential backoff
        raise ValueError(f"API Fallback: Failed to fetch {url} after {max_retries} attempts. Details: {str(last_exception)}")

    @abstractmethod
    def scrape_metadata(self, url: str) -> Dict[str, Any]:
        """
        Scrapes a fiction index page and returns metadata.
        Returns:
            Dict containing 'synopsis' (str) and 'cover_url' (str).
        """
        pass

    @abstractmethod
    def scrape_index(self, url: str) -> list[Dict[str, str]]:
        """
        Scrapes a fiction index page and returns a list of chapter links.
        Returns:
            List of Dicts containing 'title' (str) and 'url' (str).
        """
        pass

