import re
from pydantic import BaseModel
from typing import Literal, List, Optional

from app.core.config import get_config, get_llm_model
from adapters.llm_adapter import analyze_text_json
from app.core.models.narration import NarrationSegment
from app.services.voice_assignment import assign_voice
from app.services.ingest import normalize_id


class ScriptBlock(BaseModel):
    type: Literal["narration", "dialogue"]
    text: str


class NarrationBlock(ScriptBlock):
    type: Literal["narration"] = "narration"


class DialogueBlock(ScriptBlock):
    type: Literal["dialogue"] = "dialogue"
    speaker: Optional[str] = None


def parse_chapter_to_script_blocks(chapter_text: str) -> List[ScriptBlock]:
    """
    Deterministically parses a chapter's text into Narration and Dialogue blocks.
    It simply assumes anything between double quotes is dialogue, and everything else is narration.
    """
    blocks: List[ScriptBlock] = []

    chunks = re.split(r'("[^"]*"|"[^"]*")', chapter_text)

    for chunk in chunks:
        stripped = chunk.strip()
        if not stripped:
            continue

        is_standard = stripped.startswith('"') and stripped.endswith('"')
        is_curly = stripped.startswith('\u201c') and stripped.endswith('\u201d')

        if (is_standard or is_curly) and len(stripped) >= 2:
            dialogue_text = stripped[1:-1].strip()
            if dialogue_text:
                blocks.append(DialogueBlock(text=dialogue_text))
        else:
            blocks.append(NarrationBlock(text=stripped))

    return blocks


def resolve_dialogue_speakers(blocks: List[ScriptBlock]) -> List[ScriptBlock]:
    """
    Takes a list of deterministic script blocks and asks the LLM to identify the speaker
    for the dialogue blocks using the surrounding narration as context.
    """
    dialogues = [(i, b) for i, b in enumerate(blocks) if isinstance(b, DialogueBlock)]
    if not dialogues:
        return blocks

    context = []
    for b in blocks:
        if isinstance(b, NarrationBlock):
            context.append(f"Narrator: {b.text}")
        else:
            context.append(f'Quote: "{b.text}"')

    context_str = "\n".join(context)

    quotes_str = ""
    for idx, (_, b) in enumerate(dialogues):
        quotes_str += f'{idx}: "{b.text}"\n'

    prompt = f"""
Given the following context from a story:
{context_str}

Identify the most likely speaker for each of the following quotes based on the context.
{quotes_str}

Return a JSON object in this exact format: {{"speakers": {{"0": "SpeakerName", "1": "SpeakerName"}}}}
If you cannot determine the speaker, or if it is an internal thought without a specific character, use "Narrator". 
Do NOT include any prefix like "Character Name:". Just the name.
"""
    try:
        model = get_llm_model()
        response = analyze_text_json(prompt, model=model)
        if "error" in response:
            cfg = get_config()
            fallback = cfg.get("fallback_llm", "groq/llama-3.1-8b-instant")
            if fallback != model:
                response = analyze_text_json(prompt, model=fallback)

        speakers_map = response.get("speakers", {})
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Speaker resolution failed: {e}")
        speakers_map = {}

    for idx, (original_idx, b) in enumerate(dialogues):
        speaker = speakers_map.get(str(idx), "Narrator")
        blocks[original_idx].speaker = speaker

    return blocks


def build_narration_segments(chapter_text: str, story_uuid: str = None) -> List[NarrationSegment]:
    """
    High-level legacy compatibility wrapper.
    Parses text, resolves speakers, and assigns voices.

    Args:
        chapter_text: Raw text of the chapter to narrate.
        story_uuid: Story identifier used to look up locked voice IDs from the wiki.
                    If None, voices are always freshly assigned (no wiki lookup).

    Returns:
        List[NarrationSegment]: The audio-ready segments.
    """
    from app.services.wiki import load_character_wiki_json  # lazy import avoids circular

    blocks = parse_chapter_to_script_blocks(chapter_text)
    resolved = resolve_dialogue_speakers(blocks)

    segments = []
    for b in resolved:
        speaker = getattr(b, "speaker", "Narrator")
        voice_id = None
        if speaker != "Narrator":
            char_id = normalize_id(speaker)
            # A4 FIX: Prefer the locked voice from the wiki over assigning a new one.
            # assign_voice() may return a different voice than the one persisted during graduation.
            if story_uuid:
                wiki = load_character_wiki_json(story_uuid, char_id)
                voice_id = wiki.voice_id if (wiki and wiki.voice_id) else None
            if not voice_id:
                voice_id = assign_voice(char_id)

        segments.append(NarrationSegment(
            text=b.text,
            character_id=speaker,
            voice_id=voice_id
        ))
    return segments

