import os
import asyncio
from app.core.story_manager import StoryManager
from app.services.ingest import ingest_chapter, load_runtime
from adapters.tts_adapter import get_tts_engine

def main():
    print("====================================")
    print(" Initializing Webnovel Architect... ")
    print("====================================")
    
    # 1. Create a transient test story
    story_uuid = StoryManager.create_story("CLI Demo Story")
    print(f"[SYSTEM] Created Demo Story: {story_uuid}")
    
    # 2. Sample Text with characters
    sample_text = """
    "I can't believe we found the artifact," Elara whispered, the ancient gold glowing in her hands.
    Garrick laughed, a harsh, grating sound echoing in the cavern. "The night is young, little one. The real challenge begins now."
    The old man in the corner coughed, his eyes gleaming. "Beware the shadows, fools," he warned, before vanishing into thin air.
    """
    
    print("\n[PIPELINE] Processing Chapter 1...")
    # 3. Ingestion
    ingest_chapter(story_uuid, "Chapter 1: The Cavern", sample_text)
    
    print("[PIPELINE] Simulating multiple chapter readings to trigger graduation...")
    for i in range(2, 6):
        ingest_chapter(story_uuid, f"Chapter {i}", sample_text)

    # 4. Read Runtime DB
    _, runtime_db = load_runtime(story_uuid)
    print("\n[DATABASE] Characters Discovered:")
    for char_id, char_data in runtime_db.items():
        grad_status = "[MAIN CAST]" if char_data.voice_id else "[BACKGROUND]"
        print(f" - {char_data.character_id} {grad_status}: Confidence={char_data.confidence_score:.3f}, Mentions={char_data.mention_count}, Voice={char_data.voice_id}")

    # 5. TTS Demo Generation Setup
    print("\n[AUDIO] Audio synthesis available via Streamlit UI.")
    print(f"To synthesize audio, run: streamlit run app_ui.py")
    print("====================================")

if __name__ == "__main__":
    main()
