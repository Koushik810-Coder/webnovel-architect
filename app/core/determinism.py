import hashlib
import random

from app.core.logger import get_logger

logger = get_logger(__name__)


def derive_seed(story_uuid: str) -> int:
    """
    Derive a deterministic integer seed from a given string UUID.
    Uses SHA-256 to ensure it is stable across processes.
    """
    return int(hashlib.sha256(story_uuid.encode('utf-8')).hexdigest(), 16) % (2**32)


def get_story_rng(story_uuid: str) -> random.Random:
    """
    Returns a story-scoped Random instance seeded from the story UUID.

    Prefer this over ``set_story_seed()`` — it avoids mutating the global
    random state which would affect other concurrent stories/sessions
    (e.g. two Streamlit users running different stories simultaneously).
    """
    return random.Random(derive_seed(story_uuid))


def set_story_seed(story_uuid: str):
    """
    Set the global random seed based on the story UUID.

    .. deprecated::
        Use ``get_story_rng()`` instead. This function mutates the process-wide
        ``random`` state which is unsafe in multi-session contexts.
    """
    seed_val = derive_seed(story_uuid)
    random.seed(seed_val)
    logger.warning(
        f"set_story_seed() mutates global random state — prefer get_story_rng(). "
        f"Seed: {seed_val}"
    )
