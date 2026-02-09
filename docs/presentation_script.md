# Webnovel Architect: Project Review Presentation Script

**Presenter**: Team [Project Name]
**Date**: 2026-01-28
**Topic**: Zero-GPU Modular Architecture Review

---

## Slide 1: Title Slide
**Visual**: 
- Large Title: **Webnovel Architect**
- Subtitle: *Turning Evolving Web Novels into Living Audio Dramas*
- Status tag: "Zero-GPU Architecture Pivot"

**Speaker Notes**:
"Hi everyone. Today we’re reviewing the current state of **Webnovel Architect**. 
Our mission is simple but ambitious: we want to bridge the gap between written serial storytelling and high-quality audio adaptations. 
We've recently pivoted our architecture to a 'Zero-GPU' modular approach to make this technology accessible and scalable. Let’s dive in."

---

## Slide 2: The Vision
**Visual**:
- A split screen image. 
- Left side: An author typing a chapter. 
- Right side: A listener hearing the audio drama version instantly.
- Text overlay: **"Story Intelligence"**

**Speaker Notes**:
"The core vision is to create a 'Story Intelligence' engine. 
Unlike traditional audiobooks that require a finished manuscript, our system reads *along with* the author. 
It tracks characters, builds a wiki in real-time, and assigns voices dynamically. 
We are effectively automating the production studio for web serials."

---

## Slide 3: The Problem
**Visual**:
- Two bold bullet points with icons:
    1.  **The Casting Paradox** (Icon: A question mark over a silhouette)
    2.  **Wiki Decay** (Icon: A crumbling book)

**Speaker Notes**:
"We are solving two specific problems inherent to serial writing.
First, the **Casting Paradox**. In a webnovel, a character appearing in Chapter 1 might be a throwaway extra or the main villain by Chapter 50. If you cast a premium voice actor too early, you burn budget. If you cast too late, you have inconsistent audio.
Second, **Wiki Decay**. With thousands of chapters, manual wikis are perpetually out of date, leading to reader confusion and increased cognitive load for the author."

---

## Slide 4: The Solution: "Graduation"
**Visual**:
- A flowchart showing the "Graduation" mechanism.
- "Unknown Character" -> "Importance Score Calculation" -> "Threshold Passed?"
- **No** -> Generic TTS (EdgeTTS)
- **Yes** -> Locked Unique Voice (Kokoro-82M)

**Speaker Notes**:
"Our solution is the **Graduation System**. 
We don't treat every character equally. We calculate an 'Importance Score' based on:
1.  **Graph Centrality** (How connected are they?)
2.  **Event Impact** (Did they change the plot?)
3.  **Recency**
Only when a character 'graduates' past a certain score do they get assigned a permanent, high-quality neural voice. Everyone else gets a lightweight generic voice. This optimizes compute resources and narrative focus."

---

## Slide 5: The "Zero-GPU" Architecture
**Visual**:
- Diagram of the **"Switchboard"** pattern.
- Center: **Router / Main Controller**
- Connecting to removable blocks (Adapters):
    - **Brain**: LiteLLM (Gemini Flash / Llama 3)
    - **Voice**: TTS Factory (Kokoro / EdgeTTS)
    - **Memory**: Graph (NetworkX / Neo4j)

**Speaker Notes**:
"Technically, the biggest shift is our **Zero-GPU Modular Architecture**.
We realized hard-coding models was a trap. Models change every week. 
So we built a 'Switchboard'. The core system doesn't know *which* model it's using. It just asks via an Adapter.
This allows us to run entirely on a CPU today using efficient models like **Kokoro (82M)** and **Gemini Flash**, but we can swap in massive enterprise models tomorrow by just changing one line in a config file. No code refactoring needed."

---

## Slide 6: Implementation Status
**Visual**:
- Checklist Graphics:
    - [x] **Switchboard Infrastructure** (Done)
    - [x] **Adapter Plugins** (LLM, TTS, Graph) (Done)
    - [x] **Ingestion Logic** (Done)
    - [ ] **Advanced Verification** (In Progress)

**Speaker Notes**:
"Where are we right now?
The infrastructure is complete. The 'Switchboard' is live. 
We have working adapters for our LLMs, our TTS engine, and our Graph memory.
The core ingestion logic—reading the text and processing it—is refactored to use these adapters.
We are currently focusing on verification to ensure seamless engine switching under load."

---

## Slide 7: Research Alignment & Roadmap
**Visual**:
- Timeline style graphic.
- **Now**: Modular Base
- **Next**: 
    - **xCoRe**: Book-scale entity tracking.
    - **NexusSum**: Complex summarization agents.
    - **Audiobook-CC**: Context-aware prosody.

**Speaker Notes**:
"Our roadmap is heavily informed by state-of-the-art research from late 2024 and 2025.
We are looking to implement **xCoRe** for better entity tracking across long books.
We're also exploring **NexusSum** for better summaries and **Audiobook-CC** to make the voices sound more emotionally aware of the scene context.
We are building a research-backed engine, not just a wrapper."

---

## Slide 8: Conclusion
**Visual**:
- "Webnovel Architect" Logo (Text based)
- Link to Repository / Documentation
- "Questions?"

**Speaker Notes**:
"In summary, Webnovel Architect is ready to scale. 
We have a flexible, cost-effective architecture that solves the specific pain points of serial fiction.
We are ready to onboard more chapters and test the boundaries of our Story Intelligence.
Thank you. I'm happy to take any questions."
