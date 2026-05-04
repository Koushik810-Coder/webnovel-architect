import json
import os
from typing import Optional, List

from app.core.models.arc_wiki import ArcWiki
from app.core.story_manager import StoryManager
from app.core.logger import get_logger
from app.core.config import get_llm_model
from adapters.llm_adapter import analyze_text_json

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Directory helpers
# ---------------------------------------------------------------------------

def get_arc_wiki_dir(story_uuid: str) -> str:
    path = os.path.join(StoryManager.DATA_DIR, story_uuid, "wiki", "arcs")
    os.makedirs(path, exist_ok=True)
    return path

def _json_path(story_uuid: str, arc_id: str) -> str:
    return os.path.join(get_arc_wiki_dir(story_uuid), f"{arc_id}.json")

# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

def save_arc_wiki(story_uuid: str, arc: ArcWiki):
    """Persists ArcWiki to JSON and Markdown."""
    path = _json_path(story_uuid, arc.arc_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(arc.model_dump(), f, indent=2, ensure_ascii=False)
        
    md_path = os.path.join(get_arc_wiki_dir(story_uuid), f"{arc.arc_id}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(render_arc_wiki(arc))

def load_arc_wiki(story_uuid: str, arc_id: str) -> Optional[ArcWiki]:
    """Loads an ArcWiki from JSON."""
    path = _json_path(story_uuid, arc_id)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return ArcWiki(**data)
        except Exception as e:
            logger.error(f"Failed to load arc wiki {arc_id}: {e}")
    return None

def list_arc_wikis(story_uuid: str) -> List[str]:
    """Returns a list of arc_ids."""
    path = os.path.join(StoryManager.DATA_DIR, story_uuid, "wiki", "arcs")
    if not os.path.exists(path):
        return []
    return [f[:-5] for f in os.listdir(path) if f.endswith(".json")]

# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def render_arc_wiki(arc: ArcWiki) -> str:
    """Renders ArcWiki to Markdown."""
    md = f"# 🔄 {arc.display_name}\n\n"
    
    md += f"> **Theme:** *{arc.theme}*\n\n"
    
    md += "## 📖 Summary\n"
    md += f"{arc.summary}\n\n"
    
    md += "## 📈 Arc Structure\n"
    md += f"- **Chapters:** {arc.chapter_start} to {arc.chapter_end}\n"
    if arc.start_event_id:
        md += f"- **Inciting Incident:** `{arc.start_event_id}`\n"
    if arc.escalation_event_ids:
        md += "- **Escalation:**\n"
        for e in arc.escalation_event_ids:
            md += f"  - `{e}`\n"
    if arc.turning_point_event_id:
        md += f"- **Turning Point:** `{arc.turning_point_event_id}`\n"
    if arc.resolution_event_id:
        md += f"- **Resolution:** `{arc.resolution_event_id}`\n"
    md += "\n"
    
    md += "## 👥 Key Participants\n"
    if arc.participating_characters:
        md += ", ".join(f"`{c}`" for c in arc.participating_characters) + "\n"
    else:
        md += "None recorded.\n"
    md += "\n"

    md += "## 🧠 Emotional & Thematic Evolution\n"
    md += "### Emotional Shifts\n"
    if arc.emotional_evolution:
        for ev in arc.emotional_evolution:
            md += f"- **Ch. {ev.get('chapter', '?')}:** {ev.get('note', '')}\n"
    else:
        md += "None recorded.\n"
        
    md += "### Thematic Milestones\n"
    if arc.thematic_evolution:
        for ev in arc.thematic_evolution:
            md += f"- **Ch. {ev.get('chapter', '?')}:** {ev.get('note', '')}\n"
    else:
        md += "None recorded.\n"

    return md

# ---------------------------------------------------------------------------
# LLM Generation
# ---------------------------------------------------------------------------

def build_arc_page(story_uuid: str, arc_id: str, graph_provider) -> Optional[ArcWiki]:
    """Generates an ArcWiki from graph data using an LLM."""
    if not graph_provider.graph.has_node(arc_id) or graph_provider.graph.nodes[arc_id].get("type") != "arc":
        logger.warning(f"Arc '{arc_id}' not found in graph.")
        return None
        
    arc_data = graph_provider.graph.nodes[arc_id]
    event_ids = arc_data.get("event_ids", [])
    
    events = []
    characters = set()
    
    for ev_id in event_ids:
        if graph_provider.graph.has_node(ev_id):
            ev_data = graph_provider.graph.nodes[ev_id]
            events.append({
                "id": ev_id,
                "description": ev_data.get("description", ""),
                "chapter_id": ev_data.get("chapter_id", 0)
            })
            # Find participants
            for u, v, data in graph_provider.graph.in_edges(ev_id, data=True):
                 if graph_provider.graph.nodes[u].get("type") == "character":
                     characters.add(u)
                     
    events.sort(key=lambda x: x["chapter_id"])
    context_str = json.dumps(events, indent=2)

    prompt = f"""
You are the loremaster for a webnovel. Generate a detailed narrative arc wiki page for '{arc_id}'.
Here are the events that comprise this arc in chronological order:
{context_str}

Return a valid JSON object matching this schema. Be analytical about the narrative structure:
{{
    "theme": "The core thematic question or conflict (e.g., 'Discovery and self-acceptance').",
    "summary": "A cohesive narrative summary of the arc.",
    "start_event_id": "event_id of the inciting incident",
    "escalation_event_ids": ["event_id_2", "event_id_3"],
    "turning_point_event_id": "event_id of the climax/twist",
    "resolution_event_id": "event_id of the resolution",
    "emotional_evolution": [{{"chapter": int, "note": "How the characters changed internally"}}],
    "thematic_evolution": [{{"chapter": int, "note": "How the core theme progressed"}}]
}}
"""
    result = analyze_text_json(prompt, model=get_llm_model())
    if not result:
        return None

    wiki = ArcWiki(
        arc_id=arc_id,
        display_name=arc_data.get("label", arc_id.replace("_", " ").title()),
        theme=result.get("theme", "Unknown Theme"),
        summary=result.get("summary", "An arc in the story."),
        start_event_id=result.get("start_event_id"),
        escalation_event_ids=result.get("escalation_event_ids", []),
        turning_point_event_id=result.get("turning_point_event_id"),
        resolution_event_id=result.get("resolution_event_id"),
        participating_characters=list(characters),
        emotional_evolution=result.get("emotional_evolution", []),
        thematic_evolution=result.get("thematic_evolution", []),
        chapter_start=arc_data.get("chapter_start", 0),
        chapter_end=arc_data.get("chapter_end", 0)
    )
    
    save_arc_wiki(story_uuid, wiki)
    return wiki
