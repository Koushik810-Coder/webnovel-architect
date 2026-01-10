from app.services.voice_provider_dummy import DummyVoiceProvider
from app.core.constants import NARRATOR_VOICE_ID

voice_provider = DummyVoiceProvider()

def render_segments(segments):
    audio_chunks = []

    for segment in segments:
        voice_id = segment.voice_id or NARRATOR_VOICE_ID
        audio = voice_provider.synthesize(segment.text, voice_id)
        audio_chunks.append(audio)

    return audio_chunks
