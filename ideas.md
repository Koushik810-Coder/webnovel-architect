# Webnovel Architect: Core Ideas & Architecture

Based on the conversations in `chats.md` and integrating principles from the `conversation-memory` workflow, here is a condensed document of the core ideas, concepts, and architectures for the Webnovel Architect project.

## 1. Advanced RAG & Memory Paradigms

**The shift from Old RAG to Cutting-Edge RAG:**
- Move away from simple "one query → one retrieval → one answer" setups.
- Adopt **Agentic RAG**, **Graph RAG**, and **Self-Correcting RAG** pipelines.
- **Two-Level Memory System:**
  1. **Raw Memory (Graph/Vector):** The exact events, structured truths, and source text.
  2. **Wiki Memory (Derived):** The LLM-generated summaries, explanations, and narratives based on the raw memory. 

*This dual-layer approach aligns perfectly with robust conversation-memory principles, preventing hallucinations while still allowing high-level abstraction.*

---

## 2. The Dual-Timeline Model

Novels are not strictly chronological. A simple chronological chunking approach breaks down with flashbacks.

- **Narrative Time:** The order in which events are presented to the reader (chapter-by-chapter).
- **Story Time:** The actual chronological order of events within the story's universe.
- **Mechanism:** Treat absolute time as relative ordering (`Event A happens BEFORE Event B`). Tag events with `timeline_type` (e.g., present, flashback, memory, dream, rumor).

---

## 3. Dynamic Wiki Builder (Wiki as a Graph Projection)

Instead of maintaining static markdown documents for wiki pages, treat the wiki as **dynamic projections** of the underlying knowledge graph. 

- **Source of Truth:** The Neo4j Knowledge Graph.
- **Wiki Pages:** Generated on-demand or asynchronously (lazy generation) using LLM summaries of graph neighborhoods.
- **Page Types:**
  - **Character Pages:** Timeline of events, relationships, arc participation, hidden knowledge.
  - **Event Pages:** Causality chains, participants, consequences.
  - **Arc Pages (Semantic Grouping):** Start events, escalation, turning points, resolution.
  - **Location Pages:** Events and characters associated with a location.

---

## 4. Multi-View Narrative Database (Spoiler System)

Because the wiki is dynamically generated from the graph, you can apply visibility filters to create different "modes" from the same underlying data without duplicating information:

1. **Spoiler-Free Wiki (Reader Mode):** Filters out events where the `reveal_point` is greater than the reader's current chapter progress. LLMs rewrite summaries to hide future twists safely.
2. **Omniscient Wiki (God Mode):** No filtering. Shows the full event graph, all future events, hidden motivations, and complete causality chains.
3. **Character POV Wiki:** Filters the graph based on what a specific character knows (using `(:Character)-[:KNOWS]->(:Event)` edges).

---

## 5. Low-Cost Ingestion Pipeline

To avoid skyrocketing LLM API costs when ingesting hundreds of chapters, use a multi-step, batch-optimized pipeline:

1. **Cheap Extraction Pass (LLM):** A single LLM call per chapter using a smaller/cheaper model to extract atomic events into structured JSON. No reasoning, no arcs, just raw facts.
2. **Deterministic Graph Builder (Local):** Convert the extracted JSON into a Neo4j graph locally. Zero LLM cost.
3. **Lightweight Entity Resolution:** Batch-process entity deduplication using local embeddings (e.g., sentence-transformers) and cosine similarity.
4. **Optional Fixer Pass (LLM):** Only trigger an LLM correction pass when ambiguity or conflicts are detected (e.g., conflicting timelines).
5. **Arc Detection (Batched LLM):** Do not run arc detection per chapter. Run it every 5-10 chapters using clustering heuristics before sending to the LLM.
6. **Async Wiki Generation:** Queue wiki updates to run lazily in the background rather than blocking the ingestion pipeline.

---

## 6. LangGraph State Machine Implementation

The ingestion pipeline can be beautifully orchestrated using LangGraph to manage the state machine:
- **Node 1: Extract Events** (LLM cost center)
- **Node 2: Build Local Graph** (Deterministic)
- **Node 3: Resolve Entities** (Embeddings)
- **Node 4: Neo4j Upsert** (Database write)
- **Node 5: Detect Arcs** (Batched / Conditional edge)
- **Node 6: Queue Wiki Jobs** (Async tasks)

## 7. Recommended Stack

