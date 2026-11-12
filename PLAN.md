## Solution plan

**Issue:** Resume section detection fails on text with leading whitespace: [#54](https://github.com/codepath/pathreview-ai201-fa26-howard/issues/54)

### Understand

**Root cause.** `ResumeParser._detect_sections()` in `ingestion/parsers/resume_parser.py` builds four regexes per header. Every one of them requires the header to be the very first character of a line:

```python
rf"^{re.escape(section)}\s*$",      # start of line
rf"^{re.escape(section)}\s*[:|-]",
rf"\n{re.escape(section)}\s*$",     # right after a newline
rf"\n{re.escape(section)}\s*[:|-]",
```

So `"Experience:"` matches, but `"    Experience:"` doesn't. Text that `pypdf` extracts from real resumes (and the triple-quoted fixtures in our tests) usually keeps that indentation, so `detected_sections` comes back empty.

**Second instance of the same bug (not in the issue title).** `_strip_markdown()` removes markdown headers with `re.sub(r"^#+\s+", "", content, flags=re.MULTILINE)`, which has the same column-0 anchor. An indented `# Header` is left in the text. That's why `test_strip_markdown_syntax` and `test_parse_markdown_resume` are also tagged with issue #54, even though neither one calls `_detect_sections` directly.

**Expected vs. actual** (reproduced locally, commit `b06d132`):

| Input | Expected | Actual |
|---|---|---|
| `"Experience:\nEducation:\nSkills: Python"` | `['Education', 'Experience', 'Skills']` | ✅ same |
| same text, every line indented 4 spaces | `['Education', 'Experience', 'Skills']` | ❌ `[]` |
| `"    # Header\n    ## Skills"` through `_strip_markdown` | `"Header\nSkills"` | ❌ `"# Header\n    ## Skills"` |

Running `pytest tests/unit/test_resume_parser.py --runxfail` shows all 5 existing #54 tests failing.

### Map

**Files I'll change:**
- `ingestion/parsers/resume_parser.py`
  - `_detect_sections()`: the four header patterns
  - `_strip_markdown()`: the header-removal regex
- `tests/unit/test_resume_parser.py`
  - remove `@pytest.mark.xfail(strict=True, reason="issue #54: …")` from the 6 tests that cover the issue (5 existing + my reproduction test `test_detect_sections_indented_matches_flush`)
  - add edge-case tests (see below)

**Files I'm reading but not changing:**
- `ingestion/pipeline.py`: `IngestionPipeline` calls `self.resume_parser.parse()`, logs `detected_sections`, and copies the parser metadata into what gets stored. This is the downstream consumer, so the shape of `detected_sections` (a list of title-cased strings) must not change.
- `tests/conftest.py`: the `sample_resume_text` fixture is indented 4 spaces, which is why `test_parse_single_column_resume_text` fails.
- `pyproject.toml`: to check whether a ruff/mypy suppression names #54 and needs removing (per CONTRIBUTING.md).

### Plan

1. **Fix `_detect_sections()`.** Allow optional leading horizontal whitespace before the header: change `^` / `\n` to `^[^\S\n]*`, meaning "any whitespace except a newline". With `re.MULTILINE`, the `^` form already covers the `\n` form, so I'll collapse the four patterns into two. That removes duplication without changing what matches.
2. **Fix `_strip_markdown()`.** Change the header regex to `^[^\S\n]*#+\s+` so indented markdown headers are stripped too.
3. **Remove the xfail markers.** Delete `@pytest.mark.xfail` from all 6 #54 tests. They're `strict=True`, so if I miss one, CI fails with `XPASS(strict)`. Check `pyproject.toml` for any #54 suppression.
4. **Add edge-case tests** for the cases in "Edge cases" below, especially the ones that could break if the regex is loosened too far.
5. **Run every CI check locally** (`make check`, `make test-unit`, `make test-integration` if Postgres is available, and `cd frontend && npm test -- --run`), then push and open the PR using the template.

### Inputs & outputs

- **`_detect_sections(text: str) -> list[str]`**: same signature. Input is the full resume text after PDF extraction or markdown stripping. Output is still a de-duplicated list of title-cased header names (e.g. `["Education", "Experience", "Skills"]`). **Behavior change:** headers preceded by spaces, tabs, or other non-newline whitespace are now detected, so indented and flush-left text produce the same list.
- **`_strip_markdown(content: str) -> str`**: same signature. **Behavior change:** indented `#`-style headers are stripped like flush ones.
- **`parse()` / `ParseResult.metadata["detected_sections"]`**: no signature change. For indented resumes the value goes from `[]` to the real sections, and that flows through `IngestionPipeline` into stored metadata.

### Risks & unknowns

- **False positives from loosening the anchor (`_detect_sections`).** Allowing leading whitespace must not let a header word in the middle of a sentence match. The patterns still require only whitespace between the line start and the word, and then end-of-line or `:`/`|`/`-`. A test will pin this down: `"I have experience: 5 years"` must not count as a header.
- **Using `\s*` instead of `[^\S\n]*`.** `\s` includes `\n`, so `^\s*#+` in `_strip_markdown` could match across blank lines and delete them, which changes the text the chunker sees. I'll use `[^\S\n]*` in both places and test that blank lines between sections survive.
- **Non-ASCII whitespace from PDFs.** `pypdf` can emit non-breaking spaces (`\xa0`) or tabs. `[^\S\n]` covers both in Python's Unicode regex mode, but I want a test to confirm it rather than assume.
- **Existing false positive I'm not fixing.** `rf"^{section}\s*[:|-]"` already matches `"Experience-driven engineer"`. That's a separate bug from #54, so I'll mention it in the PR's Notes for Reviewers instead of widening this PR.
- **CI jobs I can't fully run locally.** `test-integration` needs Postgres and Redis (see `.github/workflows/ci.yml`). Since my change is limited to one parser, I expect it to stay green, but I'll confirm on the PR's CI run. My first fork PR may also need a maintainer to approve running workflows.

### Edge cases

1. **Tab indentation:** `"\tEducation:"` → `Education` detected.
2. **Mixed indentation in one document:** some headers flush, some indented 2, 4, or 8 spaces → all detected, same as all-flush.
3. **Header word in the middle of a line:** `"I have experience: 5 years"` and `"    my skills include Python"` → **not** detected.
4. **Non-breaking-space indentation from PDF extraction:** `"\xa0\xa0Skills: Python"` → `Skills` detected.
5. **Indented markdown headers with blank lines between them:** `"    # Jane\n\n    ## Skills"` → both `#` markers stripped, and the blank line is preserved.
6. **Multi-word headers indented:** `"    Work Experience"` → `Work Experience` detected (the space inside the header must still match).
7. **No sections at all** (e.g. `"John Doe\nSoftware Engineer"`) → `[]`, no crash.
