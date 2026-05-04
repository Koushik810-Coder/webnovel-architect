import json
import os
import re
from typing import Optional
from bs4 import BeautifulSoup

from app.core.models.character_wiki import CharacterWiki
from app.core.story_manager import StoryManager
from app.core.config import get_llm_model
from adapters.llm_adapter import analyze_text_json

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
    # Placeholder strings that LLMs return instead of null — treat as falsy.
    _PLACEHOLDER_STRINGS = {
        "unknown", "n/a", "none", "not recorded", "not available",
        "not specified", "unspecified", "tbd", "to be determined",
        "no information", "no data", "no description", "no description available",
        "detailed history not yet available.", "unassigned",
    }

    def _truthy(v) -> bool:
        if v is None: return False
        if isinstance(v, str):
            stripped = v.strip()
            if not stripped:
                return False
            # Reject LLM placeholder strings like "Unknown", "N/A", etc.
            if stripped.lower() in _PLACEHOLDER_STRINGS:
                return False
            return True
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
            
    # Validate metadata
    metadata = updates.get("metadata")
    if _truthy(metadata) and isinstance(metadata, dict):
        patch["metadata"] = metadata

    # Handle relationships safely to prevent hallucinated strings causing crashes
    rels = updates.get("relationships")
    if _truthy(rels) and isinstance(rels, list):
        valid_rels = [r for r in rels if isinstance(r, dict)]
        if valid_rels:
            patch["relationships"] = valid_rels

    # Append timeline events
    new_timeline_events = updates.get("new_timeline_events")
    if _truthy(new_timeline_events) and isinstance(new_timeline_events, list):
        valid_events = [e for e in new_timeline_events if isinstance(e, dict)]
        if valid_events:
            current_timeline = list(base.timeline)
            current_timeline.extend(valid_events)
            patch["timeline"] = current_timeline

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

def render_pill(text: str, bg_color: str, border_color: str) -> str:
    """Renders a styled HTML pill for arrays like affiliations/aliases."""
    return f'<span style="display: inline-block; background: {bg_color}; border: 1px solid {border_color}; padding: 2px 8px; border-radius: 12px; font-size: 0.85em; margin: 2px;">{text}</span>'

def render_markdown_list(items: list[str], empty_msg: str) -> str:
    """Renders a Markdown bullet list safely."""
    cleaned = [i for i in items if i]
    if not cleaned:
        return empty_msg
    return "\n".join(f"- {i}" for i in cleaned)

def render_tr(label: str, value: Optional[str], label_color: str) -> str:
    """Renders a table row for the info box."""
    val_str = value if value else "<i>Unknown</i>"
    return f'<tr style="border: none; background: transparent;"><td style="padding: 4px 0; border: none;"><b style="color: {label_color};">{label}:</b></td> <td style="padding: 4px 0; border: none;">{val_str}</td></tr>'

