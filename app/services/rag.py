from adapters.graph_adapter import get_graph_engine
from adapters.llm_adapter import analyze_text, analyze_text_json
import re

from app.core.logger import get_logger
from app.core.config import get_llm_model
from app.services.wiki_filter import get_filtered_events, rewrite_for_spoiler_free
from typing import Optional, List

def query_story(
    story_uuid: str, 
    query: str, 
    model: str = None,
    mode: str = "god",
    reader_chapter: int = 999,
    pov_character_id: Optional[str] = None
) -> str:

    """
    RAG over the story graph using Time-CoT (Time Chain-of-Thought).
    Retrieves Dynamic Event Units (DEUs) from the graph and prompts the LLM chronologically.
    """
    if model is None:
        model = get_llm_model()

    graph = get_graph_engine(story_uuid)

    # 1. Intent Extraction via LLM
    intent_prompt = f"Extract the core entities from this query:\n'{query}'\nRespond ONLY with a JSON object containing arrays for 'characters', 'locations', and 'concepts'."
    try:
        intent = analyze_text_json(intent_prompt, model=model) or {}
    except Exception:
        intent = {}
        
    query_locations = set(intent.get("locations", []))

    # 1b. Deterministic Entity Extraction from Query
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
    # Pre-calculate the whitelist of visible events for the current mode/context
    visible_event_ids = set(get_filtered_events(story_uuid, mode, reader_chapter, pov_character_id))
    
    retrieved_events = []
    seen_events = set()
    
    # 2a. Specific Entity Retrieval
    for entity_id in query_entities:
        if graph.graph.has_node(entity_id):
            for u, event_id, edge_data in graph.graph.out_edges(entity_id, data=True):
                if event_id in visible_event_ids and event_id not in seen_events and graph.graph.has_node(event_id) and graph.graph.nodes[event_id].get("type") == "event":
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
                    
    # 2b. Location/Scene Retrieval
    scene_nodes = [(n, d) for n, d in graph.graph.nodes(data=True) if d.get("type") == "scene"]
    for loc in query_locations:
        loc_lower = loc.lower()
        for scene_id, scene_data in scene_nodes:
            if loc_lower in scene_data.get("location", "").lower():
                for event_id, _, edge_data in graph.graph.in_edges(scene_id, data=True):
                    if edge_data.get("relation") == "OCCURS_IN" and event_id in visible_event_ids and event_id not in seen_events:
                        if graph.graph.has_node(event_id) and graph.graph.nodes[event_id].get("type") == "event":
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

    # 2c. General Question Fallback Retrieval (Token Preserving)
    if not retrieved_events:
        logger.info("No specific entities found in query. Falling back to the 15 most recent global events.")
        
        all_events = [(n, d) for n, d in graph.graph.nodes(data=True) if d.get("type") == "event"]
        if not all_events:
            return "The story graph is currently empty. Please process some chapters first before asking general questions."
            
        # Sort by chapter_id globally
        all_events.sort(key=lambda x: x[1].get("chapter_id", 0), reverse=True)
        recent_events = [e for e in all_events if e[0] in visible_event_ids][:15]
        
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
        return "I couldn't find any recorded events in the story graph."


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
You are allowed to be creative and provide an engaging, narrative response. You can extrapolate, interpret character motivations, and weave the events together creatively, as long as it aligns with the core facts in the timeline.

{timeline_str}

User Question: {query}

