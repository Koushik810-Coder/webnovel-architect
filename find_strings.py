import sys
import os
sys.path.insert(0, r"c:\Projects\webnovel-architect\.agents\skills\word-document-processor")
from scripts.document import Document, DocxXMLEditor

doc = Document(r"c:\Projects\webnovel-architect\unpacked_doc", author="Webnovel Architect Assistant", initials="WAA", rsid="613BD437", track_revisions=True)
editor = doc["word/document.xml"]

def check(text):
    try:
        node = editor.get_node(tag="w:p", contains=text)
        print(f"Checking '{text}': Found")
    except ValueError:
        print(f"Checking '{text}': Not Found")

check("lookups in 3.7")
check("Spearman correlation with human narrative")
check("Combined World F1 of 78.0%")
check("aggressiveness of human forgetting.")
check("Limitations and Future Constraints:")
check("Voice ID is released back to the generic pool.")
check("Zero-GPU")
check("Speaker Diarization")
