import yaml
import os
from adapters.tts_adapter import get_tts_engine
from core.ingestion import ingest_chapter_text
from core.graduation import get_graduation_system

# 1. Load Config
def load_config():
    with open("config.yaml") as f:
        return yaml.safe_load(f)

def ensure_output_dir():
    if not os.path.exists("output"):
        os.makedirs("output")

def main():
    print("Initializing Webnovel Architect...")
    config = load_config()
    ensure_output_dir()
    
    # 2. Initialize Engines (The Switchboard)
    print(f"Loading TTS Engine: {config['tts_engine']}...")
    main_tts = get_tts_engine(config["tts_engine"])
    
    print(f"Loading Fallback TTS: {config['fallback_tts']}...")
    backup_tts = get_tts_engine(config["fallback_tts"])
    
    graduation = get_graduation_system()
    
    # Sample Text
    sample_text = """
    "I can't believe we made it," Aria whispered, her voice trembling.
    Kael laughed, a harsh, grating sound. "The night is young, little one."
    The old man in the corner coughed. "Beware the shadows," he warned.
    """
    
    print("\nProcessing Chapter...")
    # 3. Step A: Analyze (Gemini Flash via LiteLLM)
    # Returns list of dicts: {'name': 'Aria', 'line': '...', 'emotion': '...'}
    characters = ingest_chapter_text(sample_text)
    
    print(f"Found {len(characters)} dialogue lines.")
    
    for i, char_data in enumerate(characters):
        name = char_data["name"]
        line = char_data["line"]
        
        # Step B: Graduation Check
        is_main_character = graduation.evaluate_character(name)
        
        filename = f"output/{i}_{name}.wav"
        
        if is_main_character:
            print(f"Speaker: {name} [MAIN] -> Using {config['tts_engine']}")
            # In a real app, 'voice_id' would be looked up from the Graph/Wiki
            main_tts.generate_audio(line, "af_bella", filename)
        else:
            print(f"Speaker: {name} [BACKGROUND] -> Using {config['fallback_tts']}")
            # Default fallback voice
            backup_tts.generate_audio(line, "en-US-GuyNeural", filename)
            
    print("\nChapter Audio Generated in /output folder!")

if __name__ == "__main__":
    main()
