# Webnovel Architect — Neuro-Symbolic Story Intelligence

> **Turning evolving web novels into living audio dramas using Dynamic Graph RAG (DyG-RAG).**

> [!IMPORTANT]
> **What this is NOT:** This is not a collaborative writing app, word processor, or plotting software. It is an ingestion engine designed to parse existing webnovel chapters and automatically generate interactive wikis and living audio dramas.

## Overview

The **Webnovel Architect** is a "Zero-GPU" modular system designed to process ongoing serial stories. Unlike traditional audiobooks which require a finished manuscript, this system reads along with the author, maintaining a persistent **"Story Intelligence"** layer that tracks character evolution and events.

It uses a **Neuro-Symbolic** approach:
1.  **Neuro**: LLMs (e.g., Gemini Flash) for text analysis and event extraction.
2.  **Symbolic**: A Directed Acyclic Graph (DAG) for reasoning, memory, and character importance scoring.

## Key Features

*   **Modular "Switchboard" Architecture**: Swap LLM providers and TTS engines easily via adapters.
*   **Event Extraction**: Automatically detects narrative events and links them to characters.
*   **Graph-Based Graduation**: Uses **PageRank** to determine "Main Character" status based on narrative centrality, not just line counts.
*   **Zero-GPU Compatible**: Designed to run on standard laptops using lightweight models and API-based extraction.

## Getting Started

### Prerequisites
*   Python 3.9+
*   `pip install -r requirements.txt`
*   **Important**: You must download the spaCy model after installing dependencies:
    ```bash
    python -m spacy download en_core_web_sm
    ```

### Quick Verification
Run the verification script to test the entire pipeline (Ingestion -> Extraction -> Graph -> Graduation -> TTS):

```bash
python verify_modular.py
```

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
*   **Phase**: Voice Management System Implemented (Phase 4 Completed)
*   **Latest Feature**: VoiceRegistry, Deterministic Assignment, and Wiki Persistence
*   **Next Milestone**: Advanced Audio Engine & Polish (Phase 5)
*   **Future Goal**: DyG-RAG based conversational chatbot for interacting with the story world

## Contributing
Please note that this is primarily a research and personal project. **We are not accepting exterior contributions lightly at this time.** If you have a major feature proposal or bug fix, please open an issue first to discuss it before submitting a pull request. Forking the project for your own experimentation is highly encouraged!
