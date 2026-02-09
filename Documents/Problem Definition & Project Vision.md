**Project Title:** _Webnovel Architect — Neuro-Symbolic Story Intelligence System_  
**Document Version:** 1.0  
**Date:** 2026-02-09

---

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
    
- Generates canonical knowledge artifacts (Wiki, Character Status, Audio Voice Assignment)
    

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
    
- Optional audio synthesis layer
    

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
    

