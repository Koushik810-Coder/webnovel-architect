If you’re aiming for **cutting-edge RAG projects on GitHub**, you’ll want to go beyond basic “PDF Q&A” and look at systems that combine **agents, memory, multimodality, and advanced retrieval strategies**. Here are some of the most modern, forward-looking RAG repos and ideas 👇

---

# 🚀 Cutting-Edge RAG GitHub Projects

## 🧠 1. LangGraph RAG Systems

* GitHub: LangChain ecosystem
* Focus: **Agentic RAG (multi-step reasoning)**

💡 What’s new:

* Instead of single retrieval → generation
* Uses **decision-making graphs**
* AI decides:

  * When to search
  * What to retrieve
  * When to stop

👉 This is **next-gen RAG (Agent + Memory + Tools)**

---

## 🔍 2. LlamaIndex Advanced RAG

* Advanced pipelines:

  * Recursive retrieval
  * Auto-merging indexes
  * Query planning

💡 Cutting-edge features:

* “Retriever of retrievers”
* Structured + unstructured data
* Self-improving pipelines

👉 Used in many **production-grade AI systems**

---

## ⚡ 3. Haystack 2.0 (Agentic RAG)

* Supports:

  * Tools
  * Memory
  * Multi-hop reasoning

💡 New capability:

* RAG + **tool calling**
* Pipelines behave like **AI agents**

---

## 🧬 4. Self-RAG (Research → GitHub Implementations)

* Concept: Model critiques its own answers

💡 What makes it cutting edge:

* Generates answer
* Evaluates correctness
* Retrieves again if needed

👉 Moves toward **self-correcting AI systems**

---

## 🧩 5. Graph RAG (Knowledge Graph + LLMs)

* Combines:

  * RAG + Knowledge Graphs

💡 Key innovation:

* Instead of plain text retrieval:

  * Uses relationships between entities

👉 Used for:

* Finance
* Healthcare
* Enterprise search

---

## 🌐 6. Multimodal RAG

* Handles:

  * Images
  * PDFs
  * Tables
  * Audio

💡 Example tools:

* Vision + text embeddings

👉 Real-world use:

* Medical imaging
* Document AI systems

---

## 🔄 7. Corrective RAG (CRAG)

* Detects bad retrieval automatically

💡 Flow:

* Retrieve → Check quality
* If bad → re-search or fallback

👉 Solves one of RAG’s biggest problems:
❌ Wrong context
✅ Better accuracy

---

## 🧠 8. Long-Context + RAG Hybrid Systems

* Combines:

  * Large context LLMs
  * Retrieval

💡 Why cutting edge:

* Uses retrieval only when needed
* Reduces cost + improves speed

---

# 🔥 What Makes These “Cutting Edge”

Modern RAG systems are shifting from:

### ❌ Old RAG

* One query → one retrieval → one answer

### ✅ New RAG

* Multi-step reasoning
* Self-correction
* Tool usage
* Memory
* Multimodal understanding

---

# 🧪 Real Trend Right Now (2025–2026)

Top research + GitHub direction:

* **Agentic RAG** (AI plans its own retrieval)
* **Self-RAG / Reflection models**
* **Graph RAG**
* **Hybrid search (keyword + vector + graph)**
* **Streaming + real-time RAG**

---

# 🎯 If You Want a Cutting-Edge Project Idea

Here are strong ideas (resume-worthy):

### 💡 1. “Self-Correcting RAG Assistant”

* Detect hallucinations
* Retry retrieval automatically

---

### 💡 2. “Multimodal Study AI”

* Input:

  * PDFs + images + diagrams
* Output:

  * Smart explanations

---

### 💡 3. “Agentic Research Assistant”

* Breaks questions into sub-queries
* Searches multiple sources
* Combines answers

---

### 💡 4. “Graph-Based Knowledge AI”

* Build knowledge graph from docs
* Query relationships

---

# ⚠️ Reality Check

Cutting-edge RAG is:

* More complex
* Harder to debug
* Requires:

  * Good retrieval design
  * Evaluation metrics
  * Prompt engineering

If you jump straight in without basics, it gets messy fast.

---

# 💬 Want the next step?

I can:

* Give you a **cutting-edge GitHub repo with code walkthrough**
* Help you **build one of these projects step-by-step**
* Or suggest a **final-year project using latest RAG techniques**

Just tell me your level (beginner/intermediate/advanced) 👍

Nice—that’s a very specific (and interesting) use case. Novel chapters behave very differently from generic documents, so the “best” setup shifts a bit.

Let me be direct:

👉 **Full GraphRAG is usually overkill for novels** unless you really care about deep narrative reasoning.

---

# 🧠 What makes novel chapters special

Unlike typical docs, novels have:

* recurring **characters**
* evolving **relationships**
* **timeline / events progression**
* lots of **implicit context** (not always stated directly)

So your system needs to track:
👉 *who did what, when, and how they relate*

---

# 🏆 Best approach for novel ingestion (few chapters/day)

## 🥇 Best practical setup

Use a **hybrid lightweight GraphRAG**

### Stack:

* LlamaIndex
* Qdrant
* Neo4j

---

## ⚙️ How it should work

### 1. When a new chapter arrives (daily)

* chunk text (by scene, not just tokens)
* generate embeddings → store in Qdrant

### 2. Extract structured info (this is the key part)

Use LLM to extract:

* characters
* locations
* events
* relationships

Example:

```json
{
  "characters": ["Alice", "Ravi"],
  "event": "argument",
  "location": "train station",
  "relationships": [
    {"Alice": "trusts", "Ravi": "less"}
  ]
}
```

Store this in Neo4j as a graph.

---

### 3. Retrieval time (important)

When user asks:

> “Why did Alice stop trusting Ravi?”

Your system should:

1. Query graph (Neo4j):

   * relationship changes
   * relevant events

2. Query vector DB:

   * fetch exact scenes

3. Combine → send to LLM

👉 This is where hybrid beats pure RAG

---

# 🥈 If you want simpler

Skip the graph and use:

* LightRAG

### Why:

* already mixes structure + semantics
* less engineering effort

👉 Good tradeoff if you don’t want to maintain Neo4j

---

# 🥉 When to use full GraphRAG

* GraphRAG

Only if you want:

* global story summaries
* thematic clustering (e.g., “all betrayal arcs”)
* book-level analysis

👉 Otherwise: too heavy for your needs

---

# 🔥 Important design tip (most people miss this)

### ❌ Don’t chunk blindly by tokens

### ✅ Chunk by **scenes or narrative units**

Because:

* novels rely on **context continuity**
* bad chunking = broken reasoning

---

# 🧠 Extra upgrade (high impact)

Add **time-awareness** to your graph:

