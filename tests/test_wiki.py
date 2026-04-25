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
    save_character_wiki_json,
    load_character_wiki_json,
    get_character_wiki_content,
    parse_character_wiki,
    apply_profile_updates,
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


# ── 5. _apply_profile_updates: field-merge logic ─────────────────────────────

class TestApplyProfileUpdates:
    """
    apply_profile_updates(base, updates) must:
    - Apply non-empty LLM fields on top of base
    - NOT erase base fields when LLM omits them
    - NOT apply null / empty-string / empty-list values from LLM
    """

    @pytest.fixture
    def base(self):
        return CharacterWiki(
            character_id="alice",
            display_name="Alice",
            short_description="Hero of the story.",
            long_description="Alice is a brave warrior.",
            status="Alive",
            age="22",
            gender="Female",
            species="Human",
            role="Protagonist",
            affiliations=["Fighters Guild"],
            appearance="Auburn hair.",
            personality_traits=["Brave"],
            notable_quirks=["Hums when nervous"],
            first_appearance_chapter=1,
            last_updated_chapter=3,
            confidence=0.85,
        )

    def test_non_empty_field_overrides_base(self, base):
        updates = {"status": "Deceased"}
        result = apply_profile_updates(base, updates)
        assert result.status == "Deceased"

    def test_synopsis_maps_to_long_description(self, base):
        updates = {"synopsis": "Alice eventually defeated the dragon."}
        result = apply_profile_updates(base, updates)
        assert result.long_description == "Alice eventually defeated the dragon."

    def test_base_field_preserved_when_llm_omits_it(self, base):
        """LLM omits 'age' — base value must survive."""
        updates = {"status": "Wounded"}  # no 'age' key
        result = apply_profile_updates(base, updates)
        assert result.age == "22"

    def test_base_field_preserved_when_llm_sends_null(self, base):
        """LLM sends null for 'appearance' — base value must survive."""
        updates = {"appearance": None}
        result = apply_profile_updates(base, updates)
        assert result.appearance == "Auburn hair."

    def test_base_field_preserved_when_llm_sends_empty_string(self, base):
        """LLM sends '' for 'role' — base value must survive."""
        updates = {"role": ""}
        result = apply_profile_updates(base, updates)
        assert result.role == "Protagonist"

    def test_base_field_preserved_when_llm_sends_empty_list(self, base):
        """LLM sends [] for 'personality_traits' — base list must survive."""
        updates = {"personality_traits": []}
        result = apply_profile_updates(base, updates)
        assert result.personality_traits == ["Brave"]

    def test_list_field_overridden_when_llm_sends_non_empty(self, base):
        updates = {"personality_traits": ["Cunning", "Resilient"]}
        result = apply_profile_updates(base, updates)
        assert result.personality_traits == ["Cunning", "Resilient"]

    def test_base_model_is_not_mutated(self, base):
        """apply_profile_updates must return a new object, never mutate base."""
        updates = {"status": "Deceased"}
        apply_profile_updates(base, updates)
        assert base.status == "Alive"  # original unchanged

    def test_short_description_updated_by_llm(self, base):
        updates = {"short_description": "A legendary knight."}
        result = apply_profile_updates(base, updates)
        assert result.short_description == "A legendary knight."

    def test_new_timeline_events_appended(self, base):
        """Timeline events must be appended, not overwritten."""
        base.timeline = [{"chapter": 1, "event": "Born"}]
        updates = {"new_timeline_events": [{"chapter": 2, "event": "Started walking"}]}
        result = apply_profile_updates(base, updates)
        assert len(result.timeline) == 2
        assert result.timeline[1]["event"] == "Started walking"
        assert len(base.timeline) == 1  # Base should not be mutated
        
    def test_metadata_and_relationships_applied(self, base):
        """Metadata and relationships from LLM should overwrite base."""
        updates = {
            "metadata": {"Power": "S-Class"},
            "relationships": [{"target_id": "bob", "relation": "Friend"}]
        }
        result = apply_profile_updates(base, updates)
        assert result.metadata == {"Power": "S-Class"}
        assert result.relationships[0]["target_id"] == "bob"

    def test_placeholder_strings_rejected_as_falsy(self, base):
        """LLM placeholder strings like 'Unknown' must NOT overwrite real data."""
        updates = {
            "status": "Unknown",
            "age": "N/A",
            "species": "unknown",
            "role": "Not specified",
            "appearance": "No description available",
            "short_description": "Detailed history not yet available.",
        }
        result = apply_profile_updates(base, updates)
        # All base values must be preserved — placeholders must be rejected
        assert result.status == "Alive"
        assert result.age == "22"
        assert result.species == "Human"
        assert result.role == "Protagonist"
        assert result.appearance == "Auburn hair."
        assert result.short_description == "Hero of the story."


