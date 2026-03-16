# Webnovel Architect — Review 1 Presentation (Final Deck)
**PRASAD V. POTLURI SIDDHARTHA INSTITUTE OF TECHNOLOGY · Dept. of CSE (Data Science)**

---

## SLIDE 1 — Title Slide

**[VISUAL: Sleek dark background. Glowing teal/violet interconnected network nodes radiating from centre. University logo placeholder top-left. All text white/light.]**

**WEBNOVEL ARCHITECT**
*Neuro-Symbolic Story Intelligence System*

Leveraging LLMs · Dynamic Graph RAG (DyG-RAG) · Real-Time Audio Drama Synthesis

**Guide:** Dr. B. Janakiramaiah | Professor, CSE (DS) & CSE (AIML)
**Team:** [person1] · [person2] · [person3]
Kanuru, Vijayawada – 521212

> 🎤 **SPEAKER NOTES:**
> "Good morning, respected panel and Dr. Janakiramaiah. We present *Webnovel Architect* — a Neuro-Symbolic Story Intelligence System. We tackle a unique challenge: taking continuously evolving serialized webnovels and using LLMs and Dynamic Graph RAG to auto-track the narrative, rank character importance, and synthesize real-time, casted audio dramas. No GPU required."

---

## SLIDE 2 — Literature Survey & Comparative Analysis

**[VISUAL: Top half — 3 floating paper cards with icons. Bottom half — sharp comparison table, 'OUR PROJECT' row highlighted accent color (teal). Clean sans-serif typography.]**

### 01 | LITERATURE SURVEY

**Papers Researched:**
| # | Paper | Source | Year |
|---|-------|---------|------|
| ★ | *DyG-RAG: Dynamic Graph Retrieval-Augmented Generation* | arXiv | 2025 |
| 2 | *From Local to Global: A Graph RAG Approach* | Microsoft / arXiv | 2024 |
| 3 | *STAGE: Knowledge Graph & Narrative Understanding* | Stanford / arXiv | 2024 |

---

**Comparative Analysis:**
| System | Graph Type | Temporal | Character Casting | Evaluation |
|---|---|---|---|---|
| Standard RAG | None | ✗ | ✗ | QA Accuracy |
| Static GraphRAG | Static Entity | ✗ | ✗ | Comprehensiveness |
| DyG-RAG (2025) | Dynamic Event | ✓ | ✗ | Temporal QA |
| **★ OUR PROJECT** | **Dynamic + PageRank** | **✓** | **✓ Voice Cast** | **Recall / RTF / ρ** |

> 🎤 **SPEAKER NOTES:**
> "Our research foundation is DyG-RAG (2025). Traditional RAG fails at temporal reasoning. While DyG-RAG solves this for QA benchmarks, it has no mechanism for narrative character casting. Microsoft's GraphRAG and Stanford's STAGE use static graphs or scene-level snapshots — too rigid and costly to rebuild for ongoing webnovels. Our project bridges this by combining dynamic event graphs with automated character importance scoring and voice casting."

---

## SLIDE 3 — The Research Gap

**[VISUAL: Three tall side-by-side cards. Each card: top = bold red ✗ problem (6 words max), bottom = green ✓ solution. Dark background, heavy typography. No extra text.]**

### RESEARCH GAP & OUR CONTRIBUTION

| | Problem | Our Solution |
|---|---|---|
| ✗→✓ | Static graphs freeze after indexing | Real-time graph updates per chapter |
| ✗→✓ | RAG answers questions; it doesn't cast characters | PageRank + Temporal Decay → auto voice cast |
| ✗→✓ | Requires expensive GPU hardware | Zero-GPU Switchboard — runs on a laptop |

> 🎤 **SPEAKER NOTES:**
> "Three precise gaps. One: existing graphs require full expensive rebuilds when a new chapter drops — ours updates live. Two: a raw graph doesn't know who the 'Main Character' is. We apply PageRank with temporal decay to determine narrative importance and assign TTS voices automatically. Three: we engineered a Zero-GPU abstraction layer — the Switchboard — so this whole system runs on any student laptop for free."

---

## SLIDE 4 — Base Paper Deep Dive

**[VISUAL: LEFT — horizontal 5-stage arrow pipeline (chevrons, gradient teal→violet). RIGHT — 3 card columns for the Core Components. Consistent dark palette. No text blocks.]**

### 02 | BASE PAPER EXPLANATION
**DyG-RAG** · Sun et al. · arXiv:2507.13396

**Workflow Pipeline:**
```
User Query  ➔  DEU Extraction  ➔  Event Graph Build  ➔  Timeline Traversal  ➔  Time-CoT Answer
```

**3 Core Components:**

