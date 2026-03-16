
**Project Title:** _Webnovel Architect — Neuro-Symbolic Story Intelligence System_  
**Document Version:** 1.0  
**Date:** 2026-02-09  
**Purpose:** Transition the prototype into a research-grade, reproducible system aligned with the DyG-RAG architecture.

---

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
    - API-based structured extraction (LiteLLM)
    - Fallback Named Entity Recognition (spaCy)
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
3. **Total Audiobook Generation:** Implement a feature to synthesize an audiobook for an entire chapter or story at once, bypassing the requirement for individual characters to graduate first. (Done)

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