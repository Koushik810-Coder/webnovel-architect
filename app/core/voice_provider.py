from typing import Protocol, Dict

class VoiceProvider(Protocol):
    def select_voice(self, vocal_traits: Dict[str, str]) -> str:
        """
        Return a provider-specific voice ID
        based on desired vocal traits.
        """
        ...

    def synthesize(self, text: str, voice_id: str) -> bytes:
        """
        Convert text to audio bytes.
        (Not implemented yet)
        """
        ...
