# 17 — ROADMAP, RISKS, OPEN QUESTIONS & DECISIONS

> Owner of: phases, cut lines, risk register, OQ/DEC logs. New feature ideas land here or in the backlog section — never directly in a milestone (P6). The builder (`AGENT_PROMPT.md` §4) appends OQs with labelled defaults and DECs for every contract change; the owner reads this doc and `TASKBOARD.md` *Owner attention*.

## 1. Phases
| Phase | Content | Exit gate | Status (2026-10-14) |
|---|---|---|---|
| 0 | Documentation set (docs 00–91) complete, internally consistent, single-agent execution model in place | Pass-3 audit P0/P1 findings closed; `scripts/docs_check.py` green; owner approval of DEC-007/008 | **In progress** — audit pass 3 (`audit/BRUTAL_AUDIT_PASS3_2026-10-14.md`) found P0 defects in the "approved" set; remediation is the M0 milestone of `docs/WORK_PLAN.md` |
| 1 (v1.0) | Milestones M1–M6 of doc 86: core + store + corpus → engine (statements, 24 rules, forecast) → API + UI + planning → exports + desktop → hardening → release | Doc 14 acceptance gate + doc 16 release checklist, each with evidence in `evidence/` | Not started (code at the build pause: core/money, calendar, errors, schema v1, 9 tests) |
| 2 (v1.1–1.3) | Real-data pilot hardening; ERP connector framework (Tally/D365/QuickBooks file profiles first, APIs if demanded); contributor budget collection; passphrase DB encryption | Pilot gate (doc 14 §7) | — |
| 3 (v2.0) | Consolidation (eliminations, FX translation, NCI), multi-currency projects, macOS build | Separate PRD amendment — not implied by the v1 data model beyond not blocking it (doc 49) | — |

## 2. Risk register (owner + mitigation + trigger)
| ID | Risk | Mitigation | Early-warning trigger |
|---|---|---|---|
| R1 | Real client files differ from corpus (format drift) | Mapping profiles, malformed corpus, pilot gate before claims | Pilot import quarantine > 10% |
| R2 | Threshold defaults wrong for owner's company | All thresholds settings with doc 18 tuning guide; acceptance uses golden defaults only | Pilot findings precision complaints |
| R3 | **Single-builder risks:** (a) context loss between sessions → re-invented contracts; (b) self-certification ("my tests pass") replacing independent testing; (c) silent spec drift when the builder resolves gaps in code; (d) scope creep by the same hand that writes the plan | (a) repository-as-memory protocol (`AGENT_PROMPT.md` §2, §7), WORK_PLAN cites spec sections per item; (b) mandatory mutation checks + milestone audit sessions run cold (doc 34) + owner spot-checks; (c) class-A/B/C gap rules — doc first, OQ/DEC, never code-only; (d) scope = WORK_PLAN, backlog here | Handover without mutations/evidence; a DEC-less contract change in a diff; any item merged that is not in WORK_PLAN; two sessions touching the same contract differently |
| R4 | Excel/PPT cosmetic churn | Golden tests; "numbers tie, cosmetics iterate" | Cosmetic change requests blocking a gate |
| R5 | Scope creep (consolidation/AI forecasting asks) | §1 phases + backlog parking with phase tags | Any commit without a WI id |
| R6 | Performance on real 250k+ data on a low-end laptop | Budgets + perf gate + streaming import | Perf regression > 10% |
| R7 | Owner decisions stall the build | Labelled defaults below; defaults ship; the builder never waits on class-A questions | OQ open past its milestone gate |
| R8 | AI provider output variance | Guardrails + golden eval (doc 11 §7); AI optional | Eval < 16/20 |
| R9 | Documentation believed complete when it is not (this happened three times: BRUTAL → REMEDIATION "fixed" → PASS2 "no P0") | Audits recompute numbers and read the schema, never trust prior verdicts; M0 doc-hardening items are tested by `scripts/docs_check.py`; every oracle number in a doc is recomputed in a test | An audit that cites no recomputation |