- **Vector/Semantic Search:** Qdrant
- **Knowledge Graph:** Neo4j
- **Orchestration / RAG:** LlamaIndex & LangGraph
- **API / Backend:** FastAPI
- **Background Jobs:** Redis / RabbitMQ / simple worker queues

---

## 8. Future Directions & Roadmap

> What's already built vs. what's missing — ranked by **Easiness × Impact**.
> Current stack: **NetworkX graph · JSON sidecars · LiteLLM · Streamlit**

### Legend
| Symbol | Meaning |
|--------|---------|
| 🟢 | Easy (< 1 day, 1–4 files) |
| 🟡 | Medium (1–3 days, new module) |
| 🔴 | Hard (major infra rewrite) |
| ⭐ | High impact on accuracy / UX |
| 💰 | Direct cost reduction |
| 🎭 | Unlocks a new user-facing feature |

---

### Phase 1 — Quick Wins (Do First)

#### 8.1 `timeline_type` on Events *(Idea #2)*
**Easiness: 🟢🟢🟢 · Impact: ⭐⭐⭐**

The graph stores events with only a `chapter_id`. Flashbacks, dreams, and rumours are currently treated identically to present-timeline events — causing the RAG Time-CoT to reason incorrectly about chronology.

**What to add:**
- `timeline_type: str = "present"` on every event node (values: `present`, `flashback`, `memory`, `dream`, `rumor`)
- Add `"timeline_type"` field to the LLM extraction prompt in `extract_chapter_intelligence_llm()`
- Pass it through `ingest.py` → `graph.add_event()`
- Surface it in `rag.py` timeline strings so the LLM sees `[FLASHBACK]` labels

**Files:** `extraction.py`, `graph_adapter.py`, `ingest.py`, `rag.py` (~30 lines total)

---

#### 8.2 `reveal_point` on Events *(Idea #4)*
**Easiness: 🟢🟢🟢 · Impact: ⭐⭐ 🎭**

Foundation for the entire Spoiler System. Every event needs a chapter number indicating when its knowledge becomes "safe" for readers. Without this field, spoiler-free mode cannot be built.

**What to add:**
- `reveal_point: int = 0` on event nodes (0 = revealed immediately, N = revealed at chapter N)
- LLM extraction: add `"reveal_point"` to the event schema — the model estimates whether the scene contains a twist or hidden truth and sets the chapter accordingly
- Pass through `ingest.py`

**Files:** `extraction.py`, `graph_adapter.py`, `ingest.py` (~20 lines total)

---

### Phase 2 — New Features (High Value)

#### 8.3 Spoiler-Free & POV Wiki Filter *(Idea #4)*
**Easiness: 🟡🟡 · Impact: ⭐⭐⭐ 🎭**

*Requires 8.2 to be done first.* Once `reveal_point` exists, a filter layer can produce three distinct wiki views from the same graph without duplicating data:

1. **Reader Mode** — hides events where `reveal_point > reader_chapter`
2. **God Mode** — no filter (current behaviour)
3. **Character POV** — shows only events the character participated in or `knows_about`

**What to build:**
- New `app/services/wiki_filter.py`: `get_filtered_events(story_uuid, mode, reader_chapter, pov_character_id)`
- `rag.py` → `query_story()`: accept `mode` and `reader_chapter` params, pass through filter before building the prompt
- `app_ui.py`: reader chapter slider + mode selector in the Query tab

**Files:** New `wiki_filter.py` + `rag.py` + `app_ui.py`

---

#### 8.4 Batched Arc Detection *(Ideas #5 & #6)*
**Easiness: 🟡🟡 · Impact: ⭐⭐⭐ 💰**

No arc concept exists anywhere in the codebase. Arcs are the semantic glue between isolated events — without them, the wiki has no sense of story structure (e.g., "The Tournament Arc", "The Betrayal Arc").

**What to build:**
- New `app/services/arc_detector.py`:
  - `detect_arcs(story_uuid, every_n=5)` — clusters recent events by location + participants, sends a single batched LLM prompt, writes `Arc` nodes to the graph
- `graph_adapter.py`: add `add_arc(arc_id, label, event_ids, chapter_start, chapter_end)` method
- `ingest.py` → `ingest_chapter()`: after `save_runtime()`, trigger `if chapter_counter % 5 == 0: detect_arcs(story_uuid)`

**Files:** New `arc_detector.py` + `graph_adapter.py` + `ingest.py`

---

