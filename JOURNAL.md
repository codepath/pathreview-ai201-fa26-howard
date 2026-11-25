## Unit 7 — Issue selection

**Issue link:** [#20](https://github.com/codepath/pathreview-ai201-fa26-howard/issues/20)

**Issue title:** Implement a DependencyAuditTool that flags outdated major dependencies in project repos

**Tier:** [ ] Tier 1  [X] Tier 2  [ ] Tier 3

**Issue fit:**
I chose Tier 2 because I’m comfortable writing Python, and working extensively with agents during my summer internship gave me the confidence to take on the orchestrator changes. I can use the existing tool interface and follow how `agent/orchestrator.py` schedules the technology detector when repository files are available. The scope is manageable because I can focus on reading three known file formats, flagging dependencies more than one major version behind, and testing when the orchestrator calls the tool.

**Problem summary:**
When dependencies are several major versions behind, they can cause failures or leave the system vulnerable. The system needs a tool to flag outdated dependencies, including versions that may be deprecated or unsupported. The fix would be to add a dependency audit tool that reads files such as `requirements.txt`, `package.json`, and `pyproject.toml` and flags dependencies that are behind on major releases. The tool description in `agent/orchestrator.py` also needs to explain how and when the orchestrator agent should use it.

**Branch name:** feat/20-dependency-audit-tool

**Setup confirmation:** [X] App runs locally at localhost:5173

**Cohort ledger:** [X] Issue added to cohort ledger

## Unit 8 — Reproduction & solution planning

**Reproduction commit link:** [01ee826 — document dependency audit gap reproduction](https://github.com/NickHibram/pathreview-ai201-fa26-howard/commit/01ee8267e5411694b8eb04529e869d96c223722a)

**Reproduction summary:**
I ran the orchestrator locally with PathReview’s own manifests and checked the frontend lockfile, which uses Vite 5.4.21 and Vitest 1.6.1 while their current major releases are 8 and 5. Both dependencies should be flagged under issue #20, but `agent/orchestrator.py` only schedules technology detection and market analysis for these inputs, so the output identifies JavaScript and Node.js without reporting either outdated dependency.

**Reproduction steps:** Run this from the repo root after local setup.

```bash
.venv/bin/python - <<'PY'
import json
from pathlib import Path

from agent.orchestrator import Orchestrator
from agent.tools.market_analyzer import MarketAnalyzer
from agent.tools.tech_detector import TechDetector

lock = json.loads(Path("frontend/package-lock.json").read_text())["packages"]
for name in ("vite", "vitest"):
    print(name, lock[f"node_modules/{name}"]["version"])

tools = (TechDetector(), MarketAnalyzer())
orchestrator = Orchestrator({tool.name: tool for tool in tools})
files = ["pyproject.toml", "frontend/package.json", "frontend/package-lock.json"]
result = orchestrator.run("issue-20-repro", {"files": files})
print("Tool results:", sorted(result["tool_results"]))
print("Technology detection:", result["tool_results"]["tech_detector"])
PY
```

**PLAN.md link:** [PLAN.md](https://github.com/NickHibram/pathreview-ai201-fa26-howard/blob/feat/20-dependency-audit-tool/PLAN.md)

**Blockers or open questions:**

## Unit 9 — Solution building & PR submission

### Check-in 1 (mid-week)

**Current progress:**
I completed steps 1–3 in `PLAN.md`. I reproduced the missed Vite and Vitest findings in a unit test, added parsing and version comparison for `package.json`, `requirements.txt`, and `pyproject.toml`, and added GitHub retrieval for manifests on the default branch, including nested files. The unit suite passed after the retrieval changes with 388 passing tests and 53 expected failures.

**Next steps:**
I’ll finish steps 4–5 by wiring the audit into the orchestrator, testing both supplied manifests and submitted GitHub repositories, and rerunning the Vite and Vitest reproduction. Then I’ll run the project checks and submit the PR.

**Blockers:**
None. The first unit run was blocked by a tokenizer download, which I resolved by caching the tokenizer data locally.

---

### Check-in 2 (end of week)

**PR link:** [PathReview PR #108 — Dependency audit tool](https://github.com/codepath/pathreview-ai201-fa26-howard/pull/108)

**Branch:** `feat/20-dependency-audit-tool`

**What you built:**
I built a dependency audit tool that reads npm and Python manifests supplied directly or fetched from a submitted GitHub repository. It compares the highest major version allowed by each declaration with the current stable release and flags gaps of two or more majors. The orchestrator returns the findings and warns about any files or dependencies the audit could not check.

**Tests added or updated:**
- `tests/unit/test_dependency_audit_tool.py` covers all three manifest formats, version boundaries, malformed inputs, and registry failures and limits.
- `tests/unit/test_github_tool.py` covers nested manifest retrieval, skipped vendor files, and partial GitHub failures.
- `tests/unit/test_orchestrator.py` covers both input paths, fresh results across runs, and the Vite and Vitest reproduction. The final unit run had 401 passes and 53 expected failures.

**Self-review confirmation**

- [x] `make check` passes
- [x] `make test-unit` passes

**Draft PR feedback received from:** none

## Unit 10 — Iteration & reflection

### Reviewer feedback

**Feedback received:** [ ] Yes  [X] No — still awaiting review

**Summary of feedback:**
I’m still awaiting reviewer feedback on [PR #108](https://github.com/codepath/pathreview-ai201-fa26-howard/pull/108). As of November 25, 2026, the PR has no submitted reviews or discussion comments.

**How you responded:**

---

### Reflection

**What was harder than you expected?**
Figuring out which major versions a declaration actually allows took more work than I expected. For example, `redis>=5` can allow major 8, while `<6,!=5.*` rules out all of major 5. Writing those cases as tests helped me pin down when the tool had enough evidence to flag a dependency.

**What did you learn about working in a large codebase?**
I learned to trace how data reaches an existing feature before deciding where to change it. The technology detector receives filenames, while the dependency audit needs the contents of those files. I had to fit the new tool into the existing orchestrator and GitHub client while preserving how the other tools are selected and run.

**How did AI tools help — and where did they fall short?**
AI helped me trace the agent code, turn the Vite and Vitest reproduction into a test, and review the first implementation. The first pass missed some Python exclusions and could lose valid findings when a neighboring manifest was malformed. A second review surfaced those cases, and running the regression tests before and after the fixes showed whether the changes worked.

**What would you do differently if you started over?**
I’d write down a small table of version ranges and expected findings before implementing the parser. I’d also include a malformed manifest and a failed lookup in the first test cases so I could verify early that the tool still returns findings from the other dependencies.

**What are you most proud of from this module?**
I’m most proud of turning a missing warning into a repeatable regression test using PathReview’s own frontend manifest. With fixed registry responses, the test shows the orchestrator reporting both Vite and Vitest with the expected gaps of three and four major versions.
