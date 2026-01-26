import random
from typing import Dict, Optional

class VoiceProvider:
    """
    Abstract Interface for Voice Providers (ElevenLabs, OpenAI, etc.)
    """
    def get_voice_id(self, gender: str, age_group: str) -> str:
        raise NotImplementedError

class MockVoiceProvider(VoiceProvider):
    """
    Mock provider that returns deterministic dummy IDs.
    """
    def get_voice_id(self, gender: str = "neutral", age_group: str = "adult") -> str:
        # In a real app coverage would be vast.
        # Here we simulate: "voice_male_adult_01"
        
        # Deterministic seed could be added here if needed, but for now random selection 
        # from a finite pool is fine as long as we LOCK it upstream.
        variants = ["01", "02", "03", "04"]
        variant = random.choice(variants)
        return f"voice_{gender}_{age_group}_{variant}"

# Global instance
_provider = MockVoiceProvider()

def assign_voice(traits: Dict[str, str]) -> str:
    """
    Selects a voice ID based on the character's traits.
    """
    gender = traits.get("gender", "neutral").lower()
    age = traits.get("age", "adult").lower()
    
    return _provider.get_voice_id(gender, age)
