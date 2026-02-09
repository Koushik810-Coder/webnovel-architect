# Webnovel Architect

**Turning evolving web novels into living audio dramas — with a built-in story wiki.**

Webnovel Architect is a backend system that converts ongoing web novels into consistent, high-quality audio by **understanding the story world before generating sound**.  
Unlike traditional TTS or audiobooks, it maintains a persistent **living wiki** of characters and story canon, ensuring both readers and audio listeners experience a coherent, immersive world.

---

## The Problem

- Web novels are published **incrementally** (daily / weekly chapters)
- Audiobooks require a **finished manuscript**
- Generic TTS systems:
  - Do not understand who is speaking
  - Assign inconsistent or inappropriate voices
  - Break immersion as characters reappear
- Wikis are often:
  - Manually maintained
  - Out of sync with the story
  - Disconnected from audio adaptations

---

## The Solution

Webnovel Architect introduces a **Story Intelligence Layer** that powers **both audio generation and a living story wiki**.

Instead of directly converting text to speech, the system:
- Tracks characters persistently across chapters
- Builds a reader-facing wiki from the story itself
- Measures narrative importance over time
- Assigns and locks voices only when the system is confident
- Keeps audio and canon synchronized automatically

Audio and wiki pages become **derived artifacts** from the same source of truth.

---

## Core Concept: Living Character Wiki

Every character exists in two clearly separated forms:

### 1. Character Wiki (Reader-Facing Canon)
The wiki is designed for **readers**, not machines.

It contains:
- Display name and aliases
- Narrative descriptions (short & long)
- Role in the story (protagonist, antagonist, mentor, etc.)
- Affiliations, species, age, appearance
- Personality traits and notable quirks
- First appearance and current status
- Confidence score indicating canon certainty

Key properties:
- Human-readable
- Editable with approval
- Safe for public display
- Resistant to AI hallucination

---

### 2. Character Runtime (System-Facing Intelligence)
The runtime model exists purely for **system logic**.

It tracks:
- Chapter appearances
- Dialogue volume
- Presence-based confidence score
- Graduation level
- Locked voice assignment

The wiki and runtime are linked only by a stable `character_id`.

> **Canon serves the reader.  
> Runtime serves the machine.  
> They never overwrite each other.**

---

## Voice Graduation System

Characters “earn” voices as their importance becomes clear.

### Graduation Levels
- **Extra**
  - One-off or background characters
  - No unique voice

- **Evolving**
  - Recurring characters
  - Tracked but not yet cast

- **Main Cast**
  - Proven narrative importance
  - Assigned a unique, locked voice

Graduation is:
- Quantitative (based on presence, not guesses)
- Explainable
- Replayable
- Vendor-agnostic

---

## Architecture Overview

### 1. Incremental Chapter Processing
- Chapters are ingested as they are written
- Characters accumulate appearances
- Confidence grows deterministically
- No premature voice or trait assignment

---

### 2. Wiki + Runtime Synchronization
- AI may **propose** wiki updates
- Humans **approve** canon changes
- Full auditability and rollback capability
- Wiki stays in sync with story progression

---

### 3. Provider-Agnostic Voice Layer
- Voice assignment is abstracted behind a clean interface
- ElevenLabs, OpenAI Audio, or local TTS can be swapped freely
- Core logic never depends on a specific vendor

---

### 4. Narration Pipeline
- Chapter text is split into narration vs dialogue
- Speakers are resolved deterministically
- Each segment is assigned:
  - Narrator voice, or
  - Character-specific locked voice
- Audio generation is a final rendering step

---

## Current Features

- Chapter ingestion API
- Manual character creation
- **Living character wiki**
- Runtime character tracking
- Confidence-based graduation
- Voice provider abstraction
- Narration segmentation & speaker resolution
- End-to-end narration → audio pipeline (stubbed audio)

---

## Tech Stack

- **Backend:** Python, FastAPI
- **Data Models:** Pydantic
- **Architecture:** Pipeline-based, replayable stages
- **Audio:** Provider-agnostic (dummy provider currently)
- **State:** In-memory (persistence planned)

---

## Roadmap

### Near Term
- Persist wiki & runtime state (SQLite / PostgreSQL / MongoDB)
- Real TTS provider integration
- Audio file generation & storage

### Mid Term
- Semantic trait accumulation
- Wiki revision history & approvals
- Spoiler-aware wiki views

### Long Term
- Multi-language audio & wiki
- Emotion & prosody control
- Game, animation, and localization pipelines

---

## Design Principles

- **Canon is sacred**
- **Audio is a derivative artifact**
- **Wiki and runtime are separate concerns**
- **AI proposes, humans approve**
- **No silent state mutation**
- **Everything is replayable**

---

## One-Line Summary

**Webnovel Architect is a story intelligence engine that powers both a living character wiki and consistent audio adaptations for evolving web novels.**

---

## Status

Architecture complete and versioned.  
Actively evolving.

Contributions, discussion, and experimentation welcome.
