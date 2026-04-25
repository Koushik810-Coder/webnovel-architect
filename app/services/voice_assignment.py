from typing import Dict, Optional
from app.services.voice_registry import VoiceRegistry

# Lazy-initialized to avoid parsing the 30MB voices.json at import time.
# Using module-level eager init meant every import of this module (e.g. in
# graduation.py → ingest.py → tests) paid a full file-parse cost even when
# voices were never actually needed.
_registry: VoiceRegistry | None = None


def get_registry() -> VoiceRegistry:
    """Returns the shared VoiceRegistry, initializing it on first call."""
    global _registry
    if _registry is None:
        _registry = VoiceRegistry()
    return _registry


def assign_voice(character_id: str, traits: Optional[Dict[str, str]] = None) -> str:
    """
    Selects a unique voice ID based on the character's traits (gender, age).
    """
    if traits is None:
        traits = {}

    gender = traits.get("gender", "neutral").lower()
    age = traits.get("age", "adult").lower()

    return get_registry().get_voice_id(character_id, gender, age)
