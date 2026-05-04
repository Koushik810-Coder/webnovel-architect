# Fact Check Report: Webnovel Architect Research Paper vs. Codebase

**Target Document:** `Webnovel_Architect_Research_Paper_28.md`
**Date:** Current
**Status:** ✅ Mostly Verified (with one minor default value discrepancy)

## 1. System Architecture (Neuro-Symbolic Switchboard)
* **Claim:** The Neural layer routes semantic tasks to a remote LLM API via **LiteLLM** using `groq/llama-3.1-8b-instant`, with a **spaCy (`en_core_web_sm`)** deterministic fallback.
* **Codebase Finding:** ✅ **VERIFIED**. 
  * `adapters/llm_adapter.py` imports and utilizes `litellm`.
  * `app/core/config.py` clearly sets `"llm_model"` and `"fallback_llm"` to `"groq/llama-3.1-8b-instant"`.
  * Extensive usage of `extractor="spacy"` is present in the tests and fallback logic, which explicitly uses `spacy.load("en_core_web_sm")` (and sometimes `md`).

## 2. Symbolic Runtime (Graph Database)
* **Claim:** The Symbolic layer uses the Python `networkx` library to build a Directed Acyclic Graph (DAG) for timeline reasoning.
* **Codebase Finding:** ✅ **VERIFIED**. 
  * `adapters/graph_adapter.py` manages the underlying operations and utilizes `networkx` extensively.

## 3. Temporal Decay Formulation
* **Claim:** The timed-decay algorithm uses the formulation `Score(c) = PageRank(c) × (1 - λ)^Δt` with a temporal decay rate of **λ = 0.15**.
* **Codebase Finding:** ⚠️ **PARTIALLY VERIFIED / MINOR DISCREPANCY**.
  * The mathematical decay logic is correctly implemented in `adapters/graph_adapter.py` (`get_character_importance`).
  * However, the **default** `decay_rate` parameter in the codebase functions (e.g., `ingest_chapter` and `get_character_importance`) is set to **`0.05`**, not `0.15`.
  * *Note:* Simulation scripts (like `scripts/simulate_decay.py` and `scripts/plot_decay_results.py`) do explicitly test and validate the **`0.15`** rate as an "Aggressive Decay PoC", aligning with the paper's ablation study findings.

## 4. Debut Prominence Quotient (DPQ)
* **Claim:** Solves the cold-start issue for voice assignment. A character achieving a DPQ value of **0.40** on their debut chapter receives a temporary graduation score of **0.16**.
* **Codebase Finding:** ✅ **VERIFIED**.
  * `adapters/graph_adapter.py` contains `get_debut_prominence(name, debut_chapter_id)`.
  * The bootstrapping logic checks exactly: `if dpq >= 0.40:`.
  * If met, the system forces provisional graduation by assigning `DELTA_UPPER + 0.01`. Since `DELTA_UPPER` is 0.15, `0.15 + 0.01 = 0.16`. This matches the paper's exact numerical claim.

## 5. Graduation State Machine Thresholds
* **Claim:** Upper Bound (δ_upper) = **0.15**, Lower Bound (δ_lower) = **0.05**, Main Cast Threshold = **0.50**.
* **Codebase Finding:** ✅ **VERIFIED**.
  * `app/core/graduation.py` defines `DELTA_UPPER = 0.15` and `MAIN_CAST_THRESHOLD = 0.50`.
  * Evaluation scripts (e.g., `scripts/evaluate.py`) explicitly track characters falling below `δ_lower = 0.05` to trigger voice release.

## 6. Voice Broker & Prosody Adjustments
* **Claim:** Character relationships are extracted with emotional valences (e.g., hostile, mentorship, betrayal) and mapped to TTS prosody parameters, such as hostile speech triggering a **1.25x** normal speech rate.
* **Codebase Finding:** ✅ **VERIFIED**.
  * `app/services/extraction.py` explicitly lists relation types: `"friendly", "hostile", "combat", "neutral", "mentor", "romantic", "betrayal"`.
  * `scripts/simulate_audio_tts.py` defines `dygrag_speed=1.25` for hostile/combat edges, matching the "25% faster speech" claim perfectly.

---

### Conclusion
The claims presented in the research paper are structurally, logically, and numerically consistent with the actual implementation in the repository. The only point of note is that the codebase's default variable for decay rate is `0.05`, while the paper heavily focuses on the `0.15` lambda run from the ablation study.
