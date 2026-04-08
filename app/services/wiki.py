import json
import os
from typing import Optional

from app.core.models.character_wiki import CharacterWiki
from app.core.story_manager import StoryManager

from app.core.logger import get_logger
logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# CharacterWiki merge utility (used by ingest pipeline)
# ---------------------------------------------------------------------------

def apply_profile_updates(base: CharacterWiki, updates: dict) -> CharacterWiki:
    """
    Applies LLM-returned update fields onto an existing CharacterWiki *without*
    erasing previous data. Only fields that are non-null and non-empty in `updates`
    will overwrite the corresponding field in `base`.

    Returns a NEW CharacterWiki; never mutates `base`.
    """
    def _truthy(v) -> bool:
        if v is None: return False
        if isinstance(v, str): return bool(v.strip())
        if isinstance(v, list): return len(v) > 0
        return bool(v)

    field_map = {
        "short_description": "short_description",
        "synopsis": "long_description",
        "status": "status",
        "age": "age",
        "gender": "gender",
        "species": "species",
        "role": "role",
        "appearance": "appearance",
        "affiliations": "affiliations",
        "personality_traits": "personality_traits",
        "notable_quirks": "notable_quirks",
    }

    patch = {}
    for llm_key, wiki_key in field_map.items():
        value = updates.get(llm_key)
        if _truthy(value):
            patch[wiki_key] = value

    return base.model_copy(update=patch)


# ---------------------------------------------------------------------------
# Directory helpers
# ---------------------------------------------------------------------------

def get_wiki_dir(story_uuid: str) -> str:
    return os.path.join(StoryManager.DATA_DIR, story_uuid, "wiki")

def ensure_wiki_dir(story_uuid: str):
    path = get_wiki_dir(story_uuid)
    os.makedirs(path, exist_ok=True)

# ---------------------------------------------------------------------------
# JSON sidecar (primary structured storage)
# ---------------------------------------------------------------------------

def _json_path(story_uuid: str, character_id: str) -> str:
    return os.path.join(get_wiki_dir(story_uuid), f"{character_id}.json")

