import os
import shutil
import yaml
import asyncio
from adapters.tts_adapter import get_tts_engine
from adapters.graph_adapter import get_graph_engine
from core.graduation import get_graduation_system
from core.ingestion import ingest_chapter_text
from unittest.mock import MagicMock, patch

# Mock the LLM adapter to avoid needing API keys for this test
def mock_analyze_text(text, model="gemini/gemini-1.5-flash"):
    # Return a fake JSON response
    return """
    {
      "dialogue": [
        { "name": "Aria", "line": "I cannot stay here.", "emotion": "sad" },
        { "name": "Thorne", "line": "Then leave.", "emotion": "neutral" }
      ],
      "events": [
        { "description": "Aria confronts Thorne", "characters": ["Aria", "Thorne"] }
      ]
    }
    """

def run_verification():
    print("=== STARTING MODULAR SYSTEM VERIFICATION ===")
    
    # 1. Setup Output
    if os.path.exists("output"):
        shutil.rmtree("output")
    os.makedirs("output")
    print("PASS: 'output' directory cleaned/created.")

    # 2. Mocking
    print("--- Setting up Mocks ---")
    with patch('core.ingestion.analyze_text', side_effect=mock_analyze_text):
        
        # 3. Load Config
        print("--- Loading Config ---")
        if not os.path.exists("config.yaml"):
            print("FAIL: config.yaml missing")
            return
        
        with open("config.yaml") as f:
            config = yaml.safe_load(f)
        print(f"PASS: Config loaded. TTS Engine: {config['tts_engine']}")

        # 4. Ingest Text
        print("--- Testing Ingestion ---")
        sample_text = "Aria looked at the horizon. Thorne grunted."
        characters = ingest_chapter_text(sample_text)
        
        if len(characters) == 2:
            print(f"PASS: Ingested {len(characters)} lines.")
        else:
            print(f"FAIL: Expected 2 lines, got {len(characters)}.")
            return

        # 5. Graph & Graduation
        print("--- Testing Graduation ---")
        grad_system = get_graduation_system()
        graph = get_graph_engine()
        
        # Force Aria to be important
        # In the naive implementation, we might need to manually hack this or rely on previous 'add_character' calls
        # The ingestion loop called 'add_character' for Aria.
        # Let's verify Aria is in the graph
        if graph.graph.has_node("Aria"):
             print("PASS: Aria is in the graph.")
        else:
             print("FAIL: Aria not added to graph.")

        # Check for Events
        event_nodes = [n for n, attr in graph.graph.nodes(data=True) if attr.get("type") == "event"]
        if len(event_nodes) > 0:
            print(f"PASS: Found {len(event_nodes)} events in graph.")
        else:
             print("FAIL: No events found in graph.")

        # Check score
        score = graph.get_character_importance("Aria")
        print(f"INFO: Aria Score: {score}")

        # 6. TTS Generation
        print("--- Testing TTS Generation ---")
        main_tts = get_tts_engine(config["tts_engine"])
        backup_tts = get_tts_engine(config["fallback_tts"])

        # Generate Audio for Aria (Main)
        try:
            filename = "output/test_aria.wav"
            print(f"Attempting to generate {filename} with {config['tts_engine']}...")
            # If Kokoro is missing, this might print a warning or fail depending on implementation
            # We want to see if it runs without crashing
            if asyncio.iscoroutinefunction(main_tts.generate_audio):
                 asyncio.run(main_tts.generate_audio("Test audio", "af_bella", filename))
            else:
                 main_tts.generate_audio("Test audio", "af_bella", filename)
            print("PASS: Main TTS call completed (check console for Mock vs Real).")
        except Exception as e:
            print(f"FAIL: Main TTS threw exception: {e}")

        # Generate Audio for Thorne (Backup)
        try:
            filename = "output/test_thorne.mp3"
            print(f"Attempting to generate {filename} with {config['fallback_tts']}...")
            if asyncio.iscoroutinefunction(backup_tts.generate_audio):
                 asyncio.run(backup_tts.generate_audio("Test audio", "en-US-GuyNeural", filename))
            else:
                 backup_tts.generate_audio("Test audio", "en-US-GuyNeural", filename)
            
            # EdgeTTS is async, verify_modular needs to handle that if the adapter doesn't wrap it well
            # Looking at tts_adapter.py, EdgeAdapter.generate_audio runs asyncio.run internally?
            # Let's check the code... 
            # Yes: EdgeAdapter.generate_audio calls asyncio.run(_run_edge())
            
            print("PASS: Backup TTS call completed.")
        except Exception as e:
            print(f"FAIL: Backup TTS threw exception: {e}")

    print("\n=== VERIFICATION COMPLETE ===")

if __name__ == "__main__":
    run_verification()
