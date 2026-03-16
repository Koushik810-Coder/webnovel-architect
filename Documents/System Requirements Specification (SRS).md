# Document 7: System Requirements Specification (SRS)

**Project Title:** Webnovel Architect — Neuro-Symbolic Story Intelligence System  
**Document Type:** Formal IEEE SRS Template Application  
**Version:** 1.0  

---

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
3.  **Ingestion ("The Eye") (L3):** Entity matching via `Gemini Flash` or `spaCy en_core_web_sm`.
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
*   **FR-01.2:** The system SHALL offer both an LLM-based and an offline deterministic (spaCy) extraction pipeline.
*   **FR-01.3:** The system SHALL identify unique character names and world-building terms.

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
