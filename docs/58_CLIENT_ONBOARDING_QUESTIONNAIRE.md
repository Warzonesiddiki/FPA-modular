# 58 — CLIENT ONBOARDING QUESTIONNAIRE (pilot discovery instrument)

> Turns doc 17 OQ defaults into a specific client's facts before pilot (doc 83). Owner completes with the client; answers become project settings + a DEC entry. Sections: 
**Company:** entities/legal structure, FY start, currencies, reporting calendar, close target days. **Systems:** ERP + version, export formats available (attach samples!), other sources (payroll/bank/AR/AP), who exports what by when. **Chart & masters:** COA file, cost centres, suspense/accrual accounts, account owners list. **Current process:** month-end steps today, hours spent, pack contents, who reviews, known pain top-3. **Budgets/forecast:** budget grain & owner, forecast method today, planning drivers, board questions most asked. **Thresholds & controls:** materiality, approval limits, manual-journal policy, lock policy. **Data samples:** 2 months GL + budget + subledgers (anonymisation per doc 78 if needed). **Success:** what "month-end in half the time" must prove at pilot review (doc 84 metrics). Each question has: why we ask (one line) + the default we use if unanswered (from doc 17) — a questionnaire that blocks on unanswered questions fails its own purpose.


## The full question set (answer or accept the stated default — unanswered never blocks)

### A. Company & calendar
A1 Legal entities and names? (default: 1) · A2 FY start month? (Apr) · A3 Reporting currency? (INR) · A4 Periods: monthly only, or any 4-4-5 need? (monthly) · A5 Target lock day after month-end? (T+5 business days, doc 62) · A6 Company holidays list (paste or attach).
### B. Systems & files
B1 ERP name/version? · B2 Who exports the GL, on which day, in what format? (attach a sample file — this becomes your first mapping profile) · B3 Budget file: who owns it, what grain (entity/account/cost-centre/month)? · B4 Sub-ledgers available: bank / AR / AP / payroll (which, formats)? · B5 Opening balances: available from (date)? · B6 Typical GL rows per month? (sizes the perf profile, doc 67) · B7 Sign convention in your exports: debit/credit columns or signed amounts? Any credit-negative quirks?
### C. Chart, masters & owners
C1 Attach COA export. Which accounts are suspense/clearing? (default: tagged + code 1999*) · C2 Accrual accounts? · C3 Accounts that must never be flagged (contra-allowed list for EXC-012)? · C4 Cost centres list + owners per account area (name; email optional)? · C5 Vendors where a single name has variants (e.g., "AWS", "Amazon Web Services")? — drives your alias clean-up list.
### D. Today's month-end (baseline we must beat)
D1 List your close steps in order, with owner and day for each. D2 Where do the hours actually go (top 3)? D3 Current pack: which Excel sheets / PPT slides, who receives them, on which day? D4 How are variances explained today, and who writes them? D5 Close cycle days last 3 months (period-end → pack sent)?
### E. Budgets, forecast & planning
E1 Budget approved by whom, locked when? E2 Forecast today: method, owner, update rhythm? E3 Key drivers (volume/price/headcount/…)? E4 Any headcount/capex/debt planning done outside the GL today (attach)? E5 Board's three most-asked questions?
### F. Thresholds & controls
F1 Materiality for management reporting (₹ and %)? (₹100k + 5%) · F2 Approval limit(s) for spend? (₹500k) · F3 Manual-journal policy: who may post, any review? · F4 Who may lock/unlock a period; who signs off close? · F5 Suspense clearing expectation (days)? (30)
### G. Access, data & AI
G1 Whose laptop, encrypted drive? (doc 18 guidance) · G2 Backup habit today? · G3 AI: allowed at all? Which provider if any (doc 11 consent facts)? Default: off. · G4 Any data that must never leave the machine even as aggregates? (default posture already: nothing leaves except optional AI aggregates)
### H. Pilot success (doc 83)
H1 The one number that proves the pilot (default: close cycle days −40% by close 3)? H2 Who is the CFO sponsor and the analyst operator (names)? H3 Parallel-run month preference (which month)? 
**Output of this questionnaire:** completed answers → project settings (doc 62), master data, mapping profiles, and a DEC entry recording every non-default (integrator completes within 2 working days of receipt).
