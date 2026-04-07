from abc import ABC, abstractmethod
import os
import asyncio

# Re-exported for convenience so app_ui.py can import from one place

from app.core.logger import get_logger
logger = get_logger(__name__)

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
        logger.info("Loading Kokoro (82M)...")
        try:
            from kokoro_onnx import Kokoro
            # Check if model files exist, otherwise warn (or rely on library error)
            if not os.path.exists("models/kokoro-v0_19.onnx") or not os.path.exists("models/voices-v1.0.bin"):
                logger.warning("Kokoro model files (kokoro-v0_19.onnx, voices-v1.0.bin) not found in 'models/' directory.")
            
            self.engine = Kokoro("models/kokoro-v0_19.onnx", "models/voices-v1.0.bin")
        except ImportError:
            logger.error("kokoro_onnx not installed.")
            self.engine = None
        except Exception as e:
            logger.error(f"Error initializing Kokoro: {e}")
            self.engine = None

    def generate_audio(self, text, voice_id, output_path, **kwargs):
        """
        Generates audio using the Kokoro TTS engine.
        
        Args:
            text (str): The text to synthesize.
            voice_id (str): The voice ID to use for synthesis.
            output_path (str): The destination file path for the output audio.
            **kwargs: Additional parameters like 'speed'.
        """
        speed = kwargs.get('speed', 1.0)
        if self.engine:
            import soundfile as sf
            # kokoro-onnx .create() returns (audio_array, sample_rate)
            samples, sample_rate = self.engine.create(text, voice=voice_id, speed=speed, lang='en-us')
            sf.write(output_path, samples, sample_rate)
        else:
            logger.info(f"[Mock Kokoro] Generated audio for '{text}' to {output_path}")

# 3. The Free Backup (Edge TTS - Online)
class EdgeAdapter(TTSProvider):
    """
    Adapter for the Microsoft Edge TTS engine.
    Runs online and acts as a free fallback if local engines are unavailable.
    """
    
    def generate_audio(self, text, voice_id, output_path, **kwargs):
        """
        Generates audio using the edge-tts library asynchronously.
        
        Args:
            text (str): The text to synthesize.
            voice_id (str): The voice ID to use for synthesis.
            output_path (str): The destination file path for the output audio.
        """
        import edge_tts
        
        async def _run_edge():
            comm = edge_tts.Communicate(text, voice_id)
            await comm.save(output_path)
            
        try:
            asyncio.run(_run_edge())
        except Exception as e:
            logger.error(f"Error running EdgeTTS: {e}")

# 4. The Factory: Decides which one to give you
def get_tts_engine(config_type):
    """
    Factory function to retrieve the appropriate TTS provider based on configuration.
    
    Args:
        config_type (str): The specified TTS engine to use (e.g., 'kokoro', 'edge').
        
    Returns:
        TTSProvider: An instance of a class derived from TTSProvider that handles audio generation.
        
    Raises:
        ValueError: If an unknown config_type is provided.
    """
    if config_type == "kokoro":
        adapter = KokoroAdapter()
        if adapter.engine is None:
            logger.warning("Kokoro unavailable. Falling back to EdgeTTS.")
            return EdgeAdapter()
        return adapter
    elif config_type == "edge":
        return EdgeAdapter()
    else:
        raise ValueError(f"Unknown TTS Engine: {config_type}")
