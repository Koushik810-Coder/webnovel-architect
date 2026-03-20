# Project Vision and Status

## Problem Definition & Project Vision


### 1. Background

Modern webnovels and serialized fiction contain long, evolving narratives with large character casts, shifting relationships, and complex event timelines. Existing automated summarization or character-tracking systems rely heavily on linear pipelines or purely neural approaches that often introduce **hallucinated causality**, lose narrative consistency, or fail to maintain long-term story memory.

Writers and readers lack tooling that can:

- Track canonical character status over time
    
- Maintain consistent story knowledge
    
- Automatically generate structured “story intelligence” artifacts (wiki, cast ranking, voice assignment)
    

---

### 2. Problem Statement

Current narrative analysis systems are insufficient for long-form serialized fiction because they:

- Do not maintain persistent event relationships across chapters
    
- Infer incorrect causal links (“hallucinated causality”)
    
- Lose character salience over long timelines
    
- Depend on stateless or count-based heuristics rather than structured reasoning
    

**Therefore:**

> There is a need for a system that can continuously ingest narrative text, build a persistent structured representation of events and entities, reason over narrative importance, and generate consistent canonical outputs.

---

### 3. Proposed Solution

**Webnovel Architect** is a **Neuro-Symbolic Story Intelligence Engine** that:

- Ingests raw narrative text
    
- Extracts entities and events
    
- Constructs a **Dynamic Event Graph (DyG-RAG architecture)**
    
- Tracks character importance over time
    
- Generates canonical knowledge artifacts (Wiki, Character Status, Audio Voice Assignment via Dual Kokoro/EdgeTTS)
    

The system combines:

- Neural extraction (LLM / NLP)
    
- Symbolic reasoning (Graph representation)
    
- Retrieval-Augmented Narrative Context
    

---

### 4. Core Objectives

#### Primary Objectives

1. Build a persistent **event-centric story representation**
    
2. Reduce hallucinated causal inference
    
3. Automatically identify main characters
    
4. Maintain canonical knowledge consistency
    

#### Secondary Objectives

- Generate auto-updated wiki pages
    
- Enable character voice synthesis
    
- Support multi-hardware deployment tiers
    

---

### 5. Research Questions

1. Does an event-centric graph representation improve narrative consistency compared to linear pipelines?
    
2. Can graph centrality reliably determine narrative importance of characters?
    
3. Does DyG-RAG reduce hallucinated causality during story reasoning?
    
4. Can persistent symbolic memory improve long-context narrative tracking?
    

---

### 6. Scope Definition

#### Included

- Text ingestion and processing
    
- Entity recognition and linking
    
- Event graph construction
    
- Character salience tracking
    
- Wiki generation
    
- Extended Audio Synthesis Layer (Full Audiobook Synthesis with Script Caching)
    

#### Excluded (Current Phase)

- Full narrative understanding (themes, emotions)
    
- Human-level semantic interpretation
    
- Production-scale deployment
    

---

### 7. Expected Deliverables

- Working Story Intelligence Engine
    
- Dynamic Event Graph Runtime
    
- Auto-generated Canon Wiki
    
- Graduation/Ranking System for characters
    
- Interactive Streamlit Dashboard UI
    
- Experimental evaluation results
    

---

### 8. Stakeholders

- Final Year Evaluation Committee
    
- Research Mentor
    
- Potential Publication Reviewers
    
- Future Product Users (Writers / Readers)
    

---

### 9. Success Criteria

The project is considered successful if:

- Event graph persists narrative relationships correctly
    
- Character importance ranking aligns with ground truth
    
- Canon contradictions are minimized
    
- System demonstrates measurable improvement over baseline pipeline
    



---

## Current State Report (Implementation Status & Gap Analysis)


## 1. Executive Summary

The **Webnovel Architect** project has successfully transitioned from a heuristic prototype to a **graph-based neuro-symbolic architecture**. The system now implements:

✅ **Dynamic Event Graph (DyG-RAG)** using NetworkX with JSON persistence  
✅ **PageRank-based character graduation** for intelligent voice assignment  
✅ **Modular adapter pattern** for LLM, TTS, and Graph components  
✅ **Event extraction and relationship modeling** via LLM analysis  
✅ **Dual TTS system** (Kokoro local + EdgeTTS fallback)

