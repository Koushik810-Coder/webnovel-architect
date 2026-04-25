# CHAPTER - 1

# INTRODUCTION

## 1.1 Introduction
Serialized web fiction has emerged as a rapidly growing segment in digital publishing, with platforms hosting large-scale, long-running narratives. Transforming such content into high-quality multi-speaker audio drama introduces complex challenges, particularly in maintaining consistent voice assignments for characters across extended timelines. A key issue in this domain is the Casting Paradox, where voice assignment decisions must be made before sufficient narrative evidence is available to determine a character's importance. Existing Retrieval-Augmented Generation (RAG) systems fail to address this due to their lack of temporal awareness, leading to issues such as temporal hallucination. To overcome these challenges, this study proposes Webnovel Architect, a neuro-symbolic framework that integrates semantic understanding with temporal reasoning using a Dynamic Graph-RAG (DyG-RAG) approach for efficient and accurate audio synthesis.

## 1.2 Background of the Study
Recent advancements in AI, particularly in RAG systems, Text-to-Speech (TTS), and knowledge graphs, have significantly improved automated content processing. Traditional vector-based RAG models rely on similarity search but lack the ability to represent temporal progression in narratives. Dynamic Graph RAG systems introduced time-aware structures, but they primarily focus on factual updates rather than narrative evolution. Similarly, zero-shot TTS models enable expressive speech synthesis but require predefined speaker identities, creating a gap in automated voice assignment. Previous works in character tracking and NLP, such as BookNLP, focus on post-hoc analysis rather than real-time processing of serialized content. These limitations highlight the need for a system that combines semantic extraction with temporal reasoning, forming the foundation for this research.

## 1.3 Problem Statement

Existing systems for automated audio dramatization face a critical limitation in handling long-form serialized narratives.

- RAG systems are **temporally agnostic**, causing outdated characters to remain relevant (temporal hallucination).
- TTS systems require predefined speaker identities, which are unavailable during early narrative stages.
- Assigning voices to all characters leads to resource inefficiency and system overload.
- Thus, the main problem addressed in this study is: How to accurately assign and manage character voices in serialized fiction while preserving temporal consistency and avoiding hallucination effects**.**

## 1.4 Objectives

### 1.4.1 General Objective

To design and develop a **neuro-symbolic framework (Webnovel Architect)** that enables efficient and temporally accurate audio dramatization of serialized web fiction.

### 1.4.2 Specific Objectives

- To eliminate temporal hallucination using a **timed-decay mechanism**.
- To implement a **Dynamic Graph-RAG (DyG-RAG)** model for temporal reasoning.
- To develop the **Debut Prominence Quotient (DPQ)** for proactive voice assignment.
- To integrate neural (semantic) and symbolic (temporal) components for improved performance.
- To ensure the system operates efficiently on consumer-grade CPU hardware without requiring a GPU.

## 1.5 Scope of the Work

This study focuses on designing and evaluating a neuro-symbolic system for serialized fiction audio synthesis.

Scope includes:

- Character extraction using neural models
- Temporal tracking using graph-based symbolic methods
- Voice assignment through DPQ mechanism
- Evaluation using a limited dataset (five chapters of a web novel)

Limitations:

- Small evaluation dataset
- Fixed decay rate and thresholds
- Chapter-level processing without overlapping context

The system does not cover large-scale deployment or full-length novel processing in this phase.

## 1.6 Significance of the Study

This research contributes to both academic and practical domains by introducing a novel approach to combining neural and symbolic AI for narrative understanding.

- Eliminates **temporal hallucination**, improving accuracy in AI systems
- Enables **cost-efficient audio production** without GPU dependency
- Supports content creators and audiobook producers with scalable solutions
- Advances research in Graph-RAG, NLP, and AI-driven storytelling

Overall, the study provides a foundation for next-generation intelligent systems in automated storytelling and audio synthesis.a

## 1.7 Organization of the Report

This report is structured as follows:

- **Chapter 1** presents the introduction, background, problem statement, objectives, scope, and significance of the study.
- **Chapter 2** reviews related work in RAG systems, TTS, and character tracking.
- **Chapter 3** covers System Analysis, including the existing system landscape, proposed neuro-symbolic architecture, system requirements, and feasibility study.
- **Chapter 4** presents the Software Requirements Specification (SRS), covering functional requirements, non-functional requirements, hardware requirements, and software dependencies.
- **Chapter 5** details the Design and Methodology of the Proposed System, including the four-layer architecture, UML diagrams, database schema, and flowcharts.
- **Chapter 6** covers Implementation, describing all technologies used and providing a detailed module-by-module breakdown of the codebase with key code snippets.
- **Chapter 7** describes the Testing methodology, including unit tests, integration tests, performance benchmarks, and the complete test case results for all 20 functional test cases.
- **Chapter 8** presents the Results and Discussion, including output screen descriptions, performance evaluation, comparison with existing systems, and analysis of system limitations.
- **Chapter 9** concludes the study, summarizing all achieved objectives and technical contributions, and outlines ten future research directions for extending the system.

# CHAPTER - 2

# BACKGROUND AND LITERATURE REVIEW

## 2.1 Introduction
This chapter reviews existing research in five critical areas underpinning the Webnovel Architect project: (1) Named Entity Recognition and Information Extraction from natural language text, (2) Knowledge Graph construction and temporal reasoning, (3) PageRank and centrality measures for graph-based importance scoring, (4) Text-to-Speech synthesis for audio production, and (5) Retrieval-Augmented Generation for knowledge-grounded question answering.

The review identifies the state of the art in each area, highlights limitations of existing work, and establishes the research gap that Webnovel Architect fills. No single existing system covers the complete intersection of all five areas -- making the design of Webnovel Architect a novel contribution to both academic NLP research and practical applied AI engineering.

## 2.2 Review of Existing Systems
### 2.2.1 Named Entity Recognition (NER) Systems
The field of Named Entity Recognition has matured significantly since the introduction of CoNLL 2003 benchmark datasets. Early systems relied on hand-crafted rules and gazetteers -- lists of known entity names. The introduction of Conditional Random Fields (CRF) by Lafferty et al. (2001) brought a major improvement by modeling sequential dependencies in text. Modern deep learning approaches, particularly BERT-based systems (Devlin et al., 2018), have pushed F1 scores above 93% on news domain benchmarks like CoNLL-2003.

spaCy (Honnibal and Montani, 2017) is the industry-standard NLP library combining transformer-based NER with a highly optimized Cython pipeline. The spaCy en_core_web_sm model achieves approximately 85% F1 on general domain text but drops below 50% F1 on fantasy fiction text due to domain mismatch. The EntityRuler component introduced in spaCy 3.0 allows rule-based entity patterns to be layered on top of the statistical NER model, enabling domain adaptation without retraining.

For Webnovel Architect, we extend spaCy's pipeline with a custom EntityRuler containing 20+ domain-specific patterns covering fantasy titles (Lord, Lady, Elder), rank systems (Tier-X, Level N, Inner/Outer Disciple), magic systems (Mana Core, Spirit Root), factions (X Sect, Y Clan), and apostrophe-containing fantasy names.

### 2.2.2 Large Language Models for Information Extraction**

**GPT-4 (OpenAI, 2023) and Gemini (Google DeepMind, 2024) have demonstrated remarkable zero-shot and few-shot capabilities in structured information extraction when prompted with detailed JSON schemas. Research by Wadhwa et al. (2023) showed that LLM-based relation extraction outperforms fine-tuned BERT models on out-of-domain data, validating the use of LLMs for fantasy domain extraction.

LiteLLM (2023) is an open-source unified interface library that enables seamless switching between 100+ LLM providers using a single API call. This makes it ideal for the Switchboard Architecture of Webnovel Architect, where LLM providers can be swapped via configuration without code changes.

Google Gemini 2.5 Flash (2024) is a lightweight, fast multimodal model optimized for code and structured data tasks. Groq's Llama-3.1-8B-Instant runs on custom LPU hardware delivering sub-second inference -- making it ideal as a fallback when primary API quotas are exceeded.

### 2.2.3 Knowledge Graphs and Narrative Representation

Knowledge graphs (KGs) represent entities and relationships as nodes and edges in a graph structure. Freebase (Bollacker et al., 2008) and Wikidata (Vrandecic and Krotzsch, 2014) demonstrated the power of large-scale KGs for general knowledge representation. For narrative understanding specifically, work by Garg et al. (2020) on Narrative Graphs showed that event-centric graph structures capture story progression and character development more effectively than flat document representations.

The concept of Dynamic Event Units (DEUs) in Webnovel Architect is inspired by the Dynamic Graph (DyG) framework, where graph structure evolves over time as new information (chapters) arrives. Each DEU captures: action_summary, involved_characters, pre_conditions, post_conditions, location, and causal_links to subsequent events.

NetworkX (Hagberg et al., 2008) is the primary Python library for graph analysis. It provides NetworkX.DiGraph (directed graph), PageRank computation via networkx.pagerank, and JSON serialization for persistence -- all leveraged in Webnovel Architect.

**2.2.4 PageRank and Character Importance Scoring**

PageRank (Page et al., 1999) was originally developed to rank web pages by computing the probability that a random web surfer visits a page. It has since been applied to academic citation networks, social influence analysis, and NLP tasks including keyphrase extraction (TextRank, Mihalcea and Tarau, 2004).

In Webnovel Architect, we apply PageRank to the character-event bipartite graph. Characters with more event participations receive higher PageRank scores, as do characters who participate in events causally linked to other important events. A character's score grows as the story progresses and as they interact with more characters and events.

The Temporal Decay mechanism (score multiplied by (1.0 - decay_rate)^age) was inspired by time-aware PageRank variants in social network analysis (Walker et al., 2007). A character who was important 20 chapters ago but absent recently should not maintain full relevance.

**2.2.5 Text-to-Speech Systems**

WaveNet (van den Oord et al., 2016) demonstrated that raw audio waveforms could be modeled autoregressively, producing near-human-quality speech. Tacotron 2 (Shen et al., 2018) and FastSpeech 2 (Ren et al., 2020) introduced faster, non-autoregressive synthesis.

Kokoro (2024) is an 82-million parameter ONNX-format model running entirely on CPU, producing studio-quality English speech at faster-than-real-time rates. It supports multiple voice styles including American and British English accents and gender variants, making it ideal for multi-character audiobook production.

Microsoft Edge TTS (2023) leverages Microsoft Azure's cloud-based neural TTS service, offering 300+ voices across 100+ languages. It serves as a reliable zero-cost fallback when Kokoro model files are unavailable.

**2.2.6 Retrieval-Augmented Generation (RAG)**

Lewis et al. (2020) introduced Retrieval-Augmented Generation (RAG) as a method combining dense retrieval with a sequence-to-sequence LLM generator. The key insight is that LLMs have fixed knowledge cutoffs and are prone to hallucination, but can produce accurate, grounded answers when provided relevant retrieved context.

Standard RAG systems retrieve document chunks based on semantic similarity (cosine similarity of embedding vectors). However, for story Q&A, semantic similarity alone is insufficient. Asking 'What happened to Aria first?' requires chronological ordering of retrieved events, not just semantic relevance.

Webnovel Architect implements Time-Chain-of-Thought (Time-CoT) RAG, inspired by work on temporal reasoning in NLP. Rather than embedding-based retrieval, it traverses the knowledge graph to find events involving queried characters, sorts them by chapter_id (chronological order), and presents them as a structured timeline to the LLM.

## 2.3 Limitations of Existing Systems
### LIMITATION 1-- Domain Adaption Gap in NER:
All major pre-trained NER models are trained on news and Wikipedia corpora. Fantasy fiction texts contain proper nouns with no semantic cues for standard models. Published benchmarks show 40-50% reduction in F1 score when applying these models to fantasy text without adaptation. Webnovel Architect mitigates this with custom EntityRuler patterns and optional LLM Extraction.

LIMITATION 2 -- Single-Voice TTS Limitation:
No existing automated audiobook tool differentiates character voices. Amazon Polly and Google TTS offer multiple voices but require manual script markup -- an impractical approach when processing 5,000-word chapters automatically. Webnovel Architect solves this by voice-locking characters to specific voices based on their graduation status.

LIMITATION 3 -- Static Document Assumption:
NLP pipelines including state-of-the-art LangChain document loaders assume a complete, static document corpus. They lack mechanisms to incrementally update internal state as new chapters arrive. Webnovel Architect is fundamentally designed for incremental processing.

LIMITATION 4 -- Temporal Blindness in Standard RAG:
FAISS-based, Chroma-based, and Pinecone-based RAG systems retrieve by semantic similarity without temporal awareness. For narrative Q&A, this fails when the answer requires understanding sequence: 'Who did Aria meet before she discovered the artifact?' cannot be answered by semantic similarity alone.

LIMITATION 5 -- No Character Consistency Management:
Existing TTS tools have no concept of character identity persistence. If a user generates audio for Chapter 1 with voice A for character Aria, then generates Chapter 2 the next day, Aria may receive a different voice. Webnovel Architect's voice-locking mechanism solves this.

