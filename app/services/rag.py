from typing import List, Dict, Any
from adapters.graph_adapter import get_graph_engine
from adapters.llm_adapter import analyze_text
import spacy

from app.core.logger import get_logger
logger = get_logger(__name__)

try:
    nlp = spacy.load("en_core_web_sm", disable=["parser", "tagger", "lemmatizer", "attribute_ruler", "tok2vec"])
except:
    nlp = None

def query_story(story_uuid: str, query: str, model: str = "gemini/gemini-2.5-flash") -> str:
    """
    RAG over the story graph using Time-CoT (Time Chain-of-Thought).
    Retrieves Dynamic Event Units (DEUs) from the graph and prompts the LLM chronologically.
    """
    if nlp is None:
        return "Failed to start RAG engine: spaCy model not loaded."

    # 1. Entity Extraction from Query
    doc = nlp(query)
    query_entities = set()
    for ent in doc.ents:
        if ent.label_ in ["PERSON", "ORG", "GPE", "LOC", "FAC"]:
            clean_name = ent.text.strip().lower().replace(" ", "_").replace("'s", "")
            query_entities.add(clean_name)

    graph = get_graph_engine(story_uuid)

    # Simple fallback: if no entities found by NER, just tokenize and check for capitalized words
    if not query_entities:
        words = query.split()
        for i, w in enumerate(words):
            if w[0].isupper() and i > 0: # Ignore first word of sentence
                clean_name = w.strip('?.,!"\'').lower()
                query_entities.add(clean_name)

    # General Question Fallback (e.g., "Who is the main character?", "Summarize the story")
    if not query_entities:
        logger.info("No specific entities found in query. Falling back to top 5 characters by graph prominence.")
        char_nodes = [n for n, d in graph.graph.nodes(data=True) if d.get("type") == "character"]
        
        if not char_nodes:
            return "The story graph is currently empty. Please process some chapters first before asking general questions."
            
        # Sort characters by their total degree (number of connected events)
        sorted_chars = sorted(char_nodes, key=lambda c: graph.graph.degree(c), reverse=True)
        import itertools
        top_chars = list(itertools.islice(sorted_chars, 5))
        
        for c in top_chars:
            query_entities.add(c)

    # 2. Graph Retrieval
    retrieved_events = []
    
    # Track which event IDs we already grabbed to avoid duplicates
    seen_events = set()
    
    for entity_id in query_entities:
        # Check both the canonical character and any variants
        # In a real system, you'd use the alias resolver here on query entities too.
        if graph.graph.has_node(entity_id):
            # Characters have outgoing edges to events they participated in
            for u, event_id, edge_data in graph.graph.out_edges(entity_id, data=True):
                if event_id not in seen_events and graph.graph.has_node(event_id) and graph.graph.nodes[event_id].get("type") == "event":
                    seen_events.add(event_id)
                    event_data = graph.graph.nodes[event_id]
                    # Also find who else was in this event
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
        return f"I couldn't find any recorded events involving: {', '.join([e.title() for e in query_entities])} in the story graph."

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
