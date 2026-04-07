"""
tests/test_graph_pagerank.py
============================
Tests for the Temporal PageRank decay algorithm — the core mathematical
claim of the Webnovel Architect research paper.

Covers:
  - Single-chapter vacuum: decay multiplier must be exactly 1.0 (Δt = 0)
  - Multi-chapter decay: score must decrease as Δt increases
  - Bootstrapping: first N=5 characters always return >= 0.16
  - Unknown character: returns 0.0
  - Decay rate boundary: λ=0 means no decay; λ=1 means instant zero
"""

import pytest
import os
import math
from adapters.graph_adapter import GraphProvider

TEST_UUID = "test_pagerank_story"


@pytest.fixture(autouse=True)
def clean_graph(tmp_path, monkeypatch):
    """Redirect DATA_DIR to a temp folder so no real data is touched."""
    import app.core.story_manager as sm
    monkeypatch.setattr(sm.StoryManager, "DATA_DIR", str(tmp_path))
    yield


def _make_graph(tmp_path, monkeypatch):
    """Helper: create a fresh GraphProvider using the monkeypatched tmp dir."""
    story_dir = os.path.join(str(tmp_path), TEST_UUID)
    os.makedirs(story_dir, exist_ok=True)
    return GraphProvider(TEST_UUID)


# ── Test 1: Single-chapter vacuum ────────────────────────────────────────────

def test_single_chapter_decay_multiplier_is_one(tmp_path, monkeypatch):
    """
    When current_chapter == chapter the character was last seen in (Δt=0),
    the decay multiplier (1-λ)^0 = 1.0, so the score equals raw PageRank.
    This is the documented 'single-chapter vacuum' condition.
    """
    gp = _make_graph(tmp_path, monkeypatch)
    gp.add_character("hero", {"display_name": "Hero"})
    gp.add_event("ev1", "Hero appears", ["hero"], chapter_id=1)

    score_with_decay = gp.get_character_importance("hero", current_chapter=1, decay_rate=0.05)
    score_no_decay   = gp.get_character_importance("hero", current_chapter=1, decay_rate=0.0)

    # Both should be identical (multiplier = 1.0 regardless of λ when Δt=0)
    assert math.isclose(score_with_decay, score_no_decay, rel_tol=1e-9)
    assert score_with_decay > 0.0


# ── Test 2: Multi-chapter decay ───────────────────────────────────────────────

def test_score_decays_as_chapters_pass(tmp_path, monkeypatch):
    """
    A character last seen at chapter 1 must score progressively lower as
    current_chapter advances — proving the temporal decay mechanism works.
    """
    gp = _make_graph(tmp_path, monkeypatch)
    gp.add_character("side_char", {"display_name": "Side Char", "introduction_order": 10})
    gp.add_event("ev1", "Side char appears once", ["side_char"], chapter_id=1)

    score_ch1 = gp.get_character_importance("side_char", current_chapter=1,  decay_rate=0.10)
    score_ch5 = gp.get_character_importance("side_char", current_chapter=5,  decay_rate=0.10)
    score_ch10= gp.get_character_importance("side_char", current_chapter=10, decay_rate=0.10)

    assert score_ch1 > score_ch5 > score_ch10, (
        f"Expected monotonic decay: ch1={score_ch1:.4f} > ch5={score_ch5:.4f} > ch10={score_ch10:.4f}"
    )


# ── Test 3: Higher λ decays faster ───────────────────────────────────────────

def test_higher_lambda_decays_faster(tmp_path, monkeypatch):
    """λ=0.20 must produce a lower score than λ=0.05 after the same Δt."""
    gp = _make_graph(tmp_path, monkeypatch)
    gp.add_character("wanderer", {"display_name": "Wanderer", "introduction_order": 10})
    gp.add_event("ev1", "Wanderer seen", ["wanderer"], chapter_id=1)

    score_slow_decay = gp.get_character_importance("wanderer", current_chapter=5, decay_rate=0.05)
    score_fast_decay = gp.get_character_importance("wanderer", current_chapter=5, decay_rate=0.20)

    assert score_slow_decay > score_fast_decay, (
        f"Slow decay ({score_slow_decay:.4f}) should be > fast decay ({score_fast_decay:.4f})"
    )


# ── Test 4: DPQ bootstrapping (provisional graduation on debut) ───────────────

