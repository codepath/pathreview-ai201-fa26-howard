## Unit 7 — Issue selection

**Issue link:** https://github.com/codepath/pathreview-ai201-fa26-howard/issues/60

**Issue title:** Faithfulness checker crashes when a context chunk has `text: None`

**Tier:** [Yes] Tier 1  [No] Tier 2  [No] Tier 3

**Problem summary:**
This issue of Pathreview involves the faithfulness checker and how right now it's `check()` method is assuming that every context chunk's text value is a string when it joins retrieved chunks into a signle context. When a context chunk has `text: None`, the dictionary lookup right now is returning `None` which is causing " ".join(...) to raise a TypeError and prevents evalutuion from completing leading to a crash. Instead of `None`, the lookup should be returning the fallback value. A successful fix would handle `None` text values from chunks correctly in faithfulness_checker.py while preserving regular behavior for already valid text. It would also allow test_none_context_chunk_text to pass.

**Branch name:** fix/60-faithfulness-checker-crashes

**Setup confirmation:** [Yes] App runs locally at localhost:5173

**Cohort ledger:** [Yes] Issue added to cohort ledger


## Unit 8 — Reproduction & solution planning

**Note: steps to reproduce the bug issue**:

1. Install dependenicies with `.venv\Scripts\python.exe -m pip install -e ".[dev]"`.
2. Reproduce the bug with `.venv\Scripts\python.exe -c "from rag.evaluator.faithfulness_checker import FaithfulnessChecker; FaithfulnessChecker().check('Knows Python.', [{'text': None}])"`.
3. After that gets run, the type error message will get returned: `TypeError: sequence item 0: expected str instance, NoneType found`.
4. Run the dedicated test for this issue from the unittest folder: `.venv\Scripts\python.exe -m pytest tests/unit/test_faithfulness_checker.py::TestFaithfulnessChecker::test_none_context_chunk_text -q`. This test will return `xfailed` becuase the test is marked as expected to fail.

**Reproduction commit link:** https://github.com/ChrisReid27/pathreview-ai201-fa26-howard/commit/981e604fbff4bf762898c370b326853c86484ed0

**Reproduction summary:**
I reproduced the bug by calling `FaithfulnessChecker().check("Knows Python.", [{"text": None}])` and running the designated faithfulness checker test within the unittest folder (which had an expected fail). What I observed is that because the checker passes `None` to `" ".join(...)`, it crashes with `TypeError: sequence item 0: expected str instance, NoneType found`.

**PLAN.md link:** https://github.com/ChrisReid27/pathreview-ai201-fa26-howard/commit/875cf371e5c62d2be455720a1b93595c29ee5805

**Walkthrough video (recommended):** [link to your Loom video, ≤2 min — recommended, not graded]

**Blockers or open questions:**
Based on my edge cases from Plan.md, going into unit 9, there is the concern of how missing or empty `text` values should be treated, and whether mixed valid and invalid chunks should still get scored normally. Also, I need to make sure that ignoring the `None` chunks won't produce any misleading faithfulness scores when they are the only or most significant context available.


## Unit 9 — Solution building & PR submission

### Check-in 1 (mid-week)

**Current progress:**
I've implemented the fix for the faithfulness checker issue. Subtasks 1-4 are finished and everything looks good. I made sure my changes didn't affect the rest of the codebase.

**Next steps:**
Getting ready to open the PR in the correct format and edit my commit history titles to be in proper contributing format.

**Blockers:**
Nothing is slowing me down, I'm on track with fixing the issue.

---

### Check-in 2 (end of week)

**PR link:** https://github.com/codepath/pathreview-ai201-fa26-howard/pull/97#issue-6461316861

**Branch:** `fix/60-faithfulness-checker-crashes`

**What you built:**
I updated `FaithfulnessChecker.check()` to safely normalize missing or `None` context text to an empty string before joining chunks. This prevents a `TypeError` while preserving normal scoring for valid text and mixed valid/invalid chunks.

**Tests added or updated:**
I updated `tests/unit/test_faithfulness_checker.py` with edge case coverage for `None` text, missing text keys, mixed valid and invalid chunks, empty text, and contexts containing only `None` values.

**Self-review confirmation:** [X] make check passes  [X] make test-unit passes

**Draft PR feedback received from:** none

## Unit 10 — Iteration & reflection

### Reviewer feedback

**Feedback received:** [ ] Yes  [X] No — still awaiting review

**Summary of feedback:**
No review came in.

**How you responded:**


---

### Reflection

**What was harder than you expected?**
The edge cases were harder than the original fix. It was easy to change the join so that `None` no longer caused a crash, but I also had to think through missing keys, empty strings, mixed valid and invalid chunks, and contexts containing only invalid values without changing the behavior for normal text.

**What did you learn about working in a large codebase?**
I learned that a small change still requires understanding the surrounding tests, conventions, and expected behavior before editing the code. In someone else's production code, preserving existing behavior is just as important as fixing the reported failure, so the focused tests and full unit checks helped me confirm that the changes I made stayed in their own lane and didn't cause any unwanted ripple effects.

**How did AI tools help — and where did they fall short?**
I used Copilot to help me locate the relevant checker and test for my issue, and had it explain why `dict.get("text", "")` still returns `None` when the key exists, and identify useful edge cases to test. They helped with suggesting implementation but I had to be careful prompting becuase they wouould often want to go beyond the scope of my fix and alter other parts of the codebase.

**What would you do differently if you started over?**
I would define the expected behavior for missing and `None` text values earlier in the planning stage and write the edge-case tests before implementing the fix. That would make the intended behavior clearer from the beginning and reduce uncertainty about how contexts with no usable text should be handled.

**What are you most proud of from this module?**
I'm less so proud about the fix becuase it didn't take much but the process of doing a PR properly was new and making sure I followed the contributing guidelines. Just that I learned industry norms to keep people's projects/codebase's neat and organized.