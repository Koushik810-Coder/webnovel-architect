import os
import json
from datetime import datetime
from typing import Dict, Tuple, List, Optional, Callable

from app.core.models.chapter import Chapter
from app.core.models.character_runtime import CharacterRuntime
from app.core.models.character_wiki import CharacterWiki
from app.services.extraction import extract_chapter_intelligence, extract_chapter_intelligence_llm
from app.services.wiki import save_character_wiki
from app.core.graduation import check_graduation_status
from app.core.story_manager import StoryManager
from app.core.logger import get_logger

logger = get_logger(__name__)

def normalize_id(name: str) -> str:
    """
    Converts a display name (e.g., 'Lord Stark') to a unique ID (e.g., 'lord_stark').
    Used for linking Wiki entries to Runtime stats.
    """
    return name.lower().replace(" ", "_")

def load_runtime(story_uuid: str) -> Tuple[int, Dict[str, CharacterRuntime]]:
    """
    Loads the persistent runtime database for characters in a specific story.
    
    Args:
        story_uuid (str): The unique identifier for the story.
        
    Returns:
        Tuple[int, Dict[str, CharacterRuntime]]: The current chapter counter and 
            a dictionary mapping character IDs to their CharacterRuntime profiles.
    """
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
    """
    Saves the character runtime database and chapter counter to disk.
    
    Args:
        story_uuid (str): The unique identifier for the story.
        chapter_counter (int): The current chapter count.
        runtime_db (Dict[str, CharacterRuntime]): Dictionary mapping character IDs to their runtime models.
    """
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
    """
    Saves the full text and metadata of a chapter to the file system.
    
    Args:
        story_uuid (str): The unique identifier for the story.
        chapter (Chapter): The chapter model containing text and metadata to save.
    """
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

def load_index_state(story_uuid: str) -> Optional[Dict]:
    """Loads the persisted index state for a story, if it exists."""
    path = os.path.join(StoryManager.DATA_DIR, story_uuid, "index_state.json")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return None
    return None

