# 34 — VERIFICATION & AUDIT PLAYBOOK (self-verification, milestone audit sessions, owner spot-checks)

> In the single-agent model (DEC-007) the builder is also the tester and the auditor. That only works if verification is **procedural, evidenced and cold**: fixed checklists, pasted outputs, and audit sessions run as a stranger to the code. This doc owns those procedures; `AGENT_PROMPT.md` §6 is the per-item summary and must stay consistent with §1 here.

## 1. Per-item self-verification (every work item, before `done`)
1. **Read-back:** re-open the cited spec sections and the item's acceptance line; list the three highest-risk claims.
2. **Scope diff:** `git diff --stat` shows only the deliverable, its paired test, fixtures the spec names. Anything else is reverted or justified.
3. **Fresh run:** paired test from a clean process → pasted counts. Then the module's tests, then the full suite, then `scripts/check.py` when it exists.
4. **Mutation checks (≥3):** (a) main return → constant; (b) drop one leg of an AND / flip a boundary (`>=`↔`>`); (c) off-by-one in period/date/rounding; for rules also (d) swap the grain key order. Each mutation must make ≥1 test fail; record `mutation → failing test`. If none fails, the tests are theatre: fix the tests first.
5. **Edge checklist** (WORK_PLAN header): zero, negative, empty, huge (250k), duplicate, locked period, missing optional input, hostile text, unknown master code, period boundary, currency exponent ≠ 2 — each `PASS` (tested) / `N/A` (reason).
6. **Money audit:** no `float(`, no money arithmetic outside `money.py` patterns; API money is strings; UI never computes.
7. **Spec conformance:** verify the three claims from step 1 against behaviour; cite doc + §.
8. **No-invention:** every key, field, endpoint, error code, threshold exists in the cited docs (else class-B first).
9. **Determinism:** run twice; identical. Engines: diff artefacts.
10. **Handover block** (`AGENT_PROMPT.md` §8) in TASKBOARD; commit.

## 2. Milestone audit session (gate closure; run in a fresh session, written as a stranger)
Output: `evidence/audits/M<n>_audit.md` — method, cases, results, defects (with WI ids), verdict. An audit that finds nothing must show its method and the cases tried ("no findings" without evidence = not audited).
1. Re-read the milestone gate (doc 86 §1) and run every gate command; paste outputs with hashes.
2. **Sample re-verification:** choose ten `done` items by rule `WI number mod 7 == (milestone number mod 7)` (first ten matches; deterministic, not by preference); re-run §1 steps 2–9 on each from scratch.
3. Run the audit streams that apply to the milestone (§3): M1 A, C, J · M2 A, B, C · M3 C, D, K · M4 E, H · M5 I, A · M6 F, G, L.
4. File every defect as a TASKBOARD row (`blocked` or reopened `queued`), fix, re-run the affected stream, append the re-run to the audit file.
5. Close the gate: TASKBOARD, `docs/00_INDEX.md` §10, commit `audit: M<n> gate closed`.

## 3. Audit streams (A–L; other docs cite them as `AUD-A` … `AUD-L`)
- **A Recompute:** hand-rebuild PL/BS/CF/BvA/KPIs from raw fixtures in a spreadsheet (committed as `.calc.md`/`.xlsx` in `evidence/`); diff to the minor unit.
- **B Rule hunting (×24):** boundary ±1 minor unit and ±0.01% around every threshold; zero base; leap/short periods; designed false positives on the coherent corpus; confirm each doc 42 control catches its named wrong implementation by temporarily introducing that implementation.
- **C Contract parity:** API ↔ doc 05 (endpoints) ↔ doc 90 (fields); schema ↔ doc 02 (tables + columns); error codes ↔ doc 22; finding keys ↔ doc 07 §2; tokens ↔ doc 13; screens ↔ doc 21; settings keys ↔ doc 62.
- **D Adversarial:** prompt/formula/SQL/path injection; zip bomb; 1M-row file; tampered DB and broken audit chain; foreign-id access; AI-off socket test.
- **E UX tabletop:** a fresh session with only doc 18 completes a month-end on the sample project; every stumble is a defect with screen + step.
- **F Truth:** every README/doc/UI claim → evidence link or deletion (the "v1.0.0-rc2" rule from attempt #4).
- **G Performance & soak:** doc 14 §4 budgets on the reference profile; 12-period continuous use; DB growth; memory.
- **H Accessibility:** axe on every screen; keyboard-only S03/S07/S08; 200 % zoom.
- **I Export fidelity:** Excel formulas re-perform in a clean spreadsheet app; PPT vs Excel vs API vs PDF on a **second golden dataset generated from a different seed during the session** (never the dev fixture).
- **J Docs traceability:** every FR (doc 19) ↔ WI ↔ test (doc 20 planned matrix checked by `scripts/docs_check.py` in M0, built/evidenced matrix regenerated and diffed by `scripts/docs_check_release.py` in M6); every error code raised in a test; every screen state screenshotted; every oracle number in a doc recomputed in a test.
- **K Security review:** doc 12 §8 suite; secrets scan; dependency audit (`pip-audit`, `npm audit`) with lockfiles; licence check of any copied code.
- **L Release readiness:** doc 16 §4 checklist with evidence links; fresh-machine install; rollback drill (doc 61).

## 4. Owner spot-checks (any time, no notice)
Pick any `done` row; ask for the pasted commands to be re-run live; pick one mutation from the row and re-apply it. A row that fails a spot-check is reopened and the milestone audit for that milestone is re-run in full.

## 5. Severity & exit
**P0** wrong number / data loss / security hole / silent discard → release blocked; fix + re-audit the stream. **P1** contract divergence (doc ≠ code, doc ≠ doc) or missing evidence → fix before the gate closes. **P2** wrong behaviour, right numbers → fix or owner-accepted DEC with workaround in doc 18. **P3** cosmetic → backlog (doc 17 §5). Audit reports carry data hashes and the commit audited.
