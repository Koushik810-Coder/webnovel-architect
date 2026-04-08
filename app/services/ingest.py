import os
import json
from datetime import datetime
from typing import Dict, Tuple, List, Optional, Callable

from app.core.models.chapter import Chapter
from app.core.models.character_runtime import CharacterRuntime
from app.core.models.character_wiki import CharacterWiki
from app.services.extraction import extract_chapter_intelligence, extract_chapter_intelligence_llm
from app.services.wiki import (
    save_character_wiki,
    load_character_wiki_json,
    update_character_profile,
    get_character_wiki_content,
    apply_profile_updates,
)
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
        "characters": {k: v.model_dump() for k, v in runtime_db.items()}
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


# ---------------------------------------------------------------------------
# Public ingestion functions
# ---------------------------------------------------------------------------

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
    
    # 2. Extract Intelligence FIRST — before committing any state to disk.
    # If extraction fails the chapter_counter is never incremented, so the next
    # attempt will reuse the same chapter slot (no off-by-one drift).
    if extractor == "llm":
        intelligence = extract_chapter_intelligence_llm(text)
    else:
        intelligence = extract_chapter_intelligence(text)

    # Extraction succeeded — now it is safe to advance the counter and persist.
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
    
    # Extract character relationships, events, and demographic data
    intelligence = extract_chapter_intelligence(text, extractor=extractor)
    active_names = intelligence.get("active_character_names", [])
    events = intelligence.get("events", [])
    
    # 2.5 Resolve Aliases against existing graph characters to prevent cross-chapter duplicates
    from adapters.graph_adapter import get_graph_engine
    graph = get_graph_engine(story_uuid)
    
    existing_char_names = [data.get("display_name", str(node)) for node, data in graph.graph.nodes(data=True) if data.get("type") == "character"]
    from app.services.alias_resolver import resolve_aliases_with_map
    
    all_names = list(set(active_names + existing_char_names))
    _, full_alias_map = resolve_aliases_with_map(all_names)
    
    # Map the isolated active_names for this chapter to their true global canonical names
    original_active_names = active_names
    active_names = list(set([full_alias_map.get(n, n) for n in active_names]))
    
    # We only care about the mapping subset that affects THIS chapter's characters
    alias_map = {k: v for k, v in full_alias_map.items() if k in original_active_names or v in original_active_names}
    
    # 2.6 Propagate Gender Predictions to Canonical Names
    raw_genders = intelligence.get("character_genders", {})
    predicted_genders = {}
    for raw_name, gender in raw_genders.items():
        # Look up the newly resolved canonical name, or fall back to the raw name
        canon = full_alias_map.get(raw_name, raw_name)
        predicted_genders[canon] = gender
    
    logger.info(f"Intelligence extracted ({len(active_names)} active characters after alias collapsing). Updating relational graph...")
    
    # 3. Graph Updates
    # Add characters to graph
    for name in active_names:
        char_id = normalize_id(name)
        graph.add_character(char_id, {"display_name": name, "last_seen_chapter": chapter_counter})
            # Create an event to represent the occurrences in this chapter
    if events:
        # First pass: Create all events and store their generated IDs
        event_ids: list[str] = []
        for idx, event_data in enumerate(events):
            action_summary = event_data.get("action_summary", "Unknown Event")
            involved_chars = event_data.get("involved_characters", [])
            
            # Map involved_chars using the global full_alias_map
            involved_chars = list(set([full_alias_map.get(n, n) for n in involved_chars]))
            
            # Filter out characters that aren't in active_names to be safe
            valid_chars = [normalize_id(n) for n in involved_chars if normalize_id(n) in [normalize_id(an) for an in active_names]]
            
            event_id = f"chapter_{chapter_counter}_event_{idx}"
            event_ids.append(event_id)
            
            if valid_chars:
                pre_conditions = event_data.get("pre_conditions", "")
                post_conditions = event_data.get("post_conditions", "")
                location = event_data.get("location", "Unknown")
                relation_type = event_data.get("relation_type", "participant")
                # Clamp intensity to valid range 1-5
                raw_intensity = event_data.get("intensity", 1)
                try:
                    intensity = max(1, min(5, int(raw_intensity)))
                except (TypeError, ValueError):
                    intensity = 1

                graph.add_event(
                    event_id,
                    action_summary,
                    valid_chars,
                    chapter_id=chapter_counter,
                    pre_conditions=pre_conditions,
                    post_conditions=post_conditions,
                    location=location,
                    relation_type=relation_type,
                    intensity=intensity,
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
    
    logger.info("Graph updated. Calculating PageRank and Temporal Runtime Milestones...")
    
    # 4. Update Story Engine State (Runtime tracking)
    for name in active_names:
        char_id = normalize_id(name)
        
        # Calculate proper graph-based Centrality (PageRank with Temporal Decay)
        new_score = graph.get_character_importance(char_id, current_chapter=chapter_counter, decay_rate=decay_rate)
        
        # Runtime Update
        predicted_gender = predicted_genders.get(name, "neutral")
        
        if char_id not in runtime_db:
            # ── New Character Discovery ────────────────────────────────────
            runtime_db[char_id] = CharacterRuntime(
                character_id=char_id,
                first_seen_chapter=chapter_counter,
                last_seen_chapter=chapter_counter,
                confidence_score=new_score,
                mention_count=1
            )

            # Build event block for this character
            char_events_new = [e for e in events if name.lower() in [i.lower() for i in e.get("involved_characters", [])]]
            event_text_block_new = "\n".join([f"- {e.get('action_summary')}" for e in char_events_new])

            # LLM enrichment even on first appearance (if they have events)
            if event_text_block_new:
                first_profile = update_character_profile("", event_text_block_new, name)
            else:
                first_profile = {}

            # Build aliases list: all surface forms from this chapter that map to this character
            char_aliases = sorted({alias for alias, canon in alias_map.items() if canon == name and alias != name})

            wiki_entry = CharacterWiki(
                character_id=char_id,
                display_name=name,
                aliases=char_aliases,
                short_description=(
                    first_profile.get("short_description")
                    or f"Appeared in Chapter {chapter_counter}."
                ),
                long_description=first_profile.get("synopsis"),
                status=first_profile.get("status"),
                age=first_profile.get("age"),
                gender=first_profile.get("gender") or predicted_gender,
                species=first_profile.get("species"),
                role=first_profile.get("role"),
                affiliations=first_profile.get("affiliations") or [],
                appearance=first_profile.get("appearance"),
                personality_traits=first_profile.get("personality_traits") or [],
                notable_quirks=first_profile.get("notable_quirks") or [],
                first_appearance_chapter=chapter_counter,
                last_updated_chapter=chapter_counter,
                confidence=new_score,
            )
            save_character_wiki(story_uuid, wiki_entry)

            # DPQ: evaluate graduation immediately in case they dominate the chapter
            char = runtime_db[char_id]
            did_graduate = check_graduation_status(char, wiki_traits={"gender": wiki_entry.gender or predicted_gender})
            if did_graduate:
                logger.info(f"New Character {char.character_id} graduated via DPQ! Assigned Voice: {char.voice_id}")
                wiki_entry.voice_id = char.voice_id
                save_character_wiki(story_uuid, wiki_entry)
                
        else:
            # ── Existing Character Update ──────────────────────────────────
            char = runtime_db[char_id]
            char.last_seen_chapter = chapter_counter
            char.mention_count += 1
            char.confidence_score = new_score

            # Find what happened to them this chapter
            char_events_this_chapter = [e for e in events if name.lower() in [i.lower() for i in e.get("involved_characters", [])]]
            event_text_block = "\n".join([f"- {e.get('action_summary')}" for e in char_events_this_chapter])

            # Load existing wiki from JSON sidecar (auto-migrates .md if needed)
            old_wiki = load_character_wiki_json(story_uuid, char_id)

            if not event_text_block:
                # No new events — skip the LLM call and the save entirely (no change)
                did_graduate = check_graduation_status(char, wiki_traits={"gender": old_wiki.gender if old_wiki else None})
                if did_graduate:
                    logger.info(f"Character {char.character_id} graduated (no events)! Voice: {char.voice_id}")
                    if old_wiki:
                        old_wiki = old_wiki.model_copy(update={"voice_id": char.voice_id, "confidence": char.confidence_score})
                        save_character_wiki(story_uuid, old_wiki)
                runtime_db[char_id] = char
                continue

            # Fetch the existing markdown for the LLM context (so it can write prose)
            existing_wiki_md = get_character_wiki_content(story_uuid, char_id)

            # LLM merge: existing bio + new events
            profile_data = update_character_profile(existing_wiki_md, event_text_block, name)

            # Graduation Check & Voice Locking
            did_graduate = check_graduation_status(char, wiki_traits=profile_data)
            if did_graduate:
                logger.info(f"Character {char.character_id} graduated! Assigned Voice: {char.voice_id}")

            # Build the updated wiki by applying LLM response on top of old data
            # so no previously known field is silently erased
            if old_wiki:
                base_wiki = old_wiki.model_copy(update={
                    "last_updated_chapter": chapter_counter,
                    "confidence": char.confidence_score,
                    "voice_id": char.voice_id,
                })
            else:
                # Defensive fallback — shouldn't happen but safer than crashing
                base_wiki = CharacterWiki(
                    character_id=char_id,
                    display_name=name,
                    short_description=f"First appeared in Chapter {char.first_seen_chapter}.",
                    first_appearance_chapter=char.first_seen_chapter,
                    last_updated_chapter=chapter_counter,
                    confidence=char.confidence_score,
                    voice_id=char.voice_id,
                )

            # Merge alias backfill
            char_aliases = sorted({alias for alias, canon in alias_map.items() if canon == name and alias != name})
            if char_aliases:
                existing_aliases = set(base_wiki.aliases or [])
                merged_aliases = sorted(existing_aliases | set(char_aliases))
                base_wiki = base_wiki.model_copy(update={"aliases": merged_aliases})

            # Apply LLM overrides — only non-empty values win
            wiki_entry = apply_profile_updates(base_wiki, profile_data)

            save_character_wiki(story_uuid, wiki_entry)

            # Update local state
            runtime_db[char_id] = char

    # Phase 2: Iterate over all known characters to handle decay/de-graduation for absent characters
    for char_id, char in runtime_db.items():
        if char_id not in [normalize_id(n) for n in active_names]:
            # They didn't appear, but their score decays due to time passing
            decayed_score = graph.get_character_importance(char_id, current_chapter=chapter_counter, decay_rate=decay_rate)
            char.confidence_score = decayed_score
            
            # Did they fall out of provisional MAIN_CAST status?
            if check_graduation_status(char):
                logger.info(f"Character {char_id} score decayed. Voice lock released.")

    # Atomically save all changes to disk
    save_runtime(story_uuid, chapter_counter, runtime_db)
    logger.info(f"Chapter {chapter_counter} ({title}) fully ingested and state persisted.")
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
        if os.path.exists("cancel_ingestion.flag"):
            logger.info("Batch ingestion cancelled by user.")
            break
            
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
                    if progress_callback is not None:
                        progress_callback(i + 1, total)
                    continue
            else:
                if progress_callback is not None:
                    progress_callback(i + 1, total)
                continue
                
        try:
            chapter = ingest_chapter(story_uuid, title, text, extractor, decay_rate)
            ingested_chapters.append(chapter)
        except Exception as e:
            # Stop the batch at the failed chapter so last_ingested_index stays
            # at N-1 (already persisted by progress_callback).  The next
            # user-triggered batch will start from this chapter automatically.
            err_msg = str(e)
            logger.error(f"Failed to ingest chapter '{title}' (stopping batch): {err_msg}")
            with open("cancel_ingestion.flag", "w") as f:
                f.write(f"error: {err_msg}")
            break
        
        if progress_callback is not None:
            progress_callback(i + 1, total)
            
    return ingested_chapters
