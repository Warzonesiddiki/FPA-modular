# 01 — PRODUCT REQUIREMENTS DOCUMENT (PRD)

> Status: Phase-0 spec v1.1 (pass-3 audit applied) · Owner of: what/why/scope · Behaviour lives in docs 02–13 as numbered requirements · Numbers that gate releases live in doc 14 · Conflicts: this doc wins on scope, doc 03/07/08 win on formulas, doc 02 wins on fields.

## 1. Product in one paragraph
FP&A Month-End Copilot is a local, offline, single-user Windows desktop app for a mid-size company's finance team. The analyst drops in the month's ERP exports (GL, budget, sub-ledgers as CSV/XLSX); the app validates and balances them, compares actuals vs budget/prior-year at the lowest shared grain, flags *potential* exceptions for human review with an accountable owner each, refreshes the rolling forecast with deterministic backtested methods, and generates the board Excel pack and PowerPoint deck — every figure drillable to the source transaction and the exact file and row it came from. It never writes back to the ERP, needs no internet, and stores everything in one local project folder.

## 2. The manual workflow being replaced
| # | Today (manual) | Pain | Product answer (FR) |
|---|---|---|---|
| 1 | Download/merge ERP exports monthly | Format drift, silent row loss | FR-IMP-* (doc 06): profiling, versioned mapping profiles, quarantine-with-reasons, control totals |
| 2 | Hand-build trial balance & check balance | Hours; errors found late | FR-IMP-010 TB gate before any analysis unlocks |
| 3 | BvA in pivots, filter-sort to transactions | Not repeatable; no drill standard | FR-CAL-* (doc 03): BvA at lowest shared grain, 1-click drill to voucher/row |
| 4 | Ad-hoc anomaly hunting, email owners | No tracking, no audit trail | FR-EXC-* (doc 07): 24-rule catalog, owner inbox, lifecycle, audit |
| 5 | Rebuild forecast in spreadsheets | No backtest, versions overwritten | FR-FOR-* (doc 08): methods + MAPE backtest, immutable versions, rolling rhythm |
| 6 | Copy numbers into Excel pack & PPT | Transcription errors; numbers diverge | FR-EXP-* (docs 09/10): generated from one data snapshot, cross-artifact tie-out test |
| 7 | Write variance commentary from scratch | Slowest senior-hour sink | FR-AI-* (doc 11, optional/off-default): drafts from verified tables only |

## 3. Personas & jobs-to-be-done
- **P1 FP&A analyst (primary operator).** JTBD: "Close the month and ship a board pack I can defend line-by-line, in one sitting, without Excel archaeology." Non-technical; Excel-fluent; colour-vision and keyboard use must never block them (doc 13).
- **P2 Accounting owner (secondary, does not operate the app daily).** Receives a finding list (in-app inbox view or exported action list), corrects entries in the ERP, re-export closes the loop. JTBD: "Tell me exactly which vouchers to look at and why."
- **P3 CFO/MD (consumer only).** Reads Excel/PPT/PDF. JTBD: "Every number I challenge drills to evidence in one step; commentary tells me what, why, what's next."
- Out of scope as users: external auditor (receives exports only), IT admin (installer only), multi-analyst concurrent teams (v1 is single-user; doc 17 phase 3).

## 4. Scope — v1 forced in/out
### IN (v1.0)
P&L/BS/CF (indirect) statements; BvA + PY + forecast-vs-actual; variance bridge where drivers exist; 24 exception rules with owner workflow; rolling forecast (8 methods, doc 08) + Base/Upside/Downside scenarios; Excel pack (12 sheets), PPT deck (8 slide types), PDF summary; CSV/XLSX import from any ERP via mapping profiles; single entity-group with multiple entities (reporting by entity/cc/account), single reporting currency per project; sample company; backup/restore; optional AI commentary (doc 11).
### OUT (explicit, with phase)
Live ERP connectors/API sync (Phase 2), multi-currency & FX translation & consolidation/eliminations & NCI (Phase 3), multi-user/roles/cloud (never in desktop line; possible separate product), full budget *authoring* workflow with contributor collection (Phase 2; v1 imports budgets + audited grid editing of imported budgets, doc 29 §1), tax/statutory reporting (never), ERP write-back (never), macOS/Linux (Phase 3).

## 5. Functional requirement families (detail owned elsewhere)
IMP (doc 06) · CAL statements/BvA/KPI (doc 03) · EXC rules/workflow (doc 07) · FOR forecast/scenarios (doc 08) · EXP exports (docs 09/10) · AI (doc 11) · SEC (doc 12) · UI screens S01–S19 (docs 13/21). Every FR has: statement, acceptance test pointer (doc 14), screen(s), API endpoint(s) (doc 05). No FR exists only in this PRD.

## 6. Success metrics (measured at gates, doc 14)
Golden sample month-end ≤ 30 min analyst hands-on time; acceptance bars (doc 14 §3) all green; 250k-row NFRs met; cross-artifact tie-out 100%; first-run-to-first-pack ≤ 60 min for a new analyst using only doc 18; zero P1 defects open at release; support burden target: ≤ 1 owner-decision (OQ) escalated per month-end on sample data.

## 7. Principles (binding, inherited from attempts 1–4 post-mortem)
P1 Docs before code. P2 Spec is truth; code drift = defect. P3 AI never computes/approves/posts money. P4 Offline-first, local-only, zero telemetry. P5 Every number drills to source row. P6 Scope discipline (new ideas → doc 17 backlog). P7 Non-technical UX, plain language. P8 "Potential exception", never accusation. P9 Quality bars are numbers. P10 Boring, testable, single-owner-per-concern code. P11 Monthly rhythm is first-class (month 2 must be easier than month 1). P12 All-or-nothing imports. P13 Nothing silently discarded. P14 Versioned everything the user edits. P15 Upgradeable releases, data preserved. P16 User docs ship with features. P17 Pinned, licence-checked dependencies. P18 Imported content is hostile data. P19 Colour never the only signal. P20 Tabletop walkthrough before approval.

## 8. Branding, naming, disclaimer
Working name "FP&A Month-End Copilot" appears in exactly: window title, installer display name, About screen (S13). Renaming = config change, never code. In-app and in every export footer: *"Advisory aid — not a certified accounting opinion, tax advice, or statutory audit assurance. Review by a qualified finance professional before external use."*

## 9. Assumptions & defaults (full register in doc 17)
Windows 11 target; FY start April (configurable, default Apr–Mar, IN-style but locale-neutral); currency INR default symbol-configurable, one per project; amounts in source files may be major units with decimals — parsed to integer minor units at import (doc 06); budget imported as CSV/XLSX at same grain or coarser (coarser handled per doc 03 §6).
