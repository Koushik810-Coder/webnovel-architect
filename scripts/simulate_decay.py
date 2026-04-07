import os
import sys
import networkx as nx
import pandas as pd

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.extraction import extract_chapter_intelligence

def calculate_temporal_pagerank(graph, lambda_val, current_chapter):
    scores = {}
    if len(graph) == 0:
        return scores
        
    try:
        pr = nx.pagerank(graph)
    except Exception as e:
        print(f"PageRank error: {e}")
        return scores
    
    N = len(graph.nodes())
    
    for node in graph.nodes():
        if graph.nodes[node].get('type') == 'character':
            last_seen = graph.nodes[node].get('last_seen', 0)
            delta_t = current_chapter - last_seen
            
            scaled_pr = pr[node] * N
            scores[node] = scaled_pr * ((1 - lambda_val) ** delta_t)
            
    return scores

def run_simulation(chapter_files, lambda_val):
    import spacy
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        nlp = spacy.load("en_core_web_md")
    
    G = nx.DiGraph()
    history = []
    
    for ch_num, file_path in enumerate(chapter_files, 1):
        if not os.path.exists(file_path):
            print(f"Warning: {file_path} not found. Skipping.")
            continue
            
        print(f"Processing Chapter {ch_num} (Lambda: {lambda_val})...")
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
            
        # Use focused spaCy PERSON NER to avoid sentence fragments polluting the graph.
        doc = nlp(text[:50000])  # Cap at 50k chars for performance
        
        # Strict filter: PERSON label, single/double token, no pronouns, starts with uppercase
        entities = list(set([
            ent.text.strip()
            for ent in doc.ents
            if ent.label_ == "PERSON"
            and 1 <= len(ent.text.split()) <= 2
            and ent.text[0].isupper()
            and ent.text.lower() not in {"i", "he", "she", "they", "we", "you"}
        ]))
        
        for entity in entities:
            if not G.has_node(entity):
                G.add_node(entity, type='character', first_seen=ch_num)
            
            G.nodes[entity]['last_seen'] = ch_num
            # Tie the character to the chapter event for graph structure
            G.add_node(f"Chapter_{ch_num}", type='event')
            G.add_edge(entity, f"Chapter_{ch_num}")
            G.add_edge(f"Chapter_{ch_num}", entity)
            
        scores = calculate_temporal_pagerank(G, lambda_val, ch_num)
        
        for char, score in scores.items():
            history.append({
                'Lambda Run': lambda_val,
                'Chapter': ch_num, 
                'Character': char, 
                'Temporal Score': score
            })
            
    return pd.DataFrame(history)

def main():
    dataset_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'dataset'))
    files = [os.path.join(dataset_dir, f"chapter_{i}.txt") for i in range(1, 6)]
    
    print("--- Running Ablation Study: Lambda = 0.00 (Static Edge Base) ---")
    df_static = run_simulation(files, lambda_val=0.00)
    
    print("\n--- Running Validation: Lambda = 0.15 (Aggressive Decay PoC) ---")
    df_decay = run_simulation(files, lambda_val=0.15)
    
    # Combine the dataframes
    final_df = pd.concat([df_static, df_decay], ignore_index=True)
    
    output_path = os.path.join(dataset_dir, "decay_results.csv")
    final_df.to_csv(output_path, index=False)
    print(f"\nSuccessfully generated {len(final_df)} data points into {output_path}.")

if __name__ == "__main__":
    main()