def save_character_wiki(story_uuid: str, character: CharacterWiki):
    """
    Saves a character's canon data to:
      1. A human-readable Markdown file (for readers / GitHub wiki).
      2. A JSON sidecar (structured source-of-truth for the engine).
    """
    ensure_wiki_dir(story_uuid)
    filepath = os.path.join(get_wiki_dir(story_uuid), f"{character.character_id}.md")

    # Format lists
    affiliations_clean = [a for a in (character.affiliations or []) if a]
    affiliations_html = " ".join([render_pill(a, "rgba(163, 190, 140, 0.15)", "rgba(163, 190, 140, 0.4)") for a in affiliations_clean]) if affiliations_clean else "<i>None</i>"
    
    aliases_clean = [a for a in (character.aliases or []) if a]
    aliases_html = " ".join([render_pill(a, "rgba(180, 142, 173, 0.15)", "rgba(180, 142, 173, 0.4)") for a in aliases_clean]) if aliases_clean else "<i>None</i>"

    traits_str = render_markdown_list(character.personality_traits or [], "Personality details not recorded.")
    quirks_str = render_markdown_list(character.notable_quirks or [], "No notable quirks documented.")

    # Timeline formatting
    timeline_str = "No events recorded."
    if character.timeline:
        timeline_str = "\n".join([f"- **Ch. {ev.get('chapter', '?')}**: {ev.get('event', '')}" for ev in character.timeline])
        
    # Relationships formatting
    relationships_str = "No relationships recorded."
    if character.relationships:
        # Create a Mermaid diagram
        mermaid_lines = ["```mermaid", "graph TD"]
        for rel in character.relationships:
            raw_target = rel.get('target_id') or 'Unknown'
            raw_relation = rel.get('relation') or 'Unknown'
            target = str(raw_target).replace(" ", "_").replace("'", "").replace('"', '')
            relation = str(raw_relation).replace('"', "'")
            mermaid_lines.append(f'    {character.character_id} -->|"{relation}"| {target}')
        mermaid_lines.append("```\n")
        
        rel_list = "\n".join([f"- **{rel.get('target_id') or 'Unknown'}** ({rel.get('relation') or 'Unknown'}): {rel.get('context') or ''}" for rel in character.relationships])
        relationships_str = "\n".join(mermaid_lines) + "\n" + rel_list

    # Metadata formatting (for info box)
    metadata_rows = ""
    if character.metadata:
        for k, v in character.metadata.items():
            metadata_rows += render_tr(str(k).title(), str(v).replace(chr(10), " "), "#d08770")

    bio_color = "#a3be8c"
    series_color = "#b48ead"

    content = f"""<div style="float: right; width: 320px; border: 1px solid rgba(128,128,128,0.2); padding: 20px; margin-left: 25px; margin-bottom: 20px; border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.1); background: rgba(128,128,128,0.03);">
<h2 style="text-align: center; margin-top: 0; margin-bottom: 15px; border-bottom: 2px solid #4a90e2; padding-bottom: 10px; font-weight: bold;">{character.display_name}</h2>
<div style="margin-top: 15px;">
<div style="font-size: 0.85em; text-transform: uppercase; letter-spacing: 1.2px; color: #88c0d0; margin-bottom: 8px; font-weight: bold;">Biographical Info</div>
<table style="width: 100%; border-collapse: collapse; font-size: 0.95em; border: none; background: transparent;">
{render_tr("Status", str(character.status).replace(chr(10), ' ') if character.status else None, bio_color)}
{render_tr("Age", str(character.age).replace(chr(10), ' ') if character.age else None, bio_color)}
{render_tr("Gender", str(character.gender).replace(chr(10), ' ') if character.gender else None, bio_color)}
{render_tr("Species", str(character.species).replace(chr(10), ' ') if character.species else None, bio_color)}
{render_tr("Role", str(character.role).replace(chr(10), ' ') if character.role else None, bio_color)}
{metadata_rows}
</table>
<div style="margin-top: 12px; font-size: 0.95em;">
<b style="color: {bio_color}; display: block; margin-bottom: 6px;">Affiliations:</b> 
<div style="line-height: 1.8;">{affiliations_html}</div>
</div>
</div>
<div style="margin-top: 20px;">
<div style="font-size: 0.85em; text-transform: uppercase; letter-spacing: 1.2px; color: #88c0d0; margin-bottom: 8px; font-weight: bold;">Series Info</div>
<table style="width: 100%; border-collapse: collapse; font-size: 0.95em; border: none; background: transparent;">
{render_tr("Debut", f"Chapter {character.first_appearance_chapter}", series_color)}
{render_tr("Latest", f"Chapter {character.last_updated_chapter}", series_color)}
</table>
<div style="margin-top: 12px; font-size: 0.95em;">
<b style="color: {series_color}; display: block; margin-bottom: 6px;">Aliases:</b> 
<div style="line-height: 1.8;">{aliases_html}</div>
</div>
</div>
</div>

# ✨ {character.display_name}

> *{character.short_description}*

## 📖 Synopsis
{character.long_description or "Detailed history not yet available."}

## 👁️ Appearance
{character.appearance or "Appearance details not recorded."}

## 🧠 Personality & Traits
{traits_str}

## 🎭 Quirks & Habits
{quirks_str}

## 🕸️ Relationships
{relationships_str}

## 📜 Timeline
{timeline_str}

<br style="clear: both;">

---
<div style="background: rgba(128,128,128,0.05); padding: 12px 18px; border-left: 4px solid #5e81ac; border-radius: 6px; font-size: 0.9em;">
<b>⚙️ System Meta</b><br>
<b>ID:</b> <code>{character.character_id}</code> &nbsp;|&nbsp; <b>Confidence:</b> {character.confidence} &nbsp;|&nbsp; <b>TTS Voice:</b> <code>{character.voice_id or 'Unassigned'}</code>
</div>
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
    Extracts all CharacterWiki fields from the markdown layout using BeautifulSoup
    and Regex. Used ONLY as a migration fallback — prefer load_character_wiki_json().
    """
    data = {}
    if not markdown.strip():
        return data

    try:
        # Separate HTML part (infobox) from Markdown content
        parts = re.split(r"\n# ", markdown, maxsplit=1)
        html_part = parts[0]
        md_part = "# " + parts[1] if len(parts) > 1 else ""

        soup = BeautifulSoup(html_part, "html.parser")
        
        # 1. Parse InfoBox Table Rows
        for tr in soup.find_all("tr"):
            tds = tr.find_all("td")
            if len(tds) == 2:
                key = tds[0].get_text(strip=True).replace(":", "")
                val = tds[1].get_text(strip=True)
                if val != "Unknown" and val:
                    if key == "Status": data["status"] = val
                    elif key == "Age": data["age"] = val
                    elif key == "Gender": data["gender"] = val
                    elif key == "Species": data["species"] = val
                    elif key == "Role": data["role"] = val
                    elif key == "Debut": 
                        try: data["first_appearance_chapter"] = int(val.replace("Chapter", "").strip())
                        except ValueError: pass
                    elif key == "Latest":
                        try: data["last_updated_chapter"] = int(val.replace("Chapter", "").strip())
                        except ValueError: pass

        # 2. Parse Affiliations and Aliases
        for b in soup.find_all("b"):
            key = b.get_text(strip=True).replace(":", "")
            if key in ["Affiliations", "Aliases"]:
                parent_div = b.find_parent("div")
                if parent_div:
                    spans = parent_div.find_all("span")
                    if spans:
                        vals = [s.get_text(strip=True) for s in spans if s.get_text(strip=True)]
                        if key == "Affiliations":
                            data["affiliations"] = vals
                        elif key == "Aliases":
                            data["aliases"] = vals

        # 3. Parse System Meta (Footer)
        footer_match = re.search(r"<div[^>]*>.*?<b>⚙️ System Meta</b>.*?</div", markdown, flags=re.DOTALL)
        if footer_match:
            footer_soup = BeautifulSoup(footer_match.group(0), "html.parser")
            footer_text = footer_soup.get_text(separator=" ")
            conf_match = re.search(r"Confidence:\s*([0-9.]+)", footer_text)
            if conf_match:
                try: data["confidence"] = float(conf_match.group(1))
                except ValueError: pass
            voice_match = re.search(r"TTS Voice:\s*(\S+)", footer_text)
            if voice_match:
                v = voice_match.group(1).strip()
                if v != "Unassigned":
                    data["voice_id"] = v

        # 4. Parse Markdown Headers & Sections
        name_match = re.search(r"^# ✨ (.+)$", md_part, flags=re.MULTILINE)
        if not name_match:
            name_match = re.search(r"^# (.+)$", md_part, flags=re.MULTILINE)
        if name_match: 
            data["display_name"] = name_match.group(1).strip()

        short_desc_match = re.search(r"^> \*(.*?)\*", md_part, flags=re.MULTILINE)
        if short_desc_match:
            data["short_description"] = short_desc_match.group(1).strip()

        SECTION_END = r"(?=\n## |\n<br|\n---|\n<div)"

        synopsis_match = re.search(r"## (?:📖 )?Synopsis\n(.*?)" + SECTION_END, md_part, flags=re.DOTALL)
        if synopsis_match: 
            val = synopsis_match.group(1).strip()
            if "Detailed history not yet available" not in val:
                data["synopsis"] = val

        appearance_match = re.search(r"## (?:👁️ )?Appearance\n(.*?)" + SECTION_END, md_part, flags=re.DOTALL)
        if appearance_match:
            val = appearance_match.group(1).strip()
            if "Appearance details not recorded" not in val:
                data["appearance"] = val

        traits_match = re.search(r"## (?:🧠 )?Personality & Traits\n(.*?)" + SECTION_END, md_part, flags=re.DOTALL)
        if traits_match:
            lines = traits_match.group(1).strip().split("\n")
            cleaned = [
                l.lstrip("- ").strip() for l in lines
                if l.strip() and "Personality details" not in l
            ]
            if cleaned:
                data["personality_traits"] = cleaned

        quirks_match = re.search(r"## (?:🎭 )?Quirks & Habits\n(.*?)" + SECTION_END, md_part, flags=re.DOTALL)
        if quirks_match:
            lines = quirks_match.group(1).strip().split("\n")
            cleaned = [
                l.lstrip("- ").strip() for l in lines
                if l.strip() and "notable quirks documented" not in l
            ]
            if cleaned:
                data["notable_quirks"] = cleaned

    except Exception as e:
        logger.error(f"Error parsing legacy wiki markdown: {e}")
        
    return data