Instead of:

```
Alice → trusts → Ravi
```

Do:

```
Alice → trusts → Ravi (Chapter 3)
Alice → distrusts → Ravi (Chapter 8)
```

👉 This enables:

* character arc tracking
* causal reasoning

---

# 🚀 Bottom line

For *novel chapters (few per day)*:

### Best choice:

👉 LlamaIndex + Qdrant + Neo4j (hybrid)

### Simplest viable:

👉 LightRAG

### Overkill:

👉 GraphRAG (unless doing literary analysis at scale)

---

If you want, I can design:

* a **Neo4j schema for characters/events**
* or **LLM prompts for extracting relationships accurately**

That’s where most of the real performance gains come from.

Nice — a **dynamic wiki builder** actually fits perfectly on top of the same dual-timeline + event graph idea you were already exploring.

If you design it right, your RAG system stops being “document retrieval” and becomes a **living knowledge graph that reorganizes itself**.

---

# 🧠 Core Idea: Wiki = Structured Views over Your Graph

Instead of storing “wiki pages” as primary data, you treat them as:

> **generated projections of your event + entity graph**

So:

* Graph = source of truth
* Wiki pages = dynamic views
* RAG = query layer over both

---

# 🏗️ System Architecture

## 1. Ingestion Layer (what you already started)

You extract:

* Events
* Characters
* Scenes
* Relationships
* Timeline info (story + narrative)

This feeds your graph.

---

## 2. Knowledge Graph (core backbone)

You’ll want something like:

### Nodes

* Character
* Event
* Location
* Object
* Arc (important for wiki grouping)

### Edges

* INVOLVED_IN
* BEFORE / AFTER
* LOCATED_AT
* CAUSES
* BELONGS_TO_ARC

This is your “truth layer”.

---

## 3. Wiki Generator Layer (the missing piece)

This is where your idea becomes powerful.

You generate **wiki pages on demand or periodically**.

---

# 📄 Wiki Page Types

Instead of static pages, you generate *types* of pages:

## 1. Character Page

Generated from graph:

**Alice**

* Summary (LLM-generated)
* Timeline of key events (story-time ordered)
* Relationships graph
* Arc participation
* Hidden knowledge (what she knows vs what reader knows)

---

## 2. Event Page

**“Alice meets Ravi”**

* Narrative occurrences (chapter appearances)
* Story-time position
* Participants
* Consequences (forward edges)
* Preceding causes (backward edges)

---

## 3. Arc Page (VERY important for novels)

Example:

**“Ravi betrayal arc”**

* Start event
* Key escalation events
* Reveal event
* Resolution event
* Characters involved

This becomes your *semantic grouping layer*.

---

## 4. Location Page

* Events occurring there
* Characters frequently present
* Timeline of changes

---

# 🔁 Key Innovation: Wiki is Recomputed, not Stored

Instead of saving markdown pages, you do:

```text
WikiPage(character_id) = LLM(graph neighborhood of node)
```

So every update to graph → wiki updates automatically.

---

# 🧠 Retrieval Flow (important for RAG)

When user asks:

> “Why did Alice stop trusting Ravi?”

System should:

### Step 1: Graph query

* find distrust event
* trace backward edges (causal chain)

### Step 2: Pull subgraph

* Alice + Ravi + related events

### Step 3: Generate “mini wiki page”

* causal explanation
* timeline snippet

### Step 4: Answer grounded in that

---

# ⚡ The Real Trick: Two-Level Memory

You now have:

## 1. Raw Memory (Graph)

* exact events
* structured truth

## 2. Wiki Memory (Derived)

* summaries
* explanations
* human-readable narratives

This prevents hallucination while still allowing abstraction.

---

# 🧩 Handling “Dynamic Wiki Behavior”

To make it feel alive:

## 1. Lazy generation

Only build pages when requested or frequently accessed.

## 2. Versioning

Store:

```json
wiki_page_version: {
  version: 3,
  generated_at: timestamp,
  graph_snapshot_id: xyz
}
```

## 3. Personalization layer (optional later)

Same graph → different wiki views depending on query intent.

---

# 🔥 Advanced Upgrade (this is where it gets interesting)

## “Wiki as a Query Language”

Instead of static pages:

* “Show me Alice before betrayal”
* “Show me Ravi from Alice’s perspective”
* “Show all hidden knowledge events”

Each becomes a **filtered graph projection + LLM summary**

---

# 🧠 How this connects to your flashback model

Your dual timeline becomes a first-class wiki feature:

* “Story timeline view” page
* “Chronological truth view” page
* “Reader discovery view” page

Same data, different projections.

---

# 🚀 Minimal Stack (practical version)

If you want to build fast:

* Graph DB: Neo4j / ArangoDB
* Event extractor: LLM pipeline
* Wiki generator: LLM + templating
* API layer: FastAPI / Node
* Frontend: React + graph viewer

---

# 💡 The key mental shift

You are NOT building:

> a wiki system

You are building:

> a **queryable narrative intelligence layer over a story graph**

---

If you want next step, I can help you design:

* a **full Neo4j schema for wiki + timeline + arcs**
* or a **prompt pipeline that turns raw chapters → graph → wiki automatically**
* or even a **MVP architecture you can build in 7–10 days**

Just tell me where you want to go next.

Good — these two pieces are basically the “brain + metabolism” of your system:

* **Neo4j schema = long-term memory structure**
* **Prompt pipeline = how memory gets created and updated**

I’ll give you both, but in a way that actually fits together (most designs fail because they treat them separately).

---

# 🧠 PART 1: FULL NEO4J SCHEMA (Wiki + Timeline + Arcs)

This is designed for:

* novels
* flashbacks
* unreliable narration
* dynamic wiki generation

---

# 🧱 CORE NODE TYPES

## 1. Character

```cypher
(:Character {
  id,
  name,
  aliases,
  description,
  first_appearance_chapter
})
```

---

## 2. Event (MOST IMPORTANT NODE)

```cypher
(:Event {
  id,
  name,
  summary,

  narrative_chapter,
  narrative_order,

  story_time_rank,   // relative ordering
  timeline_type,     // present | flashback | dream | rumor

  confidence,        // LLM confidence
  is_canonical       // true/false (for unreliable narration)
})
```

👉 This is your dual-timeline anchor:

* narrative = “how story is told”
* story_time_rank = “what actually happened”

---

## 3. Scene

```cypher
(:Scene {
  id,
  chapter,
  location,
  summary
})
```

---

## 4. Arc (THIS IS YOUR WIKI STRUCTURE LAYER)

```cypher
(:Arc {
  id,
  name,
  theme,
  summary
})
```

---

## 5. Location