**Current Status:** The core architecture is **functionally complete** and verified. The system can process narrative text, build a persistent story graph, calculate character importance using PageRank, and generate audio with appropriate voice assignment.

**Next Phase:** Optimization, advanced features (temporal weighting, alias resolution), and research validation.

---

## 2. Phase Status Overview

| Phase | Description | Status |
|-------|-------------|--------|
| **Phase 1** | Heuristic Prototype Development | ✅ **Completed** |
| **Phase 2** | Story Intelligence Verification | ✅ **Completed** |
| **Phase 3** | Neuro-Symbolic Graph Migration | ✅ **Completed** (Feb 2026) |
| **Phase 4** | Voice Management System | ✅ **Completed** (VoiceRegistry & Persistence) |
| **Phase 5** | Evaluation Harness & Metrics | ✅ **Completed** (Mar 2026) |
| **Phase 6** | Story Q&A (Time-CoT RAG) | ✅ **Completed** (DyG-RAG DEUs) |
| **Phase 7** | Synchronized Visualizer & Wiki Memory | ✅ **Completed** |
| **Phase 8** | Advanced Optimization (Alias/Kuzu) | 🟡 **Partially Implemented** (Alias Resolution integrated) |

---

## 3. Subsystem Implementation Status

### 3.1 Ingestion Engine ("The Eye")

**Status:** ✅ **Implemented with LLM and spaCy-based Extraction**

