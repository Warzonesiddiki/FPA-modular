# 14 — TESTING & ACCEPTANCE SPECIFICATION

> Owner of: quality bars as numbers (P9), the acceptance gate, Definition of Done. Bars are release-blocking; weakening one requires an owner DEC in doc 17 + this doc changed in the same commit — never a quiet edit (attempt-#4 honesty rule).

## 1. Test pyramid (per work item — the paired test is part of the item, `docs/WORK_PLAN.md`)
Unit (pure functions: money, calendar, rules, methods, parsers) · Contract (every doc-05 endpoint + error; schema↔doc 02 equality **at table and column level**; doc 22↔`errors.py` code-set equality; OpenAPI↔doc 05 equality; UI token check; finding-key format) · Integration (import→commit→statements→rules→exports on fixture projects; mid-commit kill test; re-import idempotency) · Cross-artifact (API value == Excel cell == PPT number == PDF text for the golden period) · E2E (UI: one full month-end on sample company) · Perf (§4) · Security (doc 12 §8) · Accessibility (axe on every screen, keyboard path on S03/S07/S08).

## 2. Oracle-first rule
Every formula in docs 03/07/08/29/38–46 has a hand-worked example; the example is encoded as a fixture *before* the implementation and cited in the TASKBOARD handover. Tests must fail on a stubbed implementation — the builder mutation-checks every item (`AGENT_PROMPT.md` §6: ≥3 mutations, each caught by at least one test) and records the mutations in the handover.

## 3. THE acceptance gate (`scripts/acceptance.py`, runs harness twice)
Corpus: sample-data coherent corpus + answer_key (**36 plants, 13 controls**, doc 42 §7–§8). The corpus is self-authored, so a missed plant is a defect in a rule or in the plant — never an acceptable miss; the bars are therefore exact (DEC-008, amended by DEC-011 when rules 025–028 added P33–P36 and C11–C13).
| Bar | Threshold |
|---|---|
| Planted-exception recall | **36/36** plants found with the exact finding key (doc 07 §2) |
| High-severity recall | **19/19** High plants carry severity `high` (doc 42 §7; generator asserts the count) |
| Control precision | **0/13** controls fire |
| Suggestion exactness | every plant's finding carries the suggestion kind, balanced lines (Σ = 0) and confidence of doc 07 §7.3 / doc 42 §7 (answer key field `expected_suggestion`) |
| Severity exactness | every plant's severity equals the answer key (incl. P30 staying Medium) |
| Extra findings | Machine-checkable: harness emits extras.json listing every non-plant finding; gate passes only if every extra has a justification record {finding_key, classification: genuine|defect, reason ≥20 chars, reviewer} in acceptance_justifications.json and `defect` count = 0. Missing/short justifications fail the gate automatically. |
| Stability | Two consecutive runs produce identical finding keys + amounts |
| Coverage | 28/28 rules wired and executed (not_run only with documented missing-input reason) |
| ERP shape parity | committing each `sample-data/erp_shapes/` file of the golden period yields the same gl_rows as the CSV shape (doc 42 §4); the F&O shape's 3 `Tax`-layer rows are quarantined `OUT_OF_SCOPE_LAYER`; the trial-balance tie-out file reports zero differences |
| Connector parity (DEC-013) | with `tools/mock_d365.py` serving the corpus, `POST /connector/pull {2025-P07, [gl, ap, tb, masters]}` for **each** product ends `staged` with the preset auto-applied; committing yields gl_rows identical (ids, amounts, dimensions, vendor after enrichment) to the file import of the same shape and to the CSV shape; F&O `Tax`-layer rows quarantined; TB tie-out zero; a second pull returns `no_change` with no new batch; faults `429`, `503`, `truncate`, `count-drift`, `missing-entity` produce ERR-115/115/118/118/114 with zero batches and no snapshot file left behind; security assertions of doc 12 §8 (allow-list, redaction, keyring-only) pass |
| Statements | Golden PL/BS/CF tie to oracles to the minor unit; TB balanced |
| Cross-artifact | Golden period: API == Excel == PPT == PDF on 100% of compared figures |
Verdict written to `evidence/acceptance_report.{json,md}` with corpus hash. FAIL = release blocked, report says why per plant (the attempt-#4 report format is the template — it was excellent; its numbers were the problem).

## 4. Performance NFRs (reference profile: 4-core/16GB Windows, SSD; measured in tests/perf, budgets asserted)
250k-row GL: connector pull from the local mock (paged 10k, incl. snapshot write) ≤ 300s with ≤ 1 page of rows resident in memory · parse+stage ≤ 120s · commit ≤ 60s · full 28-rule run incl. suggestions ≤ 60s · statements+BvA ≤ 5s · Excel pack (12 sheets incl. 250k-row DrillData) ≤ 60s · PPT ≤ 20s · UI interactive (filter/sort 10k table rows) ≤ 1s perceived (virtualised). Regression > 10% on any budget fails CI; absolute breach fails release.

## 5. Coverage & static gates (`scripts/check.py`, one command, honest exit)
ruff clean · mypy strict on core/calc/rules/forecast · pytest pass · coverage: core/calc/rules ≥ 95% lines, overall ≥ 85% · UI: eslint + tsc + vitest + token check + axe · money-AST check (no `float(` in money paths, no money arithmetic outside money.py patterns) · full docs gate (`scripts/docs_check_release.py`, including the M0 bootstrap checks; doc 86 §1.1, DEC-014) · secret + telemetry scan (doc 12). No `--skip` flags exist.

## 6. Definition of Done (every work item; enforced by the builder's self-verification protocol, `AGENT_PROMPT.md` §6, and re-checked in the milestone audit session)
File(s) at the WORK_PLAN path · paired tests exist and pass with output pasted in the TASKBOARD handover · spec sections cited; zero undocumented deviation · ≥3 mutation checks recorded, each caught · no TODO/TBD/stub/mock-only path · user-facing text passes doc-13 copy rules · audit events emitted where doc 12 §3 requires · TASKBOARD row updated with evidence, never by claim.

## 7. UAT & go-live
Tabletop: owner walks one full month-end using only doc 18 (stumbles = defects). Pilot: one real (anonymisable) month from the owner’s company through import→pack; success = pack produced + every number spot-tied to source + findings reviewed (doc 17 Phase-2 gate). Release checklist (doc 16) signed with evidence links.
