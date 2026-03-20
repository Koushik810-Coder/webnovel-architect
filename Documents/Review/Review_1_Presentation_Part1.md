PRASAD V. POTLURI SIDDHARTHA INSTITUTE OF TECHNOLOGY  ·  Dept. of CSE (Data Science)
Webnovel Architect — Neuro-Symbolic Story Intelligence System
Leveraging LLMs  ·  Dynamic Graph RAG (DyG-RAG)  ·  Real-Time Audio Drama Synthesis
Guide : Dr.B.Janakiramaiah
Professor of CSE(DS) and CSE(AIML)
person1
person2
person3
Kanuru, Vijayawada – 521212  |  Department of Computer Science & Engineering (Data Science)

[PROMPT: Sleek title slide. Futuristic background of glowing, interconnected graph nodes. Bold sans-serif main title centered. University name at top. Dark background with teal/violet accent glow.]

================================================================================
01
Literature
Survey
Research Papers · Comparative Analysis · Research Gap
5 Marks

[PROMPT: Transition slide. Large bold '01'. Subtitle 'Literature Survey'. Background: faint data-stream pattern with a subtle magnifying glass icon. Dark theme.]
================================================================================

PAPER 1 (BASE PAPER) 
DyG-RAG: Dynamic Graph Retrieval-Augmented Generation with Event-Centric Reasoning
Sun et al. (2025)  ·  arXiv:2507.13396

[PROMPT: 4-column info card slide. Each column has a bold header (Problem / Architecture / Capabilities / Limitations) and 3-4 short phrase bullets beneath. Use matching icon per column: ⚠️ 🔧 ✓ ✗. Keep bullet text ≤ 4 words each.]

Problem Addressed
• Temporal reasoning gaps
• Static event ordering
• No temporal anchors
• No character casting

Architecture / Model
• Dynamic Event Units (DEUs)
• Time-aware graph traversal
• Event-centric pipeline
• Time-CoT generation

System Capabilities
• Multi-hop temporal reasoning
• Sequence retrieval accuracy
• Resolves temporal ambiguity
• Dynamic event insertion

Limitations
• QA benchmarks only
• No TTS / audio output
• Ignores character centrality
• Console-only interface

▶ Research Gap: DyG-RAG excels at QA over temporal events — but it doesn't tell stories, track characters, or cast audio drama voices for serialized webnovels.

ADDITIONAL RESEARCH PAPERS — 2 & 3

02 From Local to Global: A Graph RAG Approach to Query-Focused Summarization
Edge et al. (Microsoft Research, 2024) - arXiv
Technique: Static Entity Knowledge Graph + Community Detection (Louvain).
⚠ Static-only, high index cost, no character casting
Our contribution: Real-time evolving DyG-RAG — no full re-build needed per chapter.

03 STAGE: Knowledge Graph Construction and Narrative Understanding
Stanford University (2024) - arXiv
Technique: GraphRAG-style construction for movie screenplays.
⚠ Scene-level snapshots only, no temporal decay
Our contribution: Continuous character graduation via Temporal Decay PageRank.

[PROMPT: Slide split into top (3 paper summary cards with icons) and bottom (comparison table). Highlight the 'OUR PROJECT' row with accent color (teal/violet). Columns: Paper | LLM | Graph Type | Temporal | Character Casting | Evaluation.]

COMPARATIVE ANALYSIS OF RELATED WORKS
Paper               | LLM Used | Graph Type    | Temporal | Character Casting | Evaluation
Standard RAG        | Various  | None          | ✗        | ✗                 | QA Metrics
Static GraphRAG     | GPT-4    | Static Entity | ✗        | ✗                 | Comprehensiveness
DyG-RAG (2025)      | Llama-3  | Dynamic Event | ✓        | ✗                 | Temporal QA
OUR PROJECT ★       | Gemini   | DyG-RAG+      | ✓        | ✓ Voice Cast      | [See Eval Plan]

[PROMPT: Full-slide "Research Gap" layout. Three bold side-by-side cards. Top of each card: large red ✗. Bottom: large green ✓. Short punchy phrases only — 6 words max per line. Impact typography.]

RESEARCH GAP & OUR CONTRIBUTION

✗ Current RAG systems just answer questions.
→ ✓ Ours tells stories and casts voices.

✗ Existing graphs are built once and frozen.
→ ✓ Ours evolves live, chapter by chapter.

✗ Intelligence requires expensive GPU hardware.
→ ✓ Ours runs Zero-GPU on a student laptop.

================================================================================
02
Base Paper
Explanation
Architecture · Algorithms · Limitations
5 Marks

[PROMPT: Transition slide for '02 Base Paper Explanation'. Dark blueprint / architectural schematic image. Light-on-dark text. Bold section number.]
================================================================================

BASE PAPER: SYSTEM ARCHITECTURE & DYG-RAG FLOW

[PROMPT: Horizontal arrow-flow diagram. 5 stages connected by chevrons (▶). Each stage: title + 2-line description. Color: dark bg, gradient teal→violet per stage. Stage icons: 🔍 🔗 🧠 📅 💬]

Base Paper Pipeline — DyG-RAG Workflow

User Query
Natural language
temporal question
▶
DEU Extraction
Dynamic Event Units
(semantic + temporal)
▶
Event Graph Build
Link entities close
in time & topic
▶
Timeline Traversal
Topological
time-aware path
▶
Time-CoT Answer
Grounded, ordered
event response

3 Specialized Components — Separation of Concerns

[PROMPT: 3 column cards, each with a bold title, colored border (teal/blue/violet), and 4 short bullet phrases. Max 4 words per bullet.]

Dynamic Event Units (DEU)
• Semantic + temporal encoding
• Eliminates ambiguity
• Precise time anchors
• Foundation for graph

Event Graph Construction
• Links entities over time
• Multi-hop traversal
• Topological structure
• Supports reasoning

Timeline Retrieval Pipeline
• Time-aware traversal
• Sequential extraction
• Time-CoT prompting
• Chronological output

BASE PAPER: ALGORITHMS, METRICS & LIMITATIONS vs OUR IMPROVEMENTS

[PROMPT: Two-panel slide. Left: numbered algorithm steps (1-3) on dark cards. Right: limitations vs improvements table with ✗ and ✓ rows. Matching column colors.]

ALGORITHMS USED

1
Dynamic Event Extraction
LLM entity-event coupling with temporal tagging

2
Time-Aware Graph Traversal
Topological sequence-path mapping

3
Time Chain-of-Thought (Time-CoT)
Prompt strategy for grounded generation

LIMITATIONS → OUR IMPROVEMENTS

✗ QA-only output
✓ Full Audio Drama + Character Wiki

✗ Static long-document evaluation
✓ Live, continuous webnovel chapters

✗ No character importance scoring
✓ Temporal Decay PageRank → "Main Cast"

✗ No deployment interface
✓ Interactive Streamlit Dashboard

EVALUATION METRICS HARNESS (Phase 6 Completed)
• Entity Extraction Recall (%)
• Graph Traversal Latency (ms)
• PageRank Score Accuracy vs. human annotation
• TTS Generation Speed — Real Time Factor (RTF)
• Character Importance Rank Correlation (Spearman ρ)
