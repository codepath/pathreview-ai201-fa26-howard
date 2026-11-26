## Solution plan

**Issue:** [#12 — Add snapshot tests for prompt templates to catch accidental changes](https://github.com/codepath/pathreview-ai201-fa26-howard/issues/12)

### Understand

I want a test that catches an edit to a prompt people already know as `v1`. The current snapshot test concatenates every template, computes an MD5 digest, and checks that the result is a 32-character string. In the reproduction, reversing the request for specific examples left all 37 prompt tests green. A saved expectation for each name and version would make that edit visible.

### Map

- `rag/generator/prompt_templates.py` holds `PROMPT_TEMPLATES`, a dictionary of names, versions, and prompt strings. Its `get_template(name, version="v1")` function returns the selected text.
- `rag/generator/review_generator.py` calls that lookup in `ReviewGenerator.generate_section()` before substituting the portfolio context. The text I need to snapshot is the reusable prompt, before any user data is inserted.
- `tests/unit/test_prompt_templates.py` contains `TestPromptTemplates.test_template_snapshot_content_hash` alongside checks for placeholders, template names, and invalid versions. I expect this to be the only code file I change.

### Plan

1. Record a fixed SHA-256 digest for each of the five existing `(name, version)` pairs, using the exact UTF-8 prompt text at the reproduced baseline.
2. Replace the length check with a parameterized comparison against each recorded digest. Include both the name and version in a failing case so I can find the changed prompt.
3. Compare the registry's version keys with the snapshot keys. Verify that adding a second version calls for its own snapshot and that removing a recorded version is detected.
4. Rerun the in-memory wording edit from my journal, check the unchanged registry, and run `make check` and `make test-unit`. Inspect the diff for accidental changes to prompts or unrelated expected failures.

### Inputs & outputs

The input is a template name such as `skills_feedback`, a version such as `v1`, and the raw string returned by `get_template()`. Exact text at every recorded version should pass. Different text under the same pair should fail the corresponding test. A new pair should pass once its own digest is recorded and the earlier pairs still match.

### Risks & unknowns

An expected digest computed from the live registry during the test would repeat the original mistake. I plan to record the baseline values as literals in the test and calculate only the actual values at runtime. Regenerating an old digest could also hide a prompt edit, so an intentional change should add a version and a snapshot. Stripping whitespace or formatting the prompt with a real portfolio would change the comparison. I'll hash the raw lookup result and include a whitespace-only edit in verification.

### Edge cases

- Replace “with specific examples” with “without specific examples” in `skills_feedback/v1`. The test for that version should fail even though its placeholders still match.
- Append one newline to `first_impression/v1`. The extra byte should change that snapshot.
- Add `skills_feedback/v2` while preserving `v1`. The new key should need its own expectation. With both snapshots recorded, both versions should pass.
- Remove a recorded version from the registry. The version inventory should identify the missing pair.
