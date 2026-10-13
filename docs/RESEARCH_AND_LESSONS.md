# RESEARCH & LESSONS — evidence base for the Master Plan

## Prior attempts reviewed (2026-10-13)
| Repo | Stack | Scale reached | Where it stopped |
|---|---|---|---|
| `Warzonesiddiki/fpa` (OneFP&A) | Tauri 2 + Rust core + React 19, SQLite, HyperFormula | 76 docs, 42 screens (S-001…S-076), 56 tables, ~1,245 tests claimed | Rust handlers partly mock-only (WS-05/WS-07), native code never compiled in its build sandbox, CI red with fixes unpushed (expired token), design-token drift (7 undefined tokens / 39 uses) |
| `Warzonesiddiki/finalFPA` | Python FastAPI + React/Vite, DuckDB+SQLite, PyInstaller/Inno | 33+ docs, 355 py files, 24-rule catalog, full packaging | Acceptance gate red and honestly reported: planted recall 11/32, 422 extras (370 from incoherent random budget/actuals), 14 rules zero-coverage, key/grain mismatches (EXC-006/008/021/024), real-data pilot blocked |
| `java-fpa-tool-development-2-`, `v0-fpa-tool-development` | (not readable: GitHub integration returns 403 for these two) | — | Treated as attempts 1–2 by chronology; recommend owner grants access or exports a zip so their lessons can be mined before Wave 0 freezes |

## Lessons encoded as rules (traceability)
K1 scope-before-spine → Master Plan §3, §8 cut line · K2 incoherent corpus → §6 + sample-data work items, corpus precedes rules · K3 key divergence → §5 canonical contracts + freeze gate · K4 unverifiable native → §4 Python stack · K5 claimed-done drift → §9 evidence-or-not-done + independent testers (§7).

## What prior attempts got right (kept verbatim in spirit)
Docs-before-code; Decimal-only money; offline/local-only, zero telemetry; atomic all-or-nothing imports; nothing silently discarded; versioned mappings/thresholds; "potential exception" wording; 5-state screens; typed error catalogue; cross-artifact tie-out (UI == Excel == PPT); oracle fixtures before engines; largest-remainder rounding for statement presentation; planted-exception acceptance harness as a release gate.

## Market (Oct 2026, re-verify before any customer-facing use)
Cloud FP&A (Anaplan, Pigment, Planful, OneStream) = enterprise, custom pricing, long implementation; Excel-native (Datarails, Cube, Vena) = per-seat cloud under Excel; 2026 AI race = variance commentary + anomaly detection + agentic forecasting with drill-to-transaction. Sources: getaleph.com AI-FP&A comparisons, financecopilothq.com FP&A software 2026, chatfin.ai FP&A tools guide (accessed via web search 2026-10-13). **Positioning:** offline, single-analyst, one-time desktop tool — the wedge none of the cloud vendors can copy without cannibalising per-seat pricing.
