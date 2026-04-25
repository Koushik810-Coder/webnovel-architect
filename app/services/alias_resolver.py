from typing import Dict, List, Tuple


def resolve_aliases(names: List[str]) -> List[str]:
    """Thin wrapper — returns only the canonical name list. Existing call sites unchanged."""
    canonical, _ = resolve_aliases_with_map(names)
    return canonical


def resolve_aliases_with_map(names: List[str]) -> Tuple[List[str], Dict[str, str]]:
    """
    Takes a list of character names extracted from a chapter and
    merges strict substrings (e.g. "Aria" and "Aria the Mage" -> "Aria").

    Returns:
        canonical_names: deduplicated, sorted list of canonical names.
        alias_map: maps every input name to its resolved canonical form.
                   e.g. {"Aria the Mage": "Aria", "Aria": "Aria"}

    This helps prevent graph fragmentation when the same character is referred
    to by multiple surface forms in a single chapter.
    """
    if not names:
        return [], {}

    # Sort by length descending, so longer forms are checked against shorter ones
    sorted_names = sorted(list(set(names)), key=len, reverse=True)

    canonical_names: set = set()
    merged_map: Dict[str, str] = {}  # Maps every name -> its canonical form

    for long_name in sorted_names:
        found_target = False

        # Check against already established canonical names first
        for target in list(canonical_names):
            # strict word-boundary substring match (e.g. 'Aria' in 'Aria of the West')
            if _is_word_substring(target.lower(), long_name.lower()):
                merged_map[long_name] = target
                found_target = True
                break

        if not found_target:
            # This is the canonical form until a shorter one absorbs it
            canonical_names.add(long_name)
            merged_map[long_name] = long_name

    # Second pass: collapse canonical names that contain a shorter canonical sibling.
    # Sort by length ascending so the shortest form always wins deterministically
    # (set iteration order is undefined; without sorting the winner varies per run).
    final_names: set = set()
    remap: Dict[str, str] = {}  # old canonical -> new (shorter) canonical

    for name in sorted(canonical_names, key=len):
        shorter_match = None
        for other in canonical_names:
            if len(other) < len(name) and _is_word_substring(other.lower(), name.lower()):
                if shorter_match is None or len(other) < len(shorter_match):
                    shorter_match = other

        if shorter_match:
            final_names.add(shorter_match)
            remap[name] = shorter_match
        else:
            final_names.add(name)

    # Apply second-pass remap to merged_map so every alias points to its final canonical
    for alias, canon in merged_map.items():
        if canon in remap:
            merged_map[alias] = remap[canon]

    return sorted(list(final_names)), merged_map


def _is_word_substring(short_str: str, long_str: str) -> bool:
    """
    Checks if short_str is a substring of long_str, but aligned to word boundaries.
    e.g. 'Tom' is a substring of 'Tom Baker' (True)
    e.g. 'Tom' is a substring of 'Atom' (False)
    """
    if short_str == long_str:
        return True

    # Normalise delimiters then check for whole-word match
    padded_long = f" {long_str} "
    for split_char in [" ", "-", "'", '"']:
        target_exact = f"{split_char}{short_str}{split_char}"
        if target_exact in padded_long.replace("-", " ").replace("'", " ").replace('"', " "):
            return True

    return False
