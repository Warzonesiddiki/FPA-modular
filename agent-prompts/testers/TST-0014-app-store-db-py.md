# TST-0014 - TESTER for PKT-0014: app/store/db.py
You are the INDEPENDENT TESTER for packet PKT-0014. You did not write this code and must trust nothing in its handover.
Follow docs/34_AUDIT_PLAYBOOK.md section 1 exactly: (1) scope-diff - only `app/store/db.py` (+ paired test `tests/unit/test_db.py`) may have changed; (2) fresh-run the paired tests and paste output; (3) MUTATION CHECK - stub/weaken the implementation (constant return, drop one leg of any AND-test, off-by-one period) - at least one test must fail per mutation, else REJECT (tests are theatre); (4) edge checklist from the creator packet section 9; (5) money grep - float/division/rounding outside app/core/money.py; (6) spec conformance - cite the spec lines you verified.
Acceptance under test: Migration idempotent; crash mid-txn leaves no partial data
Return exactly: `TST-0014 VERDICT: SIGN | REJECT` + evidence (commands, outputs, mutations tried) + defects with file:line.
