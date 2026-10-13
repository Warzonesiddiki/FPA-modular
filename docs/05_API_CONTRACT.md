# 05 — API CONTRACT

> Owner of: every HTTP endpoint between UI/CLI and engine. Routes implement this 1:1 (parity test, doc 14). Base: `http://127.0.0.1:<port>/api/v1`. All money in JSON = string decimal in major units (`"125000.50"`) at the boundary, converted via money.py — never JSON numbers for money. Dates ISO. Errors: `{code:"FP&A-ERR-###", message:<plain language>, hint:<next action>, retryable:bool, details:{}}` (catalogue in `app/core/errors.py`, doc 15).

## 1. Conventions
Pagination: `?limit=100&cursor=` (default 100, max 1000) on list endpoints; response `{items:[], next_cursor}`. Long jobs (import commit, rules, forecast, export): `POST` returns `202 {job_id}`; `GET /jobs/{id}` → `{status:queued|running|done|failed|cancelled, progress_pct, stage, error?}`; `POST /jobs/{id}/cancel` → 200. Idempotency: import commit and export accept `Idempotency-Key` header; replay returns original result. Versioning: breaking change = `/api/v2` + doc update first (P2).

## 2. Endpoints
### Health & projects
| Method & path | In | Out | Errors |
|---|---|---|---|
| GET `/health` | — | `{status:"ok", version}` | — |
| GET `/projects` | — | list of project summaries | — |
| POST `/projects` | `{name, base_currency, fy_start_month, calendar_type}` | project | ERR-010 name exists |
| GET `/projects/{id}` | — | project + period list + close progress | ERR-001 not found |
| POST `/projects/{id}/periods/{period_id}/lock` | `{note}` | period (locked) | ERR-011 open findings high-severity (returns list; override requires `{force:true, note}` audited) |
| POST `/projects/{id}/backup` / `/restore` | `{path}` | backup manifest | ERR-012 path not writable |

### Imports (doc 06)
| POST `/projects/{id}/imports` (multipart file(s) + `source_kind, period_id`) | → batch staged + profile summary | ERR-020 unsupported file, ERR-021 file too large (>200MB) |
| GET `/imports/{batch_id}` | batch detail incl. counts, control totals, quarantine summary | |
| GET `/imports/{batch_id}/quarantine?limit&cursor` | quarantined rows + reasons | |
| GET/POST/PUT `/mapping-profiles` (+`/{id}`) | profile CRUD; POST `/mapping-profiles/suggest` `{batch_id}` → ranked column suggestions | ERR-022 canonical field mapped twice |
| POST `/imports/{batch_id}/validate` | → validation report (job) | |
| POST `/imports/{batch_id}/commit` | → `{committed counts, tb_status}` (job) | ERR-023 control-total mismatch (details: declared vs actual), ERR-024 trial balance imbalance (details by account) — commit is blocked, staging preserved |
| POST `/imports/{batch_id}/discard` | staging deleted, audit written | |

### Statements, BvA, drill (doc 03)
| GET `/projects/{id}/statements?period_id&entity_id?&statement=pl|bs|cf` | statement lines `{line_key,label,amount,presentation_sign,drill_key}` | ERR-030 period has no committed GL |
| GET `/projects/{id}/bva?period_id&budget_version&grain` | variance rows (doc 03 §5 fields) | |
| GET `/projects/{id}/kpi?period_id` | KPI list `{key,label,value|n/a,reason?,formula}` | |
| GET `/projects/{id}/drill?drill_key` | voucher groups → rows `{voucher_no, dates, description, amount, source_file, source_row}` paginated | |
| GET `/projects/{id}/bridge?period_id&account_group` | components or `{available:false, reason}` | |

### Exceptions (doc 07)
| POST `/projects/{id}/exceptions/run` `{period_id}` → job; GET findings list with filters `status,severity,owner_id,rule_id,q` | |
| GET `/exceptions/{finding_id}` | finding + evidence + history | |
| POST `/exceptions/{finding_id}/transition` `{to_status, note?, waive_reason?, waive_days?}` | ERR-040 illegal transition, ERR-041 waive needs reason+expiry | |
| POST `/exceptions/bulk-assign` `{finding_ids, owner_id, due_date}` | |
| GET `/projects/{id}/owners` + master-data CRUD under `/projects/{id}/master/{entities|accounts|cost-centres|vendors|owners}` | ERR-050 code duplicate |

### Forecast & scenarios (doc 08)
| POST `/projects/{id}/forecast/run` `{base_period_id, method_map?}` → job → run `{accuracy per group}` |
| GET `/forecast/runs?project_id` · GET `/forecast/runs/{id}` (lines paginated) · POST `/forecast/runs/{id}/lock` |
| POST `/projects/{id}/scenarios` `{name, base_run_id, deltas}` · GET compare `?scenario_ids=a,b,c&period_id` |
| PUT `/driver-values` bulk upsert (imports also create these) |

### Exports & commentary & settings
| POST `/projects/{id}/exports` `{kind:excel|pptx|pdf, period_id}` → job → report `{report_id, path, sha256, checks}` | ERR-060 checks failed (tie-out details; generation blocked for pptx/pdf, excel allowed with Checks sheet flag) |
| GET `/projects/{id}/reports` · GET `/reports/{id}/download` (file) |
| GET/PUT `/projects/{id}/commentary?period_id&scope` (PUT creates new version) · POST `/projects/{id}/commentary/draft` (AI; doc 11) → ERR-070 AI disabled/unconfigured, ERR-071 guardrail rejected draft (reasons) |
| GET/PUT `/projects/{id}/settings` (thresholds under `rule.*` keys) · GET `/projects/{id}/audit?limit&cursor` · POST `/projects/{id}/audit/verify` |
| GET `/projects/{id}/dashboard?period_id` | S01 aggregate DTO (KPIs, top variances, findings by severity/owner, close checklist, forecast accuracy) |

## 3. Contract tests (doc 14)
Every endpoint: happy path + each listed error + money-as-string assertion + pagination. OpenAPI generated from routes is diffed against this doc's table in CI (endpoint set equality).
