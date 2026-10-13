# 02 — DATA DICTIONARY

> Owner of: every table, field, type, and example. `app/store/schema.sql` must implement this 1:1 (schema-equality test, doc 14). Money is always INTEGER minor units (e.g., paise/cents); display formatting happens in calc/UI, never storage. All timestamps UTC ISO-8601. All IDs text.

## 1. Conventions
- `*_minor` INTEGER NOT NULL: money in minor units. Sign convention: debit positive, credit negative in `gl_rows.amount_minor` (doc 03 owns statement sign presentation).
- Every user-editable table carries `version INTEGER`, `created_at`, `updated_at`, `created_by` (local user label), and writes an `audit_log` row on mutation.
- Soft-delete only via `is_active=0`; financial rows are never deleted — a batch is superseded (`import_batches.status='superseded'`).

## 2. Tables

### projects
| field | type | notes/example |
|---|---|---|
| project_id | TEXT PK | `prj_` + 12 hex |
| name | TEXT | "Acme India — FP&A" |
| base_currency | TEXT(3) | `INR` |
| fy_start_month | INTEGER 1–12 | 4 = April |
| calendar_type | TEXT | `monthly` (v1); `445` reserved |
| created_at/updated_at | TEXT | UTC |
| is_sample | INTEGER 0/1 | sample company flagged everywhere |

### periods
| period_id TEXT PK (`2026-P01`) · project_id FK · fiscal_year INT · period_no INT 1–12 · start_date/end_date DATE · status TEXT `open|closing|locked` · locked_at TEXT NULL · lock_note TEXT NULL |

**Period identity (normative):** `fiscal_year` = calendar year in which the fiscal year *starts*. `period_id = <fiscal_year>-P<period_no 01..12>`; with fy_start_month=4, `2026-P01` = April 2026, `2026-P12` = March 2027. PY of `2026-P01` = `2025-P01`. All docs' examples follow this.

### entities / accounts / cost_centres / vendors / owners
Master data, each: `<x>_id TEXT PK`, `project_id FK`, `code TEXT`, `name TEXT`, `is_active INT`, `version INT`, timestamps. `accounts` adds: `account_type` (`revenue|cogs|opex|asset|liability|equity|other`), `statement_line` (doc 03 mapping key), `normal_side` (`debit|credit`). `owners`: `owner_id, display_name, email NULL, role_label`. `account_owners(account_id, owner_id, valid_from)` assigns accountability (doc 07).

### import_batches
| batch_id TEXT PK (`bat_`+hash12) · project_id · period_id · source_kind (`gl|budget|subledger|drivers|opening`) · file_name · file_sha256 TEXT(64) · file_size INT · mapping_profile_id FK · status (`staged|committed|rejected|superseded`) · row_count_in/valid/quarantined INT · control_debit_minor/control_credit_minor INT NULL · declared_* INT NULL · committed_at · supersedes_batch_id NULL |

### import_rows_raw (staging, per batch)
| raw_id PK · batch_id FK · sheet_name TEXT · row_no INT (1-based in source incl. header offset recorded) · raw_json TEXT (original cells as strings) · parse_status (`ok|quarantined`) · quarantine_reason TEXT NULL |

### gl_rows (the fact table)
| gl_row_id TEXT PK = hash(batch_id+row_no) (deterministic, doc 06) · project_id · period_id · batch_id FK · entity_id · account_id · cost_centre_id NULL · vendor_id NULL · voucher_no TEXT · document_date DATE · posting_date DATE · description TEXT (hostile data — never executed/rendered as markup) · amount_minor INT (debit +, credit −) · quantity_decimal TEXT NULL (decimal string; floats are banned everywhere including drivers, doc 46) · source_file TEXT · source_row INT |

### mapping_profiles / mapping_rules
`mapping_profiles(profile_id PK, project_id, source_kind, name, version, is_default, created_at)`. `mapping_rules(profile_id FK, source_column TEXT, canonical_field TEXT, transform TEXT (`none|date:fmt|amount:debit_credit_cols|sign_flip`), constant_value TEXT NULL, PK(profile_id, canonical_field))`. Canonical fields: entity, account, cost_centre, vendor, voucher_no, document_date, posting_date, description, amount, debit, credit, quantity.

