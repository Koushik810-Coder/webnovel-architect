from adapters.graph_adapter import get_graph_engine
from adapters.llm_adapter import analyze_text
import re

from app.core.logger import get_logger
from app.core.config import get_llm_model
logger = get_logger(__name__)

def query_story(story_uuid: str, query: str, model: str = None) -> str:
    """
    RAG over the story graph using Time-CoT (Time Chain-of-Thought).
    Retrieves Dynamic Event Units (DEUs) from the graph and prompts the LLM chronologically.
    """
    if model is None:
        model = get_llm_model()

    graph = get_graph_engine(story_uuid)

    # 1. Deterministic Entity Extraction from Query
    query_entities = set()
    query_lower = query.lower()
    
    char_nodes = [(n, d) for n, d in graph.graph.nodes(data=True) if d.get("type") == "character"]
    
    for n, d in char_nodes:
        names_to_check = [n.lower()]
        if "display_name" in d:
            names_to_check.append(d["display_name"].lower())
        if "aliases" in d and isinstance(d["aliases"], list):
            names_to_check.extend([a.lower() for a in d["aliases"]])
            
        for name in names_to_check:
            # Word boundary check to prevent partial substring matches
            pattern = r'\b' + re.escape(name) + r'\b'
            if re.search(pattern, query_lower):
                query_entities.add(n)
                break

    # 2. Graph Retrieval
    retrieved_events = []
    seen_events = set()
    
    # 2a. Specific Entity Retrieval
    for entity_id in query_entities:
        if graph.graph.has_node(entity_id):
            for u, event_id, edge_data in graph.graph.out_edges(entity_id, data=True):
                if event_id not in seen_events and graph.graph.has_node(event_id) and graph.graph.nodes[event_id].get("type") == "event":
                    seen_events.add(event_id)
                    event_data = graph.graph.nodes[event_id]
                    involved = [k for k, v in graph.graph.in_edges(event_id) if graph.graph.nodes[k].get("type") == "character"]
                    
                    retrieved_events.append({
                        "chapter_id": event_data.get("chapter_id", 0),
                        "description": event_data.get("description", ""),
                        "pre_conditions": event_data.get("pre_conditions", ""),
                        "post_conditions": event_data.get("post_conditions", ""),
                        "location": event_data.get("location", "Unknown"),
                        "participants": [p.replace("_", " ").title() for p in involved]
                    })
                    
    # 2b. General Question Fallback Retrieval (Token Preserving)
    if not retrieved_events:
        logger.info("No specific entities found in query. Falling back to the 15 most recent global events.")
        
        all_events = [(n, d) for n, d in graph.graph.nodes(data=True) if d.get("type") == "event"]
        if not all_events:
            return "The story graph is currently empty. Please process some chapters first before asking general questions."
            
        # Sort by chapter_id globally
        all_events.sort(key=lambda x: x[1].get("chapter_id", 0), reverse=True)
        recent_events = all_events[:15]
        
        for event_id, event_data in recent_events:
            if event_id not in seen_events:
                seen_events.add(event_id)
                involved = [k for k, v in graph.graph.in_edges(event_id) if graph.graph.nodes[k].get("type") == "character"]
                retrieved_events.append({
                    "chapter_id": event_data.get("chapter_id", 0),
                    "description": event_data.get("description", ""),
                    "pre_conditions": event_data.get("pre_conditions", ""),
                    "post_conditions": event_data.get("post_conditions", ""),
                    "location": event_data.get("location", "Unknown"),
                    "participants": [p.replace("_", " ").title() for p in involved]
                })
    if not retrieved_events:
        return f"I couldn't find any recorded events in the story graph."


    # 3. Time-CoT Ordering
    # Sort chronologically by chapter_id
    retrieved_events.sort(key=lambda x: x["chapter_id"])
    
    # 4. Construct Prompt
    timeline_str = "Story Timeline (Chronological Context):\n"
    for ev in retrieved_events:
        chap = ev['chapter_id']
        desc = ev['description']
        pre = ev['pre_conditions']
        post = ev['post_conditions']
        loc = ev['location']
        parts = ", ".join(ev['participants'])
        
        timeline_str += f"""
--- Chapter {chap} ---
Location: {loc}
Involved: {parts}
Before: {pre}
Action: {desc}
Result / After: {post}
"""

    prompt = f"""
You are the architect and loremaster of a serialized web novel.
The user has asked a question about the story.

Use the provided chronological timeline of retrieved Dynamic Event Units (DEUs) to answer their question. 
Reason step-by-step through the timeline (Time-CoT) to understand how states changed over time.
If the answer is not in the timeline, say you don't know based on the current context.

{timeline_str}

User Question: {query}

Reason through the context chronologically and then provide a clear, narrative answer.
"""

    # 5. LLM Generation
    response = analyze_text(prompt, model=model)
    
    # Primary model fallback to Groq to prevent RAG downtime
    if (response is None or response.startswith("API Fallback:")) and not model.startswith("groq"):
        logger.warning(f"Primary model {model} failed. Falling back to Groq as a safeguard...")
        fallback_model = "groq/llama-3.1-8b-instant"
        response = analyze_text(prompt, model=fallback_model)
        
    return response
