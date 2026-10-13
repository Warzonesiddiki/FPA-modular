# 37 — MISSING DOCS & PERFECTION REGISTER (gap audit, 2026-10-14)

> Audit of docs 00–36 + MASTER_PLAN against "absolute perfection, zero compromise". **STATUS 2026-10-14: all 50 docs below have been WRITTEN (docs 38–87).** This register remains as the audit trail + the checklist the docs-traceability audit stream signs against (doc 34 stream J). Priority: **P0** = blocks M1 (build on sand without it) · **P1** = blocks its feature milestone · **P2** = blocks release · **P3** = blocks pilot/commercial/Phase-2. Proposed numbering continues 38+.

## A. FP&A domain depth — the biggest holes (finance correctness)
| # | Proposed doc | Why fatal if missing | P |
|---|---|---|---|
| 38 | `38_YEAR_END_AND_OPENING_BALANCE_SPEC` | Nothing today says how BS balances roll FY→FY, P&L closes to retained earnings, or opening imports reconcile. Every multi-year user hits this in month 13. | P0 |
| 39 | `39_MANAGEMENT_ADJUSTMENTS_SPEC` | Analysts make top-side/management adjustments that must NOT rewrite GL. No adjustment layer, audit separation, or reversal spec exists — without it users corrupt source truth or do it in Excel. | P0 |
| 40 | `40_COST_ALLOCATION_SPEC` | Overhead/shared-cost allocation (drivers, step-down, reciprocal-lite) is core FP&A; entirely absent. | P1 |
| 41 | `41_RESTATEMENT_AND_RECLASSIFICATION_SPEC` | Prior-period restatements, reclasses, comparative recasting, and what happens to locked periods/forecasts. Absent → first restatement breaks history. | P0 |
| 42 | `42_SAMPLE_DATA_SPEC` | Corpus is only ~15 lines (06 §7). Needs full design: companies, COA, 24 months, seasonality, every plant mapped to rule/answer-key, malformed set, regeneration proof. K2 (attempt-#4 killer) lives here. | P0 |
| 43 | `43_KPI_DICTIONARY_DETAILED` | 29 lists 30+ KPIs in one line each. Each needs formula, grain, source fields, interpretation, RAG thresholds, worked fixture. | P1 |
| 44 | `44_RULE_ALGORITHMS_DETAILED` (appendix to 07) | 07 gives one-line logic per rule. Each rule needs pseudocode, parameter table, grain/key derivation, boundary cases (±1 minor unit), false-positive design notes. K3 lives here. | P0 |
| 45 | `45_STATEMENT_PRESENTATION_AND_MAPPING_SPEC` | Account→statement-line rules, subtotal definitions, sign map, grouping, "what if unmapped" behaviour — currently implicit in 03. | P0 |
| 46 | `46_FORECAST_MATHEMATICS_APPENDIX` | Holt-Winters equations, initialisation, grid search, seasonality with <24 months, driver formula registry math. 08 names methods; the math the builder must implement exactly is not written. | P1 |
| 47 | `47_VARIANCE_COMMENTARY_AND_REPORTING_STANDARD` | What a good commentary/board narrative contains (structure, materiality ordering, wording, examples good vs bad). AI (11) and humans both need this standard. | P1 |
| 48 | `48_PLANNING_CALENDAR_AND_ASSUMPTIONS_REGISTER_SPEC` | Annual budget cycle calendar, assumption ownership/versioning/approval, assumption→driver→forecast lineage. 29 has mechanics, not governance. | P1 |
| 49 | `49_INTERCOMPANY_AND_CONSOLIDATION_DESIGN` (Phase-3 design, written now) | "Not blocking it later" (01) is currently a hope. Entities/IC accounts data design must be reserved in v1 schema or Phase 3 becomes a rewrite. | P1 |
| 50 | `50_FX_AND_MULTI_CURRENCY_DESIGN` (Phase-3 design, written now) | Same: currency fields/translation design reserved now, built later. | P1 |

## B. Product & user depth
| # | Proposed doc | Why | P |
|---|---|---|---|
| 51 | `51_USER_STORIES_AND_ACCEPTANCE_CRITERIA` | 19 has FR statements; no per-FR user stories/Given-When-Then. Verification needs GWT to test against. | P0 |
| 52 | `52_USER_JOURNEYS_AND_USE_CASES` | End-to-end narratives (first month, month 2, restated month, owner correction loop, CFO challenge) — the tabletop (P20) needs scripts. | P0 |
| 53 | `53_DESIGN_SYSTEM_AND_COMPONENT_SPEC` | 13 names components; no visual spec (spacing, type scale, colour values, dark/light, charts palette, icon set). Without it 19 screens look like 19 products. | P1 |
| 54 | `54_WIREFRAMES_AND_PROTOTYPE_SPEC` | Layout per screen (zones, hierarchy, table densities). Text tables in 21 are not layouts. | P1 |
| 55 | `55_COPY_AND_MICROCOPY_CATALOG` | Every button/empty/error/tooltip string in one reviewed catalog (incl. finding-name plain-language names for 28 rules). Copy invented per-screen drifts and can accuse ("error/fraud" ban). | P1 |
| 56 | `56_ONBOARDING_AND_FIRST_RUN_SPEC` | First-run wizard steps, sample-data tour, empty-project path, migration from Excel checklist. 13 §5 is a paragraph. | P1 |
| 57 | `57_ACCESSIBILITY_CONFORMANCE_SPEC` (VPAT/ACR-style) | 13 states WCAG AA; no per-criterion conformance table, keyboard maps per screen, screen-reader announcements for charts/tables. | P2 |
| 58 | `58_CLIENT_ONBOARDING_QUESTIONNAIRE` | The discovery instrument (ERP, FY, COA, grain, thresholds, owners) that turns OQ defaults (17) into a real client's answers before pilot. Attempt #4 had this; we dropped it. | P1 (pilot P3) |
| 59 | `59_TRAINING_PLAN_AND_MATERIALS` | Analyst enablement: curriculum, exercises on sample data, competency check. Product nobody is trained on gets abandoned (P7). | P2 |

## C. Engineering depth
| # | Proposed doc | Why | P |
|---|---|---|---|
| 60 | `60_DEVELOPER_SETUP_AND_CONTRIBUTING` | Exact env, toolchain versions, how to run gates, PR flow for humans joining. The builder has WORK_PLAN items; humans joining have nothing. | P0 |
| 61 | `61_DATABASE_MIGRATION_AND_VERSIONING_SPEC` | 15/16 mention append-only migrations; no numbering, downgrade, fixture, or failure-recovery spec. First upgrade will improvise on user data. | P0 |
| 62 | `62_CONFIGURATION_REFERENCE` | Every setting/threshold/flag: key, type, default, range, impact, where stored. Settings are currently scattered across 07/13/29. | P1 |
| 63 | `63_API_EXAMPLES_AND_PAYLOAD_COOKBOOK` | 05 is tables; needs full example request/response per endpoint incl. error bodies, pagination, job polling. UI items will guess payloads otherwise. | P0 |
| 64 | `64_JOB_AND_BACKGROUND_PROCESS_SPEC` | Job registry semantics: progress, cancel, resume, crash recovery, concurrency limits. Referenced everywhere, specified nowhere. | P1 |
| 65 | `65_LOGGING_AND_DIAGNOSTICS_SPEC` | Log format, levels, redaction rules, rotation, diagnostics bundle manifest. 12 §5 is principles only. | P1 |
| 66 | `66_CI_CD_PIPELINE_SPEC` | Branch protection, exact CI stages, artefacts, secrets handling, environment matrix. 14/16 assume it. | P1 |
| 67 | `67_PERFORMANCE_TEST_PLAN` | 36 gives budgets; no datasets, hardware protocol, measurement method, or regression triage. Unmeasurable NFRs get quietly dropped (K5). | P1 |
| 68 | `68_COMPATIBILITY_MATRIX` | Windows builds, Excel/PowerPoint/LibreOffice versions, file-format variants tested. "Works with Excel" is currently untested scope. | P2 |
| 69 | `69_EXPRESSION_GRAMMAR_SPEC` (KPI/report builder) | 19J mentions a safe grammar; no EBNF, function list, or error model. Security-relevant (25) — must be formal. | P1 |
| 70 | `70_FILE_AND_FOLDER_STRUCTURE_SPEC` | Project folder/app data layout, naming, cleanup, what is safe to delete/share. Partially in 04 §5 only. | P1 |
| — | *Dynamics 365 direct connector* (DEC-013, 2026-10-14) | Deliberately **not** a new numbered doc: the normative spec is doc 26 §8 (products, auth, profiles, pull protocol, security, mock, IT setup) with its contract pieces in their owning docs — 05 (routes), 90 (schemas), 63 (examples), 02 (tables), 12/25 (security), 22 (ERR-110…118), 23 §11 (states), 62 (`connector.*`), 64 (job), 65 (logs), 19 C2 (FR-CON), 14 §3 (parity bar), 89 §4b (fixtures), 18 §8 (admin setup). A separate doc would duplicate owners. | done |

## D. Quality, audit & governance
| # | Proposed doc | Why | P |
|---|---|---|---|
| 71 | `71_UAT_SCRIPTS` | Step-by-step UAT cases (actor, data, steps, expected) for owner sign-off. 14 §7 describes UAT; nobody can execute it as written. | P2 |
| 72 | `72_DEFECT_AND_CHANGE_MANAGEMENT` | Defect lifecycle/severities, RFC template, DEC/ADR templates, baseline rules. 17 §6 is 4 lines. | P1 |
| 73 | `73_INTERNAL_CONTROLS_MATRIX` | Control per process (import, lock, waive, export) — who/what prevents & detects error; single-user SoD limitation disclosed formally. Auditors/CFOs will ask. | P2 |
| 74 | `74_MODEL_RISK_AND_VALIDATION_SPEC` | Forecast/goal-seek model governance: validation, backtest evidence, change control for methods/thresholds. Finance models without MRM get rejected by serious CFOs. | P2 |
| 75 | `75_AI_MODEL_CARD_AND_PROMPT_REGISTRY` | Per-prompt model card: purpose, payload, eval results, known limits, version history. 11 specifies behaviour; registry is the audit artefact. | P2 |
| 76 | `76_PRIVACY_IMPACT_ASSESSMENT_DPIA` | Even local tools process employee/vendor names. Lawful basis, minimisation proof, retention. | P2 |
| 77 | `77_EVIDENCE_AND_AUDIT_ARTIFACT_INDEX` | Where every gate's evidence lives, naming, retention. 34 demands evidence; no index means it scatters. | P1 |
| 78 | `78_TEST_DATA_MANAGEMENT_SPEC` | Fixture governance: synthetic-only rule, anonymisation if real data ever used for pilot, fixture versioning. | P1 |

## E. Commercial, legal & launch (needed before anyone pays/uses it for real)
| # | Proposed doc | Why | P |
|---|---|---|---|
| 79 | `79_PRICING_AND_LICENSING_SPEC` | Model (one-time/perpetual/trial?), licence keys/offline activation, grace, transfer. Attempt #2 spec'd this; we have OQ only. | P3 |
| 80 | `80_LEGAL_PACK` (EULA + privacy notice + advisory terms) | Shipping software with financial advice-adjacent outputs without terms is exposure. | P2 |
| 81 | `81_THIRD_PARTY_NOTICES_AND_LICENCE_COMPLIANCE` | OSS licence inventory/process (SBOM exists in 16; the legal artefact doesn't). | P2 |
| 82 | `82_GO_LIVE_AND_HYPERCARE_RUNBOOK` | Go-live day sequence, rollback triggers, hypercare staffing, exit criteria. 16 is build-side only. | P2 |
| 83 | `83_PILOT_PLAN` | Pilot client selection, anonymised data protocol, success/exit criteria, conversion to paid. 14 §7 is a paragraph. | P3 |
| 84 | `84_POST_GO_LIVE_REVIEW_TEMPLATE` | 30/60/90-day review: adoption, close-cycle-days trend, defect themes → backlog. Closes the "army replacement" promise with measurement. | P3 |
| 85 | `85_RACI_AND_PROJECT_GOVERNANCE` | Owner/builder/support decision rights; who can approve DEC, cut scope, sign releases. | P1 |
| 86 | `86_WBS_AND_AGENT_WAVE_PLAN_DETAILED` | MASTER_PLAN milestones at month level; needs item-level WBS with dependencies/order. (Now: generated `docs/WORK_PLAN.*` with resolved dependency ids; doc 86 = milestones/gates.) | P0 |

## F. Templates pack (one doc, many artefacts)
| # | Proposed doc | Contents | P |
|---|---|---|---|
| 87 | `87_TEMPLATES_PACK` | ADR, DEC, RFC, defect report, UAT sign-off, release sign-off, audit report, handover, pilot report, post-go-live review — fill-in templates so every artefact is uniform. | P1 |

## What is NOT missing (verified present, do not duplicate)
Money/rounding (03), canonical finding keys (07 §2), coherent-corpus principle (06 §7 — but see #42), acceptance bars (14 §3), threat model (25), state machines (23), error catalogue (22), ERP presets (26), competitive positioning (32).

**Count: 50 proposed docs (38–87).** Recommended execution: P0 set (38,39,41,42,44,45,51,52,60,61,63,86 + this register's approval) **before M1 code**; P1 with their milestones; P2 before release gate; P3 before pilot/commercial launch.