def save_character_wiki_json(story_uuid: str, character: CharacterWiki):
    """Persists the structured CharacterWiki as a JSON sidecar file."""
    ensure_wiki_dir(story_uuid)
    path = _json_path(story_uuid, character.character_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(character.model_dump(), f, indent=2, ensure_ascii=False)

def load_character_wiki_json(story_uuid: str, character_id: str) -> Optional[CharacterWiki]:
    """
    Loads a CharacterWiki from the JSON sidecar.

    Auto-migration: if no .json exists but a .md does, the .md is parsed with
    the legacy regex parser and the result is immediately persisted as .json so
    subsequent reads are fast and reliable.

    Returns None if neither file exists (truly new character).
    """
    path = _json_path(story_uuid, character_id)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return CharacterWiki(**data)
        except Exception as e:
            logger.warning(f"Corrupt JSON sidecar for {character_id}, falling back to .md: {e}")

    # --- Auto-migration from legacy .md ---
    md_content = get_character_wiki_content(story_uuid, character_id)
    if not md_content:
        return None

    logger.info(f"Auto-migrating wiki for '{character_id}' from .md to .json")
    parsed = parse_character_wiki(md_content)

    # Build a best-effort CharacterWiki from parsed fields
    # Some required fields may be missing; we fall back to safe defaults
    try:
        wiki = CharacterWiki(
            character_id=character_id,
            display_name=parsed.get("display_name", character_id.replace("_", " ").title()),
            short_description=parsed.get("short_description", ""),
            long_description=parsed.get("synopsis"),
            status=parsed.get("status"),
            age=parsed.get("age"),
            gender=parsed.get("gender"),
            species=parsed.get("species"),
            role=parsed.get("role"),
            affiliations=parsed.get("affiliations", []),
            appearance=parsed.get("appearance"),
            personality_traits=parsed.get("personality_traits", []),
            notable_quirks=parsed.get("notable_quirks", []),
            first_appearance_chapter=parsed.get("first_appearance_chapter", 1),
            last_updated_chapter=parsed.get("last_updated_chapter", 1),
            confidence=parsed.get("confidence", 1.0),
            voice_id=parsed.get("voice_id"),
        )
        save_character_wiki_json(story_uuid, wiki)
        return wiki
    except Exception as e:
        logger.error(f"Auto-migration failed for '{character_id}': {e}")
        return None

# ---------------------------------------------------------------------------
# Markdown rendering (human-readable output — not used for reading back)
# ---------------------------------------------------------------------------

def save_character_wiki(story_uuid: str, character: CharacterWiki):
    """
    Saves a character's canon data to:
      1. A human-readable Markdown file (for readers / GitHub wiki).
      2. A JSON sidecar (structured source-of-truth for the engine).
    """
    ensure_wiki_dir(story_uuid)
    filename = f"{character.character_id}.md"
    filepath = os.path.join(get_wiki_dir(story_uuid), filename)

    # Safely format list fields
    affiliations_str = ", ".join(character.affiliations) if character.affiliations else "Unknown"
    aliases_str = ", ".join(character.aliases) if character.aliases else "None"

    traits_list = "\n".join([f"- {t}" for t in character.personality_traits])
    traits_str = traits_list if character.personality_traits else "Personality details not recorded."

    quirks_list = "\n".join([f"- {q}" for q in character.notable_quirks])
    quirks_str = quirks_list if character.notable_quirks else "No notable quirks documented."

    content = f"""<div style="float: right; width: 300px; border: 1px solid rgba(128,128,128,0.2); padding: 15px; margin-left: 20px; background: rgba(128,128,128,0.05); border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
  <h2 style="text-align: center; margin-top: 0; margin-bottom: 5px;">{character.display_name}</h2>
  
  <div style="margin-top: 15px;">
    <b style="font-size: 1.1em; opacity: 0.9;">Biographical Information</b>
    <hr style="margin: 8px 0; border: 0; border-top: 1px solid rgba(128,128,128,0.2);">
    <b>Status:</b> {character.status or "Unknown"}<br>
    <b>Age:</b> {character.age or "Unknown"}<br>
    <b>Gender:</b> {character.gender or "Unknown"}<br>
    <b>Species:</b> {character.species or "Unknown"}<br>
    <b>Role:</b> {character.role or "Unknown"}<br>
    <b>Affiliations:</b> {affiliations_str}<br>
  </div>
  
  <div style="margin-top: 15px;">
    <b style="font-size: 1.1em; opacity: 0.9;">Series Information</b>
    <hr style="margin: 8px 0; border: 0; border-top: 1px solid rgba(128,128,128,0.2);">
    <b>First Appearance:</b> Chapter {character.first_appearance_chapter}<br>
    <b>Last Updated:</b> Chapter {character.last_updated_chapter}<br>
    <b>Aliases:</b> {aliases_str}
  </div>
</div>

# {character.display_name}

{character.short_description}

## Synopsis
{character.long_description or "Detailed history not yet available."}

## Appearance
{character.appearance or "Appearance details not recorded."}

## Personality & Traits
{traits_str}

## Quirks & Habits
{quirks_str}

<br style="clear: both;">

---
**System Meta:**
- ID: `{character.character_id}`
- Confidence: {character.confidence}
- TTS Voice: `{character.voice_id or 'Unassigned'}`
"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    # Always keep the JSON sidecar in sync
    save_character_wiki_json(story_uuid, character)

# ---------------------------------------------------------------------------
# Legacy helpers (kept for auto-migration fallback)
# ---------------------------------------------------------------------------

def get_character_wiki_content(story_uuid: str, character_id: str) -> str:
    """Reads the raw markdown content of a character's wiki, or '' if not found."""
    filepath = os.path.join(get_wiki_dir(story_uuid), f"{character_id}.md")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def parse_character_wiki(markdown: str) -> dict:
    """
    Safely extracts all CharacterWiki fields from the Fandom-style markdown layout
    using regex. Used ONLY as a migration fallback — prefer load_character_wiki_json().
    """
    import re
    data = {}
    if not markdown.strip():
        return data

    status_match = re.search(r"<b>Status:</b> (.*?)<br>", markdown)
    if status_match: data["status"] = status_match.group(1).replace("Unknown", "").strip()

    age_match = re.search(r"<b>Age:</b> (.*?)<br>", markdown)
    if age_match: data["age"] = age_match.group(1).replace("Unknown", "").strip()

    gender_match = re.search(r"<b>Gender:</b> (.*?)<br>", markdown)
    if gender_match: data["gender"] = gender_match.group(1).replace("Unknown", "").strip()

    species_match = re.search(r"<b>Species:</b> (.*?)<br>", markdown)
    if species_match: data["species"] = species_match.group(1).replace("Unknown", "").strip()

    role_match = re.search(r"<b>Role:</b> (.*?)<br>", markdown)
    if role_match: data["role"] = role_match.group(1).replace("Unknown", "").strip()

    affil_match = re.search(r"<b>Affiliations:</b> (.*?)<br>", markdown)
    if affil_match:
        raw_affils = affil_match.group(1).replace("Unknown", "").strip()
        data["affiliations"] = [a.strip() for a in raw_affils.split(",") if a.strip()]

    # Confidence & voice from System Meta block
    conf_match = re.search(r"- Confidence: ([0-9.]+)", markdown)
    if conf_match:
        try: data["confidence"] = float(conf_match.group(1))
        except ValueError: pass

    voice_match = re.search(r"- TTS Voice: `([^`]+)`", markdown)
    if voice_match:
        v = voice_match.group(1).strip()
        if v != "Unassigned":
            data["voice_id"] = v

    # Chapter meta from infobox
    first_ch_match = re.search(r"<b>First Appearance:</b> Chapter (\d+)", markdown)
    if first_ch_match:
        try: data["first_appearance_chapter"] = int(first_ch_match.group(1))
        except ValueError: pass

    last_ch_match = re.search(r"<b>Last Updated:</b> Chapter (\d+)", markdown)
    if last_ch_match:
        try: data["last_updated_chapter"] = int(last_ch_match.group(1))
        except ValueError: pass

    # Heading name (used as display_name fallback during migration)
    name_match = re.search(r"^# (.+)$", markdown, flags=re.MULTILINE)
    if name_match: data["display_name"] = name_match.group(1).strip()

    # Short description: first non-empty line after the infobox closing div
    short_desc_match = re.search(r"</div>\s*\n+# [^\n]+\n+([^\n#<]+)", markdown)
    if short_desc_match:
        data["short_description"] = short_desc_match.group(1).strip()

    # Section boundary stops at the next heading or the HTML footer
    SECTION_END = r"(?=\n## |\n<br|\n---|\n\*\*System|$)"

    synopsis_match = re.search(r"## Synopsis\n(.*?)" + SECTION_END, markdown, flags=re.DOTALL)
    if synopsis_match: data["synopsis"] = synopsis_match.group(1).strip()

    appearance_match = re.search(r"## Appearance\n(.*?)" + SECTION_END, markdown, flags=re.DOTALL)
    if appearance_match:
        raw = appearance_match.group(1).replace("Appearance details not recorded.", "").strip()
        data["appearance"] = raw

    traits_match = re.search(r"## Personality & Traits\n(.*?)" + SECTION_END, markdown, flags=re.DOTALL)
    if traits_match:
        lines = traits_match.group(1).strip().split("\n")
        cleaned = [
            l.lstrip("- ").strip() for l in lines
            if l.strip()
            and not l.startswith("Personality details")
            and not l.startswith("<br")
            and not l.startswith("---")
            and "System Meta" not in l
        ]
        data["personality_traits"] = cleaned

    quirks_match = re.search(r"## Quirks & Habits\n(.*?)" + SECTION_END, markdown, flags=re.DOTALL)
    if quirks_match:
        lines = quirks_match.group(1).strip().split("\n")
        cleaned = [
            l.lstrip("- ").strip() for l in lines
            if l.strip()
            and not l.startswith("No notable quirks")
            and not l.startswith("<br")
            and not l.startswith("---")
            and "System Meta" not in l
            and "Confidence" not in l
            and "TTS Voice" not in l
        ]
        data["notable_quirks"] = cleaned

    return data

# ---------------------------------------------------------------------------
# LLM profile update
# ---------------------------------------------------------------------------

def update_character_profile(existing_wiki_md: str, new_events_text: str, character_name: str) -> dict:
    """
    Uses the LLM to merge new chapter events into the character's ongoing biography.

    Returns a dictionary of updated CharacterWiki fields including:
      - short_description  (punchy one-liner for the wiki header)
      - synopsis           (full chronological biography)
      - status, age, gender, species, role, affiliations
      - appearance, personality_traits, notable_quirks
    """
    if not new_events_text.strip() and not existing_wiki_md.strip():
        return {}

    from adapters.llm_adapter import analyze_text_json
    from app.core.config import get_llm_model

    prompt = f"""
You are the loremaster for a webnovel. Your job is to update the canonical wiki profile of a character named '{character_name}'.

Here is their CURRENT wiki page (may be empty if this is their first appearance):
---
{existing_wiki_md}
---

Here are the new events that happened to {character_name} in the latest chapter:
---
{new_events_text}
---

Update the character's profile based on the current wiki and these new events.
Respond STRICTLY with a valid JSON object matching this schema.
If a field is genuinely unknown, use null or an empty list — do NOT use placeholder text like "Unknown" or "Not recorded".

{{
    "short_description": "A single punchy sentence (≤20 words) summarising who this character IS — their role, defining trait, or function in the story.",
    "synopsis": "A cohesive, chronological biography that seamlessly integrates the new events into their existing history. Keep it narrative and engaging.",
    "status": "Alive, Deceased, Missing, etc. — or null.",
    "age": "Their current perceived or stated age — or null.",
    "gender": "Their gender identity or presentation — or null.",
    "species": "Their race or species — or null.",
    "role": "Protagonist, Antagonist, Supporting, Mentor, etc. — or null.",
    "affiliations": ["Faction A", "Family B"],
    "appearance": "A cohesive description of how they look.",
    "personality_traits": ["Trait 1", "Trait 2"],
    "notable_quirks": ["Quirk 1", "Quirk 2"]
}}
"""
    try:
        updated_profile = analyze_text_json(prompt, model=get_llm_model())
        if not updated_profile:
            return {}
        logger.info(f"Dynamically updated wiki profile for {character_name}")
        return updated_profile
    except Exception as e:
        logger.error(f"Failed to dynamically update profile for {character_name}. Error: {e}")
        return {}
