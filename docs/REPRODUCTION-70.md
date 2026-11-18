# Issue #70 — local reproduction

**Issue:** [README parser test fixture is indented, so it contains no headings](https://github.com/codepath/pathreview-ai201-fa26-howard/issues/70)

**Confirmed:** November 17, 2026, on macOS with Python 3.12.13 and pytest 9.2.0, from branch `fix/70-readme-parser-fixture`, baseline commit `bd1626d`.

## Steps and observed results

From the repository root, using the virtual environment created during setup:

```bash
.venv/bin/pytest tests/unit/test_readme_parser.py::TestReadmeParser::test_parse_standard_readme -v -rx
```

Observed: `1 xfailed`. The strict marker cites issue #70 / manifest H-03; this result acknowledges the known defect rather than demonstrating a working test.

Expose the underlying assertion without editing the test or fixture:

```bash
.venv/bin/pytest tests/unit/test_readme_parser.py::TestReadmeParser::test_parse_standard_readme --runxfail -v
```

Observed: exit status **1**, `1 failed`. The failure is in `tests/unit/test_readme_parser.py:31`:

```text
>       assert result.metadata["heading_count"] > 0
E       assert 0 > 0
```

The input comes from `sample_readme_text()` in `tests/conftest.py`. Its first heading is literally `'    # Weather App'`, with four leading spaces. `ReadmeParser._extract_heading_hierarchy()` in `ingestion/parsers/readme_parser.py` matches `r"^(#{1,6})\s+(.+)$"`, so that input yields no matches.

## Controlled investigation

This compares the current fixture with a corrected copy held only in memory. It does not modify project files or remove any expected-failure markers.

```bash
.venv/bin/python - <<'PY'
from textwrap import dedent
from tests.conftest import sample_readme_text
from ingestion.parsers.readme_parser import ReadmeParser

original = sample_readme_text.__wrapped__()
parser = ReadmeParser()
for label, content in [("original", original), ("dedented", dedent(original))]:
    result = parser.parse(content)
    print(label, result.metadata)
    print(parser._extract_heading_hierarchy(content))
    print("text preserved:", result.text == content)
PY
```

Observed:

- Original: `heading_count=0`, `word_count=39`, hierarchy `[]`.
- Dedented copy: `heading_count=3`, `word_count=39`; headings are `Weather App` (level 1), `Features` (level 2), and `Tech Stack` (level 2).
- Both: `source_type='readme'`, `has_code_blocks=False`, `has_badges=False`, and returned text exactly equals the supplied input.

Baseline regression command:

```bash
.venv/bin/pytest tests/unit/test_readme_parser.py -q -rx
```

Observed: **13 passed, 2 xfailed**. The two expected failures cover #70 and the separate heading-hierarchy fixture issue #71. `rg -n 'sample_readme_text' tests` finds only its definition and the standard README test's use/assertion in this checkout.

## Conclusion

The test fixture is malformed for its intended purpose. The parser currently preserves the input and correctly finds no column-zero headings in it. The planned fix belongs in the fixture and the #70 test marker; production parser changes are not indicated by this reproduction. No issue fix has been applied in this reproduction commit.
