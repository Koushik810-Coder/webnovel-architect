# Phase 6: Quantitative Evaluation Results Summary

Below is the condensed summary of the quantitative evaluation tests run for the Webnovel Architect Phase 6 Review. The complete methodology and context is in `4_Research_Paper.md`. Raw simulation data is in `dataset/decay_results.csv`; the ablation chart is `dataset/temporal_ablation.png`.

### Metric 1: Entity Extraction (Precision / Recall / F1)
Text string extraction tested against the dense naming conventions of serialized fantasy webnovels.
*   **spaCy Fallback Pipeline**: 
    *   Character Entities: $40\%$ F1
    *   World Terms: $22\%$ F1
    *   Combined Set: $46\%$ F1 *(Failed target: $\ge 80\%$)*
*   **LiteLLM Neural Pipeline**: 
    *   Character Entities: **$100\%$ F1**
    *   World Terms: $77\%$ F1
    *   Combined Set: **$84\%$ F1** *(Pass)*

**Multi-chapter NER Recall (spaCy, 5-chapter corpus):**

| Chapter | Gold | Extracted | True Positives | Recall |
|---|---|---|---|---|
| 1 | 5 | 15 | 5 | **1.000** |
| 2 | 5 | 23 | 5 | **1.000** |
| 3 | 5 | 20 | 5 | **1.000** |
| 4 | 4 | 14 | 4 | **1.000** |
| 5 | 6 | 21 | 6 | **1.000** |
| **Macro Avg** | — | — | — | **1.000 ✅** |

*Perfect recall across all five chapters (zero missed protagonists). Lower macro-precision (0.274) is by design — over-extraction is filtered by PageRank.*

### Metric 2: Graph Traversal Latency (Zero-GPU Simulation)
Measured the CPU lookup latency of the PageRank temporal decay mechanism across structural Directed Acyclic Graphs of scaling topological density (pre-warmed; cold-start artifact excluded).
*   **10 nodes**: $0.7$ ms
*   **50 nodes**: $0.8$ ms
*   **100 nodes**: $0.7$ ms
*   **500 nodes**: $1.7$ ms
*   **1000 nodes**: **$3.2$ ms** *(Pass, target $< 500$ ms)*
*Conclusion: The temporal graph scaling is effectively instantaneous on an isolated consumer CPU — > 150× under target.*

### Metric 3: TTS Real-Time Factor (RTF)
Tested synthesized audio duration efficiency vs. logical generation time.
*   **Edge TTS Generator**: **$0.127$ RTF** *(Pass, target $< 1.0$)*
*(Approximate audio duration: $0.17$s generated natively in $0.02$ seconds)*

### Metric 4: Lambda (λ) Ablation — Multi-Chapter Decay Simulation
Longitudinal simulation across 5 chapters tracking Temporal PageRank under two regimes:

| Condition | Ch.1-absent character score at Ch.5 | Released from memory? |
|---|---|---|
| **λ = 0.0** (Vector RAG baseline) | Permanently above δ_lower | ❌ Never released |
| **λ = 0.15** (DyG-RAG) | Decays below δ_lower = 0.3 | ✅ Correctly released |

*Empirical proof: DyG-RAG correctly fades absent characters; static Vector RAG does not. See `dataset/temporal_ablation.png`.*

**Spearman ρ:** Undefined in single-chapter context (Δt = 0 collapses decay multiplier to 1.0). Multi-chapter ablation above is the correct evaluation.

### Metric 5: End-to-End System Evaluation
Complete execution of the pipeline: Text Ingestion $\rightarrow$ LLM Context Interpretation $\rightarrow$ DAG Node Connection $\rightarrow$ Audiobook Script Structuring $\rightarrow$ Synthesized Media Construction.
*   **Step 1: Ingestion & Spatial Graph Update**: $37$ ms
*   **Step 2: Scripting & Audio Model Synthesis**: $87.8$ s
*   **Step 3: WebVTT Sequence Offset Compilation**: Generated ($< 10$ ms)
*   **Status: PASS**
