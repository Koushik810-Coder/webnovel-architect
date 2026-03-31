# Phase 6: Quantitative Evaluation Results Summary

Below is the condensed summary of the quantitative evaluation tests ran for the Webnovel Architect Phase 6 Review. The complete details of the methodology and context are contained within the `4_Research_Paper.md` document.

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

### Metric 2: Graph Traversal Latency (Zero-GPU Simulation)
Measured the CPU lookup latency of the PageRank temporal decay mechanism across structural Directed Acyclic Graphs of scaling topological density.
*   **10 nodes**: $124.0$ ms
*   **50 nodes**: $0.8$ ms
*   **100 nodes**: $0.8$ ms
*   **500 nodes**: $1.7$ ms
*   **1000 nodes**: **$3.4$ ms** *(Pass, target $< 500$ ms)*
*Conclusion: The temporal graph scaling is effectively instantaneous on an isolated consumer CPU.*

### Metric 3: TTS Real-Time Factor (RTF)
Tested synthesized audio duration efficiency vs. logical generation time.
*   **Edge TTS Generator**: **$0.127$ RTF** *(Pass, target $< 1.0$)*
*(Approximate audio duration: $0.17$s generated natively in $0.02$ seconds)*

### Metric 4: Spearman Rank Correlation ($\rho$)
*   **N/A**: The fallback regex `spaCy` extraction pipeline—utilized internally by the Spearman evaluation metric prior to TTS synthesis—failed to correctly identify characters with unconventional names (such as "Zorian" vs "Kirielle"), preventing the rank arrays from aligning logically for mathematical analysis. 

### Metric 5: End-to-End System Evaluation
Complete execution of the pipeline: Text Ingestion $\rightarrow$ LLM Context Interpretation $\rightarrow$ DAG Node Connection $\rightarrow$ Audiobook Script Structuring $\rightarrow$ Synthesized Media Construction.
*   **Step 1: Ingestion & Spatial Graph Update**: $37$ ms
*   **Step 2: Scripting & Audio Model Synthesis**: $87.8$ s
*   **Step 3: WebVTT Sequence Offset Compilation**: Generated ($< 10$ ms)
*   **Status: PASS**
