
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

#### Phase 3 — Neuro-Symbolic Runtime Migration (Critical)

**Goal:** Replace count-based logic with an event-centric dynamic graph.

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

#### Phase 3.1 — Zero-GPU Event Extraction Validation

**Goal:** Validate DyG-RAG feasibility without heavy compute. (COMPLETED)

**Approach**

- API-based structured extraction
    
- Convert JSON response → graph insertion
    

**Benefits**

- Fast experimentation
    
- Architecture validation independent of local GPU
    

**Exit Criteria**

- End-to-end pipeline functioning with event graph updates
    

---

#### Phase 3.2 — Graph-Based Character Importance

**Goal:** Replace heuristic confidence scoring. (COMPLETED)

**Implementation**

- Compute centrality metrics:
    
    - PageRank
        
    - Degree centrality
        
- Combine with:
    
    - Event participation frequency
        
    - Temporal weighting
        

**Output**

- Character classification tiers:
    
    - Background
        
    - Supporting
        
    - Main Cast
        

**Exit Criteria**

- Ranking aligns with manually labeled ground truth
    

---

### 3. Phase 4 — Knowledge & Output Stabilization

#### Wiki Generator Integration

**Tasks**

- Update data source from runtime dict → graph queries
    
- Expand wiki schema:
    
    - Event history
        
    - Relationship graph snapshot
        

**Exit Criteria**

- Canonical wiki auto-updates after each ingestion cycle
    

---

### 4. Phase 5 — Audio Layer Integration (Non-Core)

**Goal:** Demonstrate multimodal narrative representation.

**Implementation Priority**

1. Edge-TTS (Zero-GPU)
    
2. Piper (Laptop Tier)
    
3. StyleTTS2 (Research Tier)
    

**Function**

- Assign consistent voice per main character
    

**Exit Criteria**

- Audio generated for at least one main cast member
    

---

### 5. Experimentation & Evaluation Plan

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

#### Metrics

- Entity consistency score
    
- Event precision/recall
    
- Graph coverage ratio
    
- Character salience correlation
    

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

- spaCy or API extraction functional
    
- Dynamic event graph operational
    
- Centrality-based graduation implemented
    
- Wiki generated from graph
    
- Experimental comparison vs baseline completed
    

---

### 9. Future Research Extensions (Post-Submission)

- Narrative causality inference models
    
- Temporal reasoning across arcs
    
- Cross-novel knowledge transfer
    
- Emotion and theme tracking
    
- Author-assist editing tools
    

---

### 10. Final Delivery Package

At completion, the project should include:

- Source code repository
    
- Architecture documentation
    
- Research methodology
    
- Experimental results
    
- Demonstration pipeline
    
- Canonical wiki output
    
- Optional audio demo
    

---

If you want, we can continue the documentation set.  
Say **“next”** and I will produce **Document 5 — Research Methodology, Evaluation Design, and Publication Outline** (this is the piece that typically determines whether your work is accepted as a paper).