LIMITATION 6 -- GPU Dependency:
State-of-the-art multi-speaker TTS models require GPU inference, making them inaccessible on standard laptops. Webnovel Architect's Zero-GPU design ensures accessibility without specialized hardware.

## 2.4 Research Gap and Novelty
The literature review reveals a clear research gap: no existing system combines all of the following capabilities in a unified, zero-GPU pipeline:

(1) Incremental chapter-by-chapter processing with persistent memory across sessions.
(2) Domain-adapted NER for fantasy fiction using hybrid rule-based and LLM approaches.
(3) Dynamic Knowledge Graph with character-event relationships, causal links, and DEU structure.
(4) Temporal PageRank with decay for automatic character importance scoring.
(5) Automatic voice locking for multi-character audio consistency across chapters.
(6) Time-Chain-of-Thought RAG for temporally-aware story Q&A.
(7) Dual-extraction pipeline allowing users to choose speed (spaCy) vs. accuracy (LLM).
(8) Modular Switchboard Architecture allowing any LLM or TTS engine to be swapped via config.

Webnovel Architect fills this complete gap. While individual components exist in isolation, their integration into a coherent serial-fiction-processing system with temporal intelligence has not been previously achieved.

NOVELTY OF THE DEU SCHEMA:
The DEU schema -- capturing action_summary, involved_characters, pre_conditions, post_conditions, location, and causes_event_indexes -- provides a richer narrative representation than simple event-mention approaches in prior narrative graph work. The causal link structure enables logical reasoning chains: Event A caused Event B which caused Event C.

## 2.5 Summary
The literature review yields five key insights that directly influenced the design: INSIGHT 1: Rule-based NER augmentation is essential for fantasy domains. A custom EntityRuler improves character extraction F1 by an estimated 25-30 percentage points compared to vanilla spaCy NER on fantasy text. INSIGHT 2: Knowledge graphs with causal edge structures are the most suitable representation for story events. Flat document storage or vector embeddings alone cannot capture the temporal and causal dependencies that define narrative progression. INSIGHT 3: PageRank centrality is a validated, mathematically grounded method for measuring node importance in a graph. Combined with temporal decay, it provides a principled mechanism for automatic main character detection. INSIGHT 4: LLMs excel at structured extraction when provided precise JSON schemas and few-shot examples. The json_object response format in modern LLM APIs eliminates markdown parsing overhead. INSIGHT 5: Zero-GPU TTS is viable for production-quality audio. Kokoro ONNX achieves a Real-Time Factor of approximately 0.42 on Intel Core i7 processors, making local audiobook generation practical without GPU hardware.

# CHAPTER - 3

# SYSTEM ANALYSIS

## 3.1 Existing System
### 3.1.1 Traditional Audiobook Production
The traditional audiobook production workflow follows a sequential, human-intensive process:
Step 1: Author completes the full manuscript (typically 80,000-120,000 words).
Step 2: Publisher contracts a professional voice actor (cost: \$200-\$400 per finished audio hour).
Step 3: Voice actor records in a soundproof studio over days or weeks.
Step 4: Audio engineer edits, masters, and produces the final MP3 files.
Step 5: Publisher distributes to Audible, Storytel, etc.
Total time from manuscript to published audio: 3-6 months. Total cost: \$5,000-\$50,000 per title.
This pipeline is entirely incompatible with serial web novels publishing 1-3 chapters per week.

### 3.1.2 Automated Single-Voice TTS Solutions
Tools such as the built-in Royal Road TTS reader, Amazon Polly integrations, and Epub-to-audio converters provide automated text-to-speech but:
- All characters speak in the same voice, making dialogue confusing.
- No understanding of narrative structure or character differentiation.
- No memory across chapters -- each chapter processed in isolation.
- No character tracking, wiki generation, or story Q&A.

### 3.1.3 Fan Wiki Systems (Fandom.com)

Platforms like Fandom.com allow fans to manually create and maintain wikis. While these provide rich character databases for popular series, they:
- Require significant volunteer effort (hours per chapter for popular series).
- Are unavailable for new or lesser-known series with small fanbases.
- Contain no automated extraction -- all content is manually typed.
- Have no integration with audio or Q&A systems.

###

### 3.1.4 Standard NLP Document Analysis Tools
LangChain, LlamaIndex, and similar document Q&A frameworks:
- Treat each chapter as an independent document with no cross-chapter memory.
- Lack narrative-specific data structures (no character graph, no event causality).
- Cannot generate character wikis or audiobooks.
- Have no temporal reasoning in their retrieval.

| **Feature** | **Traditional Systems** | **Automated TTS Systems** | **Fan Wiki Systems** | **NLP QA Systems** |
|---|---|---|---|---|
| Multi-voice Audio | Yes (Expensive) | No | N/A | N/A |
| Serial Processing | No | Partial | Manual | No |
| Character Tracking | No | No | Manual | No |
| Story Q&A | No | No | No | Yes (Poor) |
| Cost | Very High | Low | Free | Medium |

## 3.2 Proposed System
Webnovel Architect proposes a neuro-symbolic AI pipeline that processes web novel chapters incrementally, producing real-time audio dramas, character wikis, and graph-based Q&A, all on standard laptop hardware without GPU requirements.

### 3.2.1 Metaphorical System Overview

The system is built around four metaphorical subsystems:
'The Eye' (Ingestion Engine): reads and pre-processes raw chapter text from multiple sources.
'The Brain' (Story Intelligence): understands and structures content into the knowledge graph.
'The Director' (Graduation Engine): decides which characters are important enough for unique voices.
'The Voice' (Audio Synthesis): generates multi-voice audio output.

### 3.2.2 Key Innovations

INNOVATION 1 -- Switchboard Architecture:
All LLM providers (Gemini, Groq, Ollama) and TTS engines (Kokoro, Edge TTS) are accessed through abstract adapter interfaces. Switching engines requires only a single line change in config.yaml -- no code modification needed. This future-proofs the system against the rapidly evolving AI model landscape.

INNOVATION 2 -- Dual Extraction Pipeline:
Users select between two NER strategies:
(a) spaCy Fast Mode: Custom EntityRuler + statistical NER. Processes 5,000 words in under 500ms. Best for rapid batch processing. Achieves approximately 72% F1 on fantasy text.
(b) LLM Smart Mode: Gemini Flash with structured JSON prompting. Extracts full Dynamic Event Units with causal relationships. Achieves approximately 91% F1. Best for accuracy-critical chapters.

INNOVATION 3 -- Temporal PageRank with Bootstrapping Mitigation:
Standard PageRank on sparse early-chapter graphs assigns near-zero scores to protagonists who appear in only 1-2 chapters. Two mechanisms mitigate this:
(a) The first 5 introduced characters receive a guaranteed minimum importance score of 0.16 (above the 0.15 graduation threshold) until the graph matures.
(b) Temporal decay reduces scores for characters absent from recent chapters.

INNOVATION 4 -- Time-CoT RAG:
Instead of embedding-based retrieval, the Q&A engine traverses the knowledge graph and retrieves events sorted by chapter_id. This produces chronologically ordered context for the LLM, enabling accurate temporal reasoning.

INNOVATION 5 -- Voice Locking:
Once a character achieves Main Cast status (confidence_score >= 0.75), a specific voice_id is assigned and locked in runtime_db.json. This voice is used for all future audiobook generations involving that character, ensuring audio consistency across the entire series.

### 3.2.3 Advantages Over Existing Systems:
- Fully automated: no manual editing required after initial setup.
- Incremental: processes chapters as published with no complete manuscript requirement.
- Multi-voice: characters speak with consistent, differentiated voices.
- Zero-GPU: runs on standard laptops.
- Modular: any component can be upgraded independently.
- Multi-story: manages unlimited independent story projects simultaneously.

## 3.3 System Requirements
###

### 3.3.1 Functional Requirements

FR-01 Story Management: Users shall create, rename, duplicate, soft-delete, and switch between independent stories. Each story maintains completely isolated data directories.

FR-02 Text Ingestion: The system shall provide a Chapter Title text input field and Chapter Text text area. 'Process Chapter' shall execute the full ingestion pipeline.

FR-03 EPUB Ingestion: The system shall accept .epub file uploads, parse all chapters using EpubParser, display a chapter selector, and process selected chapters.

FR-04 Royal Road Ingestion: The system shall accept Royal Road fiction index URLs and individual chapter URLs. For index URLs it shall scrape the full chapter list, persist it as index_state.json, and support batch ingestion of N consecutive chapters with progress tracking.

FR-05 Extraction Method Selection: Users shall select between spaCy (fast) and LLM (smart) extraction modes before processing a chapter.

FR-06 Knowledge Graph Build: For each ingested chapter, the system shall add character nodes, DEU event nodes, and typed directed edges (participant, featured, causes) to the knowledge graph.

FR-07 Character Importance Scoring: After each chapter, the system shall recalculate PageRank-based importance scores for all characters with temporal decay applied.

FR-08 Character Graduation: The system shall classify characters as EXTRA (score &lt; 0.25), EVOLVING (0.25-0.75), or MAIN_CAST (&gt;=0.75). Characters reaching MAIN_CAST shall have a voice_id assigned and locked.

FR-09 Wiki Generation: The system shall create and update Markdown wiki entries per character using LLM. Wiki fields include role, status, age, species, appearance, affiliations, personality_traits, and notable_quirks.

FR-10 Audiobook Generation: The system shall generate complete multi-voice MP3 audiobooks with synchronized WebVTT subtitle files. Cancellation shall be supported via UI button.

FR-11 Story Q&A: Users shall enter natural language queries. The system shall retrieve events from the graph chronologically, construct a Time-CoT prompt, and return an LLM-generated narrative answer.

FR-12 Knowledge Graph Visualization: The system shall render an interactive PyVis HTML graph with color-coded nodes and physics simulation.

FR-13 Evaluation Harness: The system shall run automated benchmarks measuring Entity F1, Graph Latency at multiple scales, and TTS Real-Time Factor.

### 3.3.2 Non-Functional Requirements

NFR-P01: spaCy extraction shall complete within 5 seconds for chapters up to 10,000 words.
NFR-P02: LLM-based extraction shall complete within 15 seconds under normal network conditions.
NFR-P03: Knowledge graph PageRank shall complete within 500ms for graphs with up to 2,000 nodes.
NFR-P04: Kokoro TTS shall achieve Real-Time Factor below 1.0 on minimum hardware.
NFR-R01: The system shall implement 3-attempt retry with exponential backoff for all LLM calls.
NFR-R02: On primary LLM failure, the system shall automatically fall back to Groq.
NFR-R03: On Kokoro failure, the system shall automatically fall back to Edge TTS.
NFR-R04: All story data shall be persisted to disk after each chapter ingestion.
NFR-S01: The system shall support a minimum of 100 chapters per story.
NFR-S02: The system shall support a minimum of 500 unique characters per story.
NFR-SEC01: API keys shall be stored exclusively in .env files and never hardcoded.
NFR-M01: Adding a new LLM provider shall require only implementing the LiteLLM adapter convention plus a config.yaml entry with no other code changes required.
NFR-M02: Adding a new TTS engine shall require only implementing the TTSProvider abstract class plus a factory case plus a config.yaml entry.

## 3.4 FEASIBILITY STUDY

### 3.4.1 Technical Feasibility

All technologies selected for Webnovel Architect are production-grade, actively maintained, and well-documented:

Python 3.9+: The de-facto language for AI/ML development with an enormous ecosystem.
spaCy 3.x: Used in production by major enterprises; stable, fast, extensible.
NetworkX 3.x: Industry-standard graph library used in research and production worldwide.
Streamlit: Powers thousands of production data apps globally.
LiteLLM: Supports 100+ LLM providers through a single unified API.
Kokoro ONNX: Released 2024, CPU-compatible with no CUDA driver dependencies.
Edge TTS: Backed by Microsoft Azure infrastructure.

GPU REQUIREMENT ANALYSIS: The system is explicitly designed for Zero-GPU operation. Both TTS engines function without CUDA. LLM inference is API-based (cloud). spaCy's en_core_web_sm model runs efficiently on CPU. NetworkX graph operations are CPU-bound memory operations. This confirms technical feasibility for laptops without dedicated GPU hardware.

### 3.4.2 Economic Feasibility

DEVELOPMENT COSTS:
All libraries used are free and open-source. LLM API costs: Gemini Flash free tier supports 15 requests/minute. Groq free tier supports 14,400 requests/day. Development costs are effectively zero. Kokoro ONNX model files are freely downloadable from HuggingFace.

OPERATIONAL COSTS:
Local deployment: \$0/month. For heavy commercial usage: Gemini Flash costs approximately \$0.075 per 1 million input tokens -- a 5,000-word chapter costs approximately \$0.002 per ingestion. The cost to process an entire 500-chapter web novel would be approximately \$1.00 in API fees.

### 3.4.3 Operational Feasibility

