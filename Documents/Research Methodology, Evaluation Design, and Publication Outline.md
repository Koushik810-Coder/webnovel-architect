**Project Title:** _Webnovel Architect — Neuro-Symbolic Story Intelligence System_  
**Document Version:** 1.0  
**Date:** 2026-02-09  
**Purpose:** Define a rigorous, reproducible methodology suitable for academic evaluation and submission to a peer-reviewed venue.

---

### 1. Research Approach

The project follows a **Design Science + Experimental Evaluation** methodology:

- **Design Science Component:**  
    Creation of a novel neuro-symbolic system (DyG-RAG) for persistent narrative intelligence.
    
- **Experimental Component:**  
    Quantitative comparison against baseline narrative processing approaches.
    

This dual approach positions the work as both:

- An engineering artifact
    
- A research contribution
    

---

### 2. Hypotheses

**H1 — Narrative Consistency**

Event-centric graph representation reduces canonical inconsistencies compared to a linear pipeline.

**H2 — Character Salience Detection**

Graph centrality metrics produce rankings closer to human-annotated importance than mention-frequency heuristics.

**H3 — Long-Context Retention**

Persistent symbolic memory improves tracking of entities across long narrative sequences.

---

### 3. Experimental Design

#### 3.1 Baseline System

Linear pipeline with:

- Regex/spaCy entity detection
    
- Mention counting
    
- Stateless processing
    

#### 3.2 Experimental System

DyG-RAG architecture with:

- Event extraction
    
- Persistent dynamic graph
    
- Centrality-based reasoning
    

---

### 4. Dataset Strategy

#### Sources

- Public domain novels or serialized webnovels
    
- Selected chapters representing multi-character interactions
    

#### Dataset Preparation

- Segment into chapter units
    
- Annotate:
    
    - Character presence
        
    - Event participation
        
    - Ground-truth importance ranking
        

#### Dataset Partitioning

- Development Set
    
- Evaluation Set
    
- Validation Set
    

---

### 5. Annotation Protocol

To ensure reliable ground truth:

- Define explicit character importance criteria:
    
    - Frequency of appearance
        
    - Role in key events
        
    - Narrative influence
        
- Use either:
    
    - Self-annotation with documented rubric
        
    - Multiple annotators with agreement scoring (if team available)
        

#### Agreement Metric

- Inter-annotator agreement (e.g., Cohen’s Kappa)
    

---

### 6. Evaluation Metrics

#### Entity Consistency

- Percentage of correctly linked references
    
- Alias resolution accuracy
    

#### Event Extraction Quality

- Precision
    
- Recall
    
- F1 Score
    

#### Narrative Consistency

- Canon contradiction rate:
    
    - Conflicting relationships
        
    - Incorrect event causality
        

#### Character Importance Accuracy

- Rank correlation with ground truth:
    
    - Spearman correlation coefficient
        

#### Graph Coverage

- Ratio of narrative events represented in graph
    

---

### 7. Experimental Procedure

1. Run baseline pipeline across dataset.
    
2. Record:
    
    - Extracted entities
        
    - Character rankings
        
    - Generated wiki
        
3. Run DyG-RAG system.
    
4. Compute metrics for both systems.
    
5. Perform comparative statistical analysis.
    

---

### 8. Ablation Study Plan

Evaluate the contribution of individual components:

- Without graph centrality
    
- Without persistent storage
    
- Without event representation
    
- Neural extraction vs heuristic extraction
    

Purpose:

- Demonstrate which subsystem drives performance gains.
    

---

### 9. Reproducibility Requirements

Each experiment must include:

- Configuration file
    
- Model version
    
- Dataset version
    
- Graph snapshot
    
- Metric outputs
    

#### Repository Practices

- Tagged releases
    
- Versioned schemas
    
- Deterministic processing where possible
    

---

### 10. Threats to Validity

#### Internal Validity

- Event extraction noise affecting graph structure
    

Mitigation:

- Manual validation subset
    

#### External Validity

- Dataset may not generalize to all narrative genres
    

Mitigation:

- Include at least two different narrative styles
    

#### Construct Validity

- Character importance is partially subjective
    

Mitigation:

- Explicit annotation rubric
    

---

### 11. Ethical Considerations

- Use only legally distributable text
    
- Clearly disclose automated processing limitations
    
- Avoid misrepresentation of generated narrative interpretations
    

---

### 12. Target Publication Venues (Examples)

- Student research conferences (IEEE regional)
    
- NLP or Digital Humanities workshops
    
- Applied AI symposiums
    

Selection criteria:

- Accept system + evaluation papers
    
- Support hybrid neuro-symbolic research
    

---

### 13. Proposed Paper Structure

1. **Abstract**
    
2. **Introduction**
    
    - Motivation
        
    - Problem definition
        
3. **Related Work**
    
    - Narrative understanding
        
    - Neuro-symbolic AI
        
4. **System Architecture**
    
5. **Methodology**
    
6. **Experimental Setup**
    
7. **Results**
    
8. **Discussion**
    
9. **Limitations**
    
10. **Future Work**
    
11. **Conclusion**
    

---

### 14. Expected Research Contributions

- Demonstration of DyG-RAG for narrative modeling
    
- Evidence that event-centric memory improves consistency
    
- Framework for automated story intelligence systems
    

---

If you want to complete the full professional documentation set, say **“next”** and I will provide **Document 6 — Project Management Plan, Timeline, and Milestone Schedule** (useful for mentor reviews, viva, and progress tracking).