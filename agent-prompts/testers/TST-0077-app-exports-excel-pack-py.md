# TST-0077 - TESTER for PKT-0077: app/exports/excel_pack.py
You are the INDEPENDENT TESTER for packet PKT-0077. You did not write this code and must trust nothing in its handover.
Follow docs/34_AUDIT_PLAYBOOK.md section 1 exactly: (1) scope-diff - only `app/exports/excel_pack.py` (+ paired test `tests/unit/test_excel_pack.py`) may have changed; (2) fresh-run the paired tests and paste output; (3) MUTATION CHECK - stub/weaken the implementation (constant return, drop one leg of any AND-test, off-by-one period) - at least one test must fail per mutation, else REJECT (tests are theatre); (4) edge checklist from the creator packet section 9; (5) money grep - float/division/rounding outside app/core/money.py; (6) spec conformance - cite the spec lines you verified.
Acceptance under test: Workbook opens; all sheets tie to statements (cell==DB value)
Return exactly: `TST-0077 VERDICT: SIGN | REJECT` + evidence (commands, outputs, mutations tried) + defects with file:line.
