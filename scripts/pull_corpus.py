import os
import sys

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.scrapers.royalroad_scraper import RoyalRoadScraper

def main():
    scraper = RoyalRoadScraper()
    dataset_dir = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), 'dataset')
    os.makedirs(dataset_dir, exist_ok=True)
    
    # We will use Mother of Learning as the PoC Webnovel
    # https://www.royalroad.com/fiction/21220/mother-of-learning
    mol_index_url = "https://www.royalroad.com/fiction/21220/mother-of-learning"
    
    print(f"Scraping fiction index: {mol_index_url}")
    try:
        chapters = scraper.scrape_index(mol_index_url)
    except Exception as e:
        print(f"Index scraping failed: {e}")
        return
        
    print(f"Found {len(chapters)} chapters. Pulling the first 5...")
    
    # Pull chapters 1 through 5
    for i, chap in enumerate(chapters[:5]):
        chapter_num = i + 1
        url = chap['url']
        print(f"Downloading Chapter {chapter_num}: {chap['title']} ({url})")
        
        try:
            chapter_data = scraper.scrape_chapter(url)
            text_content = chapter_data['text']
            
            output_path = os.path.join(dataset_dir, f"chapter_{chapter_num}.txt")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text_content)
                
            print(f" -> Saved {len(text_content)} characters to {output_path}")
        except Exception as e:
            print(f" -> Failed to download Chapter {chapter_num}: {e}")

if __name__ == "__main__":
    main()
