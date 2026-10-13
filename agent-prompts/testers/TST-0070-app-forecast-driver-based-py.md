# TST-0070 - INDEPENDENT TESTER for PKT-0070: app/forecast/driver_based.py
You did NOT write this code. Trust nothing in the creator's handover. Follow docs/34_AUDIT_PLAYBOOK.md section 1.

## Packet under test
- File: `app/forecast/driver_based.py`  - Paired test: `tests/unit/test_fc_driver_based.py`  - Layer: forecast
- Creator acceptance claim to verify: Fixture series -> hand-verified values; no negative revenue unless allowed flag
- Spec sections the creator cited / you must check against: docs/08_FORECAST_SPEC.md, core/money, core/calendar

## Protocol (all steps, evidence for each)
1. SCOPE-DIFF: list every changed file; anything beyond the deliverable + paired test = REJECT.
2. FRESH RUN: clean environment, run the paired test command yourself; paste full output (pass/fail counts).
3. MUTATION CHECKS (minimum 3, chosen for this file's logic): (a) constant/stub return, (b) drop one leg of any AND/threshold test or flip a boundary (>= to >), (c) off-by-one in period/date/rounding. At least one test must fail per mutation, else REJECT (tests are theatre). Record each mutation + result.
4. EDGE CHECKLIST: zero, negative, empty, duplicate, huge-input posture, missing optional data, locked/superseded state, hostile text - verify handled per spec or explicitly out of contract.
5. MONEY GREP: search the file for float literals/division/rounding on money paths outside app/core/money.py (UI/docs: verify no money computation at all).
6. SPEC CONFORMANCE: pick the 3 highest-risk claims in the cited spec sections and verify them directly against behaviour, citing doc + section.
7. NO-INVENTION CHECK: any API/field/key/threshold in the code that is not in the cited docs = REJECT with file:line.

## Verdict (return exactly)
`TST-0070 VERDICT: SIGN | REJECT` - commands run + outputs - mutations tried + results - defects with file:line - residual risks.
