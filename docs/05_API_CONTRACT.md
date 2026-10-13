# 05 — API CONTRACT

> Owner of: every HTTP endpoint between UI/CLI and engine (field-level payloads: doc 90; both are normative). Routes implement this 1:1 (parity test, doc 14). Base: `http://127.0.0.1:<port>/api/v1`. All money in JSON = string decimal in major units (`"125000.50"`) at the boundary, converted via money.py — never JSON numbers for money. Dates ISO. Errors: `{code:"FP&A-ERR-###", message:<plain language>, hint:<next action>, retryable:bool, details:{}}` (catalogue in `app/core/errors.py`, doc 15).

## 1. Conventions
### 1.1 HTTP outcomes and error transport (DEC-015)
Success: `200` synchronous read/action; `201` resource created; `202` asynchronous job accepted (`{job_id}`); `204` successful action with no body **only when the endpoint explicitly specifies it**. An accepted job is not a successful business result. `GET /jobs/{id}` returns `200` for every retained job, including `failed` and `cancelled`; its `error` carries the same catalogue body as a synchronous failure. An unknown/foreign job id is `404` / ERR-001. Cancellation is not HTTP status 499 and a provider throttle is not forwarded as local status 429.

The table is exhaustive for the **73 codes in doc 22 §2**, with each code in exactly one row. It applies when a failure is returned synchronously; after `202`, use the job's terminal state/error instead. Error bodies always use the public code prefix `FP&A-` (for example `FP&A-ERR-027`) and the shape `{code, message, hint, retryable, details}` from doc 22; retryability comes from that catalogue, not from the HTTP status. `details` may contain money **only as decimal strings in major units** via money.py, never JSON numbers/minor-unit integers. Per-endpoint detail schemas remain required by WI-0001; this table alone does not complete that item.

| HTTP status / transport | Catalogue codes | Meaning |
|---|---|---|
| 400 | ERR-002, ERR-005, ERR-013, ERR-015, ERR-022, ERR-025, ERR-026, ERR-031, ERR-032, ERR-085, ERR-104, ERR-108, ERR-109, ERR-111, ERR-113 | Invalid request, selector, confirmation, OAuth callback/sign-in input, or disallowed connector transport. ERR-111 does not represent local API-token authentication. |
| 403 | ERR-117 | The signed-in Microsoft identity cannot read the selected company; this does not describe local API-token authentication. |
| 404 | ERR-001 | Requested resource missing or outside the current project. |
| 409 | ERR-003, ERR-010, ERR-016, ERR-028, ERR-040, ERR-050, ERR-052, ERR-061, ERR-100, ERR-103, ERR-107, ERR-110, ERR-112, ERR-118 | Resource state, uniqueness, referenced-record, connection state or concurrent-ledger-change conflict. |
| 413 | ERR-021, ERR-073, ERR-116 | File/row/payload volume cap exceeded. |
| 415 | ERR-020 | Unsupported file type. |
| 422 | ERR-011, ERR-014, ERR-023, ERR-024, ERR-029, ERR-030, ERR-041, ERR-042, ERR-043, ERR-044, ERR-045, ERR-046, ERR-051, ERR-060, ERR-062, ERR-071, ERR-080, ERR-081, ERR-082, ERR-083, ERR-084, ERR-090, ERR-101, ERR-102, ERR-105, ERR-106, ERR-114 | Validly shaped request blocked by a business, integrity or safety check. |
| 423 | ERR-027, ERR-063 | Import target period locked, or exports locked by licence state. Connector staging uses ERR-027 just like a file import. |
| 500 | ERR-091, ERR-099 | Migration or unexpected internal failure (no raw exception/secret in the response). |
| 503 | ERR-012, ERR-070, ERR-072, ERR-092, ERR-093, ERR-115 | Required local/remote resource unavailable; connector retries exhausted are ERR-115, not local 429. |
| Job error only | ERR-004 | Terminal `cancelled` job, returned inside a `200` job poll. The cancel action itself acknowledges the request; it does not manufacture a failed HTTP response. |

