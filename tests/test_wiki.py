"""
tests/test_wiki.py
==================
TDD tests for the wiki service: save → parse round-trip fidelity.

All tests follow the Red-Green-Refactor cycle.
"""

import pytest

from app.core.models.character_wiki import CharacterWiki
from app.core.story_manager import StoryManager
from app.services.wiki import (
    save_character_wiki,
    get_character_wiki_content,
    parse_character_wiki,
)
from adapters.graph_adapter import _graph_instances


@pytest.fixture(autouse=True)
def isolated_env(tmp_path, monkeypatch):
    monkeypatch.setattr(StoryManager, "DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setattr(StoryManager, "TRASH_DIR", str(tmp_path / "_trash"))
    _graph_instances.clear()
    yield
    _graph_instances.clear()


@pytest.fixture
def full_wiki():
    return CharacterWiki(
        character_id="alice",
        display_name="Alice",
        short_description="Hero of the story.",
        long_description="Alice is a brave warrior who fights dragons.",
        first_appearance_chapter=1,
        last_updated_chapter=3,
        confidence=0.85,
        status="Alive",
        age="22",
        gender="Female",
        species="Human",
        role="Protagonist",
        affiliations=["Fighters Guild", "Order of Light"],
        appearance="Tall with auburn hair and piercing green eyes.",
        personality_traits=["Brave", "Compassionate", "Stubborn"],
        notable_quirks=["Hums when nervous", "Taps left foot when thinking"],
    )


@pytest.fixture
def story_id():
    return StoryManager.create_story("Wiki Test Story")


# ── 1. Basic round-trip: all fields survive save → parse ─────────────────────

def test_status_survives_round_trip(story_id, full_wiki):
    save_character_wiki(story_id, full_wiki)
    md = get_character_wiki_content(story_id, "alice")
    parsed = parse_character_wiki(md)
    assert parsed.get("status") == "Alive"

def test_gender_survives_round_trip(story_id, full_wiki):
    save_character_wiki(story_id, full_wiki)
    md = get_character_wiki_content(story_id, "alice")
    parsed = parse_character_wiki(md)
    assert parsed.get("gender") == "Female"


def test_age_survives_round_trip(story_id, full_wiki):
    save_character_wiki(story_id, full_wiki)
    md = get_character_wiki_content(story_id, "alice")
    parsed = parse_character_wiki(md)
    assert parsed.get("age") == "22"


def test_species_survives_round_trip(story_id, full_wiki):
    save_character_wiki(story_id, full_wiki)
    md = get_character_wiki_content(story_id, "alice")
    parsed = parse_character_wiki(md)
    assert parsed.get("species") == "Human"


def test_role_survives_round_trip(story_id, full_wiki):
    save_character_wiki(story_id, full_wiki)
    md = get_character_wiki_content(story_id, "alice")
    parsed = parse_character_wiki(md)
    assert parsed.get("role") == "Protagonist"


def test_affiliations_survive_round_trip(story_id, full_wiki):
    save_character_wiki(story_id, full_wiki)
    md = get_character_wiki_content(story_id, "alice")
    parsed = parse_character_wiki(md)
    assert parsed.get("affiliations") == ["Fighters Guild", "Order of Light"]


def test_synopsis_survives_round_trip(story_id, full_wiki):
    save_character_wiki(story_id, full_wiki)
    md = get_character_wiki_content(story_id, "alice")
    parsed = parse_character_wiki(md)
    assert "brave warrior" in parsed.get("synopsis", "")


def test_appearance_survives_round_trip(story_id, full_wiki):
    save_character_wiki(story_id, full_wiki)
    md = get_character_wiki_content(story_id, "alice")
    parsed = parse_character_wiki(md)
    assert "auburn hair" in parsed.get("appearance", "")


def test_personality_traits_survive_round_trip(story_id, full_wiki):
    save_character_wiki(story_id, full_wiki)
    md = get_character_wiki_content(story_id, "alice")
    parsed = parse_character_wiki(md)
    traits = parsed.get("personality_traits", [])
    assert "Brave" in traits
    assert "Compassionate" in traits
    assert "Stubborn" in traits


# ── 2. The notable_quirks bleed bug ──────────────────────────────────────────

def test_notable_quirks_do_not_bleed_into_footer(story_id, full_wiki):
    """
    BUG: parse_character_wiki's quirks regex captured the HTML footer
    (<br style='clear: both;'>, ---, **System Meta:**, etc.) as extra quirks.
    After the fix the extracted list must contain exactly the real quirks.
    """
    save_character_wiki(story_id, full_wiki)
    md = get_character_wiki_content(story_id, "alice")
    parsed = parse_character_wiki(md)
    quirks = parsed.get("notable_quirks", [])

    # Must contain real quirks
    assert "Hums when nervous" in quirks
    assert "Taps left foot when thinking" in quirks

    # Must NOT contain footer junk
    for q in quirks:
        assert "System Meta" not in q, f"Footer leaked into quirks: {quirks}"
        assert "---" not in q, f"Footer leaked into quirks: {quirks}"
        assert "<br" not in q, f"HTML leaked into quirks: {quirks}"
        assert "Confidence" not in q, f"Footer leaked into quirks: {quirks}"
        assert "TTS Voice" not in q, f"Footer leaked into quirks: {quirks}"


def test_notable_quirks_exact_count(story_id, full_wiki):
    """Only the 2 real quirks should be returned, not footer junk."""
    save_character_wiki(story_id, full_wiki)
    md = get_character_wiki_content(story_id, "alice")
    parsed = parse_character_wiki(md)
    quirks = parsed.get("notable_quirks", [])
    assert len(quirks) == 2, f"Expected 2 quirks, got {len(quirks)}: {quirks}"


# ── 3. Empty / default values don't corrupt round-trip ───────────────────────

def test_empty_traits_parse_cleanly(story_id):
    wiki = CharacterWiki(
        character_id="bob", display_name="Bob",
        short_description="A minor character.",
        first_appearance_chapter=1, last_updated_chapter=1,
        confidence=0.3,
        # No traits, quirks, affiliations set
    )
    save_character_wiki(story_id, wiki)
    md = get_character_wiki_content(story_id, "bob")
    parsed = parse_character_wiki(md)

    # Must return empty lists, not placeholder text
    assert parsed.get("personality_traits", []) == []
    assert parsed.get("notable_quirks", []) == []
    assert parsed.get("affiliations", []) == []


def test_unknown_fields_stripped_to_empty(story_id):
    """Fields that say 'Unknown' should parse to empty string, not 'Unknown'."""
    wiki = CharacterWiki(
        character_id="carol", display_name="Carol",
        short_description="Mystery person.",
        first_appearance_chapter=2, last_updated_chapter=2,
        confidence=0.2,
        # status, age, species intentionally left None → renders as Unknown
    )
    save_character_wiki(story_id, wiki)
    md = get_character_wiki_content(story_id, "carol")
    parsed = parse_character_wiki(md)

    # Should NOT have "Unknown" as a value — it should be empty string or absent
    assert parsed.get("status", "") != "Unknown"
    assert parsed.get("age", "") != "Unknown"
    assert parsed.get("species", "") != "Unknown"


# ── 4. Ingest update path: parsed data flows back correctly ──────────────────

def test_parsed_data_applied_to_new_wiki_entry(story_id, full_wiki):
    """
    Simulate what ingest.py does after parse_character_wiki:
    the parsed dict must be rich enough to rebuild a CharacterWiki
    with all key fields populated.
    """
    save_character_wiki(story_id, full_wiki)
    md = get_character_wiki_content(story_id, "alice")
    profile_data = parse_character_wiki(md)

    # Simulate ingest.py creating a new wiki_entry and applying profile_data
    wiki_entry = CharacterWiki(
        character_id="alice",
        display_name="Alice",
        short_description="First appeared in Chapter 1. Last seen in Chapter 3.",
        first_appearance_chapter=1,
        last_updated_chapter=4,
        confidence=0.9,
    )
    if profile_data.get("synopsis"):
        wiki_entry.long_description = profile_data["synopsis"]
    if profile_data.get("status"):
        wiki_entry.status = profile_data["status"]
    if profile_data.get("age"):
        wiki_entry.age = str(profile_data["age"])
    if profile_data.get("gender"):
        wiki_entry.gender = str(profile_data["gender"])
    if profile_data.get("species"):
        wiki_entry.species = profile_data["species"]
    if profile_data.get("role"):
        wiki_entry.role = profile_data["role"]
    if profile_data.get("appearance"):
        wiki_entry.appearance = profile_data["appearance"]
    if isinstance(profile_data.get("affiliations"), list):
        wiki_entry.affiliations = profile_data["affiliations"]
    if isinstance(profile_data.get("personality_traits"), list):
        wiki_entry.personality_traits = profile_data["personality_traits"]
    if isinstance(profile_data.get("notable_quirks"), list):
        wiki_entry.notable_quirks = profile_data["notable_quirks"]

    assert wiki_entry.status == "Alive"
    assert wiki_entry.age == "22"
    assert wiki_entry.gender == "Female"
    assert wiki_entry.species == "Human"
    assert wiki_entry.role == "Protagonist"
    assert "auburn hair" in (wiki_entry.appearance or "")
    assert "Fighters Guild" in wiki_entry.affiliations
    assert "Brave" in wiki_entry.personality_traits
    assert "Hums when nervous" in wiki_entry.notable_quirks
    # Verify quirk count is not inflated by footer junk
    assert len(wiki_entry.notable_quirks) == 2
