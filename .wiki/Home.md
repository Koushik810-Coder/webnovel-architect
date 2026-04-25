# 🏛️ Webnovel Architect — Project Wiki

> **Zero-GPU Neuro-Symbolic Story Intelligence Engine** | Phase 8 PoC Final | April 2026

Webnovel Architect transforms serialized web fiction into living, multi-modal story worlds — auto-generating a persistent character wiki, a dynamic knowledge graph, and a fully synthesized multi-voice audiobook, all on consumer-grade CPU hardware.

---

## 🗺️ Wiki Navigation

| Page | Description |
|------|-------------|
| **[Home](Home)** | You are here — overview and navigation |
| **[Getting Started](Getting-Started)** | Installation, setup, and quick-start guide |
| **[System Architecture](System-Architecture)** | The Neuro-Symbolic Switchboard, DyG-RAG design |
| **[Pipeline Walkthrough](Pipeline-Walkthrough)** | End-to-end: Eye → Brain → Director → Voice |
| **[Graduation Algorithm](Graduation-Algorithm)** | Temporal Decay PageRank + DPQ explained |
| **[Technology Stack](Technology-Stack)** | All components, adapters, and providers |
| **[Evaluation Results](Evaluation-Results)** | Benchmarks, metrics, λ ablation proofs |
| **[API Reference](API-Reference)** | Key modules, functions, and data models |
| **[Configuration Guide](Configuration-Guide)** | `config.yaml`, `.env`, and provider switching |
| **[Development & Testing](Development-and-Testing)** | TDD workflow, pytest suite, contributing |
| **[Roadmap](Roadmap)** | Phase history and future milestones |

---

## ⚡ 30-Second Overview

```
Raw Chapter Text  →  "The Eye" (Extraction)  →  "The Brain" (Knowledge Graph)
                                                          ↓
                   "The Voice" (Audio MP3+VTT)  ←  "The Director" (Graduation)
                   "Memory" (Wiki Markdown)     ←
```

**The core academic problem solved:** the **Casting Paradox** — the impossibility of assigning a persistent synthetic voice to a character at their *first appearance*, before narrative evidence of their importance exists.

**The solution:** a **DyG-RAG (Dynamic Graph Retrieval-Augmented Generation)** architecture pairing cloud-based neural extraction with a local Temporal Decay PageRank engine on CPU.

---

## 🏆 Validated Benchmarks (Phase 8)

| Metric | Result | Target |
|--------|--------|--------|
| Character Entity F1 (LLM pipeline) | **100%** | ≥ 80% ✅ |
| Graph traversal latency @ 1,000 nodes | **3.2 ms** | < 500 ms ✅ |
| TTS Real-Time Factor (RTF) | **0.127** | < 1.0 ✅ |
| Multi-chapter NER Recall (5-ch corpus) | **1.000** | — ✅ |

---

## 🔑 Key Concepts

- **DyG-RAG** — Dynamic Graph RAG using timestamped Dynamic Event Units (DEUs) for temporal reasoning
- **Temporal Decay PageRank** — Characters fade from memory when absent, preventing "temporal hallucination"
- **DPQ (Debut Prominence Quotient)** — Bootstraps main characters from Chapter 1 without a warm-up period
- **The Switchboard** — Modular adapter pattern; swap LLM/TTS/Graph backends via one config file
- **Voice Locking** — Once a character graduates, their voice ID is permanently locked for continuity

---

*Last updated: April 2026 | Phase 8 PoC Final*
