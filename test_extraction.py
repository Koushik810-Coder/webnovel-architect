import sys
from app.services.extraction import extract_chapter_intelligence

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
    
    result = extract_chapter_intelligence(dummy_text)
    names = result.get("active_character_names", [])
    world_terms = result.get("active_world_terms", [])
    
    print("Extracted Names:", names)
    print("Extracted World Terms:", world_terms)
    
    # "Lady Elara" should become "Elara"
    # "Zelithra Moonfall's" should become "Zelithra Moonfall"
    expected_names = {"John", "Elara", "Vael'Thar", "Zelithra Moonfall"}
    
    expected_world_terms = {"Tier-3 Mage", "Inner Disciple", "Upper Realm", "Azure Cloud Sect"}
    
    # Check for unwanted noise (first day, last night)
    noise_words = {"The", "Beware", "This", "No", "There", "Many", "Only", "Same", "first day", "last night"}
    
    noise_found = [n for n in (names + world_terms) if n.lower() in noise_words]
    missing_expected_names = expected_names - set(names)
    missing_expected_world = expected_world_terms - set(world_terms)
    
    if noise_found:
        print(f"FAILED: Found noise words: {noise_found}")
        sys.exit(1)
        
    if missing_expected_names:
        print(f"FAILED: Missing expected names: {missing_expected_names}")
        sys.exit(1)
        
    if missing_expected_world:
        print(f"FAILED: Missing expected world terms: {missing_expected_world}")
        sys.exit(1)
        
    print("SUCCESS: Extraction test passed!")

if __name__ == "__main__":
    main()