## 3. Open questions with LABELLED DEFAULTS (the default ships unless the owner overrides; the builder appends new rows per `AGENT_PROMPT.md` §4-A)
| OQ | Question | Default (ships unless overridden) | Status |
|---|---|---|---|
| OQ-01 | Fiscal year start? | April (configurable per project) | default accepted (DEC-006) |
| OQ-02 | Reporting currency? | INR, per-project setting; single currency v1 | default accepted |
| OQ-03 | Materiality defaults? | ₹100,000 AND 5% (doc 07) | default accepted |
| OQ-04 | Suspense account identification? | Master-data tag + code prefix `1999` | default accepted |
| OQ-05 | AI provider/model? | None (off); bring-your-own key, provider-agnostic | default accepted |
| OQ-06 | Product final name/branding? | Working name stays (config-only rename, doc 01 §8) | open, non-blocking |
| OQ-07 | Code-signing certificate at go-live? | Unsigned pilot; decide before external distribution (M5) | open |
| OQ-08 | Budget grain available from client? | Coarsest grain handled per doc 03 §5–6 | default accepted |
| OQ-09 | Approval limit for split-detection? | ₹500,000 (doc 07 EXC-021) | default accepted |
| OQ-10 | Data retention of imported originals? | Kept in project `imports/` (hash-named) until the user deletes the project | default accepted |
| OQ-11 | Target Python version: 3.11 or 3.12? | **3.11+** (`pyproject` lowered from `>=3.12`; CI runs 3.11 and 3.12) — chosen because the current build host is 3.11 and nothing in the design needs 3.12 | open; default applied in M0 |
| OQ-12 | Should High-severity findings be waivable? | Yes, with reason + expiry ≤ 90 days, and the waiver is listed in the close pack (doc 23 §3) | open; default applied |
| OQ-13 | Interest in the cash-flow statement: operating or financing? | Operating (setting `calc.cf_interest_section`, doc 03 §3) | open; default applied |
| OQ-14 | Vendor codes mandatory on import? | No — vendor kept as text label unless `import.require_known_vendor` is on (doc 06 §4) | open; default applied |

## 4. Decision log (DEC) — append-only
- **DEC-001** Stack Python + FastAPI + SQLite + React (doc 04 ADR-001…008).
- **DEC-002** Windows-first, single-user, offline v1.
- **DEC-003** 24-rule catalogue with canonical finding keys (doc 07 §2).
- **DEC-004** Coherent corpus + planted acceptance as the release gate (docs 42, 14 §3).
- **DEC-005** AI edge-only / off by default (doc 11).
- **DEC-006** 2026-10-14 (owner, auto-decision mode): docs 00–88 baselined; Wave 1 build authorised on the multi-agent model. **Superseded in part by DEC-007** — the build was paused after Wave 1a/1b (core/money, calendar, errors, schema v1, 9 tests) and the "remediation verified 9/9" claim is withdrawn by audit pass 3.
- **DEC-007** 2026-10-14 (owner): **single-agent execution model.** The 500-agent packet model (317 creator + 317 tester prompts, file-disjoint waves, integrator role) is retired. One builder agent executes `docs/WORK_PLAN.md` (241 work items, milestones M0–M6, generated by `tools/generate_work_plan.py`) under `AGENT_PROMPT.md`, keeps `TASKBOARD.md`, and performs the tester/auditor roles itself through the self-verification protocol and milestone audit sessions. `agent-prompts/`, `tools/generate_agent_packets.py`, `docs/FILE_MANIFEST.*` and `docs/DEPENDENCY_GRAPH.*` are deleted; docs 33, 34, 85, 86, 91 and MASTER_PLAN §7–§12 are rewritten accordingly. Rationale: the owner now runs one most-capable agent; the multi-agent apparatus was 636 files of coordination overhead with its own defects (BLOCKED-and-wait semantics that a sole agent cannot use, prose dependency links, duplicated contracts).
- **DEC-008** 2026-10-14 (builder, pending owner veto — see TASKBOARD *Owner attention*): **acceptance bars corrected.** Recall 32/32 (was "≥ 29/31"), controls 0/10 (was 0/8; two one-leg controls added per AND-rule), High 18/18 unchanged but now enumerated; P30 converted from an undefined "control" into a real EXC-018 Medium plant that tests the escalation boundary. Rationale: the corpus is self-authored, so any missed plant is a defect; the old controls (both legs failing) could not distinguish an AND from an OR implementation — the exact attempt-#4 bug. Docs 14 §3, 42 §7–§8, 07 §4/§6, 03 §5 changed in one commit.
- **DEC-009** 2026-10-14 (builder, pending owner veto): **error catalogue extended** from 24 to 63 codes (doc 22) so every FR in doc 19 has a defined failure; ERR-025 introduced for bad amounts (money.py's reuse of ERR-021 was a defect); HTTP status mapping fixed in doc 05 §1.

## 5. Backlog (parked, phase-tagged — not in v1)
Live ERP connectors [P2] · contributor budget collection [P2] · consolidation/FX/NCI [P3] · macOS/Linux [P3] · industry packs (manufacturing/SaaS/retail calendars) [P2+] · anomaly ML scoring beyond rules [P2+, must remain explainable] · multi-user review workflow [separate product evaluation] · email/Slack push for alerts [P2] · scheduled rule runs [P2].

## 6. Change control
Spec changes after the Phase-0 freeze: one commit editing the owning doc (doc 00 §5) + every doc that repeats the fact + `docs/CHANGELOG.md` + a DEC entry here when scope/contract-affecting; if the change alters a work item, `tools/generate_work_plan.py` is edited and `docs/WORK_PLAN.*` regenerated in the same commit. Code follows in a separate commit. Emergency fixes follow the same path — there is no "code first, docs later" lane (`AGENT_PROMPT.md` §4-B).
