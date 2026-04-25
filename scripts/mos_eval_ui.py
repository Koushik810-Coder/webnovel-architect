"""
scripts/mos_eval_ui.py
======================
Mean Opinion Score (MOS) Blind A/B Evaluation Dashboard.

A Streamlit app for subjective perceptual evaluation of synthesized audiobook
clips. Evaluators rate each clip on three axes (naturalness, distinctiveness,
fatigue) on a 1–5 scale, and results are persisted to a local CSV log.

Usage:
    streamlit run scripts/mos_eval_ui.py

Flags (pass via --  separator):
    --audio_dir   Path to a directory containing .mp3 clips to evaluate.
                  Defaults to scanning all stories under data/.
    --csv_path    Path for the results CSV log.
                  Defaults to output/mos_results.csv
"""

from __future__ import annotations

import csv
import os
import sys
from datetime import datetime, timezone
from typing import List, Dict

# ── Path bootstrap so module imports work when run directly ──────────────────
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


# ══════════════════════════════════════════════════════════════════════════════
#  Pure-Python core (tested by tests/test_mos_eval.py)
# ══════════════════════════════════════════════════════════════════════════════

def discover_audio_clips(directory: str) -> List[str]:
    """Returns a sorted list of absolute paths to .mp3 files in *directory*.

    Returns an empty list if the directory does not exist.
    """
    if not os.path.isdir(directory):
        return []
    clips = [
        os.path.abspath(os.path.join(directory, f))
        for f in sorted(os.listdir(directory))
        if f.lower().endswith(".mp3")
    ]
    return clips


_CSV_HEADER = ["clip", "naturalness", "distinctiveness", "fatigue", "timestamp"]


def save_mos_rating(
    csv_path: str,
    *,
    clip: str,
    naturalness: int,
    distinctiveness: int,
    fatigue: int,
) -> None:
    """Appends one MOS rating row to *csv_path*, creating the file + header if needed."""
    file_exists = os.path.exists(csv_path)
    os.makedirs(os.path.dirname(csv_path) if os.path.dirname(csv_path) else ".", exist_ok=True)
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_CSV_HEADER)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "clip": clip,
            "naturalness": naturalness,
            "distinctiveness": distinctiveness,
            "fatigue": fatigue,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })


def load_mos_results(csv_path: str) -> List[Dict[str, str]]:
    """Reads all MOS rating rows from *csv_path*.

    Returns an empty list if the file does not exist or contains only a header.
    """
    if not os.path.exists(csv_path):
        return []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [row for row in reader]


# ══════════════════════════════════════════════════════════════════════════════
#  Streamlit UI
# ══════════════════════════════════════════════════════════════════════════════

def _gather_all_clips(data_dir: str) -> List[str]:
    """Recursively find all .mp3 files under *data_dir*."""
    clips: List[str] = []
    for root, dirs, files in os.walk(data_dir):
        # Skip hidden dirs
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for fname in sorted(files):
            if fname.lower().endswith(".mp3"):
                clips.append(os.path.abspath(os.path.join(root, fname)))
    return clips