Example, a locked connector pull rejected before any job or network request:
```http
POST /api/v1/projects/prj_9f2c41aa07e1/connector/pull
Content-Type: application/json
X-FPA-Token: <per-launch token>

{"period_id":"2025-P07","sources":["gl"]}
```
```json
{"code":"FP&A-ERR-027","message":"Period 2025-P07 is locked, so nothing can be imported into it.","hint":"Unlock the period (with a note) or choose another period","retryable":false,"details":{"period_id":"2025-P07"}}
```
HTTP `423`; no job, pull, batch or snapshot created. A missing GL after a read request is instead `422` / ERR-030. All resource ownership checks precede business checks so a foreign id yields ERR-001, not information about another project's locks.

### 1.2 Existing shared conventions (endpoint expansion in progress)

**Paths:** every route below is relative to the base URL; routes written without `/projects/{id}` (e.g. `/imports/{batch_id}`) are project-scoped through the resource id (the batch belongs to one project) — the server verifies ownership and answers ERR-001 for a foreign id.
**Job results:** `GET /jobs/{id}` → `{status, progress_pct, stage, error?, result?}` where `result` on `done` is the same body the synchronous form would return (import commit → `{committed counts, tb_status}`; rules → `{run_id, findings_new, findings_reopened, not_run: [{rule_id, reason}]}`; forecast → run; export → report). Jobs are kept 7 days; a job list `GET /projects/{id}/jobs?limit&cursor` exists for the S01 job tray.
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
| POST `/imports/{batch_id}/control-file` (multipart: ERP trial-balance export, `tb_check` shape) | attaches per-account declared movements to a staged GL batch (doc 06 §2 step 6) → per-account comparison | ERR-020, ERR-022 (unmapped TB shape) |
| POST `/imports/{batch_id}/enrich` | runs vendor enrichment from the period's AP sub-ledger batch (doc 06 §2 step 9) → `{matched, ambiguous, unmatched, already_had_vendor}` (job) | ERR-001 no AP batch for the period |
| POST `/projects/{id}/tb-check` `{period_id, batch_id}` | compares a committed `tb_check` batch with committed GL per account → `{differences[]: {account_id, erp_minor, app_minor, delta_minor}}`; zero differences flips the close item (doc 30) | ERR-030 period has no committed GL |

