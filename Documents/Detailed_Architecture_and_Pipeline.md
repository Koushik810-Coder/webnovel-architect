# Webnovel Architect: Detailed Architecture & User Pipeline

**Version:** 1.0  
**Date:** 2026-02-09  
**Status:** Architecture Definition

---

## 1. Executive Summary

The **Webnovel Architect** is a **Neuro-Symbolic Story Intelligence System** designed to function on consumer hardware ("Zero-GPU"). It evolves static text into a living, queryable world.

The system relies on two core architectural innovations:
1.  **The Switchboard Pattern (Zero-GPU Architecture):** A modular adapter system that allows heavy AI components (LLM, TTS, Database) to be swapped based on available hardware (e.g., swapping OpenAI API for a local quantized Llama model).
2.  **DyG-RAG (Dynamic Graph RAG):** A narrative memory system that builds a knowledge graph *as the story progresses*, allowing for accurate retrieval of past events and character relationships.

---

## 2. High-Level Architecture: The "Switchboard"

The core philosophy is strict separation between **Narrative Logic** (The Application) and **AI Compute** (The Provider). The "Switchboard" acts as the central router, connecting the logic to the best available tool for the job.

### 2.1 Component Diagram

```mermaid
%%{init: {
  "flowchart": {
    "useMaxWidth": true,
    "nodeSpacing": 20,
    "rankSpacing": 40,
    "padding": 5
  },
  "themeVariables": {
    "fontSize": "12px"
  }
}}%%
graph TD
    subgraph "Core Application (The Logic)"
        direction TB
        Orchestrator[Story Orchestrator]
        Ingest[Ingestion Engine]
        Director[Director / Graduation]
        Wiki[Wiki Generator]
    end

    subgraph Switchboard ["The Switchboard (Router)"]
        direction TB
        SB[Switchboard Router]
    end

    subgraph Adapters ["Adapters (Interchangeable)"]
        direction TB
        LLM[LLM Adapter]
        TTS[TTS Adapter]
        Graph[Graph DB Adapter]
    end

    subgraph Providers ["Providers (External)"]
        direction TB
        OpenAI["OpenAI /<br/>Groq API"]
        LocalLLM["Local Ollama /<br/>Llamacpp"]
        Piper["Piper TTS<br/>(Local)"]
        StyleTTS["StyleTTS2<br/>(GPU)"]
        Kuzu["KuzuDB<br/>(Embedded)"]
        Neo4j["Neo4j<br/>(Server)"]
    end

    Orchestrator --> SB
    SB -- "Text Gen" --> LLM
    SB -- "Audio" --> TTS
    SB -- "Knowledge" --> Graph

    LLM -.-> OpenAI
    LLM -.-> LocalLLM
    TTS -.-> Piper
    TTS -.-> StyleTTS
    Graph -.-> Kuzu
    Graph -.-> Neo4j

    classDef core fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef switch fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,stroke-dasharray: 5 5;
    classDef adapter fill:#e0f2f1,stroke:#00695c,stroke-width:2px;
    classDef provider fill:#f3e5f5,stroke:#8e24aa,stroke-width:1px;
    
    class Orchestrator,Ingest,Director,Wiki core;
    class SB switch;
    class LLM,TTS,Graph adapter;
    class OpenAI,LocalLLM,Piper,StyleTTS,Kuzu,Neo4j provider;
```

### 2.2 Visual Prompts for Presentation

![Modular 'Zero-GPU' Architecture: Swap Intelligence Providers without breaking the Story Logic.](Pictures/Architechture%20diagram.png)

*Figure 1: Modular 'Zero-GPU' Architecture - A central Switchboard connecting interchangeable AI providers.*

---

<div style="page-break-after: always;"></div>

## 3. End-to-End User Pipeline

The user pipeline transforms a raw text file (chapter) into a fully realized audio drama experience with a supporting wiki.

### 3.1 Pipeline Stages

1.  **Ingestion ("The Eye")**: Reading text, identifying entities, and extracting "Candidate Events".
2.  **Graph Construction ("The Brain")**: Inserting events into the KuzuDB graph and linking them to existing characters.
3.  **Reasoning ("The Director")**: Running PageRank/Centrality algorithms to decide which characters are important enough to get a unique voice ("Graduation").
4.  **Synthesis ("The Voice" & "Memory")**: Generating the Wiki pages and synthesizing Audio for the graduated characters.

