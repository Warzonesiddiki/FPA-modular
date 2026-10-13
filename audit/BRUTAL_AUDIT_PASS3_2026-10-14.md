# BRUTAL AUDIT — PASS 3 (2026-10-14) · documentation set, plan, code stub, execution model

> **Addendum 2026-10-14 (b):** the owner delegated all pending decisions (DEC-010). The §6 items below are therefore **closed**: DEC-008/009 accepted, OQ-11…14 accepted. In the same session DEC-011 (entry-hygiene rules EXC-025…028 + rectification suggestions + ERP journal file) and DEC-012 (Dynamics 365 first-class shapes) changed the numbers quoted in this audit: acceptance bars are now **36/36 · 0/13 · 19/19** (+ suggestion exactness, ERP shape parity), rule coverage **28/28**, error catalogue **64 codes** (ERR-046 added), FR register **122**, work plan **250 items** (M0=7 M1=51 M2=75 M3=31 M4=50 M5=26 M6=10). The findings and root causes in §1–§5 stand unchanged; see `docs/CHANGELOG.md` 2026-10-14 (b) for the file-level trail.

**Scope:** every file in the repository at commit `2db2ae7` (772 files: 99 docs, 636 agent prompts, 3 audit files, 8 code/test files, sample CSV, pyproject). **Method:** read every doc; recomputed every numeric oracle with `decimal.Decimal`; diffed `docs/02` against `app/store/schema.sql` column by column; ran the test suite (`python -m pytest -q` → 9 passed, Python 3.11.2); cross-checked ids (FR, ERR, EXC, S##, OQ/DEC) across docs; checked the acceptance design against the attempt-#4 failure it claims to prevent. **Nothing in this audit relies on a prior audit's verdict.**

**Verdict:** the documentation set was **not** build-ready, contrary to `DOCS_AUDIT_PASS2` ("no P0/P1 remaining") and `REMEDIATION` ("FIXED"). Twelve P0 and fifteen P1 defects were found, of which the contract-level ones are fixed in this pass (docs only — code is frozen) and the depth-of-spec ones are converted into the seven M0 work items of `docs/WORK_PLAN.md`. The execution model has been changed to a single builder (DEC-007). **The three earlier audit files are superseded and banner-marked.**

---

## 1. Why the previous verdicts were wrong (so it does not happen a fourth time)
| Prior claim | Reality found in pass 3 | Root cause |
|---|---|---|
| REMEDIATION: "enumerated plant register … contradiction fixes — FIXED" | Doc 42 contained two copies of §5–§7, a scratch paragraph in normative text, a severity column contradicting its own §1 rule for five plants, period ids in a notation (`FY26-P07`) that doc 02 forbids, and a "control" (P30) that fires both legs of the rule it is supposed to be silent for | Fixes were written, never re-read as a stranger; no recomputation |
| PASS 2: "no P0/P1 remaining" | Doc 02 claimed "schema.sql implements this 1:1, test-enforced" while the schema had ≥12 undocumented columns, a different `periods` PK, a duplicate driver table in the doc and no `validated` state; the "schema-equality test" compared 13 table *names* | The audit trusted the doc's claim instead of opening the schema |
| Doc 14: "Every code has a test asserting message+hint" | `errors.py` lacks ERR-011, 012, 030, 080, 081, 090, 091, 099; `money.py` raises ERR-021 (file too large) for an unparseable amount; doc 22's table was broken by a row appended after its closing paragraph | Claims written as future tense were read as present tense |
| Doc 46: HW oracle "indices 0.952/1.048 … → next ŷ = 100.0" | Not derivable from the stated equations (n = 12 does not meet the doc's own n ≥ 14 minimum; with the stated init the additive model's first forecast is 105 − 5 = 100 only by coincidence of a flat series, and the "indices" belong to the multiplicative/seasonal-index method, not HW) | Oracle written from intuition, not computed |
| MASTER_PLAN/README/00_INDEX: "500-agent model, 766 assignments" | Owner decided on one agent; nothing reflected it; 636 prompt files were dead weight with their own defects (BLOCKED-and-wait semantics, prose dependencies) | Decision not propagated |

**Rule adopted (doc 17 R9):** an audit that cites no recomputation and no schema read is not an audit. Every oracle number in a doc is now also a test fixture (doc 89), so the next drift is caught by CI, not by reading.

---

## 2. P0 findings (contract-level; would have produced wrong numbers or invented contracts)
| ID | Finding | Evidence | Status |
|---|---|---|---|
| **P0-1** | **Acceptance gate could not catch the attempt-#4 bug.** Bars were "recall ≥ 29/31, controls 0/8". Both EXC-018 controls failed *both* materiality legs (e.g. 900,000 vs 880,000: +20,000 / +2.27 %), so an OR-implementation (the exact attempt-#4 defect) passes them. On a self-authored corpus "≥ 29/31" tolerates two unexplained misses. P30 was called a control but its own numbers fire the rule. | Recomputed: abs ₹100,000 / 5 % → 900,000 vs 880,000 fails abs **and** pct. New C02 10,150,000 vs 10,000,000 → abs pass/pct fail; new C09 260,000 vs 200,000 → abs fail/pct pass; C04/C10 likewise for EXC-013. | **FIXED** — doc 14 §3 (32/32, 0/10, 18/18, severity exactness), doc 42 §7–§8, doc 07 §4/§6, doc 03 §5 six-case oracle. **DEC-008, owner may veto.** |
| **P0-2** | **Doc 42 corrupted.** Duplicate §5–§7; scratch paragraph; Sev column said Medium for P12/P14/P17/P20/P21 while §1 escalation and the High-count (18) require High; `FY26-P07` notation; weak/undefined controls. | File read; High count without the five = 13 ≠ 18. | **FIXED** — doc 42 rewritten; 18 High enumerated and asserted by generator test. |
| **P0-3** | **Prior audit verdicts false** (see §1). | — | **RECORDED**; files banner-marked superseded; CHANGELOG annotated. |
| **P0-4** | **FR register was ten ids** (FR-PRJ-001…004, FR-MDM-001…003, FR-CAL-001…007 inline) for ~120 behaviours; doc 01 cited `FR-IMP-09` which did not exist; doc 20 matrix family-level with "packets" columns. | grep of `FR-[A-Z]+-[0-9]+` across docs. | **FIXED** — doc 19 rebuilt: 114 numbered FRs, each with rule/errors/screen/API/test; doc 01 → `FR-IMP-010`; doc 20 header maps families → ranges. FR-level matrix = **WI-0007** (M0). |
| **P0-5** | **Doc 02 ≠ `schema.sql`** while claiming 1:1 test enforcement: undocumented `projects.currency_exponent`, `accounts.tags/ic_counterparty_entity_id`, `cost_centres.entity_id`, `vendors.linked_entity_id`, `gl_rows.fx_currency/fx_amount_minor/fx_rate/layer`, `driver_values.assumption_id/version`, `audit_log.canonical`, `finding_comments`; `periods` PK composite in schema, single in doc; doc listed `planning_drivers` **and** `driver_values` for the same data; no `validated` batch state anywhere in schema; `created_by` promised on every table, present on two; `test_store.py` checks 13 table names. | Column diff (schema lines 3–11, 15–30, 37–55, 62–66, 75–84, 96–99). | **Doc FIXED** (02 §1/§2/§5 + new §7 delta list). Schema v2 + column-level equality test = **WI for `app/store/schema.sql`** (M1). |
| **P0-6** | **Execution model obsolete**: owner moved to a single agent; MASTER_PLAN §7–§12, README, 00_INDEX §2/§6, docs 33/34/85/86/91 and 636 prompt files described a 500-agent dispatch with BLOCKED-and-wait, prose deps, integrator role. | Owner instruction; file counts. | **FIXED** — `AGENT_PROMPT.md`, `docs/WORK_PLAN.*`, `TASKBOARD.md`, generator; docs rewritten; apparatus deleted. **DEC-007.** |
| **P0-7** | **Error catalogue unusable as a contract**: table broken (ERR-042 after the closing paragraph), 24 codes for ~60 failure modes (no code for: locked-period import, unsafe file, invalid drill key, bad request field, idempotency conflict, year-end failure, restatement, headcount negative, forecast articulation, locked run edits, KPI expression, settings range, licence expiry, DB busy/disk full, AI provider unreachable…); `errors.py` missing 8 of the 24; `money.py` reuses ERR-021. | doc 22 read; `grep ERR- app/core/errors.py`; `money.py:32`. | **Doc FIXED** — 63 codes, numbering scheme, parity rule, ERR-025 for bad amounts (**DEC-009**). Code = **WIs for `errors.py`, `money.py`** (M1). |
| **P0-8** | **API contract not implementable**: no HTTP status mapping; routes mixed `/projects/{id}/…` with bare `/imports/{batch_id}` without a scoping rule; planning/budget/report-builder/KPI-builder endpoints existed only as a prose sentence in doc 29 §10; no job-result schema per job kind; doc 90 had a malformed `AdjustmentCreate` and mapped unknown fields to ERR-001 (not found). | docs 05, 29 §10, 90. | **Partially FIXED** — doc 05 §1 (status mapping, scoping rule, job results, job list), §4 (planning/budgets/KPI-builder/diagnostics rows), doc 90 fixes. OpenAPI-grade rewrite = **WI-0001** (M0). |
| **P0-9** | **Calculation spec silent or wrong on things the engine must do**: §3 rounding said "residual to the largest line" while `money.py` implements largest-remainder; no CF classification (which line keys are operating/investing/financing, with signs); no retained-earnings roll; no KPI balance basis (closing vs average) or precision; BvA oracle set could not discriminate AND/OR. | doc 03 vs `money.py` `largest_remainder_allocate`. | **FIXED** — doc 03 §3 (CF table by doc 45 keys, RE roll, movement BS, largest-remainder), §4 (basis, 2 dp, n/a), §5 (six cases). Remaining depth (phasing oracles, bridge at sub-group grain) = **WI-0004** (M0). |
| **P0-10** | **Forecast oracles wrong/underivable**: HW fixture (see §1); Holt oracle said "l4, b4 recorded in fixture" with no numbers anywhere; doc 08 said `seasonal` < 24 → `not_run` while doc 46 said "falls back to naive-seasonal". | Recomputed Holt: l₂ 110/b₂ 10; l₃ 115.5/b₃ 9.55; l₄ 122.035/b₄ 9.2485; ŷ₅ 131.2835; ŷ₆ 140.532. HW on [100,110]×12 (n = 24) is a fixed point → 100/110/100 for all (α,β,γ). | **FIXED** — docs 46, 08, 89 §3 (`holt_basic`, `hw_flat`, `seasonal_short`). |
| **P0-11** | **Screen spec not implementable**: 19 screens at ≈ 40 words each in doc 21; doc 13 navigation rail omitted Close, Planning, Reconcile, Alerts (S16–S19) although doc 20 declared them. | docs 13 §1, 21. | Nav rail **FIXED** (doc 13). Per-screen sections = **WI-0002** (M0). |
| **P0-12** | **Rule algorithms depended on inputs that did not exist**: "spend" undefined (sign convention for revenue accounts?); EXC-008 "is_manual flag from import profile" — no such column; EXC-005 "period lock log" — no such table; EXC-023 "system balancing leg (import tag)" — no such tag; short-history behaviour defined for EXC-015 only. | doc 44 vs doc 02/schema. | **FIXED** — doc 44 §0 (spend, manual journal = `import_batches.is_manual` ∨ `rule.manual_prefixes`, tags incl. `accrual_balancing`, lock evidence = `committed_at > periods.locked_at`, per-rule history minimums, boundary semantics); doc 02 columns added. Parameter tables + evidence schemas = **WI-0003** (M0). |

## 3. P1 findings (divergence or missing evidence; fix before the M1 gate)
| ID | Finding | Status |
|---|---|---|
| P1-1 | Doc 03 §5 "non-material" oracle failed both legs (same defect as P0-1 at unit level) | **FIXED** (six-case table, fixture `bva_basic` in doc 89) |
| P1-2 | KPI precision undefined; doc 43 said EBITDA margin 18.0 % (actual 17.95 %), net 10.9 % (10.93 %), opex 19.5 % (19.53 %) | **FIXED** (doc 03 §4: 2 dp ROUND_HALF_UP; doc 43 values recomputed) |
| P1-3 | Doc 43: nine KPI rows said "per fixture" — no oracle existed | **FIXED** — computed from `bs_basic` lines now fully specified in doc 89 §1 (DPO 13.60, DIO 7.18, WC days −0.75, current 0.78, quick 0.59, Debt/EBITDA 0.26, ROCE 272.45 % annualised, interest cover n/a, Capex/D&A 2.56) |
| P1-4 | Two cash-flow worlds (`cf_basic`: capex 640,000, ΔCash 320,000 vs doc 29 §7: capex 400,000, ΔWC −64,200, ΔCash 480,000) with the same P&L, mixed in doc 43 | **FIXED** — named `cf_basic` vs `integrated_basic`; never mixed in one fixture |
| P1-5 | `tests/integration/test_month_end_spine.py` asserts TB balance tautologically (sum of signed rows it just inserted); `test_store.py` is a 13-name subset | Code frozen → **WIs** for both tests (M1), acceptance lines require column-level equality and an imbalance case |
| P1-6 | Batch crash state: doc 06 "stays `staged`" vs doc 23 "stays `validated`" | **FIXED** (`validated`, both docs + doc 02) |
| P1-7 | Doc 44 lacked parameter tables (setting key/type/default/range), `evidence_json` schema, grain-key derivation per rule | §0 added; rest = **WI-0003** |
| P1-8 | Doc 17: DEC-006 "Wave 1 authorised" vs README "build paused"; no DEC for the pause; Phase-0 row stale; R3 about 500-agent variance | **FIXED** (phase table with status, R3/R9, DEC-006 partially superseded, DEC-007/008/009, OQ-11…14) |
| P1-9 | CHANGELOG not in date order; 00_INDEX said "01–87" with 91 docs; README said 766 assignments | **FIXED** |
| P1-10 | `pyproject.toml` `requires-python >= 3.12` while the build host runs 3.11.2; version ranges unpinned; no lockfile | **OQ-11** (default 3.11+); **WI for `pyproject.toml`** (M1) adds lock + CI matrix |
| P1-11 | Doc 91 claimed "machine-checkable dependencies" but the old generator held prose deps and the graph was derived by string lookup; nothing asserted acyclicity | **FIXED** — new generator resolves every dependency to WI ids and fails on unresolved/cyclic/cross-milestone deps. First strict run found **3 cycles** (doc 21 ↔ doc 55; forecast/engine ↔ scenarios/rolling via `forecast/*`), **1 cross-milestone dep** (M1 harness → M2 rules engine) and **22 unresolved references**; all corrected in the generator |
| P1-12 | Doc 55 copy catalogue incomplete (per-screen mandatory keys only) | **WI-0005** (M0) |
| P1-13 | Doc 31 glossary ≈ 30 terms | **WI-0006** (M0) |
| P1-14 | Docs 09/10: sheet-level cell maps and slide data bindings thin (sheet names + prose) | Open; M5 export items carry acceptance lines "golden cell map / slide map per doc 89 §6" — the builder must deepen 09/10 under the class-B rule before the first export item |
| P1-15 | Import: no quarantine reason for unknown cost centre/vendor; unsafe-file handling (zip bomb, traversal) had no error code | **FIXED** (doc 06 §1/§4, ERR-029) |

## 4. P2 findings (quality; fix opportunistically, tracked here)
- 43 of 99 docs had no numbered sections; average depth ≈ 480 words/doc; thin: 24, 25, 36, 40, 50, 53, 61, 69, 71 (not blocking: each has a consuming WI whose acceptance line forces the detail to exist before code).
- Doc 90 syntax leftovers (`AdjustmentCreate{… , }`) — fixed; unknown-field error code — fixed (ERR-002).
- Period notation drift (`FY26-P07`, `FY27`) in docs 42, 89 — fixed; `scripts/docs_check.py` (M6 WI) will enforce `<fy>-P<nn>`.
- `.gitignore` does not exclude `evidence/**/*.xlsx` scratch; `sample-data/gl_sample.csv` is the only data file and is fine.
- Wording: "error/fraud" never appears in finding copy (checked); "tester/integrator/packet/wave" purged from 30 docs.

## 5. What is fixed in this pass vs what is open
**Fixed now (docs only; 44 files changed, 642 deleted):** P0-1, 2, 3, 4 (register), 6, 7 (doc), 9, 10, 12; P1-1, 2, 3, 4, 6, 8, 9, 11, 15; P2 items above. Full list in `docs/CHANGELOG.md`.

**Open, with owner (WI id in `docs/WORK_PLAN.md`):**
| Open item | WI | Milestone |
|---|---|---|
| OpenAPI-grade API contract (P0-8) | WI-0001 `docs/05_API_CONTRACT.md` | M0 |
| Per-screen sections S01–S19 (P0-11) | WI-0002 `docs/21_SCREEN_SPEC_DETAILED.md` | M0 |
| Rule parameter tables + evidence schemas (P0-12/P1-7) | WI-0003 `docs/44_RULE_ALGORITHMS_DETAILED.md` | M0 |
| Remaining calc oracles (P0-9) | WI-0004 `docs/03_CALCULATION_SPEC.md` | M0 |
| Copy catalogue (P1-12) | WI-0005 `docs/55_COPY_AND_MICROCOPY_CATALOG.md` | M0 |
| Glossary (P1-13) | WI-0006 `docs/31_GLOSSARY.md` | M0 |
| FR-level traceability matrix (P0-4) | WI-0007 `docs/20_TRACEABILITY_MATRIX.md` | M0 |
| Schema v2 = doc 02 columns; column-level equality test (P0-5, P1-5) | `app/store/schema.sql`, `tests/unit/test_schema.py` | M1 |
| `errors.py` complete; `money.py` ERR-025 (P0-7) | `app/core/errors.py`, `app/core/money.py` | M1 |
| Python 3.11+, lockfile (P1-10) | `pyproject.toml` | M1 |
| Export cell/slide maps (P1-14) | class-B before first `app/exports/*` item | M5 |

## 6. Decisions needed from the owner (all have defaults; silence = default at the M1 gate)
1. **DEC-008** — exact acceptance bars (32/32, 0/10, 18/18). Alternative: keep "≥ 29/31" (not recommended: on a self-authored corpus a miss is a defect).
2. **DEC-009** — error catalogue 63 codes / ERR-025. Alternative: fewer codes with `details` discrimination (not recommended: codes drive copy, status and tests).
3. **OQ-11** Python 3.11+ · **OQ-12** High findings waivable ≤ 90 d · **OQ-13** CF interest in operating · **OQ-14** vendor codes optional on import.
4. **DEC-007** is the owner's own instruction (single agent); recorded for the log.

## 7. Verification trail (commands run in this pass)
```
python -m pytest -q                                  # 9 passed (frozen code)
python tools/generate_work_plan.py                   # 241 items; M0=7 M1=51 M2=67 M3=31 M4=50 M5=25 M6=10; 0 generator defects after fixes
python - <<EOF  (Decimal recomputations: Holt, HW fixed point, BvA six cases, KPI table, bs_basic/pl_basic/cf_basic tie-outs)  EOF
grep -rn "agent-prompts|FILE_MANIFEST|DEPENDENCY_GRAPH|PKT-|TST-|tester agent|integrator" --include=*.md --include=*.py .   # only historical mentions remain (DEC-006/007 text, CHANGELOG, doc 86 §4)
```
Tie-outs: pl_basic opex split 620,000+180,000+140,000+120,000+90,000+90,000 = 1,240,000 ✓ · bs_basic 3,850,000 + 4,920,000 = 8,770,000 = 4,950,000 + 2,000,000 + 1,820,000 ✓ · cf_basic 1,480,000 − 640,000 − 520,000 = 320,000 = 1,400,000 − 1,080,000 ✓ · KPI values as listed in doc 43 (2 dp) ✓.

*Next audit: the M0 gate audit session (doc 34 §2), written by the builder as a stranger, into `evidence/audits/M0_audit.md`.*
