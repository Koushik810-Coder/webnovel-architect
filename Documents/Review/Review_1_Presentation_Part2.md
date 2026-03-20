================================================================================
03
Technical
Architecture
System Design · Pipelines · Modules
5 Marks

[PROMPT: Transition slide for '03 Technical Architecture'. 3D isometric stacked-layer graphic. Bold '03'. Dark theme with teal/violet accent.]
================================================================================

PROPOSED SYSTEM ARCHITECTURE — 5-LAYER DESIGN

[PROMPT: Generate a clean 5-layer stacked-block diagram. Each block is a horizontal bar with a small icon on the left, the layer name (bold), and the tech stack listed to the right. Use distinct background shades per layer to make them visually separable: Layer 1 (top)=teal, Layer 2=blue, Layer 3=indigo, Layer 4=violet, Layer 5=deep purple. Show downward arrows between layers. This diagram should be self-sufficient — no text list needed below it.]

Layer 1 — PRESENTATION        │ Streamlit SPA · 3 UI Tabs (Ingest / Wiki / Audio)
Layer 2 — SWITCHBOARD         │ The Switchboard Pattern · Zero-GPU Modularity
Layer 3 — INGESTION "Eye"     │ LiteLLM (Gemini Flash) · spaCy NER Fallback
Layer 4 — STORY RUNTIME "Brain"│ NetworkX / KuzuDB · JSON Graph Persistence
Layer 5 — GRADUATION "Director"│ PageRank + Temporal Decay · Kokoro ONNX / Edge-TTS

▼ Request Flow: Raw Text → Eye → Brain → Director → Wiki + Audio → Streamlit UI

NOTE FOR COLOR CODING: Layer colors carry over to the 4-Phase Pipeline below.
Use same color per matching phase (Layer 3=indigo → Phase 01 Ingestion; Layer 4=violet → Phase 02 Graph; etc.)

[PROMPT: 4-node circular-hub pipeline diagram. Each hub matches the layer color from above (indigo / violet / deep-purple / teal). Hub title is bold. Below each: Role • Tool • Output. Bottom: sequential execution arrow. This directly maps to Layers 3-5 of the architecture above.]

PIPELINE PHASE WORKFLOW — HOW DATA MOVES THROUGH THE ARCHITECTURE
(Each phase corresponds to one of the colored layers above)

USER INPUT: Serialized Webnovel Chapter / Narrative Text
▼
01 INGESTION ENGINE [Layer 3 — Indigo] "The Eye"
Role: Identify characters, locations & events from raw text
Tool: LiteLLM (Gemini Flash) + spaCy NER
Output: Structured JSON events

02 GRAPH RUNTIME [Layer 4 — Violet] "The Brain"
Role: Persist relationships, link event chains
Tool: NetworkX graph + JSON store
Output: (Character)→[PARTICIPATED_IN]→(Event) graph

03 GRADUATION SYSTEM [Layer 5 — Deep Purple] "The Director"
Role: Rank character importance over time
Tool: PageRank + Temporal Decay weights
Output: Main Cast list (threshold > 0.15)

04 VOICE SYNTHESIS [Layer 5 Output — Teal] "The Voice"
Role: Cast voices based on character rank
Tool: Kokoro ONNX (Main Cast) / Edge-TTS (Background)
Output: Audio Drama MP3s + Markdown Character Wiki

▶ Sequential: Ingestion → Graph → Graduation → Audio/Wiki

================================================================================
04
Dataset
Strategy
Corpora · Graphs · Preprocessing · Ethics
5 Marks

[PROMPT: Transition slide for '04 Dataset Strategy'. Abstract data-flow visualization — 0s and 1s fading into a glowing network graph. Same teal/violet palette.]
================================================================================

DATASET STRATEGY — CORPUS & RUNTIME DATA

[PROMPT: 3 wide horizontal data card rows. Each row: number badge (01/02/03), dataset name, type tag (Text/JSON/Acoustic), source, and 1-line use description. Keep extremely concise.]

📊 Data sources supporting extraction, graph memory, and audio casting

01 Serialized Webnovel Corpus   │ Text/NLP   │ Custom / Project Gutenberg
   Use: Multi-chapter ingestion to test long-context graph evolution

02 Generated Event Graph        │ JSON/Graph │ System Runtime (auto-generated)
   Use: Persists canonical character-event relationships per chapter

03 Voice Embeddings Registry    │ Acoustic   │ Kokoro TTS Metadata
   Use: Maps "Graduated" Main Cast characters to deterministic voice IDs

