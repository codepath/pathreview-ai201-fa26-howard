## Solution plan

**Issue:** [#69 — Output parser crashes on a top-level JSON array fallback](https://github.com/codepath/pathreview-ai201-fa26-howard/issues/69)

### Understand

Both JSON decode paths in `parse_review_output()` pass the decoded value to `_parse_json_output()`. A valid array decodes to a Python list, so the dictionary parser raises an `AttributeError` when it calls `data.items()`. The exception escapes before the text fallback. Array responses should preserve their feedback as text and return normally. Existing object responses should still produce structured sections.

### Map

- `rag/generator/output_parser.py` contains the raw and fenced JSON decode paths, the dictionary parser, and the existing plain-text fallback. Change the two decode paths here.
- `tests/unit/test_output_parser.py` contains the strict expected-failure test for #69 and existing object and plain-text cases. Update the regression coverage here.
- `rag/generator/review_generator.py` calls the parser and uses the first returned section. Use it to verify the return contract.

### Plan

1. Check the decoded value at both JSON entry points. Send dictionaries to `_parse_json_output()` as before.
2. Route successfully decoded non-object values through `_parse_plaintext_output()`, passing the original response so feedback is preserved. Keep the existing recovery behavior for invalid JSON.
3. Remove the strict expected-failure marker for #69 once the fix passes. Cover raw and fenced arrays, and assert that the fallback returns a `general_feedback` section containing the original text.
4. Run `.venv/bin/python -m pytest tests/unit/test_output_parser.py -q` from the repository root and confirm the existing object and plain-text cases still pass.

### Inputs & outputs

The parser accepts a raw model-response string and returns a list of `FeedbackSection` objects. A raw or fenced array should produce one section with `section_name="general_feedback"`, the original response as content, confidence `0.7`, and an empty suggestions list. Objects retain the existing structured output. An empty object still returns an empty list.

### Risks & unknowns

- The raw and fenced branches are separate in `output_parser.py`. Guarding only the raw branch would leave the fenced crash intact.
- The issue asks for graceful fallback and does not specify a schema for array items. The plan preserves the full response as one section, which fits `review_generator.py` because it consumes only the first parsed section.
- Keep JSON decode failures on the existing recovery path. A broad exception handler could hide bugs in the structured parser and change the behavior of malformed fenced responses.

### Edge cases

- A fenced array with explanatory text around the fence should preserve the full response in the fallback section.
- An empty array, arrays of objects or mixed values, and valid scalar JSON should take the text fallback without relying on dictionary methods.
- Valid raw or fenced objects should keep their section names and suggestions. Malformed JSON and ordinary prose should continue through the existing plain-text path.
