# Document 5: Research Methodology, Evaluation Design, and Publication Outline

**Project Title:** Webnovel Architect — Neuro-Symbolic Story Intelligence System  
**Document Version:** 1.0  
**Date:** 2026-03-15  

---

## 1. Research Methodology

The research methodology follows a **Neuro-Symbolic** approach, designed to address the "Casting Paradox" in serialized web fiction (inability to determine character importance proactively) and the "Temporal Hallucination" problem inherent in standard LLM Retrieval-Augmented Generation (RAG).

### 1.1 The Neuro-Symbolic Paradigm
*   **Neural Component (The Eye):** Utilizes Large Language Models (LLMs) via the `litellm` adapter (currently Gemini Flash) to parse unstructured natural language. Its sole responsibility is structured extraction (Named Entity Recognition and dialogue classification).
*   **Symbolic Component (The Brain):** Utilizes a Directed Acyclic Graph (DAG) built with `networkx` to represent the chronological ontology of the story. Entities (Characters) and Events are discrete nodes connected by directional edges (`participant`, `featured`).

### 1.2 Algorithmic Foundation: PageRank + Temporal Decay
To automate the classification of "Main Line Cast" versus "Background Characters", the system utilizes a modified PageRank centrality algorithm over the event graph. 

Because webnovels are serialized chronologically, raw PageRank overvalues characters who appeared frequently early on but were subsequently written out of the narrative. To solve this, a **Temporal Decay Mechanism** is applied:

$$ Score = PageRank(Node) \times (1 - \lambda)^{\Delta t} $$

Where:
*   $\lambda$ is the Temporal Decay Rate (dynamically adjustable via UI, default $0.05$).
*   $\Delta t$ is the difference between the most recent ingested chapter and the character's last known event occurrence. 

This ensures that only characters with both high narrative centrality *and* high recency graduate to the main voice-acted cast.

---

## 2. Evaluation Design (Phase 6 Harness)

To empirically validate the system, a formal quantitative evaluation harness was built (`scripts/evaluate.py`). The evaluation measures four specific dimensions of system performance against a manually annotated Gold Standard dataset.

### 2.1 Metric Definitions

| Metric Name | Purpose | Target Threshold | Method |
| :--- | :--- | :--- | :--- |
| **Entity Extraction (F1)** | Evaluates the Neural layer's ability to identify relevant entities without hallucinations. | $Recall \ge 80\%$ | Compares parsed Character/World Terms against `dataset/gold_standard.json` annotations using Precision, Recall, and F1 formulas. |
| **Graph Traversal Latency** | Evaluates the Symbolic layer's efficiency at scale (Zero-GPU bounds). | $< 500 ms$ | Synthetic graph generation (10 to 1,000 nodes). Wall-clock time of `get_character_importance()` execution. |
| **TTS Real-Time Factor (RTF)** | Evaluates the feasibility of live audio drama generation. | $RTF \le 1.0$ | Time taken to synthesize audio divided by the length of the resulting audio file. Target must be faster than real-time. |
| **Spearman Rank Correlation** | Evaluates the accuracy of the Graduation algorithm versus human perception. | $\rho \ge 0.70$ | Correlates the algorithm's continuous `confidence_score` ranking against a discrete human-ranked ground truth ordinal list. |

### 2.2 Threats to Validity
*   **Construct Validity:** The Gold Standard dataset currently relies on a single chapter annotation. Future work requires cross-annotator agreement on a larger corpus.
*   **Internal Validity:** LLM extraction is subject to platform variation (e.g., Gemini vs GPT-4o). The `spaCy` fallback provides a deterministic baseline to mitigate this API-based volatility.

---

## 3. Recommended Publication Outline

This project is structured to meet the criteria for a conference paper submission in the domain of Computational Narratology or Applied AI. 

### Title Ideas
*   *Zero-GPU Story Intelligence: Dynamic Graph RAG for Serialized Fiction Audio Synthesis*
*   *Solving the Casting Paradox: Neuro-Symbolic Character Prominence Scoring in Evolving Narratives*

### Proposed Section Breakdown

1.  **Abstract:** Summary of the Casting Paradox, the dyG-RAG solution, and the zero-GPU constraint.
2.  **Introduction:** 
    *   The rise of serialized web fiction.
    *   Failures of standard RAG models regarding temporal narrative states.
    *   Our contribution: A modular, real-time audio dramatization engine.
3.  **Related Work:**
    *   Standard GraphRAG (Microsoft, 2024).
    *   DyG-RAG (Sun et al., 2025) and its QA-focus limitations.
    *   Audiobook-CC (2025) prosody models.
4.  **System Architecture (The Switchboard):**
    *   Layer 1: Neural Extraction (LLM + NER fallback).
    *   Layer 2: Symbolic Runtime (Dynamic Event Graph).
    *   Layer 3: The Graduation Algorithm (PageRank + Decay).
5.  **Experimental Evaluation:**
    *   Detailed reporting of the 4 metrics (Entity F1, Latency, RTF, Spearman Rank).
6.  **Case Study:** Walkthrough of a 5-chapter ingestion demonstrating a character graduating from "Unknown" to "Main Cast" and locking a TTS Voice ID.
7.  **Conclusion & Future Work:** Discussion on expanding the graph to infer narrative causality and multi-agent interaction.
