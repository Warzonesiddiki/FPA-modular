# Session start and housekeeping — 2026-10-13 UTC

Scope: baseline verification and the three owner-requested housekeeping changes, not a milestone audit or a product acceptance verdict. Inherited 2026-10-14 dates are retained as historical text; this execution uses the sandbox's current UTC date.

## Baseline
- `git fetch origin && git log --oneline -3`: HEAD `6cc5776` (shallow checkout); branch `arena/f906a206-fpa-modular`; initial working tree clean. No reset needed.
- First fetch attempt explicitly used `/home/user` rather than the checkout and returned `fatal: not a git repository`; repeated from `/home/user/FPA-modular`, successful.
- First `python -m pytest -q`: `/usr/bin/python: No module named pytest`.
- `pip install --break-system-packages pytest`: successful (pytest 9.1.1 in the sandbox only; no dependency pins or product files changed).
- `python -m pytest -q`: `9 passed in 0.40s`.
- `scripts/check.py` does not exist; not claimed run. No docs checker exists yet either.

## Housekeeping changes
1. `53a3cba`: AGENT_PROMPT §11 includes DEC-013, doc 26 §8 and doc 12 connector security sections; CHANGELOG updated.
2. `8df2d2d`: generated forbidden-network line matches AGENT_PROMPT §10; no item or dependency changes; CHANGELOG updated.
3. DEC-014: plan the M0 bootstrap at WI-0008 and preserve the full M6 checker at WI-0260 (`scripts/docs_check_release.py`); scopes owned by doc 86 §1.1. Exactly one new work item. TASKBOARD statuses preserved by path, not by the renumbered id. M0 stays open; no WI done.

Scope justification: generator and its generated outputs; owning gate/decision docs; references in README/docs 00/14/20/34/66/91/MASTER_PLAN; TASKBOARD and CHANGELOG. All seven repeated gate strings reconciled to their union (including the desktop launch, malformed corpus, walkthrough and second-seed requirements that the previous generator omitted). The stale doc-86/MASTER_PLAN M1 counts were corrected to DEC-011, not new bars. No app, schema, fixtures or product test changes.

## Executed verification

`python tools/generate_work_plan.py`:

```text
work items: 267; milestones: M0=8, M1=53, M2=75, M3=44, M4=51, M5=26, M6=10
```

Inline Python verification used `csv.DictReader`, `runpy.run_path('tools/generate_work_plan.py')`, SHA-256 and assertions for:
- 267 items, unique paths; WI-0008 = bootstrap with WI-0001…0007 dependencies; release checker in M6.
- 7/7 exact gate strings in generator == doc 86 §1.
- 267/267 TASKBOARD id/path/milestone triples == generated CSV.
- Regenerate a second time and compare SHA-256 of both generated files.
- Isolated graph mutations using the generator's actual `resolve_deps` / `check_graph` functions (no repository mutation): unresolved path, cycle, M0-to-M6 dependency.

Executed output:

```text
Plan checks: 267 unique items; WI-0008 after all seven docs; M6 full checker retained; 7/7 gates identical; 267/267 TASKBOARD identities match.
Regeneration: 2/2 generated files byte-identical on repeat.
Mutation 1 (unresolved dependency): caught by resolve_deps.
Mutation 2 (cycle): caught by check_graph.
Mutation 3 (M0 depends on M6): caught by check_graph.
```

`python -m pytest -q`: `9 passed in 0.12s`.

The first `git diff --check` after renumbering failed: Python CSV's default CRLF was reported as trailing whitespace on every changed row. Fixed the **generator**, not its output, with `lineterminator="\n"`; regenerated. Subsequent `git diff --check`: exit 0, no output. LF repeat-generation verification is recorded below after the final run.

## Limits
These checks validate plan wiring and unchanged nucleus tests. They do **not** validate semantic completeness of docs, implement the planned checkers, or close any gate. Existing `exists-unverified` items remain unverified. Product-data edge cases (money signs/exponents, 250k rows, locked periods, waivers, hostile financial input) are N/A to these docs/plan-only housekeeping changes; deterministic generation and invalid dependency input were exercised.

## Final housekeeping re-run (after LF correction)

```text
python tools/generate_work_plan.py
work items: 267; milestones: M0=8, M1=53, M2=75, M3=44, M4=51, M5=26, M6=10
[inline assertions with csv/runpy/subprocess/hashlib, also comparing HEAD:TASKBOARD.md statuses by path]
Final checks: 267 plan/ledger identities; 266 inherited statuses preserved; 7/7 gate strings; 2/2 repeat-generation hashes; CSV LF-only: PASS.
python -m pytest -q
9 passed in 0.10s
git diff --check
[exit 0, no output]
```
