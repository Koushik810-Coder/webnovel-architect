import zipfile
import re
from bs4 import BeautifulSoup
from typing import Dict, Any, List

class EpubParser:
    """
    Parses EPUB files and extracts chapter text.
    """
    
    def parse_epub(self, file_content: bytes) -> List[Dict[str, Any]]:
        """
        Parses raw bytes of an EPUB file into a list of chapters.
        Returns:
            List of dicts containing 'title' (str) and 'text' (str).
        """
        chapters = []
        import io
        
        with zipfile.ZipFile(io.BytesIO(file_content)) as archive:
            # 1. Look for the container.xml to find the rootfile (usually .opf)
            if 'META-INF/container.xml' not in archive.namelist():
                raise ValueError("Invalid EPUB: META-INF/container.xml missing")
                
            container_data = archive.read('META-INF/container.xml')
            container_soup = BeautifulSoup(container_data, "xml")
            
            rootfile_tag = container_soup.find("rootfile")
            if not rootfile_tag or not rootfile_tag.get("full-path"):
                raise ValueError("Invalid EPUB: rootfile missing in container.xml")
                
            opf_path = rootfile_tag["full-path"]
            opf_dir = opf_path.rsplit('/', 1)[0] + '/' if '/' in opf_path else ''
            
            # 2. Read OPF to find spine (reading order) and manifest (files)
            opf_data = archive.read(opf_path)
            opf_soup = BeautifulSoup(opf_data, "xml")
            
            manifest = opf_soup.find("manifest")
            spine = opf_soup.find("spine")
            
            if not manifest or not spine:
                raise ValueError("Invalid EPUB: manifest or spine missing from OPF")
                
            # Map id to href
            id_to_href = {}
            for item in manifest.find_all("item"):
                item_id = item.get("id")
                href = item.get("href")
                if item_id and href:
                    # Resolve relative path
                    id_to_href[item_id] = opf_dir + href
                    
            # 3. Read chapters in spine order
            chapter_counter = 1
            for itemref in spine.find_all("itemref"):
                item_id = itemref.get("idref")
                if item_id in id_to_href:
                    html_path = id_to_href[item_id]
                    try:
                        html_data = archive.read(html_path)
                        soup = BeautifulSoup(html_data, "html.parser")
                        
                        # Extract title
                        title_tag = soup.find(["h1", "h2", "title"])
                        if title_tag:
                            title = title_tag.text.strip()
                        else:
                            title = f"Chapter {chapter_counter}"
                            
                        # Extract text
                        body = soup.find("body")
                        if body:
                            paragraphs = body.find_all("p")
                            text = "\n\n".join([p.text.strip() for p in paragraphs if p.text.strip()])
                            
                            # Fallback if no <p> tags
                            if not text:
                                text = body.text.strip()
                                
                            if text: # Only save if there is content
                                chapters.append({
                                    "title": title,
                                    "text": text
                                })
                                chapter_counter += 1
                    except Exception as e:
                        print(f"EpubParser warning: Failed to read {html_path}: {e}")
                        continue
                        
        return chapters
