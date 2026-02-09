
**Project Title:** _Webnovel Architect — Neuro-Symbolic Story Intelligence System_  
**Document Version:** 1.0  
**Date:** 2026-02-09  
**Lifecycle Phase:** Prototype Verified → Architecture Transition

---

### 1. Executive Summary

The project has successfully demonstrated the **core “Story Intelligence” capability** through a functional prototype. The system can ingest narrative text, identify characters, track confidence scores, and generate canonical wiki pages.

However, a recent research audit triggered a strategic pivot from a **linear, heuristic pipeline** toward a **Dynamic Event Graph (DyG-RAG) architecture**.

At present:

- The **implementation reflects the original count-based design**.
    
- The **documentation reflects the new event-centric architecture**.
    

This mismatch introduces architectural drift and must be resolved through structured refactoring in the next phase.

---

### 2. Phase Status Overview

|Phase|Description|Status|
|---|---|---|
|Phase 1|Heuristic Prototype Development|Completed|
|Phase 2|Story Intelligence Verification|Completed|
|Phase 3|Neuro-Symbolic Graph Migration|Planned (Immediate)|
|Phase 4|Audio Synthesis Integration|Not Started|

---

### 3. Subsystem Implementation Status

#### 3.1 Ingestion Engine (“Eye”)

**Status:** Implemented (Event Extraction Added)

**Current Implementation**

- Module: `app.services.ingest.py`
    
- Method: Regex and heuristic name detection
    
- Example capability: Detects entities such as “Aria”
    

**Limitations**

- No context-aware linking
    
- Prone to alias confusion
    
- Cannot detect implicit references
    

**Planned Upgrade**

- Replace heuristics with:
    
    - spaCy (Laptop Tier)
        
    - xCoRe (Research Tier)
        
    - API-based extraction (Zero-GPU Tier)
        

**Gap Severity:** Medium

---

#### 3.2 Story Runtime (“Brain”)

**Status:** Partial / Outdated

**Current Implementation**

- In-memory dictionary (`_runtime_db`)
    
- Tracks:
    
    - Character names
        
    - Confidence scores
        

**Limitations**

- No persistence
    
- No relationship modeling
    
- Cannot represent event causality
    

**Planned Upgrade**

- Replace with Dynamic Event Graph (DyG-RAG)
    
- Database candidates:
    
    - KuzuDB
        
    - Neo4j
        

**Gap Severity:** Critical

This is the highest priority refactor.

---

#### 3.3 Event Representation Layer

**Status:** Implemented (Basic)

**Current Behavior**

- Events are implicitly inferred from mention frequency.
    

**Required Capability**

- Formal event objects:
    
    - Actors
        
    - Action
        
    - Time
        
    - Relationships
        

**Gap Severity:** Critical

---

#### 3.4 Graduation System (“Director”)

**Status:** Implemented (PageRank Integration)

**Current Logic**

```
if confidence > 0.75:
    assign_voice()
```

**Limitations**

- Based only on mention counts
    
- No structural reasoning
    

**Planned Upgrade**

- Graph-based importance scoring:
    
    - PageRank
        
    - Event participation
        
    - Temporal weighting
        

**Gap Severity:** Medium–High

---

#### 3.5 Wiki Generator (“Memory”)

**Status:** Implemented

**Current Implementation**

- Module: `app.services.wiki.py`
    
- Output: Markdown files (e.g., `wiki/aria.md`)
    

**Assessment**

- Stable
    
- Requires only minor schema adaptation for graph integration
    

**Gap Severity:** Low

---

#### 3.6 Audio Synthesis Layer (“Voice”)

**Status:** Not Started

**Planned Implementations**

- Research Tier: StyleTTS2
    
- Laptop Tier: Piper
    
- Zero-GPU Tier: Edge-TTS (placeholder)
    

**Gap Severity:** Low (Non-core research dependency)

---

### 4. Technology Alignment Status

|Component|Current|Target|
|---|---|---|
|Entity Extraction|Regex|spaCy / xCoRe|
|Runtime Memory|In-memory dict|Graph DB|
|Event Modeling|None|Event-centric schema|
|Importance Scoring|Count-based|Graph centrality|
|Persistence|None|Database-backed|

---

### 5. Architecture Drift Analysis

**Observation**

- Documentation describes DyG-RAG.
    
- Code still operates as a linear heuristic pipeline.
    

**Risk**

- Experimental results cannot be reproduced.
    
- Mentor review becomes difficult.
    
- Future development complexity increases.
    

**Required Action**

- Refactor runtime layer before adding new features.
    

---

### 6. Operational Strengths

- Functional prototype exists
    
- Modular service layout established
    
- Wiki generation already stable
    
- Deployment tier strategy defined
    

---

### 7. Current Technical Debt

- Lack of persistent storage
    
- Absence of formal event schema
    
- Weak entity linking
    
- Non-reproducible runtime state
    

---

### 8. Immediate Priority Tasks (Next Sprint)

1. Replace `_runtime_db` with KuzuDB or SQLite-backed structure.
    
2. Implement structured event representation.
    
3. Introduce API-based event extraction.
    
4. Prepare graph schema definition.
    
5. Maintain compatibility with existing wiki generator.
    

---

### 9. Readiness Assessment

|Capability|Readiness|
|---|---|
|Prototype Demonstration|High|
|Research Validation|Medium|
|Publication Submission|Low (until graph runtime exists)|
|Productization|Early Stage|

---

When you’re ready, say **“next”** and I will provide **Document 4 — Detailed Implementation Roadmap & Future Development Plan**.