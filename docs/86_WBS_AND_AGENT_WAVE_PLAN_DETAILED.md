# 86 — DETAILED WBS & AGENT WAVE PLAN (dispatch order for 572 assignments)

> Expands MASTER_PLAN §8. Rule: a packet is dispatchable only when every packet in its "depends on" column is tester-SIGNED. Integrator (33) enforces; TASKBOARD (33 §3) is the live view.

| Wave | Packets (manifest layers/ids by layer) | Depends on | Gate to open next wave |
|---|---|---|---|
| 0 Docs | docs packets (01–18, 19–36 verify, 38–87 as authored) | — | Doc gate: docs-verify, tabletop J1–J8 read-through, owner approval DEC |
| 1a Core | core/* (money, errors, calendar, ids, hashing, audit, config, logging) + pyproject | Wave 0 | Unit gates; money AST check live |
| 1b Truth | store/schema+db, sample-data generator + answer key + malformed corpus, oracle fixtures, acceptance harness (runs red-by-design) | 1a | Corpus hash-stable; TB balanced; harness reports 0/32 with correct plumbing |
| 1c Foundations | imports/models+parsers+profiler | 1a/1b | Parser fixtures incl. hostile set |
| 2a Import engine | mapping, validation, control totals, commit, TB | 1c | Idempotency + kill-mid-commit tests |
| 2b Calc | statements, KPIs, BvA, attribution, drilldown, quality_score | 1b | Oracle fixtures green |
| 2c Rules | exc_001…024 (parallel, one agent each), engine, owner resolver, workflow | 2b + frozen doc 44 | Acceptance bars green (14 §3) |
| 2d Forecast/planning | forecast/*, planning/* (drivers→integrate last) | 2b | Backtest oracle; integrated balance oracle |
| 3 Services/API | month_end, dashboard, close, alerts, api routes, CLI, AI | 2a–2d | Contract parity (05↔routes↔63); AI-off socket test |
| 4 UI | api client, tokens, components, then screens S01–S19 (screens depend on their API routes) | 3 | 5-state + axe + token checks |
| 5 Exports | excel sheets → pack, slides → pack, pdf, report builder | 2b/2d/3 | Cross-artifact tie-out |
| 6 Ship | scripts, packaging, CI, user-guide final, AUD-001…132 | all | Doc 16 release checklist signed |

**Dispatch mechanics:** max parallel creators per wave bounded by disjointness (manifest guarantees); tester assigned at return, never pre-assigned to a creator's packet by the creator; BLOCKED returns go to integrator same-day (33 §4). Estimated critical path: 1a→1b→2b→2c (acceptance) — protect it; UI/export waves can absorb slip via the cut line (MASTER_PLAN §8).
