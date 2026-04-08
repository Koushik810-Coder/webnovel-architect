# Webnovel Architect: Future Ideas & Expansion Proposals

*These ideas were generated upon the successful completion of the Phase 7 Logic Roadmap and 100% test-suite validation.*

### Option 1: True "Story-World" Chatbot UI
Currently, the **Story Q&A** tab in the Streamlit UI is a simple "one question, one answer" text box. We could convert this into a continuous, interactive **Streamlit Chat Interface** (`st.chat_message`). 
* **Mechanics:** Build memory into the Streamlit session state and attach the RAG timeline extraction to an ongoing conversation.
* **Why it's cool:** It fully realizes the "Future Goal" stated in the README, letting users dynamically interrogate the story character-relationships (DyG-RAG) as if they were a historian having a fluid conversation inside the world.

### Option 2: The "Export & Package" Finalizer
Currently, chapters generate `.mp3` and `.vtt` chunks hidden in the `data/` directory.
* **Mechanics:** Build an **"Export Audiobook"** feature in the UI that stitches all chapter MP3s together using FFmpeg, binds the VTT files, and wraps them in a stylized HTML "Web Player" or downloadable ZIP.
* **Why it's cool:** It turns the "PoC" pipeline into a highly polished, distributable product you can immediately hand to someone to read and listen to natively.

### Option 3: Dockerization & Release Polish
If the codebase functionality is completely finalized for the showcase/submission, it needs to be made perfectly reproducible.
* **Mechanics:** Write a `Dockerfile` and `docker-compose.yml`, clean up the dependencies in `requirements.txt`, and finalize the `README.md` to be an exact step-by-step launch guide. 
* **Why it's cool:** Guarantees that whoever grades or evaluates the proof-of-concept can run the entire pipeline with a single `docker compose up` command, skipping Python virtual environment and spaCy installation headaches entirely.

---

### Additional Engine Optimizations (Cost / Speed)
*   **Persistent Local LLM Prompt Caching:** Implement SQLite/JSON caching in `llm_adapter.py`. Reprocessing identical text drops API costs to $0.00 and execution time to zero.
*   **Audio Generation Caching:** Hash `(voice_id + text)` for local disk caching. Repeated phrases during edge-TTS synthesis will skip the API entirely.
*   **Extraction Pre-filtering:** Use a lightweight keyword density window to slice only action-heavy paragraphs out of a chapter, sending a fraction of the raw chapter text to the LLM for intelligence extraction without missing events.
