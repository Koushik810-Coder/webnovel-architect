"""
scripts/evaluate.py — Phase 6 Evaluation Harness
=================================================
Runs all four quantitative evaluation metrics defined in the Review 1 deck
and prints a formatted summary.

Usage:
    python scripts/evaluate.py [--no-llm] [--no-tts]

Flags:
    --no-llm   Skip the LLM extraction metric (avoids API call / cost).
    --no-tts   Skip the TTS RTF metric (avoids audio synthesis time).
"""

import sys
import os
import json
import time
import argparse
import math

# --- Path Setup ---
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

# Load .env so API keys are available
env_path = os.path.join(ROOT, ".env")
if os.path.exists(env_path):
    with open(env_path, "r") as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip().strip("\"'"))


# ── ANSI colours (works on Windows 10+ with ENABLE_VIRTUAL_TERMINAL_PROCESSING) ──
class C:
    BOLD   = "\033[1m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    CYAN   = "\033[96m"
    RESET  = "\033[0m"
    DIM    = "\033[2m"

def header(title: str):
    width = 60
    print(f"\n{C.CYAN}{C.BOLD}{'─' * width}")
    print(f"  {title}")
    print(f"{'─' * width}{C.RESET}")

def metric_row(label: str, value: str, note: str = "", ok: bool = True):
    icon = f"{C.GREEN}✓{C.RESET}" if ok else f"{C.YELLOW}~{C.RESET}"
    print(f"  {icon}  {C.BOLD}{label:<36}{C.RESET}  {value}  {C.DIM}{note}{C.RESET}")


# ══════════════════════════════════════════════════════════════════════════════
# Metric 1 — Entity Precision, Recall & F1
# ══════════════════════════════════════════════════════════════════════════════

def compute_prf(predicted: list, gold: list):
    """Returns (precision, recall, f1) over string sets (case-insensitive)."""
    pred_set = {x.lower() for x in predicted}
    gold_set = {x.lower() for x in gold}
    if not pred_set:
        return 0.0, 0.0, 0.0
    precision = len(pred_set & gold_set) / len(pred_set)
    recall    = len(pred_set & gold_set) / len(gold_set) if gold_set else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    return precision, recall, f1


def run_entity_extraction(gold_data: dict, run_llm: bool):
    header("Metric 1 — Entity Extraction  (Precision / Recall / F1)")

    text          = gold_data["text"]
    gold_chars    = gold_data["gold_characters"]
    gold_world    = gold_data["gold_world_terms"]
    gold_all      = gold_chars + gold_world

    # ── spaCy ──
    from app.services.extraction import extract_chapter_intelligence
    t0 = time.perf_counter()
    result_spacy = extract_chapter_intelligence(text)
    spacy_ms = (time.perf_counter() - t0) * 1000

    spacy_chars  = result_spacy.get("active_character_names", [])
    spacy_world  = result_spacy.get("active_world_terms", [])
    spacy_all    = spacy_chars + spacy_world

    p, r, f = compute_prf(spacy_chars, gold_chars)
    metric_row("spaCy — Character   P / R / F1",
               f"{p:.0%} / {r:.0%} / {f:.0%}", f"({spacy_ms:.0f} ms)", ok=(r >= 0.5))

    p, r, f = compute_prf(spacy_world, gold_world)
    metric_row("spaCy — World Terms P / R / F1",
               f"{p:.0%} / {r:.0%} / {f:.0%}", ok=(r >= 0.5))

    p, r, f = compute_prf(spacy_all, gold_all)
    metric_row("spaCy — Combined    P / R / F1",
               f"{p:.0%} / {r:.0%} / {f:.0%}", "target: R ≥ 80%", ok=(r >= 0.8))

    # ── LLM ──
    if run_llm:
        from app.services.extraction import extract_chapter_intelligence_llm
        print(f"\n  {C.DIM}Calling LLM (this may take a few seconds)…{C.RESET}")
        t0 = time.perf_counter()
        try:
            result_llm  = extract_chapter_intelligence_llm(text)
            llm_ms      = (time.perf_counter() - t0) * 1000
            llm_chars   = result_llm.get("active_character_names", [])
            llm_world   = result_llm.get("active_world_terms", [])
            llm_all     = llm_chars + llm_world

            p, r, f = compute_prf(llm_chars, gold_chars)
            metric_row("LLM   — Character   P / R / F1",
                       f"{p:.0%} / {r:.0%} / {f:.0%}", f"({llm_ms:.0f} ms)", ok=(r >= 0.5))

            p, r, f = compute_prf(llm_world, gold_world)
            metric_row("LLM   — World Terms P / R / F1",
                       f"{p:.0%} / {r:.0%} / {f:.0%}", ok=(r >= 0.5))

            p, r, f = compute_prf(llm_all, gold_all)
            metric_row("LLM   — Combined    P / R / F1",
                       f"{p:.0%} / {r:.0%} / {f:.0%}", "target: R ≥ 80%", ok=(r >= 0.8))
        except Exception as e:
            print(f"  {C.RED}✗  LLM extraction failed: {e}{C.RESET}")
    else:
        print(f"  {C.DIM}  [LLM extraction skipped — pass --llm to enable]{C.RESET}")


# ══════════════════════════════════════════════════════════════════════════════
# Metric 2 — Graph Traversal Latency
# ══════════════════════════════════════════════════════════════════════════════

def run_graph_latency():
    header("Metric 2 — Graph Traversal Latency")

    import networkx as nx
    import tempfile
    from adapters.graph_adapter import GraphProvider

    # Use a real temp directory scoped graph so we don't pollute real data
    with tempfile.TemporaryDirectory() as tmpdir:
        # Patch DATA_DIR to use temp dir
        import app.core.story_manager as sm_mod
        original_data_dir = sm_mod.StoryManager.DATA_DIR
        sm_mod.StoryManager.DATA_DIR = tmpdir

        try:
            for n_chars in [10, 50, 100, 500, 1000]:
                gp = GraphProvider("bench_story")

                # Populate synthetic graph
                for i in range(n_chars):
                    gp.graph.add_node(f"char_{i}", type="character", last_seen_chapter=i)
                for i in range(n_chars):
                    ev_id = f"event_{i}"
                    gp.graph.add_node(ev_id, type="event", chapter_id=i)
                    gp.graph.add_edge(f"char_{i}", ev_id, relation="participant", chapter_id=i)
                    gp.graph.add_edge(ev_id, f"char_{i}", relation="featured", chapter_id=i)

                # Time importance lookup
                t0 = time.perf_counter()
                gp.get_character_importance("char_0", current_chapter=n_chars, decay_rate=0.05)
                latency_ms = (time.perf_counter() - t0) * 1000

                ok = latency_ms < 500
                metric_row(f"Graph size {n_chars:>5} nodes — lookup latency",
                           f"{latency_ms:7.1f} ms", "target: < 500 ms", ok=ok)

                # Reset graph between iterations
                gp.graph = nx.DiGraph()
        finally:
            sm_mod.StoryManager.DATA_DIR = original_data_dir


# ══════════════════════════════════════════════════════════════════════════════
# Metric 3 — TTS Real-Time Factor (RTF)
# ══════════════════════════════════════════════════════════════════════════════

BENCHMARK_TEXT = (
    "The warrior stood at the edge of the realm, his voice echoing across the valley. "
    "He had journeyed for seven years to reach this moment."
)
# Approximate speech duration at 150 words/min
APPROX_AUDIO_SECONDS = len(BENCHMARK_TEXT.split()) / 150.0


def run_tts_rtf():
    header("Metric 3 — TTS Real-Time Factor (RTF)")

    import tempfile

    # Try Kokoro first, fall back to EdgeTTS, then skip
    engines_to_try = ["kokoro", "edge_tts"]
    tried_any = False

    for engine_name in engines_to_try:
        try:
            from adapters.tts_adapter import get_tts_engine
            tts = get_tts_engine(engine_name)

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
                out_path = tf.name

            t0 = time.perf_counter()
            import asyncio
            import inspect
            if inspect.iscoroutinefunction(tts.generate_audio):
                asyncio.run(tts.generate_audio(BENCHMARK_TEXT, None, out_path))
            else:
                tts.generate_audio(BENCHMARK_TEXT, None, out_path)
            wall_time = time.perf_counter() - t0

            rtf = wall_time / APPROX_AUDIO_SECONDS
            ok  = rtf < 1.0
            metric_row(
                f"{engine_name} — RTF",
                f"{rtf:.3f}",
                f"(gen {wall_time:.2f}s / audio ~{APPROX_AUDIO_SECONDS:.2f}s)  target: < 1.0",
                ok=ok,
            )
            tried_any = True
            # Clean up
            try:
                os.remove(out_path)
            except OSError:
                pass
            break  # stop after first success

        except Exception as e:
            print(f"  {C.DIM}  [{engine_name} unavailable: {e}]{C.RESET}")

    if not tried_any:
        print(f"  {C.YELLOW}  [TTS skipped — no working engine found]{C.RESET}")


# ══════════════════════════════════════════════════════════════════════════════
# Metric 4 — Spearman Rank Correlation (ρ)
# ══════════════════════════════════════════════════════════════════════════════

def spearman_rho(rank_a: list, rank_b: list) -> float:
    """
    Computes Spearman ρ from two ordered lists of the same items.
    rank_a and rank_b are lists of items in human-judged / computed order.
    """
    if len(rank_a) != len(rank_b):
        return float("nan")
    n = len(rank_a)
    if n < 2:
        return 1.0

    pos_a = {item: i for i, item in enumerate(rank_a)}
    pos_b = {item: i for i, item in enumerate(rank_b)}

    common = [x for x in rank_a if x in pos_b]
    n = len(common)
    if n < 2:
        return float("nan")

    d_sq_sum = sum((pos_a[x] - pos_b[x]) ** 2 for x in common)
    rho = 1.0 - (6 * d_sq_sum) / (n * (n ** 2 - 1))
    return rho


def run_spearman(gold_data: dict):
    header("Metric 4 — Spearman ρ  (Character Importance Ranking)")

    import tempfile
    import app.core.story_manager as sm_mod

    gold_chars    = gold_data["gold_characters"]
    expected_rank = gold_data["expected_rank_order"]  # human-judged, best → worst
    text          = gold_data["text"]

    with tempfile.TemporaryDirectory() as tmpdir:
        original_data_dir = sm_mod.StoryManager.DATA_DIR
        sm_mod.StoryManager.DATA_DIR = tmpdir

        try:
            from app.services.ingest import ingest_chapter
            from adapters.graph_adapter import get_graph_engine, _graph_instances

            # Clear any cached graph instance
            _graph_instances.clear()

            # Create a throwaway story
            story_uuid = sm_mod.StoryManager.create_story("eval_bench")

            # Ingest the gold chapter
            ingest_chapter(story_uuid, "Gold Chapter", text, extractor="spacy")

            # Pull the computed ranking from runtime
            from app.services.ingest import load_runtime
            _, runtime_db = load_runtime(story_uuid)

            if not runtime_db:
                print(f"  {C.YELLOW}  [No characters ingested — cannot compute ρ]{C.RESET}")
                return

            # Sort characters by confidence_score descending → computed rank
            computed_sorted = sorted(
                runtime_db.values(),
                key=lambda c: c.confidence_score,
                reverse=True,
            )
            computed_rank = [c.character_id for c in computed_sorted]

            # Convert expected_rank (display names) to ids for comparison
            def to_id(name: str) -> str:
                return name.lower().replace(" ", "_").replace("'", "")

            expected_ids = [to_id(n) for n in expected_rank]
            # Filter to only IDs that actually appear in both lists
            common_ids = [x for x in expected_ids if x in computed_rank]

            rho = spearman_rho(expected_ids, computed_rank)

            ok = not math.isnan(rho) and rho >= 0.7
            rho_str = f"{rho:.3f}" if not math.isnan(rho) else "N/A"
            metric_row(
                "Spearman ρ (computed vs. human)",
                rho_str,
                f"n={len(common_ids)} common chars  target: ρ ≥ 0.70",
                ok=ok,
            )

            print(f"\n  {C.DIM}  Human rank   : {expected_ids}")
            print(f"  Computed rank: {computed_rank[:len(expected_ids)]}{C.RESET}")

        except Exception as e:
            print(f"  {C.RED}✗  Spearman computation failed: {e}{C.RESET}")
            import traceback
            traceback.print_exc()
        finally:
            _graph_instances.clear()
            sm_mod.StoryManager.DATA_DIR = original_data_dir


# ══════════════════════════════════════════════════════════════════════════════
# Entry Point
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Webnovel Architect — Phase 6 Evaluation")
    parser.add_argument("--llm",    action="store_true",  help="Include LLM extraction metric (makes API call).")
    parser.add_argument("--no-tts", action="store_true",  help="Skip TTS RTF metric.")
    args = parser.parse_args()

    print(f"\n{C.BOLD}{C.CYAN}╔══════════════════════════════════════════════════════════╗")
    print(f"║   Webnovel Architect — Phase 6 Evaluation Harness       ║")
    print(f"╚══════════════════════════════════════════════════════════╝{C.RESET}")

    # Load gold-standard data
    gold_path = os.path.join(ROOT, "dataset", "gold_standard.json")
    if not os.path.exists(gold_path):
        print(f"{C.RED}ERROR: gold_standard.json not found at {gold_path}{C.RESET}")
        sys.exit(1)

    with open(gold_path, "r", encoding="utf-8") as f:
        gold_data = json.load(f)

    # Run metrics
    run_entity_extraction(gold_data, run_llm=args.llm)
    run_graph_latency()
    if not args.no_tts:
        run_tts_rtf()
    else:
        print(f"\n  {C.DIM}[TTS metric skipped via --no-tts flag]{C.RESET}")
    run_spearman(gold_data)

    print(f"\n{C.BOLD}{C.CYAN}{'─' * 60}")
    print(f"  Evaluation complete.")
    print(f"{'─' * 60}{C.RESET}\n")


if __name__ == "__main__":
    main()