Reason through the context chronologically and then provide a clear, narrative answer.
"""

    # 5. LLM Generation
    # analyze_text() handles its own Groq fallback internally — no need to repeat it here.
    response = analyze_text(prompt, model=model)

    # 6. Optional Spoiler Rewrite Pass
    if mode == "reader" and response:
        logger.info("Applying spoiler-safe rewrite pass to RAG response.")
        response = rewrite_for_spoiler_free(response)

    return response


def query_character_profile(
    story_uuid: str, 
    character_id: str, 
    character_name: str, 
    model: str = None, 
    existing_wiki_json: str = None,
    mode: str = "god",
    reader_chapter: int = 999,
    pov_character_id: Optional[str] = None
) -> dict:
    """
    RAG-powered character profile enrichment using Time-CoT.

    Retrieves ALL events this character participated in across every ingested
    chapter, reasons through them chronologically, and returns a structured
    dict of wiki fields (same schema as update_character_profile).

    This produces far richer profiles than the chapter-by-chapter extractor
    because it reasons over the full story arc in a single pass.
    """
    if model is None:
        model = get_llm_model()

    from adapters.llm_adapter import analyze_text_json

    graph = get_graph_engine(story_uuid)

    # Get the whitelist of visible events
    visible_event_ids = set(get_filtered_events(story_uuid, mode, reader_chapter, pov_character_id))

    if graph.graph.has_node(character_id):
        for _, event_id, _ in graph.graph.out_edges(character_id, data=True):
            node_data = graph.graph.nodes.get(event_id, {})
            if event_id in visible_event_ids and event_id not in seen_events and node_data.get("type") == "event":
                seen_events.add(event_id)
                involved = [
                    k for k, _ in graph.graph.in_edges(event_id)
                    if graph.graph.nodes[k].get("type") == "character"
                ]
                retrieved_events.append({
                    "chapter_id": node_data.get("chapter_id", 0),
                    "description": node_data.get("description", ""),
                    "pre_conditions": node_data.get("pre_conditions", ""),
                    "post_conditions": node_data.get("post_conditions", ""),
                    "location": node_data.get("location", "Unknown"),
                    "participants": [p.replace("_", " ").title() for p in involved],
                })

    if not retrieved_events:
        logger.warning(f"No events found in graph for character '{character_id}' — skipping RAG enrichment.")
        return {}

    # --- Time-CoT ordering ---
    retrieved_events.sort(key=lambda x: x["chapter_id"])

    timeline_str = f"Full Story Timeline for {character_name} (Chronological):\n"
    for ev in retrieved_events:
        timeline_str += f"""
--- Chapter {ev['chapter_id']} | Location: {ev['location']} ---
Participants: {', '.join(ev['participants'])}
Before: {ev['pre_conditions']}
Action: {ev['description']}
After: {ev['post_conditions']}
"""

    existing_context = ""
    if existing_wiki_json:
        existing_context = f"""
Here is their CURRENT wiki page information in JSON format:
---
{existing_wiki_json}
---
IMPORTANT: You MUST merge your findings from the timeline with the current wiki information above. Do NOT discard existing information (like appearances, traits, or past relationships) unless it is explicitly contradicted by the timeline. Combine them to form a cohesive, updated profile.
"""

    prompt = f"""
You are the loremaster of a serialized web novel. Your task is to build a complete, accurate wiki profile for the character '{character_name}' by reasoning through every event they have been involved in, from their first appearance to their most recent.
{existing_context}

{timeline_str}

Based on ALL of the above events and the current wiki (if provided), produce a comprehensive character profile as a JSON object. 

CRITICAL CONSTRAINTS:
1. FACTUAL ACCURACY: Only extract facts explicitly stated or directly demonstrated in the provided timeline events, or preserved from the existing wiki.
2. NO HALLUCINATIONS: Do not invent, assume, or guess names, places, relationships, traits, ages, or appearances.
3. MISSING DATA: If a detail is missing or unknown based strictly on the timeline or existing wiki, leave it as null or an empty list. Do NOT use placeholders like "Unknown" or "Not recorded".

Respond ONLY with a valid JSON object matching this exact schema:
{{
    "short_description": "A single punchy sentence (≤20 words) describing who this character IS.",
    "synopsis": "A cohesive, chronological narrative biography covering their full story arc so far.",
    "status": "Alive, Deceased, Missing, or null.",
    "age": "Their stated or inferred age as a string — or null.",
    "gender": "Their gender — or null.",
    "species": "Their race or species — or null.",
    "role": "Protagonist, Antagonist, Supporting, Mentor, etc. — or null.",
    "affiliations": ["Faction A", "Group B"],
    "appearance": "A cohesive physical description inferred from context.",
    "personality_traits": ["Trait 1", "Trait 2", "Trait 3"],
    "notable_quirks": ["Quirk 1", "Quirk 2"],
    "relationships": [{{"target_id": "character_id", "relation": "Rival", "context": "Brief context for the relationship"}}],
    "new_timeline_events": [{{"chapter": 5, "event": "Description of what happened to this character"}}]
}}
"""


    try:
        profile = analyze_text_json(prompt, model=model)
        if profile and mode == "reader":
            # Apply spoiler rewrite to the narrative fields
            if "short_description" in profile:
                profile["short_description"] = rewrite_for_spoiler_free(profile["short_description"])
            if "synopsis" in profile:
                profile["synopsis"] = rewrite_for_spoiler_free(profile["synopsis"])
        
        if profile:
            logger.info(f"RAG enrichment produced profile for '{character_name}' from {len(retrieved_events)} events.")
        return profile or {}
    except Exception as e:
        logger.error(f"RAG enrichment failed for '{character_name}': {e}")
        return {}
