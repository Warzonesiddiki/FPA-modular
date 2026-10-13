# 19 — DETAILED FUNCTIONAL SPECIFICATION (FR Register)

> Every functional requirement in the product, numbered `FR-<FAM>-<nnn>`. PRD (01) owns scope; this doc owns the behavioural register; the owning doc named in each row owns the detail (formula, states, copy). **Any FR not here must not be built; any row here must have a work item in `docs/WORK_PLAN.md` and a test** (doc 20 is the matrix). Column key: *Rule* = processing rule in one line (detail in the owning doc §), *Err* = error codes (doc 22), *Scr* = screens (doc 13/21), *API* = doc 05 route group, *Test* = paired test (doc 89 / WORK_PLAN acceptance line). IDs are stable: never renumber; retire with `(retired, DEC-nnn)`.

## A. Projects & periods (FR-PRJ) — owner docs 02, 23, 12
| ID | Statement | Rule | Err | Scr | API | Test |
|---|---|---|---|---|---|---|
| FR-PRJ-001 | Create project | name, base currency (+exponent), FY start month, calendar type → project folder, DB, default thresholds (07 §1), COA template (28) | ERR-010 | S02 | projects | project_repo |
| FR-PRJ-002 | Sample project | generated from the corpus (42), flagged `is_sample`, deletable, never mixed with real data | — | S02 | projects | e2e sample load |
| FR-PRJ-003 | Period lifecycle | periods auto-created per FY; `open→closing→locked→(unlock)→closing` (23 §1); lock blocked by open High findings unless `force`+note (audited); unlock requires note; locked period rejects postings (EXC-005) | ERR-011 | S13, S16 | periods lock | period_repo, routes_projects |
| FR-PRJ-004 | Backup / restore | zip of DB+imports+manifest with SHA-256; restore verifies hash and audit chain before opening (12 §2) | ERR-012 | S13 | backup/restore | test_backup |
| FR-PRJ-005 | Delete project | typed-name confirmation; folder moved to trash dir then purged after 30 days (12 §2) | — | S02 | projects | project_repo |
| FR-PRJ-006 | Multi-entity & consolidation view (v1) | entities within one project; statements/BvA/KPI per entity or `all` (simple sum, same currency); IC/FX reserved (49 §2) | — | S06 | statements?entity_id | statements |
| FR-PRJ-007 | Fiscal calendar | `calendar.py`: 4-4-5 or calendar months, FY start any month, period ids `<fy>-P<nn>`, prior-year/prior-period helpers | ERR-026 | — | — | test_calendar |