def save_index_state(story_uuid: str, state: Dict):
    """Saves the index state (e.g., scraped chapters and last ingested index)."""
    path = os.path.join(StoryManager.DATA_DIR, story_uuid, "index_state.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

def ingest_chapter(story_uuid: str, title: str, text: str, extractor: str = "llm", decay_rate: float = 0.05) -> Chapter:
    """
    Processes and ingests a single chapter for a given story.
    
    This pipeline extracts chapter intelligence, updates relational graphs, tracks
    character prominence and centrality, handles voice graduations, and saves the
    ingested content to the filesystem.
    
    Args:
        story_uuid (str): The unique identifier for the story.
        title (str): The chapter title.
        text (str): The full raw text of the chapter.
        extractor (str): The extraction strategy to use (default is "llm").
        decay_rate (float): The temporal decay rate for graph centrality calculations.
        
    Returns:
        Chapter: The fully processed and persisted Chapter object.
    """
    chapter_counter, runtime_db = load_runtime(story_uuid)
    
    logger.info(f"Ingesting chapter: '{title}' for story {story_uuid} using extractor '{extractor}'")
    
    chapter_counter += 1

    from datetime import timezone
    chapter = Chapter(
        id=chapter_counter,
        title=title,
        raw_text=text,
        created_at=datetime.now(timezone.utc)
    )
    
    # Save chapter to disk
    save_chapter(story_uuid, chapter)
    
    # 2. Extract Intelligence
    if extractor == "llm":
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
    events = intelligence.get("events", [])
    if events:
        # First pass: Create all events and store their generated IDs
        event_ids: list[str] = []
        for idx, event_data in enumerate(events):
            action_summary = event_data.get("action_summary", "Unknown Event")
            involved_chars = event_data.get("involved_characters", [])
            
            # Resolve aliases for the involved characters
            involved_chars = resolve_aliases(involved_chars)
            
            # Filter out characters that aren't in active_names to be safe
            valid_chars = [normalize_id(n) for n in involved_chars if normalize_id(n) in [normalize_id(an) for an in active_names]]
            
            event_id = f"chapter_{chapter_counter}_event_{idx}"
            event_ids.append(event_id)
            
            if valid_chars:
                pre_conditions = event_data.get("pre_conditions", "")
                post_conditions = event_data.get("post_conditions", "")
                location = event_data.get("location", "Unknown")
                
                graph.add_event(
                    event_id, 
                    action_summary, 
                    valid_chars, 
                    chapter_id=chapter_counter,
                    pre_conditions=pre_conditions,
                    post_conditions=post_conditions,
                    location=location
                )
        
        # Second pass: Process causal links now that all events exist
        for idx, event_data in enumerate(events):
            source_event_id = event_ids[idx]
            causes_indexes = event_data.get("causes_event_indexes", [])
            
            if isinstance(causes_indexes, list):
                for target_idx in causes_indexes:
                    # Sanity check: Ensure the index is an integer and within valid bounds
                    try:
                        target_idx = int(target_idx)
                        if 0 <= target_idx < len(event_ids) and target_idx != idx:
                            target_event_id = event_ids[target_idx]
                            graph.add_causal_edge(source_event_id, target_event_id)
                    except (ValueError, TypeError):
                        logger.warning(f"Invalid causal index '{target_idx}' in event {idx}")
                        
    elif active_names:
        # Fallback to the generic event if no specific events were extracted
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
                logger.info(f"Character {char.character_id} graduated! Assigned Voice: {char.voice_id}")
                
            # Grab existing wiki content
            from app.services.wiki import get_character_wiki_content, update_character_summary
            existing_wiki_md = get_character_wiki_content(story_uuid, char_id)
            
            # Extract only the "long_description" part from the raw MD, or just use the whole thing if simple
            import re
            desc_match = re.search(r"## Description\n(.*?)(?=\n##|$)", existing_wiki_md, flags=re.DOTALL)
            existing_desc = desc_match.group(1).strip() if desc_match else ""
            
            # Find what happened to them this chapter
            char_events_this_chapter = [e for e in events if name.lower() in [i.lower() for i in e.get("involved_characters", [])]]
            event_text_block = "\n".join([f"- {e.get('action_summary')}" for e in char_events_this_chapter])
            
            new_long_desc = existing_desc
            if event_text_block:
                # Only run the LLM if they actually did something in an event (saves tokens/time for background chars)
                new_long_desc = update_character_summary(existing_desc, event_text_block, name)
                
            # Always update the Wiki so it reflects the latest stats (Confidence, Mentions)
            wiki_entry = CharacterWiki(
                character_id=char_id,
                display_name=name,
                short_description=f"First appeared in Chapter {char.first_seen_chapter}. Last seen in Chapter {char.last_seen_chapter}.",
                long_description=new_long_desc if new_long_desc else None,
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

def ingest_multiple_chapters(
    story_uuid: str, 
    chapters: List[Dict[str, str]], 
    extractor: str = "llm", 
    decay_rate: float = 0.05,
    progress_callback: Optional[Callable] = None
) -> List[Chapter]:
    """
    Ingests a list of chapters sequentially.
    'chapters' is a list of dicts with 'title' and 'url' or 'text'.
    If 'url' is provided, it must be scraped first (caller should handle scraping or we do it here).
    For the UI flow, we usually have the text ready if we clicked "Process All", 
    but if we only have URLs, we need to fetch them.
    
    Actually, to keep it clean, let's assume 'chapters' contains 'title' and 'text'.
    If 'text' is missing, it will skip or the caller should have populated it.
    """
    ingested_chapters = []
    total = len(chapters)
    
    for i, chap_data in enumerate(chapters):
        title = chap_data.get("title", f"Chapter {i+1}")
        text = chap_data.get("text")
        
        if not text:
            # If text is missing, we might need to scrape it here if a URL is present
            url = chap_data.get("url")
            if url:
                from app.services.scrapers.royalroad_scraper import RoyalRoadScraper
                scraper = RoyalRoadScraper()
                try:
                    scraped = scraper.scrape_chapter(url)
                    text = scraped.get("text")
                except Exception as e:
                    logger.error(f"Error scraping {url}: {e}")
                    continue
            else:
                continue
                
        chapter = ingest_chapter(story_uuid, title, text, extractor, decay_rate)
        ingested_chapters.append(chapter)
        
        if progress_callback is not None:
            progress_callback(i + 1, total)
            
    return ingested_chapters
