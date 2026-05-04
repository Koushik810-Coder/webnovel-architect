import json
import math
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.story_manager import StoryManager
from app.services.ingest import ingest_chapter, load_runtime
from adapters.graph_adapter import _graph_instances

def spearman(a, b):
    if len(a) < 2: return 0.0
    pa = {x: i for i, x in enumerate(a)}
    pb = {x: i for i, x in enumerate(b)}
    # Only compare common elements to avoid bias from extra discovered characters
    common = [x for x in a if x in pb]
    if len(common) < 2: return 0.0
    
    d2 = sum((pa[x] - pb[x])**2 for x in common)
    n = len(common)
    return 1 - (6 * d2) / (n * (n**2 - 1))

def run_ablation():
    gold_path = "dataset/gold_standard.json"
    if not os.path.exists(gold_path):
        print(f"Error: {gold_path} not found")
        return

    with open(gold_path, "r", encoding="utf-8") as f:
        gold_data = json.load(f)

    text = gold_data["text"]
    expected_rank = gold_data["expected_rank_order"]
    expected_ids = [n.lower().replace(" ", "_").replace("'", "") for n in expected_rank]

    # Test range of decay rates
    decay_rates = [0.0, 0.01, 0.05, 0.1, 0.15, 0.2, 0.5]
    results = []

    print(f"Running Ablation Study on {gold_path}...")
    print(f"{'Lambda':<10} | {'Spearman Rho':<15} | {'Top 1 Match'}")
    print("-" * 45)

    for l in decay_rates:
        # Use a fresh temp story for each run to avoid state contamination
        story_id = StoryManager.create_story(f"ablation_lambda_{l}")
        _graph_instances.pop(story_id, None)
        
        try:
            # Ingest using spaCy for speed and determinism
            ingest_chapter(story_id, "Gold Chapter", text, extractor="spacy", decay_rate=l)
            _, rdb = load_runtime(story_id)
            
            # Sort by score
            computed_sorted = sorted(rdb.values(), key=lambda c: c.confidence_score, reverse=True)
            computed_rank = [c.character_id for c in computed_sorted]
            
            rho = spearman(expected_ids, computed_rank)
            top_match = "YES" if (computed_rank and expected_ids and computed_rank[0] == expected_ids[0]) else "NO"
            
            print(f"{l:<10.2f} | {rho:<15.4f} | {top_match}")
            results.append({"lambda": l, "rho": rho, "top_match": top_match})
            
        finally:
            # Cleanup
            StoryManager.soft_delete_story(story_id)
            _graph_instances.pop(story_id, None)

    # Find optimal
    best = max(results, key=lambda x: x["rho"])
    print("-" * 45)
    print(f"Optimal Lambda Found: {best['lambda']} (Rho: {best['rho']:.4f})")

if __name__ == "__main__":
    run_ablation()
