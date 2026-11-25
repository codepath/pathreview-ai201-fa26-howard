## Solution plan

**Issue:** [Architecture doc doesn't explain the hybrid retrieval scoring formula](https://github.com/codepath/pathreview-ai201-fa26-howard/issues/11)

### Understand
The architecture guide describes hybrid retrieval as combining vector similarity and BM25 keyword search, but does not explain how the scores are normalized or combined. `HybridRetriever` normalizes each result set by its maximum score and blends the normalized scores using configurable weights that default to 0.7 for vector search and 0.3 for keyword search. The expected change is to explain this existing behavior in the docs without changing retrieval code.

### Map
- `docs/ARCHITECTURE.md` — the file to update with the scoring explanation and example.
- `rag/retriever/hybrid.py` — reference for score normalization, default weights, blending, and missing-score behavior.
- `rag/retriever/vector_store.py` — reference for how vector search scores are generated.
- `rag/retriever/keyword_search.py` — reference for BM25 keyword scores.

### Plan
- Add a hybrid scoring subsection to `docs/ARCHITECTURE.md`.
-Explain that vector and keyword results are normalized separately by dividing each score by the maximum score in that result set.
- Document the default weighted-sum formula: `0.7 × normalized vector score + 0.3 × normalized keyword score`.
- Include a worked example, such as scores of 0.8 and 0.6 producing `0.7 × 0.8 + 0.3 × 0.6 = 0.74`.
- Clarify that the weights are configurable and that a missing score from one search method contributes zero; compare the wording with the implementation.

### Inputs & outputs
The inputs are a query's vector-search and keyword-search results and their scores. The documentation will show how the normalized scores are combined into a blended score used to rank each candidate chunk. For example, normalized scores of 0.8 (vector) and 0.6 (keyword) produce a blended score of 0.74 with the default weights.

### Risks & unknowns
The weights are constructor parameters, so the docs must identify 0.7 and 0.3 as defaults rather than fixed values. The code normalizes against each returned result set's maximum, so the explanation should not imply scores are normalized across the full corpus or comparable across different queries. The architecture guide should stay concise and avoid claiming to explain BM25 or vector-distance internals beyond what is needed to describe the blend.

### Edge cases
- If a chunk appears in only one result set, its score for the other method is zero.
- If a result set's maximum score is zero, the implementation uses zero for its normalized scores instead of dividing by zero.
- If custom weights are passed to `HybridRetriever`, the blended score uses those values instead of the defaults.
