# Webnovel Architect — Review 1 | Full Presentation Script (18 Slides)
**PRASAD V. POTLURI SIDDHARTHA INSTITUTE OF TECHNOLOGY · Dept. of CSE (Data Science)**

---

## SLIDE 01 — Title Slide
**[VISUAL: Dark background, glowing teal/violet interconnected graph nodes radiating from centre. University name top. All text white. Subtitle italic.]**

**WEBNOVEL ARCHITECT**
*Neuro-Symbolic Story Intelligence System*

Leveraging LLMs · Dynamic Graph RAG (DyG-RAG) · Real-Time Audio Drama Synthesis

**Guide:** Dr. B. Janakiramaiah | Professor, CSE (DS) & CSE (AIML)
**Team:** [person1] · [person2] · [person3]
Kanuru, Vijayawada – 521212

> 🎤 **SPEAKER NOTES:** "Good morning, respected panel and Dr. Janakiramaiah. We present *Webnovel Architect* — a Neuro-Symbolic Story Intelligence System. We take continuously evolving serialized webnovels and use LLMs with Dynamic Graph RAG to auto-track the narrative, rank character importance, and synthesize real-time casted audio dramas — entirely without a GPU."

---

## SLIDE 02 — Section Transition: Literature Survey
**[VISUAL: Full-screen dark slide. Large bold "01" top-left. Section title centered. Faint data-stream/book icon in background. Teal accent rule below number.]**

```
01
Literature Survey
Research Papers · Comparative Analysis · Research Gap
                                                    5 Marks
```

---

## SLIDE 03 — Base Paper (Paper 1)
**[VISUAL: 4-column card layout. Header per column: Problem / Architecture / Capabilities / Limitations. Each column: 4 short-phrase bullets, matching icon. Dark bg, teal top-border on each card.]**

**PAPER 1 (BASE PAPER)**
*DyG-RAG: Dynamic Graph Retrieval-Augmented Generation with Event-Centric Reasoning*
Sun et al. (2025) · arXiv:2507.13396

| Problem Addressed | Architecture / Model | System Capabilities | Limitations |
|---|---|---|---|
| Temporal reasoning gaps | Dynamic Event Units (DEUs) | Multi-hop temporal reasoning | QA benchmarks only |
| Static event ordering | Time-aware graph traversal | Accurate sequence retrieval | No TTS / audio output |
| No temporal anchors | Event-centric pipeline | Resolves temporal ambiguity | Ignores character centrality |
| No character casting | Time-CoT generation | Dynamic event insertion | CLI/console only |

▶ **Research Gap:** DyG-RAG excels at temporal QA — it doesn't tell stories, track characters, or cast audio drama voices for serialized webnovels.

> 🎤 **SPEAKER NOTES:** "Our base paper is DyG-RAG from 2025. It introduces Dynamic Event Units that tie semantic meaning to explicit time anchors, eliminating temporal hallucinations in LLMs. It's powerful for QA — but it has no mechanism for character casting or audio output, which is exactly the gap we fill."

---

## SLIDE 04 — Additional Papers 2 & 3
**[VISUAL: Two side-by-side paper cards. Each card: paper number badge, title, author, technique bullets, ⚠ limitation tags, and 'Our Contribution' line in accent color at the bottom.]**

**02** *From Local to Global: A Graph RAG Approach to Query-Focused Summarization*
Edge et al. (Microsoft Research, 2024) · arXiv

Technique: Static Entity Knowledge Graph + Louvain Community Detection
⚠ Static-only — high index rebuild cost per update
⚠ No character importance logic, no TTS pipeline
**Our Contribution:** Real-time evolving DyG-RAG — no full re-build needed per chapter.

---

**03** *STAGE: Knowledge Graph Construction and Narrative Understanding*
Stanford University (2024) · arXiv

Technique: GraphRAG-style construction for movie screenplays
⚠ Scene-level snapshots only — not continuous
⚠ No temporal decay or character ranking
**Our Contribution:** Continuous serialized character graduation via Temporal Decay PageRank.

> 🎤 **SPEAKER NOTES:** "Microsoft's GraphRAG and Stanford's STAGE both use static graphs or scene-level snapshots. They're too rigid and expensive to rebuild for an ongoing webnovel. Our system extends both by supporting continuous ingestion and applying PageRank to rank character importance dynamically."

