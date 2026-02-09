**Project Title:** _Webnovel Architect — Neuro-Symbolic Story Intelligence System_  
**Document Version:** 1.1  
**Date:** 2026-02-09

---

### 1. Development Methodology (SDLC Model)

The project follows a **Hybrid SDLC Approach** combining:

### Primary Model: **Spiral Model (Research-Driven Development)**

**Rationale**

- The architecture is evolving based on experimentation.
    
- Risk identification (e.g., hallucinated causality, extraction accuracy) is central.
    
- Iterative refinement of the DyG-RAG design is required before stabilization.
    

**Spiral Activities Applied**

1. Requirement Analysis
    
2. Risk Evaluation
    
3. Prototyping / Experimentation
    
4. Validation and Feedback
    

Each iteration produces:

- Updated architecture
    
- Measured results
    
- Revised implementation plan
    

---

### Supporting Execution Style: **Incremental / Agile Implementation**

Within each spiral cycle:

- Work is executed in small milestones (“sprints”).
    
- Functional subsystems are delivered incrementally.
    

**Reason**

- Enables continuous demonstration to mentor.
    
- Maintains implementation momentum while research evolves.
    

---

### SDLC Summary

|Aspect|Model Used|
|---|---|
|Research & Architecture Evolution|Spiral Model|
|Engineering Execution|Incremental / Agile|
|Final Stabilization|Structured Integration Phase|

---

### 2. Project Lifecycle Phases

#### Phase 0 — Problem Definition & Literature Study

**Objectives**

- Define research problem
    
- Review neuro-symbolic and narrative modeling work
    

**Deliverables**

- Problem Statement Document
    
- Literature Review Notes
    

**Status:** Completed

---

#### Phase 1 — Heuristic Prototype Development

**Objectives**

- Build minimal story intelligence functionality
    
- Validate feasibility of entity tracking
    

**Implemented Components**

- Regex ingestion
    
- Confidence scoring
    
- Wiki generation
    

**Exit Criteria**

- Prototype demonstrates character detection
    

**Status:** Completed

---

#### Phase 2 — Prototype Verification

**Objectives**

- Confirm that the system tracks characters across text
    
- Validate graduation logic concept
    

**Outcome**

- Story Intelligence core proven
    

**Status:** Completed

---

#### Phase 3 — Neuro-Symbolic Architecture Transition (Current Phase)

**Objectives**

- Replace linear pipeline with Dynamic Event Graph
    
- Introduce event-centric reasoning
    

**Key Tasks**

- Implement graph schema
    
- Integrate KuzuDB
    
- Add structured event extraction
    

**Exit Criteria**

- Persistent event graph operational
    

**Priority Level:** Highest

---

#### Phase 3.1 — Graph-Based Reasoning Enhancement

**Objectives**

- Replace count-based importance scoring
    

**Tasks**

- Implement centrality metrics
    
- Validate against annotated dataset
    

**Exit Criteria**

- Character ranking accuracy measurable
    

---

#### Phase 4 — Knowledge Stabilization

**Objectives**

- Integrate wiki generator with graph runtime
    

**Tasks**

- Expand canonical memory structure
    

**Exit Criteria**

- Canon wiki generated from graph queries
    

---

#### Phase 5 — Multimodal Output Integration

**Objectives**

- Add audio synthesis
    

**Implementation Order**

1. Edge-TTS
    
2. Piper
    
3. StyleTTS2
    

**Exit Criteria**

- Voice assigned to main characters
    

---

#### Phase 6 — Experimental Evaluation & Publication Preparation

**Objectives**

- Run comparative experiments
    
- Produce reproducible metrics
    

**Deliverables**

- Experimental results
    
- Draft research paper
    

---

#### Phase 7 — Final Submission & Demonstration

**Objectives**

- Complete documentation
    
- Prepare demonstration workflow
    

---

### 3. High-Level Timeline (Indicative)

_(Adjust durations based on remaining academic calendar.)_

|Phase|Duration|Output|
|---|---|---|
|Phase 3|4–6 weeks|Dynamic Graph Runtime|
|Phase 3.1|2–3 weeks|Centrality-based graduation|
|Phase 4|2 weeks|Graph-driven Wiki|
|Phase 5|1–2 weeks|Audio demo|
|Phase 6|3–4 weeks|Experimental validation|
|Phase 7|Final weeks|Submission package|

---

### 4. Milestone Schedule

|Milestone|Deliverable|
|---|---|
|M1|Graph schema finalized|
|M2|KuzuDB integration complete|
|M3|Event extraction operational|
|M4|Centrality ranking validated|
|M5|Canon wiki fully automated|
|M6|Experimental metrics collected|
|M7|Research paper draft complete|
|M8|Final demo system ready|

---

### 5. Roles and Responsibility (Single-Developer Scenario)

**Primary Developer (You)**

- Architecture design
    
- Implementation
    
- Experimentation
    
- Documentation
    

**Mentor**

- Technical review
    
- Research validation
    
- Publication guidance
    

---

### 6. Progress Tracking Mechanism

- Weekly milestone review
    
- Version-controlled repository
    
- Experiment logs per iteration
    

**Artifacts Maintained**

- Architecture revision history
    
- Experiment records
    
- Change log
    

---

### 7. Risk Monitoring Plan

|Risk|Monitoring Method|Response|
|---|---|---|
|Event extraction inaccuracies|Evaluation metrics|Model adjustment|
|Graph complexity|Performance profiling|Schema optimization|
|Time constraints|Weekly milestone check|Scope reduction to MPS|

---

### 8. Definition of Phase Completion

Each phase is considered complete when:

- Documented deliverables exist
    
- System functionality is demonstrable
    
- Results are reproducible
    

---

### 9. Transition to Productization (Optional Path)

If extended beyond academic submission:

- Replace research APIs with optimized local models
    
- Add UI layer
    
- Introduce automated pipeline orchestration
    

---

You now have a **complete, professionally structured documentation chain** from problem definition → architecture → state → roadmap → research → management.

If you want to go one level higher in polish, I recommend one more artifact.

Say **“next”** and I will produce **Document 7 — System Requirements Specification (SRS)** formatted the way external examiners and IEEE-style reviews expect.