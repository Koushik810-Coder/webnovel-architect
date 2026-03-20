# Requirements and Planning

## System Requirements Specification (SRS)


## 1. Introduction

### 1.1 Purpose
The purpose of this document is to clearly define the functional and non-functional requirements of the "Webnovel Architect" system. This document is intended as the primary technical reference for the development and evaluation phases.

### 1.2 Scope
Webnovel Architect is an open-source, Zero-GPU ingestion engine that processes serialized chapters of web fiction. It utilizes a Litellm/spaCy pipeline to extract events, models them dynamically in a Directed Acyclic Graph (DAG), calculates character centrality over time using PageRank, and dynamically casts Text-to-Speech (TTS) voices to high-importance characters to produce live audio dramas.

### 1.3 Target Audience
1.  **Readers / Listeners:** Users consuming an ongoing webnovel who desire an immersive, auto-updating audio drama format.
2.  **Authors / Editors:** Writers seeking to maintain a consistent "Story Bible" or canonical Character Wiki without manual data entry.

---

## 2. Overall Description

### 2.1 Product Perspective
Webnovel Architect acts as an intermediary "middleware" between raw text generation (the author publishing a chapter) and final content delivery (audio generation). It is built as a self-contained local Python application deployed via Streamlit.

### 2.2 System Architecture
The system employs a 5-Layer "Switchboard" Architecture:
1.  **Presentation (L1):** Interactive `app_ui.py` Streamlit Dashboard.
2.  **Switchboard (L2):** Adapter layer routing requests to available LLM/TTS resources.
3.  **Ingestion ("The Eye") (L3):** Entity matching and alias resolution via `Groq`/`Gemini Flash` or `spaCy en_core_web_sm`.
4.  **Story Runtime ("The Brain") (L4):** In-memory and persistent JSON DAG (`networkx`).
5.  **Graduation ("The Director") (L5):** Evaluation of metrics (PageRank/Decay) and execution of audio generation (`Kokoro ONNX` / `EdgeTTS`).

### 2.3 Operating Environment
*   **OS:** Windows, macOS, Linux
*   **Runtime:** Python 3.9+ installed natively.
*   **Hardware Constraint ("Zero-GPU"):** The core innovation is that the system must operate entirely on standard consumer CPUs without requiring discrete graphical processing hardware.

---

## 3. Specific Requirements

### 3.1 Functional Requirements

#### FR-01: Ingestion Engine
*   **FR-01.1:** The system SHALL accept raw string text representing a novel chapter.
*   **FR-01.2:** The system SHALL offer both an LLM-based (Groq/Gemini) and an offline deterministic (spaCy) extraction pipeline.
*   **FR-01.3:** The system SHALL identify unique character names and world-building terms, resolving aliases where context permits.
*   **FR-01.4 (Scraper):** The system SHALL support auto-fetching chapters from Fiction Index URLs.
*   **FR-01.5 (EPUB):** The system SHALL support parsing and ingesting chapters from EPUB files.

#### FR-02: Knowledge Graph
*   **FR-02.1:** The system SHALL maintain a chronological DAG of extracted entities against story chapters.
*   **FR-02.2:** The system SHALL recalculate a character’s "Importance Score" upon any graph update.
*   **FR-02.3:** The system SHALL apply Temporal Decay such that older event participation deprecates over time.

#### FR-03: Character Graduation & Wiki
*   **FR-03.1:** The system SHALL promote a character to the "Main Cast" if their Importance Score breaches a configurable threshold ($0.15$).
*   **FR-03.2:** Upon "Graduation," the system SHALL lock a persistent TTS Voice ID to that character profile.
*   **FR-03.3:** The system SHALL autogenerate a Markdown-formatted Character Wiki document reflecting current graph state.

#### FR-04: Audio Generation
*   **FR-04.1:** The system SHALL synthesize provided dialogue using the character's designated Voice ID.
*   **FR-04.2:** The system SHALL execute audio synthesis locally (`kokoro-onnx`) or fall back to an online edge API if constraints demand it.
*   **FR-04.3:** The system SHALL generate synchronized WebVTT subtitles for on-screen text highlighting during playback.
*   **FR-04.4 (Caching & Fallback):** The system SHALL chunk texts for script extraction, apply cross-LLM failover (e.g., Groq to Gemini), and cache generated audiobook scripts to minimize API overhead.

---

### 3.2 Non-Functional Requirements

#### NFR-01: Performance Constraints
*   **NFR-01.1 (Latency):** Graph traversal and PageRank calculation for up to 1,000 nodes MUST execute in under $500 ms$.
*   **NFR-01.2 (Real-Time Factor):** Audio synthesis MUST execute faster than real-time ($RTF < 1.0$).

#### NFR-02: Reliability
*   **NFR-02.1 (Switchboard Fallback):** If an LLM extraction pipeline fails (e.g. rate limit), the system MUST gracefully fall back to the local `spaCy` NER model without breaking the ingestion timeline.

#### NFR-03: Maintainability
*   **NFR-03.1 (Isolation):** Individual webnovel datasets MUST be wholly contained within their own `data/[UUID]` isolate. Deleting the folder entirely resets the narrative state.

---

## 4. Evaluation and Verification
Implementation of these requirements is measured and verified dynamically by the Phase 6 `scripts/evaluate.py` test framework:
*   FR-01 validation via Entity P/R/F1.
*   FR-02/FR-03 validation via Spearman Rank Correlation ($>0.70$).
*   NFR-01 validation via explicit Latency and RTF checks integrated into the CI/CD test suite.


---

## Project Management Plan, SDLC Model, Timeline, and Milestone Schedule


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

#### Phase 3 — Neuro-Symbolic Architecture Transition (COMPLETED)

**Objectives**

- Replace linear pipeline with Dynamic Event Graph
    
- Introduce event-centric reasoning
    

**Key Tasks**

- Implement graph schema
    
- Integrate KuzuDB
    
- Add structured event extraction
    

**Exit Criteria**

- Persistent event graph operational
    

**Status:** Completed (Feb 2026)

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

#### Phase 4 — Knowledge Stabilization (Current Phase)

**Objectives**

- Integrate wiki generator with graph runtime
    

**Tasks**

- Expand canonical memory structure
    

**Exit Criteria**

- Canon wiki generated from graph queries
    

**Status:** Completed

---

#### Phase 5 — Interactive UI Dashboard (COMPLETED)

**Objectives**

- Provide a central data hub for monitoring features and outputs.
    

**Implemented Components**

- Streamlit Web UI Dashboard
- Character Wiki Viewer
- Ingestion and Generation Interfaces

**Status:** Completed

---

#### Phase 6 — Multimodal Output Integration & Evaluation (COMPLETED)

**Objectives**

- Add audio synthesis
- Run comparative experiments
- Produce reproducible metrics
    

**Deliverables**

- Experimental results
    
- Draft research paper
    

**Status:** Completed

---

#### Phase 7 — Final Submission & Demonstration (Current Phase)

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

---