def main_ui() -> None:  # pragma: no cover
    import streamlit as st

    # ── Page config ──────────────────────────────────────────────────────────
    st.set_page_config(
        page_title="MOS Audio Evaluator — Webnovel Architect",
        page_icon="🎧",
        layout="centered",
    )

    # ── Custom CSS ───────────────────────────────────────────────────────────
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .mos-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        border-radius: 12px;
        padding: 2rem 2.5rem;
        margin-bottom: 1.5rem;
        color: white;
    }
    .mos-header h1 { font-size: 1.8rem; font-weight: 700; margin: 0 0 .25rem; }
    .mos-header p { opacity: .75; margin: 0; font-size: .95rem; }

    .clip-card {
        background: #1e1e2e;
        border: 1px solid #2d2d44;
        border-radius: 10px;
        padding: 1.2rem 1.6rem;
        margin-bottom: 1rem;
    }
    .clip-label { color: #a0a0c0; font-size: .78rem; text-transform: uppercase; letter-spacing: .08em; }
    .clip-name  { color: #e0e0ff; font-size: 1rem; font-weight: 600; margin-top: .2rem; word-break: break-all; }

    .progress-bar-wrap {
        background: #2d2d44;
        border-radius: 100px;
        height: 6px;
        width: 100%;
        margin: .6rem 0 1.2rem;
    }
    .progress-bar-fill {
        background: linear-gradient(90deg, #7c3aed, #4f46e5);
        border-radius: 100px;
        height: 6px;
    }

    .results-table th { color: #a0a0c0 !important; }

    div[data-testid="stSlider"] > div > div > div { background: #4f46e5 !important; }
    </style>
    """, unsafe_allow_html=True)

    # ── Sidebar — configuration ───────────────────────────────────────────────
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")
        default_data_dir = os.path.join(ROOT, "data")
        audio_dir = st.text_input(
            "Audio directory",
            value=default_data_dir,
            help="Root directory to scan recursively for .mp3 clips.",
        )
        default_csv = os.path.join(ROOT, "output", "mos_results.csv")
        csv_path = st.text_input(
            "Results CSV path",
            value=default_csv,
            help="Where to save / load evaluation results.",
        )
        st.divider()
        st.markdown("### Legend")
        st.markdown("""
| Score | Meaning |
|-------|---------|
| 5 | Excellent |
| 4 | Good |
| 3 | Fair |
| 2 | Poor |
| 1 | Bad |
        """)

    # ── Header ───────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="mos-header">
        <h1>🎧 MOS Audio Evaluator</h1>
        <p>Blind perceptual evaluation · Rate each clip on naturalness, speaker distinctiveness, and listening fatigue</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Discover clips ────────────────────────────────────────────────────────
    all_clips = _gather_all_clips(audio_dir)

    if not all_clips:
        st.warning(
            f"No .mp3 files found under **{audio_dir}**.\n\n"
            "Generate audiobook chapters first, or set a different audio directory in the sidebar.",
            icon="⚠️",
        )
        return

    # ── Session state ─────────────────────────────────────────────────────────
    if "clip_index" not in st.session_state:
        st.session_state["clip_index"] = 0
    if "rated_clips" not in st.session_state:
        existing = load_mos_results(csv_path)
        st.session_state["rated_clips"] = {r["clip"] for r in existing}
    if "shuffled_clips" not in st.session_state:
        import random
        shuffled = all_clips.copy()
        random.shuffle(shuffled)
        st.session_state["shuffled_clips"] = shuffled

    # Filter out already-rated clips from the shuffled list
    remaining = [c for c in st.session_state["shuffled_clips"] if os.path.basename(c) not in st.session_state["rated_clips"]]

    # ── Progress ─────────────────────────────────────────────────────────────
    total = len(all_clips)
    done  = total - len(remaining)
    pct   = int(done / total * 100) if total else 0

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"""
        <div class="progress-bar-wrap">
            <div class="progress-bar-fill" style="width:{pct}%;"></div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.metric("Progress", f"{done} / {total}")

    if not remaining:
        st.success("🎉 All clips evaluated! See the **Results** tab below.")
    else:
        idx   = st.session_state["clip_index"] % len(remaining)
        clip  = remaining[idx]
        cname = os.path.basename(clip)

        # ── Clip card ────────────────────────────────────────────────────────
        st.markdown(f"""
        <div class="clip-card">
            <div class="clip-label">Now evaluating — clip {idx + 1} of {len(remaining)}</div>
            <div class="clip-name">🔊 {cname}</div>
        </div>
        """, unsafe_allow_html=True)

        # Audio player
        if os.path.exists(clip):
            with open(clip, "rb") as f:
                audio_bytes = f.read()
            st.audio(audio_bytes, format="audio/mp3")
        else:
            st.error(f"File not found: {clip}")

        st.markdown("---")

        # ── Rating sliders ────────────────────────────────────────────────────
        col_n, col_d, col_f = st.columns(3)
        with col_n:
            st.markdown("**Naturalness**")
            st.caption("Does it sound like a human voice?")
            naturalness = st.slider("Naturalness", 1, 5, 3, key=f"nat_{idx}", label_visibility="collapsed")
        with col_d:
            st.markdown("**Distinctiveness**")
            st.caption("Are characters clearly different?")
            distinctiveness = st.slider("Distinctiveness", 1, 5, 3, key=f"dis_{idx}", label_visibility="collapsed")
        with col_f:
            st.markdown("**Fatigue**")
            st.caption("How tiring is it to listen to? (1=exhausting, 5=effortless)")
            fatigue = st.slider("Fatigue", 1, 5, 3, key=f"fat_{idx}", label_visibility="collapsed")

        st.markdown("")

        btn_col1, btn_col2, _ = st.columns([1, 1, 2])
        with btn_col1:
            if st.button("✅ Submit Rating", type="primary", use_container_width=True):
                save_mos_rating(
                    csv_path,
                    clip=cname,
                    naturalness=naturalness,
                    distinctiveness=distinctiveness,
                    fatigue=fatigue,
                )
                st.session_state["rated_clips"].add(cname)
                st.session_state["clip_index"] = 0  # reset pointer into remaining list
                st.rerun()
        with btn_col2:
            if st.button("⏭ Skip", use_container_width=True):
                st.session_state["clip_index"] = (idx + 1) % len(remaining)
                st.rerun()

    # ── Results viewer ────────────────────────────────────────────────────────
    st.markdown("---")
    with st.expander("📊 View Results", expanded=(not remaining)):
        rows = load_mos_results(csv_path)
        if not rows:
            st.info("No ratings submitted yet.")
        else:
            import statistics

            nat_scores  = [int(r["naturalness"])     for r in rows]
            dis_scores  = [int(r["distinctiveness"])  for r in rows]
            fat_scores  = [int(r["fatigue"])          for r in rows]

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Ratings logged",     len(rows))
            m2.metric("Avg Naturalness",    f"{statistics.mean(nat_scores):.2f}")
            m3.metric("Avg Distinctiveness",f"{statistics.mean(dis_scores):.2f}")
            m4.metric("Avg Fatigue",        f"{statistics.mean(fat_scores):.2f}")

            st.markdown("#### Raw Log")
            st.dataframe(rows, use_container_width=True)

            # Download button
            with open(csv_path, "rb") as cf:
                st.download_button(
                    label="📥 Download CSV",
                    data=cf,
                    file_name="mos_results.csv",
                    mime="text/csv",
                )


if __name__ == "__main__":
    main_ui()
