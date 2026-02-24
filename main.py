import yaml
import os
import asyncio
from adapters.tts_adapter import get_tts_engine
from app.services.ingest import ingest_chapter, _runtime_db
from adapters.graph_adapter import get_graph_engine

# 1. Load Config
def load_config():
    with open("config.yaml") as f:
        return yaml.safe_load(f)

def ensure_output_dir():
    if not os.path.exists("output"):
        os.makedirs("output")

def main():
    print("====================================")
    print(" Initializing Webnovel Architect... ")
    print("====================================")
    config = load_config()
    ensure_output_dir()
    
    # 2. Initialize Engines (The Switchboard)
    print(f"\n[SYSTEM] Loading Main TTS Engine: {config['tts_engine']}...")
    main_tts = get_tts_engine(config["tts_engine"])
    
    print(f"[SYSTEM] Loading Fallback TTS: {config['fallback_tts']}...")
    backup_tts = get_tts_engine(config["fallback_tts"])
    
    graph = get_graph_engine()
    
    # Sample Text with new characters
    sample_text = """
    "I can't believe we found the artifact," Elara whispered, the ancient gold glowing in her hands.
    Garrick laughed, a harsh, grating sound echoing in the cavern. "The night is young, little one. The real challenge begins now."
    The old man in the corner coughed, his eyes gleaming. "Beware the shadows, fools," he warned, before vanishing into thin air.
    """
    
    print("\n[PIPELINE] Processing Chapter...")
    # 3. Step A: Analysis & Ingestion
    chapter = ingest_chapter("Chapter 1: The Cavern", sample_text)
    
    # Let's say we process the same chapter multiple times to simulate graduating a character
    print("[PIPELINE] Simulating multiple chapter readings to trigger graduation...")
    for i in range(2, 17):
        ingest_chapter(f"Chapter {i}", sample_text)

    print(f"\n[DATABASE] Characters Discovered:")
    for char_id, char_data in _runtime_db.items():
        print(f" - {char_data.character_id}: Confidence={char_data.confidence_score:.2f}, Voice={char_data.voice_id}")

    # Step C: TTS Generation
    print("\n[AUDIO] Generating Audio for Dialogue Lines...")
    
    # We'll just generate audio for the known dialogue manually for demonstration
    dialogue_lines = [
        {"name": "elara", "line": "I can't believe we found the artifact."},
        {"name": "garrick", "line": "The night is young, little one. The real challenge begins now."},
        {"name": "old_man", "line": "Beware the shadows, fools."}
    ]
    
    for i, char_data in enumerate(dialogue_lines):
        name = char_data["name"]
        line = char_data["line"]
        
        char_runtime = _runtime_db.get(name)
        # If graduated, they have a voice ID.
        has_voice = char_runtime and char_runtime.voice_id is not None
        
        filename = f"output/{i}_{name}.wav"
        
        if has_voice:
            voice = char_runtime.voice_id
            print(f"Speaker: {name} [MAIN CAST] -> Using Main TTS with voice '{voice}'")
            if asyncio.iscoroutinefunction(main_tts.generate_audio):
                 asyncio.run(main_tts.generate_audio(line, voice, filename))
            else:
                 main_tts.generate_audio(line, voice, filename)
        else:
            print(f"Speaker: {name} [BACKGROUND] -> Using Fallback TTS")
            if asyncio.iscoroutinefunction(backup_tts.generate_audio):
                 asyncio.run(backup_tts.generate_audio(line, "en-US-GuyNeural", filename))
            else:
                 backup_tts.generate_audio(line, "en-US-GuyNeural", filename)
            
    print("\n[SUCCESS] Chapter Audio Generated in /output folder!")

if __name__ == "__main__":
    main()
