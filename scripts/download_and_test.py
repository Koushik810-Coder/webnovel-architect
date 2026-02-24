import os
import urllib.request
import json
from core.ingestion import ingest_chapter_text
from adapters.graph_adapter import get_graph_engine

def load_env():
    if os.path.exists(".env"):
        with open(".env", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    key, val = line.strip().split("=", 1)
                    os.environ[key] = val.strip('\"\'')

def download_and_test():
    load_env()
    
    # clear old graph
    if os.path.exists("story_graph.json"):
        os.remove("story_graph.json")

    url = "https://www.gutenberg.org/cache/epub/11/pg11.txt"
    dataset_dir = "dataset"
    if not os.path.exists(dataset_dir):
        os.makedirs(dataset_dir)

    text_path = os.path.join(dataset_dir, "alice_full.txt")
    if not os.path.exists(text_path):
        print("Downloading full Alice in Wonderland dataset from Gutenberg...")
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            full_text = response.read().decode('utf-8')
        
        with open(text_path, "w", encoding="utf-8") as f:
             f.write(full_text)
    else:
        print("Full dataset already downloaded.")

    print("Dataset ready. Testing pipeline with a 4000-character snippet...")
    with open(text_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Extract a meaningful snippet, skipping Gutenberg preamble
    start_idx = text.find("CHAPTER I.")
    if start_idx == -1:
        start_idx = 0
    text_snippet = text[start_idx:start_idx+4000]

    print(f"Ingesting text snippet ({len(text_snippet)} chars)...")
    try:
        # Hitting real Gemini endpoint using the env key
        dialogue = ingest_chapter_text(text_snippet)
        print(f"Extracted Dialogue Lines: {len(dialogue)}")
        
        graph = get_graph_engine()
        nodes = graph.graph.number_of_nodes()
        edges = graph.graph.number_of_edges()
        print(f"Graph Details -> Total Nodes: {nodes}, Total Edges: {edges}")
        
        print("\n--- Character Centrality (PageRank) Scores ---")
        for node in graph.graph.nodes:
             if graph.graph.nodes[node].get("type") == "character":
                 score = graph.get_character_importance(node)
                 print(f"{node}: {score:.4f}")

    except Exception as e:
        print(f"Pipeline error: {e}")

if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    download_and_test()