The system's Streamlit UI is designed for non-technical end users:
- Navigation uses clear labeled pages accessible via sidebar radio buttons.
- All forms provide placeholder text and descriptive labels.
- Progress bars and spinner animations provide visual feedback.
- Error messages include specific reason and suggested remediation.

Deployment process for technical administrators:
Step 1: Install Python 3.9+ and run 'pip install -r requirements.txt'.
Step 2: Download spaCy model: 'python -m spacy download en_core_web_sm'.
Step 3: Create .env file with API keys (GEMINI_API_KEY, GROQ_API_KEY).
Step 4: Download Kokoro model files to models/ directory (optional).
Step 5: Run 'streamlit run app_ui.py'.

Total setup time for a technical user: approximately 15-30 minutes.
CONCLUSION: The system is fully operationally feasible for both technical and non-technical users.

**Technical Feasibility**: Assess availability of technology and tools

**Economic Feasibility**: Evaluate cost-effectiveness

**Operational Feasibility**: Determine ease of use and implementation

# CHAPTER - 4

# SOFTWARE REQUIREMENTS SPECIFICATION

## 4.1 Introduction
This Software Requirements Specification (SRS) formally specifies the functional and non-functional requirements of Webnovel Architect version 1.0. It serves as a binding agreement between the development team and stakeholders, defining precisely what the system must accomplish, the constraints under which it operates, and the performance criteria it must meet.

INTENDED AUDIENCE: Development team, academic evaluators, and potential future contributors. It documents both visible behaviors accessible through the Streamlit UI and internal service-layer behaviors that drive those UI interactions.

DOCUMENT SCOPE: This SRS covers the complete Webnovel Architect system including the Streamlit UI (app_ui.py), ingestion pipeline (app/services/ingest.py), entity extraction (app/services/extraction.py), knowledge graph management (adapters/graph_adapter.py), TTS synthesis (adapters/tts_adapter.py), LLM integration (adapters/llm_adapter.py), RAG Q&A (app/services/rag.py), wiki generation (app/services/wiki.py), audiobook generation (app/services/audiobook_generator.py), story management (app/core/story_manager.py), and the evaluation harness.

ASSUMPTIONS AND DEPENDENCIES:
- A valid GEMINI_API_KEY or GROQ_API_KEY must be present in .env for LLM-based extraction.
- Internet connectivity is required for LLM API calls and Edge TTS synthesis.
- spaCy's en_core_web_sm model must be downloaded before first use.
- For Kokoro TTS: kokoro-v0_19.onnx and voices-v1.0.bin must be in the models/ directory.

**4.2 FUNCTIONAL REQUIREMENTS**

FR-01: Story Creation and Multi-Story Management
The system shall support creation of multiple independent stories, each identified by a UUID. For each story, the system shall maintain completely isolated data directories under data/&lt;story_uuid&gt;/. Operations supported: create, rename, duplicate (deep copy), soft-delete (move to \_trash directory), and restore. The sidebar shall display a dropdown of all available stories.

FR-02: Chapter Ingestion via Text Input
The Ingestion Engine page shall provide Chapter Title text input and Chapter Text text area. Upon clicking 'Process Chapter', the system shall call ingest_chapter(story_uuid, title, text, extractor, decay_rate) and display success/failure feedback with extracted data preview.

FR-03: Chapter Ingestion via EPUB Upload
The system shall provide a file uploader restricted to .epub files. Upon upload and clicking 'Parse EPUB Chapters', the system shall use EpubParser to extract all chapters. A dropdown shall allow the user to select which chapter to load for processing.

FR-04: Chapter Ingestion via Royal Road URL Scraping
The system shall accept Royal Road fiction index URLs and individual chapter URLs. For index URLs, RoyalRoadScraper shall retrieve the complete chapter list. The scraped index shall be persisted to index_state.json. The UI shall display chapter count, last ingested index, and batch ingestion controls.

FR-05: Batch Chapter Ingestion
For scraped indexes, the system shall support batch ingestion of N consecutive chapters. A progress bar shall update after each chapter. The last_ingested_index shall be saved incrementally after each chapter so partial batch progress is not lost on failure.

FR-06: Knowledge Graph Management
For each ingested chapter: (a) Character nodes shall be added or updated with display_name and last_seen_chapter attributes. (b) DEU event nodes shall be added with description, chapter_id, pre_conditions, post_conditions, and location. (c) Participation and featured edges shall be added with chapter_id. (d) Causal edges shall be added based on causes_event_indexes from the LLM extraction.

FR-07: Character Importance Calculation
After each chapter, the system shall compute PageRank (alpha=0.85) over the full graph. For each character, a temporal multiplier is applied: multiplier = (1 - decay_rate)^age. Characters introduced in positions 1-5 (by introduction_order) receive a guaranteed minimum score of 0.16.

FR-08: Character Graduation and Voice Assignment
The system shall evaluate each character's confidence_score: below 0.25 = EXTRA, 0.25 to 0.75 = EVOLVING, 0.75 or above = MAIN_CAST. Characters transitioning to MAIN_CAST for the first time shall have a voice_id assigned and persisted in runtime_db.json permanently.

FR-09: Character Wiki Generation and Updates
On first appearance, a Markdown wiki file shall be created in wiki/&lt;char_id&gt;.md. On subsequent appearances with events, the LLM shall update the wiki with new story information. Wiki fields: synopsis, status, age, species, role, appearance, affiliations, personality traits, and notable quirks.

FR-10: Multi-Voice Audiobook Generation
The Audio Hub page shall trigger full-chapter audiobook generation. The system shall: (a) Extract dialogue attribution per character using LLM. (b) Synthesize each dialogue segment with the speaker's locked voice. (c) Synthesize narration with narrator voice. (d) Concatenate audio segments into a complete chapter MP3. (e) Generate synchronized WebVTT subtitle file. (f) Display an embedded audio player with subtitle track.

FR-11: Story Q&A via Time-CoT RAG
The system shall: (a) Extract entity names from query using spaCy NER. (b) Look up entities in the knowledge graph. (c) Retrieve all linked events. (d) Sort events by chapter_id. (e) Construct timeline prompt. (f) Submit to LLM. (g) Display the answer in the UI.

FR-12: Knowledge Graph Visualization
The Knowledge Graph page shall render an interactive PyVis visualization: red nodes for characters (size 25), blue nodes for events (size 15), grey edges for participation, orange dashed edges for causal links. Shows node counts below the graph.

FR-13: Evaluation Harness
The Evaluation page shall run benchmarks against dataset/gold_standard.json: Entity Precision/Recall/F1 for characters and world terms; Graph traversal latency at 10, 50, 100, 500, 1000 node scales; TTS Real-Time Factor for available engines.

**4.3 NON-FUNCTIONAL REQUIREMENTS
**
**PERFORMANCE REQUIREMENTS:**
NFR-P01: spaCy entity extraction must complete within 5 seconds for chapters up to 10,000 words on hardware meeting minimum specifications (Intel Core i5, 8GB RAM).
NFR-P02: LLM-based extraction (including API call) must complete within 15 seconds under normal network conditions.
NFR-P03: Knowledge graph PageRank computation must complete within 500ms for graphs with up to 2,000 nodes.
NFR-P04: Kokoro TTS must achieve a Real-Time Factor below 1.0 on minimum hardware.
NFR-P05: UI page transitions must complete within 1 second for normal page loads.

**RELIABILITY REQUIREMENTS:**
NFR-R01: The system must implement 3-attempt retry with exponential backoff (2^n seconds) for all LLM API calls.
NFR-R02: On primary LLM failure after 3 attempts, the system must automatically fall back to the Groq Llama-3.1-8B model without user intervention.
NFR-R03: On Kokoro TTS failure or model file absence, the system must automatically fall back to Edge TTS.
NFR-R04: All story data must be persisted to disk after each chapter ingestion. An application crash mid-processing must not corrupt previously saved data.
NFR-R05: The system must handle malformed chapter text gracefully with user-facing error messages rather than unhandled exceptions.

**SCALABILITY REQUIREMENTS:**
NFR-S01: The system must support a minimum of 100 chapters per story.
NFR-S02: The system must support a minimum of 500 unique characters per story.
NFR-S03: Multiple stories must be manageable simultaneously without data leakage.

**SECURITY REQUIREMENTS:**
NFR-SEC01: API keys must be read exclusively from .env files using os.environ.setdefault().
NFR-SEC02: The .gitignore file must explicitly list .env to prevent credential exposure.
NFR-SEC03: Uploaded EPUB files must be processed in-memory without permanent server storage.

**MAINTAINABILITY REQUIREMENTS:**
NFR-M01: Adding a new LLM provider must require only: implementing the LiteLLM calling convention, adding a config.yaml entry, and no changes to any service or UI code.
NFR-M02: Adding a new TTS engine must require only: implementing the TTSProvider abstract class, adding a factory case, and a config.yaml entry.
NFR-M03: All services must expose clear Python function interfaces callable without UI.

**USABILITY REQUIREMENTS:
**NFR-U01: Primary workflows must be completable without referring to documentation.
NFR-U02: Error messages must include the specific failure reason and a suggested fix.
NFR-U03: Long-running operations (>2 seconds) must display a spinner or progress indicator.

**4.4 HARDWARE REQUIREMENTS**

MINIMUM CONFIGURATION (Edge TTS Cloud Mode):
Processor: Intel Core i5 6th Generation or equivalent (2.4 GHz, 4 cores)
RAM: 4 GB DDR4
Storage: 500 MB free disk space (excluding audio output)
Network: Broadband internet connection (minimum 5 Mbps) for LLM API calls and Edge TTS
Display: 1366x768 resolution (for Streamlit UI)
GPU: Not required

RECOMMENDED CONFIGURATION (Kokoro Local TTS Mode):
Processor: Intel Core i7 8th Generation or equivalent (3.0 GHz, 8 cores)
RAM: 16 GB DDR4
Storage: 5 GB free disk space (2 GB for Kokoro model files plus audio output)
Network: Broadband internet connection (10 Mbps or higher) for LLM API calls
Display: 1920x1080 resolution
GPU: Not required (Kokoro runs on CPU via ONNX Runtime)

STORAGE BREAKDOWN:
Kokoro model files: kokoro-v0_19.onnx (290 MB) + voices-v1.0.bin (48 MB) = approximately 338 MB total
spaCy en_core_web_sm model: approximately 12 MB
Per-story data (100 chapters, 200 characters): approximately 50-100 MB
Generated audio per full chapter MP3: approximately 15-40 MB
Python environment and all dependencies: approximately 1.5 GB

TEST ENVIRONMENT USED DURING DEVELOPMENT:
System: Windows 11 Home
Processor: Intel Core i7-12th Gen (2.5 GHz)
RAM: 16 GB
Storage: 512 GB NVMe SSD
Network: 100 Mbps broadband

**4.5 SOFTWARE REQUIREMENTS**

OPERATING SYSTEM:
Windows 10 (Build 19041+) or Windows 11
Ubuntu 20.04 LTS or later
macOS 12 (Monterey) or later

RUNTIME ENVIRONMENT:
Python 3.9, 3.10, 3.11, 3.12, or 3.14 (all tested and compatible)
pip package manager

PYTHON DEPENDENCIES (from requirements.txt):
litellm: Unified LLM provider interface supporting 100+ providers
google-generativeai: Google Gemini API client library
kokoro-onnx: Local TTS engine with ONNX runtime for CPU inference
soundfile: Audio file writing and reading
edge-tts: Microsoft Edge TTS cloud client (free)
networkx: Graph data structures and algorithms including PageRank
pydantic: Data validation via Python type annotations (version 2.x)
pyyaml: YAML configuration file parsing
streamlit: Web UI framework for interactive data applications
pyvis: Interactive graph visualization in HTML format
beautifulsoup4: HTML parsing for Royal Road web scraping
requests: HTTP client for Royal Road scraping and API calls
spacy: NLP pipeline with Named Entity Recognition
fastapi: REST API framework for programmatic access (optional)
uvicorn: ASGI server for FastAPI

AI MODELS:
Google Gemini 2.5 Flash (gemini/gemini-2.5-flash): Primary LLM for entity extraction, wiki updates, and audiobook scripting
Groq Llama-3.1-8B-Instant (groq/llama-3.1-8b-instant): Fallback LLM, faster and free tier
spaCy en_core_web_sm: Statistical NER model for English text (12MB)
Kokoro v0.19 ONNX: Local TTS model (kokoro-v0_19.onnx plus voices-v1.0.bin)
Microsoft Edge Neural TTS: Cloud TTS via edge-tts Python library

DEVELOPMENT TOOLS:
Git: Version control for source code management
Python venv: Virtual environment isolation
pytest: Unit testing framework with fixtures in conftest.py
Visual Studio Code or PyCharm: Recommended IDE

CONFIGURATION FILES:
config.yaml: Engine selection (llm_model, tts_engine, fallback_tts)
.env: API key storage (GEMINI_API_KEY, GROQ_API_KEY) -- never committed to git

# CHAPTER - 5

# DESIGN AND METHODOLOGY OF PROPOSED SYSTEM

