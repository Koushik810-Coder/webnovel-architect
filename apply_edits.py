import sys
import os
sys.path.insert(0, r"c:\Projects\webnovel-architect\.agents\skills\word-document-processor")
from scripts.document import Document, DocxXMLEditor

doc = Document(r"c:\Projects\webnovel-architect\unpacked_doc", author="Webnovel Architect Assistant", initials="WAA", rsid="613BD437", track_revisions=True)
editor = doc["word/document.xml"]

# 1. Zero-GPU to Zero-Local-GPU
try:
    n1 = editor.get_node(tag="w:r", contains='a Zero-GPU Neuro-Symbolic')
    rpr = tags[0].toxml() if (tags := n1.getElementsByTagName("w:rPr")) else ""
    editor.replace_node(n1, f'<w:r w:rsidR="613BD437">{rpr}<w:t>a </w:t></w:r><w:del><w:r>{rpr}<w:delText>Zero-GPU</w:delText></w:r></w:del><w:ins><w:r>{rpr}<w:t>Zero-Local-GPU</w:t></w:r></w:ins><w:r w:rsidR="613BD437">{rpr}<w:t> Neuro-Symbolic</w:t></w:r>')
except: pass

try:
    n2 = editor.get_node(tag="w:r", contains='constraint).')
    rpr2 = tags[0].toxml() if (tags := n2.getElementsByTagName("w:rPr")) else ""
    editor.replace_node(n2, f'<w:r w:rsidR="613BD437">{rpr2}<w:t>(the "</w:t></w:r><w:del><w:r>{rpr2}<w:delText>Zero-GPU</w:delText></w:r></w:del><w:ins><w:r>{rpr2}<w:t>Zero-Local-GPU</w:t></w:r></w:ins><w:r w:rsidR="613BD437">{rpr2}<w:t>" constraint).</w:t></w:r>')
except: pass

# 2. Voice Broker & Bootstrapping
try:
    n3 = editor.get_node(tag="w:p", contains='speculative one at first appearance.')
    tracked_para = DocxXMLEditor.suggest_paragraph('However, this presents a Bootstrapping Paradox: entirely new characters possess no topological significance upon introduction. To mitigate this, the architecture employs a temporary Voice Broker buffer. Distinct persistent voices are drawn from a finite pool (e.g., 6 Kokoro models) only upon threshold graduation. Characters below the threshold are rendered using a generic, rotating ambient voice pool until their continuous presence forces their PageRank high enough to warrant persistent casting. If the API extracting characters goes down or becomes unaffordable, the fallback drops to 40% F1, proving the system heavily relies on external GPU API endpoints.')
    editor.insert_after(n3, tracked_para)
except: pass

# 3. Lambda empirical grounding
try:
    n4 = editor.get_node(tag="w:p", contains='roughly 10 consecutive chapters before their score degrades to background status—consistent with observed pacing conventions in serialized web fiction arcs.')
    tracked_lambda = DocxXMLEditor.suggest_paragraph('However, this single constant lacks formal empirical grounding; further ablation studies and sensitivity analyses are required to mathematically validate this decay rate across diverse fiction lengths.')
    editor.insert_after(n4, tracked_lambda)
except: pass

# 4. Binary edges
try:
    n5 = editor.get_node(tag="w:p", contains='The current implementation employs binary edge semantics for inter-character relationships (interacts_with, mentions).')
    tracked_edges = DocxXMLEditor.suggest_paragraph('Because the graph cannot differentiate between hostile acts and passive observations, the PageRank centrality scores derived from this graph are measuring narrative exposure, rather than true narrative importance.')
    editor.insert_after(n5, tracked_edges)
except: pass

doc.save(r"c:\Projects\webnovel-architect\unpacked_modified", validate=False)
print("Finished saving")
