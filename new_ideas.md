# RAG for Novel Chapters — Ideas & Reference

---

## Cutting-Edge RAG Approaches

**LangGraph RAG** — Agentic multi-step reasoning. AI decides when to search, what to retrieve, and when to stop.

**LlamaIndex Advanced RAG** — Recursive retrieval, auto-merging indexes, query planning. "Retriever of retrievers" across structured + unstructured data.

**Self-RAG** — Model generates answer → evaluates correctness → retrieves again if needed. Self-correcting loop.

**Graph RAG** — Retrieval over entity relationships, not plain text. Used in finance, healthcare, enterprise search.

**Corrective RAG (CRAG)** — Detects bad retrieval automatically. Retrieve → check quality → re-search or fallback if poor.

**Multimodal RAG** — Handles images, PDFs, tables, audio via vision + text embeddings.

**Hybrid search** — Keyword + vector + graph combined.

---

## Novel Chapter RAG — Core Architecture

Novels have characters, evolving relationships, timeline/event progression, and lots of implicit context. The system needs to track *who did what, when, and how they relate*.

**Best stack:** LlamaIndex + Qdrant + Neo4j (hybrid)
**Simpler alternative:** LightRAG (mixes structure + semantics, less engineering)
**Overkill:** Full GraphRAG (only worth it for literary analysis at scale)

**Key design rule:** Chunk by scenes/narrative units, not tokens. Novels rely on context continuity — bad chunking breaks reasoning.

---

## Dual Timeline Model (for flashbacks)

Every event needs two time values:

```json
{
  "event": "Alice meets Ravi",
  "narrative_time": 10,   // chapter it appears in
  "story_time": 2,         // when it actually happened
  "type": "flashback"
}
```

**Flashback detection prompt:**
```
Is this scene: present | flashback | memory | dream | parallel storyline?
Extract temporal cues ("years ago…", "he remembered…", "back then…").
Assign relative time: BEFORE event X / AFTER event Y.
```

**Tricky cases:**
- Nested flashbacks → add `"depth": 2`
- Unreliable narration → tag as `"type": "dream" | "imagined" | "rumor"`
- Ambiguous time → `"story_time": "unknown", "relative": "before major_event_X"`

**Retrieval rule:** Query story timeline for causal questions ("why did X happen?"). Use narrative order only when asked about reader experience ("when was it revealed?").

**Time-aware graph edges** (high-impact upgrade):
```
Alice → trusts → Ravi (Chapter 3)
Alice → distrusts → Ravi (Chapter 8)
```
Enables character arc tracking and causal reasoning.

---

## Knowledge Graph Schema (Neo4j)

**Nodes:**
```cypher
(:Character { id, name, aliases, description, first_appearance_chapter })

(:Event {
  id, name, summary,
  narrative_chapter, narrative_order,
  story_time_rank,       // relative chronological order
  timeline_type,         // present | flashback | dream | rumor
  confidence,            // LLM confidence score
  is_canonical           // false for unreliable narration
})

(:Scene { id, chapter, location, summary })
(:Arc { id, name, theme, summary })
(:Location { id, name, description })
(:WikiPage { id, type, title, content, generated_at, version })  // derived, not source of truth
```

**Relationships:**
```cypher
(:Event)-[:BEFORE]->(:Event)
(:Event)-[:AFTER]->(:Event)
(:Event)-[:CAUSES]->(:Event)
(:Event)-[:RESULTS_IN]->(:Event)
(:Event)-[:OCCURS_IN]->(:Scene)
(:Scene)-[:IN_CHAPTER]->(:Chapter)
(:Character)-[:INVOLVED_IN {role}]->(:Event)   // role: protagonist | witness | cause | victim
(:Arc)-[:STARTS_WITH | HAS_EVENT | ENDS_WITH]->(:Event)
(:Character)-[:PARTICIPATES_IN]->(:Arc)
(:Event)-[:BELONGS_TO]->(:Arc)
(:Character)-[:KNOWS]->(:Event)        // for POV-based wiki
(:Character)-[:UNAWARE_OF]->(:Event)
(:WikiPage)-[:DERIVED_FROM]->(:Character | :Event | :Arc)
```

---

## Wiki = Dynamic Projections over the Graph

Don't store wiki pages as primary data. Store the graph as truth; generate pages on demand.

```
WikiPage(character_id) = LLM(graph neighborhood of node)
```

**Page types:**

**Character page** — identity summary, story-time event timeline, relationships, arc participation, hidden knowledge (what they know vs. what reader knows).

**Event page** — what happened, causal chain (why), before/after events, participants and roles, arc context, narrative vs. story-time comparison.

**Arc page** — theme, start event, escalation events, turning point, resolution, characters, emotional/thematic evolution.

**Location page** — events there, characters frequently present, timeline of changes.

**Wiki versioning:**
```json
{ "version": 3, "generated_at": timestamp, "graph_snapshot_id": "xyz" }
```

---

## 3-Stage LLM Prompt Pipeline

### Stage 1 — Chapter → Structured Events

```
You are extracting structured story events from a novel chapter.
Return JSON only.

For each event extract:
- event_name
- summary
- characters involved
- location
- timeline type: present | flashback | dream | rumor
- narrative order (sequence in chapter)
- story time clues (relative ordering hints)
- causal relationships if implied
- arc hints if any

IMPORTANT:
- Split into atomic events
- Do not merge unrelated actions
- Preserve temporal ambiguity if unsure

CHAPTER TEXT: {chapter_text}
```

Output:
```json
{
  "events": [{
    "name": "...", "summary": "...", "characters": [],
    "timeline_type": "flashback", "narrative_order": 3,
    "causes": [], "implied_arc": ""
  }]
}
```

