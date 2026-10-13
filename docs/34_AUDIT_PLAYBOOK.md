# 34 — AUDIT & REVIEW PLAYBOOK (for tester + auditor agents)

## 1. Tester protocol (per packet, ~30 min)
1. Read the packet + cited spec only. 2. Diff the return: exactly the packet's file(s) changed? 3. Run the packet's tests fresh (clean env) — paste output. 4. Mutation check: stub/weaken the implementation (e.g., return constant, drop the AND-leg of a threshold) → at least one test must fail; if none fail, verdict = REJECT (tests are theatre). 5. Edge checklist: zero, negative, empty, huge (250k), duplicate, locked-period, missing-optional-input, hostile text — each either handled per spec or explicitly out-of-contract. 6. Money audit: grep the file for float/division/rounding outside money.py. 7. Verdict in handover format: `TST-#### VERDICT: SIGN | REJECT — <evidence>`.

## 2. Audit streams (Wave 6 + pre-release; each an AUD packet)
- **AUD-A Recompute:** hand-rebuild PL/BS/CF/BvA from raw fixtures in a spreadsheet; diff to minor unit.
- **AUD-B Rule hunting (×24):** boundary ±1 minor unit, ±0.01% around thresholds; zero-base; leap/short periods; designed false-positive attempts on coherent corpus.
- **AUD-C Contract parity:** run + extend parity scripts (API↔05, schema↔02, tokens, finding keys, error codes ↔ 22, screens ↔ 21).
- **AUD-D Adversarial:** prompt/formula/SQL/path injection; zip-bomb & 1M-row files; tampered DB/audit; token-less API calls.
- **AUD-E UX tabletop:** fresh agent + only doc 18 completes a month-end on sample; log every stumble as a defect w/ screen+step.
- **AUD-F Truth:** every README/doc/UI claim → evidence or deletion list (the "v1.0.0-rc2" rule).
- **AUD-G Performance & soak:** doc 14 budgets; 12-period continuous use (month 2…12 rhythm), DB growth, memory.
- **AUD-H Accessibility:** axe + keyboard-only S03/S07/S08 + 200% zoom pass.
- **AUD-I Export fidelity:** Excel formulas re-perform in a clean spreadsheet app; PPT numbers vs Excel vs API on a second golden period (not the dev fixture — auditor-generated data).
- **AUD-J Docs completeness:** every FR (19) traced (20); every error code (22) raised somewhere in tests; every screen state (21) screenshotted.

## 3. Severity & exit
P1 wrong number / data loss / security hole → release blocked, fix + re-audit stream. P2 wrong behaviour, right numbers → fix or owner-accepted DEC w/ workaround in doc 18. P3 cosmetic → backlog (17). Audit reports live in `evidence/audits/` with data hashes; an audit that finds nothing must show its method + cases tried (empty-report rule: "no findings" without evidence = not audited).
