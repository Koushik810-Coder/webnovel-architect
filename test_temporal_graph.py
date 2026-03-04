import os
import shutil
from adapters.graph_adapter import GraphProvider

def test():
    story_uuid = "test_temporal_graph"
    # cleanup first
    test_dir = f"data/{story_uuid}"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
        
    gp = GraphProvider(story_uuid)
    
    # Character A appears in Chapter 1 only
    gp.add_character("char_a", {"display_name": "Character A"})
    gp.add_event("event_1", "Intro", ["char_a"], chapter_id=1)
    
    # Character B appears in Chapter 10 only
    gp.add_character("char_b", {"display_name": "Character B"})
    gp.add_event("event_10", "Later Intro", ["char_b"], chapter_id=10)
    
    # Both have 1 event. Without decay, they should have equal importance.
    imp_a_no_decay = gp.get_character_importance("char_a", current_chapter=10, decay_rate=0)
    imp_b_no_decay = gp.get_character_importance("char_b", current_chapter=10, decay_rate=0)
    
    # With decay, B should have much higher importance than A
    imp_a_decay = gp.get_character_importance("char_a", current_chapter=10, decay_rate=0.2)
    imp_b_decay = gp.get_character_importance("char_b", current_chapter=10, decay_rate=0.2)
    
    print(f"No Decay -> A: {imp_a_no_decay:.4f}, B: {imp_b_no_decay:.4f}")
    assert abs(imp_a_no_decay - imp_b_no_decay) < 0.0001, "Should be identical without decay"
    
    print(f"With Decay -> A: {imp_a_decay:.4f}, B: {imp_b_decay:.4f}")
    assert imp_b_decay > imp_a_decay, "B should be higher than A with decay"
    
    print("Test passed.")

if __name__ == "__main__":
    test()
