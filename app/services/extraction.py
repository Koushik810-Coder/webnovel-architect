import re
import spacy
from typing import Dict, Any

from app.core.logger import get_logger
from app.core.config import get_llm_model

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
    
    dialogue_pattern = r'"([^"]*)"'
    dialogues = re.findall(dialogue_pattern, text)
    dialogue_count = len(dialogues)
    
    logger.info(f"spaCy Extraction Complete | {len(potential_characters)} characters | {len(extracted_world_terms)} world terms | {dialogue_count} dialogue blocks")
    
    return {
        "active_character_names": potential_characters,
        "active_world_terms": extracted_world_terms,
        "dialogue_count_total": dialogue_count,
        # Mock raw_entities to maintain backwards compatibility with other modules if needed
        "raw_entities": {name: 1 for name in potential_characters}
    }

def extract_chapter_intelligence_llm(text: str, model: str = None) -> Dict[str, Any]:
    """
    Analyzes chapter text using an LLM.
    Returns metrics to update the Story Intelligence Engine.
    """
    if model is None:
        model = get_llm_model()
    from adapters.llm_adapter import analyze_text_json
    
    prompt = f"""
    Analyze the following chapter text and extract these elements:
    
    CRITICAL: YOU MUST Return a valid JSON object strictly matching this schema. Write your thought process in the "_thought_process" field before generating the arrays.

    SCHEMA:
    {{
        "_thought_process": "Analyze the text for entities and events. Step 1: Filter generic nouns. Step 2: Identify core entities. Step 3: Map events.",
        "active_character_names": ["Name1", "Name2"],
        "character_genders": {{"Name1": "male", "Name2": "female"}},
        "active_world_terms": ["Location1", "Faction1"],
        "dialogue_count_total": 5,
        "events": [
            {{
                "action_summary": "Character1 discovers the ancient artifact",
                "involved_characters": ["Character1"],
                "relation_type": "neutral",
                "intensity": 3,
                "pre_conditions": "Character1 is searching the ruins.",
                "post_conditions": "Character1 gains magical powers.",
                "location": "Ancient Ruins",
                "causes_event_indexes": []
            }}
        ]
    }}

    Rules & Constraints:
    - HALLUCINATION GUARDRAILS: Do NOT list generic time references ("today", "tomorrow", "this morning", "one day") or vague pronouns as entities or world terms.
    - Entities must be specific proper nouns.
    - 'active_character_names': Unique character names. Normalize titles (e.g., return "Stark" instead of "Lord Stark").
    - 'character_genders': Map names to "male", "female", or "neutral".
    - 'active_world_terms': Unique world-building terms (locations, factions, magical systems, ranks).
    - 'events': List of significant events. Must follow strictly the intensity rubric:
      1=Minor passing mention, 2=Brief casual conversation, 3=Significant sustained conversation/minor argument, 4=Major argument/physical altercation, 5=Life-altering event.
    - 'relation_type' must be ONE of: "friendly", "hostile", "combat", "neutral", "mentor", "romantic", "betrayal".
    - 'causes_event_indexes': Array of zero-based integers linking to other events in the list.

    FEW-SHOT EXAMPLES:
    Example Input Snippet:
    "Tomorrow, Lord Vael would visit the Upper Realm. 'I must prepare,' he thought."
    Example '_thought_process':
    "1. 'Tomorrow' is a time reference, ignore. 2. 'Lord Vael' -> 'Vael'. 3. 'Upper Realm' = world term. 4. Event: Musing preparation. Intensity 1."
    
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
    
    logger.info(f"LLM Extraction Complete | {len(active_characters)} characters | {len(active_world_terms)} world terms | {len(events)} events | {dialogue_count} dialogue blocks")
    
    return {
        "active_character_names": active_characters,
        "character_genders": result.get("character_genders", {}),
        "active_world_terms": active_world_terms,
        "dialogue_count_total": dialogue_count,
        "events": events,
        "raw_entities": {name: 1 for name in active_characters}
    }