#### 8.5 Location & Event Wiki Pages *(Idea #3)*
**Easiness: 🟡🟡 · Impact: ⭐⭐ 🎭**

The wiki currently only has character pages. The graph already stores `location` on every event — a location wiki page is essentially a free aggregation query.

**What to build:**
- New `app/services/location_wiki.py`: `build_location_page(story_uuid, location_name)` — queries all events at that location, builds a timeline, LLM-generates a summary
- New `app/services/event_wiki.py`: `build_event_page(story_uuid, event_id)` — renders the event's full causal chain, participants, pre/post conditions
- `app_ui.py`: new "Locations" and "Events" tabs in the Wiki section

**Files:** New `location_wiki.py`, `event_wiki.py` + `app_ui.py`

---

#### 8.6 Character POV Knowledge Edges *(Idea #4, item 3)*
**Easiness: 🟡🟡🟡 · Impact: ⭐⭐**

Currently there's no way to model what a character *knows about* without being present. Adding `[:KNOWS]→(Event)` edges enables richer POV filtering.

**What to add:**
- `graph_adapter.py`: `add_knowledge_edge(character_id, event_id)` — a lightweight directed edge of type `"knows_about"`
- Extraction prompt: add `"known_by": ["CharB"]` field to events — for scenes where a character overhears or is told about something
- `wiki_filter.py` POV mode uses these edges to expand what a POV character "sees"

**Files:** `graph_adapter.py`, `extraction.py`, `ingest.py`, `wiki_filter.py`

---

### Phase 3 — Infrastructure Upgrades (Defer)

#### 8.7 Neo4j Knowledge Graph *(Ideas #3, #6, #7)*
**Easiness: 🔴 · Impact: ⭐⭐ (at scale)**

NetworkX + JSON files work well for the current story sizes. Neo4j is only warranted when the graph outgrows in-memory operation (>100k nodes) or when Cypher queries become necessary for complex traversals.

**Trigger:** Revisit when a single story graph exceeds ~50MB JSON or query latency becomes noticeable.

---

#### 8.8 Qdrant Vector Store *(Idea #7)*
**Easiness: 🔴 · Impact: ⭐⭐**

The current RAG uses graph traversal (entity matching → neighbourhood retrieval). Qdrant would enable semantic similarity search over chapter embeddings — useful for "find chapters similar to this scene" but not needed for the current Q&A use case.

**Trigger:** Add when implementing a "Similar Scenes" or "Chapter Search" feature.

---

#### 8.9 LangGraph State Machine *(Idea #6)*
**Easiness: 🔴 · Impact: 💰 (pipeline clarity)**

The ingestion pipeline in `ingest.py` is already a well-structured sequential pipeline. LangGraph adds retries, branching, and observability — valuable for production, but a full rewrite of the current working system.

**Trigger:** Add when the pipeline needs parallel chapter processing or retry logic for LLM failures beyond the current `retries.py` mechanism.

---

#### 8.10 Redis / RabbitMQ Background Jobs *(Idea #5, item 6)*
**Easiness: 🔴 · Impact: 💰**

`enrich_all_wikis_from_rag()` already exists and works. True async job queues are only needed when wiki enrichment blocks the UI noticeably under concurrent user load.

**Trigger:** Add when moving from single-user Streamlit to a multi-user FastAPI deployment.

---

### Summary Ranking Table

| # | Feature | Easiness | Impact | Phase |
|---|---------|----------|--------|-------|
| 8.1 | `timeline_type` on events | 🟢🟢🟢 | ⭐⭐⭐ | 1 |
| 8.2 | `reveal_point` on events | 🟢🟢🟢 | ⭐⭐ 🎭 | 1 |
| 8.3 | Spoiler-Free / POV wiki filter | 🟡🟡 | ⭐⭐⭐ 🎭 | 2 |
| 8.4 | Batched arc detection | 🟡🟡 | ⭐⭐⭐ 💰 | 2 |
| 8.5 | Location & Event wiki pages | 🟡🟡 | ⭐⭐ 🎭 | 2 |
| 8.6 | Character POV knowledge edges | 🟡🟡🟡 | ⭐⭐ | 2 |
| 8.7 | Neo4j migration | 🔴 | ⭐⭐ | 3 |
| 8.8 | Qdrant vector store | 🔴 | ⭐⭐ | 3 |
| 8.9 | LangGraph orchestration | 🔴 | 💰 | 3 |
| 8.10 | Redis/RabbitMQ job queue | 🔴 | 💰 | 3 |
