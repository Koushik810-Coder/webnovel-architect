"""
tests/test_voice_registry.py
============================
Tests for the VoiceRegistry state machine — gender-based voice allocation,
pool exhaustion fallbacks, and voice recycling via release_voice.
"""

import pytest
import json
from app.services.voice_registry import VoiceRegistry


MOCK_VOICES = {
    "en-US-GuyNeural":    {"gender": "Male",   "description": "Guy"},
    "en-US-DavisNeural":  {"gender": "Male",   "description": "Davis"},
    "en-US-JennyNeural":  {"gender": "Female", "description": "Jenny"},
    "en-US-AriaNeural":   {"gender": "Female", "description": "Aria"},
    "en-US-SaraNeural":   {"gender": "Female", "description": "Sara"},
    "en-US-NeutralVoice": {"gender": "Neutral","description": "Neutral"},
}


@pytest.fixture
def voices_file(tmp_path):
    """Write MOCK_VOICES to a temp JSON file and return its path."""
    p = tmp_path / "voices.json"
    p.write_text(json.dumps(MOCK_VOICES))
    return str(p)


@pytest.fixture
def registry(voices_file):
    return VoiceRegistry(voices_path=voices_file)


# ── Loading ───────────────────────────────────────────────────────────────────

def test_registry_loads_voices(registry):
    assert len(registry.male_voices) == 2
    assert len(registry.female_voices) == 3
    assert len(registry.neutral_voices) == 1


def test_registry_with_missing_file(tmp_path):
    """Registry must not crash when voices.json does not exist."""
    reg = VoiceRegistry(voices_path=str(tmp_path / "nonexistent.json"))
    assert reg.male_voices == []
    assert reg.female_voices == []
    assert reg.neutral_voices == []


# ── Allocation ────────────────────────────────────────────────────────────────

def test_get_male_voice(registry):
    voice = registry.get_voice_id(character_id="char1", gender="male")
    assert voice in MOCK_VOICES
    assert MOCK_VOICES[voice]["gender"] == "Male"


def test_get_female_voice(registry):
    voice = registry.get_voice_id(character_id="char2", gender="female")
    assert voice in MOCK_VOICES
    assert MOCK_VOICES[voice]["gender"] == "Female"


def test_allocated_voice_is_reserved(registry):
    """A voice allocated once must not be handed out again."""
    voice1 = registry.get_voice_id(character_id="char1", gender="male")
    voice2 = registry.get_voice_id(character_id="char2", gender="male")
    assert voice1 != voice2


def test_all_male_voices_allocated(registry):
    """Exhaust male pool — third request must fall back to another gender or neutral."""
    registry.get_voice_id(character_id="char1", gender="male")
    registry.get_voice_id(character_id="char2", gender="male")
    # Pool exhausted — fallback
    v3 = registry.get_voice_id(character_id="char3", gender="male")
    assert v3 is not None  # Must not crash


# ── Release / Recycle ─────────────────────────────────────────────────────────

def test_release_voice_frees_slot(registry):
    voice1 = registry.get_voice_id(character_id="char1", gender="male")
    registry.release_voice(voice1)
    # The released voice is now available again
    assert voice1 not in registry.reserved_voices


def test_released_voice_can_be_reallocated(registry):
    voice1 = registry.get_voice_id(character_id="char1", gender="male")
    registry.release_voice(voice1)
    voice2 = registry.get_voice_id(character_id="char2", gender="male")
    # voice1 is back in pool, so it could be selected again
    assert voice2 is not None


def test_release_nonexistent_voice_does_not_crash(registry):
    """Releasing a voice that was never reserved must not raise."""
    registry.release_voice("en-US-GhostVoice")  # Not in registry


# ── Exhaustion Fallback ───────────────────────────────────────────────────────

def test_full_pool_exhaustion_returns_something(voices_file):
    """When every voice is reserved, system must still return a voice (reuse)."""
    reg = VoiceRegistry(voices_path=voices_file)
    allocated = []
    for i in range(len(MOCK_VOICES)):
        allocated.append(reg.get_voice_id(character_id=f"char{i}", gender="neutral"))

    # All pool slots taken — next call should still return something
    overflow = reg.get_voice_id(character_id="overflow_char", gender="neutral")
    assert overflow is not None
