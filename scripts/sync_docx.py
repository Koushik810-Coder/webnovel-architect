import sys
import os
import re
import subprocess
from difflib import SequenceMatcher
import xml.etree.ElementTree as ET

# Add the docx skill root to path
sys.path.append(r'c:\Projects\webnovel-architect\.agents\skills\word-document-processor')
from scripts.document import Document, DocxXMLEditor

def normalize(text):
    if not text: return ""
    return re.sub(r'\s+', ' ', text).strip()

def get_para_text(para_node):
    return normalize("".join(c.data for n in para_node.getElementsByTagName("w:t") for c in n.childNodes if c.nodeType == c.TEXT_NODE))

def main():
    docx_path = r'c:\Projects\webnovel-architect\Documents\Webnovel_Architect_Refined (2).docx'
    unpack_dir = r'c:\Projects\webnovel-architect\unpacked_sync'
    
    if os.path.exists(unpack_dir):
        import shutil
        shutil.rmtree(unpack_dir)

    # Unpack document using docx skill
    subprocess.run(["python", r"c:\Projects\webnovel-architect\.agents\skills\docx\scripts\office\unpack.py", docx_path, unpack_dir], check=True)
    
    doc = Document(unpack_dir, track_revisions=False)
    xml_editor = doc["word/document.xml"]
    
    with open(r'c:\Projects\webnovel-architect\Documents\4_Research_Paper.md', encoding='utf-8') as f:
        md_text = f.read()
    
    raw_md_paras = [p.strip() for p in md_text.split('\n\n') if p.strip()]
    
    body = xml_editor.dom.getElementsByTagName("w:body")[0]
    
    # Save the sectPr if it exists at the end of the body
    sect_pr = None
    for child in list(body.childNodes):
        if child.nodeName == "w:sectPr":
            sect_pr = child
        body.removeChild(child)
            
    # Rebuild body
    for new_text in raw_md_paras:
        safe_text = new_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&#8220;').replace("'", '&#8217;')
        
        # Simple heading detection
        if safe_text.startswith('# '):
            p_xml = f'<w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>{safe_text[2:]}</w:t></w:r></w:p>'
        elif safe_text.startswith('### '):
            p_xml = f'<w:p><w:pPr><w:pStyle w:val="Heading2"/></w:pPr><w:r><w:t>{safe_text[4:]}</w:t></w:r></w:p>'
        else:
            p_xml = f'<w:p><w:r><w:t>{safe_text}</w:t></w:r></w:p>'

        # Add standard Word namespace so minidom doesn't throw unbound prefix
        p_xml = p_xml.replace('<w:p>', '<w:p xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">', 1)
        
        import xml.dom.minidom
        new_node = xml.dom.minidom.parseString(p_xml).documentElement
        body.appendChild(new_node)
        
    if sect_pr:
        body.appendChild(sect_pr)
        
    print("Document body rebuilt successfully! Saving...")
    doc.save(validate=False)
    subprocess.run(["python", r"c:\Projects\webnovel-architect\.agents\skills\docx\scripts\office\pack.py", unpack_dir, docx_path], check=True)
    print("Document repacked successfully!")

if __name__ == '__main__':
    main()
