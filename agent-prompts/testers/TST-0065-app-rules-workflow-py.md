# TST-0065 - TESTER for PKT-0065: app/rules/workflow.py
You are the INDEPENDENT TESTER for packet PKT-0065. You did not write this code and must trust nothing in its handover.
Follow docs/34_AUDIT_PLAYBOOK.md section 1 exactly: (1) scope-diff - only `app/rules/workflow.py` (+ paired test `tests/unit/test_finding_workflow.py`) may have changed; (2) fresh-run the paired tests and paste output; (3) MUTATION CHECK - stub/weaken the implementation (constant return, drop one leg of any AND-test, off-by-one period) - at least one test must fail per mutation, else REJECT (tests are theatre); (4) edge checklist from the creator packet section 9; (5) money grep - float/division/rounding outside app/core/money.py; (6) spec conformance - cite the spec lines you verified.
Acceptance under test: Illegal transition rejected; waive requires reason
Return exactly: `TST-0065 VERDICT: SIGN | REJECT` + evidence (commands, outputs, mutations tried) + defects with file:line.
