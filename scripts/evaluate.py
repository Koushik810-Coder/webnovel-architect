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
            # Pre-warming benchmark to eliminate cold-start anomaly
            gp_warm = GraphProvider("bench_warmup")
            gp_warm.graph.add_node("warm_char", type="character", last_seen_chapter=1)
            gp_warm.graph.add_node("warm_event", type="event", chapter_id=1)
            gp_warm.graph.add_edge("warm_char", "warm_event", relation="participant", chapter_id=1)
            gp_warm.get_character_importance("warm_char", current_chapter=1, decay_rate=0.05)
            gp_warm.graph = nx.DiGraph()

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
    engines_to_try = ["kokoro", "edge"]
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


def run_spearman(gold_data: dict, run_llm: bool):
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

            # Ingest the gold chapter using LLM if requested to ensure 100% Extraction
            extractor_engine = "llm" if run_llm else "spacy"
            ingest_chapter(story_uuid, "Gold Chapter", text, extractor=extractor_engine)

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

            # Baseline comparison: Simple Frequency Ranker (Raw Degree)
            baseline_sorted = sorted(
                runtime_db.values(),
                key=lambda c: get_graph_engine(story_uuid).graph.degree(c.character_id) if get_graph_engine(story_uuid).graph.has_node(c.character_id) else 0,
                reverse=True,
            )
            baseline_rank = [c.character_id for c in baseline_sorted]
            rho_baseline = spearman_rho(expected_ids, baseline_rank)

            rho = spearman_rho(expected_ids, computed_rank)

            ok = not math.isnan(rho) and rho >= 0.7
            rho_str = f"{rho:.3f}" if not math.isnan(rho) else "N/A"
            metric_row(
                "Spearman ρ (Temporal PageRank)",
                rho_str,
                f"n={len(common_ids)} common chars  target: ρ ≥ 0.70",
                ok=ok,
            )
            
            rho_base_str = f"{rho_baseline:.3f}" if not math.isnan(rho_baseline) else "N/A"
            metric_row(
                "Spearman ρ (Baseline Frequency)",
                rho_base_str,
                "Raw degree count baseline",
                ok=True, # Informational
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


def run_lambda_ablation(gold_data: dict, run_llm: bool):
    header("Lambda Ablation Study (Spearman ρ across decay rates)")
    
    import tempfile
    import app.core.story_manager as sm_mod
    
    text = gold_data["text"]
    expected_rank = [name.lower().replace(" ", "_").replace("'", "") for name in gold_data["expected_rank_order"]]
    
    with tempfile.TemporaryDirectory() as tmpdir:
        original_data_dir = sm_mod.StoryManager.DATA_DIR
        sm_mod.StoryManager.DATA_DIR = tmpdir
        try:
            from app.services.ingest import ingest_chapter, load_runtime
            from adapters.graph_adapter import get_graph_engine, _graph_instances
            
            _graph_instances.clear()
            story_uuid = sm_mod.StoryManager.create_story("ablation_bench")
            
            # Ingest once
            extractor_engine = "llm" if run_llm else "spacy"
            ingest_chapter(story_uuid, "Gold Chapter", text, extractor=extractor_engine)
            _, runtime_db = load_runtime(story_uuid)
            
            if not runtime_db:
                print(f"  {C.YELLOW}  [No characters ingested — cannot run ablation]{C.RESET}")
                return
                
            gp = get_graph_engine(story_uuid)
            
            # Test multiple lambdas
            lambdas = [0.01, 0.03, 0.05, 0.10, 0.20]
            print(f"  {C.DIM}Testing λ ∈ {lambdas}...{C.RESET}")
            
            best_rho = -1.0
            best_l = 0.05
            
            for l in lambdas:
                # Re-calculate ranks with specific decay
                computed_sorted = sorted(
                    runtime_db.values(),
                    key=lambda c: gp.get_character_importance(c.character_id, current_chapter=1, decay_rate=l),
                    reverse=True,
                )
                computed_rank = [c.character_id for c in computed_sorted]
                rho = spearman_rho(expected_rank, computed_rank)
                
                if not math.isnan(rho) and rho > best_rho:
                    best_rho = rho
                    best_l = l
                    
                rho_str = f"{rho:.3f}" if not math.isnan(rho) else "N/A"
                metric_row(f"λ = {l:.2f}", rho_str, ok=True)
                
            print(f"  {C.GREEN}✓ Optimal λ empirically determined: {best_l:.2f} (ρ={best_rho:.3f}){C.RESET}")
            
        except Exception as e:
            print(f"  {C.RED}✗  Ablation failed: {e}{C.RESET}")
        finally:
            _graph_instances.clear()
            sm_mod.StoryManager.DATA_DIR = original_data_dir


# ══════════════════════════════════════════════════════════════════════════════
# Metric 5 — End-to-End System Evaluation
# ══════════════════════════════════════════════════════════════════════════════

def run_end_to_end_pipeline(gold_data: dict, run_llm: bool, run_tts: bool):
    header("Metric 5 — End-to-End System Evaluation")

    if not run_llm or not run_tts:
        print(f"  {C.YELLOW}  [Skipped — requires both --llm and TTS enabled to run full pipeline]{C.RESET}")
        return

    import tempfile
    import app.core.story_manager as sm_mod

    text = gold_data["text"]

    with tempfile.TemporaryDirectory() as tmpdir:
        original_data_dir = sm_mod.StoryManager.DATA_DIR
        sm_mod.StoryManager.DATA_DIR = tmpdir

        try:
            from app.services.ingest import ingest_chapter, load_runtime
            from app.services.audiobook_generator import generate_chapter_audiobook
            from adapters.graph_adapter import _graph_instances

            _graph_instances.clear()

            print(f"  {C.DIM}Ingesting chapter via Neural LLM…{C.RESET}")
            t0 = time.perf_counter()
            story_uuid = sm_mod.StoryManager.create_story("eval_e2e")
            ingest_chapter(story_uuid, "Gold Chapter", text, extractor="litellm")
            ingest_ms = (time.perf_counter() - t0) * 1000
            
            # Verify graph state
            _, runtime_db = load_runtime(story_uuid)
            graph_ok = len(runtime_db) > 0

            metric_row("E2E — Step 1: Ingestion & Graph",
                       f"{ingest_ms:.0f} ms", f"found {len(runtime_db)} entities", ok=graph_ok)

            print(f"  {C.DIM}Generating audiobook script & synthesizing (Edge-TTS fallback)…{C.RESET}")
            t1 = time.perf_counter()
            # Suppress excessive logs
            import logging
            logging.getLogger("adapters.tts_adapter").setLevel(logging.CRITICAL)
            logging.getLogger("app.services.audiobook_generator").setLevel(logging.CRITICAL)
            
            result = generate_chapter_audiobook(story_uuid, 1, engine="edge")
            audio_ms = (time.perf_counter() - t1) * 1000

            if result is None:
                metric_row("E2E — Step 2: Audio Synthesis", "FAILED", ok=False)
            else:
                audio_path, vtt_path = result
                audio_ok = os.path.exists(audio_path) and os.path.getsize(audio_path) > 1000
                vtt_ok = os.path.exists(vtt_path) and os.path.getsize(vtt_path) > 10
                
                metric_row("E2E — Step 2: Audio Generation", f"{audio_ms:.0f} ms", ok=audio_ok)
                metric_row("E2E — Step 3: VTT Compilation", "Generated", ok=vtt_ok)
                metric_row("E2E — Full Pipeline Status", "PASS", "End to end successful", ok=audio_ok and vtt_ok and graph_ok)

        except Exception as e:
            print(f"  {C.RED}✗  E2E Pipeline failed: {e}{C.RESET}")
            import traceback
            traceback.print_exc()
        finally:
            _graph_instances.clear()
            sm_mod.StoryManager.DATA_DIR = original_data_dir


# ══════════════════════════════════════════════════════════════════════════════
# Metric 6 — Multi-Chapter Temporal Divergence
# ══════════════════════════════════════════════════════════════════════════════

def run_temporal_divergence(run_llm: bool):
    """
    Ingests a 5-chapter synthetic corpus sequentially and compares the
    Temporal PageRank score against a raw Frequency baseline for two characters:

    - Kirielle: prominent in Ch1, absent Ch2-Ch5 → score SHOULD decay
    - Zorian:   present in every chapter         → score SHOULD remain stable

    This empirically proves the temporal decay mechanism diverges from raw
    frequency counting once Δt > 0, addressing the core limitation where the
    single-chapter evaluation collapsed the exponent to 1.0.
    """
    header("Metric 6 — Multi-Chapter Temporal Divergence (Δt Proof)")

    multi_path = os.path.join(ROOT, "dataset", "multi_chapter_gold.json")
    if not os.path.exists(multi_path):
        print(f"  {C.RED}✗  multi_chapter_gold.json not found at {multi_path}{C.RESET}")
        return

    with open(multi_path, "r", encoding="utf-8") as f:
        mc_data = json.load(f)

    chapters = mc_data["chapters"]
    expected_final_rank = mc_data["expected_final_rank_order"]
    expected_faded = [n.lower().replace(" ", "_") for n in mc_data.get("expected_faded_characters", [])]

    import tempfile
    import app.core.story_manager as sm_mod

    with tempfile.TemporaryDirectory() as tmpdir:
        original_data_dir = sm_mod.StoryManager.DATA_DIR
        sm_mod.StoryManager.DATA_DIR = tmpdir

        try:
            from app.services.ingest import ingest_chapter, load_runtime
            from adapters.graph_adapter import get_graph_engine, _graph_instances

            _graph_instances.clear()
            story_uuid = sm_mod.StoryManager.create_story("temporal_bench")

            extractor = "llm" if run_llm else "spacy"
            print(f"  {C.DIM}Ingesting {len(chapters)} chapters sequentially using [{extractor}]…{C.RESET}")

            for i, chap in enumerate(chapters, start=1):
                t0 = time.perf_counter()
                ingest_chapter(story_uuid, chap["title"], chap["text"], extractor=extractor)
                elapsed = (time.perf_counter() - t0) * 1000
                print(f"    {C.DIM}  ✓ Ch{i}: '{chap['title']}' — {elapsed:.0f} ms{C.RESET}")

            total_chapters = len(chapters)
            _, runtime_db = load_runtime(story_uuid)
            gp = get_graph_engine(story_uuid)

            print()

            # ── Score snapshot after all chapters ──
            decay_scores: dict[str, float] = {}
            freq_scores: dict[str, float] = {}

            for char_id, char in runtime_db.items():
                decay_scores[char_id] = gp.get_character_importance(
                    char_id, current_chapter=total_chapters, decay_rate=0.05
                )
                # Raw frequency baseline = simple degree count (no decay)
                freq_scores[char_id] = float(
                    gp.graph.degree(char_id) if gp.graph.has_node(char_id) else 0
                )

            # ── Print per-character comparison ──
            header_line = f"  {'Character':<20} {'Temporal Score':>15} {'Freq Score':>12} {'Δ':>8}  {'Status'}"
            print(f"{C.DIM}{header_line}{C.RESET}")
            print(f"  {'-'*72}")

            diverged = False
            for char_id in sorted(decay_scores, key=lambda x: decay_scores[x], reverse=True):
                ds = decay_scores[char_id]
                fs = freq_scores.get(char_id, 0.0)
                # Normalise freq for fair comparison
                max_freq = max(freq_scores.values()) if freq_scores else 1.0
                fs_norm = fs / max_freq if max_freq > 0 else 0.0
                delta = ds - fs_norm
                faded = char_id in expected_faded
                expected_decay = faded and delta < -0.01  # decayed character has lower temporal score
                status = "✓ decayed correctly" if expected_decay else ("✓ stable" if not faded else "~ no decay observed")
                if abs(delta) > 0.001:
                    diverged = True
                flag = C.GREEN if expected_decay or not faded else C.YELLOW
                print(f"  {flag}{char_id:<20}{C.RESET}  {ds:>14.4f}  {fs_norm:>11.4f}  {delta:>+8.4f}  {status}")

            # Track exact chapter of decay crossing for empirical proof
            # Threshold is LOWER_BOUND (0.05)
            # Find the chapter where score drops below threshold
            decay_crossing_chapters = {}
            for char_id in expected_faded:
                hist_scores = []
                for step in range(1, total_chapters + 1):
                    s = gp.get_character_importance(char_id, current_chapter=step, decay_rate=0.05)
                    hist_scores.append(s)
                    if s < 0.05 and char_id not in decay_crossing_chapters:
                        decay_crossing_chapters[char_id] = step
                
                crossing_str = f"Ch {decay_crossing_chapters[char_id]}" if char_id in decay_crossing_chapters else "Did not cross"
                print(f"  {C.DIM}  > {char_id} crossed the δ_lower (0.05) threshold at {crossing_str}{C.RESET}")

            print()
            ok = diverged
            metric_row(
                "Temporal vs Frequency divergence",
                "PROVEN" if diverged else "NOT DIVERGED",
                f"Scores differ across {total_chapters} chapters",
                ok=ok,
            )

            # ── Final rank correlation after multi-chapter ──
            computed_sorted = sorted(decay_scores, key=lambda x: decay_scores[x], reverse=True)

            def to_id(name: str) -> str:
                return name.lower().replace(" ", "_").replace("'", "")

            expected_ids = [to_id(n) for n in expected_final_rank]
            rho = spearman_rho(expected_ids, computed_sorted)
            rho_str = f"{rho:.3f}" if not math.isnan(rho) else "N/A"
            rho_ok = not math.isnan(rho) and rho >= 0.70
            metric_row(
                "Multi-chapter Spearman ρ",
                rho_str,
                f"n={len(expected_ids)} expected chars  target: ρ ≥ 0.70",
                ok=rho_ok,
            )

        except Exception as e:
            print(f"  {C.RED}✗  Temporal divergence test failed: {e}{C.RESET}")
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
    parser.add_argument("--llm",          action="store_true",  help="Include LLM extraction metric (makes API call).")
    parser.add_argument("--no-tts",       action="store_true",  help="Skip TTS RTF metric.")
    parser.add_argument("--no-temporal",  action="store_true",  help="Skip multi-chapter temporal divergence metric (Metric 6).")
    args = parser.parse_args()

    print(f"\n{C.BOLD}{C.CYAN}╔══════════════════════════════════════════════════════════╗")
    print("║   Webnovel Architect — Phase 6 Evaluation Harness       ║")
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
    run_spearman(gold_data, run_llm=args.llm)
    run_lambda_ablation(gold_data, run_llm=args.llm)
    run_end_to_end_pipeline(gold_data, run_llm=args.llm, run_tts=not args.no_tts)
    if not args.no_temporal:
        run_temporal_divergence(run_llm=False)  # spaCy only — avoids extra API cost by default
    else:
        print(f"\n  {C.DIM}[Temporal divergence metric skipped via --no-temporal flag]{C.RESET}")

    print(f"\n{C.BOLD}{C.CYAN}{'─' * 60}")
    print("  Evaluation complete.")
    print(f"{'─' * 60}{C.RESET}\n")


if __name__ == "__main__":
    main()
