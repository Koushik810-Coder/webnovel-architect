from adapters.graph_adapter import get_graph_engine
from adapters.llm_adapter import analyze_text, analyze_text_json
import re

from app.core.logger import get_logger
from app.core.config import get_llm_model
from app.services.wiki_filter import get_filtered_events, rewrite_for_spoiler_free
from typing import Optional, List

logger = get_logger(__name__)

def query_story(
    story_uuid: str, 
    query: str, 
    model: str = None,
    mode: str = "god",
    reader_chapter: int = 999,
    pov_character_id: Optional[str] = None,
    chat_history: Optional[List[dict]] = None
) -> str:

    """
    RAG over the story graph using Time-CoT (Time Chain-of-Thought).
    Retrieves Dynamic Event Units (DEUs) from the graph and prompts the LLM chronologically.
    """
    if model is None:
        model = get_llm_model()

    graph = get_graph_engine(story_uuid)

    # 1. Intent Extraction via LLM
    # Pass chat history context so it can resolve pronouns or implicit references like "what about his sword?"
    history_context = ""
    if chat_history:
        # Just grab the last 2 interactions to give the LLM some context
        recent = chat_history[-4:]
        history_context = "Recent conversation context:\n" + "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent]) + "\n\n"
        
    intent_prompt = f"{history_context}Extract the core entities from this new query:\n'{query}'\nRespond ONLY with a JSON object containing arrays for 'characters', 'locations', and 'concepts'."
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
                
    # Also attempt to extract entities from intent if the deterministic check missed them
    for char_name in intent.get("characters", []):
        for n, d in char_nodes:
            if char_name.lower() in n.lower() or (d.get("display_name") and char_name.lower() in d["display_name"].lower()):
                query_entities.add(n)

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
    response = analyze_text(prompt, model=model, chat_history=chat_history)

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

    retrieved_events: list = []
    seen_events: set = set()

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
    "appearance": "A single cohesive prose paragraph covering ALL confirmed physical traits: hair, eyes, height, build, skin tone, attire, and any distinguishing marks.",
    "appearance_traits": {{
        "hair_color": "exact colour mentioned in the text — null if never described",
        "hair_style": "e.g. long and wavy, cropped short — null if unknown",
        "eye_color": "exact colour — null if unknown",
        "skin_tone": "e.g. pale, olive, dark — null if unknown",
        "height": "e.g. tall, average, short — null if unknown",
        "build": "e.g. lean, muscular, slender — null if unknown",
        "distinguishing_marks": "scars, tattoos, birthmarks, etc. — null if none mentioned",
        "typical_attire": "clothing style or colours usually worn — null if unknown"
    }},
    "appearance_change_note": "One-sentence reason if any appearance trait changed across the timeline, or null.",
    "personality_traits": ["Trait 1", "Trait 2", "Trait 3"],
    "notable_quirks": ["Quirk 1", "Quirk 2"],
    "abilities": ["Powers, combat techniques, innate skills, or magic systems they demonstrably use"],
    "goals": ["Concrete objectives, ambitions, or driving motivations — including hidden ones if revealed"],
    "weaknesses": ["Physical limitations, emotional vulnerabilities, power suppression, fears, or curses"],
    "key_facts": [
        "All other wiki-worthy facts: origin, faction rank, titles earned, past crimes, prophecies about them, rank-ups, secrets discovered, transformations, oaths, losses, key achievements"
    ],
    "relationships": [{{"target_id": "character_id", "relation": "Rival", "context": "Brief context for the relationship"}}],
    "new_timeline_events": [{{"chapter": 5, "event": "Description of what happened to this character"}}]
}}

