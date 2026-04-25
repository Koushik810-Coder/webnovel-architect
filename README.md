# Webnovel Architect: Zero-GPU Story Intelligence
**Version: Phase 7 PoC Final**

This repository contains the Proof-of-Concept for a Neuro-Symbolic Dynamic Graph-RAG system designed for Serialized Fiction Audio Synthesis.

## CORE ARCHITECTURE
* **Neural Layer**: Semantic entity extraction via Llama-3.1-8b (API).
* **Symbolic Layer**: Local temporal reasoning via NetworkX (CPU).
* **Audio Broker**: Proactive voice assignment based on Temporal PageRank.

## EVALUATION SUITE
* `/scripts/simulate_decay.py`: Longitudinal temporal ablation engine.
* `/scripts/evaluate.py`: End-to-end performance & F1 extraction metrics.
* `/scripts/generate_mos_survey.py`: Double-blind audio panel randomization.

## BENCHMARKS
* **Character Entity Recall**: 100%
* **Graph Traversal Latency**: 3.2 ms (1,000 nodes)
* **Real-Time Factor (RTF)**: <= 0.15

## Key Features

*   **Modular "Switchboard" Architecture**: Swap LLM providers and TTS engines easily via adapters.
*   **Dual Extraction Pipelines**: Utilizes both a LiteLLM-based structured extraction and a fallback spaCy NER pipeline.
*   **Event Extraction & Weighted Edges**: Automatically detects narrative events and assigns qualitative intensity weights (1-5) matching character involvement.
*   **Graph-Based Graduation**: Uses **Weighted PageRank** combined with **Temporal Decay** to determine "Main Character" status based on narrative centrality and recency.
*   **Algorithmic Bootstrapping**: Implements a **Debut Prominence Quotient (DPQ)** to dynamically assign provisional voices to character introductions without resorting to hardcoded limits.
*   **Interactive UIs**: Includes a fully-featured Streamlit user interface (`app_ui.py`) for dashboard tracking, plus a blinding **MOS Evaluator Dashboard** (`scripts/mos_eval_ui.py`) for human perceptual grading of generated audio.
*   **Zero-GPU Compatible**: Designed to run on standard laptops using lightweight models and API-based extraction.

## Getting Started

### Prerequisites
*   Python 3.9+
*   `pip install -r requirements.txt`
*   **Important**: You must download the spaCy model after installing dependencies:
    ```bash
    python -m spacy download en_core_web_sm
    ```

### Quick Start: Interactive UIs

#### 1. Professional Suite (Streamlit)
Ideal for developers and researchers to monitor the Knowledge Graph and debug extraction.
```bash
streamlit run app_ui.py
```

#### 2. End-User Experience (FastAPI + React)
The polished interface for reading and listening.

**Step A: Start Backend**
```bash
uvicorn app.main:app --reload
```

**Step B: Start Frontend**
```bash
cd web-ui
npm run dev
```

### Usage Guide
1. **Import a Novel**: Open the React UI (usually `localhost:5173`) and paste a RoyalRoad Fiction URL in the "Add New Novel" box.
2. **Background Ingestion**: The system will automatically scrape and begin extracting the first few chapters.
3. **Listen**: Select the novel in your Library, choose a chapter, and click "Play". The system will generate high-quality audio segments and sync them with captions in real-time.
4. **Research Tools**: Use the Streamlit dashboard (`app_ui.py`) to inspect the character relationship graph and graduation metrics.

## Architecture

### The Pipeline
1.  **Ingestion ("The Eye")**: Reads raw text and identifies dialogue and events.
2.  **Story Intelligence ("The Brain")**: Updates a network graph with new nodes (Characters, Events) and edges (Participation, Featured).
3.  **Graduation ("The Director")**: Calculates **PageRank** centrality. Characters above a threshold (e.g., 0.15) are "Graduated" to the Main Cast and assigned a unique Voice ID.
4.  **Synthesis ("The Voice")**: Generates audio using high-quality local TTS (Kokoro) or efficient online fallback (EdgeTTS).

## Project Structure
*   `adapters/`: Interface layers for LLM, Graph, and TTS.
*   `core/`: Business logic for Ingestion and Graduation.
*   `Documents/`: Detailed research reports and roadmaps.

## Current Status
*   **Phase**: Evaluation & Multimodal Integration (Phase 6 Completed)
*   **Latest Feature**: Streamlit UI Dashboard & Automated Evaluation Metric Harness (`scripts/evaluate.py`).
*   **Next Milestone**: Final Submission & Demonstration Showcase (Phase 7)
*   **Future Goal**: DyG-RAG based conversational chatbot for interacting with the story world

## Contributing
Please note that this is primarily a research and personal project. **We are not accepting exterior contributions lightly at this time.** If you have a major feature proposal or bug fix, please open an issue first to discuss it before submitting a pull request. Forking the project for your own experimentation is highly encouraged!
