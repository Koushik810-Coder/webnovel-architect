from app.core.ids import generate_character_id
from app.core.models.character_wiki import CharacterWiki
from app.core.models.character_runtime import CharacterRuntime

# Temporary in-memory storage
CHARACTER_WIKI = {}
CHARACTER_RUNTIME = {}

def create_character(
    name: str,
    short_description: str,
    first_chapter: int
):
    character_id = generate_character_id()

    wiki = CharacterWiki(
        character_id=character_id,
        display_name=name,
        short_description=short_description,
        first_appearance_chapter=first_chapter,
        last_updated_chapter=first_chapter
    )

    runtime = CharacterRuntime(
        character_id=character_id,
        first_seen_chapter=first_chapter,
        last_seen_chapter=first_chapter
    )

    CHARACTER_WIKI[character_id] = wiki
    CHARACTER_RUNTIME[character_id] = runtime

    return {
        "wiki": wiki,
        "runtime": runtime
    }
