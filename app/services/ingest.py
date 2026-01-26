from datetime import datetime
from typing import Dict
from app.core.models.chapter import Chapter
from app.core.models.character_runtime import CharacterRuntime
from app.core.models.character_wiki import CharacterWiki
from app.services.extraction import extract_chapter_intelligence
from app.services.wiki import save_character_wiki
from app.core.graduation import check_graduation_status

_chapter_counter = 0
_runtime_db: Dict[str, CharacterRuntime] = {}

def normalize_id(name: str) -> str:
    """
    Converts a display name (e.g., 'Lord Stark') to a unique ID (e.g., 'lord_stark').
    Used for linking Wiki entries to Runtime stats.
    """
    return name.lower().replace(" ", "_")

def ingest_chapter(title: str, text: str) -> Chapter:
    global _chapter_counter
    _chapter_counter += 1

    # 1. Create Base Chapter
    chapter = Chapter(
        id=_chapter_counter,
        title=title,
        raw_text=text,
        created_at=datetime.utcnow()
    )
    
    # 2. Extract Intelligence
    # This step parses the raw text to find:
    # - Active Characters (People mentioned or speaking)
    # - Dialogue Counts (Proxy for importance)
    # - Interaction pairs (Network Centrality - Planned Phase 3)
    intelligence = extract_chapter_intelligence(text)
    active_names = intelligence.get("active_character_names", [])
    
    # 3. Update Story Engine State
    for name in active_names:
        char_id = normalize_id(name)
        
        # Runtime Update
        if char_id not in _runtime_db:
            # New Character Discovery
            # We initialize with low confidence (0.1) because a single mention
            # does not guarantee this is a recurring character.
            _runtime_db[char_id] = CharacterRuntime(
                character_id=char_id,
                first_seen_chapter=_chapter_counter,
                last_seen_chapter=_chapter_counter,
                confidence_score=0.1, 
                mention_count=1
            )
            
            # Wiki Proposal (Auto-create for now)
            wiki_entry = CharacterWiki(
                character_id=char_id,
                display_name=name,
                short_description=f"Appeared in Chapter {_chapter_counter}",
                first_appearance_chapter=_chapter_counter,
                last_updated_chapter=_chapter_counter
            )
            save_character_wiki(wiki_entry)
            
        else:
            # Existing Character Update
            char = _runtime_db[char_id]
            char.last_seen_chapter = _chapter_counter
            char.mention_count += 1
            
            # Slow, deterministic confidence growth.
            # +0.05 per chapter ensures a character must appear in ~15 chapters
            # or speak frequently to graduate, preventing one-off characters from being cast.
            char.confidence_score += 0.05 
            
            # Graduation Check & Voice Locking
            did_graduate = check_graduation_status(char)
            if did_graduate:
                print(f"[EVENT] Character {char.character_id} graduated! Assigned Voice: {char.voice_id}")
            
            # Update local state
            _runtime_db[char_id] = char

    return chapter
