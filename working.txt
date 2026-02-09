# Webnovel Architect - Project Working & Tech Stack (Zero-GPU Edition)

## 1. Vision & Core Philosophy
**"Turning evolving web novels into living audio dramas."**

Unlike traditional audiobooks which require a finished manuscript, this system reads along with the author, maintaining a persistent **"Story Intelligence"** layer that tracks character evolution, builds a living wiki, and assigns voices only when narrative importance is proven.

### The Problems We Solve
1.  **The Casting Paradox:** You cannot cast a character in Chapter 1 if you don't know if they'll matter in Chapter 50. We solve this with **Graduation**.
2.  **Wiki Decay:** Manual wikis are always out of date. We solve this with **Automated Story Intelligence**.

---

## 2. Architecture: "The Switchboard" (Modular Adapter Pattern)
The system uses a "Switchboard" architecture to decouple logic from specific models, allowing "Zero-GPU" operation on standard laptops while remaining future-proof for research labs.

### A. The Brain (LLM Interface)
*   **Tech:** `litellm` (Standardized wrapper for 100+ models).
*   **Current Model:** `Gemini Flash` (Fast/Free) or `Llama 3` (Local).
*   **Role:** Extracts dialogue, identifies speakers, and detects "Events" from raw text.

### B. The Memory (Reasoning Engine)
*   **Tech:** `networkx` (In-Memory Prototype) -> `Neo4j` (Planned).
*   **Methodology:** **dyG-RAG (Dynamic Graph RAG)**.
*   **Function:** Stores the story as a Directed Acyclic Graph (DAG) of **Events** and **Characters**. This allows "Event-Centric Reasoning" (understanding cause-and-effect) rather than just keyword matching.

### C. The Voice (TTS Interface)
*   **Tech:** `soundfile` + Custom Adapters.
*   **Tier 1 (Main Cast):** `kokoro-onnx` (82M parameters). High-fidelity, local neural TTS.
*   **Tier 2 (Background):** `edge-tts`. Free, online, efficient fallback.

---

## 3. The "Graduation" Algorithm
The system intelligently assigns resources using a specific "Importance Score" formula derived from Computational Narratology.

$$ Score = (w_1 \times GraphCentrality) + (w_2 \times EventImpact) + (w_3 \times Recency) $$

*   **Logic:**
    *   **Score > Threshold:** Character "Graduates" to **Main Cast**. A unique Voice ID is **LOCKED** forever.
    *   **Score < Threshold:** Character remains **Background**. Assigned a generic/random voice.

---

## 4. The Pipeline: Raw Text -> Graph -> Audio Book

### Phase 1: Ingestion (The "Eye")
*   **Input:** Raw Text Chapter.
*   **Action:** LLM Adapter analyzes text to extract **Dialogue** and **Events**.
*   **Output:** Structured JSON (`CharacterLine`, `EventNode`).

### Phase 2: Story Intelligence (The "Brain")
*   **Action:** Update the **NetworkX Graph**.
*   **Reasoning:** Link new Events to previous ones (Temporal Edges) and connect Characters to Events (Participation Edges).
*   **Result:** A "Living Memory" that understands context.

### Phase 3: Graduation (The "Director")
*   **Action:** Calculate the **Importance Score** using the Graph.
*   **Decision:** Assign Voice IDs based on the score.

### Phase 4: Synthesis (The "Voice")
*   **Action:** Route text to the appropriate TTS engine (Kokoro vs EdgeTTS).
*   **Output:** High-quality audio files (`output/001_Aria.wav`).

---

## 5. Research Basis
This architecture is aligned with state-of-the-art NLP research (2024-2025):
1.  **DyG-RAG (2025):** Event-Centric Modeling for long-term consistency.
2.  **BOOKCOREF (2025):** Handling book-scale entity tracking.
3.  **Audiobook-CC (2025):** Context-Aware prosody and emotion.
