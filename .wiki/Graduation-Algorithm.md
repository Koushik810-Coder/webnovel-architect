# ⚖️ The Graduation Algorithm

The core academic contribution of Webnovel Architect is solving the **Casting Paradox**: how to assign high-quality, permanent voice actors to characters efficiently as a story evolves over hundreds of chapters without manual human tagging.

---

## 1. Temporal Decay PageRank

In standard graph theory, PageRank measures node centrality based on connection density. However, webnovels are chronological. A character who dominates Chapters 1-10 but dies in Chapter 11 will still have a massive, static PageRank in Chapter 100, stealing resources.

To solve this, we inject **Narrative Time**:

```text
Score(c) = PageRank(c) × N × (1 - λ)^Δt
```

Where:
- `PageRank(c)` = Standard network centrality.
- `N` = Total node count in the graph (prevents density deflation).
- `λ` = Decay Rate (Default: 0.15).
- `Δt` = Chapters elapsed since the character's last appearance.

If a character is absent for several chapters, their influence exponentially degrades, freeing up resources for new characters.

---

## 2. DPQ (Debut Prominence Quotient)

PageRank requires a dense graph to propagate accurately. A brand-new main character introduced in Chapter 50 will start with a PageRank near zero, resulting in them receiving a generic background voice. This breaks immersion.

The **Debut Prominence Quotient (DPQ)** bypasses this by analyzing the localized, single-chapter sub-graph. 

```python
dpq_score = character_event_participation / total_chapter_events
```

If a character's `DPQ ≥ 0.40` (they are involved in ≥ 40% of the narrative action in their debut chapter), they are granted a **Provisional Graduation Bpyass**. They immediately receive a premium voice lock. 

If they disappear in subsequent chapters, Temporal Decay will quickly pull them below the threshold, and their voice ID will be recycled.

---

## 3. Voice Locking & Continuity

When a character's `Score > 5.0` (or `DPQ > 0.40`), they enter the `MAIN_CAST`. 

1. The `VoiceRegistry` assigns them a Kokoro TTS voice (e.g., `af_bella`).
2. This assignment is **locked** in `voices.json` and in their `CharacterWiki`.
3. Even if their score fluctuates in the future, their voice remains consistent to preserve auditory continuity for the listener. 
4. The lock is only broken if their score drops below the permanent release threshold (`δ_lower = 0.3`).

---

*→ Next: [Evaluation Results](Evaluation-Results)*
