import requests
from bs4 import BeautifulSoup
from typing import Dict, Any
from app.services.scrapers.base_scraper import BaseScraper

class RoyalRoadScraper(BaseScraper):
    """Scraper provider for RoyalRoad.com"""
    
    @property
    def name(self) -> str:
        return "Royal Road"
        
    @property
    def base_url(self) -> str:
        return "https://www.royalroad.com"

    def can_handle_url(self, url: str) -> bool:
        return "royalroad.com/fiction/" in url and "/chapter/" in url

    def scrape_chapter(self, url: str) -> Dict[str, Any]:
        """
        Scrapes a Royal Road chapter page.
        Extracts the chapter title and the text content.
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 1. Extract Title
        title_element = soup.find("h1", class_="font-white")
        if not title_element:
            # Fallback
            title_element = soup.find("h1")
        title = title_element.text.strip() if title_element else "Unknown Royal Road Chapter"
        
        # 2. Extract Text Content
        # Royal Road puts chapter text in a div with class 'chapter-content'
        content_element = soup.find("div", class_="chapter-content")
        
        if not content_element:
            raise ValueError("Could not find chapter content div on Royal Road page.")
            
        # Get raw text, preserving paragraph breaks somewhat
        paragraphs = content_element.find_all("p")
        raw_text = "\n\n".join([p.text.strip() for p in paragraphs if p.text.strip()])
        
        # If no <p> tags, just get the text
        if not raw_text:
            raw_text = content_element.text.strip()
            
        return {
            "title": title,
            "text": raw_text
        }

    def can_handle_index_url(self, url: str) -> bool:
        return "royalroad.com/fiction/" in url and "/chapter/" not in url

    def scrape_index(self, url: str) -> list[Dict[str, str]]:
        """
        Scrapes a Royal Road fiction index page.
        Extracts all chapter titles and their complete URLs.
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        chapters = []
        
        # Royal Road chapter links are within a table with id 'chapters'
        table = soup.find("table", id="chapters")
        if table:
            rows = table.find("tbody").find_all("tr") if table.find("tbody") else table.find_all("tr")
            for row in rows:
                link_tag = row.find("a", href=True)
                if link_tag:
                    title = link_tag.text.strip()
                    href = link_tag['href']
                    # Handle relative URLs
                    full_url = f"{self.base_url}{href}" if href.startswith("/") else href
                    chapters.append({"title": title, "url": full_url})
                    
        return chapters