# ── 6. JSON sidecar: save/load round-trip ────────────────────────────────────

class TestJsonSidecar:

    def test_json_roundtrip_all_fields(self, story_id, full_wiki):
        """save_character_wiki_json → load_character_wiki_json must preserve all fields."""
        save_character_wiki_json(story_id, full_wiki)
        loaded = load_character_wiki_json(story_id, "alice")
        assert loaded is not None
        assert loaded.character_id == "alice"
        assert loaded.display_name == "Alice"
        assert loaded.status == "Alive"
        assert loaded.age == "22"
        assert loaded.gender == "Female"
        assert loaded.species == "Human"
        assert loaded.role == "Protagonist"
        assert loaded.affiliations == ["Fighters Guild", "Order of Light"]
        assert "auburn hair" in (loaded.appearance or "")
        assert "Brave" in loaded.personality_traits
        assert "Hums when nervous" in loaded.notable_quirks
        assert loaded.first_appearance_chapter == 1
        assert loaded.last_updated_chapter == 3
        assert loaded.confidence == pytest.approx(0.85)

    def test_load_returns_none_for_unknown_character(self, story_id):
        result = load_character_wiki_json(story_id, "nonexistent_char")
        assert result is None

    def test_save_character_wiki_also_writes_json_sidecar(self, story_id, full_wiki):
        """save_character_wiki (the .md writer) must also write the .json sidecar."""
        import os
        from app.services.wiki import get_wiki_dir
        save_character_wiki(story_id, full_wiki)
        json_path = os.path.join(get_wiki_dir(story_id), "alice.json")
        assert os.path.exists(json_path), "JSON sidecar was not written by save_character_wiki"

    def test_load_json_preferred_over_md(self, story_id, full_wiki):
        """When both .json and .md exist, load picks json (no regex parsing)."""
        save_character_wiki(story_id, full_wiki)
        loaded = load_character_wiki_json(story_id, "alice")
        assert loaded is not None
        assert loaded.confidence == pytest.approx(0.85)

    def test_auto_migration_md_to_json(self, story_id, full_wiki):
        """
        If only a .md file exists (no .json), load_character_wiki_json
        must auto-migrate: parse the .md with regex and produce a .json sidecar.
        Subsequent load must read the sidecar (not parse .md again).
        """
        import os
        from app.services.wiki import get_wiki_dir

        # Write only the .md (bypassing the sidecar co-save)
        ensure_wiki_dir_only(story_id)
        md_path = os.path.join(get_wiki_dir(story_id), "alice.md")
        save_character_wiki(story_id, full_wiki)  # also writes .json
        json_path = os.path.join(get_wiki_dir(story_id), "alice.json")
        os.remove(json_path)  # simulate pre-migration state: only .md

        assert not os.path.exists(json_path), "Setup: json should not exist yet"

        # First load — triggers migration
        loaded = load_character_wiki_json(story_id, "alice")
        assert loaded is not None, "Auto-migration should return a CharacterWiki"
        assert loaded.display_name == "Alice"

        # Second load — reads from newly created sidecar
        assert os.path.exists(json_path), "Migration should have created .json"
        loaded2 = load_character_wiki_json(story_id, "alice")
        assert loaded2 is not None
        assert loaded2.display_name == "Alice"


def ensure_wiki_dir_only(story_id):
    """Helper: ensure the wiki dir exists (used in migration test)."""
    import os
    from app.services.wiki import get_wiki_dir
    os.makedirs(get_wiki_dir(story_id), exist_ok=True)
