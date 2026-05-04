import json
import os
from typing import Optional, List

from app.core.models.event_wiki import EventWiki
from app.core.story_manager import StoryManager
from app.core.logger import get_logger
from app.core.config import get_llm_model
from adapters.llm_adapter import analyze_text_json

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Directory helpers
# ---------------------------------------------------------------------------

def get_event_wiki_dir(story_uuid: str) -> str:
    path = os.path.join(StoryManager.DATA_DIR, story_uuid, "wiki", "events")
    os.makedirs(path, exist_ok=True)
    return path

def _json_path(story_uuid: str, event_id: str) -> str:
    return os.path.join(get_event_wiki_dir(story_uuid), f"{event_id}.json")

# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

def save_event_wiki(story_uuid: str, event: EventWiki):
    """Persists EventWiki to JSON and Markdown."""
    path = _json_path(story_uuid, event.event_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(event.model_dump(), f, indent=2, ensure_ascii=False)
        
    md_path = os.path.join(get_event_wiki_dir(story_uuid), f"{event.event_id}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(render_event_wiki(event))

def load_event_wiki(story_uuid: str, event_id: str) -> Optional[EventWiki]:
    """Loads an EventWiki from JSON."""
    path = _json_path(story_uuid, event_id)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return EventWiki(**data)
        except Exception as e:
            logger.error(f"Failed to load event wiki {event_id}: {e}")
    return None

def list_event_wikis(story_uuid: str) -> List[str]:
    """Returns a list of event_ids."""
    path = os.path.join(StoryManager.DATA_DIR, story_uuid, "wiki", "events")
    if not os.path.exists(path):
        return []
    return [f[:-5] for f in os.listdir(path) if f.endswith(".json")]

# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def render_event_wiki(event: EventWiki) -> str:
    """Renders EventWiki to Markdown."""
    md = f"# ⚡ {event.display_name}\n\n"
    
    md += f"> *{event.summary}*\n\n"
    
    md += "## ⏱️ Context\n"
    md += f"- **Chapter:** {event.chapter_id}\n"
    if event.story_time_rank is not None:
        md += f"- **Story Time Rank:** {event.story_time_rank}\n"
    if event.arc_id:
        md += f"- **Arc:** `{event.arc_id}`\n"
    md += "\n"
    
    md += "## 🎭 Participants\n"
    if event.participants:
        for p in event.participants:
            char = p.get('character_id', 'Unknown')
            role = p.get('role', 'participant')
            md += f"- **{char}** ({role})\n"
    else:
        md += "None recorded.\n"
    md += "\n"

    md += "## 🔗 Causal Chain\n"
    if event.cause:
        md += f"**Cause:** {event.cause}\n\n"
    
    if event.pre_conditions or event.post_conditions:
        md += "**Conditions:**\n"
        if event.pre_conditions:
            md += f"- Pre: {event.pre_conditions}\n"
        if event.post_conditions:
            md += f"- Post: {event.post_conditions}\n"
        md += "\n"
        
    if event.consequences:
        md += "**Consequences:**\n"
        for c in event.consequences:
            md += f"- {c}\n"
        md += "\n"
        
    if event.after_events:
        md += "**Leads to:** " + ", ".join(f"`{e}`" for e in event.after_events) + "\n\n"
        
    md += "## 🛡️ Meta\n"
    md += f"- **Canonical:** {'Yes' if event.is_canonical else 'No'}\n"
    md += f"- **Spoiler Level:** {event.spoiler_level}\n"
    
    return md

# ---------------------------------------------------------------------------
# LLM Generation
# ---------------------------------------------------------------------------

def build_event_page(story_uuid: str, event_id: str, graph_provider) -> Optional[EventWiki]:
    """Generates an EventWiki from graph data using an LLM."""
    if not graph_provider.graph.has_node(event_id) or graph_provider.graph.nodes[event_id].get("type") != "event":
        logger.warning(f"Event '{event_id}' not found in graph.")
        return None
        
    event_data = graph_provider.graph.nodes[event_id]
    
    # Gather participants and roles from edges
    participants = []
    for u, v, data in graph_provider.graph.in_edges(event_id, data=True):
        if graph_provider.graph.nodes[u].get("type") == "character":
            participants.append({"character_id": u, "role": data.get("role", "participant")})
            
    # Gather causal chain
    before_events = []
    for u, v, data in graph_provider.graph.in_edges(event_id, data=True):
        if data.get("relation") == "causes":
            before_events.append(u)
            
    after_events = []
    for u, v, data in graph_provider.graph.out_edges(event_id, data=True):
        if data.get("relation") == "causes":
            after_events.append(v)
            
    # Gather arc
    arc_id = None
    for u, v, data in graph_provider.graph.in_edges(event_id, data=True):
        if data.get("relation") == "contains" and graph_provider.graph.nodes[u].get("type") == "arc":
            arc_id = u
            break

    context = {
        "event_id": event_id,
        "description": event_data.get("description", ""),
        "pre_conditions": event_data.get("pre_conditions", ""),
        "post_conditions": event_data.get("post_conditions", ""),
        "participants": participants,
        "location": event_data.get("location", ""),
    }
    
    context_str = json.dumps(context, indent=2)

    prompt = f"""
You are the loremaster for a webnovel. Generate a detailed wiki page for the event '{event_id}'.
Here is the context from the knowledge graph:
{context_str}

Return a valid JSON object matching this schema. Preserve the participant roles exactly as provided:
{{
    "display_name": "A catchy title for the event",
    "summary": "Detailed summary of what happened.",
    "cause": "Why this happened, if known.",
    "consequences": ["Result 1", "Result 2"],
    "participants": [{{"character_id": "id", "role": "protagonist/witness/etc"}}]
}}
"""
    result = analyze_text_json(prompt, model=get_llm_model())
    if not result:
        return None

    wiki = EventWiki(
        event_id=event_id,
        display_name=result.get("display_name", event_id),
        summary=result.get("summary", event_data.get("description", "")),
        cause=result.get("cause"),
        consequences=result.get("consequences", []),
        participants=result.get("participants", participants),
        location_id=event_data.get("location"),
        arc_id=arc_id,
        pre_conditions=event_data.get("pre_conditions"),
        post_conditions=event_data.get("post_conditions"),
        before_events=before_events,
        after_events=after_events,
        chapter_id=event_data.get("chapter_id", 0),
        narrative_order=event_data.get("narrative_order", 0),
        timeline_type=event_data.get("timeline_type", "present"),
        story_time_rank=event_data.get("story_time_rank"),
        spoiler_level=event_data.get("spoiler_level", 0),
        is_canonical=event_data.get("is_canonical", True),
        confidence=event_data.get("confidence", 1.0)
    )
    
    save_event_wiki(story_uuid, wiki)
    return wiki