```cypher
(:Location {
  id,
  name,
  description
})
```

---

## 6. WikiPage (DERIVED NODE — not source of truth)

```cypher
(:WikiPage {
  id,
  type,          // character | event | arc | location
  title,
  content,
  generated_at,
  version
})
```

---

# 🔗 RELATIONSHIPS (THE REAL POWER)

## Timeline relationships

```cypher
(:Event)-[:BEFORE]->(:Event)
(:Event)-[:AFTER]->(:Event)
```

👉 This replaces timestamps entirely.

---

## Narrative structure

```cypher
(:Event)-[:OCCURS_IN]->(:Scene)
(:Scene)-[:IN_CHAPTER]->(:Chapter)
```

---

## Character involvement

```cypher
(:Character)-[:INVOLVED_IN {role}]->(:Event)
```

role examples:

* protagonist
* witness
* cause
* victim

---

## Arc structure (VERY IMPORTANT)

```cypher
(:Arc)-[:STARTS_WITH]->(:Event)
(:Arc)-[:HAS_EVENT]->(:Event)
(:Arc)-[:ENDS_WITH]->(:Event)
```

---

## Arc participation

```cypher
(:Character)-[:PARTICIPATES_IN]->(:Arc)
(:Event)-[:BELONGS_TO]->(:Arc)
```

---

## Causality (this is your “why” engine)

```cypher
(:Event)-[:CAUSES]->(:Event)
(:Event)-[:RESULTS_IN]->(:Event)
```

---

## Knowledge separation (advanced but powerful)

```cypher
(:Character)-[:KNOWS]->(:Event)
(:Character)-[:UNAWARE_OF]->(:Event)
```

👉 This enables:

* spoilers control
* POV-based wiki pages

---

## Wiki generation linkage

```cypher
(:WikiPage)-[:DERIVED_FROM]->(:Character | :Event | :Arc)
```

---

# 🧠 PART 2: PROMPT PIPELINE (RAW CHAPTER → GRAPH → WIKI)

This is where most systems fail. You want a **3-stage LLM pipeline**.

---

# ⚙️ STAGE 1: CHAPTER → STRUCTURED EVENTS

### Input:

Raw chapter text

### Prompt:

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

CHAPTER TEXT:
{chapter_text}
```

---

### Output format:

```json
{
  "events": [
    {
      "id": "auto",
      "name": "...",
      "summary": "...",
      "characters": [],
      "location": "...",
      "timeline_type": "flashback",
      "narrative_order": 3,
      "causes": [],
      "implied_arc": ""
    }
  ]
}
```

---

# ⚙️ STAGE 2: EVENT → NORMALIZATION + GRAPH LINKING

### Input:

All extracted events + existing graph context

### Prompt:

```
You are organizing story events into a knowledge graph.

Tasks:

1. Assign story_time_rank (relative chronology)
2. Detect BEFORE / AFTER relationships
3. Identify arcs and group events
4. Resolve duplicate events with existing graph
5. Assign confidence score

Return updated event graph structure.
```

---

### Output:

```json
{
  "events": [
    {
      "id": "...",
      "story_time_rank": 12,
      "before": ["event_id"],
      "after": ["event_id"],
      "arc": "betrayal_arc",
      "confidence": 0.87
    }
  ]
}
```

---

# ⚙️ STAGE 3: GRAPH → WIKI PAGE GENERATION

This is your “dynamic wiki builder”.

---

## Character Wiki Prompt

```
Generate a wiki page for this character using graph data.

Include:

