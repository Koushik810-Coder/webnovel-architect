import re
import spacy
from typing import Dict, Any

from app.core.logger import get_logger

logger = get_logger(__name__)

# Load spaCy model at the module level
# Disable unused components for performance
try:
    nlp = spacy.load("en_core_web_sm", disable=["parser", "tagger", "lemmatizer", "attribute_ruler", "tok2vec"])
    # Process each chapter as a single unit — no chunking.
    # Raise max_length well above any realistic web-novel chapter size (~2 M chars ≈ 400 k words).
    nlp.max_length = 2_000_000
    
    # Layer 2 — Fantasy Booster (EntityRuler)
    ruler = nlp.add_pipe("entity_ruler", before="ner", config={"overwrite_ents": True})
    
    patterns = [
        # Generic Fallbacks (Lowest Priority - Placed first so later rules overwrite them)
        # Two consecutive capitalized words
        {"label": "PERSON", "pattern": [{"IS_TITLE": True}, {"IS_TITLE": True}]},
        
        # Title + Name (e.g., Lord Stark, Lady Elara)
        {"label": "PERSON", "pattern": [
            {"LOWER": {"IN": ["lord", "lady", "sir", "king", "queen", "prince", "princess", "duke", "duchess", "master", "madam", "emperor", "empress", "elder"]}}, 
            {"IS_TITLE": True}
        ]},
        # Names containing apostrophes or hyphen-like characters (e.g., Vael'Thar)
        {"label": "PERSON", "pattern": [{"TEXT": {"REGEX": r"^[A-Z][a-z]+['\-][A-Z]?[a-z]+$"}}]},
        
        # Fictional Ranks (Tier-3 Mage, Level 5, Inner Disciple)
        {"label": "RANK", "pattern": [{"TEXT": {"REGEX": r"(?i)^tier-\d+$"}}, {"IS_TITLE": True, "OP": "?"}]},
        {"label": "RANK", "pattern": [{"LOWER": "tier"}, {"TEXT": "-"}, {"IS_DIGIT": True}, {"IS_TITLE": True, "OP": "?"}]},
        {"label": "RANK", "pattern": [{"LOWER": "level"}, {"IS_DIGIT": True}]},
        {"label": "RANK", "pattern": [{"LOWER": "inner"}, {"LOWER": "disciple"}]},
        {"label": "RANK", "pattern": [{"LOWER": "outer"}, {"LOWER": "disciple"}]},
        {"label": "RANK", "pattern": [{"LOWER": "core"}, {"LOWER": "disciple"}]},
        
        # Magic Systems
        {"label": "MAGIC_SYSTEM", "pattern": [{"LOWER": "mana"}, {"LOWER": "core"}]},
        {"label": "MAGIC_SYSTEM", "pattern": [{"LOWER": "spirit"}, {"LOWER": "root"}]},
        {"label": "MAGIC_SYSTEM", "pattern": [{"IS_TITLE": True}, {"LOWER": "aura"}]},
        {"label": "MAGIC_SYSTEM", "pattern": [{"IS_TITLE": True}, {"LOWER": "qi"}]},
        
        # Locations / Realms
        {"label": "LOC", "pattern": [{"IS_TITLE": True}, {"LOWER": "realm"}]},
        {"label": "LOC", "pattern": [{"IS_TITLE": True}, {"IS_TITLE": True}, {"LOWER": "realm"}]},
        {"label": "LOC", "pattern": "Upper Realm"},
        {"label": "LOC", "pattern": "Lower Realm"},
        
        # Factions
        {"label": "FACTION", "pattern": [{"IS_TITLE": True}, {"LOWER": "sect"}]},
        {"label": "FACTION", "pattern": [{"IS_TITLE": True}, {"IS_TITLE": True}, {"LOWER": "sect"}]},
        {"label": "FACTION", "pattern": [{"IS_TITLE": True}, {"LOWER": "clan"}]},
        {"label": "FACTION", "pattern": [{"IS_TITLE": True}, {"IS_TITLE": True}, {"LOWER": "clan"}]},
        {"label": "FACTION", "pattern": [{"IS_TITLE": True}, {"LOWER": "guild"}]},
        {"label": "FACTION", "pattern": [{"IS_TITLE": True}, {"IS_TITLE": True}, {"LOWER": "guild"}]}
    ]
    ruler.add_patterns(patterns)
except OSError:
    logger.warning("spaCy model 'en_core_web_sm' not found. Please run: python -m spacy download en_core_web_sm")
    nlp = None

