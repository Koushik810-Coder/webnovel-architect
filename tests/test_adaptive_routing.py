import pytest
from app.services.extraction import route_model, extract_chapter_intelligence

def test_adaptive_routing_straightforward():
    # A simple chapter with few entities and straightforward dialogue
    text = "Alice said to Bob, 'Hello.' Bob replied, 'Hi.' They walked to the store."
    
    # Should route to local SLM
    model = route_model(text)
    assert "llama" in model.lower()

def test_adaptive_routing_complex():
    # A complex chapter with many entities, factions, and world terms
    text = """
    Lord Vael of the Iron Sect approached the Crystal Monolith in the Upper Realm.
    Lady Elara and Sir Kael watched from the shadows. 'The Mana Core is fluctuating,' 
    whispered Elara. Suddenly, the Azure Guild members ambushed them.
    General Thorne shouted orders to his Tier-5 Mages.
    """
    
    # Should route to advanced API (e.g., gemini or gpt-4)
    model = route_model(text)
    assert model.startswith("gemini/") or model.startswith("gpt-4")