---

## SLIDE 05 — Comparative Analysis Table
**[VISUAL: Full-width high-contrast comparison table. 'OUR PROJECT' row highlighted with teal/violet accent. Column headers bold. Dark background, clear cell borders. Use ✓/✗ icons for quick scan-ability.]**

**COMPARATIVE ANALYSIS OF RELATED WORKS**

| System | Graph Type | Temporal | Character Casting | Live Ingestion | Zero-GPU | Wiki Output | UI/Dashboard | Evaluation |
|---|---|---|---|---|---|---|---|---|
| Standard RAG | None | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | QA Accuracy |
| Static GraphRAG | Static Entity | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | Comprehensiveness |
| DyG-RAG (2025) | Dynamic Event | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | Temporal QA |
| ★ **OUR PROJECT** | **Dynamic + PageRank** | **✓** | **✓ Voice Cast** | **✓ Per Chapter** | **✓ Switchboard** | **✓ Markdown** | **✓ Streamlit** | **Recall / RTF / ρ** |

**Our Contributions at a Glance:**

| # | Contribution | Innovation |
|---|---|---|
| 1 | **Live Chapter Ingestion** | Graph updates incrementally per chapter — no full re-index |
| 2 | **Temporal Decay PageRank** | Ranks characters by narrative importance over time |
| 3 | **Automated Voice Casting** | Main Cast auto-assigned high-quality Kokoro ONNX voices |
| 4 | **Zero-GPU Switchboard** | Decoupled adapter layer — runs entirely on laptop/API |
| 5 | **Character Wiki Generator** | Auto-produces Markdown wikis from the graph state |
| 6 | **Interactive Streamlit Dashboard** | Full ingestion, wiki-view, and audio synthesis in one UI |

> 🎤 **SPEAKER NOTES:** "This table shows the clear progression. Standard RAG has no graph. GraphRAG has a static graph. DyG-RAG adds temporal understanding. Our system is the only one that combines all features — live chapter ingestion, character importance scoring, automated TTS voice casting, a zero-GPU architecture, auto-generated character wikis, and an interactive dashboard. We didn't just fill one gap — we filled six."


---

## SLIDE 06 — Research Gap
**[VISUAL: Three tall vertical cards side-by-side. Each card: bold red ✗ problem phrase (≤6 words) at top, bold green ✓ solution at bottom. Heavy impact typography, dark bg.]**

**RESEARCH GAP & OUR CONTRIBUTION**

| ✗ Problem | ✓ Our Solution |
|---|---|
| Static graphs freeze after indexing | Real-time graph updates per new chapter |
| RAG answers questions, not stories | PageRank + Temporal Decay → auto voice cast |
| Requires expensive GPU hardware | Zero-GPU Switchboard — runs on a laptop |

> 🎤 **SPEAKER NOTES:** "Three precise gaps. One: existing graphs require a full expensive rebuild when a new chapter drops — ours updates live. Two: a raw graph doesn't know who the 'Main Character' is — we apply PageRank with decay to determine narrative importance and assign TTS voices. Three: we engineered a Zero-GPU abstraction so the whole system runs on any student laptop for free."

---

## SLIDE 07 — Section Transition: Base Paper Explanation
**[VISUAL: Full-screen dark slide. Large bold "02". Blueprint/architectural schematic ghost image in background. Teal accent rule.]**

```
02
Base Paper Explanation
Architecture · Algorithms · Limitations
                                        5 Marks
```

---

## SLIDE 08 — DyG-RAG Architecture & Components
**[VISUAL: LEFT — horizontal 5-chevron pipeline (gradient teal→violet). RIGHT — 3 card columns (DEU / Event Graph / Timeline Retrieval), 4 bullet phrases each, max 4 words per bullet.]**

**BASE PAPER: DYG-RAG WORKFLOW**

**Pipeline:**
```
User Query  ➔  DEU Extraction  ➔  Event Graph Build  ➔  Timeline Traversal  ➔  Time-CoT Answer
```

**3 Core Components:**

