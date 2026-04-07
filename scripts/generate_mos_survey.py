import os
import sys
import glob
import random
import pandas as pd

def main():
    audio_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'output', 'audio_samples'))
    if not os.path.exists(audio_dir):
        print(f"Directory not found: {audio_dir}")
        return
        
    print(f"Scanning directory: {audio_dir}")
    
    # Find all baseline files
    baselines = glob.glob(os.path.join(audio_dir, '*_baseline.wav'))
    
    survey_data = []
    
    for baseline_path in baselines:
        filename = os.path.basename(baseline_path)
        # Format: {char}_{emotion}_baseline.wav
        prefix = filename.replace('_baseline.wav', '')
        dygrag_filename = f"{prefix}_dygrag.wav"
        dygrag_path = os.path.join(audio_dir, dygrag_filename)
        
        if not os.path.exists(dygrag_path):
            print(f"Warning: Expected pair '{dygrag_filename}' missing for '{filename}'")
            continue
            
        char, emotion = prefix.split('_', 1)
        pair_id = prefix.upper()
        
        # Randomize A vs B assignment
        is_baseline_a = random.choice([True, False])
        
        if is_baseline_a:
            sample_a = filename
            sample_b = dygrag_filename
            key = "A is Baseline, B is DyGRAG"
        else:
            sample_a = dygrag_filename
            sample_b = filename
            key = "A is DyGRAG, B is Baseline"
            
        survey_data.append({
            'Pair ID': pair_id,
            'Character': char.capitalize(),
            'Emotion/Valence': emotion.capitalize(),
            'Sample A (Link)': sample_a,
            'Sample B (Link)': sample_b,
            'Evaluation Type': 'A/B Blind Test',
            'Internal Key (DO NOT DISTRIBUTE)': key
        })
        
    if not survey_data:
        print("No valid paired audio samples found to construct survey.")
        return
        
    df = pd.DataFrame(survey_data)
    
    output_csv = os.path.join(audio_dir, 'mos_survey.csv')
    df.to_csv(output_csv, index=False)
    
    print(f"\nSuccessfully generated blinded MOS survey: {output_csv}")
    print(f"Generated {len(df)} randomized pair tests.")
    print("\nReminder: DO NOT distribute the 'Internal Key' column to the human panel.")

if __name__ == "__main__":
    main()
