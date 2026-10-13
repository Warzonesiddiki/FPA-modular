# 00 — INDEX (start here)

## §1 Purpose
FP&A Month-End Copilot (working name) — offline, local-only desktop app that lets ONE FP&A analyst run the full monthly cycle: import → validate → statements → BvA → exceptions → close → forecast/planning → board Excel/PPT/PDF pack, every number traceable to its source row. Design is complete in this folder; the build is executed by one agent following `AGENT_PROMPT.md` (DEC-007).

## §2 Reading order by role
| Role | Read |
|---|---|
| Owner / approver | `MASTER_PLAN.md` → §3/§10 here → `TASKBOARD.md` (*Owner attention*) → `17` §3/§4 (OQ/DEC) → `audit/BRUTAL_AUDIT_PASS3_2026-10-14.md` → `86` (gate table) |
| The builder agent (first session) | `AGENT_PROMPT.md` §11 order: this doc → `MASTER_PLAN` → `86` → `14` → pass-3 audit → `WORK_PLAN` header + M0 → WI-0001 |
| The builder agent (every later session) | `AGENT_PROMPT.md` → `TASKBOARD.md` → the current WI's cited sections only |
| Anyone verifying a claim | `34` (streams), `14` (bars), `evidence/` |

## §3 Owner's 10-minute brief
Problem, product, wedge and success metrics: `01_PRD` §§1–6 and `32` §Positioning. Decisions: none waiting — the owner delegated them (DEC-010 in `17` §4; DEC-008/009 accepted, OQ-11…16 closed; DEC-013 made the Dynamics 365 direct connector a v1 capability — the only thing the owner's IT must do is the 15-minute Entra app registration in `18` §8). `TASKBOARD.md` → *Owner attention* lists what was decided and where. Status: §10 below and the gate table in `86` §1.

## §4 Document map
Numbered specs 01–91 (§7 lists them), plus `MASTER_PLAN.md` (plan of record), `WORK_PLAN.md` + `WORK_PLAN.csv` (generated build sequence — 266 work items, milestones M0–M6), `RESEARCH_AND_LESSONS.md`, `CHANGELOG.md`. Root files: `AGENT_PROMPT.md` (the builder's prompt), `TASKBOARD.md` (live ledger), `tools/generate_work_plan.py` (generator of the plan). Retired by DEC-007 and deleted: `agent-prompts/`, `FILE_MANIFEST.*`, `DEPENDENCY_GRAPH.*`, `tools/generate_agent_packets.py`.

## §5 Source-of-truth matrix (who wins on conflict)
| Fact | Owner |
|---|---|
| What/why/scope | `01_PRD`; behaviour register `19` (FR ids) |
| Tables & fields | `02_DATA_DICTIONARY` (= `app/store/schema.sql`, table-and-column test; §7 lists the deltas open until M1) |
| Any number's formula | `03` (statements/KPI/BvA) · `07`+`44` (rules) · `08`+`46` (forecast) · `29`/`40` (planning/allocations) · `38` (year-end) — each with hand-worked oracles catalogued in `89` |
| Statement line keys & presentation | `45` |
| Plants, controls, answer key | `42` §7–§8 |
| Acceptance bars & Definition of Done | `14` (§3 bars, §6 DoD) |
| Endpoints / payload fields | `05` (endpoints, status codes) / `90` (fields) — both normative, parity-tested |
| Finding key format & severity | `07` §1–§2 |
| Suggested fix per rule (kinds, lines, confidence) & verification loop | `07` §7 (templates) · `44` (data-dependent derivations) |
| ERP export shapes, presets, write-back journal formats | `26` §5 / §7 (D365 F&O + BC first-class, DEC-012) · `06` (transforms, quarantine reasons, enrichment, TB tie-out) |
| Dynamics 365 direct connector (pull, auth, profiles, mock, setup) | `26` §8 (DEC-013) · `12` §1(d)/§5/§8 (security envelope) · `05` connector routes · `22` ERR-110…118 · `23` §11 · `62` `connector.*` · `19` C2 (FR-CON) |
| States & transitions | `23` |
| Error codes / UI copy | `22` / `55` |
| Settings keys | `62` |
| Screens | `13` (global rules, nav) / `21` (per screen) |
| Process, gates, order | `AGENT_PROMPT.md` + `WORK_PLAN` + `86` (milestones) + `91` (ordering rules) + `33`/`34` (handbook/verification) |
| Decisions & open questions | `17` §3–§4 |

## §6 How work gets done
One agent, one prompt. The builder reads `AGENT_PROMPT.md`, takes the next startable item from `docs/WORK_PLAN.md`, reads the spec sections that item cites, writes the oracle test first, implements, self-verifies (`AGENT_PROMPT.md` §6), records the handover in `TASKBOARD.md`, commits `WI-####: <path>`. Spec gaps are fixed in the owning doc **before** code (class A/B/C rules). Milestones close with a cold audit session (`34` §2). The owner has delegated decisions (DEC-010): the builder decides class-A questions, records `DEC-nnn (auto)` in `17` §4 and proceeds; the owner reads the DEC log and may reverse any entry by editing `17` and the owning doc.

## §7 Full document list
01 PRD · 02 Data Dictionary · 03 Calculation · 04 Architecture · 05 API Contract · 06 Import · 07 Exceptions · 08 Forecast · 09 Excel · 10 PPT · 11 AI · 12 Security · 13 UI/UX · 14 Testing/Acceptance · 15 Coding Standards · 16 Packaging · 17 Roadmap/Risks/OQ-DEC · 18 User Guide · 19 Functional Spec (FR register) · 20 Traceability · 21 Screen Spec S01–S19 · 22 Error Catalogue · 23 State Machines · 24 Data Flows/ERD · 25 Threat Model · 26 ERP Field Guides · 27 Localization/Currency · 28 COA/Templates · 29 Budgeting/Planning/KPI · 30 Close Management · 31 Glossary · 32 Competitive Parity · 33 Single-Agent Execution Handbook · 34 Verification & Audit Playbook · 35 Operations/Support · 36 NFR Catalogue · 37 Perfection Register · 38 Year-End/Opening · 39 Adjustments · 40 Allocations · 41 Restatements · 42 Sample Data · 43 KPI Dictionary · 44 Rule Algorithms · 45 Statement Presentation · 46 Forecast Maths · 47 Commentary Standard · 48 Planning Calendar/Assumptions · 49 Consolidation Design · 50 FX Design · 51 User Stories/GWT · 52 Journeys · 53 Design System · 54 Wireframes · 55 Copy Catalog · 56 Onboarding · 57 Accessibility · 58 Client Questionnaire · 59 Training · 60 Dev Setup · 61 Migrations · 62 Config Reference · 63 API Cookbook · 64 Jobs · 65 Logging · 66 CI/CD · 67 Perf Test Plan · 68 Compatibility · 69 Expression Grammar · 70 Folder Structure · 71 UAT Scripts · 72 Defects/Change · 73 Internal Controls · 74 Model Risk · 75 AI Model Cards · 76 DPIA · 77 Evidence Index · 78 Test Data · 79 Pricing/Licensing · 80 Legal Pack · 81 Third-Party Notices · 82 Go-Live/Hypercare · 83 Pilot · 84 Post-Go-Live Review · 85 RACI · 86 Milestone Plan & Gates · 87 Templates · 88 AI Prompt Texts & Golden Set · 89 Fixture & Oracle Catalog · 90 API Payload Schemas (field-level) · 91 Build-Order & Dependency Spec · WORK_PLAN (generated) · MASTER_PLAN · RESEARCH_AND_LESSONS · CHANGELOG.

## §8 Where evidence lives
`evidence/` per doc 77 index: `evidence/acceptance_report.*`, `evidence/audits/M<n>_audit.md` (milestone audits), perf runs, screenshots. Planning-phase audits live in `audit/` at the repo root; the current one is `audit/BRUTAL_AUDIT_PASS3_2026-10-14.md` (supersedes the three earlier files there).

## §9 Glossary & language
`31_GLOSSARY` is the terminology source; `55` owns exact UI strings; `27` owns number/date/currency formats; period ids are always `<fiscal_year>-P<nn>` (doc 02 §2).

## §10 Current phase (keep this section updated — the builder cites it)
**Phase 0 → M0 (spec hardening), 2026-10-14.** Execution model changed to a single builder (DEC-007). Audit pass 3 found P0 contract defects in the previously "approved" doc set; the ones fixable in one pass are fixed (see CHANGELOG), the rest are the seven M0 work items of `docs/WORK_PLAN.md`. **No new product code until the M0 gate closes** (`scripts/docs_check.py` clean; DEC-007/008/009 are accepted under DEC-010 auto-decision mode, so the gate is the docs check alone). Same day, DEC-011 (28 rules, suggested fix on every finding, ERP rectification journal), DEC-012 (Dynamics 365 first-class import shapes) and DEC-013 (direct Dynamics 365 connector in v1, `26` §8) widened the spec; the work plan is regenerated from `tools/generate_work_plan.py` (item count in `TASKBOARD.md`). Existing code (core/money, calendar, errors, schema v1, 9 tests) is frozen and marked `exists-unverified` in `TASKBOARD.md`; it is re-verified against its acceptance lines in M1.
