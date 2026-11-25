## Solution plan

**Issue:** [#20 — Implement a DependencyAuditTool that flags outdated major dependencies in project repos](https://github.com/codepath/pathreview-ai201-fa26-howard/issues/20)

### Understand

I reproduced the gap with PathReview’s own manifests. The frontend locks Vite at 5.4.21 and Vitest at 1.6.1, which were three and four major versions behind at the time of the reproduction. The orchestrator identified JavaScript and Node.js but reported neither dependency.

`Orchestrator._build_plan()` passes filenames to `TechDetector`, which uses them to identify the stack. The GitHub tool fetches repository metadata and checks for a README. The missing capability is an agent tool that reads dependency declarations, looks up current stable versions, and reports a finding when the latest major is at least two higher than the major allowed by the declaration.

### Map

- `agent/tools/dependency_audit_tool.py` — implement `DependencyAuditTool` using the existing `BaseTool` and `ToolResult` interface. Parse manifests, compare versions, and return findings.
- `agent/tools/github_tool.py` — add a read-only method to discover and fetch supported manifests from a submitted GitHub repository, using the existing authentication setup.
- `agent/orchestrator.py` — register the audit tool and schedule it when manifest contents or a submitted repository reference are available.
- `pyproject.toml` — declare `packaging` as a direct dependency for `Requirement` and `Version`.
- `tests/unit/test_dependency_audit_tool.py`, `tests/unit/test_github_tool.py`, and `tests/unit/test_orchestrator.py` — cover parsing and comparison, GitHub manifest retrieval, and orchestration.
- `tests/fixtures/dependency_audit/` — add small sample manifests and mocked GitHub, npm, and PyPI responses, following the external API fixture convention in `docs/CONTRIBUTING.md`.

The proposed scope is the agent layer. The web review service uses placeholder orchestration and GitHub ingestion, so getting the audit into a browser review would require a separate integration decision.

### Plan

1. **Capture the gap in a unit test.** Use a small `package.json` with Vite `^5.0.0` and Vitest `^1.0.0`, with stubbed current versions in majors 8 and 5. Expect two findings with gaps of 3 and 4. Include an adjacent-major example to check that a gap of exactly 1 produces no finding.
2. **Parse the three manifest types and compare versions.** Read npm `dependencies` and `devDependencies` from JSON, parse requirement lines from `requirements.txt`, and read `[project].dependencies` and `[project.optional-dependencies]` from `pyproject.toml` with `tomllib`. Preserve the original declaration and source path. Use npm’s stable `latest` tag or the latest non-yanked stable release on PyPI, and reuse each package lookup within a single audit. Inject the version lookup in unit tests so the comparison does not depend on the network or future releases.
3. **Fetch manifests for submitted GitHub repositories.** Add `GitHubTool.fetch_dependency_manifests(username, repo_name) -> tuple[dict[str, str], list[str]]`. Use the repository’s default branch, discover supported filenames including nested paths such as `frontend/package.json`, skip vendored directories such as `node_modules` and `.venv`, and fetch only the matching text files. Keep a bound on files, response size, and request time. Return manifest text and any warnings about missing coverage. Test discovery, nested paths, and partial retrieval with mocked GitHub responses.
4. **Wire the audit into the orchestrator.** Run one audit for supplied manifest contents or the submitted repo selected by the existing GitHub planning branch. The orchestrator receives its tool dictionary from its caller. Make the audit available by default while preserving any caller-supplied audit instance, and schedule it under the same name the tool declares. Return the results under `tool_results["dependency_audit"]`. Test both inputs through `Orchestrator.run()` and confirm profiles with neither input skip the audit. Bypass the orchestrator’s cross-run result cache for this tool. A second run on the same instance must see changed registry or repository data, including recovery after a failed lookup.
5. **Verify the fix locally.** Run `.venv/bin/python -m pytest tests/unit/test_dependency_audit_tool.py tests/unit/test_github_tool.py tests/unit/test_orchestrator.py -v`, then `make test-unit`. Repeat the journal reproduction with the same file list and add `profile_data["manifests"] = {"frontend/package.json": Path("frontend/package.json").read_text()}`. Compare the returned findings for Vite and Vitest with the table below, using fixed registry versions for a repeatable check. Run the repository’s PR checks before submitting.

### Inputs & outputs

- **Input** — `DependencyAuditTool.execute(input_data: dict) -> ToolResult` accepts a `manifests` mapping from repo-relative paths to file contents, or `github_username` and `repo_name` for GitHub retrieval. The manifest contents take precedence if both are supplied.
- **Output** — `ToolResult.data` contains `findings` and `warnings` lists. A finding contains the ecosystem, package name, manifest path, original version specifier, highest allowed major, latest stable version, and the major-version gap. Put skipped files and failed lookups in `data["warnings"]`, since `Orchestrator.run()` forwards only `ToolResult.data`. Verify warnings survive that call even when no packages could be checked.
- **Comparison** — Flag only when `latest_major - highest_allowed_major > 1`. Start with exact pins, npm caret and tilde ranges, and Python compatible releases, wildcards, and explicit upper bounds. For example, `>=4.0.1,<5.0.0` allows at most major 4, while `redis>=5.0.0` has no upper bound and cannot establish that Redis is outdated. Keep manifest constraints distinct from installed or locked versions.

**Acceptance cases with fixed registry responses**

| Manifest | Declaration | Registry major | Expected result |
|---|---|---:|---|
| `frontend/package.json` | Vite `^5.0.0` | 8 | Flag Vite, gap 3 |
| `frontend/package.json` | Vitest `^1.0.0` | 5 | Flag Vitest, gap 4 |
| `requirements.txt` | `example==2.4.0` | 4 | Flag example, gap 2 |
| `requirements.txt` | `example==2.4.0` | 3 | No finding, gap 1 |
| `pyproject.toml` | `example>=3,<5` | 6 | Flag example, gap 2 from highest allowed major 4 |
| `pyproject.toml` | `redis>=5` | 8 | No finding, since the range permits major 8 |

### Risks & unknowns

- **Range semantics** — Use Python packaging rules for Python requirements and test common npm ranges independently. If a constraint is too complex to establish an upper major with confidence, skip it with a reason. [Python version specifiers](https://packaging.python.org/en/latest/specifications/version-specifiers/) · [npm semver ranges](https://docs.npmjs.com/cli/v6/using-npm/semver/)
- **Network limits** — GitHub and package registries can rate-limit or time out. Use bounded requests, keep findings from successful lookups, and report incomplete coverage. GitHub discovery can return a truncated tree, which should be visible as a warning. [GitHub repository contents](https://docs.github.com/en/rest/repos/contents)
- **Coverage decision** — The proposed first pass covers direct manifest declarations. Confirm whether the assignment expects Poetry-specific tables, lockfile resolution, or findings in the browser review before expanding the scope.

### Edge cases

- A gap of zero or one, a version ahead of the registry’s current major, or an open-ended range produces no outdated warning.
- Blank lines, comments, Python extras, npm scoped names, and ordinary development dependencies still parse. Local, Git, URL, and unsupported declarations are skipped.
- A malformed manifest, missing registry package, prerelease-only package, or failed lookup leaves any other valid findings available.
- A repository without supported manifests returns no findings. If discovery or a lookup fails, the result explains what could not be checked.
