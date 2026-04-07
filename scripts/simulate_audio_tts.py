import os
import sys

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from adapters.tts_adapter import KokoroAdapter

def simulate_event_prosody(engine, output_dir, char_name, voice_id, emotion, text, baseline_speed=1.0, dygrag_speed=1.0):
    """
    Generates A/B audio files using a strict naming convention.
    Baseline: vanilla TTS.
    DyGRAG: dynamically speed-modulated based on valence.
    """
    baseline_filename = f"{char_name}_{emotion}_baseline.wav"
    dygrag_filename = f"{char_name}_{emotion}_dygrag.wav"
    
    baseline_path = os.path.join(output_dir, baseline_filename)
    dygrag_path = os.path.join(output_dir, dygrag_filename)
    
    print(f"Generating {baseline_filename} (Speed: {baseline_speed})...")
    engine.generate_audio(text, voice_id, baseline_path, speed=baseline_speed)
    
    print(f"Generating {dygrag_filename} (Speed: {dygrag_speed})...")
    engine.generate_audio(text, voice_id, dygrag_path, speed=dygrag_speed)

def main():
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'output', 'audio_samples'))
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize Kokoro
    try:
        engine = KokoroAdapter()
    except Exception as e:
        print(f"Failed to load Kokoro: {e}")
        return
        
    print("\n--- Generating Audio Samples for MOS Panel ---")

    # Scenario 1: Combat/Hostile
    simulate_event_prosody(
        engine=engine,
        output_dir=output_dir,
        char_name="zorian",
        voice_id="am_adam", # High-quality default male voice
        emotion="hostile",
        text="I am going to throw you out the window right now!",
        baseline_speed=1.0,
        dygrag_speed=1.25 # Hostile/combat graph edges trigger 25% faster speech
    )
    
    # Scenario 2: Neutral/Conversational
    simulate_event_prosody(
        engine=engine,
        output_dir=output_dir,
        char_name="taiven",
        voice_id="af_bella", 
        emotion="neutral",
        text="You're Zorian, aren't you? It's nice to finally meet you.",
        baseline_speed=1.0,
        dygrag_speed=1.0   # Neutral remains unchanged
    )
    
    # Scenario 3: Exhausted/Betrayal (Slow, dramatic)
    simulate_event_prosody(
        engine=engine,
        output_dir=output_dir,
        char_name="zach",
        voice_id="am_michael", 
        emotion="betrayal",
        text="How could you do this? After everything we built together...",
        baseline_speed=1.0,
        dygrag_speed=0.85 # Betrayal/Sad graph nodes slow speech by 15%
    )
    
    print(f"\nSuccessfully generated {3 * 2} audio samples in {output_dir}")

if __name__ == "__main__":
    main()
