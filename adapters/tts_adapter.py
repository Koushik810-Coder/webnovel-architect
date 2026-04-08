from abc import ABC, abstractmethod
import os
import asyncio
import time

# Re-exported for convenience so app_ui.py can import from one place

from app.core.logger import get_logger
logger = get_logger(__name__)

def _truncate(text: str, limit: int = 100) -> str:
    """Helper to truncate text for logging."""
    if not text: return ""
    text = text.replace("\n", " ").strip()
    return (text[:limit] + "..") if len(text) > limit else text

# 1. The Contract: Every future breakthrough MUST follow this rule
class TTSProvider(ABC):
    """
    Abstract base class for all Text-to-Speech providers.
    Every new TTS engine must implement this interface.
    """
    
    @abstractmethod
    def generate_audio(self, text: str, voice_id: str, output_path: str, **kwargs):
        """
        Generates audio from text using the specified voice.

        Args:
            text (str): The text to be synthesized into audio.
            voice_id (str): The identifier for the voice to use.
            output_path (str): The file path where the generated audio will be saved.
        """
        pass

# 2. The Current Breakthrough (Kokoro - Local CPU)
class KokoroAdapter(TTSProvider):
    """
    Adapter for the Kokoro local TTS engine.
    Runs locally on CPU/GPU without rate limits but requires model files.
    """
    
    def __init__(self):
        logger.info("Initializing Kokoro TTS Engine (82M)...")
        start_time = time.perf_counter()
        try:
            from kokoro_onnx import Kokoro
            # Check if model files exist, otherwise warn (or rely on library error)
            if not os.path.exists("models/kokoro-v0_19.onnx") or not os.path.exists("models/voices-v1.0.bin"):
                logger.warning("Kokoro model files (kokoro-v0_19.onnx, voices-v1.0.bin) not found in 'models/' directory.")
            
            self.engine = Kokoro("models/kokoro-v0_19.onnx", "models/voices-v1.0.bin")
            duration = time.perf_counter() - start_time
            logger.info(f"Kokoro Engine loaded successfully in {duration:.2f}s")
        except ImportError:
            logger.error("kokoro_onnx not installed. Please install it to use Kokoro.")
            self.engine = None
        except Exception as e:
            logger.error(f"Error initializing Kokoro: {e}")
            self.engine = None

    def generate_audio(self, text, voice_id, output_path, **kwargs):
        """
        Generates audio using the Kokoro TTS engine.
        """
        speed = kwargs.get('speed', 1.0)
        logger.debug(f"[Kokoro] Generating audio | Voice: {voice_id} | Path: {output_path} | Text: {_truncate(text)}")
        start_time = time.perf_counter()
        
        if self.engine:
            import soundfile as sf
            try:
                # kokoro-onnx .create() returns (audio_array, sample_rate)
                samples, sample_rate = self.engine.create(text, voice=voice_id, speed=speed, lang='en-us')
                sf.write(output_path, samples, sample_rate)
                
                duration = time.perf_counter() - start_time
                logger.info(f"[Kokoro] Audio generation complete in {duration:.2f}s | Path: {output_path}")
            except Exception as e:
                logger.error(f"[Kokoro] Generation failed: {e} | Voice: {voice_id} | Text: {_truncate(text)}")
                raise
        else:
            logger.warning(f"[Mock Kokoro] Generated mock audio for '{_truncate(text)}' to {output_path} (Engine not initialized)")

# 3. The Free Backup (Edge TTS - Online)
class EdgeAdapter(TTSProvider):
    """
    Adapter for the Microsoft Edge TTS engine.
    Runs online and acts as a free fallback if local engines are unavailable.
    """
    
    def generate_audio(self, text, voice_id, output_path, **kwargs):
        """
        Generates audio using the edge-tts library asynchronously.
        """
        import edge_tts
        
        logger.debug(f"[EdgeTTS] Generating audio | Voice: {voice_id} | Path: {output_path} | Text: {_truncate(text)}")
        start_time = time.perf_counter()
        
        async def _run_edge():
            comm = edge_tts.Communicate(text, voice_id)
            await comm.save(output_path)
            
        try:
            asyncio.run(_run_edge())
            duration = time.perf_counter() - start_time
            logger.info(f"[EdgeTTS] Audio generation complete in {duration:.2f}s | Path: {output_path}")
        except Exception as e:
            logger.error(f"[EdgeTTS] Error running EdgeTTS: {e} | Voice: {voice_id} | Text: {_truncate(text)}")

# 4. The Factory: Decides which one to give you
def get_tts_engine(config_type):
    """
    Factory function to retrieve the appropriate TTS provider based on configuration.
    """
    logger.debug(f"Requesting TTS Engine factory for type: {config_type}")
    if config_type == "kokoro":
        adapter = KokoroAdapter()
        if adapter.engine is None:
            logger.warning("Kokoro unavailable during factory init. Falling back to EdgeTTS.")
            return EdgeAdapter()
        return adapter
    elif config_type == "edge":
        return EdgeAdapter()
    else:
        logger.error(f"TTS Factory failed: Unknown TTS Engine '{config_type}'")
        raise ValueError(f"Unknown TTS Engine: {config_type}")
