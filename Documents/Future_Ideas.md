# Webnovel Architect: Future Ideas & Expansion Proposals

*Consolidated from Phase 7 completion notes and architectural gap analysis. Ranked by combined Easiness × Impact.*

---

## Legend

| Symbol | Meaning |
|--------|---------|
| 🟢 | Easy — < 1 day, ≤ 4 existing files touched |
| 🟡 | Medium — 1–3 days, requires a new module |
| 🔴 | Hard — major infra rewrite or new service dependency |
| ⭐ | Improves accuracy or reasoning quality |
| 🎭 | Unlocks a new user-facing feature |
| 💰 | Reduces LLM / compute cost |
| 🐛 | Fixes a known architectural flaw |

---

## Phase 1 — Quick Wins *(< 1 day each)*

### 1.1 Dual-Timeline Fields on Events
**Easiness: 🟢🟢🟢 · Impact: ⭐⭐⭐**

The graph stores events with only a `chapter_id`. Flashbacks, dreams, and rumours are treated identically to present-timeline events — causing Time-CoT RAG to reason incorrectly about chronology in non-linear narratives. Five fields fix this entirely:

| Field | Type | Purpose |
|---|---|---|
| `timeline_type` | `str` | `present \| flashback \| memory \| dream \| rumor \| imagined` |
| `narrative_order` | `int` | Scene's position *within* the chapter (1, 2, 3…) |
| `story_time_rank` | `int \| null` | Relative position in actual chronology; `null` if ambiguous |
| `story_time_relative` | `str \| null` | Fallback for ambiguous events: `"before major_event_X"` |
| `flashback_depth` | `int` | `0` = present, `1` = flashback, `2` = flashback-within-flashback |

The `narrative_order` vs `story_time_rank` split is the key insight: a flashback has a high `narrative_order` (it appears late in the chapter) but a low `story_time_rank` (it happened long ago in-universe). When the LLM cannot determine a rank with confidence, `story_time_rank` is left `null` and `story_time_relative` is used instead (e.g. `"before the siege of Westhold"`), preserving the temporal relationship without forcing a wrong integer.

`flashback_depth` handles nested flashbacks — a character remembering a childhood memory *during* a current flashback — which `timeline_type` alone cannot express.

**Retrieval rule:** Use `story_time_rank` for causal questions (*"why did X happen?"*); use `narrative_order` for reader-experience questions (*"when was it revealed?"*).

**What to add:**
- All five fields on event nodes in `graph_adapter.py` → `add_event()`
- Extend the LLM extraction prompt (`extraction.py`) to produce all five per event
- Pass through `ingest.py`
- Surface `timeline_type` + `flashback_depth` in `rag.py` timeline strings; sort by `story_time_rank` (nulls last)

**Files:** `extraction.py`, `graph_adapter.py`, `ingest.py`, `rag.py` (~50 lines total)

---

### 1.2 Spoiler & Canonicity Fields on Events
**Easiness: 🟢🟢🟢 · Impact: ⭐⭐ 🎭**

Foundation for the entire Spoiler System (Phase 2.3) and unreliable narration support. Two fields enable this:

| Field | Type | Purpose |
|---|---|---|
| `reveal_point` | `int` | Chapter at which this event becomes safe for a reader (0 = immediate) |
| `spoiler_level` | `int` | `0` = safe, `1` = mild spoiler, `2` = major twist |
| `is_canonical` | `bool` | `False` for events a character imagines, lies about, or misremembers |
| `confidence` | `float` | LLM-estimated certainty (0.0–1.0); low confidence = unreliable narration |

The `spoiler_level` field enables finer control than a binary hide/show: a spoiler-free summary can hint at level-1 spoilers while fully suppressing level-2 twists.

**What to add:**
- All four fields on event nodes in `graph_adapter.py` → `add_event()`
- Extraction prompt: add all four to the event schema
- Pass through `ingest.py`

**Files:** `extraction.py`, `graph_adapter.py`, `ingest.py` (~25 lines total)

---

### 1.3 Persistent LLM Prompt Cache
**Easiness: 🟢🟢🟢 · Impact: 💰💰**

Implement SQLite or JSON caching in `llm_adapter.py` keyed on a hash of `(prompt + model)`. Reprocessing identical chapter text — common during debugging and re-ingestion — drops API cost to $0.00 and latency to near zero.

