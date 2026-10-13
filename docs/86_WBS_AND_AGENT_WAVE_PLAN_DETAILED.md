# 86 — MILESTONE PLAN & EXIT GATES (single-builder execution of `docs/WORK_PLAN.md`)

> Expands MASTER_PLAN §8. The multi-agent "wave" plan (572 assignments) was retired by DEC-007; this doc now defines the **seven milestones**, their exit gates and the ordering rules the sole builder follows. The authoritative, generated sequence of the 241 work items is `docs/WORK_PLAN.md` (+ `.csv`), produced by `tools/generate_work_plan.py`; `TASKBOARD.md` is the live status. Gate text here and in the generator header must be identical (the generator prints the gate at the top of each milestone section; `scripts/docs_check.py` diffs them).

## 1. Milestones
| Milestone | Scope (WORK_PLAN layers) | Items | Exit gate (all must be evidenced in `evidence/audits/M<n>_audit.md`) |
|---|---|---|---|
| **M0 — Spec hardening** (docs only) | `docs0`: deepen docs 05, 21, 44, 03, 55, 31, 20; close every P0/P1 of `audit/BRUTAL_AUDIT_PASS3_2026-10-14.md` that is a doc defect | 7 | `scripts/docs_check.py` clean (links, IDs, FR↔WI↔test matrix, period-id notation, no multi-agent terms, gate text parity); the seven docs at implementable depth per their acceptance lines; DEC-007/008/009 recorded and either accepted or vetoed by the owner |
| **M1 — Core & truth** | `config`, `core`, `store`, `data`: pyproject, money, errors, calendar, ids, hashing, audit, config, logging; schema v2 = doc 02 (tables **and columns**, incl. `connector_*`), db, migrations, repos (incl. `connector_repo`); corpus generator + plan.json + answer key + malformed corpus + ERP file and API shapes; oracle fixtures (doc 89 §1, §3–§5); acceptance harness | 53 | Schema-equality (doc 02 ↔ schema.sql) green; corpus regenerates byte-identical; TB balanced per entity × period; answer key 32/18/10 asserted; acceptance harness runs and reports 0/32 by design; all core tests green; coverage core ≥ 95% |
| **M2 — Engine** | `imports`, `calc`, `rules`, `forecast`, `planning`, `adjust` | 75 | Acceptance gate green (doc 14 §3): recall 36/36, High 19/19, controls 0/13, suggestion exactness, extras justified, two runs identical, 28/28 wired; statement/KPI/forecast/planning oracles green; malformed corpus `expected.json` exact |
| **M3 — Connector, services, API, CLI, AI, desktop shell** | `connectors` (DEC-013: models, profiles, transport, auth, odata, snapshot, F&O + BC adapters, `tools/mock_d365.py`, recorded fixtures), `services` (incl. `connector_service`), `api` (incl. `routes_connector`), `cli`, `ai`, `desktop` | 44 | OpenAPI == doc 05 catalogue (endpoints, incl. connector routes) and doc 90 (fields); AI-off **and connector-off** socket test; connector parity bar (doc 14 §3) green against the mock for both products incl. no-change and the five faults; connector security tests (doc 12 §8) green; CLI golden month-end exit 0 (file route and `fpa pull --mock`); job registry crash-recovery test; desktop shell launches the server and opens the UI placeholder |
| **M4 — UI** | `ui`: client, tokens, components (incl. `ConnectionCard`), screens S01–S19 (S01 Refresh, S03 Source step, S13 Connections) | 51 | 5-state + axe + keyboard tests on all 19 screens; token check zero-undefined; UI numbers == API fixtures; no inline strings; walkthrough (doc 18 §1) passes on the sample project |
| **M5 — Exports** | `exports`: Excel sheets → pack, slides → deck, PDF, report builder, rectification journal | 26 | Cross-artifact tie-out 100% on golden period `2025-P07` (both layers); golden-file cell/slide tests; blocked-deck case; second-seed audit dataset generated and passed (doc 34 stream I) |
| **M6 — Ship** | `scripts`, `packaging`, `ci`, `docs6` | 10 | Fresh-machine install → sample month-end → pack out; perf budgets met or DEC; doc 16 §4 release checklist signed with evidence links; truth audit clean (doc 34 stream F); docs gate green |

Test items (`test` layer) belong to the milestone of the module they test and are listed beside it in WORK_PLAN.

## 2. Ordering rules
1. **Strict milestone order.** No item of M*n+1* starts while M*n*'s gate is open. Exception: a `blocked` item (class C, `AGENT_PROMPT.md` §4) may be bypassed within the milestone, never across it.
2. **Within a milestone, WORK_PLAN order** (topological on declared dependencies, then layer rank, then path). The builder takes the first non-done item whose dependencies are done.
3. **Critical path:** M1 schema/corpus → M2 calc → M2 rules → acceptance gate. Protect it: when a class-A question touches it, apply the default and proceed the same session.
4. **Cut line (MASTER_PLAN §8):** if time is short, M4 screens S16–S19 and M5 report builder may ship in v1.1 by owner DEC — never the acceptance gate, cross-artifact tie-out, security suite or audit chain.
5. **Gate closure = audit session.** When every item of a milestone is `done`, the builder runs the milestone audit session (doc 34 §2) in a fresh session, writes `evidence/audits/M<n>_audit.md`, fixes defects, and only then marks the gate closed in TASKBOARD and `docs/00_INDEX.md` §10.

## 3. Capacity & estimates (for the owner's planning, not for pressure)
Items are sized so that one is typically one focused session (contract → tests → implementation → verification → handover). Rule and screen items are deliberately small and repetitive; corpus generator, acceptance harness, statements engine, Excel pack and desktop packaging are the large ones (expect 2–4 sessions each and plan a mid-item handover note in TASKBOARD). Progress is reported as the gate table above with counts from TASKBOARD, never as percentages of "feel".

## 4. What replaced what (for readers of older docs)
| Old (multi-agent) | Now |
|---|---|
| Waves 0–6, 572 assignments, 317 packets + 317 tester prompts | Milestones M0–M6, 266 work items (250 before DEC-013), one builder |
| `agent-prompts/PKT-*.md`, `TST-*.md`, `00_MASTER_AGENT_PROMPT.md` | `AGENT_PROMPT.md` + `docs/WORK_PLAN.md` |
| `docs/FILE_MANIFEST.*`, `docs/DEPENDENCY_GRAPH.*`, doc 91 packet dependencies | `docs/WORK_PLAN.csv` (deps column, machine-readable) + doc 91 build-order spec |
| Integrator, tester sign-off, BLOCKED-and-wait | Self-verification protocol, milestone audit session, class-A/B/C gap rules |
| "Dispatchable when all dependencies tester-SIGNED" | "Startable when all dependencies `done` with evidence" |
