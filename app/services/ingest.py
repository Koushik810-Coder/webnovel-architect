import os
import json
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, Tuple, List, Optional, Callable

from app.core.models.chapter import Chapter
from app.core.models.character_runtime import CharacterRuntime
from app.core.models.character_wiki import CharacterWiki
from app.services.extraction import extract_chapter_intelligence, extract_chapter_intelligence_llm
from app.services.wiki import (
    save_character_wiki,
    load_character_wiki_json,
    update_character_profile,
    batch_update_character_profiles,
    get_character_wiki_content,
    apply_profile_updates,
)
from app.services.arc_detector import detect_arcs
from app.core.graduation import check_graduation_status
from app.core.story_manager import StoryManager
from app.core.logger import get_logger
from adapters.graph_adapter import get_graph_engine
from app.services.alias_resolver import resolve_aliases_with_map

logger = get_logger(__name__)

# Sentinel file written by the UI to cancel a running batch ingestion.
# Placed in the process CWD (project root) for simplicity.
_CANCEL_FLAG = "cancel_ingestion.flag"

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
# 1.8  Conditional Fixer Pass — deterministic trigger detection (no LLM)
# ---------------------------------------------------------------------------

def _check_fixer_triggers(events: list) -> list:
    """Scan extracted events for deterministically-detectable anomalies.

    Returns a list of flag dicts: ``[{"event_id": ..., "reason": ...}, ...]``.
    An empty list means the event set is clean.

    Trigger conditions (all detectable without an LLM call):
    - Missing / None ``timeline_type``
    - A flashback whose ``story_time_rank`` is *higher* than a subsequent
      present-timeline event (causal ordering violation)
    """
    flags: list = []

    for evt in events:
        evt_id = evt.get("id", "<unknown>")

        # Trigger 1: missing timeline_type
        if not evt.get("timeline_type"):
            flags.append({
                "event_id": evt_id,
                "reason": "timeline_type is missing or None",
            })

    # Trigger 2: conflicting story_time_rank ordering
    # A flashback (timeline_type != "present") should have a LOWER
    # story_time_rank than surrounding present-timeline events.
    # Flag any flashback whose rank is higher than a later present event.
    present_ranks = [
        e.get("story_time_rank")
        for e in events
        if e.get("timeline_type") == "present" and e.get("story_time_rank") is not None
    ]
    min_present_rank = min(present_ranks) if present_ranks else None

    for evt in events:
        if evt.get("timeline_type") in ("flashback", "memory", "dream"):
            rank = evt.get("story_time_rank")
            if rank is not None and min_present_rank is not None and rank > min_present_rank:
                flags.append({
                    "event_id": evt.get("id", "<unknown>"),
                    "reason": (
                        f"story_time_rank conflict: flashback rank {rank} "
                        f"is higher than present-timeline rank {min_present_rank}"
                    ),
                })

    return flags


# ---------------------------------------------------------------------------
# Public ingestion functions
# ---------------------------------------------------------------------------

