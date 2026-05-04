import pytest
from unittest.mock import patch
from app.services.extraction import route_model, extract_chapter_intelligence


# ---------------------------------------------------------------------------
# route_model() uses a local import inside the function body:
#   from adapters.llm_adapter import analyze_text_json
# so we must patch at the source module, not at extraction.py.
# ---------------------------------------------------------------------------

def test_adaptive_routing_straightforward(monkeypatch):
    """Low complexity score (<= 6) -> stays on the default/cheap model."""
    with patch("adapters.llm_adapter.analyze_text_json", return_value={"complexity_score": 3}):
        text = "Alice said to Bob, 'Hello.' Bob replied, 'Hi.' They walked to the store."
        model = route_model(text)
    # Should route to the default local/cheap model (not gemini)
    assert not model.startswith("gemini/"), f"Expected cheap model, got: {model}"


def test_adaptive_routing_complex(monkeypatch):
    """High complexity score (>= 7) -> routes to advanced API model."""
    with patch("adapters.llm_adapter.analyze_text_json", return_value={"complexity_score": 9}):
        text = """
        Lord Vael of the Iron Sect approached the Crystal Monolith in the Upper Realm.
        Lady Elara and Sir Kael watched from the shadows. 'The Mana Core is fluctuating,'
        whispered Elara. Suddenly, the Azure Guild members ambushed them.
        General Thorne shouted orders to his Tier-5 Mages.
        """
        model = route_model(text)
    assert model.startswith("gemini/") or model.startswith("gpt-4"), (
        f"Expected advanced model, got: {model}"
    )
