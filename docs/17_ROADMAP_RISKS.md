# 17 — ROADMAP, RISKS, OPEN QUESTIONS & DECISIONS

> Owner of: phases, cut lines, risk register, OQ/DEC logs. New feature ideas land here or in the backlog section — never directly in a wave (P6).

## 1. Phases
| Phase | Content | Exit gate |
|---|---|---|
| 0 | This doc set (docs 00–18) approved | Owner approval DEC recorded; tabletop walkthrough (P20) done |
| 1 (v1.0) | Waves 1–6 of MASTER_PLAN §8: full month-end spine, 24 rules, forecast, Excel/PPT/PDF, Windows installer | Doc 14 acceptance + doc 16 release checklist |
| 2 (v1.1–1.3) | Real-data pilot hardening; ERP connector framework (Tally/D365/QuickBooks file profiles first, APIs if demanded); budget authoring + contributor collection; passphrase DB encryption (ADR) | Pilot gate (doc 14 §7) |
| 3 (v2.0) | Consolidation (multi-entity eliminations, FX translation, NCI), multi-currency projects, macOS build | Separate PRD amendment — not implied by v1 data model beyond not blocking it |

## 2. Risk register (top; owner + mitigation + trigger)
| ID | Risk | Mitigation | Early-warning trigger |
|---|---|---|---|
| R1 | Real client files differ from corpus (format drift) | Mapping profiles, malformed corpus, pilot gate before claims | Pilot import quarantine > 10% |
| R2 | Threshold defaults wrong for owner's company | All thresholds settings w/ doc 18 tuning guide; acceptance uses golden defaults only | Pilot findings precision complaints |
| R3 | 500-agent variance/invented contracts | BLOCKED-not-invent rule, file-disjoint waves, independent testers | > 5% packets BLOCKED on same contract → doc fix wave |
| R4 | Excel/PPT cosmetic churn | Golden tests; "numbers tie, cosmetics iterate" | Cosmetic change requests blocking a gate |
| R5 | Scope creep (consolidation/AI forecasting asks) | §1 phases + backlog parking with phase tags | Any PR without packet id |
| R6 | Performance on real 250k+ data on low-end laptop | Budgets + perf gate + streaming import | Perf regression > 10% |
| R7 | Owner decisions stall Wave 0 | Labelled defaults below; defaults ship | OQ open past Phase-0 gate |
| R8 | AI provider output variance | Guardrails + golden eval (doc 11 §7); AI optional | Eval < 16/20 |

## 3. Open questions with LABELLED DEFAULTS (decide or defaults ship at Phase-0 freeze)
| OQ | Question | Default (ships unless overridden) |
|---|---|---|
| OQ-01 | Fiscal year start? | April (configurable per project) |
| OQ-02 | Reporting currency? | INR, per-project setting; single currency v1 |
| OQ-03 | Materiality defaults? | ₹100,000 AND 5% (doc 07) |
| OQ-04 | Suspense account identification? | Master-data tag + code prefix `1999` |
| OQ-05 | AI provider/model? | None (off); bring-your-own key, provider-agnostic |
| OQ-06 | Product final name/branding? | Working name stays (config-only rename, doc 01 §8) |
| OQ-07 | Code-signing certificate at go-live? | Unsigned pilot; decide before external distribution |
| OQ-08 | Budget grain available from client? | Coarsest grain handled per doc 03 §5–6 |
| OQ-09 | Approval limit for split-detection? | ₹500,000 (doc 07 EXC-021) |
| OQ-10 | Data retention of imported originals? | Kept in project `imports/` (hash-named) until user deletes project |

## 4. Decision log (DEC) — append-only
DEC-001 Stack Python+FastAPI+SQLite+React (doc 04 ADR-001…008). DEC-002 Windows-first, single-user, offline v1. DEC-003 24-rule catalog with canonical finding keys (doc 07 §2). DEC-004 Coherent-corpus + planted acceptance as release gate (docs 06 §7, 14 §3). DEC-005 AI edge-only/off-default (doc 11). DEC-006 **APPROVED 2026-10-14** (owner instructed auto-decision mode): docs 00-88 baselined, brutal-audit remediation verified 9/9, Wave 1 build authorised. Stack and defaults per DEC-001..005 stand.

## 5. Backlog (parked, phase-tagged — not in v1)
Live ERP connectors [P2] · contributor budget collection [P2] · consolidation/FX/NCI [P3] · macOS/Linux [P3] · industry packs (manufacturing/SaaS/retail calendars) [P2+] · anomaly ML scoring beyond rules [P2+, must remain explainable] · multi-user review workflow [separate product evaluation].

## 6. Change control
Spec changes after Phase-0 freeze: PR editing the owning doc + CHANGELOG + affected packet regeneration (`tools/generate_agent_packets.py`) + DEC entry when scope/contract-affecting. Emergency fixes follow the same path within one commit — there is no "code first, docs later" lane.
