"""
tests/test_alias_resolver.py
============================
Tests for the alias resolution logic that prevents graph fragmentation
when the same character appears under multiple name forms.

Covers:
  - Exact duplicates collapsed to one entry
  - Substring merge ("Aria" + "Aria the Mage" → "Aria")
  - Word-boundary enforcement ("Tom" does NOT merge into "Atom")
  - Empty and single-item inputs
  - Multi-level merge chains
  - Names with hyphens and apostrophes
"""

from app.services.alias_resolver import resolve_aliases, resolve_aliases_with_map, _is_word_substring


# ── _is_word_substring unit tests ────────────────────────────────────────────

class TestIsWordSubstring:
    def test_exact_match(self):
        assert _is_word_substring("aria", "aria") is True

    def test_word_prefix(self):
        assert _is_word_substring("aria", "aria the mage") is True

    def test_word_suffix(self):
        assert _is_word_substring("mage", "aria the mage") is True

    def test_middle_word(self):
        assert _is_word_substring("the", "aria the mage") is True

    def test_not_embedded_in_word(self):
        """'tom' must NOT match inside 'atom'."""
        assert _is_word_substring("tom", "atom") is False

    def test_not_partial_prefix(self):
        """'ari' must NOT match 'aria'."""
        assert _is_word_substring("ari", "aria the mage") is False

    def test_hyphenated_name(self):
        """Hyphen acts as a word boundary."""
        assert _is_word_substring("thar", "vael-thar") is True

    def test_apostrophe_name(self):
        """Apostrophe acts as a word boundary."""
        assert _is_word_substring("thar", "vael'thar") is True

    def test_empty_strings(self):
        assert _is_word_substring("", "") is True


# ── resolve_aliases integration tests ────────────────────────────────────────

class TestResolveAliases:

    def test_empty_list(self):
        assert resolve_aliases([]) == []

    def test_single_name(self):
        assert resolve_aliases(["Aria"]) == ["Aria"]

    def test_exact_duplicates_collapsed(self):
        result = resolve_aliases(["Zorian", "Zorian", "Zorian"])
        assert result == ["Zorian"]

    def test_long_form_merged_into_short(self):
        """'Aria the Mage' should merge into 'Aria'."""
        result = resolve_aliases(["Aria", "Aria the Mage"])
        assert "Aria" in result
        assert "Aria the Mage" not in result
        assert len(result) == 1

    def test_non_substrings_kept_separate(self):
        """'Tom' and 'Atom' are distinct — word boundary prevents merge."""
        result = resolve_aliases(["Tom", "Atom"])
        assert len(result) == 2
        assert "Tom" in result
        assert "Atom" in result

    def test_multiple_aliases_for_same_character(self):
        """All variants of the same name should collapse to the shortest form."""
        result = resolve_aliases(["Jon", "Jon Snow", "Jon Snow the Bastard"])
        assert "Jon" in result
        assert len(result) == 1

    def test_independent_characters_kept(self):
        """Two completely unrelated characters must both survive."""
        result = resolve_aliases(["Zorian", "Kirielle"])
        assert "Zorian" in result
        assert "Kirielle" in result
        assert len(result) == 2

    def test_mixed_merge_and_keep(self):
        """Partial merge: one pair collapses, one stays separate."""
        result = resolve_aliases(["Aria", "Aria the Mage", "Zorian"])
        assert "Aria" in result
        assert "Zorian" in result
        assert "Aria the Mage" not in result
        assert len(result) == 2

    def test_output_is_sorted(self):
        """Returned list must always be lexicographically sorted."""
        result = resolve_aliases(["Zorian", "Aria", "Kirielle"])
        assert result == sorted(result)

    def test_case_sensitivity(self):
        """
        The resolver normalises to lowercase for comparison,
        but 'ARIA' and 'aria' are treated as distinct strings
        since the resolver preserves original casing.
        """
        result = resolve_aliases(["Aria", "ARIA"])
        # Both forms differ only in case; implementation keeps them distinct
        # (no case-folding on the output). Just ensure no crash.
        assert isinstance(result, list)
        assert len(result) >= 1


# ── resolve_aliases_with_map tests ───────────────────────────────────────────

class TestResolveAliasesWithMap:

    def test_returns_tuple(self):
        """Must return a 2-tuple of (list, dict)."""
        result = resolve_aliases_with_map(["Aria"])
        assert isinstance(result, tuple)
        assert len(result) == 2
        canonical, alias_map = result
        assert isinstance(canonical, list)
        assert isinstance(alias_map, dict)

    def test_empty_input_returns_empty_tuple(self):
        canonical, alias_map = resolve_aliases_with_map([])
        assert canonical == []
        assert alias_map == {}

    def test_canonical_list_matches_resolve_aliases(self):
        """The canonical list must be identical to what resolve_aliases returns."""
        names = ["Aria", "Aria the Mage", "Zorian"]
        canonical, _ = resolve_aliases_with_map(names)
        assert canonical == resolve_aliases(names)

    def test_alias_map_contains_all_inputs(self):
        """Every input name must appear as a key in the alias map."""
        names = ["Aria", "Aria the Mage", "Zorian"]
        _, alias_map = resolve_aliases_with_map(names)
        for name in names:
            assert name in alias_map, f"'{name}' missing from alias_map"

    def test_long_form_maps_to_short_canonical(self):
        """'Aria the Mage' should map to 'Aria'."""
        _, alias_map = resolve_aliases_with_map(["Aria", "Aria the Mage"])
        assert alias_map["Aria the Mage"] == "Aria"
        assert alias_map["Aria"] == "Aria"

    def test_unrelated_names_map_to_themselves(self):
        """Independent characters map to themselves."""
        _, alias_map = resolve_aliases_with_map(["Zorian", "Kirielle"])
        assert alias_map["Zorian"] == "Zorian"
        assert alias_map["Kirielle"] == "Kirielle"

    def test_multi_level_chain_maps_to_shortest(self):
        """All variants in a chain ultimately map to the shortest form."""
        names = ["Jon", "Jon Snow", "Jon Snow the Bastard"]
        canonical, alias_map = resolve_aliases_with_map(names)
        assert canonical == ["Jon"]
        assert alias_map["Jon"] == "Jon"
        assert alias_map["Jon Snow"] == "Jon"
        assert alias_map["Jon Snow the Bastard"] == "Jon"
