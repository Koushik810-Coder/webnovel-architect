import requests
from bs4 import BeautifulSoup
import re

def scrape_royal_road(url: str) -> dict:
    """
    Scrapes a chapter from Royal Road given its URL.
    Returns a dictionary containing 'title' and 'text'.
    """
    if not url.startswith("https://www.royalroad.com/fiction/"):
        raise ValueError("Invalid Royal Road URL. Must start with 'https://www.royalroad.com/fiction/'")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise ConnectionError(f"Failed to fetch page. Status code: {response.status_code}")
        
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract title
    title_element = soup.find('h1', style=lambda value: value and 'margin-top' in value)
    if not title_element:
        # Fallback to standard h1 if style match fails
        title_element = soup.find('h1')
    
    title = title_element.get_text(strip=True) if title_element else "Unknown Chapter"
    
    # Extract chapter content
    chapter_content = soup.find('div', class_='chapter-content')
    if not chapter_content:
        raise ValueError("Could not find chapter content on the page.")
        
    # Extract text and keep basic paragraph formatting
    paragraphs = chapter_content.find_all(['p', 'div'])
    text_content = []
    
    for p in paragraphs:
        text = p.get_text(strip=True)
        if text:
            # Clean up extra spaces
            text = re.sub(r'\s+', ' ', text)
            text_content.append(text)
            
    return {
        'title': title,
        'text': '\n\n'.join(text_content)
    }
