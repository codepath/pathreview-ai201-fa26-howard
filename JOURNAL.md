# Unit 7 — Issue Selection

**Issue Link:** https://github.com/codepath/pathreview-ai201-fa26-howard/issues/58

**Issue Title:** Bias detector patterns are too narrow to match common phrasings

**Issue Tier:** Tier 1

## Problem Summary

PathReview's bias detector currently uses patterns that are too narrow to recognize certain biased statements when they are phrased differently. This can cause the system to miss language that should be flagged, reducing the effectiveness of its bias detection. The issue focuses on improving the detection patterns in `safety/bias_detector.py` while avoiding false positives. A successful fix would recognize more variations of biased language while ensuring that neutral statements are not incorrectly flagged.

## Why I Selected This Issue

I selected this Tier 1 issue because it has a clear scope and connects to my interest in responsible AI. The issue identifies the affected code and provides existing tests that can help verify the changes. I believe this is a manageable issue because I can focus on improving specific detection patterns without changing the overall application architecture. It also provides an opportunity to strengthen my understanding of testing, debugging, and building more reliable AI-related systems.

## Working Branch

`fix/58-bias-detector-patterns`

## Setup and Issue Claim Checklist

- [x] Selected a Tier 1 issue
- [x] Claimed Issue #58 on GitHub
- [x] Added Issue #58 to the Howard cohort ledger
- [x] Created my working branch
- [x] Completed the project setup
- [x] Successfully launched PathReview at localhost:5173
- [x] Committed and pushed `JOURNAL.md` to GitHub
---

## Unit 8 — Reproduction & solution planning

**Reproduction commit link:** https://github.com/jjoiles/pathreview-ai201-fa26-howard/commit/0c85268

**Reproduction summary:**
I reproduced the existing bias detector test results by running `.venv/bin/python -m pytest tests/unit/test_bias_detector.py -v` in my Codespace. The suite reported 23 passing tests and 9 expected failures (XFAIL), documenting known cases where the detector does not yet meet the expected behavior.

**PLAN.md link:** https://github.com/jjoiles/pathreview-ai201-fa26-howard/blob/fix/58-bias-detector-patterns/PLAN.md

**Walkthrough video (recommended):** Not recorded; optional and not graded.

**Blockers or open questions:**
I need to inspect the existing matching patterns and expected-failure cases to determine which rules require changes without introducing false positives.


---

## Unit 9 — Solution building & PR submission

### Check-in 1 (mid-week)

**Current progress:**
I reviewed the nine expected-failure tests for Issue #58 and implemented additional patterns in `safety/bias_detector.py` to recognize common alternative phrasings of educational-background and demographic assumptions. I removed the nine obsolete issue-specific xfail markers and added eleven focused test cases in `tests/unit/test_bias_detector.py`, including neutral examples that should not be flagged.

**Next steps:**
Run the focused tests, `make check`, and `make test-unit`; correct any errors, request peer or mentor feedback on a draft PR, and verify all five GitHub CI jobs before marking the PR ready.

**Blockers:**
Full local test and CI verification is pending.

---

### Check-in 2 (end of week)
### Check-in 2 (end of week)

**PR link:** https://github.com/codepath/pathreview-ai201-fa26-howard/pull/92

**Branch:** `fix/58-bias-detector-patterns`

**What you built:** I expanded the bias detector's regex patterns to identify common biased statements about educational backgrounds, bootcamp graduates, self-taught developers, and demographic assumptions. I also updated the existing tests and removed the strict expected-failure markers associated with Issue #58.

**Tests added or updated:** I updated `tests/unit/test_bias_detector.py` to remove the strict expected-failure markers associated with Issue #58 and added 11 additional test cases covering biased and neutral feedback. All 43 bias detector tests passed. I also ran `make test-unit`, which completed with 395 passed and 44 expected failures. I verified the code quality using `make check`, and all five GitHub CI checks passed.

**Self-review confirmation:**
- [x] `make check` passes
- [x] `make test-unit` passes
- [x] All five GitHub CI checks passed

**Draft PR feedback received from:** I requested feedback from a peer who reviewed my work and confirmed that they had no concerns or additional changes to suggest.

## Unit 10 — Iteration & reflection

### Reviewer feedback

**Feedback received:** [x] Yes — peer feedback  [ ] No — still awaiting review

**Summary of feedback:**

I requested feedback from a peer after submitting my pull request for Issue #58. My peer indicated that they were satisfied with my work and did not suggest any additional changes. At the time of writing, I have not received any further feedback from the repository maintainers.

**How you responded:**

Since my peer did not identify any issues requiring changes, I did not make additional code modifications based on their feedback. I documented the feedback in my journal and verified that all five GitHub CI checks were passing after my final updates. I will remain open to making changes if the maintainers provide additional suggestions.

---

### Reflection

**What was harder than you expected?**

One of the hardest parts of this module was understanding how to work within an existing repository instead of starting a project from scratch. At first, I had to figure out the repository structure, how to use GitHub Codespaces, and which files were relevant to my issue. I also found it challenging to understand the purpose of the existing tests, especially those marked as expected failures. While working on Issue #58, I learned that fixing the code alone was not enough. I also needed to update the tests, remove the expected-failure markers for the corrected behavior, and make sure the changes did not affect other parts of the project.

**What did you learn about working in a large codebase?**

This experience taught me the importance of understanding existing code before making changes. When building my own projects, I usually have a clearer understanding of how everything is organized because I helped create it. However, contributing to PathReview required me to follow someone else's structure, naming conventions, and testing procedures. I learned how important it is to make focused changes instead of modifying unrelated files. I also gained a better understanding of how automated testing, code quality checks, and pull requests help developers collaborate without disrupting the rest of a project.

**How did AI tools help — and where did they fall short?**

AI tools were especially helpful when I needed to understand unfamiliar code, interpret assignment requirements, and work through GitHub commands. They helped me identify the files related to Issue #58, understand how regex patterns were being used in the bias detector, and organize the steps needed to implement and test the fix. AI assistance also helped me understand terminal output and prepare my documentation. However, I learned that AI suggestions still need to be verified. I had to rely on the actual test results, GitHub CI checks, and repository requirements to confirm that my changes worked. This showed me that AI can support the development process, but it cannot replace testing and developer judgment.

**What would you do differently if you started over?**

If I were starting this module again, I would spend more time exploring the repository and understanding the existing tests before beginning implementation. I would also create a clearer checklist of the requirements for each unit so I could track my progress more easily. Another improvement would be to request peer feedback earlier rather than waiting until the pull request was nearly finished. Overall, I would approach the contribution process with more planning and a stronger understanding of the development workflow from the beginning.

**What are you most proud of from this module?**

I am most proud of successfully contributing a fix to an existing open-source project. At the beginning of this module, I was still learning how to navigate the repository and complete the contribution workflow. By the end, I had worked on Issue #58, expanded the bias detector's patterns, updated the tests, and submitted pull request #92. Seeing all 395 passing unit tests and all five GitHub CI checks turn green was rewarding because it provided evidence that my changes worked. More importantly, I gained confidence in my ability to understand an unfamiliar codebase, contribute to an existing project, and follow a professional software development workflow.