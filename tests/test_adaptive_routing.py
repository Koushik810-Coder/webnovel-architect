import pytest
from unittest.mock import patch
from app.services.extraction import route_model


# ---------------------------------------------------------------------------
# route_model() uses a local import inside the function body:
#   from adapters.llm_adapter import analyze_text_json
# so we must patch at the source module, not at extraction.py.
#
# New routing logic (3-tier config-driven):
#   score < 7  -> fallback_llm_last_resort (Groq, cheap)
#   score >= 7 -> llm_model (NIM, primary/complex)
# ---------------------------------------------------------------------------

@pytest.mark.skip(reason="Adaptive routing currently disabled in favor of primary model + fallback chain")
def test_adaptive_routing_straightforward(monkeypatch):
    """Low complexity score (<= 6) -> stays on the cheap last-resort model (Groq)."""
    with patch("adapters.llm_adapter.analyze_text_json", return_value={"complexity_score": 3}):
        text = "Alice said to Bob, 'Hello.' Bob replied, 'Hi.' They walked to the store."
        model = route_model(text)
    # Should route to the cheap/last-resort model, not the NIM primary
    assert not model.startswith("nvidia_nim/"), f"Expected cheap model, got: {model}"


@pytest.mark.skip(reason="Adaptive routing currently disabled in favor of primary model + fallback chain")
def test_adaptive_routing_complex(monkeypatch):
    """High complexity score (>= 7) -> routes to the primary model (NIM)."""
    with patch("adapters.llm_adapter.analyze_text_json", return_value={"complexity_score": 9}):
        text = """
        Lord Vael of the Iron Sect approached the Crystal Monolith in the Upper Realm.
        Lady Elara and Sir Kael watched from the shadows. 'The Mana Core is fluctuating,'
        whispered Elara. Suddenly, the Azure Guild members ambushed them.
        General Thorne shouted orders to his Tier-5 Mages.
        """
        model = route_model(text)
    # Complex chapters should route to the primary model (NVIDIA NIM by default)
    assert model.startswith("nvidia_nim/"), (
        f"Expected NIM primary model for complex chapter, got: {model}"
    )