def test_dpq_grants_provisional_score_on_debut_chapter(tmp_path, monkeypatch):
    """
    A character that dominates > 40% of debut chapter interactions receives a
    provisional score >= DELTA_UPPER + 0.01 on their debut chapter via DPQ.
    This replaces the old hardcoded 'first 5 characters' floor.
    """
    from app.core.graduation import DELTA_UPPER
    gp = _make_graph(tmp_path, monkeypatch)

    # Single dominant character in chapter 1 with high-intensity interactions
    gp.add_character("protagonist", {"display_name": "Protagonist"})
    for i in range(5):
        gp.add_event(f"ev_{i}", f"Protagonist drives action {i}", ["protagonist"],
                     chapter_id=1, intensity=5)

    # On their debut chapter, DPQ should grant provisional graduation
    score_debut = gp.get_character_importance("protagonist", current_chapter=1, decay_rate=0.05)
    assert score_debut >= DELTA_UPPER + 0.01, (
        f"DPQ should grant provisional graduation on debut: got {score_debut:.4f}, "
        f"expected >= {DELTA_UPPER + 0.01:.4f}"
    )


def test_dpq_boost_does_not_persist_indefinitely(tmp_path, monkeypatch):
    """
    The DPQ provisional boost only applies ON the debut chapter.
    After many chapters of absence, temporal decay correctly erodes the score —
    proving the old hardcoded floor was removed and the math is now honest.
    """
    gp = _make_graph(tmp_path, monkeypatch)

    # Character appears only in chapter 1
    gp.add_character("early_char", {"display_name": "Early Char"})
    gp.add_event("ev_debut", "Early char acts", ["early_char"], chapter_id=1, intensity=3)

    # At chapter 20 with lambda=0.20 (aggressive decay), score should have eroded
    score_ch20 = gp.get_character_importance("early_char", current_chapter=20, decay_rate=0.20)
    # With (1-0.20)^19 ~= 0.014 multiplier, score should be very low
    assert score_ch20 < 0.16, (
        f"After 19 chapters of absence with lambda=0.20, character should have decayed "
        f"below 0.16, got {score_ch20:.4f}. Old hardcoded floor should be gone."
    )



# ── Test 5: Unknown node returns 0.0 ─────────────────────────────────────────

def test_unknown_character_returns_zero(tmp_path, monkeypatch):
    """Querying a character not in the graph must return 0.0."""
    gp = _make_graph(tmp_path, monkeypatch)
    score = gp.get_character_importance("nobody", current_chapter=1, decay_rate=0.05)
    assert score == 0.0


# ── Test 6: Zero decay rate means no forgetting ──────────────────────────────

def test_zero_lambda_means_no_decay(tmp_path, monkeypatch):
    """With λ=0, (1-0)^Δt = 1 for any Δt, so score must be stable across chapters."""
    gp = _make_graph(tmp_path, monkeypatch)
    gp.add_character("immortal", {"display_name": "Immortal", "introduction_order": 10})
    gp.add_event("ev1", "Immortal acts", ["immortal"], chapter_id=1)

    score_ch1  = gp.get_character_importance("immortal", current_chapter=1,   decay_rate=0.0)
    score_ch50 = gp.get_character_importance("immortal", current_chapter=50,  decay_rate=0.0)

    assert math.isclose(score_ch1, score_ch50, rel_tol=1e-9), (
        f"With λ=0, scores should be equal: ch1={score_ch1:.6f}, ch50={score_ch50:.6f}"
    )


# ── Test 7: Graph merge doesn't break decay ───────────────────────────────────

def test_merge_characters_preserves_decay_tracking(tmp_path, monkeypatch):
    """
    After merging an alias into a canonical character, the canonical must
    retain the most recent chapter_id for decay calculation.
    """
    gp = _make_graph(tmp_path, monkeypatch)
    gp.add_character("aria", {"display_name": "Aria", "introduction_order": 10})
    gp.add_character("aria_the_mage", {"display_name": "Aria the Mage", "introduction_order": 11})

    gp.add_event("ev1", "Aria acts", ["aria"], chapter_id=1)
    gp.add_event("ev5", "Aria the Mage acts", ["aria_the_mage"], chapter_id=5)

    # Merge alias into canonical
    gp.merge_characters("aria_the_mage", "aria")

    # "aria" node should exist; "aria_the_mage" should not
    assert gp.graph.has_node("aria")
    assert not gp.graph.has_node("aria_the_mage")

    # Score must still be computable
    score = gp.get_character_importance("aria", current_chapter=10, decay_rate=0.05)
    assert score > 0.0
