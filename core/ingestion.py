from pydantic import BaseModel, Field
import yaml
import json
import time # Added for event ID generation
from typing import List
from adapters.llm_adapter import analyze_text
from adapters.graph_adapter import get_graph_engine

class CharacterLine(BaseModel):
    name: str = Field(description="Name of the character speaking")
    line: str = Field(description="The exact text spoken")
    emotion: str = Field(description="Emotion of the line", default="neutral")

class ExtractedScene(BaseModel):
    characters: List[CharacterLine]

def ingest_chapter_text(text: str, config_path: str = "config.yaml"):
    """
    Analyzes the text to identify speakers and lines.
    Returns a list of objects with 'name', 'line', 'is_main_character'.
    """
    
    # Load config to get model name
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    model = config.get("llm_model", "gemini/gemini-1.5-flash")
    
    prompt = f"""
    You are a script converter and story analyst. Convert the following novel text into a structured JSON object containing:
    1. "dialogue": A list of spoken lines.
    2. "events": A list of key narrative events that occurred, identifying who was involved.
    
    Format:
    {{
      "dialogue": [
        {{ "name": "Character Name", "line": "Spoken text", "emotion": "happy/sad/neutral" }}
      ],
      "events": [
        {{ "description": "Brief description of event", "characters": ["Character A", "Character B"] }}
      ]
    }}
    
    Text Segment:
    {text[:4000]} 
    """ # Truncate for safety/cost in demo
    
    # LLM Call
    response_text = analyze_text(prompt, model=model)
    
    if not response_text:
        return []

    try:
        # Simple cleanup to ensure JSON
        cleaned_json = response_text.replace("```json", "").replace("```", "").strip()
        data = json.loads(cleaned_json)
        
        results = []
        graph = get_graph_engine()
        
        # Process Events First (Context)
        events = data.get("events", [])
        for i, event in enumerate(events):
            event_id = f"event_{int(time.time())}_{i}"
            graph.add_event(event_id, event["description"], event["characters"])
            
        # Process Dialogue
        dialogue_list = data.get("dialogue", []) if isinstance(data, dict) else data # Handle legacy list format if LLM messes up
        if isinstance(dialogue_list, list):
             for item in dialogue_list:
                # Update Graph (Naive update for demo: increment appearance)
                if "name" in item:
                    graph.add_character(item["name"], {"last_seen": "now"})
                    results.append(item)
            
        return results
        
    except json.JSONDecodeError:
        print("Failed to parse LLM response.")
        return []