### Stage 2 — Normalization + Graph Linking

```
Tasks:
1. Assign story_time_rank (relative chronology)
2. Detect BEFORE / AFTER relationships
3. Identify arcs and group events
4. Resolve duplicate events with existing graph
5. Assign confidence score
```

Output:
```json
{
  "events": [{
    "id": "...", "story_time_rank": 12,
    "before": ["event_id"], "after": ["event_id"],
    "arc": "betrayal_arc", "confidence": 0.87
  }]
}
```

### Stage 3 — Graph → Wiki Pages

**Character wiki prompt:**
```
Generate a wiki page for this character using graph data.
Include: identity summary, timeline of key events (story order),
relationships, arcs participated in, hidden knowledge.
GRAPH DATA: {character_subgraph}
```

**Event wiki prompt:**
```
Generate a wiki page for this event.
Include: what happened, why (causal chain), before/after events,
characters + roles, arc context, narrative vs story-time explanation.
GRAPH DATA: {event_subgraph}
```

**Arc wiki prompt:**
```
Generate a narrative arc wiki page.
Include: theme, start event, key progression events, turning point,
resolution, characters involved, emotional/thematic evolution.
GRAPH DATA: {arc_subgraph}
```

---

## Spoiler System — Same Graph, Different Views

Don't store multiple wikis. Store one truth graph + visibility filters.

**Event node extension:**
```cypher
(:Event {
  spoiler_level,   // 0 = safe, 1 = mild, 2 = major
  reveal_point     // chapter when it becomes known to reader
})
```

Example:
| Event | spoiler_level | reveal_point |
|---|---|---|
| Alice meets Ravi | 0 | Chapter 1 |
| Ravi is betraying Alice | 2 | Chapter 18 |
| Alice survives attack | 1 | Chapter 10 |

**Spoiler-free query:**
```cypher
MATCH (e:Event)-[:INVOLVES]->(c:Character {id:$id})
WHERE e.reveal_point <= $reader_progress
RETURN e
```
Then pass to LLM with prompt:
```
Rewrite this wiki page for a spoiler-free reader.
Do NOT reveal future events. Preserve emotional meaning.
Use vague references instead of explicit twists.
```

Example transformation:
- Full: *"Ravi betrays Alice in Chapter 18"*
- Spoiler-free: *"Ravi's actions later change Alice's trust in him"*

**Omniscient query:** No filter — return all events.

**Three-way view system:**
| Mode | What it shows |
|---|---|
| Spoiler-free | Events up to reader's current chapter |
| Character POV | Only what that character knows (`[:KNOWS]`) |
| Omniscient | Full truth graph, all arcs, all causality |

**API request shape:**
```json
{
  "wiki_type": "character",
  "entity_id": "alice",
  "mode": "spoiler_free",
  "reader_progress": 12
}
```

---

## Low-Cost Ingestion Pipeline

Goal: 1–2 LLM calls per chapter, everything else deterministic.

```
Chapter text
  ↓ [1 LLM call: structured extraction]
  ↓ [local graph builder — no LLM]
  ↓ [embedding-based entity merge]
  ↓ [Neo4j upsert]
  ↓ async: arc detection (batched) + wiki generation (lazy)
```

**Step 1 — Single extraction call (80% cost reduction):**
Prompt asks only for names, summaries, character lists, timeline type, order — no reasoning, no graph building, no summarization.

**Step 2 — Deterministic graph build (no LLM):**
```python
for event in events:
    MERGE (e:Event {id})
    SET e.narrative_order = event.order_in_chapter
    for character in event.characters:
        MERGE (c:Character {name})
        MERGE (c)-[:INVOLVED_IN]->(e)
```

**Step 3 — Entity resolution via embeddings (not LLM):**
Embed character names → cosine similarity → merge if threshold > 0.92. Use `sentence-transformers` locally or a cheap embedding API.

**Step 4 — Fixer pass (only when triggered):**
Only run when: conflicting timelines, missing characters, unclear flashback tagging, or duplicate events detected.
```
You are correcting a story graph.
Resolve duplicates, fix timeline ordering, correct flashback classification.
Do NOT re-extract everything. Only modify errors.
```

**Step 5 — Arc detection (batched every N=5–10 chapters):**
First cluster events heuristically by shared characters + causal links + time proximity. Only send clusters to LLM.

**Step 6 — Wiki generation (async, lazy):**
Queue jobs; never generate wiki during ingestion. Only run when queried or on a batch schedule.

---

## LangGraph Pipeline

```python
class IngestionState(TypedDict):
    chapter_id: str
    chapter_text: str
    events: List[Dict]
    graph_ops: List[Dict]
    resolved_entities: Dict
    arc_candidates: List[Dict]
    wiki_jobs: List[Dict]
    error: str | None

graph = StateGraph(IngestionState)
graph.add_node("extract", extract_events)        # 1 LLM call
graph.add_node("build_graph", build_graph_ops)   # no LLM
graph.add_node("resolve", resolve_entities)       # embeddings
graph.add_node("neo4j", write_to_neo4j)
graph.add_node("arc", detect_arcs)               # batched, optional LLM
graph.add_node("wiki_queue", queue_wiki_jobs)    # async
```

**Conditional arc detection (cost control):**
```python
def should_detect_arcs(state):
    return len(state["events"]) > 5

graph.add_conditional_edges("neo4j", should_detect_arcs,
    {True: "arc", False: "wiki_queue"})
```

**Spoiler metadata node (plug in after extraction):**
```python
def add_spoiler_metadata(state):
    for e in state["events"]:
        e["spoiler_level"] = compute_spoiler_level(e)
    return state
```
