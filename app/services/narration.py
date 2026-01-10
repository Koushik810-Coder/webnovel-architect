import re
from app.core.models.narration import NarrationSegment
from app.services.characters import CHARACTER_WIKI, CHARACTER_RUNTIME

DIALOGUE_REGEX = re.compile(r'"([^"]+)"')

def find_character_by_name(text: str):
    for character_id, wiki in CHARACTER_WIKI.items():
        if wiki.display_name in text:
            return character_id
    return None


def build_narration_segments(chapter_text: str):
    segments = []

    for line in chapter_text.split("\n"):
        line = line.strip()
        if not line:
            continue

        matches = DIALOGUE_REGEX.findall(line)

        if matches:
            for dialogue in matches:
                character_id = find_character_by_name(line)
                voice_id = None

                if character_id:
                    runtime = CHARACTER_RUNTIME.get(character_id)
                    voice_id = runtime.voice_id if runtime else None

                segments.append(
                    NarrationSegment(
                        text=dialogue,
                        character_id=character_id,
                        voice_id=voice_id
                    )
                )
        else:
            segments.append(NarrationSegment(text=line))

    return segments
