import random

# We will implement this in app/core/determinism.py
from app.core.determinism import set_story_seed, derive_seed

# ─────────────────────────────────────────────────────────────
# Seed derivation correctness
# ─────────────────────────────────────────────────────────────

def test_derive_seed_is_stable_across_calls():
    """Same story UUID must always yield the exact same integer seed."""
    uuid = "0605251a-d51d-44d0-b26c-b6b5358670f9"
    seed_a = derive_seed(uuid)
    seed_b = derive_seed(uuid)
    assert seed_a == seed_b

def test_derive_seed_differs_for_different_uuids():
    """Different UUIDs must produce different seeds."""
    uuid_a = "0605251a-d51d-44d0-b26c-b6b5358670f9"
    uuid_b = "0ba72968-30da-47d7-bb86-df7a01bfec43"
    assert derive_seed(uuid_a) != derive_seed(uuid_b)

def test_derive_seed_uses_sha256_not_builtin_hash():
    """
    Python's built-in hash() is randomised per-process by PYTHONHASHSEED.
    We must use SHA-256 so seeds are identical across restarts.
    """
    import hashlib
    uuid = "test-uuid-reproducibility"
    expected = int(hashlib.sha256(uuid.encode()).hexdigest(), 16) % (2**32)
    assert derive_seed(uuid) == expected

# ─────────────────────────────────────────────────────────────
# Random state reproducibility
# ─────────────────────────────────────────────────────────────

def test_set_story_seed_makes_random_reproducible():
    """
    Calling set_story_seed with the same UUID must produce the same
    random sequence both times.
    """
    uuid = "0605251a-d51d-44d0-b26c-b6b5358670f9"

    set_story_seed(uuid)
    seq_a = [random.random() for _ in range(10)]

    set_story_seed(uuid)
    seq_b = [random.random() for _ in range(10)]

    assert seq_a == seq_b

def test_set_story_seed_different_uuids_differ():
    """Different UUIDs must produce divergent random sequences."""
    set_story_seed("uuid-alpha")
    seq_a = [random.random() for _ in range(5)]

    set_story_seed("uuid-beta")
    seq_b = [random.random() for _ in range(5)]

    assert seq_a != seq_b

# ─────────────────────────────────────────────────────────────
# Audit log
# ─────────────────────────────────────────────────────────────

def test_set_story_seed_logs_seed_value(caplog):
    """set_story_seed must emit a structured log stating the seed used."""
    import logging
    with caplog.at_level(logging.INFO):
        set_story_seed("0605251a-d51d-44d0-b26c-b6b5358670f9")

    messages = [r.message for r in caplog.records]
    assert any("seed" in m.lower() for m in messages), (
        f"Expected a 'seed' audit log but got: {messages}"
    )
