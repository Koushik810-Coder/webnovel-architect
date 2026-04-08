import re
from pydantic import BaseModel
from typing import Literal, List, Optional

class ScriptBlock(BaseModel):
    type: Literal["narration", "dialogue"]
    text: str

class NarrationBlock(ScriptBlock):
    type: Literal["narration"] = "narration"

class DialogueBlock(ScriptBlock):
    type: Literal["dialogue"] = "dialogue"
    speaker: Optional[str] = None

def parse_chapter_to_script_blocks(chapter_text: str) -> List[ScriptBlock]:
    """
    Deterministically parses a chapter's text into Narration and Dialogue blocks.
    It simply assumes anything between double quotes is dialogue, and everything else is narration.
    """
    blocks: List[ScriptBlock] = []
    
    # Split text by everything wrapped in standard OR curly double quotes. 
    # By grouping it with outer parentheses, the quotes and their contents are kept in the resulting list.
    chunks = re.split(r'("[^"]*"|“[^”]*”)', chapter_text)
    
    for chunk in chunks:
        stripped = chunk.strip()
        if not stripped:
            continue
            
        is_standard = stripped.startswith('"') and stripped.endswith('"')
        is_curly = stripped.startswith('“') and stripped.endswith('”')
        
        if (is_standard or is_curly) and len(stripped) >= 2:
            # It's dialogue, strip the literal quotes
            dialogue_text = stripped[1:-1].strip()
            if dialogue_text:
                blocks.append(DialogueBlock(text=dialogue_text))
        else:
            # It's narration
            blocks.append(NarrationBlock(text=stripped))
            
    return blocks

def resolve_dialogue_speakers(blocks: List[ScriptBlock]) -> List[ScriptBlock]:
    """
    Takes a list of deterministic script blocks and asks the LLM to identify the speaker
    for the dialogue blocks using the surrounding narration as context.
    """
    from adapters.llm_adapter import analyze_text_json
    
    dialogues = [(i, b) for i, b in enumerate(blocks) if isinstance(b, DialogueBlock)]
    if not dialogues:
        return blocks
        
    context = []
    for b in blocks:
        if isinstance(b, NarrationBlock):
            context.append(f"Narrator: {b.text}")
        else:
            context.append(f'Quote: "{b.text}"')

    # To avoid overwhelming the LLM, we limit context if it's too long, but for a typical
    # chapter chunk, it should be fine.
    context_str = "\n".join(context)
    
    quotes_str = ""
    for idx, (_, b) in enumerate(dialogues):
        quotes_str += f'{idx}: "{b.text}"\n'

    prompt = f"""
Given the following context from a story:
{context_str}

Identify the most likely speaker for each of the following quotes based on the context.
{quotes_str}

Return a JSON object in this exact format: {{"speakers": {{"0": "SpeakerName", "1": "SpeakerName"}}}}
If you cannot determine the speaker, or if it is an internal thought without a specific character, use "Narrator". 
Do NOT include any prefix like "Character Name:". Just the name.
"""
    try:
        # We can use groq for fast resolution
        response = analyze_text_json(prompt, model="groq/llama-3.1-8b-instant")
        if "error" in response:
            import yaml
            try:
                with open("config.yaml", "r") as f:
                    cfg = yaml.safe_load(f)
                    fallback = cfg.get("fallback_llm", "gemini/gemini-2.5-flash")
            except Exception:
                fallback = "gemini/gemini-2.5-flash"
                
            response = analyze_text_json(prompt, model=fallback)
            
        speakers_map = response.get("speakers", {})
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Speaker resolution failed: {e}")
        speakers_map = {}

    for idx, (original_idx, b) in enumerate(dialogues):
        speaker = speakers_map.get(str(idx), "Narrator")
        blocks[original_idx].speaker = speaker

    return blocks

