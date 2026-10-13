# PKT-0061 — app/rules/exc_023.py

> **ONE AGENT. ONE FILE. NOTHING ELSE.** You create exactly `app/rules/exc_023.py` (plus its paired test if named below). You do not modify any other file. If a contract you need is missing, STOP and write `BLOCKED: <what>` — never invent a contract.

## 1. Mission
EXC-023: Voucher with single-line imbalance risk. Pure function: (gl_rows, params) -> Finding[]. Deterministic, Decimal only, catalog key format `rule|entity|account|period|grain-key` exactly as docs/07.

## 2. Read first (in this order, nothing else)
1. `docs/00_INDEX.md` §2 (reading plan) and §10 (current phase)
2. docs/07_EXCEPTION_RULES_CATALOG.md EXC-023, core/money, imports/models
3. This packet in full.

## 3. Inputs you may rely on
GL rows + threshold params

## 4. Output you must produce
- File: `app/rules/exc_023.py`
- Provides: Finding[] with evidence row_ids, amount, severity
- Layer: rules

## 5. Non-negotiable rules (violation = packet rejected)
1. **Money**: `Decimal`/integer minor units only, via `app/core/money.py`. Float for money anywhere = reject. AI never computes money.
2. **Traceability**: every aggregate must be drillable to source rows (file + row number).
3. **Nothing silently discarded**: rejected/quarantined data is reported with counts and reasons.
4. **No placeholders**: no TODO/TBD/`pass`/mock-only/stub returns. If you cannot finish, return `BLOCKED`, not a fake.
5. **No scope invention**: implement only what §1 + the cited spec section say. New ideas -> write them in your handover note, not in code.
6. **Plain language**: user-facing text is written for a non-technical FP&A analyst; every error has a hint telling them what to do next.
7. **Deterministic**: same input -> same output, byte-for-byte where applicable. No wall-clock/randomness in calculations (inject clock/seed).
8. Follow `docs/15_CODING_STANDARDS.md` (naming, typing, docstrings, error codes from `app/core/errors.py`).

## 6. Acceptance criteria (all must pass; evidence required)
Planted case fires exactly once; control case does NOT fire; key format snapshot test

## 7. Paired test file
`tests/unit/test_exc_023.py` — if named, the test is part of this packet's definition of done. Tests must include: happy path, the spec's worked example, one failure/edge case, and (for money) a rounding case. Tests must FAIL if the implementation is stubbed (mutation honesty).

## 8. Packet-specific notes
Cause of death in attempt #4: keys/thresholds diverged from answer key. The catalog doc is law - quote its sample case in your test.

## 9. Definition of done — return exactly this handover format
```
PACKET: PKT-0061
FILE: app/rules/exc_023.py
STATUS: DONE | BLOCKED
TESTS RUN: <command> -> <pass/fail counts>
EVIDENCE: <output excerpt or artefact path>
CONTRACTS USED: <spec sections + dependency APIs>
DEVIATIONS: none | <list, each with reason>
BLOCKED ON: none | <exact missing contract>
```
A `DONE` claim without test evidence is treated as not done.
