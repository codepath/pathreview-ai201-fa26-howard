# PLAN

## Solution plan

**Issue:** [#56 — Structural chunker silently drops documents that contain no headings](https://github.com/codepath/pathreview-ai201-fa26-howard/issues/56)

### Understand

**Root cause:** `StructuralChunker._extract_sections()` in `ingestion/chunking/structural_chunker.py` only collects a content line once it has seen a heading. Line 120 has the check `if heading_stack or current_section_lines:`, and a section is only saved `if heading_stack`. A document with no `#` headings never fills `heading_stack`, so `_extract_sections()` returns `[]` and `chunk()` returns `[]`. The same logic also drops any text that comes *before* the first heading. The variable `current_level` is assigned but never read (`# noqa: F841`); it was meant to carry the "no heading yet" level (0).

**Expected:** Any non-empty document produces at least one chunk. A heading-less document becomes one section. If it's over `SECTION_TOKEN_LIMIT` (800 tokens), it is sub-chunked by `SemanticChunker`, the same way large headed sections already are.

**Actual:** A heading-less README returns 0 chunks, with no error and no log. That makes it invisible to RAG retrieval. Reproduced in commit `b45151b`.

### Map

| File | Role | Change? |
|---|---|---|
| `ingestion/chunking/structural_chunker.py` | `_extract_sections()` holds the bug; `chunk()` consumes sections | **Yes**, the fix |
| `tests/unit/test_structural_chunker.py` | 3 `xfail(strict=True)` tests for #56 | **Yes**, remove the 3 markers and add an intro-text test |
| `ingestion/chunking/strategy_selector.py` | Routes `source_type == "readme"` to this chunker (only caller) | No, read only |
| `ingestion/chunking/semantic_chunker.py` | Sub-chunks sections over 800 tokens | No, reused as is |
| `docs/adr/001-chunking-strategy.md` | Explains why READMEs use the structural chunker | No, the behavior still matches the ADR |

### Plan

1. **Collect text before the first heading.** In `_extract_sections()`, drop the "only collect if we have a heading" condition so every non-heading line is collected.
2. **Save the intro section.** When the first heading is reached (and at end of input), save collected lines even when `heading_stack` is empty, as a section with `path: []` and `level: current_level` (0). This puts the existing `current_level` variable to use, so the `# noqa: F841` and the "seeded defect" comment can be removed.
3. **Skip empty sections.** Don't save a section whose content is empty after `.strip()`. Blank lines before the first heading shouldn't create blank chunks, and `test_chunks_have_text_content` must keep passing.
4. **Remove the xfail markers** from `test_document_with_no_headings`, `test_large_document_with_no_headings_is_sub_chunked`, and `test_readme_with_no_headings_through_strategy_selector`. Add `test_text_before_first_heading_is_kept`.
5. **Verify:** run `make check && make test-unit` and the reproduction snippet from JOURNAL.md, then open the PR with `Fixes #56`.

### Inputs & outputs

- **Input:** `chunk(text: str, metadata: dict)`, the raw README text plus document metadata (`source_type`, `source`, etc.).
- **Output:** `list[Chunk]`. For heading-less text, at least one `Chunk` whose metadata keeps all the caller's keys plus `heading_path: ""` and `heading_level: 0`. Documents that have headings produce the same chunks as before, plus one extra level-0 chunk if they have text before the first heading.

### Risks & unknowns

- **Is the intro text in scope?** The issue only names fully heading-less documents. The intro case comes from the same lines of code, so fixing one without the other would be odd, but it does change output for some documents that have headings. Ask a maintainer, or call it out clearly in the PR.
- **`heading_path` for heading-less chunks:** I plan to use an empty string `""`, which is what `" > ".join([])` already gives. Another option is to leave the key out. Nothing outside the chunker reads `heading_path` or `heading_level` today (checked with grep), so the risk is low either way.
- **`heading_level` 0:** `test_chunk_metadata_includes_heading_level` asserts levels are in `[1, 2, 3]`. Its fixture has no intro text, so it should still pass, but I'll confirm.
- **Pre-commit black version:** the pre-commit hook pins black 24.1.0, while CI installs the latest black. The two disagree on an existing test in this file, so I'll format with `.venv/bin/black` to match CI.

### Edge cases

- Empty or whitespace-only text → still `[]` (existing tests).
- A heading-less document under 800 tokens → exactly one chunk.
- A heading-less document over 800 tokens → several semantic sub-chunks, none of them empty.
- Text before the first heading followed by headings → an intro chunk plus the normal heading chunks.
- Blank lines before the first heading → no empty intro chunk.
- A document that is only headings with no body → no crash, and no empty chunks (`test_empty_sections_handled`).
- Text with `#` but no space, like `#hashtag` → still treated as content, not a heading (the regex requires `\s+`).
