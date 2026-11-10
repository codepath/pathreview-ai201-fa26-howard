# JOURNAL

## Unit 7 — Issue selection

**Issue link:** https://github.com/codepath/pathreview-ai201-fa26-howard/issues/56

**Issue title:** Structural chunker silently drops documents that contain no headings

**Tier:** [x] Tier 1  [ ] Tier 2  [ ] Tier 3

**Problem summary:**
The ingestion pipeline's structural chunker (`ingestion/chunking/structural_chunker.py`) splits markdown into chunks at heading boundaries before they are embedded into the RAG index. In `_extract_sections()`, content lines are only collected after a heading has been seen. A document with no `#` headings, like a plain-text resume or a bare README, produces no sections, and `chunk()` returns an empty list. Nothing is logged and no error is raised, so the whole document silently goes missing from retrieval, and reviews can't draw on it. A successful fix makes heading-less documents produce at least one chunk, either as a single block or by falling back to the semantic chunker when they're too large. The fix should also remove the `xfail` marker on `test_document_with_no_headings` in `tests/unit/test_structural_chunker.py` so it runs as a normal passing test.

**Branch name:** `fix/56-chunker-no-headings`

**Setup confirmation:** [x] App runs locally at localhost:5173

**Cohort ledger:** [x] Issue added to cohort ledger

### Selection notes ("Is this right for me?")

- **Scope fits:** The bug is in one method of one file, and one existing test confirms the fix. I don't need to change the API, database, or frontend.
- **Reproducible:** Running `StructuralChunker().chunk("This is a plain document with no headings at all. " * 20, {})` locally returns `0` chunks. The covering test is marked `xfail(strict=True)` for issue #56.
- **Tier match:** This is my first contribution to a large codebase, so I started with Tier 1. It's small, but I still have to understand how sections and the semantic sub-chunking fallback fit together, and I'll practice the whole workflow: branch, conventional commits, green CI, and a PR.
- **Not taken:** I first chose #60, but it was already claimed in the cohort ledger. No one had commented on #56 or added it to the ledger when I switched.
- **Something to watch:** Text that comes *before* the first heading in a document is dropped by the same logic. I'll check whether my fix should cover that case too, or whether it's out of scope for this issue.

## Unit 8 — Reproduction & solution planning

**Reproduction commit link:** https://github.com/kingkd22/pathreview-ai201-fa26-howard/commit/b45151b8a4c47e8f4fa1c3e4a44cf8dde6bb18ce

**Reproduction summary:**
I passed a plain README with no `#` headings through `StrategySelector` with `source_type: "readme"`, which is the real ingestion path. It returned 0 chunks. The same text with `source_type: "resume"` returned 1 chunk, and a heading-less README of about 2,400 tokens also returned 0. I committed two new `xfail(strict=True)` tests covering these cases next to the existing one. With `--runxfail`, all three fail with `assert 0 >= 1` / `assert 0 > 1`.

**PLAN.md link:** https://github.com/kingkd22/pathreview-ai201-fa26-howard/blob/fix/56-chunker-no-headings/PLAN.md

**Walkthrough video (recommended):** [link to your Loom video, ≤2 min — recommended, not graded]

**Blockers or open questions:**
- **Correction to Unit 7:** only READMEs go through the structural chunker (resumes use the semantic chunker), so the bug affects heading-less READMEs, not resumes.
- **Intro text before the first heading:** this is also silently dropped (for example, `"Intro...\n\n# Usage\nRun the tool."` keeps only `"Run the tool."`). It comes from the same lines of code, so I plan to fix it too, but I'll confirm with a mentor that this isn't scope creep.
- **Black version mismatch:** the pre-commit hook pins black 24.1.0, but CI installs the latest black, and the two disagree on an existing test in this file. For my commits I'm using the project venv's black, which matches CI.

### Reproduction steps

```bash
.venv/bin/python -c "
from ingestion.chunking.strategy_selector import StrategySelector
text = 'This project is a CLI tool for tracking habits. It is written in Python. ' * 3
print(len(StrategySelector().chunk(text, {'source_type': 'readme'})))  # 0 (expected >= 1)
print(len(StrategySelector().chunk(text, {'source_type': 'resume'})))  # 1
"
.venv/bin/python -m pytest tests/unit/test_structural_chunker.py --runxfail -q  # 3 failed, 14 passed
```