DATA SOURCES & PREPROCESSING PIPELINE

[PROMPT: 3-column data source cards above. Below: 5-step horizontal or vertical pipeline. Each step is a numbered box with action verb as heading and 1-line description. Arrows between steps. Use the same layer color coding as the architecture slide.]

LiteLLM / Gemini (Extraction)         │ NetworkX (Runtime Memory)        │ Kokoro TTS (Audio)
API-based entity/event extraction      │ Persists graph with PageRank      │ Offline ONNX synthesis
JSON-structured per chapter            │ Temporal Decay scoring            │ < 1s per character line

PREPROCESSING PIPELINE (5 STEPS)

1 Chapter Ingestion   → Text cleaned, HTML stripped
▶
2 Sentence Chunking   → Split into conversational / descriptive segments
▶
3 Dual Extraction     → LiteLLM primary · spaCy NER fallback
▶
4 Graph Insertion     → Events committed to NetworkX "Brain"
▶
5 Centrality Update   → PageRank recalculated · Wiki metrics updated

ETHICAL & BIAS CONSIDERATIONS
• Content restricted to open-license or owned narrative text
• LLM extraction is bounded — no unprompted hallucinated content
• Voice assignment is deterministic, not biased by demographic inference

================================================================================
05
Methodology
& Tools
Tech Stack · Implementation Strategy · Deployment
10 Marks

[PROMPT: Transition slide for '05 Methodology & Tools'. Abstract isometric server rack or overlapping tech-stack floating icons. Bold '05'.]
================================================================================

TECHNOLOGY STACK — TOOL SELECTION & JUSTIFICATION

[PROMPT: 2×3 grid of tech cards. Each card: logo/icon placeholder, bold tool name, role label, 2-line justification. Dark card on dark background with subtle border. Match grid format to example PDF.]

Python 3.9+               │ Core Language   │ NLP ecosystem, clean modular syntax
Streamlit                 │ Frontend UI      │ Rapid dashboard prototyping, Python-native
LiteLLM / Gemini Flash    │ Extraction LLM   │ High-accuracy event parsing, Zero-GPU enabler
NetworkX & KuzuDB         │ Graph Database   │ Lightweight dev → production scalability path
Kokoro ONNX & Edge-TTS    │ Audio Synthesis  │ Offline high-quality TTS + cloud fallback
spaCy                     │ Fallback NER     │ Deterministic local entity recognition

WHY THIS COMBINATION?
Traditional pipelines require GPUs for model training. By offloading intelligence to APIs (Gemini) and moving reasoning to a deterministic graph (NetworkX), we avoid GPU costs while eliminating hallucinations across long narratives.

[PROMPT: Two-column slide. LEFT: Implementation Phases as a vertical timeline with checkmarks/circles. RIGHT: Deployment Plan as two stacked cards (Local / Production). Use matching colors from the architecture diagram.]

IMPLEMENTATION STRATEGY & DEPLOYMENT PLAN

IMPLEMENTATION PHASES
✓ Phase 1 — Environment & NLP Setup
  Virtual env configured. spaCy pipelines running.
✓ Phase 2 — Dual Extraction & Switchboard
  LiteLLM wrappers + adapter pattern implemented.
✓ Phase 3 — Graph Runtime & Memory
  NetworkX event graph with JSON persistence.
✓ Phase 4 — Graduation System
  PageRank + Temporal Decay threshold logic.
✓ Phase 5 — Streamlit Dashboard & Audio
  Full interactive UI. Kokoro ONNX integrated.
✓ Phase 6 — Evaluation (Completed)
  Benchmarked on: Entity F1, Latency (ms), RTF, Spearman ρ

DEPLOYMENT PLAN

Local / Laptop Mode (Current)
├── Frontend → Streamlit UI (Port 8501)
├── Intelligence → Gemini Flash API (free tier)
└── Audio → Kokoro ONNX (CPU inference)

Research Lab / Scalability Mode (Target)
├── LLM → Local Llama-3 via Switchboard adapter
├── Graph DB → KuzuDB (production-grade)
└── Audio → Kokoro ONNX + StyleTTS2 (GPU)

Error Handling & Reliability
• Switchboard pattern: if Gemini fails → spaCy NER activates automatically
• Graph JSON persistence: context preserved across system restarts
• Graceful TTS fallback: Kokoro → Edge-TTS if ONNX model unavailable
