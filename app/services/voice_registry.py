import json
import os
import random
from typing import Dict, List, Set, Optional

from app.core.logger import get_logger
logger = get_logger(__name__)

VOICES_JSON_PATH = "models/voices.json"
VOICE_STATE_PATH = "output/voice_allocations.json" # To persist allocations across runs (optional but good)

class VoiceRegistry:
    def __init__(self, voices_path: str = VOICES_JSON_PATH):
        self.voices_path = voices_path
        self.voices_db: Dict[str, dict] = {}
        
        # Categorized lists of voice IDs
        self.male_voices: List[str] = []
        self.female_voices: List[str] = []
        self.neutral_voices: List[str] = []
        
        # Track reserved voices to prevent duplicates
        self.reserved_voices: Set[str] = set()
        
        self._load_voices()

    def _load_voices(self):
        if not os.path.exists(self.voices_path):
            logger.warning(f"{self.voices_path} not found. VoiceRegistry will be empty.")
            return
            
        try:
            with open(self.voices_path, 'r', encoding='utf-8') as f:
                self.voices_db = json.load(f)
                
            for voice_id, details in self.voices_db.items():
                gender = details.get("gender", "Neutral").lower()
                if gender == "male":
                    self.male_voices.append(voice_id)
                elif gender == "female":
                    self.female_voices.append(voice_id)
                else:
                    self.neutral_voices.append(voice_id)
                    
            logger.info(f"VoiceRegistry loaded: {len(self.male_voices)} Male, {len(self.female_voices)} Female, {len(self.neutral_voices)} Neutral voices.")
        except Exception as e:
            logger.error(f"Error loading {self.voices_path}: {e}")

        # Load persisted allocations
        if os.path.exists(VOICE_STATE_PATH):
            try:
                with open(VOICE_STATE_PATH, 'r', encoding='utf-8') as f:
                    allocated = json.load(f)
                    self.reserved_voices = set(allocated)
                logger.info(f"Loaded {len(self.reserved_voices)} reserved voices from state.")
            except Exception as e:
                logger.error(f"Failed to load voice state: {e}")

    def _save_voices(self):
        try:
            os.makedirs(os.path.dirname(VOICE_STATE_PATH), exist_ok=True)
            with open(VOICE_STATE_PATH, 'w', encoding='utf-8') as f:
                json.dump(list(self.reserved_voices), f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save voice state: {e}")

    def get_voice_id(self, character_id: str, gender: str = "neutral", age_group: str = "adult") -> Optional[str]:
        """
        Retrieves an unassigned voice ID matching the constraints, pseudo-randomly driven by character_id hash.
        """
        gender = gender.lower()
        pool = self.neutral_voices
        
        if gender == "male":
             pool = self.male_voices
        elif gender == "female":
             pool = self.female_voices

        # Filter out already reserved voices
        available = [vid for vid in pool if vid not in self.reserved_voices]
        
        # Fallback 1: Try mixed/neutral if preferred gender is exhausted
        if not available:
            logger.warning(f"No available {gender} voices. Falling back to neutral/other.")
            fallback_pool = self.female_voices + self.male_voices + self.neutral_voices
            available = [vid for vid in fallback_pool if vid not in self.reserved_voices]
            
        # Fallback 2: If ALL voices are reserved, allow reuse (last resort)
        if not available:
            logger.warning("VoiceRegistry exhausted! Reusing a voice.")
            available = pool if pool else list(self.voices_db.keys())
            
        if not available:
            return "en-US-GuyNeural" # Absolute fallback
            
        # Deterministic pseudo-random selection based on character_id
        import hashlib
        hash_val = int(hashlib.md5(character_id.encode('utf-8')).hexdigest(), 16)
        
        # Sort available first to ensure determinism across different runs if same set is available
        available.sort()
        selected_voice = available[hash_val % len(available)]
        
        self.reserved_voices.add(selected_voice)
        self._save_voices()
        
        logger.debug(f"Assigned voice '{selected_voice}' to character '{character_id}'.")
        return selected_voice
        
    def release_voice(self, voice_id: str):
        """Allow a voice to be reused if a character is removed."""
        if voice_id in self.reserved_voices:
            logger.debug(f"Releasing voice '{voice_id}' back to pool.")
            self.reserved_voices.remove(voice_id)
            self._save_voices()
