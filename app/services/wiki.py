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

def get_character_wiki_content(story_uuid: str, character_id: str) -> str:
    """Reads the current raw markdown content of a character's wiki, or returns empty string if not found."""
    filepath = os.path.join(get_wiki_dir(story_uuid), f"{character_id}.md")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def parse_character_wiki(markdown: str) -> dict:
    """Safely extracts all CharacterWiki fields from the Fandom-style markdown layout using regex."""
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

    # Section boundary: stop at next ## heading OR at the HTML footer (<br, ---, **System)
    SECTION_END = r"(?=\n## |\n<br|\n---|\n\*\*System|$)"

    synopsis_match = re.search(r"## Synopsis\n(.*?)" + SECTION_END, markdown, flags=re.DOTALL)
    if synopsis_match: data["synopsis"] = synopsis_match.group(1).strip()
    
    appearance_match = re.search(r"## Appearance\n(.*?)" + SECTION_END, markdown, flags=re.DOTALL)
    if appearance_match:
        raw_appearance = appearance_match.group(1).replace("Appearance details not recorded.", "").strip()
        data["appearance"] = raw_appearance
    
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

def update_character_profile(existing_wiki_md: str, new_events_text: str, character_name: str) -> dict:
    """
    Uses the LLM to dynamically parse the existing wiki and merge new chapter events into the character's ongoing biography and stats.
    Returns a dictionary of updated Fandom Wiki fields.
    """
    if not new_events_text.strip() and not existing_wiki_md.strip():
        return {}

    from adapters.llm_adapter import analyze_text_json
    
    prompt = f"""
You are the loremaster for a webnovel. Your job is to update the canonical wiki profile of a character named '{character_name}'.

Here is their CURRENT wiki page (which may be empty if this is their first appearance):
---
{existing_wiki_md}
---

Here are the new events that happened to {character_name} in the latest chapter:
---
{new_events_text}
---

Update the character's profile based on the current wiki and these new events. 
Respond STRICTLY with a valid JSON object matching this schema. If a field is unknown, use null or an empty list/string depending on the type. Do NOT use placeholder text like "Unknown" or "Not recorded"—I will handle those in the renderer.
{{
    "synopsis": "A cohesive, chronological biography that seamlessly integrates the new events into their existing history. Keep it narrative and engaging.",
    "status": "Alive, Deceased, Missing, etc.",
    "age": "Their current perceived or stated age. Or null.",
    "gender": "Their gender identity or presentation. Or null.",
    "species": "Their race or species. Or null.",
    "role": "Protagonist, Antagonist, Supporting, Mentor, etc.",
    "affiliations": ["Faction A", "Family B"],
    "appearance": "A cohesive description of how they look.",
    "personality_traits": ["Trait 1", "Trait 2"],
    "notable_quirks": ["Quirk 1", "Quirk 2"]
}}
"""
    try:
        updated_profile = analyze_text_json(prompt, model="gemini/gemini-2.5-flash")
        if not updated_profile:
            return {}
        return updated_profile
    except Exception as e:
        print(f"Warning: Failed to dynamically update profile for {character_name}. Error: {e}")
        return {}
