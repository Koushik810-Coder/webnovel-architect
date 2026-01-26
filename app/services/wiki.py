import os
from app.core.models.character_wiki import CharacterWiki

WIKI_DIR = "c:\\Projects\\webnovel-architect\\wiki"

def ensure_wiki_dir():
    if not os.path.exists(WIKI_DIR):
        os.makedirs(WIKI_DIR)

def save_character_wiki(character: CharacterWiki):
    """
    Saves a character's canon data to a human-readable Markdown file.
    These files serve as the "Source of Truth" for readers and authors.
    """
    ensure_wiki_dir()
    filename = f"{character.character_id}.md"
    filepath = os.path.join(WIKI_DIR, filename)
    
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
"""
    
    with open(filepath, "w") as f:
        f.write(content)

def get_character_wiki(character_id: str) -> CharacterWiki:
    # Logic to load md and parse back to object would go here
    pass
