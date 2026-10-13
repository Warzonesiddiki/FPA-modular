# TST-0001 - TESTER for PKT-0001: pyproject.toml
You are the INDEPENDENT TESTER for packet PKT-0001. You did not write this code and must trust nothing in its handover.
Follow docs/34_AUDIT_PLAYBOOK.md section 1 exactly: (1) scope-diff - only `pyproject.toml` (+ paired test `-`) may have changed; (2) fresh-run the paired tests and paste output; (3) MUTATION CHECK - stub/weaken the implementation (constant return, drop one leg of any AND-test, off-by-one period) - at least one test must fail per mutation, else REJECT (tests are theatre); (4) edge checklist from the creator packet section 9; (5) money grep - float/division/rounding outside app/core/money.py; (6) spec conformance - cite the spec lines you verified.
Acceptance under test: `pip install -e .` exit 0; `python -c 'import app'` exit 0
Return exactly: `TST-0001 VERDICT: SIGN | REJECT` + evidence (commands, outputs, mutations tried) + defects with file:line.
