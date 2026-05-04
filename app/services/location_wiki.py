import json
import os
from typing import Optional, List

from app.core.models.location_wiki import LocationWiki
from app.core.story_manager import StoryManager
from app.core.logger import get_logger
from app.core.config import get_llm_model
from adapters.llm_adapter import analyze_text_json

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Directory helpers
# ---------------------------------------------------------------------------

def get_location_wiki_dir(story_uuid: str) -> str:
    path = os.path.join(StoryManager.DATA_DIR, story_uuid, "wiki", "locations")
    os.makedirs(path, exist_ok=True)
    return path

def _json_path(story_uuid: str, location_id: str) -> str:
    return os.path.join(get_location_wiki_dir(story_uuid), f"{location_id}.json")

# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

def save_location_wiki(story_uuid: str, location: LocationWiki):
    """Persists LocationWiki to JSON and Markdown."""
    path = _json_path(story_uuid, location.location_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(location.model_dump(), f, indent=2, ensure_ascii=False)
        
    md_path = os.path.join(get_location_wiki_dir(story_uuid), f"{location.location_id}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(render_location_wiki(location))

def load_location_wiki(story_uuid: str, location_id: str) -> Optional[LocationWiki]:
    """Loads a LocationWiki from JSON."""
    path = _json_path(story_uuid, location_id)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return LocationWiki(**data)
        except Exception as e:
            logger.error(f"Failed to load location wiki {location_id}: {e}")
    return None

def list_location_wikis(story_uuid: str) -> List[str]:
    """Returns a list of location_ids."""
    path = os.path.join(StoryManager.DATA_DIR, story_uuid, "wiki", "locations")
    if not os.path.exists(path):
        return []
    return [f[:-5] for f in os.listdir(path) if f.endswith(".json")]

# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def render_location_wiki(location: LocationWiki) -> str:
    """Renders LocationWiki to Markdown."""
    md = f"# 🗺️ {location.display_name}\n\n"
    
    if location.region or location.significance:
        md += "## 📍 Overview\n"
        if location.region:
            md += f"- **Region:** {location.region}\n"
        if location.significance:
            md += f"- **Significance:** {location.significance}\n"
        md += "\n"

    md += "## 📖 Description\n"
    md += f"{location.description}\n\n"
    
    md += "## 📜 Timeline\n"
    if location.timeline:
        for t in location.timeline:
            md += f"- **Ch. {t.get('chapter', '?')}**: {t.get('note', '')}\n"
    else:
        md += "No timeline recorded.\n"
    md += "\n"
    
    md += "## 👥 Characters Present\n"
    if location.characters_present:
        md += ", ".join(f"`{c}`" for c in location.characters_present) + "\n"
    else:
        md += "None recorded.\n"
    
    return md

# ---------------------------------------------------------------------------
# LLM Generation
# ---------------------------------------------------------------------------

def build_location_page(story_uuid: str, location_id: str, graph_provider) -> Optional[LocationWiki]:
    """Aggregates events at a location and uses LLM to generate a wiki page."""
    import datetime
    from app.services.wiki_versioning import compute_node_hash
    
    existing = load_location_wiki(story_uuid, location_id)
    current_hash = compute_node_hash(graph_provider.graph, location_id)
    
    if existing and existing.graph_snapshot_id == current_hash and current_hash != "":
        logger.info(f"Skipping generation for location '{location_id}' — graph state unchanged.")
        return existing

    # 1. Gather context from graph
    events = []
    characters = set()
    first_chap = float('inf')
    last_chap = 0
    
    for u, data in graph_provider.graph.nodes(data=True):
        if data.get("type") == "event" and data.get("location") == location_id:
            events.append({
                "id": u,
                "description": data.get("description", ""),
                "chapter_id": data.get("chapter_id", 0)
            })
            ch = data.get("chapter_id", 0)
            if ch > 0:
                first_chap = min(first_chap, ch)
                last_chap = max(last_chap, ch)
                
            # Find characters in this event
            for src, dst, edge_data in graph_provider.graph.edges(u, data=True):
                if edge_data.get("relation") == "featured":
                    characters.add(dst)
            for src, dst, edge_data in graph_provider.graph.edges(data=True):
                 if dst == u and graph_provider.graph.nodes[src].get("type") == "character":
                    characters.add(src)

    if not events:
        logger.warning(f"No events found for location '{location_id}'")
        return None
        
    if first_chap == float('inf'):
        first_chap = 0

    # Sort events
    events.sort(key=lambda x: x["chapter_id"])
    
    context_str = json.dumps(events, indent=2)

    prompt = f"""
You are the loremaster for a webnovel. Generate a wiki page for the location '{location_id}'.
Here are the events that occurred at this location:
{context_str}

Return a valid JSON object matching this schema:
{{
    "description": "A vivid description of the location based on context.",
    "region": "The broader region it belongs to, or null if unknown.",
    "significance": "Why this place matters to the story, or null.",
    "timeline": [{{"chapter": int, "note": "Brief summary of what happened here"}}]
}}
"""
    result = analyze_text_json(prompt, model=get_llm_model())
    if not result:
        return None

    wiki = LocationWiki(
        location_id=location_id,
        version=(existing.version + 1) if existing else 1,
        generated_at=datetime.datetime.utcnow().isoformat(),
        graph_snapshot_id=current_hash,
        display_name=location_id.replace("_", " ").title(),
        description=result.get("description", "A location in the story."),
        region=result.get("region"),
        significance=result.get("significance"),
        events_occurred=[e["id"] for e in events],
        characters_present=list(characters),
        timeline=result.get("timeline", []),
        first_appearance_chapter=first_chap,
        last_updated_chapter=last_chap
    )
    
    save_location_wiki(story_uuid, wiki)
    return wiki