| Dynamic Event Units (DEU) | Event Graph Construction | Timeline Retrieval Pipeline |
|---|---|---|
| Semantic + temporal encoding | Links entities over time | Time-aware traversal |
| Precise time anchors | Multi-hop traversal | Sequential extraction |
| Eliminates ambiguity | Topological structure | Time-CoT prompting |
| Foundation for graph | Supports reasoning | Chronological output |

> 🎤 **SPEAKER NOTES:** "The DEU is DyG-RAG's core innovation — it encodes *what* happened and *when* into one unit. These units link into an event graph. When a query arrives, Time-Chain-of-Thought traverses the graph chronologically for a grounded, hallucination-free answer."

---

## SLIDE 09 — Base Paper: Algorithms + Limitations vs Improvements

**[VISUAL: Split slide. LEFT — 3 numbered dark algorithm cards. RIGHT — 2-column table (✗ Limitation / ✓ Our Improvement). 4 rows. Add planned metrics at bottom as a highlighted callout box.]**

**ALGORITHMS USED**

| # | Algorithm | Method |
|---|---|---|
| 1 | Dynamic Event Extraction | LLM entity-event coupling with temporal tagging |
| 2 | Time-Aware Graph Traversal | Topological sequence-path mapping |
| 3 | Time Chain-of-Thought (Time-CoT) | Prompt strategy for grounded generation |

**LIMITATIONS → OUR IMPROVEMENTS**

| ✗ DyG-RAG (Base) | ✓ Webnovel Architect |
|---|---|
| QA output only | Audio Dramas + Character Wikis |
| Static long-document evaluation | Live, continuous serialized chapters |
| No character importance scoring | Temporal Decay PageRank → "Main Cast" |
| CLI/code only | Interactive Streamlit SPA Dashboard |

> 📊 **Planned Evaluation Metrics:** Entity Recall (%) · Graph Latency (ms) · TTS RTF · Spearman ρ

> 🎤 **SPEAKER NOTES:** "We extend all four limitations. Most critically, instead of just answering questions, our system uses the graph to calculate character centrality — and outputs a full audio drama through a polished Streamlit UI."

---

## ════════════════════════════════════════
## ★ MIDPOINT — SLIDE 09 OF 18 ★
## ════════════════════════════════════════

---

## SLIDE 10 — Section Transition: Technical Architecture
**[VISUAL: Full-screen dark slide. Large bold "03". 3D isometric stacked-layer ghost graphic in background. Violet accent rule.]**

```
03
Technical Architecture
System Design · Pipelines · Modules
                                    5 Marks
```

---

## SLIDE 11 — System Architecture: 5-Layer Design
**[VISUAL: 5 stacked horizontal bars. Color-coded per layer (see table). Small icon left, bold layer name, tech stack right-aligned. Downward arrows between layers. Diagram IS the content — self-sufficient.]**

**PROPOSED SYSTEM ARCHITECTURE — 5-LAYER DESIGN**

| Layer | Name | Technology Stack | 🎨 Color |
|---|---|---|---|
| L1 | Presentation | Streamlit SPA · 3 UI Tabs (Ingest / Wiki / Audio) | Teal |
| L2 | Switchboard | Zero-GPU Router · Adapter Pattern | Blue |
| **L3** | **Ingestion — "The Eye"** | **LiteLLM (Gemini Flash) + spaCy NER Fallback** | **Indigo** |
| **L4** | **Story Runtime — "The Brain"** | **NetworkX / KuzuDB · JSON Graph Persistence** | **Violet** |
| **L5** | **Graduation — "The Director"** | **PageRank + Temporal Decay · Kokoro ONNX / Edge-TTS** | **Deep Purple** |

▼ *Flow: Raw Text → L3 → L4 → L5 → Wiki + Audio → L1 (Streamlit)*

> 🎤 **SPEAKER NOTES:** "Five decoupled layers. The Switchboard (L2) is the key to going Zero-GPU — it dynamically routes requests to APIs or local fallbacks. The Ingestion layer (L3) extracts events using Gemini Flash. The Runtime (L4) persists the story in a NetworkX graph. The Graduation layer (L5) runs PageRank and generates audio."

---

## SLIDE 12 — Pipeline Workflow: 4 Subsystems
**[VISUAL: 4 circular colored hubs connected by arrows. Hub colors MATCH slide 11 layers exactly: 01=Indigo · 02=Violet · 03=Deep Purple · 04=Teal. Under each hub: bold title + Role + Tool + Output (2-3 words max). Bottom: sequential arrow.]**

