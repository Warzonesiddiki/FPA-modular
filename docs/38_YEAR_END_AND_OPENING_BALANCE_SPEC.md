# 38 — YEAR-END CLOSE & OPENING BALANCE SPECIFICATION

## 1. Year-end sequence (system-guided in S16, special task set for P12)
1. All periods P01–P12 locked (or waived per doc 23). 2. Year-end checks: TB balanced for year, suspense cleared or carried with note, accrual reversals posted (EXC-011 report attached), recon signed for P12. 3. **P&L close:** system computes closing entry proposal — every revenue/cogs/opex account netted to Retained Earnings (equity account tagged `retained_earnings`, exactly one per project; missing = blocking error with setup hint). The app never posts to the ERP: it generates the closing journal as an exportable schedule (Excel/CSV) for the accountant to post in the ERP, AND applies it virtually in-app (`adjustment layer`, doc 39, type `closing`) so in-app BS rolls correctly. 4. **Rollforward:** Opening BS (new FY P01) = Closing BS prior FY after virtual closing entry. Generated as an `opening` import batch (system-generated, source_kind=`opening`, batch label `SYS-OPEN-<FY>`) — visible, auditable, never hidden magic. 5. Analyst confirms rollforward screen (per-account prior-close vs new-open, Δ must be 0 except documented reclasses per doc 41).

## 2. Rules & invariants
BS account balances carry; P&L accounts open at 0. Opening batch is immutable once the first period of the new FY locks (before that, regeneration replaces it atomically, superseding). Comparative reporting after rollforward uses stored prior-FY actuals (never the opening batch) — opening batch feeds BS presentation only. Multi-FY trend queries span FYs via periods table (fiscal_year), not via opening batches.

## 3. Edge cases
First-ever FY: opening comes from `opening` import (doc 06) with the same TB gate. Mid-year adoption: opening at adoption period + P&L YTD imported as actuals (labelled `adopted_ytd` in Sources). FY-start-month change: forbidden on a project with locked periods (ERR with "create a new project" hint) — calendar history must never rewrite.

## 4. Oracle
FY close: Revenue 12,000,000; Costs 9,500,000 → Net 2,500,000. Closing entry: Dr Revenue 12,000,000 / Cr Costs 9,500,000 (presented netted per account in schedule) / Cr Retained Earnings 2,500,000. New FY opening RE = prior RE + 2,500,000; P&L accounts open 0; BS Δ check = 0.
Tests: rollforward round-trip, first-FY opening import, locked-FY regeneration rejection, comparative-after-rollforward equality.