### 3.2 Sequence Diagram

```mermaid
%%{init: {
  "sequence": {
    "useMaxWidth": true,
    "diagramMarginX": 10,
    "diagramMarginY": 10,
    "messageMargin": 10,
    "mirrorActors": false,
    "bottomMarginAdj": 10,
    "showSequenceNumbers": true
  },
  "themeVariables": {
    "fontSize": "12px",
    "fontFamily": "arial"
  }
}}%%
sequenceDiagram
    participant User
    participant Eye as Ingestion<br/>(Eye)
    participant SB as Switchboard
    participant Brain as Runtime Graph<br/>(Brain)
    participant Director as Graduation<br/>(Director)
    participant Output as Wiki/Audio

    User->>Eye: Upload Text
    Eye->>SB: Request Entities
    SB->>Brain: Query Context (RAG)
    Brain-->>Eye: Return Context
    Eye->>Eye: Extract Events
    Eye->>Brain: Commit Events
    
    Brain->>Director: Trigger Check
    Director->>Brain: Get Centrality
    Brain-->>Director: Return Scores
    Director->>Director: Promote (if > threshold)
    
    Director->>Output: Update Wiki
    Director->>SB: Request Audio
    SB->>Output: Gen Audio Files
    Output-->>User: Deliver Wiki & Audio
```

### 3.3 Visual Prompts for Presentation

![From Raw Text to Living World: The Neuro-Symbolic Pipeline](Pictures/Pipeline.png)

*Figure 2: The Neuro-Symbolic Pipeline - From raw text input to multi-modal output (Wiki & Audio).*

---

<div style="page-break-after: always;"></div>

## 4. Subsystem Details

### 4.1 Ingestion Engine ("The Eye")
*   **Goal:** Turn unstructured text into structured data.
*   **Laptop Mode:** Uses Regex and spaCy (runs on CPU).
*   **Zero-GPU Mode:** Uses remote APIs (Groq/OpenAI) via Switchboard for high-accuracy extraction without local hardware.
*   **Research Mode:** Uses local Llama-3 for maximum privacy and control.

![Ingestion Visual: Digital eye scanning text](Pictures/Ingestion%20Visual.png)

*Figure 3: Ingestion Engine ("The Eye") - Scanning text to extract entities with confidence scores.*

### 4.2 Dynamic Graph Runtime ("The Brain")
*   **Goal:** Remember everything.
*   **Tech:** KuzuDB (Embedded, default) or Neo4j (Server, visualization).
*   **Data Model:** `(Character)-[PARTICIPATED_IN]->(Event)-[NEXT]->(Event)`.

![Dynamic Graph Runtime Visual](Pictures/Graph%20visual.png)

*Figure 4: Dynamic Graph Runtime ("The Brain") - 3D network graph representing narrative memory.*

### 4.3 Graduation System ("The Director")
*   **Goal:** Resource allocation defined by narrative importance.
*   **Algorithm:** 
    *   *Background Characters* = No Voice (Text only).
    *   *Supporting Characters* = Standard Voice (Piper/Edge-TTS).
    *   *Main Cast* = High Quality Voice (StyleTTS2/XTTS).
*   **Logic:** As a character's "Centrality" (connections) increases in the graph, they "Graduate" tiers.



---

<div style="page-break-after: always;"></div>

## 5. Technology Stack & Deployment Tiers

The system supports three distinct hardware profiles via the Switchboard.

| Tier | Extraction Strategy | Runtime Memory | Audio Synthesis |
| :--- | :--- | :--- | :--- |
| **Research Lab**<br>*(High-End GPU)* | **xCore / Llama-3 (FP16)**<br>Local, high-precision extraction. | **Neo4j Enterprise**<br>Visual, server-based graph. | **StyleTTS2 / XTTS**<br>Studio-quality voice (requires VRAM). |
| **Laptop**<br>*(Consumer CPU)* | **spaCy**<br>Fast, rule-based extraction. | **KuzuDB**<br>Embedded, local graph file. | **Piper (ONNX)**<br>Fast, medium-quality offline TTS. |
| **Zero-GPU**<br>*(Cloud Dependent)* | **LLM API (OpenAI/Groq)**<br>Offloaded intelligence. | **KuzuDB**<br>Embedded, local graph file. | **Edge-TTS / API**<br>Cloud-based synthesis. |
