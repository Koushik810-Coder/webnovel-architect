from typing import List, Dict, Set
import difflib

def resolve_aliases(names: List[str]) -> List[str]:
    """
    Takes a list of character names extracted from a chapter and
    merges strict substrings (e.g. "Aria" and "Aria the Mage" -> "Aria").
    Returns the deduplicated list of canonical names.
    
    This helps prevent graph fragmentation.
    """
    if not names:
        return []
        
    # Sort by length descending, so we check longest strings against shortest
    sorted_names = sorted(list(set(names)), key=len, reverse=True)
    
    canonical_names = set()
    merged_map = {} # Maps alias -> canonical name
    
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
            # We are currently the canonical form until proven otherwise
            canonical_names.add(long_name)
            merged_map[long_name] = long_name
            
    # As a second pass, we check if any canonical names can be merged into shorter ones 
    # that were added later (since we iterate longest first)
    final_names = set()
    for name in canonical_names:
        # Is there a strictly shorter name in the canonical set that this name contains?
        shorter_match = None
        for other in canonical_names:
            if len(other) < len(name) and _is_word_substring(other.lower(), name.lower()):
                # Pick the shortest valid substring containing name as the canonical
                if shorter_match is None or len(other) < len(shorter_match):
                    shorter_match = other
                    
        if shorter_match:
            final_names.add(shorter_match)
        else:
            final_names.add(name)

    return sorted(list(final_names))


def _is_word_substring(short_str: str, long_str: str) -> bool:
    """
    Checks if short_str is a substring of long_str, but aligned to word boundaries.
    e.g. 'Tom' is a substring of 'Tom Baker' (True)
    e.g. 'Tom' is a substring of 'Atom' (False)
    """
    if short_str == long_str:
        return True
        
    # Pad long_str with spaces to easily check boundaries
    padded_long = f" {long_str} "
    
    # We want to match whole words. Either space separated or dash separated
    for split_char in [" ", "-", "'", '"']:
        target_exact = f"{split_char}{short_str}{split_char}"
        if target_exact in padded_long.replace("-", " ").replace("'", " ").replace('"', " "):
            return True
            
    return False
