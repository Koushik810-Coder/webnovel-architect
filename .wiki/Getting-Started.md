# 🚀 Getting Started

> **Prerequisites:** Python 3.9+ | Git | A free API key from [Groq](https://console.groq.com) or [Google AI Studio](https://aistudio.google.com)

---

## 1. Clone the Repository

```bash
git clone https://github.com/Koushik810-Coder/webnovel-architect.git
cd webnovel-architect
```

---

## 2. Create Virtual Environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

> **Note:** The spaCy model download is required for the offline NER fallback pipeline.

---

## 4. Configure API Keys

Create a `.env` file in the project root:

```env
# Primary LLM (Groq — free tier, fast)
GROQ_API_KEY=gsk_your_key_here

# Fallback LLM (Google Gemini — free tier)
GEMINI_API_KEY=AIza_your_key_here

# Optional: Multiple Groq keys for rotation (bypasses rate limits)
GROQ_API_KEY_1=gsk_key_one
GROQ_API_KEY_2=gsk_key_two
```

---

## 5. Configure `config.yaml`

```yaml
llm_model: "groq/llama-3.1-8b-instant"   # Primary extraction model
fallback_llm: "gemini/gemini-1.5-flash"   # Fallback if Groq fails
tts_engine: "kokoro"                       # Main cast TTS (local CPU)
fallback_tts: "edge"                       # Background TTS (cloud)
```

> **Tip:** If you don't have Kokoro ONNX files, change `tts_engine: "edge"` to run fully cloud-based.

---

## 6. (Optional) Download Kokoro TTS Model

For high-quality local TTS synthesis (main cast voices), download:
- `kokoro-v0_19.onnx` — The Kokoro ONNX neural TTS model
- `voices.json` — Voice profile definitions

Place both files in the project root. Without these, the system falls back to EdgeTTS automatically.

---

## 7. Launch the Application

### Option A: Streamlit Dashboard (Recommended for first use)

```bash
streamlit run app_ui.py
```

Opens at `http://localhost:8501` — full dashboard with ingestion, graph viewer, wiki browser, and audio generation.

### Option B: FastAPI + React UI (End-user experience)

**Terminal 1 — Backend:**
```bash
uvicorn app.main:app --reload
```

**Terminal 2 — Frontend:**
```bash
cd web-ui
npm install
npm run dev
```

Opens at `http://localhost:5173` — polished reading + listening interface.

---

## 8. Ingest Your First Chapter

### Via Streamlit UI:
1. Open the **Ingestion Engine** tab
2. Paste a RoyalRoad fiction URL (e.g., `https://www.royalroad.com/fiction/12345/my-story`)  
   **or** upload a `.epub` file  
   **or** paste raw chapter text
3. Click **"Ingest Chapter"**
4. Watch the **Knowledge Graph** tab populate in real time

### Via Python API:
```python
from app.services.ingest import ingest_chapter

story_uuid = "my-story-001"
chapter_text = open("chapter1.txt").read()
result = ingest_chapter(story_uuid, chapter_text, chapter_id=1)
print(f"Extracted {len(result['characters'])} characters, {len(result['events'])} events")
```

---

## 9. Generate Audio

In the Streamlit **Audio Generation Hub** tab:
1. Select your story from the dropdown
2. Choose a chapter
3. Click **"Generate Audiobook"**
4. Download the resulting `.mp3` + `.vtt` subtitle file

---

## Common Issues

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: spacy` | Run `pip install -r requirements.txt` |
| `en_core_web_sm not found` | Run `python -m spacy download en_core_web_sm` |
| `AuthenticationError: Groq` | Check your `GROQ_API_KEY` in `.env` |
| Kokoro audio not generating | The ONNX model files are missing; set `tts_engine: "edge"` in `config.yaml` |
| `RuntimeError: event loop already running` | This is handled automatically via the async bridge in `audiobook_generator.py` |

---

*→ Next: [System Architecture](System-Architecture)*
