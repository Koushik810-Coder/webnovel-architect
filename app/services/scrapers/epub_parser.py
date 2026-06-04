import zipfile
import re
import io
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from typing import Dict, Any, List

from app.core.logger import get_logger
logger = get_logger(__name__)

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

        with zipfile.ZipFile(io.BytesIO(file_content)) as archive:
            # 1. Look for the container.xml to find the rootfile (usually .opf)
            if 'META-INF/container.xml' not in archive.namelist():
                raise ValueError("Invalid EPUB: META-INF/container.xml missing")

            container_data = archive.read('META-INF/container.xml')
            # Use stdlib XML parser — avoids lxml dependency
            # strip() handles EPUBs that have leading whitespace before the XML declaration
            container_root = ET.fromstring(container_data.strip())
            # Strip namespace from tag names for robust lookup
            ns_strip = re.compile(r'\{[^}]+\}')

            opf_path = None
            for elem in container_root.iter():
                tag = ns_strip.sub('', elem.tag)
                if tag == 'rootfile':
                    opf_path = elem.get('full-path')
                    break

            if not opf_path:
                raise ValueError("Invalid EPUB: rootfile missing in container.xml")

            opf_dir = opf_path.rsplit('/', 1)[0] + '/' if '/' in opf_path else ''

            # 2. Read OPF to find spine (reading order) and manifest (files)
            opf_data = archive.read(opf_path)
            opf_root = ET.fromstring(opf_data.strip())

            manifest_elem = None
            spine_elem = None
            for elem in opf_root:
                tag = ns_strip.sub('', elem.tag)
                if tag == 'manifest':
                    manifest_elem = elem
                elif tag == 'spine':
                    spine_elem = elem

            if manifest_elem is None or spine_elem is None:
                raise ValueError("Invalid EPUB: manifest or spine missing from OPF")

            # Map id to href
            id_to_href = {}
            for item in manifest_elem:
                item_id = item.get('id')
                href = item.get('href')
                if item_id and href:
                    # Resolve relative path
                    id_to_href[item_id] = opf_dir + href

            # 3. Read chapters in spine order
            chapter_counter = 1
            for itemref in spine_elem:
                item_id = itemref.get('idref')
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
                        logger.warning(f"EpubParser warning: Failed to read {html_path}: {e}")
                        continue

        return chapters