### budget_lines / budget_versions
`budget_versions(version_id PK, project_id, label (`Budget FY27 v1`), status (`draft|approved|locked`), created_at)`. `budget_lines(line_id TEXT PK, version_id FK, period_id, entity_id, account_id, cost_centre_id NULL, amount_minor INT)` + `UNIQUE INDEX ux_budget_grain ON budget_lines(version_id, period_id, entity_id, account_id, IFNULL(cost_centre_id,''))` — a composite PK over a nullable column would silently allow duplicates in SQLite, so uniqueness lives in this expression index, and a schema test inserts a duplicate grain expecting failure.

### driver_values
| driver_id TEXT (`volume|price|headcount|rate|custom:<name>`) · period_id · entity_id · account_id NULL · value TEXT (decimal string, parsed via money module rules — never float storage) · source (`import|manual|scenario`) · scenario_id NULL |

### forecast_runs / forecast_lines / scenarios
`forecast_runs(run_id PK, project_id, base_period_id, method_map_json TEXT, status (`draft|locked`), accuracy_json TEXT (per-group MAPE/bias), created_at)`. `forecast_lines(run_id FK, period_id, entity_id, account_id, cost_centre_id, amount_minor INT, method TEXT, PK(...))`. `scenarios(scenario_id PK, project_id, name (`Base|Upside|Downside|custom`), base_run_id FK, delta_json TEXT, status)`.

### findings (exceptions)
| finding_id TEXT PK = canonical key hash (doc 07 §2) · finding_key TEXT UNIQUE (`EXC-018|ENT|ACC|PERIOD|grain`) · rule_id TEXT `EXC-###` · project_id · period_id · entity_id · account_id · severity (`high|medium|low`) · amount_minor INT · evidence_json TEXT (row ids, values, thresholds — everything needed to re-derive) · status (`new|acknowledged|explained|corrected|verified|closed|waived`) · owner_id NULL · due_date DATE · waive_reason TEXT NULL · waive_expires DATE NULL · first_seen_run TEXT · last_seen_run TEXT |

### finding_comments / finding_history
Append-only: `finding_id, at, actor, action, from_status, to_status, note`.

### commentary
| commentary_id PK · project_id · period_id · scope (`exec_summary|variance:<key>|forecast`) · text TEXT · source_refs_json (variance/finding ids the numbers came from) · ai_assisted INT 0/1 · prompt_version TEXT NULL · version INT · status (`draft|approved`) |

### reports
| report_id PK · project_id · period_id · kind (`excel|pptx|pdf`) · path TEXT · sha256 · snapshot_json (statement/BvA/forecast run ids used) · created_at |

### settings / thresholds
`settings(project_id, key, value_json, version, PK(project_id,key))`. Rule thresholds are settings keys `rule.EXC-###.<param>` (doc 07 defaults).

### audit_log
| audit_id INTEGER PK AUTOINCREMENT · project_id · at TEXT · actor TEXT · entity_type TEXT · entity_id TEXT · action TEXT · before_json NULL · after_json NULL · prev_hash TEXT · hash TEXT = SHA256(prev_hash + canonical row) | Hash-chain verified on demand (S14); broken chain → read-only banner + restore guidance (doc 12).

## 3. Volumes & indexes
Design point: 250k gl_rows/project/year, 5M lifetime. Indexes: gl_rows(period_id, account_id), (voucher_no), (batch_id); findings(project_id, status, severity); budget_lines(version_id, period_id). No other indexes without a measured query (doc 15).

## 4. Example row (gl_rows)
`{"gl_row_id":"9f2c…","period_id":"2026-P01","voucher_no":"VCH-2026-0001","posting_date":"2026-04-03","account_id":"ACC-5100","amount_minor":-12500050,"source_file":"gl_apr.xlsx","source_row":142}` → ₹125,000.50 credit (expense accrual reversal, sign per §1).