**Files:** `adapters/llm_adapter.py` only

---

### 1.4 Audio Generation Cache
**Easiness: 🟢🟢 · Impact: 💰**

Hash `(voice_id + text_chunk)` and store output `.mp3` fragments on disk. Repeated phrases (narration intros, common dialogue patterns) skip the TTS engine entirely on re-synthesis.

**Files:** `adapters/tts_adapter.py`, `app/services/audiobook_generator.py`

---

### 1.5 Extraction Pre-filtering
**Easiness: 🟢🟢 · Impact: 💰 ⭐**

Use a lightweight keyword-density window (action verbs, dialogue markers) to slice only event-heavy paragraphs from a chapter before sending to the LLM. Reduces token usage per chapter by an estimated 30–50% without missing meaningful events.

**Files:** `app/services/extraction.py` (add a `_prefilter_text()` helper)

---

### 1.6 Character Role on Event Edges
**Easiness: 🟢🟢 · Impact: ⭐⭐**

Currently, character-to-event edges store only `relation_type` (e.g. `friendly`, `hostile`). A richer `role` field on the edge — tracking *how* a character was involved — enables much more precise RAG retrieval and wiki summaries.

**Valid roles:** `protagonist`, `antagonist`, `witness`, `cause`, `victim`, `bystander`

Example query this unlocks: *"Show me all events where Alice was a victim"* — a pure graph traversal, no LLM needed.

**What to add:**
- `role` field on `Character → Event` edges in `graph_adapter.py` → `add_event()`
- Extraction prompt: add `"character_roles": {"Alice": "victim", "Ravi": "cause"}` to the event schema
- Pass through `ingest.py`

**Files:** `extraction.py`, `graph_adapter.py`, `ingest.py` (~25 lines total)

---

### 1.7 Dynamic Threshold Scaling *(fixes PageRank Dilution)*
**Easiness: 🟢🟢 · Impact: ⭐⭐ 🐛**

**Known flaw:** As the graph expands across hundreds of chapters, raw PageRank scores converge toward zero. The current static graduation threshold (`0.50`) becomes mathematically unreachable for late-series characters, silently preventing main-cast voice assignment.

**Fix:** Replace the static threshold with a dynamically scaling formula:

$$M_{\text{threshold}} = M_{\text{base}} \times \frac{1}{N}$$

where $N$ is total node count. This keeps casting behaviour consistent regardless of serial length.

**Files:** `app/core/graduation.py` (update `DELTA_UPPER` / threshold calculation)

---

### 1.8 Conditional Fixer Pass
**Easiness: 🟢🟢 · Impact: ⭐⭐ 💰**

Currently, the extraction pipeline never goes back to fix ambiguous results. Adding a lightweight trigger check after graph-building lets a second, focused LLM call correct *only* the broken parts — without re-processing the entire chapter.

**Trigger conditions** (all detectable deterministically — no LLM needed to decide):
- Conflicting `story_time_rank` ordering (a flashback ranked after its future event)
- Events with no assigned `timeline_type` (extraction failed to classify the scene)
- Two events with identical character sets and location within 2 narrative positions (likely duplicate)
- Characters detected by spaCy that were not found by the LLM (coverage gap)

**Fixer prompt strategy:** Pass only the flagged event JSON — not the full chapter text — to a cheap model. Instruct it to fix ordering, deduplicate, and correct flashback classification only.

**Files:** `app/services/ingest.py` (add `_check_fixer_triggers(events)` post-extraction), `app/services/extraction.py` (add `fix_events_pass(flagged_events)`) (~40 lines total)

---

### 1.9 Time-Aware Character Relationship Edges
**Easiness: 🟢🟢 · Impact: ⭐⭐⭐**

The current `add_or_update_character_edge()` stores only the **most recent** relation type between two characters, silently overwriting earlier states. This makes it impossible to track how a relationship evolved — one of the most important narrative signals in any novel.

**The problem:** After Chapter 3 `Alice → trusts → Ravi` and Chapter 8 `Alice → distrusts → Ravi`, the graph only remembers `distrusts`. The betrayal arc is invisible.

**Fix:** Store relationship snapshots as a list on the edge rather than overwriting, keyed by chapter:

```python
edge_data["relation_history"] = [
    {"chapter": 3, "relation": "trusts"},
    {"chapter": 8, "relation": "distrusts"}
]
```