EXTRACTION RULES:
- FACTUAL ONLY: Populate only from the timeline events and existing wiki. Never invent.
- NULL vs EMPTY: Unknown scalars → null. Empty lists → []. Never use placeholder strings.
- APPEARANCE: Only confirmed traits. Reflect the LATEST value if a trait changed; explain in appearance_change_note.
- ABILITIES: Be specific (e.g. "Spatial Compression Technique", not just "a technique").
- GOALS: State concrete objectives. Distinguish overt goals from hidden ones where relevant.
- WEAKNESSES: Physical limits, emotional vulnerabilities, suppressed powers, curses, known fears.
- KEY FACTS: Anything wiki-worthy that doesn't fit other fields. Be comprehensive — this is the catch-all.
"""


    try:
        profile = analyze_text_json(prompt, model=model)
        if profile is None or (isinstance(profile, dict) and profile.get("error")):
            raise ValueError(f"LLM returned empty or malformed JSON for {character_name}.")
            
        if profile and mode == "reader":
            # Apply spoiler rewrite to the narrative fields
            if "short_description" in profile:
                profile["short_description"] = rewrite_for_spoiler_free(profile["short_description"])
            if "synopsis" in profile:
                profile["synopsis"] = rewrite_for_spoiler_free(profile["synopsis"])
        
        logger.info(f"RAG enrichment produced profile for '{character_name}' from {len(retrieved_events)} events.")
        return profile
    except Exception as e:
        logger.error(f"RAG enrichment failed for '{character_name}': {e}")
        raise ValueError(f"RAG enrichment failed for '{character_name}': {e}") from e

def query_story_with_filter(
    story_uuid: str, 
    nl_query: str, 
    model: str = None,
    mode: str = "god",
    reader_chapter: int = 999,
    pov_character_id: Optional[str] = None
) -> str:
    """
    Translates a natural language query into graph filter operations,
    retrieves the matching events, and generates a dynamic wiki projection.
    (Phase 2.8: Wiki as a Query Language)
    """
    if model is None:
        model = get_llm_model()

    from adapters.llm_adapter import analyze_text_json, analyze_text
    graph = get_graph_engine(story_uuid)

    # 1. Intent Parsing
    intent_prompt = f"""
You are a graph query parser. The user wants a specific slice of the story's history.
Query: "{nl_query}"