## 5. Expansion tables (docs 19/29/30 — same conventions §1; schema.sql must include all)
- **close_tasks**: task_id PK · project_id · period_id · template_key · title · owner_id NULL · due_offset_days INT · depends_on NULL · kind (`system|attest|manual`) · status (doc 23 §7) · completed_by/at · note.
- **close_signoffs**: signoff_id PK · project_id · period_id · signer · attestation_text · snapshot_json · at.
- **planning_drivers**: driver_row_id PK · project_id · period_id · entity_id · driver_id · account_id NULL · value_decimal TEXT · source (`import|manual|scenario`) · scenario_id NULL · version.
- **headcount_plans**: plan_id PK · project_id · period_id · cost_centre_id · opening_hc INT · joiners INT · leavers INT · avg_cost_minor INT · increment_pct TEXT · bonus_pct TEXT.
- **capex_assets**: asset_id PK · project_id · class_label · cost_minor INT · addition_period · useful_life_months INT · method (`slm|wdv`) · residual_pct TEXT · disposal_period NULL · proceeds_minor NULL.
- **debt_schedules**: facility_id PK · project_id · label · opening_minor INT · rate_pct TEXT · kind (`fixed|floating`) — movements in **debt_movements**(facility_id, period_id, kind `draw|repay`, amount_minor).
- **wc_assumptions**: project_id · entity_id · dso_days/dpo_days/dio_days TEXT · effective_period. PK(project_id, entity_id, effective_period).
- **cash13_inputs**: input_id PK · project_id · week_start DATE · kind (`ar_due|ap_due|payroll|debt|capex|tax|other_in|other_out`) · amount_minor · party_label NULL · source_ref.
- **recon_runs**: recon_id PK · project_id · period_id · kind (`bank|ar|ap|payroll`) · tolerance_minor INT · status (doc 23 §8) · signed_by/at. **recon_matches**: recon_id FK · side (`subledger|gl`) · ref_id · amount_minor · matched_group NULL · score TEXT.
- **alerts**: alert_id PK · project_id · alert_key · period_id · kind (`kpi|finding|bias|close`) · severity · message · status (doc 23 §9) · seen_count INT · created_at/last_seen.
- **report_definitions**: def_id PK · project_id · name · blocks_json (statement/bva/kpi blocks, grain, period mode) · version · created_by.
All expansion tables carry created_at/updated_at/version and audit-on-mutation per §1.

## 6. Tables required by docs 38–48 (normative — schema.sql is incomplete without these)
- **adjustments** (doc 39): adj_id TEXT PK · project_id · period_id · entity_id · account_id · cost_centre_id NULL · amount_minor INT · kind (`reclass|provision|closing|correction_view|other`) · label · reason TEXT NOT NULL · pair_group_id TEXT NULL · contra_account_id NULL · status (`draft|applied|reversed`) · reverses_adj_id NULL · source (`manual|system_closing|allocation`) · created_by/at · version. Rule runs record their layer; statement queries take layer as a parameter.
- **allocation_definitions**: def_id PK · project_id · name · method (`pct|driver|step_down`) · source_scope_json · driver_id NULL · step_order_json NULL · version · is_active. **allocation_receivers**: def_id FK · cost_centre_id · pct TEXT NULL (driver method computes shares). **allocation_runs**: run_id PK · def_id FK · period_id · status (`draft|applied`) · created_at (output = adjustments rows with source=`allocation`, label `ALLOC:<name>`).
- **assumptions** (doc 48): assumption_id PK · project_id · scope (`project|entity|account_group`) · scope_ref · key · value_decimal TEXT · unit · owner_id NULL · source_note · valid_from_period · version · status (`draft|approved`). Forecast runs store assumption versions in accuracy/snapshot JSON.
- **year_end_runs**: ye_id PK · project_id · fiscal_year INT · status (`checks|closing_proposed|confirmed`) · closing_batch_ref NULL · rollforward_check_json · created_at. (Closing journal itself is stored as adjustments kind=`closing` + a generated `opening` import batch, doc 38.)
Schema-equality test (doc 14) compares this doc's full table list (sections 2, 5, 6) against sqlite_master — any table here missing from schema.sql fails CI.
