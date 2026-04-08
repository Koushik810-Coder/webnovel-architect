from typing import Dict, Optional
from app.services.voice_registry import VoiceRegistry

# Global instance
_registry = VoiceRegistry()

def assign_voice(character_id: str, traits: Optional[Dict[str, str]] = None) -> str:
    """
    Selects a unique voice ID based on the character's traits (gender, age).
    """
    if traits is None:
        traits = {}
        
    gender = traits.get("gender", "neutral").lower()
    age = traits.get("age", "adult").lower()
    
    return _registry.get_voice_id(character_id, gender, age)

def get_registry() -> VoiceRegistry:
    return _registry