- Identity summary
- Timeline of key events (story order)
- Relationships
- Arcs participated in
- Hidden knowledge (what they know vs don't know)

GRAPH DATA:
{character_subgraph}
```

---

## Event Wiki Prompt

```
Generate a wiki page for this event.

Include:

- What happened
- Why it happened (causal chain)
- Before / after events
- Characters involved and roles
- Arc context
- Narrative vs story-time explanation

GRAPH DATA:
{event_subgraph}
```

---

## Arc Wiki Prompt

```
Generate a narrative arc wiki page.

Include:

- Theme of arc
- Start event
- Key progression events
- Turning point
- Resolution
- Characters involved
- Emotional or thematic evolution

GRAPH DATA:
{arc_subgraph}
```

---

# 🔁 SYSTEM LOOP (IMPORTANT)

```text
Chapter Ingested
   ↓
Event Extraction (Stage 1)
   ↓
Graph Update (Stage 2)
   ↓
Arc Linking + Timeline Ordering
   ↓
Wiki Regeneration (Stage 3)
   ↓
RAG-ready Knowledge Base
```

---

# 🧠 WHY THIS DESIGN WORKS

### 1. Flashbacks stop breaking your system

Because narrative_time and story_time_rank are separate.

---

### 2. Wiki never becomes stale

Because it's always derived from graph

---

### 3. You can answer 3 types of questions:

* “What happened in chapter 5?” → narrative layer
* “Why did X happen?” → causal graph traversal
* “What is Alice’s story?” → wiki projection

---

### 4. You get multi-perspective storytelling

Same graph can generate:

* spoiler-free wiki
* full omniscient wiki
* character POV wiki

---

# 🚀 If you want next step

I can help you design:

### 1. Real Neo4j Cypher schema (ready to paste)

### 2. FastAPI ingestion service architecture

### 3. LangGraph / LlamaIndex pipeline version

### 4. Or a minimal MVP you can build in 48 hours

Just tell me.

A low-cost ingestion pipeline for this kind of **chapter → graph → dual wiki system** is mostly about one thing:

> **minimizing LLM calls while maximizing structured reuse**

If you design it badly, every chapter becomes 5–10 expensive calls.
If you design it well, you can get it down to **1–2 small calls per chapter + batching**.

---

# 🧠 LOW-COST INGESTION PIPELINE (PRINCIPLED DESIGN)

## 🔁 High-level flow

```text
Chapter Text
   ↓
(1) Cheap extraction pass (single LLM call)
   ↓
(2) Deterministic graph builder (no LLM)
   ↓
(3) Batch embedding + dedup
   ↓
(4) Optional second-pass “fixer” (only if needed)
   ↓
Neo4j update
   ↓
Async wiki generation (lazy)
```

---

# ⚙️ STEP 1 — SINGLE LOW-COST EXTRACTION CALL (MOST IMPORTANT)

### Goal:

Replace multi-step extraction with **one structured pass**

Use a **cheap model (or small-context model)**.

---

## Prompt (optimized for cost)

```text id="c1p0ex"
Extract structured information from this chapter.

Return JSON ONLY.

Split into atomic EVENTS.

For each event:

- name
- 1-line summary
- characters (names only)
- location (if any)
- type: present | flashback | dream | rumor
- order_in_chapter (integer)
- temporal cues (optional short text)
- implied causality (only if obvious)

Do NOT:
- write explanations
- do not infer deeply
- do not create arcs yet

CHAPTER:
{text}
```

---

## Why this is cheap:

* no reasoning-heavy tasks
* no graph building
* no summarization
* just structured extraction

👉 This is your **80% cost reduction step**

---

# ⚙️ STEP 2 — DETERMINISTIC GRAPH BUILDER (NO LLM)

Now you convert JSON → graph locally.

### Rules:

* create Event nodes
* link to Characters (MERGE nodes)
* preserve chapter order
* assign provisional IDs

---

## Example logic:

```python id="g9k2pl"
for event in events:
    MERGE (e:Event {id})
    SET e.narrative_order = event.order_in_chapter

    for character in event.characters:
        MERGE (c:Character {name})
        MERGE (c)-[:INVOLVED_IN]->(e)
```

---

### Why this matters:

✔ zero LLM cost
✔ fast ingestion
✔ repeatable
✔ safe (no hallucination)

---

# ⚙️ STEP 3 — LIGHTWEIGHT ENTITY RESOLUTION (BATCHED)

Instead of asking LLM:

> “is Ravi the same as R. Ravi?”

You do:

### Embedding-based clustering (cheap + scalable)

* embed character names
* cosine similarity
* merge if threshold > 0.92

Use:

* sentence-transformers (local)
* or cheap embedding API

---

# ⚙️ STEP 4 — OPTIONAL “FIXER PASS” (ONLY FOR HARD CASES)

Instead of running a second LLM pass always:

👉 only trigger when ambiguity detected:

### triggers:

* conflicting timelines
* missing characters
* unclear flashback tagging
* duplicate events suspected

---

## Fixer prompt:

```text id="k8xqop"
You are correcting a story graph.

Given extracted events and relationships:
- resolve duplicates
- fix timeline ordering
- correct flashback classification

Do NOT re-extract everything.

Only modify errors.
```

---

# ⚙️ STEP 5 — ARC DETECTION (BATCHED, NOT PER CHAPTER)

THIS is where people waste money.

❌ Wrong: detect arcs per chapter
✅ Right: detect arcs every N chapters (e.g. 5–10)

---

## Cheap heuristic first:

Before LLM:

* cluster events by:

  * shared characters
  * causal links
  * time proximity

Then only send clusters to LLM:

```text id="x2m8ld"
Identify narrative arcs from these grouped events.
```

---

# ⚙️ STEP 6 — ASYNC WIKI GENERATION (NEVER INLINE)

Do NOT generate wiki during ingestion.

Instead:

### queue jobs:

* Character wiki updates
* Event wiki updates
* Arc wiki updates

Use:

* Redis queue / RabbitMQ / simple background worker

---

## Why this saves cost:

✔ wiki generation becomes **lazy**
✔ only runs when queried or batch scheduled
✔ avoids recomputing every chapter

---

# 💡 COST OPTIMIZATION SUMMARY

## What you eliminated:

❌ multi-call extraction pipelines
❌ per-event LLM calls
❌ per-chapter arc detection
❌ immediate wiki generation
❌ repeated summarization passes

---

## What you kept:

✔ 1 extraction call per chapter
✔ deterministic graph build
✔ batched embeddings
✔ occasional correction pass
✔ lazy wiki generation

---

# 🧠 FINAL ARCHITECTURE

```text id="z9p2kx"
CHAPTER
  ↓
[1 LLM CALL: structured extraction]
  ↓
[local graph builder]
  ↓
[embedding-based entity merge]
  ↓
[Neo4j update]
  ↓
(async)
    ├── arc detection (batched)
    ├── wiki generation (lazy)
    └── indexing for RAG
```

---

# 🚀 REAL COST PROFILE (rough)

If using small/cheap model:

* Extraction: ~1 call / chapter
* Fixer: ~1 call / 10–20 chapters (only sometimes)
* Wiki: async, not per ingestion

👉 You can run **novel-scale ingestion for very low cost**

---

# 🔥 If you want next upgrade

I can design:

### 1. Ultra-cheap “open-source only” version (no API dependency)

### 2. LangGraph version of this pipeline

### 3. Real FastAPI + Neo4j + queue implementation

### 4. Or a production-ready folder structure

Just tell me.

Good choice—LangGraph fits this use case really well because your pipeline is **not linear**, it’s a **conditional state machine with batching + retries + async side effects**.

Below is a **production-style LangGraph design** for your:

> Chapter → Events → Graph → Arcs → Wiki (spoiler + omniscient views)

optimized for **low cost + controlled LLM usage**.

---

# 🧠 OVERALL LANGGRAPH DESIGN

We model ingestion as a **stateful graph pipeline**:

```text id="lg0flow"
        ┌────────────────────┐
        │  Chapter Input     │
        └────────┬───────────┘
                 ↓
     ┌──────────────────────────┐
     │ 1. Event Extraction LLM  │  (ONLY expensive step per chapter)
     └────────┬─────────────────┘
              ↓
     ┌──────────────────────────┐
     │ 2. Local Graph Builder   │  (NO LLM)
     └────────┬─────────────────┘
              ↓
     ┌──────────────────────────┐
     │ 3. Entity Resolution     │  (embeddings / rules)
     └────────┬─────────────────┘
              ↓
     ┌──────────────────────────┐
     │ 4. Neo4j Upsert          │
     └────────┬─────────────────┘
              ↓
     ┌──────────────────────────┐
     │ 5. Arc Detection (batch) │  (optional LLM)
     └────────┬─────────────────┘
              ↓
     ┌──────────────────────────┐
     │ 6. Wiki Queue Jobs       │  (async, lazy)
     └──────────────────────────┘
```

---

# 🧱 LANGGRAPH STATE MODEL

```python id="state1"
from typing import TypedDict, List, Dict, Any

class IngestionState(TypedDict):
    chapter_id: str
    chapter_text: str

    events: List[Dict]
    graph_ops: List[Dict]

    resolved_entities: Dict
    neo4j_ops: List[Dict]

    arc_candidates: List[Dict]

    wiki_jobs: List[Dict]

    error: str | None
```

---

# ⚙️ NODE 1 — EVENT EXTRACTION (ONLY LLM COST CENTER)

```python id="node_extract"
def extract_events(state: IngestionState):
    prompt = f"""
Extract atomic events from this chapter.

Return JSON only:
- name
- summary
- characters
- location
- type (present/flashback/dream/rumor)
- order_in_chapter

CHAPTER:
{state["chapter_text"]}
"""

    response = llm.invoke(prompt)  # cheap model preferred
    return {"events": response["events"]}
```

---

# ⚙️ NODE 2 — LOCAL GRAPH BUILDER (NO LLM)

```python id="node_graph"
def build_graph_ops(state: IngestionState):
    ops = []

    for e in state["events"]:
        event_id = f"{state['chapter_id']}_{e['order_in_chapter']}"

        ops.append({
            "op": "MERGE_EVENT",
            "id": event_id,
            "props": e
        })

        for c in e["characters"]:
            ops.append({
                "op": "MERGE_CHARACTER_REL",
                "character": c,
                "event": event_id
            })

    return {"graph_ops": ops}
```

---

# ⚙️ NODE 3 — ENTITY RESOLUTION (LOW COST)

```python id="node_entity"
def resolve_entities(state: IngestionState):
    # embedding-based clustering or simple canonical map
    resolved = {}

    for op in state["graph_ops"]:
        if "character" in op:
            name = op["character"].lower().strip()
            resolved[name] = resolved.get(name, name)

    return {"resolved_entities": resolved}
```

---

# ⚙️ NODE 4 — NEO4J UPSERT (PURE DETERMINISTIC)

```python id="node_neo4j"
def write_to_neo4j(state: IngestionState):
    ops = state["graph_ops"]

    for op in ops:
        if op["op"] == "MERGE_EVENT":
            neo4j.run("""
            MERGE (e:Event {id: $id})
            SET e += $props
            """, op)

        if op["op"] == "MERGE_CHARACTER_REL":
            neo4j.run("""
            MERGE (c:Character {name: $character})
            MERGE (e:Event {id: $event})
            MERGE (c)-[:INVOLVED_IN]->(e)
            """, op)

    return {}
```

---

# ⚙️ NODE 5 — ARC DETECTION (BATCHED + OPTIONAL LLM)

Only run every N chapters or when triggered.

```python id="node_arc"
def detect_arcs(state: IngestionState):
    # cheap clustering first
    clusters = cluster_events(state["events"])

    arc_candidates = []

    for cluster in clusters:
        if len(cluster) < 3:
            continue

        arc_candidates.append(cluster)

    return {"arc_candidates": arc_candidates}
```

---

## OPTIONAL LLM refinement (only for clusters)

```python id="node_arc_llm"
def refine_arcs(state: IngestionState):
    refined = []

    for cluster in state["arc_candidates"]:
        prompt = f"""
Identify narrative arc.

Events:
{cluster}
"""

        refined.append(llm.invoke(prompt))

    return {"wiki_jobs": refined}
```

---

# ⚙️ NODE 6 — WIKI JOB QUEUE (ASYNC)

```python id="node_wiki"
def queue_wiki_jobs(state: IngestionState):
    jobs = []

    for e in state["events"]:
        jobs.append({
            "type": "event_wiki",
            "event_id": e["name"]
        })

    for arc in state.get("arc_candidates", []):
        jobs.append({
            "type": "arc_wiki",
            "data": arc
        })

    return {"wiki_jobs": jobs}
```

---

# 🔁 LANGGRAPH STRUCTURE

```python id="graph1"
from langgraph.graph import StateGraph

graph = StateGraph(IngestionState)

graph.add_node("extract", extract_events)
graph.add_node("build_graph", build_graph_ops)
graph.add_node("resolve", resolve_entities)
graph.add_node("neo4j", write_to_neo4j)
graph.add_node("arc", detect_arcs)
graph.add_node("wiki_queue", queue_wiki_jobs)

graph.set_entry_point("extract")

graph.add_edge("extract", "build_graph")
graph.add_edge("build_graph", "resolve")
graph.add_edge("resolve", "neo4j")
graph.add_edge("neo4j", "arc")
graph.add_edge("arc", "wiki_queue")

app = graph.compile()
```

---

# 🧠 OPTIONAL CONTROL FLOW (IMPORTANT UPGRADE)

You can make arc detection conditional:

```python id="cond1"
def should_detect_arcs(state):
    return len(state["events"]) > 5
```

```python id="cond_edge"
graph.add_conditional_edges(
    "neo4j",
    should_detect_arcs,
    {
        True: "arc",
        False: "wiki_queue"
    }
)
```

---

# 🔥 WHY THIS LANGGRAPH DESIGN IS GOOD

## 1. Cost efficiency

* ONLY 1 LLM call per chapter (extract)
* arc detection is batched
* wiki generation is async

---

## 2. Deterministic core

Everything important (graph building) is **non-LLM**

---

## 3. Scales to novels easily

You can ingest:

* books
* series
* fanfiction corpora

without exponential cost

---

## 4. Natural extension to your spoiler system

You just add:

```python id="spoiler_node"
def add_spoiler_metadata(state):
    for e in state["events"]:
        e["spoiler_level"] = compute_spoiler_level(e)

    return state
```

---

# 🚀 WHAT YOU NOW HAVE

This LangGraph pipeline gives you:

### ✔ Event graph

### ✔ Dual timeline support

### ✔ Arc detection

### ✔ Wiki generation queue

### ✔ Low-cost ingestion

### ✔ Deterministic core + LLM enhancement layer

---

# 🧠 If you want next step

I can extend this into:

### 1. Full production repo structure (FastAPI + LangGraph + Neo4j)

### 2. Spoiler-free vs omniscient wiki generator nodes

### 3. Streaming ingestion (chapter-by-chapter live updates)

### 4. Or a UI design for the wiki + spoiler toggle system

Just tell me.

Great question — this is exactly where most “novel RAG” systems break if you don’t model it properly.

If you just attach **chapter numbers as time**, flashbacks will completely mess up your reasoning.

So you need to separate **two timelines**:

---

# 🧠 The Core Idea: Dual Timeline Model

Every event should have:

### 1. **Narrative time (when it appears)**

* Chapter / scene order
* What the reader sees

### 2. **Story time (when it actually happened)**

* Chronological order inside the story world

---

## ⚙️ Example

A flashback scene in Chapter 10:

json
{
  "event": "Alice meets Ravi",
  "narrative_time": 10,
  "story_time": 2,
  "type": "flashback"
}


So:

* Chapter 10 → narrative timeline
* Actually happened earlier → story timeline

---

# 🔍 How to Detect Flashbacks

You won’t get perfect accuracy automatically — but you can get *very usable* results with structured extraction.

## Step 1: Use LLM classification

When processing a scene, ask:

> “Is this scene:
>
> * present timeline
> * flashback
> * memory
> * dream
> * parallel storyline?”

---

## Step 2: Extract temporal signals

Look for cues like:

* “years ago…”
* “when she was a child…”
* “he remembered…”
* “back then…”

---

## Step 3: Assign relative time

Instead of exact timestamps, use:

* BEFORE event X
* AFTER event Y
* SAME AS current timeline

---

# 🏗️ Graph Schema (important)

If you're using Neo4j, structure events like this:

### Nodes:

* Character
* Event
* Scene

### Relationships:

plaintext
(Event)-[:OCCURS_IN]->(Scene)
(Event)-[:INVOLVES]->(Character)

(Event)-[:BEFORE]->(Event)
(Event)-[:AFTER]->(Event)


### Properties on Event:

json
{
  "narrative_order": 10,
  "story_order": 2,
  "timeline_type": "flashback"
}


---

# 🔥 Better than timestamps: Relative ordering

Absolute time is hard.

👉 Instead, store:

* Event A happens BEFORE Event B
* Event C happens DURING Event D

This is more robust for novels.

---

# 🧠 Retrieval Strategy (this is key)

When answering:

> “Why did Alice stop trusting Ravi?”

### You should:

1. Query **story timeline**

   * find causally earlier events

2. Ignore narrative order unless asked:

   * “when was it revealed?”

---

# ⚡ Handling tricky cases

## 1. Nested flashbacks

Flashback inside flashback:

👉 Add:

json
"depth": 2


---

## 2. Unreliable narration / dreams

Tag events as:

json
"type": "dream" | "imagined" | "rumor"


So you don’t treat them as facts.

---

## 3. Ambiguous time

If unsure:

json
"story_time": "unknown",
"relative": "before major_event_X"


---

# 🧪 Practical LLM prompt (high impact)

When extracting events, use something like:

Extract events from this scene.

For each event:
- What happens?
- Which characters are involved?
- Is this:
  - present
  - flashback
  - memory
  - dream
- When does it occur relative to other events?
- Any time clues?

Return structured JSON.


---

# 🚀 Simple vs Advanced approach

## Simple (works surprisingly well)

* Just tag: flashback = true/false
* Keep narrative order
* Let LLM infer rest

## Advanced (what you’re aiming for)

* Dual timeline
* Relative event graph
* Typed events (real vs memory vs dream)

---

# 🧠 Final takeaway

👉 Don’t treat time as a single axis
👉 Treat it as:

* **“when it’s told”** vs **“when it happened”**

That distinction is what makes your system *feel intelligent* instead of confused.

---

If you want, I can:

* design a **complete Neo4j schema for novels**
* or give you **ready-to-use extraction prompts + code**

Those details will matter more than the choice of framework.


Ee were taking about this and i mentioned I want to also build a dynamic wiki builder 

Nice — a dynamic wiki builder actually fits perfectly on top of the same dual-timeline + event graph idea you were already exploring.

If you design it right, your RAG system stops being “document retrieval” and becomes a living knowledge graph that reorganizes itself.

🧠 Core Idea: Wiki = Structured Views over Your Graph
Instead of storing “wiki pages” as primary data, you treat them as:

generated projections of your event + entity graph

So:

Graph = source of truth

Wiki pages = dynamic views

RAG = query layer over both

🏗️ System Architecture
1. Ingestion Layer (what you already started)
You extract:

Events

Characters

Scenes

Relationships

Timeline info (story + narrative)

This feeds your graph.

2. Knowledge Graph (core backbone)
You’ll want something like:

Nodes
Character

Event

Location

Object

Arc (important for wiki grouping)

Edges
INVOLVED_IN

BEFORE / AFTER

LOCATED_AT

CAUSES

BELONGS_TO_ARC

This is your “truth layer”.

3. Wiki Generator Layer (the missing piece)
This is where your idea becomes powerful.

You generate wiki pages on demand or periodically.

📄 Wiki Page Types
Instead of static pages, you generate types of pages:

1. Character Page
Generated from graph:

Alice

Summary (LLM-generated)

Timeline of key events (story-time ordered)

Relationships graph

Arc participation

Hidden knowledge (what she knows vs what reader knows)

2. Event Page
“Alice meets Ravi”

Narrative occurrences (chapter appearances)

Story-time position

Participants

Consequences (forward edges)

Preceding causes (backward edges)

3. Arc Page (VERY important for novels)
Example:

“Ravi betrayal arc”

Start event

Key escalation events

Reveal event

Resolution event

Characters involved

This becomes your semantic grouping layer.

4. Location Page
Events occurring there

Characters frequently present

Timeline of changes

🔁 Key Innovation: Wiki is Recomputed, not Stored
Instead of saving markdown pages, you do:

WikiPage(character_id) = LLM(graph neighborhood of node)
So every update to graph → wiki updates automatically.

🧠 Retrieval Flow (important for RAG)
When user asks:

“Why did Alice stop trusting Ravi?”

System should:

Step 1: Graph query
find distrust event

trace backward edges (causal chain)

Step 2: Pull subgraph
Alice + Ravi + related events

Step 3: Generate “mini wiki page”
causal explanation

timeline snippet

Step 4: Answer grounded in that
⚡ The Real Trick: Two-Level Memory
You now have:

1. Raw Memory (Graph)
exact events

structured truth

2. Wiki Memory (Derived)
summaries

explanations

human-readable narratives

This prevents hallucination while still allowing abstraction.

🧩 Handling “Dynamic Wiki Behavior”
To make it feel alive:

1. Lazy generation
Only build pages when requested or frequently accessed.

2. Versioning
Store:

wiki_page_version: {
  version: 3,
  generated_at: timestamp,
  graph_snapshot_id: xyz
}
3. Personalization layer (optional later)
Same graph → different wiki views depending on query intent.

🔥 Advanced Upgrade (this is where it gets interesting)
“Wiki as a Query Language”
Instead of static pages:

“Show me Alice before betrayal”

“Show me Ravi from Alice’s perspective”

“Show all hidden knowledge events”

Each becomes a filtered graph projection + LLM summary

🧠 How this connects to your flashback model
Your dual timeline becomes a first-class wiki feature:

“Story timeline view” page

“Chronological truth view” page

“Reader discovery view” page

Same data, different projections.

🚀 Minimal Stack (practical version)
If you want to build fast:

Graph DB: Neo4j / ArangoDB

Event extractor: LLM pipeline

Wiki generator: LLM + templating

API layer: FastAPI / Node

Frontend: React + graph viewer

💡 The key mental shift
You are NOT building:

a wiki system

You are building:

a queryable narrative intelligence layer over a story graph

If you want next step, I can help you design:

a full Neo4j schema for wiki + timeline + arcs

or a prompt pipeline that turns raw chapters → graph → wiki automatically

or even a MVP architecture you can build in 7–10 days

Just tell me where you want to go next.


a full Neo4j schema for wiki + timeline + arcs
or a prompt pipeline that turns raw chapters → graph → wiki automatically

Good — these two pieces are basically the “brain + metabolism” of your system:

Neo4j schema = long-term memory structure

Prompt pipeline = how memory gets created and updated

I’ll give you both, but in a way that actually fits together (most designs fail because they treat them separately).

🧠 PART 1: FULL NEO4J SCHEMA (Wiki + Timeline + Arcs)
This is designed for:

novels

flashbacks

unreliable narration

dynamic wiki generation

🧱 CORE NODE TYPES
1. Character
(:Character {
  id,
  name,
  aliases,
  description,
  first_appearance_chapter
})
2. Event (MOST IMPORTANT NODE)
(:Event {
  id,
  name,
  summary,

  narrative_chapter,
  narrative_order,

  story_time_rank,   // relative ordering
  timeline_type,     // present | flashback | dream | rumor

  confidence,        // LLM confidence
  is_canonical       // true/false (for unreliable narration)
})
👉 This is your dual-timeline anchor:

narrative = “how story is told”

story_time_rank = “what actually happened”

3. Scene
(:Scene {
  id,
  chapter,
  location,
  summary
})
4. Arc (THIS IS YOUR WIKI STRUCTURE LAYER)
(:Arc {
  id,
  name,
  theme,
  summary
})
5. Location
(:Location {
  id,
  name,
  description
})
6. WikiPage (DERIVED NODE — not source of truth)
(:WikiPage {
  id,
  type,          // character | event | arc | location
  title,
  content,
  generated_at,
  version
})
🔗 RELATIONSHIPS (THE REAL POWER)
Timeline relationships
(:Event)-[:BEFORE]->(:Event)
(:Event)-[:AFTER]->(:Event)
👉 This replaces timestamps entirely.

Narrative structure
(:Event)-[:OCCURS_IN]->(:Scene)
(:Scene)-[:IN_CHAPTER]->(:Chapter)
Character involvement
(:Character)-[:INVOLVED_IN {role}]->(:Event)
role examples:

protagonist

witness

cause

victim

Arc structure (VERY IMPORTANT)
(:Arc)-[:STARTS_WITH]->(:Event)
(:Arc)-[:HAS_EVENT]->(:Event)
(:Arc)-[:ENDS_WITH]->(:Event)
Arc participation
(:Character)-[:PARTICIPATES_IN]->(:Arc)
(:Event)-[:BELONGS_TO]->(:Arc)
Causality (this is your “why” engine)
(:Event)-[:CAUSES]->(:Event)
(:Event)-[:RESULTS_IN]->(:Event)
Knowledge separation (advanced but powerful)
(:Character)-[:KNOWS]->(:Event)
(:Character)-[:UNAWARE_OF]->(:Event)
👉 This enables:

spoilers control

POV-based wiki pages

Wiki generation linkage
(:WikiPage)-[:DERIVED_FROM]->(:Character | :Event | :Arc)
🧠 PART 2: PROMPT PIPELINE (RAW CHAPTER → GRAPH → WIKI)
This is where most systems fail. You want a 3-stage LLM pipeline.

⚙️ STAGE 1: CHAPTER → STRUCTURED EVENTS
Input:
Raw chapter text

Prompt:
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

CHAPTER TEXT:
{chapter_text}
Output format:
{
  "events": [
    {
      "id": "auto",
      "name": "...",
      "summary": "...",
      "characters": [],
      "location": "...",
      "timeline_type": "flashback",
      "narrative_order": 3,
      "causes": [],
      "implied_arc": ""
    }
  ]
}
⚙️ STAGE 2: EVENT → NORMALIZATION + GRAPH LINKING
Input:
All extracted events + existing graph context

Prompt:
You are organizing story events into a knowledge graph.

Tasks:

1. Assign story_time_rank (relative chronology)
2. Detect BEFORE / AFTER relationships
3. Identify arcs and group events
4. Resolve duplicate events with existing graph
5. Assign confidence score

Return updated event graph structure.
Output:
{
  "events": [
    {
      "id": "...",
      "story_time_rank": 12,
      "before": ["event_id"],
      "after": ["event_id"],
      "arc": "betrayal_arc",
      "confidence": 0.87
    }
  ]
}
⚙️ STAGE 3: GRAPH → WIKI PAGE GENERATION
This is your “dynamic wiki builder”.

Character Wiki Prompt
Generate a wiki page for this character using graph data.

Include:

- Identity summary
- Timeline of key events (story order)
- Relationships
- Arcs participated in
- Hidden knowledge (what they know vs don't know)

GRAPH DATA:
{character_subgraph}
Event Wiki Prompt
Generate a wiki page for this event.

Include:

- What happened
- Why it happened (causal chain)
- Before / after events
- Characters involved and roles
- Arc context
- Narrative vs story-time explanation

GRAPH DATA:
{event_subgraph}
Arc Wiki Prompt
Generate a narrative arc wiki page.

Include:

- Theme of arc
- Start event
- Key progression events
- Turning point
- Resolution
- Characters involved
- Emotional or thematic evolution

GRAPH DATA:
{arc_subgraph}
🔁 SYSTEM LOOP (IMPORTANT)
Chapter Ingested
   ↓
Event Extraction (Stage 1)
   ↓
Graph Update (Stage 2)
   ↓
Arc Linking + Timeline Ordering
   ↓
Wiki Regeneration (Stage 3)
   ↓
RAG-ready Knowledge Base
🧠 WHY THIS DESIGN WORKS
1. Flashbacks stop breaking your system
Because narrative_time and story_time_rank are separate.

2. Wiki never becomes stale
Because it's always derived from graph

3. You can answer 3 types of questions:
“What happened in chapter 5?” → narrative layer

“Why did X happen?” → causal graph traversal

“What is Alice’s story?” → wiki projection

4. You get multi-perspective storytelling
Same graph can generate:

spoiler-free wiki

full omniscient wiki

character POV wiki

🚀 If you want next step
I can help you design:

1. Real Neo4j Cypher schema (ready to paste)
2. FastAPI ingestion service architecture
3. LangGraph / LlamaIndex pipeline version
4. Or a minimal MVP you can build in 48 hours
Just tell me.


spoiler-free wiki
full omniscient wiki

Spoiler toggle 

Now you’re basically describing a multi-view narrative database, not just a wiki. The spoiler system becomes a filter over the same graph, not separate data.

This is exactly how you make it feel “intelligent” instead of just structured.

🧠 Core Idea: Same Graph, Different Knowledge Views
You do NOT store multiple wikis.

You store:

One truth graph + multiple visibility filters

🔐 1. SPOILER MODEL (THE KEY DESIGN)
Every node (Event, Arc, etc.) gets a reveal status.

Event node extension:
(:Event {
  id,
  name,
  summary,

  story_time_rank,
  narrative_order,

  spoiler_level,   // 0 = safe, 1 = mild, 2 = major spoiler
  reveal_point,    // chapter or event when it becomes known to reader

  timeline_type
})
Example:
Event	spoiler_level	reveal_point
“Alice meets Ravi”	0	Chapter 1
“Ravi is betraying Alice”	2	Chapter 18
“Alice survives attack”	1	Chapter 10
👁️ 2. TWO WIKI MODES
🟢 SPOILER-FREE WIKI (Reader Mode)
Rule:
Only show events where:

reveal_point <= current_reader_progress
or:

spoiler_level == 0
Output behavior:
Hides future twists

Rewrites summaries safely

Replaces unknowns with hints

Example transformation:

FULL: “Ravi betrays Alice in Chapter 18”

Becomes:

SPOILER-FREE: “Ravi’s actions later change Alice’s trust in him”

Important trick:
You don’t just hide data — you re-summarize with LLM

Prompt:

Rewrite this wiki page for a spoiler-free reader.

Rules:
- Do NOT reveal future events
- Preserve emotional meaning
- Use vague references instead of explicit twists
🔵 OMNISCIENT WIKI (God Mode)
Rule:
Show EVERYTHING:

full event graph

all arcs

all future events

hidden motivations

causality chains

No filtering.

Output style:
Explicit betrayals

Full timeline ordering

Cause → effect chains

Character hidden knowledge exposed

🎛️ 3. SPOILER TOGGLE SYSTEM
This is just a graph query filter switch.

API-level design
{
  "wiki_type": "character",
  "entity_id": "alice",
  "mode": "spoiler_free" | "omniscient",
  "reader_progress": 12
}
Backend logic:
If SPOILER-FREE:
MATCH (e:Event)-[:INVOLVES]->(c:Character {id:$id})
WHERE e.reveal_point <= $reader_progress
RETURN e
Then pass to LLM → rewrite safely.

If OMNISCIENT:
MATCH (e:Event)-[:INVOLVES]->(c:Character {id:$id})
RETURN e
No filtering.

🧠 4. CRITICAL DESIGN INSIGHT
You are not building:

“two wikis”

You are building:

a single narrative graph with visibility semantics

🧩 5. BONUS: “CHARACTER KNOWLEDGE SPOILER MODE”
This is where it gets really powerful.

You can also filter by POV awareness:

(:Character)-[:KNOWS]->(:Event)
So you can generate:

“Alice wiki”
what Alice knows

vs
“Reader wiki”
what reader knows

vs
“Omniscient wiki”
everything

🔥 6. THREE-WAY VIEW SYSTEM
Mode	What it shows
Spoiler-Free Wiki	Safe narrative progression
Character Wiki	Subjective knowledge
Omniscient Wiki	Full truth graph
⚡ 7. THE REAL MAGIC (IMPORTANT)
Because everything is derived from the same graph:

You can dynamically generate:
“What would Alice believe right now?”

“What does the reader not know yet?”

“What is the full truth of this arc?”

All without duplicating data.

🚀 If you want next step
I can help you design:

1. Full Cypher schema for spoiler + knowledge tracking
2. LangGraph pipeline that auto-generates both wiki modes
3. UI design for spoiler toggle (very important UX problem)
4. Or a minimal MVP architecture (FastAPI + Neo4j + LLM)
Just tell me where you want to go next.


Give me a low cost ingestion pipeline 

A low-cost ingestion pipeline for this kind of chapter → graph → dual wiki system is mostly about one thing:

minimizing LLM calls while maximizing structured reuse

If you design it badly, every chapter becomes 5–10 expensive calls.
If you design it well, you can get it down to 1–2 small calls per chapter + batching.

🧠 LOW-COST INGESTION PIPELINE (PRINCIPLED DESIGN)
🔁 High-level flow
Chapter Text
   ↓
(1) Cheap extraction pass (single LLM call)
   ↓
(2) Deterministic graph builder (no LLM)
   ↓
(3) Batch embedding + dedup
   ↓
(4) Optional second-pass “fixer” (only if needed)
   ↓
Neo4j update
   ↓
Async wiki generation (lazy)
⚙️ STEP 1 — SINGLE LOW-COST EXTRACTION CALL (MOST IMPORTANT)
Goal:
Replace multi-step extraction with one structured pass

Use a cheap model (or small-context model).

Prompt (optimized for cost)
Extract structured information from this chapter.

Return JSON ONLY.

Split into atomic EVENTS.

For each event:

- name
- 1-line summary
- characters (names only)
- location (if any)
- type: present | flashback | dream | rumor
- order_in_chapter (integer)
- temporal cues (optional short text)
- implied causality (only if obvious)

Do NOT:
- write explanations
- do not infer deeply
- do not create arcs yet

CHAPTER:
{text}
Why this is cheap:
no reasoning-heavy tasks

no graph building

no summarization

just structured extraction

👉 This is your 80% cost reduction step

⚙️ STEP 2 — DETERMINISTIC GRAPH BUILDER (NO LLM)
Now you convert JSON → graph locally.

Rules:
create Event nodes

link to Characters (MERGE nodes)

preserve chapter order

assign provisional IDs

Example logic:
for event in events:
    MERGE (e:Event {id})
    SET e.narrative_order = event.order_in_chapter

    for character in event.characters:
        MERGE (c:Character {name})
        MERGE (c)-[:INVOLVED_IN]->(e)
Why this matters:
✔ zero LLM cost
✔ fast ingestion
✔ repeatable
✔ safe (no hallucination)

⚙️ STEP 3 — LIGHTWEIGHT ENTITY RESOLUTION (BATCHED)
Instead of asking LLM:

“is Ravi the same as R. Ravi?”

You do:

Embedding-based clustering (cheap + scalable)
embed character names

cosine similarity

merge if threshold > 0.92

Use:

sentence-transformers (local)

or cheap embedding API

⚙️ STEP 4 — OPTIONAL “FIXER PASS” (ONLY FOR HARD CASES)
Instead of running a second LLM pass always:

👉 only trigger when ambiguity detected:

triggers:
conflicting timelines

missing characters

unclear flashback tagging

duplicate events suspected

Fixer prompt:
You are correcting a story graph.

Given extracted events and relationships:
- resolve duplicates
- fix timeline ordering
- correct flashback classification

Do NOT re-extract everything.

Only modify errors.
⚙️ STEP 5 — ARC DETECTION (BATCHED, NOT PER CHAPTER)
THIS is where people waste money.

❌ Wrong: detect arcs per chapter
✅ Right: detect arcs every N chapters (e.g. 5–10)

Cheap heuristic first:
Before LLM:

cluster events by:

shared c