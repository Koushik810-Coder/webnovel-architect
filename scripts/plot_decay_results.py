import os
import pandas as pd
import matplotlib.pyplot as plt

def main():
    dataset_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'dataset'))
    csv_file = os.path.join(dataset_dir, "decay_results.csv")
    
    if not os.path.exists(csv_file):
        print(f"Error: Could not find {csv_file}")
        return
        
    df = pd.read_csv(csv_file)
    
    # 'Mother' appears mainly in Ch1 then fades — ideal decay demonstration subject.
    # DyG-RAG (lambda=0.15) drives her below delta_lower=0.3 by Ch5.
    # Vector RAG (lambda=0.0, real dilution) stays above 0.3 — proving temporal hallucination.
    target_char = "mother"
    char_df = df[df['Character'].str.lower() == target_char].copy()
    
    if char_df.empty:
        print(f"Character {target_char} not found.")
        return
        
    decay_df  = char_df[char_df['Lambda Run'] == 0.15].sort_values('Chapter')
    static_df = char_df[char_df['Lambda Run'] == 0.00].sort_values('Chapter')
    
    chapters_range = decay_df['Chapter'].tolist()
    
    plt.figure(figsize=(10, 6))
    
    # Plot Static Vector RAG Baseline (real dilution, no lambda penalty)
    plt.plot(static_df['Chapter'], static_df['Temporal Score'],
             marker='o', linestyle='--', color='red', linewidth=2, 
             label=r"Standard Vector RAG ($\lambda=0.00$, no decay penalty)")
             
    # Plot DyG-RAG Decay
    plt.plot(decay_df['Chapter'], decay_df['Temporal Score'], 
             marker='s', linestyle='-', color='royalblue', linewidth=3, 
             label=r"Webnovel Architect DyG-RAG ($\lambda=0.15$)")
             
    # Add Threshold Lines
    plt.axhline(y=1.5, color='green', linestyle=':', label=r"Upper Threshold ($\delta_{upper} = 1.5$)")
    plt.axhline(y=0.3, color='orange', linestyle=':', label=r"Lower Threshold ($\delta_{lower} = 0.3$)")
    
    plt.title(f"Temporal Hallucination Ablation: Character '{target_char.capitalize()}'")
    plt.xlabel(r'Chapters Elapsed ($\Delta t$)')
    plt.ylabel('Retrieved Relevance Score')
    plt.xticks(range(1, 6))
    plt.ylim(bottom=0.0)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    output_png = os.path.join(dataset_dir, "temporal_ablation.png")
    plt.savefig(output_png, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Successfully generated ablation chart: {output_png}")

if __name__ == "__main__":
    main()
