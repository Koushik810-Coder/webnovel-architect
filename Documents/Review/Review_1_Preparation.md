# Major Project Review–1 Preparation Document
**Project Title**: Webnovel Architect — Neuro-Symbolic Story Intelligence System

---

## 1. Literature Survey (5 Marks)
**Objective**: Demonstrate research depth, existing models, and identify the research gap.

### Researched Papers (Recent & Reputed Sources)
1. **"DyG-RAG: Dynamic Graph Retrieval-Augmented Generation with Event-Centric Reasoning"** (Sun et al., 2025) - *arXiv*
2. **"From Local to Global: A Graph RAG Approach to Query-Focused Summarization"** (Edge et al., 2024) - *arXiv / Microsoft Research*
3. **"STAGE: Knowledge Graph Construction and Narrative Understanding"** (2024) - *arXiv*

### Comparison Table & Research Gap

| Feature / Model | Standard RAG | Static GraphRAG (Microsoft, 2024) | DyG-RAG Framework (2025 Base Paper) | Webnovel Architect (Proposed Implementation) |
| :--- | :--- | :--- | :--- | :--- |
| **Technique** | Vector-based similarity search | Static Graph construction + Community Detection | Dynamic Event Units (DEUs) + Event Graph | DyG-RAG + Neuro-Symbolic Switchboard architecture |
| **Understanding** | Fails at global temporal/context queries | Excellent for static, pre-indexed global context | Continuously evolving graph explicitly encoding time/events | Real-time graph evolution as chapters are read |
| **Limitations** | Context window limits, temporal ambiguity | Very high initial indexing cost, static memory | Focuses purely on temporal QA generation | Adds character importance (PageRank) for audio mapping |
| **Character Focus** | No explicit character logic | Entity groupings based on general text frequency | Event-centric sequence retrieval (Time-CoT) | PageRank + Temporal Decay to identify and voice "Main Cast" |

**Research Gap Identified**: 
While Static GraphRAG models handle fixed datasets well, they fail at continuous, evolving narratives. The **DyG-RAG** framework introduces dynamic event units for temporal reasoning, but there is still a gap in applying this to long-form **serialized Webnovels** with live narrative tracking. The Webnovel Architect extends DyG-RAG into a complete "Zero-GPU" system that not only answers queries but utilizes graph metrics to cast Audio drama characters automatically.

---

## 2. Base Paper Explanation (5 Marks)
**Primary Reference Paper**: *"DyG-RAG: Dynamic Graph Retrieval-Augmented Generation with Event-Centric Reasoning"* (Sun et al., 2025, arXiv:2507.13396)

* **Problem Addressed**: Existing Graph RAG methods struggle with temporal reasoning in evolving narratives due to an inability to model the fluid order and progression of real-world events over time.
* **Model Architecture**: An event-centric temporal reasoning pipeline:
  1. **Dynamic Event Units (DEUs)**: Encodes semantic content and precise temporal anchors.
  2. **Event Graph Construction**: Links DEUs that share entities and are close in time for multi-hop reasoning.
  3. **Event Timeline Retrieval Pipeline**: Traverses the graph in a time-aware manner to retrieve event sequences.
* **Algorithms/Strategies Used**: Time Chain-of-Thought (Time-CoT) strategy, Time-aware graph traversal.
* **Evaluation Metrics**:
  * Evaluated on temporal QA benchmarks (Accuracy and Recall).
  * Measured across three temporal reasoning types: chronological ordering, temporal proximity, and timeline-based relations.
* **Mathematical / Logic Flow**: Resolves temporal ambiguity using explicit temporal anchors and topological graph traversal rather than simple embedding proximity.
* **Dataset Used (Base Paper)**: Temporal Question Answering (QA) benchmarks and long-context documents.
* **Limitations of Base Paper**: The framework primarily targets QA answering and pure event retrieval, lacking specific adaptations for ongoing character-driven dramatic synthesis (like text-to-speech audio casting).
* **Scope for Improvement (Our Project)**: We improve upon the DyG-RAG base by introducing **Temporal Decay weighted PageRank** on top of the event graph. This allows us to use the event network not just for QA answering, but for real-time **Centrality scoring of characters** as new chapters arrive, actively mapping them to generated TTS voices.

