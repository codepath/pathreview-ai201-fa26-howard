## Solution plan

**Issue:** Faithfulness checker crashes when a context chunk has `text: None` | https://github.com/codepath/pathreview-ai201-fa26-howard/issues/60

### Understand
What is the root cause of this issue? What behavior is expected vs. actual?

The checker builds one context string by joining each chunk's `text` value. `chunk.get("text", "")` only uses the empty-string fallback when the key is missing so will it return `None` when the key exists with a `None` value. Passing that result to `" ".join(...)` raises the `TypeError: sequence item 0: expected str instance, NoneType found`, so evaluation stops instead of returning a faithfulness score.

The expected behavior is to treat a `None` chunk text like missing text and continue evaluating, while preserving the existing behavior for valid string text.

### Map
Which files, functions, or modules are involved?
List the specific files you expect to touch.

- `rag/evaluator/faithfulness_checker.py`
  - `FaithfulnessChecker.check()` constructs the joined context and contains the root cause.
- `tests/unit/test_faithfulness_checker.py`
  - `test_none_context_chunk_text` reproduces the issue and should verify the corrected behavior.

### Plan
What are the steps to fix this issue?
Break it into 3–5 concrete sub-tasks.

1. Update `FaithfulnessChecker.check()` so `None` text values are converted to an empty string before the context chunks are joined.
2. Preserve normal scoring for chunks whose `text` value is already a string, as well as graceful handling of a missing `text` key.
3. Update the `test_none_context_chunk_text` test to mark the intended successful behavior rather than marking the issue as an expected failure.
4. Run the focused faithfulness-checker tests and the relevant type/lint checks.

### Inputs & outputs
What does your fix take as input? What should it produce or change?

The input would still be a feedback string and a list of context-chunk dictionaries. For a `{"text": None}` chunk, the checker should use an empty string for that chunk and return a float score between `0.0` and `1.0` instead of raising an exception. Valid text strings should produce the same scores as before.

### Risks & unknowns
What could go wrong? What are you still unsure about?

Changing the fallback logic could unintentionally alter scoring for valid values if the implementation is broader than the `None` case. The fix has to stay limited to missing or `None` text values.

### Edge cases
What inputs or states should your fix handle gracefully?

- A context chunk with `text: None`.
- A context chunk with no `text` key.
- A context chunk with valid string text.
- An empty context-chunk list.
- Empty feedback or feedback with no extractable claims.