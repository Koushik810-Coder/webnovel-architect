from uuid import uuid4

def generate_character_id() -> str:
    return f"char_{uuid4().hex[:8]}"
