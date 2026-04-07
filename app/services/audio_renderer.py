from app.core.constants import NARRATOR_VOICE_ID

_voice_provider = None

def get_voice_provider():
    global _voice_provider
    if _voice_provider is None:
        from app.services.voice_provider_dummy import DummyVoiceProvider
        _voice_provider = DummyVoiceProvider()
    return _voice_provider
def render_segments(segments):
    audio_chunks = []

    for segment in segments:
        voice_id = segment.voice_id or NARRATOR_VOICE_ID
        audio = get_voice_provider().synthesize(segment.text, voice_id)
        audio_chunks.append(audio)

    return audio_chunks