### Dynamics 365 connector (doc 26 §8, DEC-013; `routes_connector.py`) — read-only against the ERP; secrets never in a response body
| Endpoint | Behaviour | Errors |
|---|---|---|
| GET `/projects/{id}/connector` | `{enabled, kind: d365fo\|d365bc\|none, base_url, tenant_id, client_id, auth_mode, company, state: not_configured\|configured\|signed_in\|token_expired\|disconnected, signed_in_as?, last_pull?: {pull_id, period_id, finished_at, status, row_counts}, profile: {version, entity_check}}` — never a token or secret | |
| PUT `/projects/{id}/connector` `{kind, base_url, tenant_id, client_id, auth_mode, company?, client_secret?}` | saves non-secret fields to `connector.*` settings; `client_secret` (application mode) goes straight to the OS keyring and is never echoed; host validated against the allow-list shape | ERR-002 invalid, ERR-113 host not allowed / not https |
| POST `/projects/{id}/connector/sign-in` | delegated mode: starts auth-code+PKCE, returns `{authorize_url, port}`; the API opens the system browser; completion arrives on the callback below | ERR-110 not configured, ERR-111 sign-in failed |
| GET `/connector/callback?code&state` | loopback redirect target (`http://localhost:<port>/connector/callback`); exchanges the code, stores the MSAL cache in the keyring, returns a tiny HTML page "You can close this tab"; state mismatch → 400 and ERR-111 in the UI | ERR-111 |
| POST `/projects/{id}/connector/test` | token (silent) → companies list → entity check against the active profile → `{companies[], entity_check: {ok, missing[]: {source, entity, field?}, candidates[]}}` | ERR-110, ERR-112, ERR-113, ERR-114, ERR-117 |
| GET `/projects/{id}/connector/companies` | legal entities (F&O `LegalEntities`) / BC `companies` the signed-in identity can read | ERR-112, ERR-117 |
| GET/PUT `/projects/{id}/connector/profile` | active connector profile JSON (PUT creates a new version and re-runs the entity check) | ERR-002, ERR-114 |
| POST `/projects/{id}/connector/pull` `{period_id, sources: [gl\|ap\|tb\|budget\|masters], company?}` | → job `connector-pull` (doc 64); result `{pull_id, status: staged\|no_change, snapshot_sha256, batches[]: {batch_id, source_kind, rows_in, quarantined}, row_counts}`; batches are staged+validated, **not** committed (unless `connector.auto_commit_when_clean`) | ERR-110, ERR-112, ERR-113, ERR-114, ERR-115, ERR-116, ERR-117, ERR-118; ERR-027 period locked |
| POST `/projects/{id}/connector/check-changes` `{period_id}` | BC: `$count` with `lastModifiedDateTime gt <last pull>` → `{changed_rows, last_pull_at}`; F&O without a watermark field → `{changed_rows: null}` (UI says "pull to check") | ERR-110, ERR-112, ERR-115 |
| GET `/projects/{id}/connector/pulls?limit&cursor` | pull history (`connector_pulls`) | |
| POST `/projects/{id}/connector/disconnect` | removes the keyring entries + MSAL cache, sets state `disconnected`, keeps settings and history, audits | |

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
| GET `/exceptions/{finding_id}` (as above) includes `suggestion` (doc 90 `Suggestion`), `suggestion_status`, `suggestion_ref` | |
| POST `/exceptions/{finding_id}/suggestion/apply` `{mode: adjustment|journal|dismiss, note?}` | `adjustment` → doc-39 group of kind `correction_view` created from the suggestion lines, finding → `corrected`, returns `{pair_group_id}`; `journal` → lines queued for the period's rectification journal (`suggestion_status = queued`); `dismiss` → `dismissed` with mandatory note | ERR-046 suggestion has no journal lines / target period locked / queue consumed, ERR-005 already applied or queued, ERR-002 dismiss without note |
| GET `/projects/{id}/rectification-journal?period_id` | the queued lines for the period with their findings, totals (must net to zero) and the formats available | |
| GET `/projects/{id}/owners` + master-data CRUD under `/projects/{id}/master/{entities|accounts|cost-centres|vendors|owners}` | ERR-050 code duplicate |

### Forecast & scenarios (doc 08)
| POST `/projects/{id}/forecast/run` `{base_period_id, method_map?}` → job → run `{accuracy per group}` |
| GET `/forecast/runs?project_id` · GET `/forecast/runs/{id}` (lines paginated) · POST `/forecast/runs/{id}/lock` |
| POST `/projects/{id}/scenarios` `{name, base_run_id, deltas}` · GET compare `?scenario_ids=a,b,c&period_id` |
| PUT `/driver-values` bulk upsert (imports also create these) |

