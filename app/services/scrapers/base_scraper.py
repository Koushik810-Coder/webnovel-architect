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

    @abstractmethod
    def scrape_index(self, url: str) -> list[Dict[str, str]]:
        """
        Scrapes a fiction index page and returns a list of chapter links.
        Returns:
            List of Dicts containing 'title' (str) and 'url' (str).
        """
        pass
