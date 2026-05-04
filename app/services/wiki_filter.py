from typing import List, Optional
from app.core.logger import get_logger
from adapters.graph_adapter import get_graph_engine
from adapters.llm_adapter import analyze_text

logger = get_logger(__name__)

def get_filtered_events(
    story_uuid: str,
    mode: str = "god",
    reader_chapter: int = 999,
    pov_character_id: Optional[str] = None
) -> List[str]:
    """Returns a list of event IDs that are visible under the current filter mode.
    
    Modes:
    - god: All events visible.
    - reader: Hide events where reveal_point > reader_chapter OR spoiler_level >= 2.
    - pov: Show only events the POV character is involved in or knows about.
    """
    graph = get_graph_engine(story_uuid)
    all_events = [n for n, d in graph.graph.nodes(data=True) if d.get("type") == "event"]
    
    if mode == "god":
        return all_events
        
    filtered = []
    
    # Pre-fetch POV knowledge if needed
    pov_known_events = set()
    if mode == "pov" and pov_character_id:
        if graph.graph.has_node(pov_character_id):
            # Known via involvement (Character -> Event edge) or explicit knowledge
            for _, event_id, data in graph.graph.out_edges(pov_character_id, data=True):
                if graph.graph.nodes[event_id].get("type") == "event":
                    # Only exclude if explicitly marked as "unaware_of"
                    if data.get("relation") != "unaware_of":
                        pov_known_events.add(event_id)
            
            # Also include events they are "featured" in (Event -> Character)
            for event_id, _, data in graph.graph.in_edges(pov_character_id, data=True):
                if graph.graph.nodes[event_id].get("type") == "event":
                    pov_known_events.add(event_id)

    for event_id in all_events:
        data = graph.graph.nodes[event_id]
        
        # Reader mode checks
        if mode == "reader":
            reveal_point = data.get("reveal_point", 0)
            spoiler_level = data.get("spoiler_level", 0)
            
            if reveal_point > reader_chapter:
                continue
            # Level 2 is a major twist, fully hidden in reader mode.
            if spoiler_level >= 2:
                continue
                
        # POV mode checks
        if mode == "pov" and pov_character_id:
            if event_id not in pov_known_events:
                continue
                
        filtered.append(event_id)
        
    return filtered

def rewrite_for_spoiler_free(wiki_text: str) -> str:
    """Uses an LLM to re-summarize or obscure spoilers in the assembled wiki text.
    
    Instead of deleting events, it rewrites level-1 spoilers to be vague.
    """
    if not wiki_text or len(wiki_text) < 50:
        return wiki_text
        
    prompt = f"""
    The following is a character wiki page from a novel. 
    Your task is to REWRITE the text to be "spoiler-safe" for a reader who hasn't finished the book.
    
    CRITICAL RULES:
    1. Identify any major plot twists or betrayals and OBSCURE them with vague hints.
       Example: Instead of "Ravi betrays Alice in Chapter 18", write "Ravi's actions later change Alice's trust in him".
    2. If a character dies or a major status change occurs, refer to it as a "turning point" or "shift in circumstances".
    3. Do NOT invent new facts.
    4. Maintain the same general length and tone.
    5. Return the full updated text.
    
    Wiki Text:
    {wiki_text}
    """
    
    try:
        # Use the default model for the rewrite pass.
        return analyze_text(prompt)
    except Exception as e:
        logger.error(f"Spoiler rewrite failed: {e}")
        return wiki_text