## 5.1 System Architecture
**5.1.1 Architectural Overview
**
Webnovel Architect is designed as a four-layer modular architecture:

LAYER 1 -- PRESENTATION LAYER:
The Streamlit application (app_ui.py) serves as the sole user interface with 7 pages:
1\. Dashboard: Story-level metrics and configuration display.
2\. Ingestion Engine: Chapter input and processing controls.
3\. Wiki Memory: Character wiki browser with export functionality.
4\. Knowledge Graph: Interactive PyVis graph visualization.
5\. Story Q&A: Natural language query interface.
6\. Audio Hub: Audiobook generation and playback; character voice testing.
7\. Evaluation: Automated benchmark execution.
The Streamlit session_state mechanism maintains UI state across page interactions. The active_story_uuid is stored in session_state and used to scope all data operations.

LAYER 2 -- SERVICE LAYER:
Services implement business logic called by the UI layer:
ingest.py: Orchestrates the complete chapter processing pipeline.
extraction.py: Dual-mode NER (spaCy + LLM).
wiki.py: Character wiki creation, parsing, and LLM-based updating.
rag.py: Time-CoT graph retrieval and LLM Q&A generation.
audiobook_generator.py: Multi-voice MP3 generation with VTT subtitles.
scrapers/royalroad_scraper.py: Royal Road chapter and index scraping.
scrapers/epub_parser.py: EPUB file chapter extraction.
alias_resolver.py: Canonical name resolution to prevent duplicate character nodes.

LAYER 3 -- ADAPTER LAYER (The Switchboard):
Adapters provide abstract interfaces to external AI providers:
llm_adapter.py: Wraps LiteLLM for all LLM API calls. Exposes analyze_text() and analyze_text_json() with retry logic and automatic Groq fallback.
graph_adapter.py: Wraps NetworkX DiGraph. Provides domain-specific story graph methods with persistence. Includes in-memory story-to-instance caching.
tts_adapter.py: Abstract TTSProvider base class with KokoroAdapter and EdgeAdapter implementations. Factory function selects engine from config.

LAYER 4 -- DATA PERSISTENCE LAYER:
All story data is stored in flat files under data/&lt;story_uuid&gt;/:
story_graph.json: NetworkX DiGraph in node-link JSON format.
runtime_db.json: Character runtime state (scores, voice IDs, mention counts).
index_state.json: Scraped Royal Road chapter list and ingestion progress.
chapters/&lt;id&gt;/text.txt + metadata.json: Raw chapter text and metadata.
wiki/&lt;char_id&gt;.md: Character wiki Markdown files.
generated_audio/chapter_N_full.mp3 + .vtt: Audiobook output files.
story_meta.json: Story name, UUID, creation and update timestamps.

**5.1.2 Data Flow Diagram**

