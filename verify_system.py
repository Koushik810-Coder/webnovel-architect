import os
import shutil
from app.services.ingest import ingest_chapter, _runtime_db
from app.services.wiki import WIKI_DIR

def run_verification():
    print("=== STARTING SYSTEM VERIFICATION ===")
    
    # Clean state
    if os.path.exists(WIKI_DIR):
        shutil.rmtree(WIKI_DIR)
    
    # Test Data: Chapter 1
    # "Aria" is introduced. "Thorne" is introduced.
    print("\n--- Ingesting Chapter 1 ---")
    text_c1 = """
    Aria looked at the horizon. "I cannot stay here," she whispered.
    Thorne grunted. "Then leave," he said. Thorne did not care.
    Aria turned back.
    """
    ingest_chapter("The Beginning", text_c1)
    
    # Check State
    aria = _runtime_db.get("aria")
    thorne = _runtime_db.get("thorne")
    
    if not aria or not thorne:
        print("FAIL: Characters not extracted.")
        return
        
    print(f"PASS: Extracted Aria (Conf: {aria.confidence_score:.2f}) & Thorne (Conf: {thorne.confidence_score:.2f})")
    
    # Check Wiki Creation
    if os.path.exists(os.path.join(WIKI_DIR, "aria.md")):
        print("PASS: Wiki file for Aria created.")
    else:
        print("FAIL: Wiki file for Aria missing.")

    # Test Data: Chapter 2 -> Graduation Push
    # We spam appearances to trigger high confidence
    print("\n--- Ingesting Chapter 2 (Graduation Push) ---")
    text_c2 = """
    Aria fought hard. Aria cast a spell. Aria shouted, "Fire!"
    Aria avoided the attack. Aria was determined.
    "I will win," Aria declared.
    """
    # Simulate many chapters or heavy usage to boost score fast for test
    # Our ingest increments by +0.05 per chunk, but let's just run it multiple times to simulate time
    for i in range(15):
        ingest_chapter(f"Training Day {i}", text_c2)
        
    aria = _runtime_db.get("aria")
    print(f"Aria Confidence: {aria.confidence_score:.2f}")
    
    if aria.voice_id:
        print(f"PASS: Aria Graduated! Voice ID: {aria.voice_id}")
    else:
        print("FAIL: Aria did not graduate (Voice ID is None).")

if __name__ == "__main__":
    try:
        run_verification()
    except Exception as e:
        print(f"ERROR: {e}")
