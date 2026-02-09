from abc import ABC, abstractmethod
import os
import asyncio

# 1. The Contract: Every future breakthrough MUST follow this rule
class TTSProvider(ABC):
    @abstractmethod
    def generate_audio(self, text: str, voice_id: str, output_path: str):
        pass

# 2. The Current Breakthrough (Kokoro - Local CPU)
class KokoroAdapter(TTSProvider):
    def __init__(self):
        print("Loading Kokoro (82M)...")
        try:
            from kokoro_onnx import Kokoro
            # Check if model files exist, otherwise warn (or rely on library error)
            if not os.path.exists("kokoro-v0_19.onnx") or not os.path.exists("voices.json"):
                print("Warning: Kokoro model files (kokoro-v0_19.onnx, voices.json) not found in current directory.")
            
            self.engine = Kokoro("kokoro-v0_19.onnx", "voices.json")
        except ImportError:
            print("Error: kokoro_onnx not installed.")
            self.engine = None
        except Exception as e:
            print(f"Error initializing Kokoro: {e}")
            self.engine = None

    def generate_audio(self, text, voice_id, output_path):
        if self.engine:
            # Maps "hero_voice" to Kokoro's internal ID if needed, 
            # for now passing voice_id directly (e.g., 'af_bella')
            self.engine.create_audio(text, voice_id, output_path)
        else:
            print(f"[Mock Kokoro] Generated audio for '{text}' to {output_path}")

# 3. The Free Backup (Edge TTS - Online)
class EdgeAdapter(TTSProvider):
    def generate_audio(self, text, voice_id, output_path):
        import edge_tts
        
        async def _run_edge():
            comm = edge_tts.Communicate(text, voice_id)
            await comm.save(output_path)
            
        try:
            asyncio.run(_run_edge())
        except Exception as e:
            print(f"Error running EdgeTTS: {e}")

# 4. The Factory: Decides which one to give you
def get_tts_engine(config_type):
    if config_type == "kokoro":
        return KokoroAdapter()
    elif config_type == "edge":
        return EdgeAdapter()
    else:
        raise ValueError(f"Unknown TTS Engine: {config_type}")
