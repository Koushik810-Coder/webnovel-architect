from adapters.graph_adapter import get_graph_engine
from adapters.llm_adapter import analyze_text_json
from app.core.logger import get_logger

logger = get_logger(__name__)

def _call_llm_for_arcs(events_chunk):
    # This is a real implementation using analyze_text_json
    # but the test mocks it.
    prompt = "Group these events into narrative arcs and provide a label and the list of event IDs for each arc:\n\n"
    for e in events_chunk:
        prompt += f"ID: {e['id']}, Description: {e.get('description', '')}, Location: {e.get('location', '')}\n"
    
    # Simple structured prompt
    prompt += "\nRespond ONLY with a JSON array of objects, each containing 'label' (string) and 'event_ids' (list of strings)."
    
    try:
        result = analyze_text_json(prompt)
        if isinstance(result, list):
            return result
        if isinstance(result, dict):
            # Check common keys LLMs use when they decide to wrap the array
            for key in ["arcs", "narrative_arcs", "story_arcs", "events"]:
                if key in result and isinstance(result[key], list):
                    return result[key]
        return []
    except Exception as e:
        logger.error(f"Error parsing arcs from LLM: {e}")
        return []

def detect_arcs(story_uuid: str, every_n: int = 5):
    graph = get_graph_engine(story_uuid)
    
    # Get all events
    events = [
        {"id": n, **d} for n, d in graph.graph.nodes(data=True) 
        if d.get("type") == "event"
    ]
    
    # Sort chronologically
    events.sort(key=lambda x: x.get("chapter_id", 0))
    
    # In a real implementation we might only process the last N chapters,
    # but for simplicity we'll just process everything or the recent ones.
    if not events:
        return []
        
    # Group by location + participant overlap (simplified by passing to LLM)
    # We will pass recent events to LLM
    arcs = _call_llm_for_arcs(events)
    
    for i, arc in enumerate(arcs):
        arc_id = f"arc_{story_uuid}_{len(events)}_{i}"
        label = arc.get("label", "Unknown Arc")
        event_ids = arc.get("event_ids", [])
        
        # Calculate chapter start/end from events
        arc_events = [e for e in events if e["id"] in event_ids]
        if arc_events:
            chapter_start = min(e.get("chapter_id", 0) for e in arc_events)
            chapter_end = max(e.get("chapter_id", 0) for e in arc_events)
        else:
            chapter_start = 0
            chapter_end = 0
            
        graph.add_arc(arc_id, label, event_ids, chapter_start, chapter_end)
        
    graph.save_graph()
    return arcs
