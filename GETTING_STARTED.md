# Getting Started with Webnovel Architect

This guide will help you set up the project locally and understand the core "Story Intelligence" pipeline.

## Prerequisites

-   **Python 3.9+**
-   **pip** (Python package manager)

## 1. Installation

Clone the repository and set up your environment:

```bash
# Clone the repo (if using git)
# git clone <your-repo-url>
# cd webnovel-architect

# Create a virtual environment (Optional but Recommended)
python -m venv venv
# Windows
.\venv\Scripts\activate
# Mac/Linux
# source venv/bin/activate

# Install Dependencies
pip install -r requirements.txt
```

## 2. Running the System

### Option A: Run the Verification Script (Quick Start)
To see the entire Neuro-Symbolic pipeline in action (Ingestion -> Event Extraction -> Graph PageRank -> Graduation), run the modular verification script:

```bash
python verify_modular.py
```

**What happens:**
1.  Ingests Chapter 1 text.
2.  **Extracts Events**: Identifies narrative events (e.g., "Aria confronts Thorne") and dialogue.
3.  **Updates Graph**: Adds characters and events to the `story_graph.json`.
4.  **Calculates Importance**: Runs **PageRank** to determine who matters.
5.  **Graduates**: Assigns Voice IDs to characters with PageRank > 0.15.
6.  **Synthesizes**: Generates audio using Kokoro (or EdgeTTS).

### Option B: Run the API Server
To start the full backend server:

```bash
uvicorn app.main:app --reload
```
The API will be available at `http://localhost:8000`.
You can view the interactive Swagger docs at `http://localhost:8000/docs`.

---

## 3. How It Works: The Pipeline

Webnovel Architect turns text into audio using a 4-step Neuro-Symbolic pipeline:

### Step 1: Ingestion ("The Eye")
-   **Input**: Raw text of a chapter.
-   **Action**: Calls LLM (via `adapters/llm_adapter.py`) to extract:
    -   **Dialogue**: Spoken lines.
    -   **Events**: Narrative beats (e.g., "Battle at the Gate").

### Step 2: Story Intelligence ("The Brain")
-   **Structure**: Directed Acyclic Graph (DAG) managed by `adapters/graph_adapter.py`.
-   **Updates**:
    -   Nodes: Characters, Events.
    -   Edges: Character <-> Event (Participation).

### Step 3: Graduation & Voice Locking ("The Director")
-   **Method**: **PageRank Centrality**.
-   **Logic**:
    -   If `PageRank(character) > 0.15`: Graduate to **Main Cast**.
    -   Assign specific Voice ID (locked for consistency).

### Step 4: Synthesis ("The Voice")
-   **Engine**: Selectable via `config.yaml` (Kokoro, EdgeTTS, etc.).
-   **Output**: High-quality audio for Main Cast, fast audio for background.

## Directory Structure
-   `app/api/`: FastAPI route handlers (endpoints).
-   `app/core/`: Core business logic (Graduation, Models).
-   `app/services/`: "Heavy lifting" (Ingest, Extraction, Wiki IO).
-   `wiki/`: Generated markdown files for characters.