Parse this query into the following JSON schema:
{{
    "target_characters": ["Name1", "Name2"], // Characters explicitly asked about
    "target_locations": ["Location"], // Locations explicitly asked about
    "target_arcs": ["Arc Name"], // Arcs explicitly asked about
    "time_bound": {{
        "operator": "before" | "after" | "during" | null,
        "event_concept": "short description of the pivot event (e.g. 'the betrayal')" | null
    }},
    "pov_character": "Name" | null, // If the user asks for someone's specific perspective
    "hidden_knowledge_only": true | false // If they ask for secrets, hidden truth, or non-canonical events
}}
Respond ONLY with valid JSON.
"""
    try:
        intent = analyze_text_json(intent_prompt, model=model) or {}
    except Exception:
        intent = {}

    target_characters = [c.lower() for c in intent.get("target_characters", [])]
    target_locations = [l.lower() for l in intent.get("target_locations", [])]
    target_arcs = [a.lower() for a in intent.get("target_arcs", [])]
    time_bound = intent.get("time_bound", {})
    pov_char_intent = intent.get("pov_character")
    hidden_only = intent.get("hidden_knowledge_only", False)

    # Override POV if the query explicitly requested a perspective
    effective_pov = pov_char_intent.lower() if pov_char_intent else pov_character_id
    
    # We must match the effective_pov to a real node ID if it's a string
    effective_pov_id = None
    if effective_pov:
        for n, d in graph.graph.nodes(data=True):
            if d.get("type") == "character":
                names = [n.lower()]
                if "display_name" in d: names.append(d["display_name"].lower())
                if effective_pov in names or effective_pov in n.lower():
                    effective_pov_id = n
                    break
        if not effective_pov_id:
            effective_pov_id = pov_character_id # fallback

    visible_event_ids = set(get_filtered_events(story_uuid, mode, reader_chapter, effective_pov_id))
    
    all_events = [(n, d) for n, d in graph.graph.nodes(data=True) if d.get("type") == "event" and n in visible_event_ids]
    
    # 2. Find Time Pivot
    pivot_rank = None
    if time_bound and time_bound.get("operator") and time_bound.get("event_concept"):
        concept = time_bound["event_concept"].lower()
        # Simple search for the pivot event
        best_match = None
        for n, d in all_events:
            desc = d.get("description", "").lower()
            title = d.get("display_name", n).lower()
            if concept in desc or concept in title:
                best_match = d
                break
        if best_match:
            pivot_rank = best_match.get("story_time_rank", best_match.get("chapter_id", 0))

    # 3. Filter Events
    filtered_events = []
    
    char_nodes_lower = {n: [n.lower(), d.get("display_name", "").lower()] for n, d in graph.graph.nodes(data=True) if d.get("type") == "character"}
    
    for event_id, event_data in all_events:
        # Check hidden only
        if hidden_only:
            if event_data.get("is_canonical", True) and event_data.get("spoiler_level", 0) == 0:
                continue
                
        # Check time bounds
        if pivot_rank is not None:
            ev_rank = event_data.get("story_time_rank", event_data.get("chapter_id", 0))
            op = time_bound["operator"]
            if op == "before" and ev_rank >= pivot_rank: continue
            if op == "after" and ev_rank <= pivot_rank: continue
            if op == "during" and ev_rank != pivot_rank: continue

        # Check entity inclusion (Characters, Locations, Arcs)
        keep = False
        
        # If no specific targets, we keep it (unless it was filtered out by time/hidden)
        if not target_characters and not target_locations and not target_arcs:
            keep = True
        else:
            # Characters
            if target_characters:
                involved = [k for k, v in graph.graph.in_edges(event_id) if graph.graph.nodes[k].get("type") == "character"]
                involved_lower = []
                for inv in involved:
                    involved_lower.extend(char_nodes_lower.get(inv, [inv.lower()]))
                
                for tc in target_characters:
                    if any(tc in il for il in involved_lower):
                        keep = True
                        break
            
            # Locations
            if not keep and target_locations:
                loc = event_data.get("location", "").lower()
                for tl in target_locations:
                    if tl in loc:
                        keep = True
                        break
            
            # Arcs (check if event is in the specified arc)
            if not keep and target_arcs:
                for u, v, edata in graph.graph.in_edges(event_id, data=True):
                    if edata.get("relation") == "contains" and graph.graph.nodes[u].get("type") == "arc":
                        arc_name = graph.graph.nodes[u].get("label", u).lower()
                        for ta in target_arcs:
                            if ta in arc_name:
                                keep = True
                                break

        if keep:
            involved = [k for k, v in graph.graph.in_edges(event_id) if graph.graph.nodes[k].get("type") == "character"]
            filtered_events.append({
                "chapter_id": event_data.get("chapter_id", 0),
                "description": event_data.get("description", ""),
                "location": event_data.get("location", "Unknown"),
                "participants": [p.replace("_", " ").title() for p in involved]
            })

    if not filtered_events:
        return f"No events matched the query criteria: '{nl_query}'. The events might be hidden by your current Reader/POV perspective, or they haven't occurred yet."

    # 4. Generate Projection
    filtered_events.sort(key=lambda x: x["chapter_id"])
    
    timeline_str = ""
    for ev in filtered_events:
        timeline_str += f"- [Ch {ev['chapter_id']}] At {ev['location']} with {', '.join(ev['participants'])}: {ev['description']}\n"

    prompt = f"""
You are the loremaster of a serialized web novel.
The user submitted a complex query: "{nl_query}"

Based on this query, the system filtered the knowledge graph and retrieved the following specific events:
{timeline_str}

Write a comprehensive, engaging Wiki Projection that answers their query directly using ONLY the retrieved events.
Format it beautifully in Markdown with appropriate headings, bold text, and bullet points if necessary.
"""
    result = analyze_text(prompt, model=model)
    return result
