from app.core.ids import generate_character_id
from app.core.models.character_wiki import CharacterWiki
from app.core.models.character_runtime import CharacterRuntime
from app.services.ingest import load_runtime, save_runtime
from app.services.wiki import save_character_wiki

def create_character(
    story_uuid: str,
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

    chapter_count, runtime_db = load_runtime(story_uuid)
    runtime_db[character_id] = runtime

    save_character_wiki(story_uuid, wiki)
    save_runtime(story_uuid, chapter_count, runtime_db)

    return {
        "wiki": wiki,
        "runtime": runtime
    }
