import os
from app.core.models.character_wiki import CharacterWiki
from app.core.story_manager import StoryManager

def get_wiki_dir(story_uuid: str) -> str:
    return os.path.join(StoryManager.DATA_DIR, story_uuid, "wiki")

def ensure_wiki_dir(story_uuid: str):
    path = get_wiki_dir(story_uuid)
    os.makedirs(path, exist_ok=True)

def save_character_wiki(story_uuid: str, character: CharacterWiki):
    """
    Saves a character's canon data to a human-readable Markdown file.
    These files serve as the "Source of Truth" for readers and authors.
    """
    ensure_wiki_dir(story_uuid)
    filename = f"{character.character_id}.md"
    filepath = os.path.join(get_wiki_dir(story_uuid), filename)
    
    content = f"""# {character.display_name}
    
**Role**: {character.role or 'Unknown'}
**Status**: {character.status or 'Unknown'}
**Affiliations**: {", ".join(character.affiliations)}

---

## Description
{character.short_description}

{character.long_description or ""}

## Traits
- { "\\n- ".join(character.personality_traits) }

## System Data
- ID: `{character.character_id}`
- Confidence: {character.confidence}
- Voice: `{character.voice_id or 'Unassigned'}`
"""
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

def get_character_wiki_content(story_uuid: str, character_id: str) -> str:
    """Reads the current raw markdown content of a character's wiki, or returns empty string if not found."""
    filepath = os.path.join(get_wiki_dir(story_uuid), f"{character_id}.md")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def update_character_summary(existing_bio: str, new_events_text: str, character_name: str) -> str:
    """
    Uses the LLM to dynamically merge new chapter events into the character's ongoing biography.
    """
    if not new_events_text.strip():
        return existing_bio

    from adapters.llm_adapter import analyze_text
    
    prompt = f"""
You are the loremaster for a webnovel. Your job is to update the canonical biography of a character named '{character_name}'.

Here is their CURRENT biography (which may be empty if this is their first appearance):
---
{existing_bio}
---

Here are the new events that happened to {character_name} in the latest chapter:
---
{new_events_text}
---

Write a new, cohesive, and chronological biography for {character_name} that seamlessly integrates the new events into their existing history. 
Write ONLY the biography text. Do not include markdown headers or meta-commentary. Keep it narrative and engaging.
"""
    try:
        updated_bio = analyze_text(prompt, model="gemini/gemini-2.5-flash")
        return updated_bio.strip()
    except Exception as e:
        print(f"Warning: Failed to dynamically update bio for {character_name}. Fallback to existing bio. Error: {e}")
        return existing_bio