TEXT INPUT -> Ingestion Service (ingest.py)
-> Extract Intelligence (extraction.py) \[spaCy NER or LLM JSON\]
-> Alias Resolution (alias_resolver.py)
-> Graph Update (graph_adapter.py) \[add characters, events, causal links\]
-> PageRank + Temporal Decay \[importance scoring for all characters\]
-> Graduation Check (graduation.py) \[EXTRA / EVOLVING / MAIN_CAST\]
-> Wiki Update (wiki.py) \[LLM-based profile refresh\]
-> Persist All State to Disk \[runtime_db.json, story_graph.json, wiki/*.md\]
-> UI: Success Message + Extracted Data Preview

## 5.2 UML Diagrams
The following subsections describe the key UML diagrams for Webnovel Architect. These diagrams should be inserted as high-resolution images exported from a UML tool such as draw.io, Lucidchart, or PlantUML.

## 5.3 Database Design
**5.3.1 Story Graph Schema (story_graph.json)
**
The knowledge graph is persisted using NetworkX's node-link JSON format:
{"directed": true, "multigraph": false, "nodes": \[...\], "edges": \[...\]}

CHARACTER NODE SCHEMA:
{"id": "character_id", "type": "character", "display_name": "Original Name",
"last_seen_chapter": 5, "introduction_order": 1}

EVENT NODE (DEU) SCHEMA:
{"id": "chapter_3_event_0", "type": "event", "description": "Action summary",
"chapter_id": 3, "pre_conditions": "Before state", "post_conditions": "After state",
"location": "Location name or Unknown"}

EDGE SCHEMA:
{"source": "character_id", "target": "chapter_3_event_0",
"relation": "participant", "chapter_id": 3}
Relation types: participant (char to event), featured (event to char), causes (event to event)

**5.3.2 Runtime Database Schema (runtime_db.json)**

{"chapter_counter": 12, "characters": {
"aria_stormveil": {
"character_id": "aria_stormveil",
"first_seen_chapter": 1, "last_seen_chapter": 12,
"confidence_score": 0.8432, "mention_count": 34,
"voice_id": "af_heart",
"vocal_traits": {"gender": "female", "age_category": "young_adult"}
}
}}

**5.3.3 Character Wiki Schema (wiki/&lt;char_id&gt;.md)**

Each wiki is a structured Markdown file:
# CharacterName
**Role:** \[role\] | **Status:** \[status\] | **Age:** \[age\] | **Voice:** \[voice_id\]
**First Appearance:** Chapter N | **Last Updated:** Chapter M
## Short Description
\[One-line summary\]
## Synopsis
\[Multi-paragraph story overview\]
## Appearance
\[Physical description\]
## Affiliations
- \[Faction 1\]
## Personality Traits
- \[Trait 1\]
## Notable Quirks
- \[Quirk 1\]

**5.3.4 Story Metadata Schema (story_meta.json)
**
{"uuid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
"name": "The Dragon's Covenant",
"created_at": "2026-04-01T10:00:00Z",
"updated_at": "2026-04-19T09:00:00Z"}

**5.3.5 Index State Schema (index_state.json)
**
{"source_url": "<https://www.royalroad.com/fiction/XXXXX/story-name>",
"chapters": \[
{"title": "Chapter 1: The Beginning",
"url": "<https://www.royalroad.com/fiction/XXXXX/chapter/1"}>
\],
"last_ingested_index": 4}

## 5.4 Flowcharts
### 5.4.1 Chapter Ingestion Flowchart (Main Pipeline)

START
-> User provides chapter input (text / EPUB selection / Royal Road URL)
-> \[Decision\] Input type?
TEXT: Use directly
EPUB: EpubParser.parse_epub() -> select chapter
URL: RoyalRoadScraper.scrape_chapter()
-> Load runtime state: load_runtime(story_uuid) -> (chapter_counter, runtime_db)
-> Increment chapter_counter
-> Create Chapter object (id, title, raw_text, created_at)
-> Save chapter text to disk
-> \[Decision\] Extractor mode?
spaCy: extract_chapter_intelligence(text)
LLM: extract_chapter_intelligence_llm(text) -> Gemini API call
-> Resolve aliases: resolve_aliases(active_names)
-> \[Loop\] For each character:
normalize_id(name) -> char_id
graph.add_character(char_id, {display_name, last_seen_chapter})
-> \[Decision\] Events extracted?
YES: For each event -> Create DEU node, add edges, add causal links
NO: Create generic chapter event node
-> \[Loop\] For each character:
score = graph.get_character_importance(char_id, chapter_counter, decay_rate)
\[Decision\] Is this a new character?
YES: Create CharacterRuntime entry, create initial wiki, save wiki
NO: Update last_seen_chapter, mention_count, and confidence_score
check_graduation_status(char)
\[Decision\] Graduated to MAIN_CAST?
YES: assign_voice(vocal_traits) -> lock voice_id
\[Decision\] Has events this chapter?
YES: update_character_profile(wiki, events, name) via LLM
NO: parse_character_wiki(wiki) only
save_character_wiki()
-> save_runtime(story_uuid, chapter_counter, runtime_db)
-> Return Chapter object to UI
-> Display success message and extracted data preview
END

**5.4.2 Character Graduation Decision Flowchart
**
RECEIVE character.confidence_score
-> \[Decision\] score >= 0.75?
YES: evaluate_graduation() returns MAIN_CAST
\[Decision\] voice_id is None?
YES: assign_voice(vocal_traits) -> lock voice_id -> return True
NO: already graduated, return False (no change)
NO: \[Decision\] score >= 0.25?
YES: EVOLVING (tracked in wiki, no voice yet)
NO: EXTRA (background character, no persistent tracking)

**5.4.3 Time-CoT RAG Query Flowchart
**
RECEIVE user query string
-> spaCy NER: extract named entities from query
-> \[Decision\] Entities found?
NO: tokenize query, extract capitalized words
-> \[Decision\] Still no entities?
YES: fallback to top 5 characters by graph degree
NO: continue
-> \[Loop\] For each entity_id:
\[Decision\] graph.has_node(entity_id)?
YES: get all out_edges with relation=participant
for each event_id: collect DEU data
-> \[Decision\] retrieved_events is empty?
YES: return 'No events found' message
-> Sort retrieved_events by chapter_id (chronological)
-> Build structured timeline string with chapter markers
-> Construct LLM prompt: \[loremaster system\] + \[Timeline\] + \[User Question\]
-> Call analyze_text(prompt, model='gemini/gemini-2.5-flash')
-> \[Decision\] Response failed or is API fallback?
YES: retry with Groq fallback model
-> Return LLM-generated narrative answer to UI
END

# CHAPTER - 6

# IMPLEMENTATION

## 6.1 Technologies Used
PROGRAMMING LANGUAGE:
Python 3.9+ was selected as the sole programming language. Python's dominance in the AI/ML ecosystem ensures seamless integration with the latest models and libraries. Type hints used throughout the codebase combined with Pydantic v2 validation provide production-grade data integrity without verbose boilerplate.

WEB UI FRAMEWORK -- Streamlit:
Streamlit transforms Python scripts into interactive web applications without requiring frontend development expertise. Key features used: st.session_state for cross-page state management, st.file_uploader for EPUB uploads, st.progress for batch tracking, st.components.v1.html for PyVis graph embedding, st.audio for TTS preview playback.

NLP -- spaCy 3.x with Custom EntityRuler:
spaCy's processing pipeline with disabled unused components (parser, tagger, lemmatizer) provides a 60% speed improvement. The custom EntityRuler adds domain patterns: PERSON with title+name, apostrophe names, and two-capitalized-word patterns; RANK for Tier-X and Level N systems; MAGIC_SYSTEM for Mana Core and Spirit Root; LOC for realm names; FACTION for sects and clans. Post-processing normalizes possessives and strips generic titles.

GRAPH ENGINE -- NetworkX:
NetworkX.DiGraph stores characters and events. Core operations: nx.pagerank(graph, alpha=0.85) computes normalized PageRank; add_node/add_edge with attribute dictionaries; nx.node_link_data and node_link_graph for JSON serialization; out_edges traversal for character event history; degree as performance fallback metric.

LLM INTEGRATION -- LiteLLM:
Single unified API for 100+ LLM providers. Two exposed functions: analyze_text() returning string response for wiki updates and Q&A; analyze_text_json() returning parsed dict for entity extraction enforcing json_object response format. Both implement 3-attempt retry loop, exponential backoff, and automatic Groq fallback.

TTS ENGINES:
Kokoro ONNX: kokoro_onnx.Kokoro.create(text, voice, speed, lang) generates (audio_array, sample_rate). soundfile.write() saves to WAV/MP3. 54 available voice IDs.
Edge TTS: edge_tts.Communicate(text, voice_id).save(path) async function. 300+ voices. Used as automatic fallback when Kokoro model files are absent.

GRAPH VISUALIZATION -- PyVis:
Network(height, width, bgcolor, font_color, directed=True) creates interactive HTML. toggle_physics(True) enables force-directed layout. Red nodes for characters, blue for events, grey edges for participation, orange dashed edges for causal links.

ADDITIONAL LIBRARIES:
FastAPI + Uvicorn: REST API for programmatic chapter ingestion via app/api/ endpoints.
Pydantic v2: Data models for Chapter, CharacterRuntime, CharacterWiki.
BeautifulSoup4 + Requests: HTML parsing for Royal Road scraping.
EbookLib: EPUB file reading and chapter extraction.
PyYAML: config.yaml parsing for engine configuration.
Pytest: Unit testing with fixtures defined in conftest.py.

AI MODELS USED:
Google Gemini 2.5 Flash: Primary LLM for entity extraction, wiki updates, audiobook scripting
Groq Llama-3.1-8B-Instant: Fallback LLM
spaCy en_core_web_sm: Statistical NER model for English text
Kokoro v0.19 ONNX: Local TTS synthesis model
Microsoft Edge Neural TTS: Cloud TTS fallback

## 6.2 Module Description
MODULE 1 -- app_ui.py (Streamlit UI Application, 861 lines)
The main entry point for user interaction. Implements all 7 UI pages as conditional branches in a single file routed by st.radio sidebar selection. Loads .env file manually at startup to ensure API keys are available before any service module imports.

MODULE 2 -- app/services/ingest.py (Ingestion Orchestrator, 360 lines)
The central orchestration service for chapter processing. Contains: load_runtime() and save_runtime() for JSON-based character state persistence; save_chapter(), load_index_state(), and save_index_state() for chapter and index persistence; ingest_chapter() as the main 5-step pipeline (extraction, graph update, importance scoring, graduation, wiki update); ingest_multiple_chapters() for batch processing with progress callback; normalize_id() for display-name-to-file-ID conversion.

MODULE 3 -- app/services/extraction.py (NER Engine, 208 lines)
Implements the dual extraction pipeline. extract_chapter_intelligence() uses spaCy with EntityRuler, processes the entire chapter as one document (max_length=2,000,000), returns character names, world terms, and dialogue count. extract_chapter_intelligence_llm() uses LLM structured JSON prompting returning full DEU events with pre/post conditions and causal indexes. STOP_ENTITIES set filters known temporal false positives.

MODULE 4 -- adapters/graph_adapter.py (Knowledge Graph Manager, 200 lines)
Wraps NetworkX DiGraph with domain-specific methods. add_character() assigns introduction_order to new nodes for bootstrapping paradox mitigation. get_character_importance() implements full PageRank plus temporal decay plus bootstrapping guarantee. merge_characters() transfers all edges from alias to canonical node. save_graph/load_graph() use nx.node_link_data format. \_graph_instances dict caches story-to-GraphProvider mappings in memory.

MODULE 5 -- adapters/llm_adapter.py (LLM Switchboard, 111 lines)
Implements \_run_with_model() with exponential backoff retry. analyze_text() targets string responses. analyze_text_json() enforces json_object response format and strips markdown fences before JSON parsing. get_model_info() provides model capability lookup via LiteLLM.

MODULE 6 -- adapters/tts_adapter.py (TTS Switchboard, 121 lines)
Implements the Strategy design pattern for TTS. TTSProvider (ABC) defines generate_audio() as abstract method. KokoroAdapter loads Kokoro ONNX model at initialization and generates audio via engine.create(). EdgeAdapter wraps edge_tts async Communicate.save() in asyncio.run() for synchronous calling. get_tts_engine() factory falls back to Edge on Kokoro initialization failure.

MODULE 7 -- app/services/rag.py (RAG Engine, 134 lines)
Implements Time-CoT RAG: entity extraction from query via spaCy NER, graph traversal, chronological event ordering, and LLM prompting. The timeline prompt provides chapter-by-chapter context with Location, Involved characters, Before/After state, and Action summary for each event. Includes top-5-by-degree fallback for queries with no entity matches.

MODULE 8 -- app/services/wiki.py (Wiki Service, 7579 bytes)
Manages character wiki operations: save_character_wiki() generates standardized Markdown from CharacterWiki model; get_wiki_dir() returns story-specific wiki directory; get_character_wiki_content() reads existing wiki; update_character_profile() calls LLM to update wiki with chapter events; parse_character_wiki() parses Markdown without LLM for unchanged characters.

MODULE 9 -- app/services/audiobook_generator.py (Audio Production, 16141 bytes)
The most complex service. LLM extracts dialogue attribution from chapter text as structured JSON. Each segment (narration or dialogue) synthesized with appropriate voice. Segments concatenated into single MP3. WebVTT subtitle file generated with millisecond timestamps. Supports cancellation via cancel_audio.flag sentinel file checked between segments.

MODULE 10 -- app/core/story_manager.py (Story Lifecycle, 5225 bytes)
Manages multi-story operations: create_story() generates UUID4 and creates directory structure; list_stories() reads all story_meta.json files; duplicate_story() deep copies entire story directory with new UUID; soft_delete_story() moves directory to \_trash/; \_touch_updated_at() updates timestamp on every save.

MODULE 11 -- app/core/graduation.py (Graduation Engine, 38 lines)
Implements 3-tier classification (GraduationLevel enum: EXTRA, EVOLVING, MAIN_CAST). evaluate_graduation() maps confidence_score to tier. check_graduation_status() triggers voice assignment on first transition to MAIN_CAST -- the graduation event.

MODULE 12 -- app/services/alias_resolver.py (Name Canonicalization, 2893 bytes)
Prevents duplicate character nodes from name variants. Uses string similarity and prefix matching to detect aliases. Critical for stories where the narrator uses different name forms for the same character (Aria, Lady Aria, Aria Stormveil).

## 6.3 Code Snippets (Optional)
SNIPPET 1 -- PageRank with Temporal Decay and Bootstrapping (graph_adapter.py):

def get_character_importance(self, name, current_chapter=0, decay_rate=0.05):
if not self.graph.has_node(name):
return 0.0
try:
pagerank_scores = nx.pagerank(self.graph, alpha=0.85)
base_score = float(pagerank_scores.get(name, 0.0))
max_chapter = max(
(data.get('chapter_id', 0)
for \_, \_, data in self.graph.out_edges(name, data=True)),
default=0
)
if current_chapter > 0 and max_chapter > 0:
age = max(0, current_chapter - max_chapter)
temporal_multiplier = (1.0 - decay_rate) ** age
score = base_score * temporal_multiplier
else:
score = base_score
intro_order = self.graph.nodes\[name\].get('introduction_order', 999)
if intro_order <= 5:
return max(score, 0.16)
return score
except Exception as e:
return float(self.graph.degree(name))

**EXPLANATION**: The algorithm first computes standard PageRank (characters connected to many important events receive higher scores). It applies exponential temporal decay -- a character absent for 10 chapters at 5% decay rate has their score multiplied by (0.95)^10 = 0.60. The bootstrapping guarantee prevents the Silent Protagonist Problem where main characters introduced before the graph is dense enough receive near-zero scores.

SNIPPET 2 -- LLM Adapter with Retry and Fallback (llm_adapter.py):

def analyze_text_json(text, model='groq/llama-3.1-8b-instant'):
messages = \[
{'role': 'system', 'content': 'Respond ONLY with valid JSON. No markdown.'},
{'role': 'user', 'content': text}
\]
def \_run_with_model(target_model, max_attempts=3):
for attempt in range(1, max_attempts + 1):
try:
response = litellm.completion(
model=target_model, messages=messages,
response_format={'type': 'json_object'})
content = response.choices\[0\].message.content
return True, json.loads(content.strip())
except Exception as e:
if attempt < max_attempts:
time.sleep(2 ** attempt) # 2s, 4s, 8s
return False, None
success, result = \_run_with_model(model)
if success:
return result
if not model.startswith('groq'):
\_, result = \_run_with_model('groq/llama-3.1-8b-instant', max_attempts=2)
if result:
return result
return {}

EXPLANATION: Exponential backoff (2s, 4s, 8s) prevents thundering herd problems during API instability. The Groq fallback ensures temporary Gemini outages do not block ingestion.

SNIPPET 3 -- spaCy EntityRuler Pattern (extraction.py):

ruler = nlp.add_pipe('entity_ruler', before='ner', config={'overwrite_ents': True})
patterns = \[
{'label': 'PERSON', 'pattern': \[{'IS_TITLE': True}, {'IS_TITLE': True}\]},
{'label': 'PERSON', 'pattern': \[
{'LOWER': {'IN': \['lord','lady','sir','king','queen','prince','elder'\]}},
{'IS_TITLE': True}
\]},
{'label': 'PERSON', 'pattern': \[{'TEXT': {'REGEX': r'^\[A-Z\]\[a-z\]+\[-\]\[A-Z\]?\[a-z\]+\$'}}\]},
{'label': 'RANK', 'pattern': \[{'LOWER': 'inner'}, {'LOWER': 'disciple'}\]},
{'label': 'MAGIC_SYSTEM', 'pattern': \[{'LOWER': 'mana'}, {'LOWER': 'core'}\]},
{'label': 'LOC', 'pattern': \[{'IS_TITLE': True}, {'LOWER': 'realm'}\]},
{'label': 'FACTION', 'pattern': \[{'IS_TITLE': True}, {'LOWER': 'sect'}\]},
\]
ruler.add_patterns(patterns)

EXPLANATION: These patterns supplement the statistical NER model with domain-specific knowledge about fantasy fiction structure, covering titles, ranks, magic systems, and fictional locations that the general-purpose model fails to recognize.

# CHAPTER-7

# TESTING

## 7.1 Introduction
Testing is a critical quality assurance phase that validates Webnovel Architect against both functional requirements and quantitative performance benchmarks. Given the hybrid nature of the system -- combining deterministic graph algorithms, probabilistic NLP models, and non-deterministic LLM API calls -- a multi-tier testing strategy is essential.

TESTING OBJECTIVES:
1\. Verify that each module correctly implements its specified interface.
2\. Validate that the integrated pipeline produces correct end-to-end results.
3\. Benchmark entity extraction accuracy, graph latency, and TTS RTF against targets.
4\. Confirm UI functionality across all 7 pages.
5\. Validate error handling and fallback mechanisms.

TESTING CHALLENGES:
LLM non-determinism: LLM outputs vary across runs. Tests must check structural correctness (valid JSON, required fields present) rather than exact content matches.
API dependency: Full integration tests require live API keys. Unit tests mock LLM calls.
TTS file output: Audio correctness requires subjective human evaluation. RTF is measured as an objective proxy metric.
Graph state isolation: Tests must use temporary directories to prevent cross-test contamination of graph state.

TESTING TOOLS:
pytest 7.x: Test discovery, execution, and reporting framework.
conftest.py: Shared fixtures including temporary story dirs, mock runtime databases, and sample chapter text.
Python mock / unittest.mock: Mocking LLM API responses for deterministic unit tests.
time.perf_counter: High-precision latency measurement for performance benchmarks.

## 7.2 Testing Methodology
**7.2.1 Unit Testing Strategy**

Individual service functions are tested in isolation using pytest:
test_extraction.py: Tests spaCy NER pipeline with fantasy text samples. Verifies character name normalization, title stripping, stop entity filtering.
test_graduation.py: Tests evaluate_graduation() threshold logic. Verifies GraduationLevel classification. Tests check_graduation_status() voice assignment trigger.
test_graph.py: Tests GraphProvider methods with synthetic graph data. Verifies node/edge addition, PageRank calculation, temporal decay calculation, merge_characters() edge transfer.
test_ingest.py: Tests normalize_id() conversion. Tests load_runtime/save_runtime round-trip persistence.

**7.2.2 Integration Testing Strategy
**
The verify_modular.py script tests the complete pipeline end-to-end:
Step 1: Creates a temporary story with a known UUID.
Step 2: Ingests a pre-written sample chapter using both extractor modes.
Step 3: Verifies the knowledge graph contains expected character and event nodes.
Step 4: Verifies character importance scores are non-zero.
Step 5: Verifies graduated characters have voice_id assigned.
Step 6: Triggers TTS synthesis for a test dialogue segment.
Step 7: Verifies the output audio file exists and has non-zero size.
Step 8: Cleans up temporary story data.

**7.2.3 Performance Benchmarking (Evaluation Harness)
**
The built-in Evaluation tab runs automated benchmarks:

METRIC 1 -- ENTITY PRECISION/RECALL/F1:
The gold_standard.json file contains a manually annotated sample chapter with known character names and world terms. The system runs both extraction modes and computes:
P = |predicted AND gold| / |predicted|
R = |predicted AND gold| / |gold|
F1 = 2PR / (P+R)
Results displayed as Streamlit data tables comparing spaCy and LLM performance.

METRIC 2 -- GRAPH TRAVERSAL LATENCY:
A synthetic benchmark creates graphs of increasing size (10, 50, 100, 500, 1000 characters times 2 = 20 to 2000 nodes), performs get_character_importance() for the first node, and measures wall-clock time using time.perf_counter(). Target: all sizes under 500ms.

METRIC 3 -- TTS REAL-TIME FACTOR:
A benchmark sentence of known word count is synthesized by each available TTS engine. RTF = synthesis_time / expected_audio_duration. Expected duration = word_count / 150 (average speaking rate in WPM). Target: RTF below 1.0.

**7.2.4 UI Testing Methodology**

Manual testing conducted on all 7 UI pages:
Navigation between pages via sidebar radio buttons.
Creating, renaming, duplicating, and deleting stories.
Ingesting chapters via all three input methods.
Verifying wiki content updates after each ingestion.
Verifying knowledge graph adds nodes and edges correctly.
Testing Story Q&A with entity-containing and entity-free queries.
Generating audiobooks for processed chapters.
Running evaluation harness and verifying metric display.

## 7.3 Test Cases
TC-01: spaCy -- Title Normalization
Input: 'Lord Gavlen confronted Elder Myra at the Iron Gate.'
Expected: characters=\['Gavlen','Myra'\], world_terms includes 'Iron Gate'
Result: PASS -- Titles stripped, location detected.

TC-02: spaCy -- Fantasy Name with Hyphen
Input: 'Khal-Mora raised his spirit root and challenged Tier-3 Mage Chen.'
Expected: characters include 'Khal-Mora', world_terms include 'Tier-3 Mage'
Result: PASS -- Hyphen name matched by EntityRuler REGEX pattern.

TC-03: spaCy -- Stop Entity Filtering
Input: 'Last night, Aria met Lucian near the lower realm.'
Expected: 'last night' NOT in results, characters=\['Aria','Lucian'\]
Result: PASS -- Temporal false positive filtered correctly.

TC-04: LLM Extraction -- DEU Event Structure
Input: Sample chapter text with clear action sequences.
Expected: events list with non-empty action_summary, involved_characters, pre_conditions, post_conditions.
Result: PASS -- All DEU fields populated correctly by Gemini Flash.

TC-05: LLM Extraction -- Causal Link Detection
Input: Chapter where Event A clearly causes Event B.
Expected: causes_event_indexes for Event A contains index of Event B.
Result: PASS -- Causal relationship correctly identified.

TC-06: Graduation -- EXTRA Classification
Input: CharacterRuntime(confidence_score=0.10)
Expected: evaluate_graduation() returns GraduationLevel.EXTRA
Result: PASS -- Below 0.25 threshold correctly classified.

TC-07: Graduation -- EVOLVING Classification
Input: CharacterRuntime(confidence_score=0.45)
Expected: evaluate_graduation() returns GraduationLevel.EVOLVING
Result: PASS -- Between 0.25 and 0.75 correctly classified.

TC-08: Graduation -- MAIN_CAST and Voice Assignment
Input: CharacterRuntime(confidence_score=0.85, voice_id=None)
Expected: check_graduation_status() returns True, voice_id is not None
Result: PASS -- Voice ID assigned and locked on first graduation.

TC-09: Graduation -- No Re-assignment After Graduation
Input: CharacterRuntime(confidence_score=0.90, voice_id='af_heart')
Expected: check_graduation_status() returns False, voice_id still 'af_heart'
Result: PASS -- No re-assignment on subsequent calls.

TC-10: Graph -- Character Node Addition
Input: add_character('aria', {display_name: 'Aria', last_seen_chapter: 1})
Expected: graph.has_node('aria') == True, introduction_order == 1
Result: PASS -- Node added with correct attributes.

TC-11: Graph -- Event Node and Edge Addition
Input: add_event('ch1_ev0', 'Aria fights troll', \['aria'\], chapter_id=1)
Expected: event node exists, participant and featured edges both created
Result: PASS -- Both edge directions created correctly.

TC-12: Graph -- PageRank Calculation
Input: Graph with 3 characters and 5 events; current_chapter=5, decay_rate=0.05
Expected: All character scores > 0.0, first character score >= 0.16 (bootstrapping)
Result: PASS -- PageRank computed with bootstrapping guarantee applied.

TC-13: Graph -- Temporal Decay
Input: Character last seen chapter 1, current_chapter=11, decay_rate=0.10
Expected: score = base_score * (0.90)^10 = base_score * 0.3487
Result: PASS -- Decay correctly applied.

TC-14: Graph -- Merge Characters (Alias Resolution)
Input: Nodes 'aria' and 'aria_stormveil' both with event edges
Expected: After merge: 'aria' node removed, 'aria_stormveil' inherits all edges
Result: PASS -- Edges transferred, alias node removed.

TC-15: End-to-End Ingest Pipeline
Input: Complete chapter text via ingest_chapter()
Expected: runtime_db populated, story_graph.json written, wiki files created
Result: PASS -- Full pipeline completes, all files created successfully.

TC-16: Royal Road Scraping -- Index URL
Input: Valid Royal Road fiction index URL
Expected: Chapter list with title and url keys, length > 0
Result: PASS -- Chapter list scraped and persisted to index_state.json.

TC-17: EPUB Parsing
Input: Valid .epub file with multiple chapters
Expected: parse_epub() returns list of {title, text} dicts, length > 0
Result: PASS -- Chapters extracted successfully.

TC-18: RAG Query -- Entity Found in Graph
Input: Story with 2 ingested chapters; query='What happened to Aria?'
Expected: Non-empty response containing chronological event information
Result: PASS -- Time-CoT retrieval returns ordered events with narrative answer.

TC-19: RAG Query -- No Entity in Graph
Input: Empty story graph; query='What happened to Aria?'
Expected: Response indicating no events found
Result: PASS -- Graceful fallback message returned.

TC-20: LLM Fallback on Primary Failure
Input: Invalid Gemini API key; valid Groq API key
Expected: System retries primary 3 times then calls Groq fallback without user-visible error
Result: PASS -- Groq fallback called automatically, valid response returned.

## 7.4 Results
7.4 TEST RESULTS AND SUMMARY

Table 7.2: Entity Extraction Benchmark Results

| **Extraction**

**Method** | **Metric** | **Characters** | **World Terms** | **Combined** |
| -------------------------------- | ---------- | -------------- | --------------- | ------------ |
| spaCy (Rule + NER)               | Precision  | 78%            | 71%             | 75%          |
| spaCy (Rule + NER)               | Recall     | 67%            | 65%             | 66%          |
| spaCy (Rule + NER)               | F1 Score   | 72%            | 68%             | 70%          |
| LLM (Gemini Flash)               | Precision  | 93%            | 88%             | 91%          |
| LLM (Gemini Flash)               | Recall     | 89%            | 82%             | 86%          |
| LLM (Gemini Flash)               | F1 Score   | 91%            | 85%             | 88%          |

Observation:
LLM-based extraction significantly outperforms spaCy, achieving an improvement of 19 F1 points for character extraction. However, spaCy's 70% F1 score with processing time under 500 ms provides a practical trade-off for batch processing scenarios.

Table 7.3: Graph Traversal Latency Results

| **Characters** | **Total Nodes** | **Latency** | **Target** | **Pass** |
|---|---|---|---|---|
| 10 | 20 | 1.2ms | <500ms | YES |
| 50 | 100 | 3.8ms | <500ms | YES |
| 100 | 200 | 8.1ms | <500ms | YES |
| 500 | 1000 | 41.3ms | <500ms | YES |
| 1000 | 2000 | 87.2ms | <500ms | YES |

Observation:
All graph sizes perform well within the target latency of 500 ms. The system demonstrates scalability and can efficiently handle stories with 1000+ characters without performance degradation.

Table 7.4: TTS Real-Time Factor Results

| **Engine** | **Synthesis Time** | **Audio Duration** | **RTF** | **Target** | **Pass** |
|---|---|---|---|---|---|
| Kokoro ONNX | 0.89 sec | 2.13 sec | 0.42 | < 1.0 | YES |
| Edge TTS | 0.66 sec | 2.13 sec | 0.31 | < 1.0 | YES |

Observation:
Both TTS engines achieve a Real-Time Factor (RTF) significantly below 1.0, confirming that audio generation is faster than real-time playback on standard laptop hardware.

Overall Test Summary

- Total Functional Test Cases: 20 / 20 → PASS
- Entity Extraction Performance:
  - spaCy: 70% F1
  - LLM: 88% F1
     _(Both exceed the 60% baseline target)_
- Graph Latency Target (< 500 ms): Achieved at all tested scales
- TTS RTF Target (< 1.0): Achieved for both engines
- Critical Bugs in Final Integration: 0
- Minor Issues Resolved: 2

Issue 1: Unicode encoding error in LLM response parsing → _Fixed_
Issue 2: PageRank failure on disconnected graphs → _Fixed using degree fallback method_

# CHAPTER - 8

# RESULT AND DISCUSSION

## 8.1 Output Screens
**8.1.1 Dashboard Page
**
The Dashboard displays three key metrics in a 3-column layout:
Processed Chapters: Total chapters ingested (from runtime_db.json chapter_counter).
Discovered Characters: Total unique character nodes (len(runtime_db)).
Graduated Characters: Characters with confidence_score >= 0.75 or with voice_id assigned.

Below the metrics, a System Configuration code block displays current engine config:
LLM Engine: groq/llama-3.1-8b-instant
Main TTS: kokoro
Fallback TTS: edge

**8.1.2 Ingestion Engine Page
**
SECTION A -- Fetch from URL: Royal Road URL input form with 'Fetch Content' button. On successful index scrape, chapter count appears. On single-chapter fetch, text auto-populates.
SECTION B -- EPUB Upload: File uploader restricted to .epub extension. On upload and 'Parse EPUB Chapters' click, chapter count message appears and chapter dropdown loads.
SECTION C -- Active Index Panel: Shows scraped index status, chapter selector, 'Load Preview' button, and batch ingestion controls with batch size input.
SECTION D -- Chapter Processing: Title input, text area (pre-filled from URL/EPUB if applicable), extraction method radio selector, temporal decay slider, and 'Process Chapter' primary button.

On successful processing: st.success message, st.balloons animation, and JSON preview showing {id, title, status: 'Graph Updated', extractor_used}.

**8.1.3 Wiki Memory Page
**
Character wiki entries displayed as rendered Markdown. Dropdown selector at top allows selection from all generated characters. Export Wiki Entry download button saves raw Markdown. Sample output for graduated character:

# Aria Stormveil
Role: Protagonist | Status: Active | Age: 19 | Voice: af_heart
First Appearance: Chapter 1 | Last Updated: Chapter 7 | Confidence: 0.8432

Short Description: Aria is the determined young swordswoman introduced in Chapter 1.
Synopsis: Aria wandered the borderlands (Ch.1), repelled a Tier-2 Shadow Wolf (Ch.2), joined Silver Moon Guild (Ch.4), raided Hollowed Keep with Lucian (Ch.6), awarded Inner Disciple rank by Elder Myra (Ch.7).
Affiliations: Silver Moon Guild, Hollow Mountain Refugees
Personality: Fiercely independent, protective of companions, reluctant to accept help

**8.1.4 Knowledge Graph Visualization
**
Full-height (700px) interactive PyVis HTML visualization. Red circles (size 25) for character nodes. Blue circles (size 15) for event nodes. Grey edges for participation. Orange dashed edges for causal links. Physics simulation allows node dragging. Summary statistics (Character Nodes count, Event Nodes count) shown below the graph.

**8.1.5 Story Q&A Page
**
Natural language query form. Example interaction:
USER QUERY: 'What happened to Aria when she joined the Silver Moon Guild?'
SYSTEM RESPONSE: 'Based on the story timeline, Aria first encountered the Silver Moon Guild in Chapter 3 after being rescued by Guild member Davin from a Tier-3 monster attack. She formally applied for membership in Chapter 4 during the Guild Acceptance Ceremony. Her first mission as provisional Guild member occurred in Chapter 5...'

**8.1.6 Audio Hub Page
**
Full Chapter Audiobook section: chapter number selector, engine radio (Kokoro/Edge TTS), 'Synthesize Entire Chapter' primary button, and 'Cancel Generation' secondary button. After generation, embedded HTML5 audio player with CC button for synchronized VTT subtitle playback showing which character is currently speaking.

Character Voice Testing section: graduated character selector with locked voice ID, test dialogue text area, TTS engine selector, and 'Generate Audio' button with st.audio() playback.

**8.1.7 Evaluation Harness Page
**
Three expandable sections:
Entity Precision/Recall/F1: Formatted dataframe comparing spaCy and optional LLM metrics against gold standard.
Graph Traversal Latency: Table showing latency at 5 graph scale points with pass/fail.
TTS Real-Time Factor: Metric cards with RTF for each available engine, color-coded delta (green if below 1.0, red if above 1.0).

## 8.2 Performance Evaluation
**8.2.1 Entity Extraction Performance Analysis
**
The gold standard annotation was created by manually annotating a 3,000-word fantasy chapter. spaCy's improvement over vanilla NER (without EntityRuler): approximately +25% F1 on fantasy text, validating the custom pattern approach.

Key observations on extraction quality:
The EntityRuler hyphen/apostrophe pattern correctly identifies names like Vael'Thar, Khal-Mora, and Jin'sei.
The title-stripping post-processor (Lord Gavlen -> Gavlen) prevents duplicate entries.
LLM's ability to infer character names from pronouns and contextual references gives it a significant recall advantage over pattern-based NER.
False positive rate: spaCy 15% (two-word capitalized pattern overfires), LLM 7%.

**8.2.2 Graph Performance Scaling Analysis
**
Graph performance scales in approximate O(N log N) time due to PageRank's iterative computation (max_iter=100, tol=1e-6). Web novel graphs are sparse -- most characters appear in a subset of events -- which keeps convergence fast. At 2,000 nodes, computation takes approximately 87ms, well within the 500ms target.

Memory usage scales approximately linearly with node count. A 2,000-node graph in NetworkX occupies approximately 8-15MB RAM, negligible on modern hardware.

**8.2.3 TTS Performance Analysis
**
Kokoro ONNX achieves RTF=0.42, generating 2.13 seconds of audio in 0.89 seconds on Intel Core i7 CPU without GPU. For a full 5,000-word chapter (approximately 35 minutes of audio), Kokoro requires approximately 14.7 minutes of generation time. Edge TTS (cloud, RTF=0.31) achieves the same in approximately 10.9 minutes.

**8.2.4 End-to-End Pipeline Latency (spaCy Mode)
**
Measured on Intel Core i7-12th Gen, 16GB RAM, for a 3,000-word chapter:
spaCy NER extraction: 0.31 sec
Alias resolution: 0.01 sec
Graph node and edge updates: 0.08 sec
PageRank computation (50 chars): 0.004 sec
Wiki read/write (10 chars): 0.12 sec
Runtime DB save: 0.02 sec
Chapter text save: 0.01 sec
TOTAL (spaCy mode): 0.55 sec

End-to-End Pipeline Latency (LLM Mode, with network round-trip):
Gemini Flash API call: 2.8-4.2 sec
JSON parse and alias resolution: 0.02 sec
Graph updates and PageRank: 0.09 sec
LLM wiki update (if events): 1.5-3.0 sec
File I/O: 0.15 sec
TOTAL (LLM mode): 4.5-7.5 sec

## 8.3 Comparison with Existing System
**TABLE 8.1: COMPREHENSIVE FEATURE COMPARISON
**
Capability | Traditional | Auto TTS | LangChain | Webnovel Architect
Multi-voice audio | Yes(manual) | No | N/A | Yes(automated)
Serial chapter processing | No | No | No | Yes
Persistent character tracking | No | No | No | Yes
Knowledge graph construction | No | No | No | Yes
DEU causal event modeling | No | No | No | Yes
Temporal story reasoning (QA) | No | No | Partial | Yes (Time-CoT)
Character wiki auto-generation | No | No | No | Yes
Fantasy domain NER | N/A | N/A | No | Yes (EntityRuler)
Zero-GPU operation | Yes | Yes | No | Yes
Character voice consistency | Yes(manual) | No | N/A | Yes(voice locking)
Cost per chapter | \$20-50+ | ~\$0 | ~\$0.01 | ~\$0.002
Time to audio (1 chapter) | Days-weeks | Seconds | N/A | 5-15 min

**TABLE 8.2: ENTITY EXTRACTION F1 COMPARISON
**
| System | Character F1 | Notes |
|---|---|---|
| spaCy en_core_web_sm (vanilla) | ~50% | Fails on fantasy proper nouns |
| spaCy + EntityRuler (ours) | 72% | Domain-adapted with custom patterns |
| BERT-NER (news-trained) | ~55% | Same domain mismatch as vanilla |
| LLM Gemini Flash (ours) | 91% | Contextual understanding resolves domain |
| Human annotation baseline | 98% | Upper bound (inter-annotator ~2% gap) |

**TABLE 8.3: COST COMPARISON FOR PROCESSING A 500-CHAPTER WEB NOVEL
**
Method | Estimated Cost | Time Required
Professional human audiobook | \$25,000-50,000 | 3-6 months
AI TTS (Amazon Polly) | \$200-400 | 2-4 days
Webnovel Architect (LLM mode) | ~\$1.00 API | ~8-16 hours
Webnovel Architect (spaCy) | ~\$0.00 | ~2-4 hours

## 8.4 Discussion
**8.4.1 Neuro-Symbolic Synergy
**
The most significant finding is the complementary strength of the neuro-symbolic approach. The symbolic component (knowledge graph + PageRank) provides deterministic, explainable reasoning about character importance. The same character in the same graph topology always receives the same score, ensuring consistency. The neural component (LLM) provides semantic understanding -- correctly inferring 'the young woman' in a paragraph is 'Aria' based on preceding context -- that no rule-based system can match.

**8.4.2 Bootstrapping Paradox Resolution
**
A key design challenge was the Bootstrapping Paradox: in Chapter 1 of a web novel, the protagonist appears in only one chapter, the same as a minor background character. Standard PageRank cannot distinguish between them on sparse early data. The introduction_order <= 5 guarantee (minimum score 0.16) solves this by temporarily promoting early characters above the voice threshold while the graph accumulates sufficient evidence.

**8.4.3 Temporal Decay Rate Sensitivity
**
The decay_rate parameter is configurable via the UI slider (0.00 to 1.00):
decay_rate = 0.00: No temporal decay (all chapters weighted equally). Best for completed novels.
decay_rate = 0.05 (default): Balanced for typical serial pacing (1-2 chapters per week).
decay_rate = 0.20: Aggressive decay. Characters absent for 5 chapters lose approximately 67% of their relevance. Best for fast-paced stories with rotating character focus.

**8.4.4 System Limitations Identified
**
LIMITATION 1: Non-standard LLM responses: When processing chapters with mixed vocabulary, the LLM occasionally returns entity names in partially different forms. The normalize_id() function partially mitigates this; alias_resolver.py handles most variants.

LIMITATION 2: Very long chapters: Chapters exceeding 15,000 words may hit the context window limit of smaller models (Groq Llama-3.1-8B: 128K context). Gemini Flash (1M context) handles all tested chapter lengths without issues.

LIMITATION 3: Dense dialogue chapters: Chapters with many short dialogue exchanges and few narrative sentences produce sparse DEU event lists, as the LLM focuses on major plot beats. A future improvement is a dialogue-specific event extractor.

# CHAPTER - 9

# CONCLUSION AND FUTURE WORK

## 9.1 Conclusion
Webnovel Architect successfully demonstrates that a neuro-symbolic AI pipeline can transform serialized web novels into living, interactive audio dramas -- processing chapters incrementally, maintaining persistent story intelligence, and generating multi-voice audio entirely without GPU hardware at near-zero operating cost.

**9.1.1 Summary of Achieved Objectives
**
OBJECTIVE 1 (Modular Ingestion) -- ACHIEVED: Three input modes (text, EPUB, Royal Road URL) functional. Batch processing with progress tracking operational.
OBJECTIVE 2 (Hybrid NER) -- ACHIEVED: spaCy EntityRuler achieves 72% F1 on fantasy text (+25% over vanilla). LLM extraction achieves 91% F1 with full DEU event structure.
OBJECTIVE 3 (Dynamic Knowledge Graph) -- ACHIEVED: NetworkX DiGraph stores characters, events, and causal edges. JSON persistence ensures state survives application restarts.
OBJECTIVE 4 (Character Importance) -- ACHIEVED: PageRank + temporal decay + bootstrapping guarantee. Graduation system with EXTRA/EVOLVING/MAIN_CAST tiers operational.
OBJECTIVE 5 (Multi-Voice Audio) -- ACHIEVED: Kokoro ONNX (RTF=0.42) and Edge TTS (RTF=0.31) both meet the under 1.0 RTF target. Voice locking persists across sessions.
OBJECTIVE 6 (Time-CoT RAG) -- ACHIEVED: Graph-traversal RAG with chronological event ordering produces temporally-accurate story Q&A answers.
OBJECTIVE 7 (Interactive UI) -- ACHIEVED: 7-page Streamlit dashboard with full multi-story management operational.

**9.1.2 Key Technical Contributions
**
CONTRIBUTION 1: The Dynamic Event Unit (DEU) schema capturing pre_conditions, post_conditions, causal links, and spatial location provides a richer narrative representation than prior narrative graph approaches.

CONTRIBUTION 2: The Switchboard Architecture -- abstract adapter interfaces for LLM and TTS engines configurable via a single YAML file -- represents a maintainable, future-proof approach to AI component integration.

CONTRIBUTION 3: The Temporal PageRank with Bootstrapping Mitigation algorithm specifically addresses the cold-start problem in serial fiction graph analysis.

CONTRIBUTION 4: The Time-CoT RAG method applies temporal reasoning principles to story Q&A, producing chronologically-grounded answers that standard embedding-based RAG cannot achieve.

CONTRIBUTION 5: The complete implementation of a Zero-GPU audiobook production pipeline for serial fiction, validated against quantitative RTF benchmarks.

**9.1.3 Academic and Practical Significance
**
From an academic perspective, this project demonstrates the viability of combining symbolic knowledge graphs with neural language models for narrative understanding, contributing to the growing field of neuro-symbolic AI. From a practical perspective, it provides an immediately usable tool for the growing community of 15+ million active web novel readers who lack access to professional audiobook productions.

## 9.2 Future Work
FUTURE DIRECTION 1 -- LLM-Based Co-Reference Resolution:
Current alias resolution uses string similarity matching. A future version could pass extracted entity lists to an LLM with the prompt: 'Identify which names likely refer to the same person and group them.' This would dramatically improve character node accuracy for stories with complex naming conventions.

FUTURE DIRECTION 2 -- Multi-Language Support:
The spaCy EntityRuler patterns and LLM prompts are English-only. Extending to support Chinese web novels (xianxia, wuxia), Japanese light novels, and Korean manhwa would serve a significantly larger user base. LiteLLM's provider-agnostic interface allows incorporating multilingual models without major architectural changes.

FUTURE DIRECTION 3 -- Emotion-Aware Voice Modulation:
Currently voice synthesis uses fixed voice IDs and speed settings. A future version could analyze dialogue sentiment and adjust TTS parameters dynamically: angry dialogue gets faster speech rate and higher variation; whispered dialogue gets lower volume and slower rate; excited dialogue gets increased speaking rate.

FUTURE DIRECTION 4 -- DyG-RAG Conversational Chatbot:
The current Q&A system answers single questions. A conversational chatbot would maintain dialogue history and allow follow-up questions ('What happened next?', 'Who else was involved?'), with the knowledge graph serving as persistent structured memory. This is the primary planned next milestone (Phase 7).

FUTURE DIRECTION 5 -- Fine-Tuned Domain NER Model:
Training a custom spaCy or HuggingFace transformer model on a fantasy web-novel corpus would improve entity F1 from the current 72% toward the 90%+ achieved by LLM extraction but at spaCy's processing speed.

FUTURE DIRECTION 6 -- EPUB/PDF Wiki Export:
Converting generated character wikis into a polished EPUB or PDF document -- a companion book for the story -- would be highly valued by readers. The existing Markdown wiki format could be compiled using python-docx or Pandoc.

FUTURE DIRECTION 7 -- Real-Time Publishing Webhook Integration:
Implementing an RSS feed monitor that automatically triggers chapter ingestion when a new chapter is published on Royal Road would enable fully automatic processing. The system would update its knowledge graph, wikis, and prepare audio production without any user action required.

FUTURE DIRECTION 8 -- Relationship Type Classification:
The current knowledge graph models character-event edges only. Adding typed character-to-character relationship edges (ally, rival, romantic interest, mentor, student) classified by LLM analysis would enable richer Q&A and graph visualizations highlighting social dynamics.

FUTURE DIRECTION 9 -- Collaborative Multi-Reader Support:
Adding user authentication and shared story projects would allow reading groups or fan communities to collaboratively annotate and enrich auto-generated wikis, combining community knowledge with AI automation.

FUTURE DIRECTION 10 -- Mobile Application:
A React Native mobile app consuming the FastAPI backend would make Webnovel Architect accessible on smartphones, enabling readers to listen to generated audiobooks on-the-go and ask story questions from their mobile devices.

# REFERENCES & BIBLIOGRAPHY

\[1\] Honnibal, M., and Montani, I. (2017). spaCy 2: Natural language understanding with Bloom embeddings, convolutional neural networks and incremental parsing. Explosion AI. <https://spacy.io>

\[2\] Lewis, P., Perez, E., Piktus, A., et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. Advances in Neural Information Processing Systems (NeurIPS), 33, 9459-9474.

\[3\] Page, L., Brin, S., Motwani, R., and Winograd, T. (1999). The PageRank Citation Ranking: Bringing Order to the Web. Technical Report 1999-66, Stanford InfoLab.

\[4\] Devlin, J., Chang, M.W., Lee, K., and Toutanova, K. (2019). BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding. Proceedings of NAACL-HLT 2019, 4171-4186.

\[5\] van den Oord, A., Dieleman, S., Zen, H., et al. (2016). WaveNet: A Generative Model for Raw Audio. arXiv preprint arXiv:1609.03499.

\[6\] Mihalcea, R., and Tarau, P. (2004). TextRank: Bringing Order into Texts. Proceedings of EMNLP 2004, 404-411.

\[7\] Ren, Y., Ruan, Y., Tan, X., et al. (2020). FastSpeech 2: Fast and High-Quality End-to-End Text to Speech. arXiv preprint arXiv:2006.04558.

\[8\] Hagberg, A., Swart, P., and Chult, D. (2008). Exploring network structure, dynamics, and function using NetworkX. Proceedings of the 7th Python in Science Conference, 11-15.

\[9\] Google DeepMind. (2024). Gemini: A Family of Highly Capable Multimodal Models. Technical Report. <https://deepmind.google/technologies/gemini/>

\[10\] Kipf, T.N., and Welling, M. (2017). Semi-Supervised Classification with Graph Convolutional Networks. Proceedings of ICLR 2017.

\[11\] Streamlit Inc. (2024). Streamlit Documentation. <https://docs.streamlit.io>

\[12\] NetworkX Developers. (2023). NetworkX 3.x Documentation. <https://networkx.org>

\[13\] LiteLLM Contributors. (2024). LiteLLM: Call all LLM APIs in the OpenAI format. <https://github.com/BerriAI/litellm>

\[14\] Kokoro TTS. (2024). Kokoro: Open Weight TTS Model (82M parameters). HuggingFace. <https://huggingface.co/hexgrad/Kokoro-82M>

\[15\] Microsoft Corporation. (2024). Azure Cognitive Services Text to Speech. <https://azure.microsoft.com/products/cognitive-services/text-to-speech/>

\[16\] Vrandecic, D., and Krotzsch, M. (2014). Wikidata: A Free Collaborative Knowledge Base. Communications of the ACM, 57(10), 78-85.

\[17\] Wadhwa, S., Amir, S., and Wallace, B.C. (2023). Revisiting Relation Extraction in the era of Large Language Models. Proceedings of ACL 2023.

\[18\] Garg, S., Chakraborty, T., and Saha, S.K. (2020). Temporal Reasoning in Natural Language Inference. Findings of EMNLP 2020.

\[19\] Walker, D., Xie, H., Yan, K.K., and Bhatt, S. (2007). Ranking Scientific Publications Using a Model of Network Traffic. Journal of Statistical Mechanics, 2007.

\[20\] Lafferty, J., McCallum, A., and Pereira, F.C.N. (2001). Conditional Random Fields: Probabilistic Models for Segmenting and Labeling Sequence Data. ICML 2001, 282-289.

# APPENDIX - A

## FULL CODE

The complete source code for Webnovel Architect is available in the project repository. The codebase consists of 12 primary modules totalling approximately 2,500 lines of Python. Key files include:

app_ui.py (861 lines) - Streamlit UI application and all 7 page implementations.

app/services/ingest.py (360 lines) - Central ingestion orchestrator and runtime persistence.

app/services/extraction.py (208 lines) - Dual NER pipeline (spaCy and LLM modes).

adapters/graph_adapter.py (200 lines) - Knowledge graph manager with PageRank and temporal decay.

app/services/audiobook_generator.py (16,141 bytes) - Multi-voice audio production and VTT subtitle generation.

_GITHUB URL :_ [_https://github.com/Koushik810-Coder/webnovel-architect.git_](https://github.com/Koushik810-Coder/webnovel-architect.git)_._

# APPENDIX - B

**Mapping of Sustainable Development Goals (SDGs)(1-2 pages)**

This section explains how the project contributes to relevant Sustainable Development Goals (SDGs) by addressing societal, technological, or educational needs.

| **SDG**                                        | **Contribution of the Project**                                                                                                                                                                |
| ---------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SDG 4: Quality Education                       | Automated audiobook generation makes serialized fiction accessible to visually impaired readers and reduces the literacy barrier for complex narratives.                                       |
| SDG 9: Industry, Innovation and Infrastructure | Introduces a novel neuro-symbolic AI pipeline (DEU schema, Time-CoT RAG) that operates on commodity CPU hardware, advancing accessible AI infrastructure for the digital media industry.       |
| SDG 10: Reduced Inequalities                   | Reduces the cost of audiobook production from \$25,000-\$50,000 to approximately \$1 per novel, democratizing high-quality audio content for independent and self-published authors worldwide. |

### Table B.1: Mapping of SDGs
Summarize how the project supports selected SDGs by improving efficiency, accessibility, innovation, or decision-making.

# APPENDIX - C

**Published Paper**

If a research paper based on this project has been submitted to or published in a conference or journal, attach a copy of the paper (or acceptance letter) here. Include the full citation in the following format:

_Author(s). "Paper Title." Conference/Journal Name, Volume(Issue), Pages, Year. DOI: XXXXXXXXXX_

If no paper has been published yet, this appendix may be left blank or replaced with an abstract submitted to a relevant conference.

# APPENDIX B

## MAPPING OF SUSTAINABLE DEVELOPMENT GOALS (SDGs)

This section explains how the Webnovel Architect project contributes to relevant United Nations Sustainable Development Goals (SDGs). The project aligns with three primary SDGs.

SDG 4: QUALITY EDUCATION
Webnovel Architect contributes to SDG 4 (Ensure inclusive and equitable quality education and promote lifelong learning opportunities for all) by:
(a) Making literary content more accessible through automated audiobook generation. Visually impaired individuals who cannot read printed text can consume web novels as high-quality multi-voice audio productions at zero cost.
(b) Providing an educational tool for NLP and AI students. The project demonstrates real-world applications of Named Entity Recognition, Knowledge Graphs, RAG systems, and TTS synthesis.
(c) Reducing the literacy barrier for consuming complex serialized narratives by enabling audio formats that do not require sustained reading ability.

SDG 9: INDUSTRY, INNOVATION AND INFRASTRUCTURE
Webnovel Architect contributes to SDG 9 (Build resilient infrastructure, promote sustainable industrialization and foster innovation) by:
(a) Developing and demonstrating novel AI infrastructure (neuro-symbolic pipeline, DEU schema, Time-CoT RAG) that can be adopted by the digital media and publishing industries.
(b) Making advanced AI capabilities (LLM extraction, knowledge graphs, neural TTS) accessible on commodity hardware without specialized GPU infrastructure.
(c) Providing open-source tooling that independent authors and content creators can use to produce professional-quality audio content without expensive studio infrastructure.

SDG 10: REDUCED INEQUALITIES
Webnovel Architect contributes to SDG 10 (Reduce inequality within and among countries) by:
(a) Democratizing audiobook production. Professional audiobooks cost \$5,000-\$50,000 and are accessible only to authors with publishing contracts or significant capital. Webnovel Architect enables any author to produce multi-voice audiobooks for approximately \$1-2 per novel.
(b) Reducing the advantage held by major publishing conglomerates over independent creators. The system levels the production quality playing field for self-published and indie authors.
(c) Enabling readers in regions without access to traditional audiobook services or libraries to enjoy story content in an accessible audio format.

### Table B.1: Mapping of SDGs to Project Features

SDG 4 | Quality Education | Zero-cost audiobook generation for visually impaired readers
SDG 4 | Quality Education | Educational NLP and AI demonstration codebase for students
SDG 9 | Industry and Innovation | Novel neuro-symbolic pipeline architecture (DEU + Time-CoT)
SDG 9 | Industry and Innovation | Zero-GPU deployment on commodity hardware
SDG 9 | Industry and Innovation | Switchboard adapter pattern (reusable industry infrastructure)
SDG 10 | Reduced Inequalities | Democratizing audiobook production (approx \$1 vs \$50,000)
SDG 10 | Reduced Inequalities | Open-source tools for independent and indie authors

SUMMARY: The Webnovel Architect project most strongly contributes to SDG 9 through its novel neuro-symbolic AI architecture and Zero-GPU infrastructure design. It meaningfully advances SDG 4 by making serialized narrative content accessible through automated audio production, and SDG 10 by democratizing high-quality audiobook production for independent content creators.

# APPENDIX D

## GLOSSARY OF KEY TERMS

API (Application Programming Interface): A set of protocols and rules allowing software components to communicate with each other. In this project, API refers specifically to the LLM provider APIs (Google Gemini, Groq) used for entity extraction and wiki generation.

DEU (Dynamic Event Unit): A structured representation of a narrative event. Each DEU captures: action_summary, involved_characters, pre_conditions, post_conditions, location, and causes_event_indexes. This schema was designed specifically for this project.

DyG (Dynamic Graph): A graph whose structure changes over time as new data arrives. In Webnovel Architect, the story graph is a DyG that grows with each new chapter ingested.

EntityRuler: A spaCy pipeline component that matches text against user-defined rule patterns before or after the statistical NER model, enabling domain adaptation without retraining.

LLM (Large Language Model): A neural network trained on massive text corpora capable of generating, summarizing, and extracting information from text. This project uses Google Gemini Flash and Groq Llama-3.1-8B as the primary LLMs.

LiteLLM: An open-source Python library providing a unified API interface to 100+ LLM providers, allowing model switching without code changes. Used as the Switchboard in this project.

NER (Named Entity Recognition): The NLP task of identifying and classifying named entities (persons, locations, organizations) in text. Central to the extraction module.

ONNX (Open Neural Network Exchange): An open format for representing machine learning models, enabling cross-platform inference without framework dependency. Kokoro TTS uses ONNX format.

PageRank: A graph centrality algorithm developed by Larry Page at Google. Assigns importance scores to nodes based on the quantity and quality of incoming edges. Used to compute character importance from the story graph structure.

RAG (Retrieval-Augmented Generation): An AI architecture combining a retrieval mechanism with a language model generator. Retrieved context prevents LLM hallucination in Q&A tasks.

RTF (Real-Time Factor): A metric for TTS speed. RTF equals synthesis_time divided by audio_duration. RTF below 1.0 means synthesis is faster than real-time playback.

Streamlit: An open-source Python framework for building interactive web applications. Used as the UI framework for all user-facing features of Webnovel Architect.

Temporal Decay: The mechanism by which a character's importance score decreases over time if the character does not appear in recent chapters. Implemented as: score equals base_score multiplied by (1 minus decay_rate) raised to the age_in_chapters power.

Time-CoT (Time Chain-of-Thought): The RAG variant in Webnovel Architect where retrieved events are sorted chronologically before prompting the LLM, enabling temporal reasoning in story Q&A.

TTS (Text-to-Speech): Technology that synthesizes human-sounding audio from text input. This project uses Kokoro ONNX (local) and Microsoft Edge TTS (cloud).

UUID (Universally Unique Identifier): A 128-bit identifier used to uniquely identify each story, preventing name collision across the data directory.

VTT (Web Video Text Tracks): A subtitle file format providing timestamped captions synchronized with audio playback. Generated alongside each audiobook MP3 to display the current speaker.

Webnovel: A serialized form of fiction published chapter by chapter on online platforms. Unlike traditional novels, webnovels may have thousands of chapters published over multiple years, creating the unique incremental processing challenge this project addresses.

# APPENDIX E

## SYSTEM CONFIGURATION AND SETUP GUIDE

This appendix documents the complete step-by-step setup process for Webnovel Architect version 1.0 on a Windows system.

STEP 1: PREREQUISITES
Ensure the following are installed before proceeding:
- Python 3.9 or later (download from python.org)
- Git (download from git-scm.com)
- A code editor such as Visual Studio Code or PyCharm

STEP 2: CLONE THE REPOSITORY
Open a terminal or PowerShell window and run:
git clone <https://github.com/<username>/webnovel-architect.git>
cd webnovel-architect

STEP 3: CREATE AND ACTIVATE VIRTUAL ENVIRONMENT
python -m venv venv
venv\\Scripts\\activate (Windows PowerShell)
source venv/bin/activate (Linux/macOS)

STEP 4: INSTALL DEPENDENCIES
pip install -r requirements.txt
python -m spacy download en_core_web_sm

STEP 5: CONFIGURE API KEYS
Create a .env file in the project root directory with the following content:
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here

Obtain API keys from:
- Google Gemini: <https://aistudio.google.com/app/apikey> (free tier available)
- Groq: <https://console.groq.com/> (free tier available)

STEP 6: CONFIGURE ENGINE SELECTION
Edit config.yaml to select your preferred engines:
llm_model: 'gemini/gemini-2.5-flash' # or groq/llama-3.1-8b-instant
tts_engine: 'kokoro' # or edge
fallback_tts: 'edge'

STEP 7: OPTIONAL -- INSTALL KOKORO TTS MODEL
For local TTS without internet dependency, download the Kokoro model files:
- kokoro-v0_19.onnx (290 MB)
- voices-v1.0.bin (48 MB)
Place both files in the models/ directory of the project.
Download from: <https://huggingface.co/hexgrad/Kokoro-82M>

If Kokoro model files are not present, the system automatically falls back to Edge TTS.

STEP 8: LAUNCH THE APPLICATION
streamlit run app_ui.py

The application will open in your default web browser at <http://localhost:8501>

STEP 9: QUICK START WORKFLOW
1\. Click 'Create New Story' in the sidebar and enter a story name.
2\. Navigate to the 'Ingestion Engine' page.
3\. Paste a chapter title and text in the respective fields.
4\. Select 'spaCy' extraction mode for speed or 'LLM' for accuracy.
5\. Click 'Process Chapter' and wait for the success confirmation.
6\. Navigate to 'Wiki Memory' to view auto-generated character profiles.
7\. Navigate to 'Knowledge Graph' to view the character-event visualization.
8\. Navigate to 'Story Q&A' and ask a question about your story.
9\. Navigate to 'Audio Hub' and click 'Synthesize Entire Chapter' for audiobook generation.

TROUBLESHOOTING COMMON ISSUES:

Issue: 'GEMINI_API_KEY not found' error
Solution: Ensure .env file is in the project root directory and contains the correct key.

Issue: 'spaCy model not found' error
Solution: Run 'python -m spacy download en_core_web_sm' in the virtual environment.

Issue: Kokoro TTS 'model file not found' warning
Solution: Either place Kokoro model files in models/ directory or set tts_engine: 'edge' in config.yaml to use cloud TTS instead.

Issue: Empty knowledge graph after chapter ingestion
Solution: Ensure the chapter text contains named characters. Try switching to LLM extraction mode which provides better entity recognition for fantasy text.