**PIPELINE WORKFLOW — DATA MOVING THROUGH THE ARCHITECTURE**
*(Hub colors directly match Layers 3–5 from the previous slide)*

```
  [Indigo]           [Violet]          [Deep-Purple]       [Teal]
01 INGESTION  →  02 GRAPH RUNTIME  →  03 GRADUATION  →  04 VOICE SYNTHESIS
 "The Eye"         "The Brain"         "The Director"      "The Voice"
 LiteLLM+spaCy     NetworkX            PageRank+Decay      Kokoro ONNX
 ↓ JSON Events     ↓ Network Graph     ↓ Main Cast>0.15    ↓ Audio Drama MP3
```

▶ Sequential Execution: Ingestion → Graph → Graduation → Audio/Wiki

> 🎤 **SPEAKER NOTES:** "The same colors from the last slide map directly to these four hubs. A raw chapter enters the Eye (Indigo). JSON events go into the Brain (Violet). The Director (Deep Purple) calculates centrality — if a character's PageRank exceeds 0.15, they graduate to Main Cast. The Voice (Teal) assigns a dedicated Kokoro TTS voice and renders the final audio."

---

## SLIDE 13 — Section Transition: Dataset Strategy
**[VISUAL: Full-screen dark slide. Large bold "04". Abstract data-flow visual — 0s and 1s fading into a glowing network graph. Violet accent rule.]**

```
04
Dataset Strategy
Corpora · Graphs · Preprocessing · Ethics
                                         5 Marks
```

---

## SLIDE 14 — Dataset Sources
**[VISUAL: 3 wide horizontal data-source rows. Each: number badge (01/02/03), dataset name bold, type tag pill, source, 1-line use description. Compact, no padding wasted.]**

**DATASET STRATEGY — CORPUS & RUNTIME DATA**

📊 *Data sources supporting extraction, graph memory, and audio casting*

| # | Dataset | Type | Source | Use |
|---|---|---|---|---|
| 01 | Serialized Webnovel Corpus | Text / NLP | Public Domain / Custom | Raw pipeline input & long-context graph testing |
| 02 | Generated Event Graph | JSON / Graph | System Runtime (auto-generated) | Persists canonical character-event relationships |
| 03 | Voice Embeddings Registry | Acoustic / JSON | Kokoro TTS Metadata | Deterministic voice-actor assignment per character |

**Ethics & Bias Considerations:**
- Open-license or personally owned text only
- LLM extraction is bounded — no unprompted hallucinated content
- Voice assignment is deterministic, not biased by demographic inference

> 🎤 **SPEAKER NOTES:** "Our data strategy has three pillars: raw text as input, auto-generated JSON event graphs as memory, and acoustic voice embeddings for casting. Crucially, all processing is bounded — the LLM only extracts, never freely generates story content."

---

## SLIDE 15 — Preprocessing Pipeline
**[VISUAL: 5-step horizontal pipeline (numbered boxes, downward chevron arrows). Box content: step number (large), action verb (bold), 1-line description. Use the layer colors from slide 11 as gradient across the 5 steps.]**

**5-STEP PREPROCESSING PIPELINE**

```
  1               2               3               4               5
HTML Clean   →  Sentence    →  Dual Extract  →  Graph Insert  →  Centrality
             Chunking       (LLM + NER)       (NetworkX)        Update
Remove tags  Split into    LiteLLM primary   Commit events    Recalculate
& formatting  convo/desc   spaCy fallback    to "Brain"       PageRank
              segments
```

**Data Sources at Each Stage:**

| Source | Role | Output |
|---|---|---|
| LiteLLM / Gemini Flash | Event extraction | Structured character/event JSON |
| NetworkX Runtime | Persistent storage | Temporal event graph |
| Kokoro ONNX | Audio output | < 1s per spoken line (RTF < 1.0) |

> 🎤 **SPEAKER NOTES:** "Every chapter goes through this 5-step pipeline before touching the graph. We clean HTML, chunk into conversational and descriptive segments, run a dual-extraction with Gemini as primary and spaCy as a deterministic fallback, commit entities to the NetworkX Brain, then trigger a global PageRank update."

