# Solution plan

**Issue:** [GitHub Issue #57 — Tech detector counts vendored and build-output files, skewing language detection](https://github.com/codepath/pathreview-ai201-fa26-howard/issues/57)
**Tier:** 1
**Branch:** `fix/57-tech-detector-exclude-generated`
**Reproduction evidence:** [93568a5b474064b0dbc66cf6050a5987433fc8d1](https://github.com/blayne-montaque/pathreview-ai201-fa26-howard/commit/93568a5b474064b0dbc66cf6050a5987433fc8d1)
**Status:** Unit 8 plan, recorded November 8, 2026. Implementation is deferred to Unit 9.

### Understand

The issue's exact input contains two Python source paths and six JavaScript paths under root-level `node_modules/` and `build/`. The executed, unfixed detector returns:

```json
{"primary_language": "JavaScript", "all_languages": ["JavaScript", "Python"], "frameworks": []}
```

The intended result is:

```json
{"primary_language": "Python", "all_languages": ["Python"], "frameworks": []}
```

`TechDetector._should_skip_file()` searches for substrings such as `"/node_modules/"` and `"/build/"`. Root-relative paths have no leading slash, so they survive filtering. Nested paths such as `frontend/node_modules/lib/index.js` do match and are already excluded. The same defect lets root-level excluded directories contribute configuration indicators: the executed `main.py` plus `node_modules/lib/package.json` and `build/package.json` case adds JavaScript and Node.js.

`_detect_tech()` already filters once before both extension and configuration detection. The correction belongs in directory matching, preserving that shared filter. Languages are stored in a set; the primary is the first alphabetically sorted language. The issue's file counts describe its example but are not the selection algorithm. Do not introduce frequency ranking as part of this fix.

The two supplied regression tests currently report **2 XFAIL**; running those same tests with `--runxfail` exposes **2 assertion failures**, each comparing actual JavaScript with expected Python. A successful future fix must exclude exact vendor/generated directory components at every depth, preserve legitimate source/configuration paths, return the existing result schema, and make those assertions pass.

### Map

| File / symbol | Role and planned treatment |
| --- | --- |
| `agent/tools/tech_detector.py::TechDetector._should_skip_file` | Primary change site: replace the leading-slash-dependent substring condition with exact directory-component matching. Keep the existing eight excluded names. |
| `agent/tools/tech_detector.py::TechDetector._detect_tech` | Verify that the common filtered list continues to govern extension and configuration detection. Preserve language/framework sorting and primary-language policy; no redesign is planned. |
| `agent/tools/tech_detector.py::TechDetector.execute` | Public input/output boundary: preserve `ToolResult`, success/error handling, and missing/empty input behavior. Test through this boundary. |
| `tests/unit/test_tech_detector.py::TestTechDetector` | Extend `test_node_modules_excluded` and `test_build_directory_excluded`; add focused root/nested, configuration, all-excluded, and false-positive assertions. `test_vendor_files_excluded` currently has no assertion, so strengthen it for the same exclusion policy rather than treating its PASS as evidence. |
| `agent/orchestrator.py::Orchestrator._build_plan` | Inspected caller: passes `profile_data["files"]` directly to the detector. Read-only contract reference; no planned orchestrator change. |
| `agent/tools/base.py::ToolResult` | Inspected response contract (`success`, `data`, optional `error`). Read-only reference; no schema changes. |

No dependency, API, frontend, database, or LLM change is needed for the verified POSIX-path defect.

### Plan

1. **Correct the directory boundary check.** In `_should_skip_file()`, compare directory components before the final filename against the existing names `node_modules`, `vendor`, `dist`, `build`, `.git`, `__pycache__`, `.venv`, and `venv`. Apply the same rule to the first directory and every nested directory. Use lexical POSIX component matching for the verified input contract, without filesystem access, case folding, or resolving `..`. Do not use loose substrings or host-dependent path parsing. Clarify the helper's documented interpretation. Backslash support is conditional on the contract decision described below.
2. **Make exclusion tests prove the whole result.** Extend the two issue tests to assert `success`, `primary_language`, `all_languages`, and `frameworks`. Add parametrized root/nested cases across the existing exclusion names, plus the issue's complete eight-path example. Add excluded configuration-file cases and all-excluded input; assert no JavaScript or Node.js leakage and the existing Unknown/empty-list result when nothing remains.
3. **Protect eligible paths and existing detection behavior.** Add assertions for similar directory names, a filename such as `build.py`, genuine mixed-language source, and root-level `package.json`/`requirements.txt`. Keep existing sorted outputs, empty-input behavior, and the alphabetic primary-language policy. Strengthen the assertion-free vendor test within this scope. Do not modify other weak tests or unrelated seeded bugs.
4. **Retire only the two obsolete #57 markers after proof.** Run the two original assertions with `--runxfail` to establish that the implemented fix passes, then remove only their two `xfail(strict=True)` decorators. Keep every unrelated expected-failure marker and suppression. A normal test run with the markers still present should report strict XPASS once fixed; it is not an excuse to weaken assertions.
5. **Validate the focused change and record actual results.** Rerun the journal's exact reproduction and confirm the desired dictionary, then run the commands below and inspect `git diff --check` and the complete source/test diff. Expected changes are confined to the detector and its tests, plus required later journal updates. Record any baseline limitation separately; do not repair unrelated failures.

Planned Unit 9 validation from the repository root in Git Bash (these are future acceptance checks, not a claim that a fix has run):

```bash
# Before removing the markers, prove both original assertions pass:
.venv/Scripts/python -m pytest \
  tests/unit/test_tech_detector.py::TestTechDetector::test_node_modules_excluded \
  tests/unit/test_tech_detector.py::TestTechDetector::test_build_directory_excluded \
  --runxfail -v

# After removing only #57's two obsolete markers:
.venv/Scripts/python -m pytest tests/unit/test_tech_detector.py -v
make lint
.venv/Scripts/black --check .
make typecheck
make test-unit
git diff --check
```

Use the relocated `../.pathreview-setup/project-command.sh` wrapper if GNU Make is absent from the shell's PATH. The non-writing Black check covers formatting without modifying unrelated files. Run broader frontend/integration/CI checks at the later Unit 9 submission stage as required by the contribution guide, disclosing the existing baseline limitations rather than treating them as #57 work.

### Inputs & outputs

Input is a dictionary containing `files: list[str]` of repository file paths. The issue, existing tests, and executed examples establish repository-relative POSIX strings. `Orchestrator._build_plan()` forwards them unchanged. No files need to exist on disk; the tool analyzes names only. Missing or empty `files` currently returns a successful Unknown result and must remain so.

Under the scoped fix, a path is excluded if any **directory** component exactly equals an existing excluded name. The final filename is not a directory component. Root and nested exclusions use the same policy; ordinary paths and similarly named directories remain eligible. Do not add new directories to the exclusion policy, convert extension case, mutate the caller's list, or change configuration suffix matching.

Exact issue input:

```python
[
    "main.py",
    "core/app.py",
    "node_modules/lib/index.js",
    "node_modules/lib/util.js",
    "node_modules/x/a.js",
    "node_modules/y/b.js",
    "build/bundle.js",
    "build/vendor.js",
]
```

Only `main.py` and `core/app.py` should contribute. Current output is JavaScript with languages `["JavaScript", "Python"]`; desired output is Python with languages `["Python"]`. Both have frameworks `[]`.

The public result remains `ToolResult(success=True, data={...}, error=None)`, with the data keys `primary_language`, `all_languages`, and `frameworks`. The two lists remain sorted and unique. With only excluded files, return `{"primary_language": "Unknown", "all_languages": [], "frameworks": []}`. With legitimate `main.py` and `src/app.js`, preserve both languages and the existing JavaScript primary; this is a control case, not a defect for #57.

### Risks & unknowns

| Status | Risk / question | Response in Unit 9 |
| --- | --- | --- |
| Verified defect | Root paths miss the leading-slash patterns; nested POSIX paths already match. | Test both depths together so the correction does not regress the working nested case. Apply it consistently to the existing exclusion set. |
| Verified control behavior | `build_tools`, `rebuild`, `node_modules_backup`, and `build.py` are currently eligible. | Compare complete directory components, not prefixes/substrings; retain negative controls. |
| Verified defect | Excluded root-level `package.json` adds both JavaScript and Node.js. | Test the full output, not just primary language; keep filtering ahead of both detection passes. |
| Verified behavior to preserve | Primary language is alphabetic, not frequency-based; configuration suffix matching is also independent. | Keep both policies unchanged. Do not expand the fix into ranking, case-insensitivity, or configuration matching. |
| Observed limitation; contract unresolved | Root and nested backslash paths both leak, but no inspected caller guarantees native Windows separators. A POSIX filename may legally contain a literal backslash. | Required acceptance uses the established POSIX contract. Before adding backslash normalization, verify/document that inputs may be Windows-style. If confirmed in Unit 9, normalize separators only for exclusion comparison and test root/nested/mixed separators on any host. Otherwise keep native Windows paths outside this fix and explicitly document that limitation. The current Windows development host alone does not establish that contract. |
| Input assumption | The tool accepts file paths, not directory listings; absolute paths, path traversal normalization, symlinks, malformed input, and case-insensitive directory aliases are unspecified. | Avoid introducing filesystem resolution, traversal interpretation, or validation changes. Preserve existing behavior outside the stated file-path contract. |
| Test reliability | Some existing detector tests contain no assertions. | Add meaningful assertions only for this issue's cases; do not equate the existing green suite with comprehensive detection correctness. |

The separator question is a documented scope decision for implementation, not a blocker to this verified POSIX reproduction or Unit 8 planning deliverables.

### Edge cases

For each applicable execution test, assert the full public result and preserve the input list. These are proposed Unit 9 checks; no new tests have been implemented in Unit 8.

| Case / concrete paths | Intended assertion |
| --- | --- |
| Root `node_modules/`: `main.py`, `node_modules/lib/index.js` | Python only; no JavaScript. |
| Nested `node_modules/`: `main.py`, `frontend/node_modules/lib/index.js` | Same result at nested depth. |
| Root `build/`: `main.py`, `build/bundle.js` | Python only. |
| Nested generated output: `main.py`, `frontend/build/bundle.js`, `packages/site/dist/index.js` | Python only; existing nested exclusion remains intact. |
| Existing exclusion names at both depths: parameterize `vendor`, `dist`, `.git`, `__pycache__`, `.venv`, `venv` in addition to the two issue directories | A JS file under each excluded directory contributes no technology; retained Python determines output. |
| Similar names: `src/build_tools/app.py`, `src/rebuild/app.py`, `node_modules_backup/app.js`, `src/vendorized/app.js` | All remain eligible; mixed Python/JavaScript output is preserved. |
| Filename boundary: `build.py`, `src/build.py` | Eligible Python source; a basename is not a generated directory. |
| All-excluded root and nested inputs | Successful Unknown primary with empty language/framework lists. |
| Exact eight-path issue reproduction | Python only, irrespective of the six excluded JS paths. |
| Genuine mixed source: `main.py`, `src/app.js` | Both languages remain; preserve JavaScript as the current alphabetic primary. |
| Excluded configuration: `main.py` plus root/nested `node_modules/lib/package.json` or `build/package.json` | Python only and no Node.js framework. Include an excluded `requirements.txt` with retained JS to prove Python cannot leak either. |
| Eligible configuration: root `package.json` and `requirements.txt` | Preserve current JavaScript/Python and Node.js/Python framework detection. |
| Empty list and missing `files` | Existing successful Unknown/empty-list response. |
| Backslash equivalents `node_modules\lib\index.js`, `frontend\build\bundle.js`; mixed separators if Windows inputs are confirmed | Conditional on the documented separator contract above; do not silently claim support from the POSIX fix. |
