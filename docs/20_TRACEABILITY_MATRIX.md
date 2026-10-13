# 20 — REQUIREMENTS TRACEABILITY MATRIX

> No orphan anything: every FR ↔ spec section ↔ screen ↔ API ↔ file packet ↔ test ↔ acceptance evidence. This matrix is regenerated/checked in Wave 6; a row with an empty cell blocks release (doc 14 §6).

| FR family | Spec | Screens | API (doc 05) | Packets (manifest layer) | Tests | Acceptance evidence |
|---|---|---|---|---|---|---|
| FR-PRJ projects/periods | 19A, 23 | S01,S02,S13 | projects, periods lock | store/period_repo, api/routes_projects | test_period_repo, api projects | Month-end golden run |
| FR-MDM master data | 19B, 28 | S12 | master/* | store/master_repo, ui S12 | test_master_repo | Import unknown-code flow |
| FR-IMP import | 06, 19C | S03,S04,S05 | imports, mapping-profiles | imports/* (10 packets) | parser/mapping/validation/commit/TB | Malformed corpus expected.json |
| FR-CAL statements/BvA/KPI | 03, 29 | S01,S06,S07 | statements, bva, kpi, drill, bridge | calc/* (5) | statements/kpis/bva/attribution/drilldown | Oracle fixtures pl/bs/cf_basic |
| FR-CLO close mgmt | 30 | S01 (+S16 Close) | close/* (29 §API addendum) | services/close_service, ui S16 | test_close_service | Close checklist golden period |
| FR-PLN planning | 29 | S09,S10,S17 Planning | planning/* (29) | planning/* (8 packets, §29.9) | headcount/capex/debt/wc/cash13 tests | Integrated forecast BS balances |
| FR-EXC exceptions | 07 | S08,S01 | exceptions/* | rules/* (27) | test_exc_001…024 + engine | Acceptance gate §3 doc 14 |
| FR-FOR forecast/scenario | 08, 29 | S09,S10 | forecast/*, scenarios | forecast/* (11) | fc_* + scenarios + sensitivity/goal-seek | Backtest oracle (08 §3) |
| FR-REC reconciliations | 19I | S18 Reconcile | reconcile/* (19I) | imports/reconcile.py, ui S18 | test_reconcile | Recon fixture both-sides unmatched |
| FR-RPT reporting | 09,10,19J | S11 | exports, reports | exports/* (23) | sheet_*/slide_*/pdf/report-builder | Cross-artifact tie-out |
| FR-ALR alerts | 19K | S01,S19 Alerts | alerts/* | services/alerts.py, ui S19 | test_alerts | Alert dedupe fixture |
| FR-AI commentary/Q&A | 11 | S07,S09,S11 | commentary/* | ai/* (4) | ai_client/guardrails/commentary/prompts | Golden eval 16/20 (11 §7) |
| FR-GOV audit/security | 12, 22, 23 | S13,S14 | settings, audit | core/audit, api settings | audit chain, security suite | Tamper test |
| FR-HLP help/diagnostics | 18 | S15 | — (static) | ui S15 | a11y + walkthrough test | Tabletop UAT (14 §7) |

**Screens added by doc 19/29/30 (superseding doc 13 count):** S16 Close, S17 Planning, S18 Reconcile, S19 Alerts — doc 13's 5-state/copy/a11y rules apply unchanged; UI packets for S16–S19 are in the regenerated manifest. Total screens: 19.

## Expansion rows (docs 38–88, added in brutal-audit remediation 2026-10-14)
| Area | Spec | Screens | API (doc 05 §4) | Packets | Tests | Evidence |
|---|---|---|---|---|---|---|
| Adjustments | 39, 02 §6 | S06/S07 (layer selector) | adjustments, statements?layer | app/adjustments/engine, routes_adjustments | test_adjustments | layer drill in cross-artifact |
| Allocations | 40 | S17 | allocations | planning/allocations, routes_allocations | test_allocations | doc 40 oracle |
| Assumptions | 48 | S17/S09 | assumptions | planning/assumptions, routes_assumptions | test_assumptions | stale-run list |
| Year-end | 38 | S16 | year_end | services/year_end, routes_year_end | test_year_end | rollforward Δ=0 (UAT-06) |
| Close/Recon/Alerts/Planning/Report builder | 30/19I/19K/29/19J | S16–S19 | doc 05 §4 rows | close_service, alerts, planning/*, reconcile, report_builder + routes_* | their paired tests | UAT-01/03, doc 77 index |
| Licence | 79 | S13 | settings (licence state) | core/license | test_license | forged-licence fixture |
| AI prompts | 88, 11, 75 | S07/S11 | commentary | ai/prompts implements doc 88 texts verbatim | ai golden set | ai_eval artefacts |
