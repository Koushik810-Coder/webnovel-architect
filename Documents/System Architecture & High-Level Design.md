
**Project Title:** _Webnovel Architect — Neuro-Symbolic Story Intelligence System_  
**Document Version:** 1.0  
**Date:** 2026-02-09

---

### 1. Architectural Overview

Webnovel Architect is designed as a **layered neuro-symbolic pipeline** that transforms unstructured narrative text into a persistent, queryable knowledge representation and canonical outputs.

The architecture follows an **Event-Centric DyG-RAG (Dynamic Graph Retrieval-Augmented Generation)** model in which:

- Neural components perform extraction and interpretation.
    
- Symbolic components maintain long-term structured memory.
    
- Retrieval mechanisms ensure consistency across evolving narrative context.
    

**Top-Level Flow**

```
Raw Narrative Text
    ↓
Ingestion & Entity Extraction ("Eye")
    ↓
Event Construction Layer
    ↓
Dynamic Event Graph Runtime ("Brain")
    ↓
Reasoning & Character Graduation ("Director")
    ↓
Knowledge Outputs ("Memory" + "Voice")
```

---

### 2. Core Architectural Principles

1. **Event-Centric Representation**
    
    - Narrative state is encoded as events, not mention counts.
        
2. **Persistent Canonical Memory**
    
    - All validated information is stored in a graph database.
        
3. **Neuro-Symbolic Hybridization**
    
    - Neural NLP performs perception.
        
    - Symbolic graph performs reasoning.
        
4. **Traceability**
    
    - Every output can be traced back to specific source text and events.
        
5. **Tiered Deployability**
    
    - System can operate across multiple hardware profiles.
        

---

### 3. Major System Components

#### 3.1 Ingestion Engine (“Eye”)

**Purpose**

- Convert raw narrative text into structured entities and candidate events.
    

**Inputs**

- Chapter text or document
    

**Outputs**

- Entities (characters, locations, objects)
    
- Preliminary event representations
    

**Current Implementation**

- Regex + heuristic extraction
    

**Target Implementation**

- spaCy or xCoRe entity linking
    
- LLM-based event extraction (API-driven)
    

**Key Responsibilities**

- Tokenization
    
- Named entity recognition
    
- Context-aware linking
    

---

#### 3.2 Event Construction Layer

**Purpose**

- Convert extracted information into formal event objects suitable for graph insertion.
    

**Event Schema (Conceptual)**

```
Event:
    event_id
    timestamp / narrative order
    actors
    action
    location
    relationships
    source_text_reference
```

**Outputs**

- Structured event instances
    

---

#### 3.3 Story Runtime (“Brain”) — Dynamic Event Graph (DyG-RAG)

**Purpose**

- Maintain persistent story knowledge.
    
- Represent relationships across time.
    

**Technology Options**

- KuzuDB (preferred for local research)
    
- Neo4j (alternative)
    

**Graph Model**

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
    

**Functions**

- Insert events dynamically
    
- Maintain evolving relationships
    
- Support query and retrieval
    

---

#### 3.4 Reasoning & Graduation System (“Director”)

**Purpose**

- Determine narrative importance of entities.
    

**Current Logic**

- Confidence score based on mention frequency
    

**Target Logic**

- Graph-based centrality metrics:
    
    - PageRank
        
    - Degree centrality
        
    - Event participation weighting
        

**Outputs**

- Character classification:
    
    - Background
        
    - Supporting
        
    - Main cast
        

---

#### 3.5 Knowledge Memory Layer (“Wiki Generator”)

**Purpose**

- Produce canonical, human-readable knowledge artifacts.
    

**Outputs**

- Markdown wiki pages
    
- Character summaries
    
- Relationship tables
    

**Design Decision**

- Markdown retained as canonical, version-controlled memory.
    

---

#### 3.6 Voice Synthesis Layer (“Audio”)

**Purpose**

- Assign and generate character voice output.
    

**Planned Implementations**

- Research Tier: StyleTTS2
    
- Laptop Tier: Piper
    
- Zero-GPU Tier: Edge-TTS
    

**Status**

- Not yet implemented.
    

---

### 4. Data Flow Description

1. Text is ingested.
    
2. Entities and candidate events are extracted.
    
3. Events are normalized and structured.
    
4. Events are inserted into the dynamic graph.
    
5. Graph metrics update character importance.
    
6. Wiki pages and optional audio are generated.
    

---

### 5. Deployment Tier Strategy

|Tier|Extraction|Runtime|Audio|
|---|---|---|---|
|Research Lab|xCoRe|Graph DB|StyleTTS2|
|Laptop|spaCy|Graph DB|Piper|
|Zero-GPU|API|KuzuDB|Edge-TTS|

---

### 6. Non-Functional Requirements

- Reproducibility of results
    
- Persistence of narrative state
    
- Modular extensibility
    
- Hardware adaptability
    
- Transparent reasoning trace
    

---

### 7. Known Architectural Risks

- Complexity of event extraction accuracy
    
- Graph schema evolution over time
    
- Performance with very large narratives
    
- Integration overhead between neural and symbolic layers
    

---

### 8. Architecture Governance Rule

- All major design changes must update this document.
    
- Implementation must not diverge from documented interfaces.
    

---

When ready, say **“next”** and I will provide **Document 3 — Current State Report (Implementation Status & Gap Analysis)**.