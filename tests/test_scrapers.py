import pytest
import io
import zipfile
from unittest.mock import patch, MagicMock
from app.services.scrapers.royalroad_scraper import RoyalRoadScraper
from app.services.scrapers.epub_parser import EpubParser

def test_royal_road_scraper_can_handle():
    scraper = RoyalRoadScraper()
    # Chapter URL tests
    assert scraper.can_handle_url("https://www.royalroad.com/fiction/1234/story/chapter/5678/title") is True
    assert scraper.can_handle_url("https://google.com") is False
    # Index URL tests
    assert scraper.can_handle_index_url("https://www.royalroad.com/fiction/1234/story-slug") is True
    assert scraper.can_handle_index_url("https://www.royalroad.com/fiction/1234/story/chapter/5678/title") is False

@patch('app.services.scrapers.royalroad_scraper.requests.get')
def test_royal_road_scrape_index(mock_get):
    scraper = RoyalRoadScraper()

    mock_response = MagicMock()
    mock_response.text = """
    <html>
        <body>
            <table id="chapters">
                <tbody>
                    <tr>
                        <td><a href="/fiction/1/story/chapter/100/prologue">Prologue</a></td>
                    </tr>
                    <tr>
                        <td><a href="/fiction/1/story/chapter/200/chapter-one">Chapter One</a></td>
                    </tr>
                </tbody>
            </table>
        </body>
    </html>
    """
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    result = scraper.scrape_index("https://www.royalroad.com/fiction/1/story-slug")

    assert len(result) == 2
    assert result[0]["title"] == "Prologue"
    assert result[0]["url"] == "https://www.royalroad.com/fiction/1/story/chapter/100/prologue"
    assert result[1]["title"] == "Chapter One"

@patch('app.services.scrapers.royalroad_scraper.requests.get')
def test_royal_road_scraper_extraction(mock_get):
    scraper = RoyalRoadScraper()
    
    mock_response = MagicMock()
    mock_response.text = """
    <html>
        <body>
            <h1 class="font-white">Chapter 1: The Test</h1>
            <div class="chapter-content">
                <p>This is paragraph 1.</p>
                <p>This is paragraph 2.</p>
            </div>
        </body>
    </html>
    """
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    
    result = scraper.scrape_chapter("https://www.royalroad.com/fiction/1/a/chapter/2/b")
    
    assert result["title"] == "Chapter 1: The Test"
    assert "paragraph 1." in result["text"]
    assert "paragraph 2." in result["text"]

def test_epub_parser():
    # Construct a minimal valid EPUB file in memory
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w') as zf:
        # container.xml
        zf.writestr('META-INF/container.xml', '''
        <?xml version="1.0"?>
        <container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
            <rootfiles>
                <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
            </rootfiles>
        </container>
        ''')
        
        # content.opf
        zf.writestr('OEBPS/content.opf', '''
        <?xml version="1.0"?>
        <package version="2.0" xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookId">
            <manifest>
                <item id="chap1" href="chap1.html" media-type="application/xhtml+xml"/>
            </manifest>
            <spine>
                <itemref idref="chap1"/>
            </spine>
        </package>
        ''')
        
        # chap1.html
        zf.writestr('OEBPS/chap1.html', '''
        <html>
            <head><title>Chapter 1: Test Chapter</title></head>
            <body>
                <h1>Chapter 1: Test Chapter</h1>
                <p>This is dummy content.</p>
            </body>
        </html>
        ''')
        
    out.seek(0)
    parser = EpubParser()
    chapters = parser.parse_epub(out.read())
    
    assert len(chapters) == 1
    assert "Chapter 1: Test Chapter" in chapters[0]["title"]
    assert "This is dummy content." in chapters[0]["text"]
