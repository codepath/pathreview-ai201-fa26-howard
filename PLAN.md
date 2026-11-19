## Solution plan
**Issue:** [Faithfulness checker crashes when a context chunk has `text: None`](https://github.com/codepath/pathreview-ai201-fa26-howard/issues/60)

### Understand
What is the root cause of this issue? 
The `check()` method uses `chunk.get("text", "")`. If the "text" key is completely missing, it defaults to `""`. However, if the key exists but its value is explicitly `None`, it returns `None`. The subsequent `" ".join(...)` operation then raises a `TypeError` because it expects strings, not `NoneType`.

### Map
Which files, functions, or modules are involved?
*   `rag/evaluator/faithfulness_checker.py` (specifically the `check()` method).
*   `tests/unit/test_faithfulness_checker.py` (to verify the fix).

### Plan
What are the steps to fix this issue?
1. Modify the list comprehension in `faithfulness_checker.py` to evaluate the retrieved text, substituting an empty string if the result is falsy/None (e.g., changing `chunk.get("text", "")` to `chunk.get("text") or ""`).
2. Run the specific `test_none_context_chunk_text` test to ensure the `TypeError` is resolved.
3. Run the full `pytest` suite to ensure the logic change doesn't break any other evaluations.

### Inputs & outputs
What does your fix take as input? What should it produce or change?
*   **Input:** `feedback` (str) and `context_chunks` (list of dicts, where a dict might contain `{'text': None}`).
*   **Output:** The method should successfully return a `float` faithfulness score without throwing a `TypeError`.

### Risks & unknowns
What could go wrong? What are you still unsure about?
*   Does `chunk.get("text")` ever return an empty list or integer that might still break `.join()` even if it isn't `None`? I am assuming it strictly receives strings or `None`.

### Edge cases
What inputs or states should your fix handle gracefully?
*   Chunks with a completely missing "text" key.
*   Chunks where the "text" key is explicitly set to `None`.
*   An entirely empty list of `context_chunks`.