---

## SLIDE 16 — Section Transition: Methodology & Tools
**[VISUAL: Full-screen dark slide. Large bold "05". Abstract isometric server rack or overlapping tech-stack floating icons. Deep-purple accent rule.]**

```
05
Methodology & Tools
Tech Stack · Implementation Strategy · Deployment
                                                  10 Marks
```

---

## SLIDE 17 — Technology Stack
**[VISUAL: 2×3 grid of tech cards. Each card: logo/icon placeholder (top), bold tool name, role sub-label, 1-line justification. Dark card, subtle teal border. Matches example PDF grid format.]**

**TECHNOLOGY STACK — TOOL SELECTION & JUSTIFICATION**

| Tool | Role | Why? |
|---|---|---|
| **Python 3.9+** | Core Language | NLP ecosystem · modular clean architecture |
| **Streamlit** | Frontend SPA | Rapid dashboard · Python-native UI |
| **LiteLLM / Gemini Flash** | LLM Engine | Zero-GPU extraction · free-tier API |
| **NetworkX & KuzuDB** | Graph Database | Lightweight dev → scalable production |
| **Kokoro ONNX & Edge-TTS** | Audio Synthesis | Offline CPU TTS + cloud API fallback |
| **spaCy** | NER Fallback | Deterministic · local · zero API cost |

> 💡 **Why this combination?** LLMs extract unstructured text; graphs reason over it — no GPU training needed, no hallucination risk over long narratives.

> 🎤 **SPEAKER NOTES:** "Every tool was chosen for modularity and Zero-GPU compatibility. LiteLLM with Gemini Flash achieves high-accuracy event extraction without local hardware. Kokoro ONNX delivers studio-quality TTS offline on a CPU. If any online service fails, the Switchboard silently reroutes to a local fallback — making the system highly resilient."

---

## SLIDE 18 — Implementation Status & Evaluation Plan
**[VISUAL: Split slide. LEFT — implementation checklist timeline (✓ green / ○ grey). RIGHT — evaluation strategy with 4 metric cards, each showing metric name + target value. Use architecture colors for the metric cards.]**

**IMPLEMENTATION STATUS & EVALUATION STRATEGY**

**Implementation Phases:**

| Status | Phase | Deliverable |
|---|---|---|
| ✓ | Phase 1 — Environment & NLP | spaCy pipelines + virtual env |
| ✓ | Phase 2 — Dual Extraction & Switchboard | LiteLLM + adapter pattern |
| ✓ | Phase 3 — Graph Runtime | NetworkX with JSON persistence |
| ✓ | Phase 4 — Graduation System | PageRank + Temporal Decay |
| ✓ | Phase 5 — Streamlit UI & Audio | Full dashboard + Kokoro TTS |
| ○ | **Phase 6 — Evaluation** | **In Progress → Review 2 Target** |

**Quantitative Evaluation Metrics (Phase 6):**

| Metric | Measures | Target |
|---|---|---|
| Entity Precision & Recall (%) | Extraction accuracy vs. manual annotation | > 80% Recall |
| Graph Traversal Latency (ms) | System speed as graph scales | < 500 ms |
| TTS Real-Time Factor (RTF) | Audio synthesis speed | RTF < 1.0 |
| Spearman ρ (Rank Correlation) | Character ranking vs. human judgement | ρ > 0.7 |

**Deployment Targets:**

| Mode | LLM | Graph | Audio |
|---|---|---|---|
| Laptop (Current) | Gemini Flash API | NetworkX / JSON | Kokoro ONNX (CPU) |
| Research Lab (Target) | Local Llama-3 | KuzuDB | StyleTTS2 (GPU) |

> 🎤 **SPEAKER NOTES:** "Five of six phases are complete. We are fully deployed in Zero-GPU mode. For Phase 6, we will measure entity extraction recall against manual gold annotations, benchmark graph traversal latency as the graph scales to thousands of events, and compute TTS RTF — a ratio where below 1.0 means faster than real-time. We will also validate our PageRank rankings against human judgement using Spearman correlation."

---

*End of Deck — 18 Slides | Webnovel Architect · Review 1*
*★ Midpoint marked at Slide 09 ★*