### Exports & commentary & settings
| POST `/projects/{id}/exports` `{kind:excel|pptx|pdf|journal, period_id, format?: d365fo_general_journal|d365bc_general_journal|generic_csv, finding_ids?}` → job → report `{report_id, path, sha256, checks}` | ERR-060 checks failed (tie-out details; generation blocked for pptx/pdf, excel allowed with Checks sheet flag); `journal`: ERR-046 queue empty, ERR-002 unknown format — on success the included findings move to `corrected` with `suggestion_status = exported` and `suggestion_ref = report_id` (doc 26 §7) |
| GET `/projects/{id}/reports` · GET `/reports/{id}/download` (file) |
| GET/PUT `/projects/{id}/commentary?period_id&scope` (PUT creates new version) · POST `/projects/{id}/commentary/draft` (AI; doc 11) → ERR-070 AI disabled/unconfigured, ERR-071 guardrail rejected draft (reasons) |
| GET/PUT `/projects/{id}/settings` (thresholds under `rule.*` keys) · GET `/projects/{id}/audit?limit&cursor` · POST `/projects/{id}/audit/verify` |
| GET `/projects/{id}/dashboard?period_id` | S01 aggregate DTO (KPIs, top variances, findings by severity/owner, close checklist, forecast accuracy) |

## 3. Contract tests (doc 14)
Every endpoint: happy path + each listed error + money-as-string assertion + pagination. OpenAPI generated from routes is diffed against this doc's table in CI (endpoint set equality). Connector endpoints are contract-tested against `tools/mock_d365.py` only (no tenant in CI) and additionally assert that no response body, log line or job payload contains a token-shaped string.

## 4. Addendum — expansion endpoints (docs 38–48; same conventions §1; routes_routes files in manifest)
| Area | Endpoints |
|---|---|
| Adjustments (39) | GET/POST `/projects/{id}/adjustments?period_id&status` · POST `/adjustments/{id}/apply` (balanced-group check; error ERR-023-style → new code FP&A-ERR-042 "Adjustment group doesn't balance (Δ shown)") · POST `/adjustments/{id}/reverse` · statements/bva accept `layer=gl|gl_adj` |
| Allocations (40) | CRUD `/projects/{id}/allocations` · POST `/allocations/{id}/run {period_id}` → job → adjustments created · GET run result |
| Assumptions (48) | CRUD `/projects/{id}/assumptions` · POST `/assumptions/{id}/approve` |
| Year-end (38) | POST `/projects/{id}/year-end/check {fiscal_year}` · POST `/projects/{id}/year-end/close {fiscal_year}` (creates closing adjustments + opening batch) · GET `/projects/{id}/year-end/rollforward {fiscal_year}` (Δ per account, must be 0) |
| Close (30) | GET `/projects/{id}/close?period_id` · PUT `/close/tasks/{id}` · POST `/close/sign-off` (ERR-080) |
| Reconcile (19I) | POST `/projects/{id}/reconcile/run {kind, period_id, batch_id}` → job · GET `/reconcile/{id}` (matches, unmatched both sides) · POST `/reconcile/{id}/sign-off` (ERR-081) |
| Alerts (19K) | GET `/projects/{id}/alerts?status` · POST `/alerts/{id}/ack|dismiss` |
| Planning (29) | GET/PUT `/projects/{id}/planning/{drivers|headcount|capex|debt|wc|cash13}` (bulk, versioned; PUT replaces the grid for the given scope and writes one audit row) · POST `/projects/{id}/planning/integrate {base_period_id, budget_version?, assumption_set?}` → job → forecast run (ERR-102 on articulation failure, with `details.link`) · GET `/projects/{id}/sensitivity?driver&from&to&steps&target` → table (ERR-108) · POST `/projects/{id}/goal-seek {target_kpi, target_value, driver}` → `GoalSeekResult` (ERR-108) · budget versions: GET/POST `/projects/{id}/budgets`, POST `/budgets/{version_id}/approve|lock|copy` (ERR-100), PUT `/budgets/{version_id}/lines` (grid edit, audited) · report builder `/projects/{id}/report-definitions` CRUD + POST `/report-definitions/{id}/render {period_id}` → job → report (ERR-062) · KPI builder `/projects/{id}/kpi-definitions` CRUD (ERR-104) |
| Diagnostics (18) | POST `/diagnostics/bundle` → job → zip path (logs redacted, no secrets) · GET `/projects/{id}/jobs` (job tray) |
All list endpoints paginate; all mutations audit; all money decimal strings (§1).