**Current Implementation**
- **Module:** [`core/ingestion.py`](file:///c:/Projects/webnovel-architect/core/ingestion.py)
- **Method:** LiteLLM-based structured extraction (Gemini Flash by default) AND a fallback spaCy Named Entity Recognition (NER) pipeline.
- **Capabilities:**
  - Dialogue extraction with speaker identification
  - Emotion detection per line
  - Event extraction with character participation tracking
  - Automatic graph updates during ingestion

**Architecture:**
```python
ingest_chapter_text(text) → LLM Analysis → Alias Resolution → {dialogue, events} → Graph Update
```

**Strengths:**
- Context-aware entity recognition via LLM
- Flexible model switching (Groq/Gemini/Ollama) with automatic fallback handlers
- Structured JSON output with validation
- Built-in Alias Resolution during event extraction

**Known Limitations:**
- Limited to 4000-6000 character chunks for cost/safety
- No temporal ordering of events

**Gap Severity:** 🟢 **None** (Dynamic scrapers, EPUB support, and Alias Resolution integrated)

---

### 3.2 Story Runtime ("The Brain")

**Status:** ✅ **Implemented with NetworkX Graph**

**Current Implementation**
- **Module:** [`adapters/graph_adapter.py`](file:///c:/Projects/webnovel-architect/adapters/graph_adapter.py)
- **Backend:** NetworkX DiGraph (Directed Graph)
- **Persistence:** JSON-based (`story_graph.json`)
- **Node Types:**
  - `character` nodes with attributes (e.g., `last_seen`)
  - `event` nodes with descriptions
- **Edge Types:**
  - `participant`: Character → Event (who was involved)
  - `featured`: Event → Character (bidirectional relationship)

**Key Features:**
- PageRank centrality calculation for character importance
- Automatic graph persistence on every update
- Singleton pattern for consistent state
- Temporal Weighting integrating chapter chronological progression into PageRank calculations

**Architecture:**
```python
GraphProvider:
  - add_character(name, attributes)
  - add_event(event_id, description, involved_entities)
  - get_character_importance(name) → PageRank score
  - save_graph() / load_graph()
```

**Strengths:**
- Persistent story memory across sessions
- Graph-based reasoning (not just counts)
- Extensible for future relationship types

**Known Limitations:**
- Simple JSON persistence (not scalable to large novels)
- No graph query language (manual NetworkX operations)

**Gap Severity:** 🟢 **Low** (meets current research needs)

---

### 3.3 Event Representation Layer

**Status:** ✅ **Implemented**

**Current Schema:**
```json
{
  "type": "event",
  "id": "event_1770638609_0",
  "description": "Aria confronts Thorne",
  "participants": ["Aria", "Thorne"]
}
```

**Capabilities:**
- Events extracted via LLM prompt engineering
- Automatic linking to character nodes
- Bidirectional edges for graph traversal

**Future Enhancements:**
- Temporal metadata (chapter, timestamp)
- Event types (dialogue, action, revelation)
- Causal chains (event → event edges)

**Gap Severity:** 🟢 **Low** (basic requirements met)

---

### 3.4 Graduation System ("The Director")

**Status:** ✅ **Implemented with PageRank**

**Current Implementation**
- **Module:** [`core/graduation.py`](file:///c:/Projects/webnovel-architect/core/graduation.py)
- **Algorithm:** NetworkX PageRank (α=0.85 damping factor)
- **Threshold:** 0.15 (15% of narrative attention)
- **Decision Logic:**
  ```python
  score = graph.get_character_importance(name)
  is_main_character = score >= 0.15
  ```

**How It Works:**
1. Graph contains characters and events
2. PageRank propagates importance through `participant`/`featured` edges, with an integrated Temporal Decay factor prioritizing recent chapters
3. Characters with high centrality "graduate" to main cast
4. Main cast → High-quality TTS (Kokoro)
5. Background → Fallback TTS (EdgeTTS)

**Strengths:**
- Structural reasoning (not just mention counts)
- Adapts as story evolves
- Mathematically grounded (PageRank proven for importance)

**Known Limitations:**
- Static threshold (doesn't adapt to cast size)
- Doesn't consider dialogue length, only participation

**Gap Severity:** 🟡 **Low-Medium** (functional, but research can improve)

---

### 3.5 Wiki Generator ("Memory")

**Status:** ✅ **Implemented and Stable**

**Current Implementation**
- **Module:** `app/services/wiki.py`
- **Output:** Markdown files in `wiki/` directory
- **Example:** [`wiki/aria.md`](file:///c:/Projects/webnovel-architect/wiki/aria.md), [`wiki/thorne.md`](file:///c:/Projects/webnovel-architect/wiki/thorne.md)

**Assessment:**
- Generates character profiles from graph data
- Stable and requires no immediate changes
- Ready for graph schema extensions

**Gap Severity:** 🟢 **None**

---

### 3.6 Audio Synthesis Layer ("The Voice")

**Status:** ✅ **Implemented with Voice Registry**

**Current Implementation**
- **Module:** [`adapters/tts_adapter.py`](file:///c:/Projects/webnovel-architect/adapters/tts_adapter.py)
- **Adapter Pattern:** Abstract `TTSProvider` base class
- **Engines:**
  - **KokoroAdapter:** Local CPU TTS (82M parameters, ONNX)
    - Requires: `kokoro-v0_19.onnx`, `voices.json`
    - Voice IDs: `af_bella`, etc.
  - **EdgeAdapter:** Online free TTS (Microsoft Edge)
    - Voice IDs: `en-US-GuyNeural`, etc.
    - Async implementation with `asyncio.run()`

**Configuration:**
```yaml
# config.yaml
tts_engine: "kokoro"      # Main cast
fallback_tts: "edge"      # Background characters
```

**Workflow:**
```python
main.py / audiobook_generator.py:
  # LLM extracts script (Narrator vs Dialogue) with caching & Groq->Gemini fallback
  # Using robust fallback and deduplication logic via VoiceRegistry
  voice_id = registry.get_voice_id("female", "adult")
  if graduation.evaluate_character(name):
    kokoro.generate_audio(line, voice_id, output_path)
  else:
    edge.generate_audio(line, "en-US-GuyNeural", output_path)
```

**Strengths:**
- Modular design (easy to add StyleTTS2, Piper, etc.)
- Zero-GPU compatible (CPU + online fallback)
- VoiceRegistry handles deduplication and automatic fallback.
- Advanced Audiobook Generator caches LLM scripts to prevent redundant API calls.
- Verified working in `verify_modular.py`

**Known Limitations:**
- Kokoro requires manual model download
- No voice cloning or fine-tuning

**Gap Severity:** 🟢 **Low** (Fully functional Voice Management System & Audiobook Generator)

---

### 3.7 User Interface

**Status:** ✅ **Implemented**

**Current Implementation**
- **Framework:** Streamlit (`app_ui.py`)
- **Features:**
  - Interactive Dashboard for real-time overview
  - Ingestion Engine UI for processing text files
  - Character Wiki Viewer for dynamically generated markdown profiles
  - Audio Generation Hub for on-demand TTS synthesis
- **Architecture:** Communicates with the core Python backend (Ingestion, Graduation, Graph Providers) and directly updates the Streamlit interface.

**Gap Severity:** 🟢 **None**

---

## 4. Technology Stack (Current Implementation)

| Component | Technology | Status |
|-----------|-----------|--------|
| **User Interface** | Streamlit | ✅ Implemented |
| **LLM Adapter** | LiteLLM (Gemini Flash default) | ✅ Implemented |
| **Graph Backend** | NetworkX DiGraph | ✅ Implemented |
| **Persistence** | JSON (node-link format) | ✅ Implemented |
| **Event Extraction** | LLM-based structured prompts | ✅ Implemented |
| **Importance Scoring** | PageRank (α=0.85) | ✅ Implemented |
| **TTS (Main)** | Kokoro ONNX (82M) | ✅ Implemented |
| **TTS (Fallback)** | EdgeTTS (Microsoft) | ✅ Implemented |
| **Configuration** | YAML (`config.yaml`) | ✅ Implemented |

---

## 5. Architecture Status

### ✅ **Architecture Alignment Achieved**

The previous "architecture drift" issue has been **resolved**. The implementation now matches the documented DyG-RAG design:

- ✅ Event-centric graph structure
- ✅ Graph-based importance scoring (PageRank)
- ✅ Persistent story memory
- ✅ Modular adapter pattern
- ✅ LLM-based entity/event extraction

### Current Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    WEBNOVEL ARCHITECT                    │
│              Neuro-Symbolic Story Intelligence           │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
   ┌─────────┐        ┌──────────┐       ┌──────────┐
   │   LLM   │        │  Graph   │       │   TTS    │
   │ Adapter │        │ Adapter  │       │ Adapter  │
   └─────────┘        └──────────┘       └──────────┘
        │                   │                   │
   LiteLLM            NetworkX            Kokoro/Edge
   (Gemini)           (DiGraph)           (Dual TTS)
        │                   │                   │
        └───────────────────┴───────────────────┘
                            │
                ┌───────────┴───────────┐
                ▼                       ▼
          ┌──────────┐           ┌──────────┐
          │Ingestion │           │Graduation│
          │  Engine  │           │  System  │
          └──────────┘           └──────────┘
                │                       │
                └───────────┬───────────┘
                            ▼
                    ┌───────────────┐
                    │  Story Graph  │
                    │ (Persistent)  │
                    └───────────────┘
```

---

## 6. Operational Strengths

✅ **Modular "Switchboard" Architecture**
- Swap LLM providers via `config.yaml` (Gemini, Ollama, GPT, etc.)
- Swap TTS engines without code changes
- Graph backend can be replaced (NetworkX → KuzuDB/Neo4j)

✅ **Zero-GPU Compatible**
- LLM: API-based (Gemini Flash free tier)
- TTS: CPU-based (Kokoro ONNX) + online fallback (EdgeTTS)
- Graph: Lightweight NetworkX (pure Python)

✅ **Persistent Story Memory**
- Graph saved to `story_graph.json` after every update
- Survives restarts (load on initialization)
- Enables incremental chapter processing

✅ **Verified End-to-End**
- [`verify_modular.py`](file:///c:/Projects/webnovel-architect/verify_modular.py) tests full pipeline
- Mocked LLM for reproducible testing
- Validates: Ingestion → Graph → Graduation → TTS

✅ **Research-Ready**
- PageRank-based graduation is novel for audio drama
- Event graph enables future temporal reasoning
- Modular design supports ablation studies

---

## 7. Current Limitations & Technical Debt

### 🟡 **Medium Priority**

1. **Static Graduation Threshold**
   - Hardcoded 0.15 threshold doesn't adapt to cast size
   - **Impact:** May fail for stories with 20+ characters
   - **Solution:** Dynamic threshold (e.g., top-k characters)

2. **Limited Event Metadata**
   - No timestamps, chapter numbers, or event types
   - **Impact:** Cannot implement temporal decay effectively for complex timelines
   - **Solution:** Add stricter `timestamp`, `chapter_id` to event nodes

### 🟢 **Low Priority**

5. **JSON Persistence Scalability**
   - Full graph rewrite on every update
   - **Impact:** Slow for 1000+ chapter novels
   - **Solution:** Migrate to KuzuDB or SQLite

6. **No Graph Query Interface**
   - Manual NetworkX operations in code
   - **Impact:** Hard to debug, analyze graph
   - **Solution:** Add query methods (e.g., `get_character_events(name)`)

---

## 8. Immediate Next Steps (Prioritized)

### **Sprint 1: Temporal Weighting & Alias Resolution** (Research Value & Quality)
✅ **Completed:** `chapter_id` integration and temporal decay algorithm implemented in GraphAdapter.
✅ **Completed:** Alias resolution integrated into the core ingestion pipeline.

### **Sprint 4: Advanced Graph Features**
11. Add event → event causal edges
12. Implement graph query methods
13. Create graph visualization tool (for debugging/demos)

---

## 9. Verification Status

| Test | Status | Evidence |
|------|--------|----------|
| **Ingestion** | ✅ Pass | `verify_modular.py` extracts 2 dialogue lines |
| **Event Extraction** | ✅ Pass | Events found in `story_graph.json` |
| **Graph Persistence** | ✅ Pass | Graph loads from JSON on restart |
| **PageRank Calculation** | ✅ Pass | Aria score computed successfully |
| **Graduation Logic** | ✅ Pass | Threshold comparison works |
| **Kokoro TTS** | ✅ Pass | Generates audio (or graceful mock) |
| **EdgeTTS** | ✅ Pass | Async generation works |
| **End-to-End** | ✅ Pass | `main.py` runs without errors |

---

## 10. Readiness Assessment

| Capability | Readiness | Notes |
|-----------|-----------|-------|
| **Prototype Demonstration** | ✅ **High** | Fully functional demo ready |
| **Research Validation** | 🟡 **Medium-High** | Core hypothesis testable, needs temporal weighting |
| **Publication Submission** | 🟡 **Medium** | Needs ablation studies, baseline comparisons |
| **Production Deployment** | 🟢 **Early Stage** | Functional but needs voice management, scalability |

---

## 11. Key Achievements (Phase 3 Completed)

🎉 **Successfully migrated from heuristic prototype to graph-based architecture**

- ✅ DyG-RAG with chronological Event Unit (DEU) modeling
- ✅ Temporal Chain-of-Thought (Time-CoT) Story Q&A
- ✅ Multi-source ingestion (Scrapers / EPUB / Text)
- ✅ Synchronized Audio Visualizer with WebVTT
- ✅ Living Character Wiki with dynamic biography updates

---

## 12. Repository Status

**Last Updated:** 2026-02-10  
**Git Status:** Clean (pushed to GitHub on 2026-02-09)  
**Documentation:** Comprehensive (9 documents in `Documents/`)  
**Code Quality:** Modular, well-commented, verified

**Next Milestone:** Implement voice assignment system and temporal weighting for research paper.

---

*For detailed implementation roadmap, see [`Detailed Implementation Roadmap & Future Development Plan.md`](file:///c:/Projects/webnovel-architect/Documents/Detailed%20Implementation%20Roadmap%20&%20Future%20Development%20Plan.md)*

---

## Detailed Implementation Roadmap & Future Development Plan


### 1. Strategic Development Objective

The immediate goal is to evolve the existing heuristic prototype into a **Minimum Publishable System (MPS)** that:

- Implements an event-centric dynamic graph runtime
    
- Demonstrates measurable improvement in narrative consistency
    
- Produces reproducible experimental outputs
    

All subsequent enhancements (advanced NLP, high-fidelity TTS) are considered secondary.

---

### 2. Development Phases

#### Phase 3 — Neuro-Symbolic Runtime Migration (COMPLETED)

**Goal:** Replace count-based logic with an event-centric dynamic graph. **(Status: Done)**

**Primary Deliverables**

- Graph database integrated (KuzuDB or Neo4j)
    
- Formal event schema implemented
    
- Persistent storage enabled
    

**Tasks**

1. **Define Graph Schema**
    
    **Nodes**
    
    - Character
        
    - Event
        
    - Location
        
    - Artifact
        
    
    **Edges**
    
    - ACTED_IN
        
    - CAUSED_BY
        
    - RELATED_TO
        
    - OCCURRED_AT
        
2. **Replace `_runtime_db`**
    
    - Introduce persistence layer
        
    - Implement graph insert/update operations
        
3. **Event Object Construction**
    
    Required attributes:
    
    - Event ID
        
    - Actors
        
    - Action
        
    - Source Text Reference
        
    - Narrative Order
        
4. **Migration Strategy**
    
    - Maintain compatibility with current ingestion output
        
    - Backfill prototype data into graph
        

**Exit Criteria**

- Events persist across sessions
    
- Relationships are queryable
    
- Wiki generation uses graph data
    

---

#### Phase 3.1 — Zero-GPU Event Extraction Validation (COMPLETED)

**Goal:** Validate DyG-RAG feasibility without heavy compute. **(Status: Done)**

**Approach**

- Dual Pipeline Strategy:
    - API-based structured extraction (Groq as primary, Gemini as fallback)
    - Deterministic Named Entity Recognition (spaCy fallback)
- Convert response → graph insertion

**Benefits**

- High accuracy via LLMs or deterministic fallback via spaCy
- Architecture validation independent of local GPU
    

**Exit Criteria**

- End-to-end pipeline functioning with event graph updates
    

---

#### Phase 3.2 — Graph-Based Character Importance (COMPLETED)

**Goal:** Replace heuristic confidence scoring. **(Status: Done)**

**Implementation**

- Compute centrality metrics:
    
    - PageRank
        
    - Degree centrality
        
- Combine with:
    
    - Event participation frequency
        
    - Temporal decay weighting based on chronological chapter progression
        

**Output**

- Character classification tiers:
    
    - Background
        
    - Supporting
        
    - Main Cast
        

**Exit Criteria**

- Ranking aligns with manually labeled ground truth
    

---

### 3. Phase 4 — Knowledge & Output Stabilization (COMPLETED)

#### Wiki Generator Integration

**Tasks**

- Update data source from runtime dict → graph queries
    
- Expand wiki schema:
    
    - Event history
        
    - Relationship graph snapshot
        

**Exit Criteria**

- Canonical wiki auto-updates after each ingestion cycle
    

---

### 4. Phase 5 — Interactive UI Dashboard (COMPLETED)

**Goal:** Demonstrate a fully integrated user experience for monitoring graph and managing features.

**Implementation Priority**

1. Streamlit Dashboard Data Hub
    
2. Character Wiki Viewer Interface
    
3. Ingestion and Audio Generation Controls
    

**Function**

- Assign consistent voice per main character
    

**Exit Criteria**

- Audio generated for at least one main cast member
    

---

### 5. Phase 6 — Experimentation & Evaluation Plan (COMPLETED)

#### Research Experiments

1. **Baseline Comparison**
    
    - Linear pipeline vs DyG-RAG
        
2. **Consistency Measurement**
    
    - Canon contradiction rate
        
3. **Importance Accuracy**
    
    - Character ranking vs annotated dataset
        
4. **Ablation Study**
    
    - Without graph centrality
        
    - Without event persistence
        

---

#### Metrics (Implemented in `scripts/evaluate.py`)

- Entity tracking Precision/Recall (F1)
- Graph traversal latency
- Character salience correlation (Spearman ρ)
- TTS Real-Time Factor (RTF)

---

### 6. Experiment Tracking & Reproducibility

**Required Infrastructure**

- Versioned datasets
    
- Configuration files per run
    
- Stored outputs
    

**Directory Pattern**

```
experiments/
    run_001/
        config.yaml
        metrics.json
        graph_snapshot.db
```

**Policy**

- Every experimental result must be reproducible from stored configuration.
    

---

### 7. Risk Management

|Risk|Impact|Mitigation|
|---|---|---|
|Event extraction noise|Incorrect graph edges|Human validation set|
|Graph schema changes|Data migration overhead|Versioned schema|
|Performance bottlenecks|Slow ingestion|Batch insert strategy|
|Over-ambitious scope|Missed deadlines|Lock Minimum Publishable System|

---

### 8. Minimum Publishable System (MPS) Definition

The project is publication-ready when:

- spaCy or API extraction functional (✓ Done)
- Dynamic event graph operational (✓ Done)
- Centrality-based graduation implemented (✓ Done)
- Wiki generated from graph (✓ Done)
- Experimental comparison vs baseline completed (✓ Done)

**Status:** The MPS criteria have been fully met as of Phase 6.

---

### 9. Phase 7 — Advanced Extractions & Audiobook Generation (COMPLETED)

**Goal:** Elevate extraction quality and implement full story synthesis capabilities.

**Tasks:**
1. **Default to LLM Extraction:** Transition the default extraction engine from spaCy to the LLM-based pipeline to capture nuanced, high-quality character and world data. (Done)
2. **Action-Based Event Schema / DyG-RAG Integration:** Refactor the event generation logic to Dynamic Event Units (DEUs) to support Time-CoT temporal reasoning. (Done)
3. **Total Audiobook Generation:** Implement a feature to synthesize an audiobook for an entire chapter or story at once, bypassing the requirement for individual characters to graduate first. This pipeline includes chunking logic, LLM-based Narrator/Dialogue extraction, and a dedicated caching system (`cached_script.json`) to minimize redundant API calls. (Done)

---

### 10. Phase 8 — Dynamic Memory & Accessibility Features (CURRENT)

**Goal:** Make the character wiki a living document and enhance the audiobook experience with a visualizer.

**Tasks:**
1. **Per-Chapter Wiki Evolution:** Re-integrate LLM summarization. When a character appears in a new chapter, append what happened to them (based on extracted Dynamic Event Units) to their canonical long biography, allowing their lore to grow dynamically rather than just stating their first/last chapter.
2. **TTS On-Screen Visualizer:** Upgrade the Streamlit Audio Hub to include a synchronized on-screen visualizer (WebVTT). The text of the audiobook is displayed and highlighted perfectly in sync with the TTS audio playback, mimicking a modern audiobook app.

---

### 11. Future Research Extensions (Post-Submission)

- Narrative causality inference models
    
- Temporal reasoning across arcs
    
- Cross-novel knowledge transfer
    
- Emotion and theme tracking
    
- Author-assist editing tools
    
- DyG-RAG based conversational chatbot for interacting with the story world
    

---

### 12. Final Delivery Package

At completion, the project should include:

- Source code repository
    
- Architecture documentation
    
- Research methodology
    
- Experimental results
    
- Demonstration pipeline
    
- Canonical wiki output
    
- Optional audio demo
    

---

---

## Future Development Plan


## Completed Phases

| Phase | What | Status |
|-------|------|--------|
| Phase 1 | Core ingestion pipeline, Chapter model | ✅ Done |
| Phase 2 | Character runtime, Graduation algorithm | ✅ Done |
| Phase 3 | Graph-based runtime (NetworkX / KuzuDB) | ✅ Done |
| Phase 4 | Voice Registry, TTS adapter, persistence | ✅ Done |
| Phase 5 | Streamlit Web UI Dashboard | ✅ Done |
| Phase 6 | Experimental Evaluation & Advanced Features | ✅ Done |
| Phase 7 | Final Submission & Demonstration | 🔄 Current |

---

## Recently Completed Sprints

### Sprint 1 — spaCy NER Integration
**Goal**: Replace the regex-based word extractor with a proper Named Entity Recognition model.
**Status**: ✅ Done (Implemented alongside LLM standard extraction as a deterministic fallback pipeline)

### Sprint 2 — Temporal Weighting in the Graph
**Goal**: Make character importance time-aware, not just count-based.
**Status**: ✅ Done (`chapter_id` based Temporal Decay integrated into graph PageRank scoring)

### Sprint 4 — LLM-Powered Structured Extraction
**Goal**: Replace all heuristics with a single structured LLM call per chapter.
**Status**: ✅ Done (`litellm` + Gemini Flash integration implemented in `core/ingestion.py`)

### Sprint 3 — Alias Resolution
**Goal**: Merge "Elara", "Lady Elara", and "the young mage" into one character entity.
**Status**: ✅ Done (Integrated coreference entity linking and alias normalization directly into the ingestion pipeline)

### Sprint 5 — Full Audio Chapter Rendering
**Goal**: Render an entire chapter as a complete audio drama with per-character voices.
**Status**: ✅ Done (Implemented LLM-based Narrator/Dialogue script extraction with caching, Groq to Gemini fallback, and final audio stitching)

---

## Recommended Priority Order

```
Sprint 6: DyG-RAG Webnovel Chatbot → High effort, interactive showcase
Sprint 7: Neo4j/KuzuDB Migration  → Medium effort, scalability
```

---

## Long-Term Vision

- **REST API**: Expose the pipeline as a FastAPI service (`POST /ingest`, `GET /characters`, `GET /audio/{id}`)
- **Epub/PDF Reader**: Direct ingestion from `.epub` files instead of manual paste
- **Web Reader Integration**: Embed character cards and audio in a reader experience
- **Multi-Language Support**: Swap NER and TTS models per locale
- **DyG-RAG Chatbot**: Interactive conversational agent using Dynamic Graph RAG to query and interact with the novel's universe and events


---

