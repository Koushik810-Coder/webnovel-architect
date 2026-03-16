import sys
import json
import os

# Add the parent directory (project root) to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.extraction import extract_chapter_intelligence_llm

env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env')
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                os.environ.setdefault(key.strip(), val.strip().strip('"\''))

def main():
    dummy_text = """
    The sun set over the horizon. Beware of the shadows!
    John walked into the tavern, looking for Lady Elara. 
    Suddenly, Vael'Thar the ancient wizard appeared. 
    "This is Zelithra Moonfall's domain," he proclaimed loudly.
    No one expected a King to arrive like this.
    There were Many people, but Only the Same few spoke.
    The first day was peaceful. Last night was a nightmare.
    He became a Tier-3 Mage after consulting the Inner Disciple.
    They traveled from the Upper Realm to join the Azure Cloud Sect.
    """
    
    print("Testing LLM Extraction...")
    try:
        result = extract_chapter_intelligence_llm(dummy_text)
        print(json.dumps(result, indent=2))
        
        names = result.get("active_character_names", [])
        world_terms = result.get("active_world_terms", [])
        dialogue = result.get("dialogue_count_total", 0)
        
        print("\nExtracted Names:", names)
        print("Extracted World Terms:", world_terms)
        print("Dialogue Count:", dialogue)
        print("SUCCESS: LLM Extraction test completed without errors.")
    except Exception as e:
        print(f"FAILED: Error during extraction - {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
