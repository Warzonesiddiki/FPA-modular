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

### entities / accounts / cost_centres / vendors / owners
Master data, each: `<x>_id TEXT PK`, `project_id FK`, `code TEXT`, `name TEXT`, `is_active INT`, `version INT`, timestamps. `accounts` adds: `account_type` (`revenue|cogs|opex|asset|liability|equity|other`), `statement_line` (doc 03 mapping key), `normal_side` (`debit|credit`). `owners`: `owner_id, display_name, email NULL, role_label`. `account_owners(account_id, owner_id, valid_from)` assigns accountability (doc 07).

### import_batches
| batch_id TEXT PK (`bat_`+hash12) · project_id · period_id · source_kind (`gl|budget|subledger|drivers|opening`) · file_name · file_sha256 TEXT(64) · file_size INT · mapping_profile_id FK · status (`staged|committed|rejected|superseded`) · row_count_in/valid/quarantined INT · control_debit_minor/control_credit_minor INT NULL · declared_* INT NULL · committed_at · supersedes_batch_id NULL |

### import_rows_raw (staging, per batch)
| raw_id PK · batch_id FK · sheet_name TEXT · row_no INT (1-based in source incl. header offset recorded) · raw_json TEXT (original cells as strings) · parse_status (`ok|quarantined`) · quarantine_reason TEXT NULL |

### gl_rows (the fact table)
| gl_row_id TEXT PK = hash(batch_id+row_no) (deterministic, doc 06) · project_id · period_id · batch_id FK · entity_id · account_id · cost_centre_id NULL · vendor_id NULL · voucher_no TEXT · document_date DATE · posting_date DATE · description TEXT (hostile data — never executed/rendered as markup) · amount_minor INT (debit +, credit −) · quantity REAL NULL (drivers only) · source_file TEXT · source_row INT |

### mapping_profiles / mapping_rules
`mapping_profiles(profile_id PK, project_id, source_kind, name, version, is_default, created_at)`. `mapping_rules(profile_id FK, source_column TEXT, canonical_field TEXT, transform TEXT (`none|date:fmt|amount:debit_credit_cols|sign_flip`), constant_value TEXT NULL, PK(profile_id, canonical_field))`. Canonical fields: entity, account, cost_centre, vendor, voucher_no, document_date, posting_date, description, amount, debit, credit, quantity.

### budget_lines / budget_versions
`budget_versions(version_id PK, project_id, label (`Budget FY27 v1`), status (`draft|approved|locked`), created_at)`. `budget_lines(version_id FK, period_id, entity_id, account_id, cost_centre_id NULL, amount_minor INT, PK(version_id, period_id, entity_id, account_id, cost_centre_id))`.

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
