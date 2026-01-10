from app.services.voice_provider_dummy import DummyVoiceProvider

voice_provider = DummyVoiceProvider()

def cast_voice(vocal_traits: dict) -> str:
    return voice_provider.select_voice(vocal_traits)
