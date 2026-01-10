from app.core.voice_provider import VoiceProvider

class DummyVoiceProvider:
    def select_voice(self, vocal_traits: dict) -> str:
        # Deterministic, cheap, predictable
        return "dummy_voice_deep_male"

    def synthesize(self, text: str, voice_id: str) -> bytes:
        return b""  # no audio yet