---

## 3. Technical Architecture Design (5 Marks)
**Objective**: System design clarity and feasibility.

*(You should include your "Switchboard" and "User Pipeline" architecture diagrams here from `Pictures/Architechture diagram.png`)*

### System Modules & Data Flow
1. **Ingestion Engine ("The Eye")**: Takes raw text and uses **LiteLLM (Gemini Flash)** + **spaCy NER** fallback to extract entities and narrative events.
2. **Event Construction**: Formats the extracted text into formal Event schemas (`[Character] -> [PARTICIPATED_IN] -> [Event]`).
3. **Story Runtime / Graph ("The Brain")**: Instead of a vector DB, we use a **Dynamic Graph DB (NetworkX / KuzuDB)**. It maintains the persistent story knowledge and evolving relationships.
4. **Graduation System ("The Director")**: Uses graph reasoning to calculate the importance of characters via **PageRank Centrality** and **Temporal Decay**. If a character passes a threshold (e.g., 0.15), they are "graduated" to the Main Cast.
5. **Knowledge / Audio Output ("The Voice")**: Generates the interactive Markdown Wiki and uses the Switchboard to trigger Audio Synthesis (**Kokoro ONNX** for Main Cast, **Edge-TTS** for background).

**Justification**: We use a **Neuro-Symbolic** approach. LLMs (Neural) are great at extracting unstructured text, while Graphs (Symbolic) are perfect for deterministic reasoning, memory, and resolving hallucinations over long contexts.

---

## 4. Dataset Strategy (5 Marks)

* **Dataset Source**: Custom serialized webnovel transcripts and public domain stories. Segmented into chapter units.
* **Size Adequacy**: Tested on multi-chapter sequences to validate long-context retention and graph evolution.
* **Preprocessing & Cleaning**: Text is parsed to remove HTML/formatting, split into conversational and descriptive chunks, and fed into the dual-extraction pipeline. 
* **Data Flow / Handling**: Handled primarily as text which is transformed into structured JSON graph configurations.
* **Train-Test-Validation Split**: Divided chronologically. Dev set for testing extraction rules, Evaluation set to measure canonical inconsistency, Validation set to ensure accurate Character Importance ranking.
* **Ethical & Bias Consideration**: System relies strictly on local/API-based bounded generation to prevent unprompted generation. Content processed is restricted to publicly distributable or owned webnovel text.

---

## 5. Methodology & Tools (10 Marks)

### Technology Stack & Justification
* **Framework Selection**: 
  * *UI / Frontend*: **Streamlit** (Chosen for rapid dashboard prototyping and Python-native integration).
  * *Graph / Logic*: **NetworkX** for lightweight local graphs; **KuzuDB** for target scalability. (Chosen for relational depth).
  * *Extraction*: **LiteLLM** (Gemini Flash) with **spaCy** local fallback.
* **TTS (Deployment Tools)**: **Kokoro ONNX** (for local CPU performance) and **Edge-TTS** (Cloud API fallback).
* **Hardware Planning (Zero-GPU Strategy)**: The architecture utilizes a **"Switchboard Pattern"**, meaning the AI compute (LLM, TTS) is offloaded to APIs (Gemini) or optimized CPU inferences (ONNX), allowing this complex RAG system to run efficiently on standard student laptops.
* **Version Control**: GitHub for structured commits and managing "Neuro-Symbolic" iterations.

**Why this combination?**
Traditional ML flows require heavy GPUs for training. By utilizing pre-trained LLMs solely as extraction agents and moving the "reasoning" to a deterministically calculated Graph database, the proposed system minimizes hallucinations and hardware costs while maximizing narrative logic.
