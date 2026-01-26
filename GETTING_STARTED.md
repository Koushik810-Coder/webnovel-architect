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
To see the entire pipeline in action (Ingestion -> Extraction -> Graduation), run the included verification script:

```bash
python verify_system.py
```

**What happens:**
1.  Ingests Chapter 1 (detects Characters "Aria" and "Thorne").
2.  Creates Wiki files in the `./wiki/` directory.
3.  Simulates Chapter 2 updates.
4.  **Graduates** "Aria" to Main Cast and assigns a Voice ID.
5.  Prints Pass/Fail results.

### Option B: Run the API Server
To start the full backend server:

```bash
uvicorn app.main:app --reload
```
The API will be available at `http://localhost:8000`.
You can view the interactive Swagger docs at `http://localhost:8000/docs`.

---

## 3. How It Works: The Pipeline

Webnovel Architect turns text into structured data using a 4-step pipeline:

### Step 1: Ingestion (`app/services/ingest.py`)
-   **Input**: Raw text of a chapter.
-   **Action**: Calls the Extraction Service.
-   **Goal**: Don't just save text; understand it.

### Step 2: Extraction (`app/services/extraction.py`)
-   **Method**: Uses NLP (currently Regex heuristics) to identify:
    -   **Entities** (Proper Nouns like "Aria").
    -   **Dialogue** (Quotes).
-   **Logic**:
    -   Filters out noise (mentions < threshold).
    -   Counts dialogue lines per character.

### Step 3: Story Intelligence Update (`app/core/models/`)
-   **Runtime Model** (`character_runtime.py`):
    -   Updates `confidence_score` (Presence + Dialogue).
    -   Updates `mention_count`.
-   **Canon Model** (`character_wiki.py`):
    -   If the character is new, a `.md` file is created in `wiki/`.
    -   Humans can edit this file text; the system respects existing IDs.

### Step 4: Graduation & Voice Locking (`app/core/graduation.py`)
-   **Trigger**: After every update, `check_graduation_status()` runs.
-   **Threshold**: If `confidence_score > 0.75` (Main Cast):
    -   **Voice Assignment**: The system asks `VoiceAssignmentService` for a voice.
    -   **Locking**: The `voice_id` is saved to Runtime. It will strictly be used for all future TTS generation.

## Directory Structure
-   `app/api/`: FastAPI route handlers (endpoints).
-   `app/core/`: Core business logic (Graduation, Models).
-   `app/services/`: "Heavy lifting" (Ingest, Extraction, Wiki IO).
-   `wiki/`: Generated markdown files for characters.
