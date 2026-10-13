# 14 — TESTING & ACCEPTANCE SPECIFICATION

> Owner of: quality bars as numbers (P9), the acceptance gate, Definition of Done. Bars are release-blocking; weakening one requires an owner DEC in doc 17 + this doc changed in the same commit — never a quiet edit (attempt-#4 honesty rule).

## 1. Test pyramid (per work item — the paired test is part of the item, `docs/WORK_PLAN.md`)
Unit (pure functions: money, calendar, rules, methods, parsers) · Contract (every doc-05 endpoint + error; schema↔doc 02 equality **at table and column level**; doc 22↔`errors.py` code-set equality; OpenAPI↔doc 05 equality; UI token check; finding-key format) · Integration (import→commit→statements→rules→exports on fixture projects; mid-commit kill test; re-import idempotency) · Cross-artifact (API value == Excel cell == PPT number == PDF text for the golden period) · E2E (UI: one full month-end on sample company) · Perf (§4) · Security (doc 12 §8) · Accessibility (axe on every screen, keyboard path on S03/S07/S08).

## 2. Oracle-first rule
Every formula in docs 03/07/08/29/38–46 has a hand-worked example; the example is encoded as a fixture *before* the implementation and cited in the TASKBOARD handover. Tests must fail on a stubbed implementation — the builder mutation-checks every item (`AGENT_PROMPT.md` §6: ≥3 mutations, each caught by at least one test) and records the mutations in the handover.

## 3. THE acceptance gate (`scripts/acceptance.py`, runs harness twice)
Corpus: sample-data coherent corpus + answer_key (**32 plants, 10 controls**, doc 42 §7–§8). The corpus is self-authored, so a missed plant is a defect in a rule or in the plant — never an acceptable miss; the bars are therefore exact (DEC-008).
| Bar | Threshold |
|---|---|
| Planted-exception recall | **32/32** plants found with the exact finding key (doc 07 §2) |
| High-severity recall | **18/18** High plants carry severity `high` (doc 42 §7; generator asserts the count) |
| Control precision | **0/10** controls fire |
| Severity exactness | every plant's severity equals the answer key (incl. P30 staying Medium) |
| Extra findings | Machine-checkable: harness emits extras.json listing every non-plant finding; gate passes only if every extra has a justification record {finding_key, classification: genuine|defect, reason ≥20 chars, reviewer} in acceptance_justifications.json and `defect` count = 0. Missing/short justifications fail the gate automatically. |
| Stability | Two consecutive runs produce identical finding keys + amounts |
| Coverage | 24/24 rules wired and executed (not_run only with documented missing-input reason) |
| Statements | Golden PL/BS/CF tie to oracles to the minor unit; TB balanced |
| Cross-artifact | Golden period: API == Excel == PPT == PDF on 100% of compared figures |
Verdict written to `evidence/acceptance_report.{json,md}` with corpus hash. FAIL = release blocked, report says why per plant (the attempt-#4 report format is the template — it was excellent; its numbers were the problem).

## 4. Performance NFRs (reference profile: 4-core/16GB Windows, SSD; measured in tests/perf, budgets asserted)
250k-row GL: parse+stage ≤ 120s · commit ≤ 60s · full 24-rule run ≤ 60s · statements+BvA ≤ 5s · Excel pack (12 sheets incl. 250k-row DrillData) ≤ 60s · PPT ≤ 20s · UI interactive (filter/sort 10k table rows) ≤ 1s perceived (virtualised). Regression > 10% on any budget fails CI; absolute breach fails release.

## 5. Coverage & static gates (`scripts/check.py`, one command, honest exit)
ruff clean · mypy strict on core/calc/rules/forecast · pytest pass · coverage: core/calc/rules ≥ 95% lines, overall ≥ 85% · UI: eslint + tsc + vitest + token check + axe · money-AST check (no `float(` in money paths, no money arithmetic outside money.py patterns) · docs link/ID check · secret + telemetry scan (doc 12). No `--skip` flags exist.

## 6. Definition of Done (every work item; enforced by the builder's self-verification protocol, `AGENT_PROMPT.md` §6, and re-checked in the milestone audit session)
File(s) at the WORK_PLAN path · paired tests exist and pass with output pasted in the TASKBOARD handover · spec sections cited; zero undocumented deviation · ≥3 mutation checks recorded, each caught · no TODO/TBD/stub/mock-only path · user-facing text passes doc-13 copy rules · audit events emitted where doc 12 §3 requires · TASKBOARD row updated with evidence, never by claim.

## 7. UAT & go-live
Tabletop: owner walks one full month-end using only doc 18 (stumbles = defects). Pilot: one real (anonymisable) month from the owner’s company through import→pack; success = pack produced + every number spot-tied to source + findings reviewed (doc 17 Phase-2 gate). Release checklist (doc 16) signed with evidence links.