## B. Master data (FR-MDM) — owner docs 28, 02 §2
| ID | Statement | Rule | Err | Scr | API | Test |
|---|---|---|---|---|---|---|
| FR-MDM-001 | CRUD entities/accounts/cost centres/vendors/owners | code unique per project; deactivate, never delete once referenced; `effective_from` versions | ERR-050 | S12 | master/* | master_repo |
| FR-MDM-002 | Account metadata | account_type, statement_line (45 §1), normal_side, tags (closed list 02 §2), owner with validity window | ERR-051 | S12 | master/accounts | master_repo |
| FR-MDM-003 | Import master data from CSV | same quarantine discipline as doc 06; unknown-code resolution during GL import creates master rows only with analyst confirmation | 06 reasons | S04, S12 | imports source_kind=masters | import_masters |
| FR-MDM-004 | COA template & suggestions | doc 28 template applied on create; mapping suggestions for new accounts by code range + name tokens | — | S12 | master/accounts/suggest | test_coa_template |
| FR-MDM-005 | Owner directory | owners with email (export only, no SMTP), default owner per cost centre/account | — | S12 | master/owners | master_repo |

## C. Import (FR-IMP) — owner doc 06
| ID | Statement | Rule | Err | Scr | API | Test |
|---|---|---|---|---|---|---|
| FR-IMP-001 | Stage file | copy to `imports/<sha256>.<ext>`, raw rows verbatim with sheet + 1-based row no; max 200 MB / 1M rows | ERR-020, ERR-021 | S03 | imports POST | parser tests |
| FR-IMP-002 | Profile columns | type guess, null %, distinct count, 5 escaped samples | — | S03 | imports GET | profiler |
| FR-IMP-003 | Map columns | saved profile auto-applies on header match; deterministic ranked suggestions; AI may reorder only (11 §1); analyst confirms | ERR-022 | S04 | mapping-profiles | mapping |
| FR-IMP-004 | Versioned mapping profiles | profile = version row; month-2 reuse default path | — | S04 | mapping-profiles | mapping_profiles |
| FR-IMP-005 | Transform | debit/credit pairs → signed amount; sign_flip; dates per declared format (ambiguous → quarantine); amounts via money.py (separators, parentheses, symbols) | 06 §4 | S04 | validate | transform |
| FR-IMP-006 | Validate & quarantine | per-row rules 06 §2.5; closed reason list 06 §4; `in = valid + quarantined` everywhere | — | S05 | validate, quarantine | validation |
| FR-IMP-007 | Control totals | declared count/debit/credit vs staged; mismatch blocks commit, staging kept | ERR-023 | S05 | commit | commit |
| FR-IMP-008 | Atomic commit | single transaction, 1,000-row multi-insert; crash → rollback, batch stays `validated`; audit row | ERR-025 (amount) | S05 | commit | commit + kill test |
| FR-IMP-009 | Idempotent re-import | same file hash + period → previous batch `superseded`, replaced atomically; row count never doubles | — | S05 | commit | idempotency |
| FR-IMP-010 | Trial-balance gate | per entity Σ = 0 (03 §2); failure drills to account; analysis screens blocked until balanced or waived with audited note | ERR-024 | S05, S06 | commit, statements | tb_gate |
| FR-IMP-011 | Overlap & duplicate report | within-file exact dupes keep-one/keep-all (audited); cross-batch overlap counted before commit, routed to EXC-002 | — | S05 | imports GET | overlap |
| FR-IMP-012 | Sheet accounting (XLSX) | every sheet listed as used/skipped; formula cells use cached value, flagged; missing cache → quarantine | — | S03 | imports GET | xlsx tests |
| FR-IMP-013 | Resume & discard | each stage persisted; wizard resumable after restart; discard deletes staging with audit | — | S03–S05 | discard | pipeline_resume |
| FR-IMP-014 | Source kinds | `gl`, `budget`, `subledger`, `drivers`, `opening`, `masters` share the pipeline; kind-specific required fields (02 §4) | ERR-020 | S03 | imports | per-kind fixtures |
| FR-IMP-015 | Malformed corpus conformance | each file in 42 §5 yields exactly its `expected.json` counts | — | — | — | test_malformed |
| FR-IMP-016 | Vendor enrichment from AP sub-ledger | post-commit, GL rows without vendor matched 1:1 on (voucher_no, posting_date) to the period's AP batch receive vendor_id with `vendor_source=ap_match`; column-sourced vendors never overwritten; ambiguous/unmatched counted (06 §2.9) | ERR-001 | S03, S05 | imports/{id}/enrich | test_enrichment + erp_shapes parity |
| FR-IMP-017 | Trial-balance tie-out | `tb_check` source kind: per-account ERP movement vs committed GL; differences listed; attachable to a staged batch as per-account control totals (06 §2.6); zero differences flips the close item (30) | ERR-023, ERR-030 | S05, S16 | tb-check, control-file | test_tb_check |
| FR-IMP-018 | Posting-layer scope | rows whose posting layer ∉ `import.posting_layers` (default `Current`) quarantined `OUT_OF_SCOPE_LAYER` with the layer name; setting per project | — | S04, S05 | validate | test_validation (layer) |
| FR-IMP-019 | Segmented-account and conditional transforms | closed transform list 06 §2.4 incl. `split:<field>:<n>` (raw string kept in `source_account_ref`), `conditional:<col>=<value>`, `constant:`; D365 F&O/BC presets (26 §5) map with zero manual edits on the corpus ERP shapes | ERR-022 | S04 | mapping-profiles | test_transform + preset fixtures |

## C2. Dynamics 365 connector (FR-CON) — owner doc 26 §8 (DEC-013); security doc 12 §1(d)/§5; errors doc 22 `11x`
| ID | Statement | Rule | Err | Scr | API | Test |
|---|---|---|---|---|---|---|
| FR-CON-001 | Configure a Dynamics 365 connection per project | kind `d365fo|d365bc`, base URL (https, allow-listed host shape), tenant id, client id, auth mode `delegated|client_credentials`, company; non-secret fields in `connector.*` settings; client secret write-only → OS keyring; every change audited | ERR-002, ERR-113 | S13 | connector GET/PUT | test_connector_settings |
| FR-CON-002 | Sign in with Microsoft (delegated) | auth-code + PKCE in the system browser, loopback callback on the app's own port, `state` bound to the pending attempt and accepted once; MSAL cache serialised to the keyring; silent refresh thereafter; application mode uses client credentials from the keyring | ERR-110, ERR-111, ERR-112 | S13 | connector/sign-in, /connector/callback | test_connector_auth (mock token endpoint; wrong-state rejected) |
| FR-CON-003 | Test connection + entity check | token → companies the identity can read → `$metadata`/resource probe → every entity+field of the active profile must exist; missing items listed with candidates from metadata; result stored in `connector_profiles.entity_check_json` | ERR-112, ERR-113, ERR-114, ERR-117 | S13 | connector/test, /companies | test_entity_check (mock `missing-entity` fault) |
| FR-CON-004 | Connector profiles as data | `profiles/d365fo.json`, `d365bc.json` shipped; per-project copy versioned like mapping profiles; editable entity/field/filter/sort-key/watermark per source; a tenant that names things differently is a profile edit, never code | ERR-002, ERR-114 | S13 | connector/profile | test_profile_versioning |
| FR-CON-005 | Pull a period | job `connector-pull`: token → entity check → `$count` guard → paged GET (`$select`, `$orderby` stable key, `$filter` period, company scoping) with `Retry-After`/backoff ≤ 5 attempts → count consistency (one re-pull) → deterministic snapshot workbook (preset headers, text cells, sorted, `Meta` sheet) → stage + validate; commit explicit unless `connector.auto_commit_when_clean`; no partial snapshot ever staged | ERR-110, 112–118, ERR-027 | S03 step 0, S01 | connector/pull → jobs | test_connector_pull (parity bar doc 14 §3) |
| FR-CON-006 | Snapshot is an ordinary import | `import_batches.source=connector`, `pull_id`; batch id from the data-sheet content hash; the matching `D365FO-*`/`D365BC-*` preset auto-applies; quarantine, control totals, TB gate, supersede, drill-to-source and audit behave exactly as for a file | — | S03–S05 | imports | parity assertions: connector == file == CSV |
| FR-CON-007 | No-change detection and refresh | unchanged ledger ⇒ same content hash ⇒ "no change since <date>", no batch; *Refresh this month* re-pulls gl(+ap) for the open period; BC pre-check `$count lastModifiedDateTime gt <last pull>`; F&O watermark field optional in the profile; a changed ledger supersedes the period's batch on commit after showing the row delta | ERR-112, ERR-115 | S01, S03 | connector/pull, /check-changes | test_connector_nochange, test_refresh_supersede |
| FR-CON-008 | Post-pull enrichment | committed `ap` snapshot → vendor enrichment (06 §2.9); committed `tb` snapshot → `tb_check` tie-out; `masters` sheets → masters import; all counts recorded in `connector_pulls.row_counts_json` and the import report | ERR-001, ERR-030 | S03, S05, S16 | imports/enrich, tb-check | test_connector_pull (enrichment + tie-out assertions) |
| FR-CON-009 | Security envelope | egress only to `login.microsoftonline.com` + configured host (+ `127.0.0.1` for the sample project's demo ledger); TLS mandatory; tokens/secrets only in the keyring and never in responses, logs, DB, job payloads, diagnostics or backups; *Disconnect* wipes the keyring entries and audits; no background network; with the connector disabled the socket-blocked run sees zero calls; the app never writes to the ERP | ERR-113 | S13 | connector/disconnect | doc 12 §8 connector tests; static scan for ERP writes |
| FR-CON-010 | Works without a tenant | `tools/mock_d365.py` emulates both products incl. token endpoint, `$metadata`, paging, `$count`, `$expand`, fault injection (429/503/truncate/count-drift/missing-entity) over `sample-data/erp_shapes/`; sample project offers *Connect to the demo ledger (local)*; CI runs every connector test against the mock only | — | S13, S15 | — | tests/integration/test_connector_pull.py; test_mock_d365 |

## D. Statements, KPIs, BvA, drill (FR-CAL) — owner doc 03, 43, 45
| ID | Statement | Rule | Err | Scr | API | Test |
|---|---|---|---|---|---|---|
| FR-CAL-001 | P&L / BS / CF | registry lines (45), presentation signs (03 §1), CF classification table (03 §3); BS without opening → movement statement, labelled | ERR-030 | S06 | statements | pl/bs/cf_basic |
| FR-CAL-002 | KPI library | ≥30 KPIs (43) with closing-balance basis, 2 dp, `n/a`+reason on zero divisor | — | S01, S06 | kpi | kpis fixtures |
| FR-CAL-003 | BvA | lowest shared grain; signed var_abs, var_pct, favourable from registry direction; AND-materiality (03 §5) | — | S07 | bva | bva_basic (6 cases) |
| FR-CAL-004 | Variance bridge | volume/price/mix/other only when drivers exist; else "not imported" | — | S07 | bridge | attribution |
| FR-CAL-005 | Drill to source row | every aggregate cell → vouchers → rows with file + row + layer sections (03 §8) | — | S06, S07 | drill | drilldown |
| FR-CAL-006 | Period comparisons | YTD, PY-YTD, YoY, QoQ, MoM; phased budgets stamped `source=phased:<curve>` | — | S06, S07 | statements?compare | periods tests |
| FR-CAL-007 | Data-quality score | 100 − deductions (29 §9), always with reasons; never blocks | — | S01 | dashboard | quality_score |
| FR-CAL-008 | ₹'000 display rounding | largest-remainder allocation; displayed lines sum to displayed subtotal | — | S06, exports | — | money + statements |
| FR-CAL-009 | Layers | `gl` vs `gl_adj` (39) selectable on statements/BvA/drill; exports label the layer | — | S06, S07 | ?layer | adjustments |
| FR-CAL-010 | Three-way compare | actual vs budget version vs locked forecast run, columns labelled with version names | — | S07 | bva?forecast_run | bva_threeway |

## E. Close management (FR-CLO) — owner doc 30
| ID | Statement | Rule | Err | Scr | API | Test |
|---|---|---|---|---|---|---|
| FR-CLO-001 | Close calendar | business-day aware (holiday list per project), due dates relative to period end | — | S16 | close/calendar | close_service |
| FR-CLO-002 | Task checklist | template (30 §2) instantiated per period; owner, due, dependency, evidence link; states 23 §7 | — | S16 | close/tasks | close_service |
| FR-CLO-003 | Blockers | computed from system state: TB unbalanced, High findings open, forecast stale, exports missing | — | S01, S16 | close GET | close_blockers |
| FR-CLO-004 | Sign-off | all tasks done/waived + zero blockers or override note; attestation text + timestamp → audit | ERR-080 | S16 | close/sign-off | close_signoff |
| FR-CLO-005 | Close pack | one action → Excel + PPT of the period from one snapshot (shares FR-RPT-006) | ERR-060 | S16 | exports | cross-artifact |
| FR-CLO-006 | Year-end | checks, closing adjustments to `eq_re`, opening batch for next FY, rollforward Δ = 0 (38) | ERR-082 | S16 | year-end/* | test_year_end |

## F. Budgeting & planning (FR-PLN) — owner docs 29, 48, 40
| ID | Statement | Rule | Err | Scr | API | Test |
|---|---|---|---|---|---|---|
| FR-PLN-001 | Budget versions | import or grid-author over import (every edit audited before/after), copy, `draft→approved→locked` (23 §5) | ERR-100 | S17 | budgets | budget_versions |
| FR-PLN-002 | Budget phasing | annual-only budgets phased by curve (08 §5), stamped | — | S17 | budgets/phase | phasing |
| FR-PLN-003 | Driver planning | driver kinds (29 §2), driver→account-group formula registry, formula shown beside line, overrides flagged | — | S17 | planning/drivers | drivers |
| FR-PLN-004 | Headcount plan | opening HC, joiners/leavers, avg cost, increment %, bonus % → personnel cost + closing HC (never negative) | ERR-101 | S17 | planning/headcount | headcount |
| FR-PLN-005 | Capex & depreciation | asset classes (life, SLM/WDV, residual), pro-rata month of addition, disposals with gain/loss | — | S17 | planning/capex | capex |
| FR-PLN-006 | Debt schedule | facilities, draw/repay, interest = avg balance × rate/12 (Decimal) | — | S17 | planning/debt | debt |
| FR-PLN-007 | Working-capital plan | DSO/DPO/DIO targets → AR/AP/inventory forecast | — | S17 | planning/wc | working_capital |
| FR-PLN-008 | 13-week cash | calendar weeks Mon–Sun; inflows from AR ageing + collection curve; outflows AP/payroll/debt/capex/tax calendars; min-balance alert | — | S17 | planning/cash13 | cash13 |
| FR-PLN-009 | Integrated 3-statement forecast | PL→BS→CF articulation; ΔCash(CF) = ΔCash(BS); RE roll; imbalance = named check failure, never a plug | ERR-102 | S09, S17 | planning/integrate | integrated_basic |
| FR-PLN-010 | Assumptions register | one home for assumptions; versions; approval; stale-run list when an assumption changes (48) | — | S17 | assumptions | test_assumptions |
| FR-PLN-011 | Cost allocations | methods (40 §2), runs create adjustments in `gl_adj`; oracle 40 §4 | ERR-042 | S17 | allocations | test_allocations |
| FR-PLN-012 | Planning calendar | annual template with milestones, shown S16/S17 (48 §1) | — | S16, S17 | close/calendar | test_assumptions |

## G. Exceptions (FR-EXC) — owner docs 07, 44, 42
| ID | Statement | Rule | Err | Scr | API | Test |
|---|---|---|---|---|---|---|
| FR-EXC-001 | 28 rules | EXC-001…028 per 07/44 (025–028 = entry-hygiene: narration mismatch, amount outlier/decimal shift, unusual cost centre, near-duplicate charge); each returns findings, `not_run` with reason, or empty; thresholds from settings `rule.*` | — | S08 | exceptions/run | test_exc_001…028 |
| FR-EXC-002 | Deterministic finding key | `EXC-nnn|entity|account|period|grain-key` (07 §2); re-run upserts, never duplicates; closed findings re-fire as `reopened` | — | S08 | — | engine_rerun |
| FR-EXC-003 | Run orchestration | on demand + auto after commit (setting); job with per-rule progress; `not_run` rules listed with reasons | — | S08 | exceptions/run, jobs | engine |
| FR-EXC-004 | Severity | rule default; escalation ≥3× absolute threshold (both legs for AND rules) → High (07 §1) | — | S08 | — | severity tests |
| FR-EXC-005 | Finding workflow | `new→acknowledged→explained→corrected→verified→closed`; `waived` with reason + expiry (23 §3) | ERR-040, ERR-041 | S08 | transition | finding_repo |
| FR-EXC-006 | Owner assignment & due dates | default owner from master data; bulk assign; due date default = period end + N days (setting) | — | S08 | bulk-assign | finding_repo |
| FR-EXC-007 | Evidence & drill | every finding carries rows/vouchers evidence that drills to source (03 §8) | — | S08 | exceptions/{id} | evidence tests |
| FR-EXC-008 | Owner action list export | per-owner Excel of open findings (09 §2 sheet 11 shape) | — | S08 | exports | sheet_owner_actions |
| FR-EXC-009 | Waiver expiry | expired waivers reopen on next run; expiry visible in list | — | S08 | — | engine_rerun |
| FR-EXC-010 | Acceptance harness | recall 36/36 plants, controls 0/13, High 19/19, suggestion exactness on the corpus (14 §3) | — | — | — | scripts/acceptance.py |
| FR-EXC-011 | Finding comments | threaded notes per finding, audited, exported in action list | — | S08 | exceptions/{id}/comments | finding_repo |
| FR-EXC-012 | Suggested fix on every finding | `suggestion {kind, lines, target_period_id, basis, confidence, erp_hint}` from the doc 07 §7.3 template; journal kinds net to zero; data-dependent parts per 44 (dominant account / cost centre, median, shift factor); stored in `findings.suggestion_json` | — | S08 | exceptions/{id} | test_suggestions (one case per rule) |
| FR-EXC-013 | Apply suggestion as management adjustment | creates a doc-39 `correction_view` group from the lines, reason = finding key, finding → `corrected`, `suggestion_status = applied`; locked target period → ERR-046; second apply with a new key → ERR-046 (`already_consumed`); same-key replay returns the original result | ERR-046, ERR-005 (key collision only) | S08 | exceptions/{id}/suggestion/apply | test_suggestion_apply |
| FR-EXC-014 | Rectification journal export | queued suggestion lines of a period → journal file in `d365fo_general_journal` / `d365bc_general_journal` / `generic_csv` (26 §7); nets to zero per finding; findings → `corrected`/`exported` with report id; empty queue → ERR-046 | ERR-046 | S08, S11 | exports (kind journal), rectification-journal | test_journal_export (golden files) |
| FR-EXC-015 | Correction verification loop | on each run, `corrected` findings whose correcting lines appear in newly committed GL (44 § verification match) get evidence + a proposed `verified` transition (confirm on S08; auto-confirm setting default off); unseen after 2 periods → close-checklist item | — | S08, S16 | exceptions/run | test_verification_loop |

## H. Forecast & scenarios (FR-FOR) — owner docs 08, 46
| ID | Statement | Rule | Err | Scr | API | Test |
|---|---|---|---|---|---|---|
| FR-FOR-001 | 8 methods | 08 §2 with minimum history; insufficient history → `not_run` with reason, never silent fallback | — | S09 | forecast/run | fc_* fixtures |
| FR-FOR-002 | Backtest & selection | rolling-origin backtest per group, MAPE/bias, best method chosen deterministically, ties by method order | — | S09 | forecast/runs | backtest oracle |
| FR-FOR-003 | Runs lifecycle | `draft→locked` immutable; BvA uses latest locked | ERR-103 | S09 | forecast/runs/{id}/lock | forecast_repo |
| FR-FOR-004 | Scenarios | driver/%/absolute deltas over a base run; compare ≤4 side by side | — | S10 | scenarios | scenarios |
| FR-FOR-005 | Sensitivity | one/two-variable tables over a driver, analyst-set step/range | — | S10 | sensitivity | sensitivity |
| FR-FOR-006 | Goal seek | bisection on the deterministic model, 50 iterations, minor-unit tolerance; `no_solution` reported | — | S10 | goal-seek | goal_seek |
| FR-FOR-007 | What-if sandbox | unsaved overlay on charts; save converts to scenario | — | S10 | — | ui test |
| FR-FOR-008 | FVA reporting | forecast-vs-actual accuracy and bias per group, by run (08 §6) | — | S09 | forecast/runs/{id} | fva tests |
| FR-FOR-009 | Guardrails | no negative forecasts for non-negative lines; cap on growth extrapolation; all labelled (08 §7) | — | S09 | — | guardrail tests |

## I. Reconciliations (FR-REC) — owner: this doc + 06 (source_kind `subledger`)
| ID | Statement | Rule | Err | Scr | API | Test |
|---|---|---|---|---|---|---|
| FR-REC-001 | Subledger import | bank, AR, AP, payroll extracts through the import pipeline, `source_kind=subledger`, `subledger_kind` set | 06 reasons | S03, S18 | imports | recon fixtures |
| FR-REC-002 | Matching | score by amount (exact → ±tolerance), date (±N days), reference tokens; one-to-one and many-to-one; deterministic ordering | — | S18 | reconcile/run | test_reconcile |
| FR-REC-003 | Unmatched both sides | GL-only and subledger-only lists, totals, ageing | — | S18 | reconcile/{id} | test_reconcile |
| FR-REC-004 | Tolerance & sign-off | tolerance setting per kind; sign-off blocked when unmatched net > tolerance; `open→in_review→signed_off` (23 §8) | ERR-081 | S18 | reconcile/{id}/sign-off | recon_signoff |
| FR-REC-005 | Recon as close evidence | signed-off recon links to the close task (30 §2) | — | S16 | close/tasks | close_service |

## J. Reporting & exports (FR-RPT) — owner docs 09, 10, 47
| ID | Statement | Rule | Err | Scr | API | Test |
|---|---|---|---|---|---|---|
| FR-RPT-001 | Excel pack | 12 sheets fixed order (09 §2); values + formulas policy (09 §3); Checks sheet always evaluated | ERR-060 | S11 | exports kind=excel | sheet_* |
| FR-RPT-002 | PowerPoint deck | 8 slide types fixed order; missing type → explicit placeholder slide (10 §2); blocked when checks fail | ERR-060 | S11 | exports kind=pptx | slide_* |
| FR-RPT-003 | PDF pack | same snapshot as Excel; page footer with project/period/generated-at/hash | ERR-060 | S11 | exports kind=pdf | pdf tests |
| FR-RPT-004 | Cross-artifact tie-out | the same number in DB, Excel, PPT and PDF is byte-equal after formatting (14 §4) | — | — | — | cross_artifact |
| FR-RPT-005 | Report registry | `generating→ready|failed(checks)`; ready immutable; SHA-256 recorded; download | — | S11 | reports | report_repo |
| FR-RPT-006 | Board pack | Excel + PPT + PDF in one action from one snapshot id | ERR-060 | S11 | exports kind=all | cross_artifact |
| FR-RPT-007 | Report builder | saved, versioned definitions of statement/BvA/KPI blocks × period × grain; renders through the same exporters | — | S11 | report-definitions | report_builder |
| FR-RPT-008 | KPI builder | safe expression grammar (+ − × ÷, brackets, defined names) over KPI/account aggregates; result is a KPI everywhere | ERR-104 | S11 | kpi-definitions | kpi_builder |
| FR-RPT-009 | Commentary standard | variance commentary fields and tone rules (47); approved commentary only in exports (23 §6) | — | S07, S11 | commentary | commentary tests |
| FR-RPT-010 | Export safety | no formulas referencing external workbooks; no macros; CSV/formula-injection neutralised (12 §4) | — | — | — | security suite |

## K. Alerts (FR-ALR) — owner: this doc + 08 §6
| ID | Statement | Rule | Err | Scr | API | Test |
|---|---|---|---|---|---|---|
| FR-ALR-001 | Threshold alerts | on KPIs, finding counts, forecast bias, 13-week minimum balance; evaluated after each run/commit | — | S19 | alerts | test_alerts |
| FR-ALR-002 | Dedupe & lifecycle | key `(alert_key, period)`; `active→acknowledged→dismissed` (auto on lock) (23 §9) | — | S19 | alerts/{id}/ack | test_alerts |
| FR-ALR-003 | Alert centre | S01 bell + S19 list + digest view; 90-day retention; no external push in v1 | — | S01, S19 | alerts | ui test |

## L. AI (FR-AI) — owner docs 11, 88
| ID | Statement | Rule | Err | Scr | API | Test |
|---|---|---|---|---|---|---|
| FR-AI-001 | Off by default | no provider configured → every AI entry point hidden/disabled with explanation | ERR-070 | S13 | commentary/draft | ai_client |
| FR-AI-002 | Permitted uses only | 11 §1 list (commentary drafts, mapping suggestion reorder, Q&A over computed numbers, explanation of findings); never computes, posts or approves | — | S07, S09, S11 | commentary/draft | guardrails |
| FR-AI-003 | Guardrails | every draft passes `guardrails.py`: numbers must match the payload, no new figures, banned words, length | ERR-071 | — | — | guardrails golden |
| FR-AI-004 | Provenance | AI drafts enter commentary as `draft` with model/prompt version; approval is human | — | S07 | commentary | commentary tests |
| FR-AI-005 | Evaluation | golden set 11 §7 (≥16/20) before any prompt ships; prompt texts verbatim from 88 | — | — | — | ai_eval |
| FR-AI-006 | Data minimisation | only the payload schema fields leave the machine; keys in OS keychain (12 §5) | — | S13 | settings | security suite |

## M. Governance: audit, security, settings (FR-GOV) — owner docs 12, 22, 23, 62, 79
| ID | Statement | Rule | Err | Scr | API | Test |
|---|---|---|---|---|---|---|
| FR-GOV-001 | Audit log | every mutation writes `audit_log` with canonical payload hash chained to the previous row (12 §3) | — | S14 | audit | audit chain |
| FR-GOV-002 | Audit verify | recompute chain; break → report first bad row | ERR-090 | S14 | audit/verify | tamper test |
| FR-GOV-003 | Settings | typed keys (62); impact text before save; thresholds `rule.*`; every change audited | ERR-105 | S13 | settings | settings tests |
| FR-GOV-004 | Local-only | no network calls except `ai/client.py` when configured; CI test asserts no sockets opened otherwise | — | — | — | security suite |
| FR-GOV-005 | At-rest protection | optional DB passphrase; backups encrypted when set (12 §2) | — | S13 | backup | test_backup |
| FR-GOV-006 | Hostile input | zip bombs, formula injection, oversize, path traversal in file names (12 §4) | ERR-029 | S03 | imports | security suite |
| FR-GOV-007 | Licence | offline licence file (79): states valid/expired/grace/invalid; invalid never hides data, only blocks exports after grace | ERR-063 | S13 | settings | test_license |
| FR-GOV-008 | Restatement & reclass | three events kept distinct (41 §1); locked-period restatement workflow with audit (41 §2) | ERR-083 | S06, S16 | adjustments | test_restatement |
| FR-GOV-009 | Management adjustments | balanced adjustment groups in layer `gl_adj`; apply/reverse; never touch `gl` (39) | ERR-042 | S06 | adjustments | test_adjustments |

## N. Help & diagnostics (FR-HLP) — owner doc 18
| ID | Statement | Rule | Err | Scr | API | Test |
|---|---|---|---|---|---|---|
| FR-HLP-001 | In-app guide | doc 18 content rendered in S15; context links from every empty/error state | — | S15 | — | a11y + link test |
| FR-HLP-002 | Diagnostics bundle | logs (redacted), versions, settings (no secrets), last job statuses → zip | — | S15 | diagnostics | test_diagnostics |
| FR-HLP-003 | First-run walkthrough | sample-project 10-minute tour (18 §1), dismissible, re-openable | — | S02, S15 | — | ui walkthrough |

## O. Desktop & packaging (FR-PKG) — owner doc 16
| ID | Statement | Rule | Err | Scr | API | Test |
|---|---|---|---|---|---|---|
| FR-PKG-001 | Single-executable desktop app | local server + UI in one process, port chosen at start, opens browser/webview | — | — | health | smoke |
| FR-PKG-002 | Signed installers | Windows + macOS per 16; version in `/health` and About | — | S15 | health | release checklist |
| FR-PKG-003 | Upgrade safety | schema migrations forward-only, backup before migrate, rollback instructions | ERR-091 | S13 | — | migration tests |

**Count:** PRJ 7 · MDM 5 · IMP 19 · CON 10 · CAL 10 · CLO 6 · PLN 12 · EXC 15 · FOR 9 · REC 5 · RPT 10 · ALR 3 · AI 6 · GOV 9 · HLP 3 · PKG 3 = **132 FRs** (114 at pass 3; +4 IMP and +4 EXC under DEC-011/012; +10 CON under DEC-013). Every error code referenced here exists in doc 22 (the catalogue was extended in the same commits: ERR-025, 026, 029, 051, 063, 082, 083, 100–105, 110–118).
