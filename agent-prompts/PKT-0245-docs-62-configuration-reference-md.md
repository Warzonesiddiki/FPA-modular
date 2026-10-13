# PKT-0245 — docs/62_CONFIGURATION_REFERENCE.md
> TYPE: REVIEW (file exists - verify against its spec, report gaps in the handover, do not rewrite it)

> **ONE AGENT. ONE FILE. NOTHING ELSE.** You create exactly TWO files: `docs/62_CONFIGURATION_REFERENCE.md` and its paired test if named below (section 7). You do not create or modify any other file. If a contract you need is missing, STOP and write `BLOCKED: <what>` — never invent a contract.

## 1. Mission
Perfection-register doc 62: authored by lead; agent verifies cross-refs, IDs, consistency with docs 01-36 and reports gaps - does not rewrite unilaterally.

## 2. Read first (in this order, nothing else)
1. `docs/00_INDEX.md` section 2 (reading order) and section 10 (current phase)
2. docs/37_MISSING_DOCS_AND_PERFECTION_REGISTER
3. This packet in full.

## 2b. Resolving dependencies
Dependency names below (e.g. `api/client`, `calc/bva`) are MODULE NAMES, not paths: find the owning packet in `docs/FILE_MANIFEST.csv` (search the path column) and treat that file's public contract + the cited doc sections as fixed. If the owning file does not exist yet, return BLOCKED (your wave has not opened).

## 3. Inputs you may rely on
existing doc

## 4. Output you must produce
- File: `docs/62_CONFIGURATION_REFERENCE.md`
- Provides: verified doc
- Layer: docs

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
Docs-verify passes; every referenced ID exists; zero placeholders

## 7. Paired test file
`-` — if named, the test is part of this packet's definition of done. Tests must include: happy path, the spec's worked example, one failure/edge case, and (for money) a rounding case. Tests must FAIL if the implementation is stubbed (mutation honesty).

## 8. Build order (follow exactly)
1. Re-read the cited spec sections; write down (in your head/notes) the exact contract: inputs, outputs, error codes, formulas/keys.
2. Write the paired test FIRST from the spec's worked examples + the edge checklist in section 9; run it - it must fail for the right reason.
3. Implement the smallest complete version satisfying the contract (no extra features, no extra files).
4. Run: paired tests, then the module's neighbouring tests, then `python scripts/check.py` if it exists yet (Wave>=3) - record exact commands/outputs.
5. Self-review against section 5 rules and section 9 checklist; fix before returning.

## 9. Universal edge-case checklist (address every line in code or test, or state why N/A)
Mark each line PASS (handled+tested), TEST-ONLY, or N/A with a one-line reason in your handover - silently ignoring a line = reject. Zero amounts / zero denominator; negative amounts and credit-normal accounts; empty input; single row; duplicate input; very large input (250k rows posture); missing optional data (rule must report not_run, export must label, UI must show empty state); locked period/version; superseded batch; expired waiver; hostile text (quotes, `=formula`, `<script>`, unicode, 10k-char description); ambiguous dates/amounts; currency minor-unit exponent; month 2 reuse (no month-1 assumptions hard-coded); deterministic repeat run.

## 10. Forbidden in this packet
Editing any other file (incl. "helpful" fixes); adding dependencies; changing a spec, threshold, key format, or error code; committing secrets/test data with real financials; disabling a lint/type rule; `float` on money; TODO/TBD/stub/mock-only code.

## 11. Packet-specific notes
See doc 37 for why this doc exists and its priority.

## 12. Definition of done — return exactly this handover format
```
PACKET: PKT-0245
FILE: docs/62_CONFIGURATION_REFERENCE.md
STATUS: DONE | BLOCKED
TESTS RUN: <command> -> <pass/fail counts>
EVIDENCE: <output excerpt or artefact path>
CONTRACTS USED: <spec sections + dependency APIs>
DEVIATIONS: none | <list, each with reason>
BLOCKED ON: none | <exact missing contract>
```
A `DONE` claim without test evidence is treated as not done.
