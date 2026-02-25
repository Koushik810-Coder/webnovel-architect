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

def get_character_wiki(story_uuid: str, character_id: str) -> CharacterWiki:
    # Logic to load md and parse back to object would go here
    pass
