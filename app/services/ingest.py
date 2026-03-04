import os
import json
from datetime import datetime
from typing import Dict, Tuple

from app.core.models.chapter import Chapter
from app.core.models.character_runtime import CharacterRuntime
from app.core.models.character_wiki import CharacterWiki
from app.services.extraction import extract_chapter_intelligence
from app.services.wiki import save_character_wiki
from app.core.graduation import check_graduation_status
from app.core.story_manager import StoryManager

def normalize_id(name: str) -> str:
    """
    Converts a display name (e.g., 'Lord Stark') to a unique ID (e.g., 'lord_stark').
    Used for linking Wiki entries to Runtime stats.
    """
    return name.lower().replace(" ", "_")

def load_runtime(story_uuid: str) -> Tuple[int, Dict[str, CharacterRuntime]]:
    path = os.path.join(StoryManager.DATA_DIR, story_uuid, "runtime_db.json")
    if not os.path.exists(path):
        return 0, {}
        
    with open(path, "r") as f:
        data = json.load(f)
        
    chapter_counter = data.get("chapter_counter", 0)
    characters_raw = data.get("characters", {})
    
    runtime_db = {}
    for char_id, char_data in characters_raw.items():
        # Reconstruct Pydantic model
        runtime_db[char_id] = CharacterRuntime(**char_data)
        
    return chapter_counter, runtime_db

def save_runtime(story_uuid: str, chapter_counter: int, runtime_db: Dict[str, CharacterRuntime]):
    path = os.path.join(StoryManager.DATA_DIR, story_uuid, "runtime_db.json")
    
    data = {
        "chapter_counter": chapter_counter,
        "characters": {k: v.dict() for k, v in runtime_db.items()}
    }
    
    with open(path, "w") as f:
        json.dump(data, f, indent=4)
        
    # Also touch the story updated_at
    StoryManager._touch_updated_at(story_uuid)

def save_chapter(story_uuid: str, chapter: Chapter):
    chapter_dir = os.path.join(StoryManager.DATA_DIR, story_uuid, "chapters", str(chapter.id))
    os.makedirs(chapter_dir, exist_ok=True)
    
    with open(os.path.join(chapter_dir, "text.txt"), "w", encoding="utf-8") as f:
        f.write(chapter.raw_text)
        
    metadata = {
        "id": chapter.id,
        "title": chapter.title,
        "created_at": chapter.created_at.isoformat()
    }
    with open(os.path.join(chapter_dir, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)

def ingest_chapter(story_uuid: str, title: str, text: str, extractor: str = "spacy", decay_rate: float = 0.05) -> Chapter:
    chapter_counter, runtime_db = load_runtime(story_uuid)
    
    chapter_counter += 1

    # 1. Create Base Chapter
    chapter = Chapter(
        id=chapter_counter,
        title=title,
        raw_text=text,
        created_at=datetime.utcnow()
    )
    
    # Save chapter to disk
    save_chapter(story_uuid, chapter)
    
    # 2. Extract Intelligence
    if extractor == "llm":
        from app.services.extraction import extract_chapter_intelligence_llm
        intelligence = extract_chapter_intelligence_llm(text)
    else:
        intelligence = extract_chapter_intelligence(text)
        
    active_names = intelligence.get("active_character_names", [])
    
    # 2.5 Resolve Aliases
    from app.services.alias_resolver import resolve_aliases
    active_names = resolve_aliases(active_names)
    
    # 3. Graph Updates
    from adapters.graph_adapter import get_graph_engine
    graph = get_graph_engine(story_uuid)
    
    # Add characters to graph
    for name in active_names:
        char_id = normalize_id(name)
        graph.add_character(char_id, {"display_name": name, "last_seen_chapter": chapter_counter})
        
    # Create an event to represent the occurrences in this chapter
    if active_names:
        event_id = f"chapter_{chapter_counter}_event"
        description = f"Events of Chapter {chapter_counter}"
        graph.add_event(event_id, description, [normalize_id(n) for n in active_names], chapter_id=chapter_counter)
    
    # 4. Update Story Engine State (Runtime tracking)
    for name in active_names:
        char_id = normalize_id(name)
        
        # Calculate proper graph-based Centrality (PageRank with Temporal Decay)
        new_score = graph.get_character_importance(char_id, current_chapter=chapter_counter, decay_rate=decay_rate)
        
        # Runtime Update
        if char_id not in runtime_db:
            # New Character Discovery
            runtime_db[char_id] = CharacterRuntime(
                character_id=char_id,
                first_seen_chapter=chapter_counter,
                last_seen_chapter=chapter_counter,
                confidence_score=new_score, 
                mention_count=1
            )
            
            # Wiki Proposal
            wiki_entry = CharacterWiki(
                character_id=char_id,
                display_name=name,
                short_description=f"Appeared in Chapter {chapter_counter}",
                first_appearance_chapter=chapter_counter,
                last_updated_chapter=chapter_counter,
                confidence=new_score
            )
            save_character_wiki(story_uuid, wiki_entry)
            
        else:
            # Existing Character Update
            char = runtime_db[char_id]
            char.last_seen_chapter = chapter_counter
            char.mention_count += 1
            char.confidence_score = new_score
            
            # Graduation Check & Voice Locking
            did_graduate = check_graduation_status(char)
            if did_graduate:
                print(f"[EVENT] Character {char.character_id} graduated! Assigned Voice: {char.voice_id}")
                wiki_entry = CharacterWiki(
                    character_id=char_id,
                    display_name=name,
                    short_description=f"Appeared in Chapter {char.first_seen_chapter}",
                    first_appearance_chapter=char.first_seen_chapter,
                    last_updated_chapter=chapter_counter,
                    confidence=char.confidence_score,
                    voice_id=char.voice_id
                )
                save_character_wiki(story_uuid, wiki_entry)
            
            # Update local state
            runtime_db[char_id] = char

    # Atomically save all changes to disk
    save_runtime(story_uuid, chapter_counter, runtime_db)
    return chapter