def extract_chapter_intelligence(text: str) -> Dict[str, Any]:
    """
    Analyzes chapter text using a hybrid spaCy NER pipeline.
    Returns metrics to update the Story Intelligence Engine.
    """
    if nlp is None:
        raise RuntimeError("spaCy model 'en_core_web_sm' is not installed. Please run: python -m spacy download en_core_web_sm")
        
    logger.debug("Starting spaCy-based NER extraction")
    
    # Process the entire chapter text as one document — no chunking.
    doc = nlp(text)
    
    # Common spaCy false positives
    STOP_ENTITIES = {
        "first day", "last night", "the day", "today", "tomorrow", "yesterday",
        "this morning", "tonight", "this year", "next year", "every day",
        "next week", "last week", "one day"
    }
    
    # Extract PERSON entities, strip whitespace, preserve case, and deduplicate
    names = set()
    world_terms = set()
    
    for ent in doc.ents:
        clean_name = ent.text.strip()
        
        # Normalize: Strip trailing possessives ("Gavle's" -> "Gavle")
        clean_name = re.sub(r"['’]s$", "", clean_name)
        
        if clean_name.lower() in STOP_ENTITIES:
            continue
            
        if ent.label_ == "PERSON":
            # Normalize: Strip generic titles if matched (so "Lord Gavle" -> "Gavle")
            clean_name = re.sub(r"^(Lord|Lady|Sir|King|Queen|Prince|Princess|Duke|Duchess|Master|Madam|Emperor|Empress|Elder)\s+", "", clean_name, flags=re.IGNORECASE)
            if clean_name:
                names.add(clean_name)
                
        elif ent.label_ in ["ORG", "GPE", "LOC", "RANK", "FACTION", "MAGIC_SYSTEM"]:
            if clean_name:
                world_terms.add(clean_name)
    
    # Sort for consistency
    potential_characters = sorted(list(names))
    extracted_world_terms = sorted(list(world_terms))
    
    # 1. Detect Dialogue (Still using simple regex to count dialogue blocks)
    dialogue_pattern = r'"([^"]*)"'
    dialogues = re.findall(dialogue_pattern, text)
    dialogue_count = len(dialogues)
    
    return {
        "active_character_names": potential_characters,
        "active_world_terms": extracted_world_terms,
        "dialogue_count_total": dialogue_count,
        # Mock raw_entities to maintain backwards compatibility with other modules if needed
        "raw_entities": {name: 1 for name in potential_characters}
    }

def extract_chapter_intelligence_llm(text: str, model: str = "gemini/gemini-2.5-flash") -> Dict[str, Any]:
    """
    Analyzes chapter text using an LLM.
    Returns metrics to update the Story Intelligence Engine.
    """
    from adapters.llm_adapter import analyze_text_json
    
    prompt = f"""
    Analyze the following chapter text and extract these elements:
    1. 'active_character_names': A list of unique character names present in the text. Normalize titles (e.g., return "Stark" instead of "Lord Stark").
    2. 'active_world_terms': A list of unique world-building terms like locations, factions, magical systems, and ranks.
    3. 'events': A list of significant events occurring in this chapter. Structure these as Dynamic Event Units (DEUs). Each event must have:
        - 'action_summary': A brief string describing the action, e.g., "Lucian fights the Forest Troll".
        - 'involved_characters': A list of character names involved.
        - 'pre_conditions': A brief description of the state or situation *before* the event.
        - 'post_conditions': A brief description of the state or situation *after* the event.
        - 'location': The location where the event takes place (if mentioned, otherwise "Unknown").
        - 'causes_event_indexes': An array of integers representing the zero-based indices of other events in this list that this specific event directly causes or leads to. Leave empty if none.
    
    Also count the approximate number of times dialogue occurs (dialogue blocks enclosed in quotes). Return this as an integer 'dialogue_count_total'.
    
    Respond STRICTLY with a valid JSON object matching this schema:
    {{
        "active_character_names": ["Name1", "Name2"],
        "active_world_terms": ["Location1", "Faction1"],
        "dialogue_count_total": 5,
        "events": [
            {{
                "action_summary": "Character1 discovers the ancient artifact",
                "involved_characters": ["Character1"],
                "pre_conditions": "Character1 is searching the ruins.",
                "post_conditions": "Character1 gains magical powers.",
                "location": "Ancient Ruins",
                "causes_event_indexes": []
            }}
        ]
    }}
    
    Chapter Text:
    {text}
    """
    
    logger.debug(f"Starting LLM-based intelligence extraction using {model}")
    result = analyze_text_json(prompt, model=model)
    
    if not result:
        raise ValueError("Failed to extract intelligence. The LLM response was empty or invalid JSON.")
        
    active_characters = result.get("active_character_names", [])
    if not isinstance(active_characters, list): active_characters = []
    
    active_world_terms = result.get("active_world_terms", [])
    if not isinstance(active_world_terms, list): active_world_terms = []
        
    dialogue_count = result.get("dialogue_count_total", 0)
    if not isinstance(dialogue_count, int):
        try:
            dialogue_count = int(dialogue_count)
        except (ValueError, TypeError):
            dialogue_count = 0
        
    events = result.get("events", [])
    if not isinstance(events, list):
        events = []
        
    # Deduplicate and sort
    active_characters = sorted(list(set(active_characters)))
    active_world_terms = sorted(list(set(active_world_terms)))
    
    return {
        "active_character_names": active_characters,
        "active_world_terms": active_world_terms,
        "dialogue_count_total": dialogue_count,
        "events": events,
        "raw_entities": {name: 1 for name in active_characters}
    }

def estimate_demographics(text: str, character_name: str) -> Dict[str, str]:
    """
    Estimates gender, age, and simple vocal traits from text context.
    """
    return {}
