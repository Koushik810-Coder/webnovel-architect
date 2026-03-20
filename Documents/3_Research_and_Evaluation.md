# Research and Evaluation

## Research Methodology, Evaluation Design, and Publication Outline


## 1. Research Methodology

The research methodology follows a **Neuro-Symbolic** approach, designed to address the "Casting Paradox" in serialized web fiction (inability to determine character importance proactively) and the "Temporal Hallucination" problem inherent in standard LLM Retrieval-Augmented Generation (RAG).

### 1.1 The Neuro-Symbolic Paradigm
*   **Neural Component (The Eye):** Utilizes Large Language Models (LLMs) via the `litellm` adapter (currently **Groq API** as primary, **Gemini Flash** as fallback) to parse unstructured natural language. Its sole responsibility is structured extraction (Named Entity Recognition, dialogue classification, and Alias Resolution).
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
*   **Internal Validity:** LLM extraction is subject to platform variation (e.g., Groq vs Gemini). The `spaCy` fallback provides a deterministic baseline to mitigate this API-based volatility.

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


---

## Testing_Report


## 1. Test Input Data

Both testing pipelines were provided with the exact same dummy text block designed to evaluate noise filtering and context-sensitive entity recognition:

```text
The sun set over the horizon. Beware of the shadows!
John walked into the tavern, looking for Lady Elara. 
Suddenly, Vael'Thar the ancient wizard appeared. 
"This is Zelithra Moonfall's domain," he proclaimed loudly.
No one expected a King to arrive like this.
There were Many people, but Only the Same few spoke.
The first day was peaceful. Last night was a nightmare.
He became a Tier-3 Mage after consulting the Inner Disciple.
They traveled from the Upper Realm to join the Azure Cloud Sect.
```

## 2. Expected Results

Based on the input data, the expected core extractions (minus noise) are:

- **Expected Names:** `John`, `Elara`, `Vael'Thar`, `Zelithra Moonfall`
- **Expected World Terms:** `Tier-3 Mage`, `Inner Disciple`, `Upper Realm`, `Azure Cloud Sect`
- **Expected Noise Filtered:** `The`, `Beware`, `This`, `No`, `There`, `Many`, `Only`, `Same`, `first day`, `last night`

---

## 3. Test Cases and Outputs

### Case A: `test_extraction.py` (spaCy NER)

**Engine:** `en_core_web_sm` with custom `EntityRuler` patterns.

**Response Output:**
```python
Extracted Names: ['Elara', 'John', 'Upper Realm', "Vael'Thar", 'Zelithra Moonfall']
Extracted World Terms: ['Azure Cloud Sect', 'Inner Disciple', 'Tier-3 Mage']
```

**Evaluation & Rating:**
- **Rating:** **Moderate (3/5)**
- **Pros:** Correctly identified complex names like `Vael'Thar` and `Zelithra Moonfall` without capturing the genitive `'s`. Successfully discarded all capitalization-based noise words (`Many`, `Only`, `Same`, `Beware`).
- **Cons:** Misclassified `Upper Realm` into the `Names` category rather than `World Terms`, leading to an assertion failure in our strictest test evaluation: `FAILED: Missing expected world terms: {'Upper Realm'}`.
- **Verdict:** Highly efficient but requires continuous refinement of rule-based location/rank patterns versus strict person names.

### Case B: `test_llm_extraction.py` (LiteLLM)

**Engine:** LiteLLM using `Gemini Flash`.

**Response Output:**
```python
Extracted Names: ['Elara', 'John', "Vael'Thar"]
Extracted World Terms: ['Azure Cloud Sect', 'Inner Disciple', 'King', 'Tier-3 Mage', 'Upper Realm', "Zelithra Moonfall's domain", 'tavern']
Dialogue Count: 1
```

**Evaluation & Rating:**
- **Rating:** **Very Good (4.5/5)**
- **Pros:** Perfect categorization of `Upper Realm` into `World Terms`. Accurately counts dialogue interactions. Captured the core characters without failing on noise words.
- **Cons:** The LLM's generative nature caused it to merge `Zelithra Moonfall` into a broader world term representation: `"Zelithra Moonfall's domain"`. Additionally, it captured generic objects/ranks like `King` and `tavern` as distinct world terms.
- **Verdict:** Much stronger contextual reasoning than spaCy, handling locations and terminology significantly better, although it can be occasionally overly verbose in its world-building feature extractions.

---

## 4. Conclusion

The dual-pipeline structure fits our project requirements perfectly. The **LLM pipeline** provides the dominant and most contextually accurate extraction performance necessary for rich Story Intelligence. The **spaCy pipeline** stands as an effective, deterministic, and free fallback option requiring only slight tuning to rule definitions to prevent location misclassification. Use LLM structure extraction automatically during the Ingestion phase for most robust results.

---

## 5. Phase 6 Quantitative Evaluation

As of Phase 6 (March 2026), a formal automated evaluation harness (`scripts/evaluate.py`) has been implemented to measure the system against the *Minimum Publishable System (MPS)* targets outlined in the review decks.

The system was evaluated against a manually annotated Gold Standard dataset (`dataset/gold_standard.json`).

### 5.1 Final Evaluation Metrics

| Metric | Target | Result | Status |
| :--- | :--- | :--- | :--- |
| **Entity Precision / Recall (LLM)** | Recall ≥ 80% | F1 = 100%, Recall = 100% | **PASS** |
| **Graph Traversal Latency** | < 500 ms (1,000 nodes) | ~11.5 ms | **PASS** |
| **TTS Real-Time Factor (RTF)** | RTF < 1.0 (faster than live) | ~0.081 | **PASS** |
| **Character Importance Rank (Spearman ρ)**| ρ ≥ 0.70 | ρ = 0.800 | **PASS** |

### 5.3 Ingestion & DEU Verification (March 2026)

**Module:** `tests/test_scrapers.py` & `tests/test_extraction_deu.py`

| Test Case | Method | Status | Notes |
| :--- | :--- | :--- | :--- |
| **RoyalRoad Scraper Extraction** | BeautifulSoup Mock | ✅ **PASS** | Correctly pulls Title and Chapter Text |
| **RoyalRoad Index Parsing** | BeautifulSoup / Table parse | ✅ **PASS** | Retrieves full chapter list from Fiction URL |
| **EPUB Parser** | ZipFile / XML parse | ✅ **PASS** | Correct reading order and text extraction |
| **DEU Schema Validation** | Gemini 2.5 JSON | ✅ **PASS** | Logic verifies presence of pre_conditions, post_conditions, and location |

### 5.4 Conclusion
The system successfully meets all quantitative metrics and functional verification paths for the Phase 8 milestone. The multi-modal output (Audio + VTT + Wiki) is structurally sound and validated against real-world webnovel content.


---