| Component | Purpose | Key Mechanism |
|---|---|---|
| Dynamic Event Units (DEU) | Capture events in time | Semantic + explicit temporal anchors |
| Event Graph | Link related events | Entities + temporal adjacency edges |
| Timeline Retrieval | Fetch ordered context | Time-CoT chronological traversal |

> 🎤 **SPEAKER NOTES:**
> "DyG-RAG's key innovation is the Dynamic Event Unit — it encodes *what* happened and *when* into a single retrievable unit, eliminating the temporal hallucinations common in LLMs. These units are linked into a topological event graph. When a question is posed, a Time-Chain-of-Thought strategy traverses the graph chronologically to produce a temporally grounded answer."

---

## SLIDE 5 — Base Paper Limitations vs Our Improvements

**[VISUAL: Clean two-column layout. LEFT header = "DyG-RAG (Base)" with red tones. RIGHT header = "Webnovel Architect (Ours)" with green/teal tones. 4 matching rows with ✗/✓ pairs.]**

### LIMITATIONS → OUR IMPROVEMENTS

| DyG-RAG (Base Paper) ✗ | Webnovel Architect ✓ |
|---|---|
| QA output only | Audio Dramas + Character Wikis |
| Static, pre-indexed documents | Live ingestion of serialized chapters |
| No character importance scoring | Temporal Decay PageRank → "Main Cast" |
| CLI / code-only interface | Interactive Streamlit SPA Dashboard |

> 🎤 **SPEAKER NOTES:**
> "DyG-RAG was designed for answering questions from finished, static documents via code. We adapted it for continuous serialization. Critically, instead of just answering questions, our system actively uses the graph to calculate character centrality — determining who the main cast is at any moment — then outputs a fully mixed audio drama through a polished Streamlit UI."

---

## SLIDE 6 — System Architecture (5 Layers)

**[VISUAL: 5 stacked horizontal bars. Color-coded L3=Indigo, L4=Violet, L5=Deep-Purple (MATCH TO SLIDE 7). Each bar: small left icon, layer name bold, tech stack right-aligned. Downward arrows between layers. The diagram IS the content — no text list below it.]**

### 03 | TECHNICAL ARCHITECTURE — 5-LAYER DESIGN

| Layer | Name | Technology Stack | Color |
|---|---|---|---|
| L1 | Presentation | Streamlit SPA · 3 Tabs (Ingest / Wiki / Audio) | Teal |
| L2 | Switchboard | Zero-GPU Router · Adapter Pattern | Blue |
| **L3** | **Ingestion "The Eye"** | **LiteLLM (Gemini Flash) + spaCy NER** | **Indigo** |
| **L4** | **Story Runtime "The Brain"** | **NetworkX / KuzuDB · JSON Persistence** | **Violet** |
| **L5** | **Graduation "The Director"** | **PageRank + Temporal Decay · Kokoro ONNX / Edge-TTS** | **Deep-Purple** |

▼ *Flow: Raw Text → L3 → L4 → L5 → Wiki + Audio → L1*

> 🎤 **SPEAKER NOTES:**
> "Five decoupled layers. The Presentation layer is our Streamlit dashboard. Below it, the Switchboard is the key to going Zero-GPU — it dynamically routes requests to lightweight APIs and falls back to local models. The Ingestion layer extracts events using Gemini Flash. The Runtime layer persists the story in a NetworkX graph. The Output/Graduation layer runs PageRank centrality scoring and generates the audio."

---

## SLIDE 7 — Pipeline Workflow (4 Phases)

**[VISUAL: 4 circular hubs connected by arrows. Hub colors MATCH Slides 6 layers exactly: Hub 01=Indigo, Hub 02=Violet, Hub 03=Deep-Purple, Hub 04=Teal. Under each hub: bold name + Role + Tool + Output in 2-3 words max.]**

### PIPELINE WORKFLOW — HOW DATA MOVES THROUGH THE ARCHITECTURE
*(Colors match Layers 3–5 from the previous slide)*

```
[Indigo]               [Violet]              [Deep-Purple]           [Teal]
01 INGESTION       →  02 GRAPH RUNTIME  →  03 GRADUATION       →  04 VOICE SYNTHESIS
"The Eye"              "The Brain"           "The Director"          "The Voice"
LiteLLM + spaCy        NetworkX              PageRank + Decay        Kokoro ONNX
↓ JSON Events          ↓ Network Graph       ↓ Main Cast (>0.15)     ↓ Audio Drama MP3
```

> 🎤 **SPEAKER NOTES:**
> "The same four colored nodes from this diagram map directly to Layers 3-5 in the last slide. A raw chapter enters the Eye (Indigo). Structured JSON events go into the Brain (Violet). The Director (Deep-Purple) calculates centrality — if a character's PageRank exceeds 0.15, they graduate to Main Cast. The Voice (Teal) assigns a dedicated Kokoro TTS voice and renders the audio."

---