# ---------------------------------------------------------------------------
# LLM profile update
# ---------------------------------------------------------------------------

def update_character_profile(existing_wiki_md: str, new_events_text: str, character_name: str) -> dict:
    """
    Uses the LLM to merge new chapter events into the character's ongoing biography.
    """
    if not new_events_text.strip() and not existing_wiki_md.strip():
        return {}

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

CRITICAL CONSTRAINTS:
1. FACTUAL ACCURACY: Only extract facts explicitly stated or directly demonstrated in the provided text.
2. NO HALLUCINATIONS: Do not invent, assume, or guess names, places, relationships, traits, ages, or appearances. If a detail is missing, leave it as null or empty.
3. CONSERVATIVE UPDATES: Preserve the current wiki state unless the new events provide a clear canonical change (e.g., a power rank up, a death, or a newly revealed secret).

Respond STRICTLY with a valid JSON object matching this schema.
If a field is genuinely unknown, use null or an empty list — do NOT use placeholder text like "Unknown" or "Not recorded".

{{
    "short_description": "A single punchy sentence (≤20 words) summarising who this character IS — their role, defining trait, or function in the story.",
    "synopsis": "A high-level summary of their chronological biography, combining their timeline into an engaging narrative.",
    "status": "Alive, Deceased, Missing, etc. — or null.",
    "age": "Their current perceived or stated age — or null.",
    "gender": "Their gender identity or presentation — or null.",
    "species": "Their race or species — or null.",
    "role": "Protagonist, Antagonist, Supporting, Mentor, etc. — or null.",
    "affiliations": ["Faction A", "Family B"],
    "appearance": "A cohesive description of how they look.",
    "personality_traits": ["Trait 1", "Trait 2"],
    "notable_quirks": ["Quirk 1", "Quirk 2"],
    "metadata": {{"Power Level": "A-Rank", "Magic Element": "Fire"}},
    "relationships": [{{"target_id": "bob", "relation": "Rival", "context": "Fought in the arena"}}],
    "new_timeline_events": [{{"chapter": 15, "event": "Discovered the hidden sword in the cave"}}]
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


def batch_update_character_profiles(
    characters: dict,
    model: str = None,
) -> dict:
    """Updates multiple character profiles in a single LLM call (P4 optimisation).

    Reduces per-chapter LLM calls from N (one per character) to 1-2.
    Falls back to sequential single-character calls if the batch response is
    malformed or only partially valid, so correctness is never sacrificed.

    Args:
        characters: Dict mapping character_id -> {"name": str, "existing_wiki": str, "new_events": str}
        model: Optional LLM model override.

    Returns:
        Dict mapping character_id -> profile_data dict (same schema as update_character_profile).
    """
    if model is None:
        model = get_llm_model()

    if not characters:
        return {}

    batch_prompt = f"""\
You are the loremaster for a serialized web novel. For EACH character below, update their wiki
profile based on their existing wiki (if any) and the new events from this chapter.

Return a single JSON object where each KEY is the character_id (lowercase, underscored) and
the VALUE is that character's updated profile dict.

CRITICAL CONSTRAINTS (apply to EVERY character):
1. FACTUAL ACCURACY: Only extract facts explicitly stated or directly demonstrated in the provided text.
2. NO HALLUCINATIONS: Do not invent, assume, or guess names, places, relationships, traits, ages, or appearances.
3. MISSING DATA: If a detail is genuinely unknown, use null or an empty list. Do NOT write placeholder text like "Unknown", "N/A", "Not recorded", or "Not specified".
4. CONSERVATIVE UPDATES: Preserve existing wiki info unless the new events provide a clear canonical change.
5. SHORT DESCRIPTIONS: Must be a single punchy sentence (≤20 words) describing who this character IS — NOT just their name.

Each character's profile dict MUST match this exact schema:
{{
    "short_description": "A single punchy sentence (≤20 words) describing who this character IS — their role, defining trait, or function in the story.",
    "synopsis": "A cohesive chronological narrative biography covering their full story arc so far.",
    "status": "Alive, Deceased, Missing, etc. — or null.",
    "age": "Their stated or inferred age as a string — or null.",
    "gender": "Their gender — or null.",
    "species": "Their race or species — or null.",
    "role": "Protagonist, Antagonist, Supporting, Mentor, etc. — or null.",
    "affiliations": ["Faction A", "Group B"],
    "appearance": "A cohesive physical description inferred from context.",
    "personality_traits": ["Trait 1", "Trait 2", "Trait 3"],
    "notable_quirks": ["Quirk 1", "Quirk 2"],
    "metadata": {{}},
    "relationships": [{{"target_id": "character_id", "relation": "Rival", "context": "Brief context"}}],
    "new_timeline_events": [{{"chapter": 5, "event": "Description of what happened"}}]
}}

Characters to update:
{json.dumps(characters, indent=2, ensure_ascii=False)}
"""

    try:
        result = analyze_text_json(batch_prompt, model=model)
        if not isinstance(result, dict):
            logger.warning("Batch wiki update returned non-dict — falling back to sequential.")
            return _sequential_fallback(characters, model)

        # Validate: every expected character_id must be present and be a dict
        missing = [cid for cid in characters if cid not in result or not isinstance(result[cid], dict)]
        if missing:
            logger.warning(
                f"Batch wiki update missing/invalid entries for {missing} — falling back to sequential for those."
            )
            fallback_chars = {cid: characters[cid] for cid in missing}
            result.update(_sequential_fallback(fallback_chars, model))

        logger.info(f"Batch wiki update succeeded for {list(result.keys())}")
        return result

    except Exception as e:
        logger.error(f"Batch wiki update failed ({e}) — falling back to sequential.")
        return _sequential_fallback(characters, model)


def _sequential_fallback(characters: dict, model: str) -> dict:
    """Runs update_character_profile() sequentially for each character.

    Used when the batch call fails or returns incomplete results.
    """
    results = {}
    for char_id, char_data in characters.items():
        name = char_data.get("name", char_id)
        existing_wiki = char_data.get("existing_wiki", "")
        new_events = char_data.get("new_events", "")
        profile = update_character_profile(existing_wiki, new_events, name)
        if profile:
            results[char_id] = profile
    return results




# ---------------------------------------------------------------------------
# P5: Text-mention fallback helpers for characters with no graph events
# ---------------------------------------------------------------------------

def _gather_text_mentions(
    story_uuid: str,
    character_id: str,
    character_name: str,
    max_chapters: int = 5,
) -> str:
    """Scans raw chapter texts for lines mentioning character_name.

    Returns a combined snippet string (up to 10 matching lines per chapter)
    capped at the most recent `max_chapters` chapters.
    """
    chapters_dir = os.path.join(StoryManager.DATA_DIR, story_uuid, "chapters")
    if not os.path.exists(chapters_dir):
        return ""

    chapter_ids = sorted(os.listdir(chapters_dir))[-max_chapters:]
    snippets = []
    name_lower = character_name.lower()

    for ch_id in chapter_ids:
        text_path = os.path.join(chapters_dir, ch_id, "text.txt")
        if not os.path.exists(text_path):
            continue
        with open(text_path, "r", encoding="utf-8") as f:
            text = f.read()
        lines = [ln.strip() for ln in text.splitlines() if name_lower in ln.lower() and ln.strip()]
        if lines:
            snippets.append(f"[Ch {ch_id}]: " + " | ".join(lines[:10]))

    return "\n".join(snippets)


def _enrich_from_text_mentions(
    character_name: str,
    mention_context: str,
    model: str = None,
) -> dict:
    """Calls the LLM with raw text-mention snippets to produce a basic character profile.

    Used as a fallback when the story graph has no events for a character.
    """
    if model is None:
        model = get_llm_model()

    prompt = f"""
    Based ONLY on the following mentions of '{character_name}' found in a web novel,
    write a brief character profile. Return a JSON object with these keys:
    short_description, role, personality_traits (list), and any other
    details you can reliably infer. Do NOT hallucinate — if a field is unknown, use null.

    Mentions:
    {mention_context}
    """
    result = analyze_text_json(prompt, model=model)
    return result if isinstance(result, dict) else {}


def enrich_wiki_from_rag(
    story_uuid: str, 
    character_id: str,
    mode: str = "god",
    reader_chapter: int = 999,
    pov_character_id: Optional[str] = None
) -> Optional[CharacterWiki]:
    """
    Re-generates a character's wiki by querying the full story graph with
    Time-CoT RAG (rather than the per-chapter extractor).
    """
    from app.services.rag import query_character_profile
    from app.services.wiki_versioning import compute_node_hash
    from adapters.graph_adapter import get_graph_engine
    import datetime

    existing = load_character_wiki_json(story_uuid, character_id)
    if existing is None:
        logger.warning(f"enrich_wiki_from_rag: no existing wiki for '{character_id}' — skipping.")
        return None

    # Check cache via graph snapshot hash
    graph_provider = get_graph_engine(story_uuid)
    current_hash = compute_node_hash(graph_provider.graph, character_id)
    
    if existing.graph_snapshot_id == current_hash and current_hash != "":
        logger.info(f"Skipping RAG enrichment for '{character_id}' — graph neighborhood unchanged.")
        return existing

    character_name = existing.display_name
    logger.info(f"RAG-enriching wiki for '{character_name}' ({character_id})…")
    
    existing_json_str = existing.model_dump_json(indent=2)
    profile_data = query_character_profile(
        story_uuid, 
        character_id, 
        character_name, 
        existing_wiki_json=existing_json_str,
        mode=mode,
        reader_chapter=reader_chapter,
        pov_character_id=pov_character_id
    )
    if not profile_data:
        # P5 FALLBACK: No graph events → scan raw chapter texts for text-based mentions
        logger.warning(
            f"RAG returned empty profile for '{character_id}' (no graph events). "
            f"Attempting text-mention fallback."
        )
        mention_context = _gather_text_mentions(story_uuid, character_id, character_name, max_chapters=5)
        if mention_context:
            profile_data = _enrich_from_text_mentions(character_name, mention_context)
        if not profile_data:
            logger.warning(f"No events or text mentions for '{character_id}' — skipping enrichment.")
            return None

    enriched = apply_profile_updates(existing, profile_data)
    
    # Update versioning meta
    enriched.version = existing.version + 1
    enriched.graph_snapshot_id = current_hash
    enriched.generated_at = datetime.datetime.utcnow().isoformat()
    
    save_character_wiki(story_uuid, enriched)
    logger.info(f"Wiki enriched and saved for '{character_name}'.")
    return enriched


def enrich_all_wikis_from_rag(
    story_uuid: str,
    mode: str = "god",
    reader_chapter: int = 999,
    pov_character_id: Optional[str] = None
) -> dict:
    """
    Batch-enriches every character wiki in a story using RAG.
    """
    wiki_dir = get_wiki_dir(story_uuid)
    if not os.path.isdir(wiki_dir):
        logger.warning(f"No wiki directory for story '{story_uuid}'.")
        return {"enriched": [], "skipped": []}

    enriched, skipped = [], []

    for filename in os.listdir(wiki_dir):
        if not filename.endswith(".json"):
            continue
        character_id = filename[:-5]  # strip .json
        result = enrich_wiki_from_rag(
            story_uuid, 
            character_id,
            mode=mode,
            reader_chapter=reader_chapter,
            pov_character_id=pov_character_id
        )
        if result:
            enriched.append(character_id)
        else:
            skipped.append(character_id)

    logger.info(
        f"RAG batch enrichment complete for story '{story_uuid}': "
        f"{len(enriched)} enriched, {len(skipped)} skipped."
    )
    return {"enriched": enriched, "skipped": skipped}
