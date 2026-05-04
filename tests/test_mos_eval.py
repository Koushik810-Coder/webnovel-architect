"""
tests/test_mos_eval.py
======================
TDD tests for the MOS evaluation UI's core, non-Streamlit logic.

The MOS UI has three testable pure-Python responsibilities:
1. discover_audio_clips()    — scans a story's generated_audio dir for .mp3 files
2. save_mos_rating()         — appends a rating row to the CSV log
3. load_mos_results()        — reads the CSV back as a list of dicts
"""

import csv
import os


# ---------------------------------------------------------------------------
# Helpers to import the module under test
# (scripts/ is not a package; add its parent to sys.path before importing)
# ---------------------------------------------------------------------------

import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from scripts.mos_eval_ui import discover_audio_clips, save_mos_rating, load_mos_results


# ──────────────────────────────────────────────────────────────────────────────
# 1. discover_audio_clips
# ──────────────────────────────────────────────────────────────────────────────

class TestDiscoverAudioClips:
    def test_returns_empty_list_for_missing_directory(self, tmp_path):
        clips = discover_audio_clips(str(tmp_path / "nonexistent"))
        assert clips == []

    def test_finds_mp3_files_only(self, tmp_path):
        (tmp_path / "clip_a.mp3").write_bytes(b"fake")
        (tmp_path / "clip_b.mp3").write_bytes(b"fake")
        (tmp_path / "subtitle.vtt").write_text("WEBVTT")
        (tmp_path / "concat_list.txt").write_text("")

        clips = discover_audio_clips(str(tmp_path))
        assert len(clips) == 2
        assert all(c.endswith(".mp3") for c in clips)

    def test_returns_absolute_paths(self, tmp_path):
        (tmp_path / "clip_a.mp3").write_bytes(b"fake")
        clips = discover_audio_clips(str(tmp_path))
        assert os.path.isabs(clips[0])

    def test_clips_are_sorted(self, tmp_path):
        for name in ["0010_Narrator.mp3", "0002_Zorian.mp3", "0001_Narrator.mp3"]:
            (tmp_path / name).write_bytes(b"fake")
        clips = discover_audio_clips(str(tmp_path))
        assert clips == sorted(clips)


# ──────────────────────────────────────────────────────────────────────────────
# 2. save_mos_rating
# ──────────────────────────────────────────────────────────────────────────────

class TestSaveMosRating:
    def test_creates_csv_file_if_missing(self, tmp_path):
        csv_path = str(tmp_path / "mos_results.csv")
        save_mos_rating(csv_path, clip="clip_a.mp3", naturalness=4, distinctiveness=3, fatigue=2)
        assert os.path.exists(csv_path)

    def test_csv_contains_header_on_first_write(self, tmp_path):
        csv_path = str(tmp_path / "mos_results.csv")
        save_mos_rating(csv_path, clip="clip_a.mp3", naturalness=4, distinctiveness=3, fatigue=2)
        with open(csv_path, newline="") as f:
            reader = csv.reader(f)
            header = next(reader)
        assert "clip" in header
        assert "naturalness" in header
        assert "distinctiveness" in header
        assert "fatigue" in header

    def test_appends_row_with_correct_values(self, tmp_path):
        csv_path = str(tmp_path / "mos_results.csv")
        save_mos_rating(csv_path, clip="clip_a.mp3", naturalness=5, distinctiveness=4, fatigue=1)
        rows = load_mos_results(csv_path)
        assert len(rows) == 1
        assert rows[0]["clip"] == "clip_a.mp3"
        assert int(rows[0]["naturalness"]) == 5
        assert int(rows[0]["distinctiveness"]) == 4
        assert int(rows[0]["fatigue"]) == 1

    def test_multiple_ratings_appended_correctly(self, tmp_path):
        csv_path = str(tmp_path / "mos_results.csv")
        save_mos_rating(csv_path, clip="clip_a.mp3", naturalness=3, distinctiveness=3, fatigue=3)
        save_mos_rating(csv_path, clip="clip_b.mp3", naturalness=5, distinctiveness=2, fatigue=1)
        rows = load_mos_results(csv_path)
        assert len(rows) == 2
        assert rows[1]["clip"] == "clip_b.mp3"

    def test_header_written_only_once_on_append(self, tmp_path):
        csv_path = str(tmp_path / "mos_results.csv")
        save_mos_rating(csv_path, clip="clip_a.mp3", naturalness=3, distinctiveness=3, fatigue=2)
        save_mos_rating(csv_path, clip="clip_b.mp3", naturalness=4, distinctiveness=4, fatigue=1)
        with open(csv_path, newline="") as f:
            lines = [l for l in f if l.strip()]
        # Should be: 1 header + 2 data rows = 3 lines
        assert len(lines) == 3


# ──────────────────────────────────────────────────────────────────────────────
# 3. load_mos_results
# ──────────────────────────────────────────────────────────────────────────────

class TestLoadMosResults:
    def test_returns_empty_list_for_missing_file(self, tmp_path):
        rows = load_mos_results(str(tmp_path / "nonexistent.csv"))
        assert rows == []

    def test_returns_list_of_dicts(self, tmp_path):
        csv_path = str(tmp_path / "mos_results.csv")
        save_mos_rating(csv_path, clip="clip_a.mp3", naturalness=4, distinctiveness=3, fatigue=2)
        rows = load_mos_results(csv_path)
        assert isinstance(rows, list)
        assert isinstance(rows[0], dict)

    def test_empty_csv_returns_empty_list(self, tmp_path):
        csv_path = str(tmp_path / "mos_results.csv")
        csv_path_obj = tmp_path / "mos_results.csv"
        csv_path_obj.write_text("clip,naturalness,distinctiveness,fatigue,timestamp\n")
        rows = load_mos_results(str(csv_path))
        assert rows == []