def _get_previous_chapter_context(story_uuid: str, chapter_id: int, num_paragraphs: int = 2) -> Optional[str]:
    """
    Reads the last N paragraphs of the previous chapter to provide context
    for the sliding window extraction strategy.
    """
    if chapter_id <= 0:
        return None
        
    path = os.path.join(StoryManager.DATA_DIR, story_uuid, "chapters", str(chapter_id), "text.txt")
    if not os.path.exists(path):
        return None
        
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
            
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        if not paragraphs:
            return None
            
        return "\n\n".join(paragraphs[-num_paragraphs:])
    except Exception as e:
        logger.warning(f"Failed to load previous chapter {chapter_id} context: {e}")
        return None

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
    previous_context = _get_previous_chapter_context(story_uuid, chapter_counter)
    
    if extractor == "llm":
        intelligence = extract_chapter_intelligence_llm(text, previous_context=previous_context)
    else:
        intelligence = extract_chapter_intelligence(text)

    # Extraction succeeded — now it is safe to advance the counter and persist.
    chapter_counter += 1

    chapter = Chapter(
        id=chapter_counter,
        title=title,
        raw_text=text,
        created_at=datetime.now(timezone.utc)
    )
    
    # Save chapter to disk
    save_chapter(story_uuid, chapter)
    
    active_names = intelligence.get("active_character_names", [])
    events = intelligence.get("events", [])

    # 1.8 Conditional Fixer Pass
    flags = _check_fixer_triggers(events)
    if flags:
        for f in flags:
            logger.warning(f"Fixer Pass Flag - Event {f.get('event_id')}: {f.get('reason')}")

    # 2.5 Resolve Aliases against existing graph characters to prevent cross-chapter duplicates
    graph = get_graph_engine(story_uuid)

    existing_char_names = [data.get("display_name", str(node)) for node, data in graph.graph.nodes(data=True) if data.get("type") == "character"]
    all_names = list(set(active_names + existing_char_names))
    _, full_alias_map = resolve_aliases_with_map(all_names)
    
    # Map the isolated active_names for this chapter to their true global canonical names
    original_active_names = active_names
    active_names = list(set([full_alias_map.get(n, n) for n in active_names]))
    
    # We only care about the mapping subset that affects THIS chapter's characters
    alias_map = {k: v for k, v in full_alias_map.items() if k in original_active_names or v in original_active_names}
    
    # A1 FIX: Build _char_event_index AFTER alias resolution, keyed on canonical char_id.
    # The old pre-alias index was keyed on raw LLM names; after alias collapsing the
    # lookup keys didn't match, silently returning empty event lists for every character.
    _char_event_index: Dict[str, list] = defaultdict(list)
    for _evt in events:
        for _ic in _evt.get("involved_characters", []):
            _canon_id = normalize_id(full_alias_map.get(_ic, _ic))
            _char_event_index[_canon_id].append(_evt)

    # 2.6 Propagate Gender Predictions to Canonical Names
    raw_genders = intelligence.get("character_genders", {})
    predicted_genders = {}
    for raw_name, gender in raw_genders.items():
        # Look up the newly resolved canonical name, or fall back to the raw name
        canon = full_alias_map.get(raw_name, raw_name)
        predicted_genders[canon] = gender
    
    logger.info(f"Intelligence extracted ({len(active_names)} active characters after alias collapsing). Updating relational graph...")
    
    # 3. Graph Updates
    # Add characters to graph; store aliases on node so RAG entity-matching can find them (A3)
    for name in active_names:
        char_id = normalize_id(name)
        char_aliases_for_node = sorted({
            alias for alias, canon in alias_map.items() if canon == name and alias != name
        })
        graph.add_character(char_id, {
            "display_name": name,
            "last_seen_chapter": chapter_counter,
            "aliases": char_aliases_for_node,
        })
    # Create events to represent character interactions this chapter
    if events:
        # First pass: Create all scenes and store their generated IDs
        scene_ids_seen = set()
        for event_data in events:
            scene_id = event_data.get("scene_id")
            if scene_id and scene_id not in scene_ids_seen:
                scene_ids_seen.add(scene_id)
                global_scene_id = f"chapter_{chapter_counter}_scene_{scene_id}"
                location = event_data.get("location", "Unknown")
                action_summary = event_data.get("action_summary", "A scene")
                graph.add_scene(global_scene_id, chapter_counter, location, action_summary)

        # Second pass: Create all events and store their generated IDs
        event_ids: list[str] = []
        for idx, event_data in enumerate(events):
            action_summary = event_data.get("action_summary", "Unknown Event")
            involved_chars = event_data.get("involved_characters", [])
            
            # Map involved_chars using the global full_alias_map
            involved_chars = list(set([full_alias_map.get(n, n) for n in involved_chars]))
            
            # P1 FIX: Accept characters that are active this chapter OR already exist in the graph.
            # The old filter only allowed active_names, silently dropping cross-chapter references
            # (e.g. Achille, Sophie, Andre) and leaving them with zero graph events.
            all_graph_char_ids = {normalize_id(n) for n, d in graph.graph.nodes(data=True)
                                  if d.get("type") == "character"}
            active_char_ids = {normalize_id(n) for n in active_names}

            valid_chars = []
            for _n in involved_chars:
                _cid = normalize_id(_n)
                if _cid in active_char_ids or _cid in all_graph_char_ids:
                    valid_chars.append(_cid)
            
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
                    timeline_type=event_data.get("timeline_type", "present"),
                    narrative_order=event_data.get("narrative_order", idx + 1),
                    story_time_rank=event_data.get("story_time_rank"),
                    story_time_relative=event_data.get("story_time_relative"),
                    flashback_depth=event_data.get("flashback_depth", 0),
                    reveal_point=event_data.get("reveal_point", 0),
                    spoiler_level=event_data.get("spoiler_level", 0),
                    is_canonical=event_data.get("is_canonical", True),
                    confidence=event_data.get("confidence", 1.0),
                    character_roles=event_data.get("character_roles"),
                )

                # Phase 2.9: Character POV Knowledge Edges
                # Process 'known_by'
                known_by = event_data.get("known_by", [])
                for kb in known_by:
                    kb_canon = full_alias_map.get(kb, kb)
                    kb_id = normalize_id(kb_canon)
                    if kb_id in all_graph_char_ids or kb_id in active_char_ids:
                        graph.add_knowledge_edge(kb_id, event_id, "knows")

                # Process 'unaware_of'
                unaware_of = event_data.get("unaware_of", [])
                for uo in unaware_of:
                    uo_canon = full_alias_map.get(uo, uo)
                    uo_id = normalize_id(uo_canon)
                    if uo_id in all_graph_char_ids or uo_id in active_char_ids:
                        graph.add_knowledge_edge(uo_id, event_id, "unaware_of")

                # Add event to scene
                scene_id = event_data.get("scene_id")
                if scene_id:
                    global_scene_id = f"chapter_{chapter_counter}_scene_{scene_id}"
                    graph.add_event_to_scene(event_id, global_scene_id)

                # P3: Upsert direct character-to-character co-occurrence edges for every
                # pair of participants so relationship queries don't need to traverse events.
                for _i in range(len(valid_chars)):
                    for _j in range(_i + 1, len(valid_chars)):
                        graph.add_or_update_character_edge(
                            valid_chars[_i], valid_chars[_j],
                            relation_type=relation_type,
                            chapter_id=chapter_counter,
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

    # ── P4: Pre-compute all LLM wiki updates in a SINGLE batch call ──────────
    # Build a payload for every active character that has new events this chapter.
    # New characters (not yet in runtime_db) always need a profile call.
    # Existing characters only need one if they have new events.
    _batch_payload: Dict[str, dict] = {}
    for _name in active_names:
        _cid = normalize_id(_name)
        _char_events = _char_event_index[_cid]  # A1: use canonical char_id key
        _event_block = "\n".join([f"- {e.get('action_summary')}" for e in _char_events])
        if not _event_block:
            continue  # No events → no LLM call needed (existing logic handles this)
        _existing_md = get_character_wiki_content(story_uuid, _cid) if _cid in runtime_db else ""

        # Include relevant text snippets so the LLM has prose context, not just bullets.
        # Extract sentences mentioning the character name (up to 500 chars to stay within limits).
        _text_mentions = []
        for _sentence in text.replace('\n', ' ').split('.'):
            if _name.lower() in _sentence.lower():
                _text_mentions.append(_sentence.strip() + '.')
        _text_context = ' '.join(_text_mentions)[:500] if _text_mentions else ""

        _batch_payload[_cid] = {
            "name": _name,
            "existing_wiki": _existing_md,
            "new_events": _event_block,
            "text_context": _text_context,
        }

    # Execute the batch (one LLM call instead of N). Falls back to sequential internally.
    _batch_profiles: Dict[str, dict] = {}
    if _batch_payload:
        logger.info(f"P4: Batch wiki update for {len(_batch_payload)} characters (1 LLM call)")
        _batch_profiles = batch_update_character_profiles(_batch_payload)

    # 4. Update Story Engine State (Runtime tracking)
    # B3: Compute PageRank ONCE for all characters — reuse the scores dict in the loop
    # instead of calling nx.pagerank() once per character (N calls on the same graph).
    _pagerank_cache: Dict[str, float] = graph.compute_chapter_scores(
        current_chapter=chapter_counter, decay_rate=decay_rate
    )

    for name in active_names:
        char_id = normalize_id(name)
        
        # B3: Read from cached scores instead of recomputing PageRank
        new_score = _pagerank_cache.get(char_id, 0.0)
        
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

            # Build event block for this character — A1: use char_id key
            char_events_new = _char_event_index[char_id]
            event_text_block_new = "\n".join([f"- {e.get('action_summary')}" for e in char_events_new])

            # P4: Use pre-fetched batch profile; fall back to individual call if missing
            if event_text_block_new:
                first_profile = _batch_profiles.get(char_id) or update_character_profile("", event_text_block_new, name)
            else:
                first_profile = {}

            # Build aliases list: all surface forms from this chapter that map to this character
            char_aliases = sorted({alias for alias, canon in alias_map.items() if canon == name and alias != name})

            # Build a skeleton wiki, then apply LLM profile through apply_profile_updates
            # so all the same placeholder-filtering logic that protects existing characters
            # also protects new characters (previously raw .get() let "Unknown" through).
            base_wiki = CharacterWiki(
                character_id=char_id,
                display_name=name,
                aliases=char_aliases,
                short_description=f"Appeared in Chapter {chapter_counter}.",
                gender=predicted_gender,
                first_appearance_chapter=chapter_counter,
                last_updated_chapter=chapter_counter,
                confidence=new_score,
            )
            wiki_entry = apply_profile_updates(base_wiki, first_profile)
            save_character_wiki(story_uuid, wiki_entry)

            # DPQ: evaluate graduation immediately in case they dominate the chapter
            char = runtime_db[char_id]
            did_graduate = check_graduation_status(char, wiki_traits={"gender": wiki_entry.gender or predicted_gender}, node_count=len(runtime_db))
            if did_graduate:
                logger.info(f"New Character {char.character_id} graduated via DPQ! Assigned Voice: {char.voice_id}")
                wiki_entry = wiki_entry.model_copy(update={"voice_id": char.voice_id})
                save_character_wiki(story_uuid, wiki_entry)
                
        else:
            # ── Existing Character Update ──────────────────────────────────
            char = runtime_db[char_id]
            char.last_seen_chapter = chapter_counter
            char.mention_count += 1
            char.confidence_score = new_score

            # Find what happened to them this chapter — A1: use char_id key
            char_events_this_chapter = _char_event_index[char_id]
            event_text_block = "\n".join([f"- {e.get('action_summary')}" for e in char_events_this_chapter])

            # A2: Increment dialogue_count for events with conversational intensity
            char.dialogue_count += sum(
                1 for e in char_events_this_chapter
                if e.get("intensity", 1) >= 2
            )

            # Load existing wiki from JSON sidecar (auto-migrates .md if needed)
            old_wiki = load_character_wiki_json(story_uuid, char_id)

            if not event_text_block:
                # No new events — skip the LLM call and the save entirely (no change)
                did_graduate = check_graduation_status(char, wiki_traits={"gender": old_wiki.gender if old_wiki else None}, node_count=len(runtime_db))
                if did_graduate:
                    logger.info(f"Character {char.character_id} graduated (no events)! Voice: {char.voice_id}")
                    if old_wiki:
                        old_wiki = old_wiki.model_copy(update={"voice_id": char.voice_id, "confidence": char.confidence_score})
                        save_character_wiki(story_uuid, old_wiki)
                runtime_db[char_id] = char
                continue

            # Fetch the existing markdown for the LLM context (so it can write prose)
            existing_wiki_md = get_character_wiki_content(story_uuid, char_id)

            # P4: Use pre-fetched batch profile; fall back to individual call if missing
            profile_data = _batch_profiles.get(char_id) or update_character_profile(existing_wiki_md, event_text_block, name)

            # Graduation Check & Voice Locking
            did_graduate = check_graduation_status(char, wiki_traits=profile_data, node_count=len(runtime_db))
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
    _active_char_ids = {normalize_id(n) for n in active_names}
    for char_id, char in runtime_db.items():
        if char_id not in _active_char_ids:
            # They didn't appear, but their score decays due to time passing
            # B3: Use cached scores where available; fall back to individual call for absent chars
            decayed_score = _pagerank_cache.get(char_id) or graph.get_character_importance(
                char_id, current_chapter=chapter_counter, decay_rate=decay_rate
            )
            char.confidence_score = decayed_score

            # C2 FIX: Track voice_id BEFORE calling check_graduation_status so we can
            # distinguish upward graduation from de-graduation in the log message.
            old_voice = char.voice_id
            changed = check_graduation_status(char, node_count=len(runtime_db))
            if changed and old_voice is not None and char.voice_id is None:
                # De-graduation: score decayed below EXTRA threshold → voice released
                logger.info(f"Character {char_id} score decayed below threshold. Voice lock released.")
                # Sync voice_id=None to the on-disk wiki sidecar so disk and
                # runtime stay consistent (the sidecar still had the old voice_id).
                decayed_wiki = load_character_wiki_json(story_uuid, char_id)
                if decayed_wiki and decayed_wiki.voice_id is not None:
                    updated_wiki = decayed_wiki.model_copy(
                        update={"voice_id": None, "confidence": char.confidence_score}
                    )
                    save_character_wiki(story_uuid, updated_wiki)
            elif changed and char.voice_id is not None:
                logger.info(f"Character {char_id} graduated during decay pass. Voice: {char.voice_id}")

    # Atomically save all changes to disk
    graph.save_graph()
    save_runtime(story_uuid, chapter_counter, runtime_db)
    
    # Trigger batched arc detection every 5 chapters
    if chapter_counter > 0 and chapter_counter % 5 == 0:
        logger.info(f"Triggering batched arc detection at chapter {chapter_counter}")
        try:
            detect_arcs(story_uuid, every_n=5)
        except Exception as e:
            logger.error(f"Arc detection failed: {e}")

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
    _scraper = None  # lazy-init once if any chapter needs URL scraping
    
    if os.path.exists(_CANCEL_FLAG):
        os.remove(_CANCEL_FLAG)
        logger.info("Cleared old cancel_ingestion.flag")
    
    for i, chap_data in enumerate(chapters):
        if os.path.exists(_CANCEL_FLAG):
            logger.info("Batch ingestion cancelled by user.")
            break
            
        title = chap_data.get("title", f"Chapter {i+1}")
        text = chap_data.get("text")
        
        if not text:
            # If text is missing, we might need to scrape it here if a URL is present
            url = chap_data.get("url")
            if url:
                if _scraper is None:
                    from app.services.scrapers.royalroad_scraper import RoyalRoadScraper
                    _scraper = RoyalRoadScraper()
                try:
                    scraped = _scraper.scrape_chapter(url)
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
            with open(_CANCEL_FLAG, "w") as f:
                f.write(f"error: {err_msg}")
            break
        
        if progress_callback is not None:
            progress_callback(i + 1, total)
            
    return ingested_chapters