This enables:
- *"How did Alice and Ravi's relationship change?"* — a pure graph read, no LLM retrieval
- Character arc wiki sections that show relationship evolution over time
- Arc detection heuristics (a shift from `trusts` → `distrusts` in N chapters is a strong betrayal arc signal)

**What to add:**
- `graph_adapter.py` → `add_or_update_character_edge()`: append to `relation_history` list instead of overwriting `relation_type`
- `rag.py`: when building the timeline for a character pair, sort `relation_history` by chapter and include the evolution
- `wiki.py` → relationship rendering: show a timeline of relation changes, not just the current state

**Files:** `graph_adapter.py`, `rag.py`, `wiki.py` (~30 lines total)

---

## Phase 2 — New Features *(1–3 days each)*

### 2.0 Scene Nodes as Intermediate Graph Layer
**Easiness: 🟡🟡 · Impact: ⭐⭐ ⭐**

Currently the graph goes directly from Chapter → Events, skipping the `Scene` layer. A scene is a natural chunking unit for novels — a continuous block of action in one location with one cast, before a time-jump or location change. Treating scenes as first-class nodes fixes two problems at once:

1. **Better chunking for RAG** — *"Chunk by scenes/narrative units, not tokens."* Novels rely on context continuity; token-based chunking breaks mid-scene and destroys reasoning context.
2. **Finer temporal resolution** — Events within a scene share location and cast; events across scenes have natural breaks for arc grouping.

**Graph schema addition:**
```cypher
(:Scene { id, chapter, location, summary })
(:Event)-[:OCCURS_IN]->(:Scene)
(:Scene)-[:IN_CHAPTER]->(:Chapter)
```

**What to add:**
- `graph_adapter.py`: `add_scene(scene_id, chapter_id, location, summary)` + `add_event_to_scene(event_id, scene_id)` methods
- Extraction prompt: add `"scene_id"` grouping to events — events sharing a continuous location/cast block get the same `scene_id`
- `ingest.py`: write scene nodes before events; link events to their scene
- `rag.py`: retrieve at scene granularity when query is location or cast-specific

**Files:** `graph_adapter.py`, `extraction.py`, `ingest.py`, `rag.py` (new `add_scene` method + prompt changes)

---

### 2.1 Sliding-Window Chapter Ingestion *(fixes Artificial Latency)*
**Easiness: 🟡🟡 · Impact: ⭐⭐ 🐛**

**Known flaw:** Processing chapters as strict atomic units creates context boundary issues. A scene split across two chapters can cause a character active at the boundary to unfairly accumulate temporal decay penalties mid-arc.

**Fix:** Replace the atomic chapter ingestion in `ingest.py` with a sliding-window strategy that maintains a rolling context buffer of the previous chapter's final N paragraphs, injecting them as context-only prefix into the next extraction call.

**Files:** `app/services/ingest.py`, `app/services/extraction.py`

---

### 2.2 Adaptive Model Routing
**Easiness: 🟡🟡 · Impact: 💰 ⭐**

The `llm_adapter.py` sends every extraction to the same model regardless of chapter complexity. Route dynamically:
- **Complex / ambiguous chapters** (high entity count, low coherence score) → remote API (Gemini / GPT-4o)
- **Straightforward chapters** (low entity count, clean dialogue structure) → local SLM via Ollama (Llama-3-8B)

This balances accuracy against API cost on a per-chapter basis.

**Files:** `adapters/llm_adapter.py`, `app/services/extraction.py`

---

### 2.3 Spoiler-Free & POV Wiki Filter
**Easiness: 🟡🟡 · Impact: ⭐⭐⭐ 🎭**

*Requires Phase 1.2 (`reveal_point` + `spoiler_level`) to be complete first.*

Once the spoiler fields exist on events, a filter layer produces three distinct wiki views from the **same** graph without duplicating data:

| Mode | Filter Logic |
|---|---|
| **Reader Mode** | Hide events where `reveal_point > reader_chapter` OR `spoiler_level == 2` |
| **God Mode** | No filter — full truth graph (current behaviour) |
| **Character POV** | Show only events the character `[:INVOLVED_IN]` or `[:KNOWS]→` |

**Critical design detail — LLM Spoiler Rewrite:**
Don't just *hide* filtered events — actively re-summarize visible events to be safe. A level-1 spoiler event should appear as a vague hint rather than being silently dropped:

> Full: *"Ravi betrays Alice in Chapter 18"*  
> Spoiler-Free: *"Ravi's actions later change Alice's trust in him"*

This rewrite pass uses a single cheap LLM call on the assembled wiki page, not per-event.

**`UNAWARE_OF` edges (complement to `KNOWS`):**
Explicitly track character ignorance — `(:Character)-[:UNAWARE_OF]->(:Event)` — so the POV filter can model dramatic irony (the reader knows something the character doesn't).

**What to build:**
- New `app/services/wiki_filter.py`: `get_filtered_events(story_uuid, mode, reader_chapter, pov_character_id)` + `rewrite_for_spoiler_free(wiki_text, filtered_event_ids)`
- `graph_adapter.py`: add `add_knowledge_edge(char_id, event_id, edge_type="knows"|"unaware_of")`
- `rag.py` → `query_story()`: accept `mode` + `reader_chapter`, pass through filter before building prompt
- `app_ui.py`: reader chapter progress slider + mode selector

**Files:** New `wiki_filter.py` + `graph_adapter.py` + `rag.py` + `app_ui.py`

---

### 2.4 Batched Arc Detection
**Easiness: 🟡🟡 · Impact: ⭐⭐⭐ 💰**

No arc concept exists anywhere in the codebase. Arcs are the semantic glue between isolated events — without them the wiki has no story structure (e.g. "The Tournament Arc", "The Betrayal Arc") and the graph is just a flat event list.

**What to build:**
- New `app/services/arc_detector.py`: `detect_arcs(story_uuid, every_n=5)` — clusters the most recent N chapters' events by location + participant overlap, sends a single batched LLM call, writes `Arc` nodes back to the graph
- `graph_adapter.py`: add `add_arc(arc_id, label, event_ids, chapter_start, chapter_end)` method
- `ingest.py`: after `save_runtime()`, trigger `if chapter_counter % 5 == 0: detect_arcs(story_uuid)`

**Files:** New `arc_detector.py` + `graph_adapter.py` + `ingest.py`

---

### 2.5 Location & Event Wiki Pages
**Easiness: 🟡🟡 · Impact: ⭐⭐ 🎭**

The wiki only generates character pages. The graph already stores `location` on every event — location pages are essentially a free aggregation query + one LLM summary call.

**What to build:**
- New `app/services/location_wiki.py`: `build_location_page(story_uuid, location_name)` — aggregates all events at that location, builds a timeline, LLM-generates a descriptive summary
- New `app/services/event_wiki.py`: `build_event_page(story_uuid, event_id)` — renders the event's full causal chain, participants with their **roles** (`protagonist`, `witness`, `cause`, `victim`), pre/post conditions, and narrative vs. story-time context as a wiki page
- Arc Wiki: `build_arc_page(story_uuid, arc_id)` — start event, escalation events, turning point, resolution, participating characters, emotional/thematic evolution (prompt template sourced directly from `chats.md`)
- `app_ui.py`: new "Locations", "Events", and "Arcs" tabs in the Wiki section

**Files:** New `location_wiki.py`, `event_wiki.py`, `arc_wiki.py` + `app_ui.py`

---

### 2.6a Wiki Page Versioning
**Easiness: 🟡 · Impact: ⭐ 💰**

*A natural companion to 2.5.* Wiki pages are currently regenerated from scratch on every enrichment call. Versioning enables cache invalidation: only regenerate a page if the underlying graph neighbourhood has changed since the last generation.

**What to add:**
```python
wiki_page_meta = {
    "version": 3,
    "generated_at": "2026-05-04T...",
    "graph_snapshot_id": "sha256:abc123"  # hash of relevant node+edge data
}
```
- Add `graph_snapshot_id` to `CharacterWiki` JSON sidecar
- Before calling `enrich_wiki_from_rag()`, compare current graph hash vs. stored hash — skip if unchanged
- Reduces redundant LLM calls significantly during batch re-enrichment

**Files:** `app/core/models/character_wiki.py`, `app/services/wiki.py`

---

### 2.7 Interactive Story-World Chatbot UI
**Easiness: 🟡🟡 · Impact: ⭐⭐ 🎭**

The current **Story Q&A** tab is a single text box with no memory. Convert it to a continuous `st.chat_message` interface with session-state conversation history attached to the DyG-RAG pipeline.

**Why it matters:** Fully realizes the "Future Goal" from the README — users can interrogate character relationships and plot threads as a fluid, multi-turn conversation rather than isolated one-shot queries.

**Files:** `app_ui.py` (chat tab refactor) + `app/services/rag.py` (session memory injection)

---

### 2.8 "Wiki as a Query Language"
**Easiness: 🟡🟡🟡 · Impact: ⭐⭐⭐ 🎭**

*The most powerful long-term direction from the chats.* Instead of navigating to a static character page, users type natural language graph queries that produce on-demand filtered wiki projections:

| Query | Graph Operation |
|---|---|
| *"Show me Alice before the betrayal"* | Filter character events by `story_time_rank < betrayal_event.story_time_rank` |
| *"Show Ravi from Alice's perspective"* | Intersect Ravi's events with Alice's `[:KNOWS]` edges |
| *"Show all hidden knowledge events"* | Filter events where `is_canonical = false` OR `spoiler_level = 2` |
| *"What is the full truth of this arc?"* | Arc node → all events with no filter (God Mode) |

All queries are graph traversals — no extra LLM call for retrieval, only for the final summary generation. The key enabler is having `story_time_rank`, `is_canonical`, `spoiler_level`, and `KNOWS`/`UNAWARE_OF` edges all populated (Phases 1.1, 1.2, 2.3).

**What to build:**
- `rag.py`: `query_story_with_filter(story_uuid, nl_query, mode, reader_chapter)` — adds a pre-retrieval intent-classification step that sets filter parameters before graph traversal
- `app_ui.py`: replace the plain query text box with a richer interface showing the active filter state

**Files:** `rag.py` + `app_ui.py` (+ depends on Phase 1.1, 1.2, 2.3)

---

### 2.9 Character POV Knowledge Edges *(if not covered by 2.3)*
**Easiness: 🟡🟡🟡 · Impact: ⭐⭐**

*Note: `add_knowledge_edge()` and `UNAWARE_OF` edges are now proposed as part of 2.3. This item covers the extraction-side work needed to **populate** those edges automatically.*

**What to add beyond 2.3:**
- Extraction prompt: add `"known_by": ["CharB"]` and `"unaware_of": ["CharC"]` to the event schema — for scenes where a character overhears, is told about, or is explicitly kept ignorant of an event
- `ingest.py`: call `graph.add_knowledge_edge(char_id, event_id, "knows")` and `graph.add_knowledge_edge(char_id, event_id, "unaware_of")` for each populated entry

**Files:** `extraction.py`, `ingest.py` (graph_adapter.py already updated in 2.3)

---

### 2.10 Export & Package Audiobook Finalizer
**Easiness: 🟡🟡 · Impact: 🎭**

Currently, chapters generate `.mp3` and `.vtt` chunks hidden in `data/`. Build an **"Export Audiobook"** feature that stitches all chapter MP3s via FFmpeg, binds the VTT subtitle files, and wraps them in a downloadable ZIP or stylized HTML Web Player.

**Why it matters:** Turns the pipeline from a proof-of-concept into a polished, distributable product.

**Files:** New `app/services/export.py` + `app_ui.py` (export tab)

---

## Phase 3 — Infrastructure Upgrades *(Defer)*

Each entry below includes a concrete **trigger condition** — the specific signal that makes the upgrade worth doing.

---

### 3.1 Decay Rate Optimization ($\lambda$ Ablation)
**Easiness: 🟡 · Impact: ⭐⭐ 🐛**

The current decay rate is $\lambda = 0.15$ (tuned on 5 chapters of *Mother of Learning*). Conduct longitudinal ablation studies across the full 73-chapter serial testing $\lambda \in \{0.05, 0.10, 0.15, 0.20\}$ to find the optimal global degradation curve.

**Trigger:** When expanding the evaluation corpus beyond 10 characters / 5 chapters.

---

### 3.2 Neo4j / Memgraph Knowledge Graph
**Easiness: 🔴 · Impact: ⭐⭐ (at scale)**

NetworkX + JSON files work well at current story sizes. Neo4j / Memgraph is warranted when the graph outgrows in-memory operation or when Cypher pattern-matching queries become necessary.

**Trigger:** Single story graph JSON exceeds ~50 MB, or graph query latency becomes noticeable in the UI.

---

### 3.3 Qdrant Vector Store
**Easiness: 🔴 · Impact: ⭐⭐**

Current RAG uses graph traversal (entity matching → neighbourhood retrieval). Qdrant enables semantic similarity search over dense chapter embeddings — needed for "find chapters similar to this scene" but unnecessary for the current entity-anchored Q&A.

**Trigger:** When implementing a "Similar Scenes" or full-text "Chapter Search" feature.

---

### 3.4 LangGraph State Machine Orchestration
**Easiness: 🔴 · Impact: 💰 (operational clarity)**

`ingest.py` is already a well-structured sequential pipeline. LangGraph adds retries, branching, DAG visualisation, and observability — valuable for production, but a full rewrite of a working system.

When implemented, the state machine maps cleanly to the pipeline already described:

```python
graph.add_node("extract", extract_events)        # 1 LLM call
graph.add_node("build_graph", build_graph_ops)   # no LLM
graph.add_node("resolve", resolve_entities)       # embeddings
graph.add_node("neo4j", write_to_neo4j)
graph.add_node("arc", detect_arcs)               # batched, conditional
graph.add_node("wiki_queue", queue_wiki_jobs)    # async

# Conditional arc detection — only if enough events
def should_detect_arcs(state):
    return len(state["events"]) > 5
graph.add_conditional_edges("neo4j", should_detect_arcs,
    {True: "arc", False: "wiki_queue"})
```

**Trigger:** When the pipeline needs parallel chapter processing across stories or retry/resume logic beyond the current `retries.py` mechanism.

---

### 3.7 Self-RAG / Corrective RAG (CRAG) Loop
**Easiness: 🔴 · Impact: ⭐⭐⭐**

The current RAG pipeline is a single-pass: retrieve → generate → done. Self-RAG and CRAG introduce a self-evaluation loop:

- **Self-RAG:** Generate answer → LLM evaluates its own correctness → re-retrieves if uncertain → refines answer
- **CRAG (Corrective RAG):** Retrieve → evaluate retrieval quality score → if poor, re-search or fall back to web/broader graph → answer

For story Q&A this is particularly valuable: if the retrieved events don't actually answer the question (wrong character, wrong chapter), the system catches this automatically rather than hallucinating.

**Minimal implementation path** (without full LangGraph):
- After `query_story()` generates a response, run a second cheap LLM call: *"Does this answer actually address the question? If not, what information is missing?"*
- If the self-check fails, widen the graph retrieval (more characters, broader chapter range) and regenerate
- Add a `max_retries=2` guard

**Trigger:** After the chatbot UI (2.7) is live and users start reporting non-answers or hallucinated responses.

---

### 3.5 Redis / RabbitMQ Background Job Queue
**Easiness: 🔴 · Impact: 💰**

`enrich_all_wikis_from_rag()` already exists and runs synchronously. True async job queues are only needed under concurrent multi-user load.

**Trigger:** When moving from single-user Streamlit to a multi-user FastAPI deployment.

---

### 3.6 Dockerization & Release Polish
**Easiness: 🔴 · Impact: 🎭**

Write a `Dockerfile` + `docker-compose.yml`, clean up `requirements.txt`, and finalize `README.md` as an exact step-by-step launch guide. Enables single-command reproducibility (`docker compose up`) — critical for graders or external evaluators who can't be expected to configure a Python virtualenv + spaCy model manually.

**Trigger:** When moving from single-user Streamlit to a multi-user FastAPI deployment.

---

### Summary Ranking Table

| # | Feature | Easiness | Impact | Phase |
|---|---------|----------|--------|-------|
| 1.1 | Dual-timeline fields (timeline_type, narrative_order, story_time_rank, depth, relative) | 🟢🟢🟢 | ⭐⭐⭐ | 1 |
| 1.2 | Spoiler & canonicity fields (reveal_point, spoiler_level, is_canonical, confidence) | 🟢🟢🟢 | ⭐⭐ 🎭 | 1 |
| 1.3 | Persistent LLM prompt cache | 🟢🟢🟢 | 💰💰 | 1 |
| 1.4 | Audio generation cache | 🟢🟢 | 💰 | 1 |
| 1.5 | Extraction pre-filtering | 🟢🟢 | 💰 ⭐ | 1 |
| 1.6 | Character role on event edges | 🟢🟢 | ⭐⭐ | 1 |
| 1.7 | Dynamic threshold scaling | 🟢🟢 | ⭐⭐ 🐛 | 1 |
| 1.8 | Conditional Fixer Pass | 🟢🟢 | ⭐⭐ 💰 | 1 |
| 1.9 | Time-aware relationship edges (relation history per chapter) | 🟢🟢 | ⭐⭐⭐ | 1 |
| 2.0 | Scene nodes as intermediate graph layer | 🟡🟡 | ⭐⭐⭐ | 2 |
| 2.1 | Sliding-window chapter ingestion | 🟡🟡 | ⭐⭐ 🐛 | 2 |
| 2.2 | Adaptive model routing | 🟡🟡 | 💰 ⭐ | 2 |
| 2.3 | Spoiler-free / POV wiki filter + LLM rewrite + UNAWARE_OF edges | 🟡🟡 | ⭐⭐⭐ 🎭 | 2 |
| 2.4 | Batched arc detection | 🟡🟡 | ⭐⭐⭐ 💰 | 2 |
| 2.5 | Location, Event & Arc wiki pages | 🟡🟡 | ⭐⭐ 🎭 | 2 |
| 2.6a | Wiki page versioning + cache invalidation | 🟡 | ⭐ 💰 | 2 |
| 2.7 | Story-world chatbot UI | 🟡🟡 | ⭐⭐ 🎭 | 2 |
| 2.8 | Wiki as a Query Language | 🟡🟡🟡 | ⭐⭐⭐ 🎭 | 2 |
| 2.9 | Character POV knowledge edge extraction | 🟡🟡🟡 | ⭐⭐ | 2 |
| 2.10 | Export & package audiobook | 🟡🟡 | 🎭 | 2 |
| 3.1 | Decay rate λ ablation | 🟡 | ⭐⭐ 🐛 | 3 |
| 3.2 | Neo4j / Memgraph migration | 🔴 | ⭐⭐ | 3 |
| 3.3 | Qdrant vector store | 🔴 | ⭐⭐ | 3 |
| 3.4 | LangGraph orchestration | 🔴 | 💰 | 3 |
| 3.5 | Redis / RabbitMQ job queue | 🔴 | 💰 | 3 |
| 3.6 | Dockerization & release polish | 🔴 | 🎭 | 3 |
| 3.7 | Self-RAG / CRAG self-correction loop | 🔴 | ⭐⭐⭐ | 3 |

---

## DyG-RAG Architecture: Strengths & Known Limitations

*Academic analysis from the Phase 7 evaluation.*

### Strengths

- **Resolution of the Casting Paradox:** The Debut Prominence Quotient (DPQ) successfully decouples speaker assignment from global narrative confirmation, allowing a protagonist-tier character to receive a dedicated voice profile immediately upon their debut.
- **Elimination of Temporal Hallucination:** Standard vector RAG systems fail on narrative latency. The DyG-RAG engine solves this by applying a timed-decay PageRank formulation ($\lambda = 0.15$) to a Directed Acyclic Graph, correctly dropping inactive characters below the activity threshold.
- **Zero-Local-GPU Efficiency:** By delegating temporal logic to a local, deterministic symbolic runtime (NetworkX), the system avoids the "LLM Tax." Decay lookups across 1,000 nodes execute in under 4 ms on consumer-grade CPU hardware.
- **High Extraction Accuracy:** The neural layer, backed by LiteLLM (llama-3.1-8b), achieves 100% Character Entity F1 for semantic extraction.

### Known Limitations

- **Global PageRank Dilution** *(fixed by 1.6)*: As the graph expands, raw PageRank scores converge toward zero. The static graduation threshold (`0.50`) eventually becomes mathematically unreachable for late-series characters.
- **Artificial Narrative Latency** *(fixed by 2.1)*: Strict atomic chapter ingestion creates context boundary issues — a scene split across two chapters can unfairly penalise a character mid-arc.
- **Small Evaluation Scale:** The current corpus covers only 5 chapters and 10 characters from *Mother of Learning*. Generalising to 100+ chapter serials requires longitudinal validation *(see 3.1)*.
- **spaCy Fallback Vulnerability:** The LLM fallback path (spaCy NER) drops the combined F1 score to 46.0%, revealing heavy quality dependence on remote API availability.