## SLIDE 8 — Dataset & Preprocessing

**[VISUAL: Top — 3 horizontal data source cards (icon + name + type tags). Bottom — 5-step horizontal preprocessing pipeline (numbered boxes + arrows). Compact, no padding wasted.]**

### 04 | DATASET STRATEGY & PREPROCESSING

**Data Sources:**
| # | Source | Type | Purpose |
|---|---|---|---|
| 01 | Public Domain Webnovel Chapters | Text / NLP | Raw pipeline input & long-context testing |
| 02 | Generated Event Graph (Runtime) | JSON / Graph | System memory — canonical story knowledge |
| 03 | Kokoro Voice Embeddings Registry | Acoustic | Deterministic voice-actor assignment |

**5-Step Preprocessing:**
```
1. HTML Clean  →  2. Sentence Chunk  →  3. Dual Extract (LLM+NER)  →  4. Graph Insert  →  5. Centrality Update
```

**Ethics:** Open-license text only · Bounded LLM generation · Deterministic, non-demographic voice assignment

> 🎤 **SPEAKER NOTES:**
> "Our data strategy has three pillars: raw text chapters as input, auto-generated JSON event graphs as memory, and acoustic voice embeddings for casting. Every chapter goes through a strict 5-step preprocessing pipeline before touching the graph — we clean, chunk, dual-extract with a Gemini+spaCy fallback, insert nodes, then trigger a global PageRank update."

---

## SLIDE 9 — Tech Stack

**[VISUAL: 2×3 grid of tech cards. Each card: logo placeholder icon (top), bold Tool Name, Role sub-label, 1-line justification. Dark card, subtle teal border. Matches example PDF grid format exactly.]**

### 05 | TECHNOLOGY STACK

| Tool | Role | Why? |
|---|---|---|
| **Python 3.9+** | Core Language | NLP ecosystem · modular architecture |
| **Streamlit** | Frontend SPA | Rapid dashboard · Python-native |
| **LiteLLM / Gemini Flash** | LLM Engine | Zero-GPU extraction · free-tier API |
| **NetworkX & KuzuDB** | Graph Database | Lightweight dev → scalable production |
| **Kokoro ONNX & Edge-TTS** | Audio Synthesis | Offline CPU TTS + cloud fallback |
| **spaCy** | NER Fallback | Deterministic · local · no API cost |

> 💡 **Why this combination?** LLMs extract, graphs reason — no GPU training needed.

> 🎤 **SPEAKER NOTES:**
> "Every tool was chosen for modularity and Zero-GPU compatibility. LiteLLM with Gemini Flash achieves high accuracy without local hardware. NetworkX gives us the dynamic graph. Kokoro ONNX delivers studio-quality voices entirely offline on a CPU. If any online service fails, the Switchboard silently reroutes to a local fallback."

---

## SLIDE 10 — Implementation & Evaluation Plan

**[VISUAL: Left column = Implementation checklist with ✓/○ and phase names. Right column = evaluation strategy box with 3 labeled metrics on colored cards. Split layout, matching architecture colors.]**

### IMPLEMENTATION STATUS & EVALUATION STRATEGY

**Implementation Phases:**
| Status | Phase | Outcome |
|---|---|---|
| ✓ | Phase 1 — Environment & NLP | spaCy + virtual env running |
| ✓ | Phase 2 — Dual Extraction & Switchboard | LiteLLM + adapter pattern live |
| ✓ | Phase 3 — Graph Runtime | NetworkX graph with JSON persistence |
| ✓ | Phase 4 — Graduation System | PageRank + Temporal Decay implemented |
| ✓ | Phase 5 — Streamlit UI & Audio | Full interactive dashboard + Kokoro TTS |
| ✓ | Phase 6 — Evaluation | **Completed (Automated Metrics Harness)** |

**Quantitative Evaluation Metrics (Phase 6):**
| Metric | Measures | Target |
|---|---|---|
| Entity Precision & Recall (%) | Extraction accuracy vs. manual annotation | > 80% Recall |
| Graph Traversal Latency (ms) | System speed as graph scales | < 500ms |
| TTS Real-Time Factor (RTF) | Audio synthesis speed | RTF < 1.0 (faster than real-time) |
| Spearman ρ (Rank Correlation) | Character importance vs. human ranking | ρ > 0.7 |

> 🎤 **SPEAKER NOTES:**
> "Five phases are complete. Our system is fully deployed locally in Zero-GPU mode. We are now entering Phase 6 evaluation. We will measure entity extraction precision and recall against manual gold annotations, benchmark graph traversal latency as the graph scales to thousands of events, and measure TTS generation using RTF — a ratio where less than 1.0 means faster than real-time. We also plan a Spearman correlation study to validate our PageRank character rankings against human judgement."

---
*End of Deck — 10 Slides | Webnovel Architect Review 1*
