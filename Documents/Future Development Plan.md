# Future Development Plan — Webnovel Architect

> **Status**: Active Development  
> **Last Updated**: February 2026  
> **Current Phase**: Phase 5 (UI) — Complete

---

## Completed Phases

| Phase | What | Status |
|-------|------|--------|
| Phase 1 | Core ingestion pipeline, Chapter model | ✅ Done |
| Phase 2 | Character runtime, Graduation algorithm | ✅ Done |
| Phase 3 | Graph-based runtime (NetworkX / KuzuDB) | ✅ Done |
| Phase 4 | Voice Registry, TTS adapter, persistence | ✅ Done |
| Phase 5 | Streamlit Web UI Dashboard | ✅ Done |

---

## Upcoming Sprints

### Sprint 1 — spaCy NER Integration ⭐ *Recommended Next*

**Goal**: Replace the regex-based word extractor with a proper Named Entity Recognition model.

**Why**: The current extraction captures common English words as characters (e.g., `the.md`, `beware.md`). spaCy corrects this by tagging only `PERSON` entities—CPU-only, free, and fast.

**Tasks**:
- Add `spacy` and `en_core_web_sm` to dependencies
- Rewrite `app/services/extraction.py` to use `doc.ents` filtered to `PERSON` label
- Handle multi-word spans (e.g., "Lord Stark", "Old Man")

**Effort**: Low | **Impact**: High

---

### Sprint 2 — Temporal Weighting in the Graph

**Goal**: Make character importance time-aware, not just count-based.

**Why**: A character appearing 20 times 100 chapters ago should rank lower than one appearing 5 times in the last 3 chapters.

**Tasks**:
- Store `chapter_id` on each graph edge
- Add a decay multiplier to confidence score: `score *= (1 - decay_rate) ^ chapters_ago`
- Expose a "recency weight" slider in the Dashboard UI

**Effort**: Medium | **Impact**: High

---

### Sprint 3 — Alias Resolution

**Goal**: Merge "Elara", "Lady Elara", and "the young mage" into one character entity.

**Why**: A serialized novel uses many referring expressions for the same person. Without this, each alias spawns a separate wiki entry.

**Tasks**:
- Implement fuzzy string matching between candidate names
- Use a lightweight sentence embedding model (`sentence-transformers` CPU tier) for semantic deduplication
- Surface merge suggestions in the UI for author review

**Effort**: High | **Impact**: Very High

---

### Sprint 4 — LLM-Powered Structured Extraction

**Goal**: Replace all heuristics with a single structured LLM call per chapter.

**Why**: `litellm` + Gemini Flash (already configured in `config.yaml`) can return JSON-structured character, event, and relationship data in one pass—far more accurate than regex.

**Tasks**:
- Write a prompt template: "Extract characters, events, and relationships from the following chapter. Return as JSON."
- Parse the response with Pydantic validation
- Use this as the primary path in `extraction.py`, keep regex as fallback

**Effort**: Medium | **Impact**: Very High

---

### Sprint 5 — Full Audio Chapter Rendering

**Goal**: Render an entire chapter as a complete audio drama with per-character voices.

**Why**: The TTS adapter and Voice Registry are complete; the final step is dialogue attribution and audio stitching.

**Tasks**:
- Attribute each line of dialogue to its speaker using NER + context window
- Render each line with the correct voice via the TTS adapter
- Stitch clips into a single WAV/MP3 using `pydub`
- Add a "Render Chapter Audio" button in the UI

**Effort**: High | **Impact**: Very High — Core project showcase feature

---

## Recommended Priority Order

```
Sprint 1: spaCy NER      →  Low effort, immediately improves quality
Sprint 4: LLM Extraction →  Medium effort, replaces ALL heuristics at once
Sprint 2: Temporal Decay →  Medium effort, smarter graduation
Sprint 3: Alias Resolve  →  High effort, real-world readiness
Sprint 5: Full Audio     →  High effort, showcase deliverable
```

---

## Long-Term Vision

- **REST API**: Expose the pipeline as a FastAPI service (`POST /ingest`, `GET /characters`, `GET /audio/{id}`)
- **Epub/PDF Reader**: Direct ingestion from `.epub` files instead of manual paste
- **Web Reader Integration**: Embed character cards and audio in a reader experience
- **Multi-Language Support**: Swap NER and TTS models per locale
