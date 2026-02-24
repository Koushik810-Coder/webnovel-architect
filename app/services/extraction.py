import re
from typing import List, Dict, Any, Tuple
from app.core.models.character_runtime import CharacterRuntime
from app.core.models.character_wiki import CharacterWiki

def extract_chapter_intelligence(text: str) -> Dict[str, Any]:
    """
    Analyzes chapter text using basic heuristics (Regex).
    Returns metrics to update the Story Intelligence Engine.
    
    NOTE: This is a prototype implementation.
    Production version should use Named Entity Recognition (NER) models (e.g. spaCy, BERT)
    to distinguish "Rose" (Flower) from "Rose" (Person).
    """
    
    # 1. Detect Dialogue
    # Matches text found between quotes
    dialogue_pattern = r'"([^"]*)"'
    dialogues = re.findall(dialogue_pattern, text)
    dialogue_count = len(dialogues)
    
    # 2. Detect Proper Nouns (Potential Characters)
    # Simple regex for Capitalized words not at starts of sentences would be better,
    # but for now we grab all Capitalized words and filter common stopwords later.
    words = re.findall(r'\b[A-Z][a-z]+\b', text)
    
    # Common words that frequently start sentences and shouldn't be characters
    STOP_WORDS = {
        "The", "A", "An", "And", "But", "Or", "For", "Nor", "So", "Yet",
        "He", "She", "It", "They", "We", "You", "I", "His", "Her", "Their", "Our", "My", "Your",
        "In", "On", "At", "To", "From", "By", "With", "About", "As", "Into", "Through", "During", 
        "Before", "After", "Over", "Under", "Then", "Once", "When", "Where", "Why", "How", "If",
        "Is", "Are", "Was", "Were", "Be", "Been", "Being",
        "Has", "Have", "Had", "Having", "Do", "Does", "Did", "Doing",
        "Will", "Would", "Shall", "Should", "Can", "Could", "May", "Might", "Must",
        "This", "That", "These", "Those", "Which", "Who", "Whom", "Whose", "What",
        "Beware", "Yes", "No", "Oh", "Ah", "Well", "Now", "Here", "There", "Some", "Any",
        "All", "Many", "Few", "Most", "Only", "Same", "Too", "Very"
    }
    
    entity_counts = {}
    for w in words:
        if w not in STOP_WORDS:
            entity_counts[w] = entity_counts.get(w, 0) + 1
        
    potential_characters = [name for name, count in entity_counts.items() if count > 0] # Filter noise
    
    return {
        "active_character_names": potential_characters,
        "dialogue_count_total": dialogue_count,
        # In a real implementation we would attribute dialogue to specific names
        # For this prototype version, we simply return the raw data
        "raw_entities": entity_counts
    }

def estimate_demographics(text: str, character_name: str) -> Dict[str, str]:
    """
    Estimates gender, age, and simple vocal traits from text context.
    """
    # Placeholder for NLP logic
    return {}
