# 05 — API CONTRACT

> Owner of: every HTTP endpoint between UI/CLI and engine (field-level payloads: doc 90; both are normative). Routes implement this 1:1 (parity test, doc 14). Base: `http://127.0.0.1:<port>/api/v1`. All money in JSON = string decimal in major units (`"125000.50"`) at the boundary, converted via money.py — never JSON numbers for money. Dates ISO. Errors: `{code:"FP&A-ERR-###", message:<plain language>, hint:<next action>, retryable:bool, details:{}}` (catalogue in `app/core/errors.py`, doc 15).

## 1. Conventions
### 1.1 HTTP outcomes and error transport (DEC-015)
Success: `200` synchronous read/action; `201` resource created; `202` asynchronous job accepted (`{job_id}`); `204` successful action with no body **only when the endpoint explicitly specifies it**. An accepted job is not a successful business result. `GET /jobs/{id}` returns `200` for every retained job, including `failed` and `cancelled`; its `error` carries the same catalogue body as a synchronous failure. An unknown/foreign job id is `404` / ERR-001. Cancellation is not HTTP status 499 and a provider throttle is not forwarded as local status 429.

The table is exhaustive for the **76 codes in doc 22 §2** (DEC-016 adds local-auth/origin/interruption codes), with each code in exactly one row. It applies when a failure is returned synchronously; after `202`, use the job's terminal state/error instead. Error bodies always use the public code prefix `FP&A-` (for example `FP&A-ERR-027`) and the shape `{code, message, hint, retryable, details}` from doc 22; retryability comes from that catalogue, not from the HTTP status. `details` may contain money **only as decimal strings in major units** via money.py, never JSON numbers/minor-unit integers. Per-endpoint detail schemas remain required by WI-0001; this table alone does not complete that item.

| HTTP status / transport | Catalogue codes | Meaning |
|---|---|---|
| 400 | ERR-002, ERR-005, ERR-013, ERR-015, ERR-022, ERR-025, ERR-026, ERR-031, ERR-032, ERR-085, ERR-104, ERR-108, ERR-109, ERR-111, ERR-113 | Invalid request, selector, confirmation, OAuth callback/sign-in input, or disallowed connector transport. ERR-111 does not represent local API-token authentication. |
| 401 | ERR-006 | Missing/invalid local launch token; no project or job lookup occurs. |
| 403 | ERR-007, ERR-117 | The signed-in Microsoft identity cannot read the selected company; this does not describe local API-token authentication. |
| 404 | ERR-001 | Requested resource missing or outside the current project. |
| 409 | ERR-003, ERR-010, ERR-016, ERR-028, ERR-040, ERR-050, ERR-052, ERR-061, ERR-100, ERR-103, ERR-107, ERR-110, ERR-112, ERR-118 | Resource state, uniqueness, referenced-record, connection state or concurrent-ledger-change conflict. |
| 413 | ERR-021, ERR-073, ERR-116 | File/row/payload volume cap exceeded. |
| 415 | ERR-020 | Unsupported file type. |
| 422 | ERR-011, ERR-014, ERR-023, ERR-024, ERR-029, ERR-030, ERR-041, ERR-042, ERR-043, ERR-044, ERR-045, ERR-046, ERR-051, ERR-060, ERR-062, ERR-071, ERR-080, ERR-081, ERR-082, ERR-083, ERR-084, ERR-090, ERR-101, ERR-102, ERR-105, ERR-106, ERR-114 | Validly shaped request blocked by a business, integrity or safety check. |
| 423 | ERR-027, ERR-063 | Import target period locked, or exports locked by licence state. Connector staging uses ERR-027 just like a file import. |
| 500 | ERR-091, ERR-099 | Migration or unexpected internal failure (no raw exception/secret in the response). |
| 503 | ERR-012, ERR-070, ERR-072, ERR-092, ERR-093, ERR-115 | Required local/remote resource unavailable; connector retries exhausted are ERR-115, not local 429. |
| Job error only | ERR-004, ERR-008 | Terminal `cancelled` (ERR-004) or `failed` after interruption (ERR-008) job, returned inside a `200` job poll. The cancel action itself acknowledges the request; it does not manufacture a failed HTTP response. |

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

### 1.2 Auth, project context and paths (DEC-016)
Auth is `X-FPA-Token` on **every** `/api/v1` operation, including `/health`, job polling and download. Failure: 401/ERR-006; Origin/Host rejection: 403/ERR-007. These common failures apply to every endpoint below in addition to its domain codes. Doc 12 §1.1 defines constant-time checking, exact-origin CORS, CLI and OPTIONS. The **only** data-endpoint exception is the root OAuth callback `/connector/callback`, outside `/api/v1`, protected by single-use expiring state + S256 PKCE. It returns constant HTML, not JSON, and never accepts project selection from the browser.

Project-scoped operations require `X-FPA-Project: <project_id>`, including resource-only routes (`/imports/{batch_id}`, `/exceptions/{finding_id}`, `/mapping-profiles`, `/driver-values`, `/close/sign-off`, `/jobs/{id}` and `/diagnostics/bundle`). A project path/query/body selector must equal this header. Every nested id (batch, finding, owner, account, profile, version, run, scenario, report, job) is checked in that project before state checks; mismatch/missing/foreign → 404/ERR-001. Missing project header → 400/ERR-002. Only `/health` and `/projects` GET/POST are app-scoped (no project header). No implicit last-opened/global-current-project state exists in the API.

### 1.3 Wire types, paging and idempotency (DEC-016)
Requests reject unknown fields, duplicate query parameters and unknown query keys (400/ERR-002). JSON bodies are UTF-8 objects, never implicit form data; file upload is explicitly multipart. Required vs nullable vs optional is distinct. Unspecified request bodies are forbidden; no-body actions send no body. Dates are `YYYY-MM-DD`; timestamps are RFC3339 UTC `Z`. Period ids are `<FY-start-year>-P<01..12>` with a four-digit Gregorian start year 0001..9999 (doc 02 §2); year 0000 is invalid. Financial decimals (money, percentages, ratios, drivers) are strings: no exponent syntax, separators, leading plus or floats; money permits 0/2/3 fraction digits according to the project's fixed exponent (doc 27), never UI arithmetic. Responses format money with exactly that exponent; input with excess precision is rejected rather than silently rounded. JSON integer fields are counts/indexes/version numbers, not money. Public `amount_minor` / `delta_minor` / `erp_minor` / `app_minor` / `rollforward_delta_minor` are replaced by `amount` / `delta` / `erp` / `app` / `rollforward_delta` decimal strings; storage is unchanged. A monetary settings key ending in `_minor` retains its key but its wire `value` is a major-unit decimal string, translated through money.py. Binary content and raw source cells have their explicit formats; they are not computed money values.

A list is `Page<T> = {items: T[], next_cursor: string|null}`. Default limit 100, allowed integer 1..1000; cursor omitted on first page, null ends traversal. Default sort is resource id ascending; temporal histories use `(at,id)` ascending; financial line grids use `(period_id,entity_id,account_id,cost_centre_id,id)` ascending with null cost centre before text. No client-defined SQL sort. Opaque signed cursors bind project, operation, selectors, normalized filters, sort and the read snapshot/revision. A tampered, wrong-scope or expired cursor → ERR-002; changed snapshot/revision → ERR-003 (restart at first page), never silent duplicated/missing rows. Multi-page financial results pin their batch/version/run snapshot for the job-history retention period (7 days). Finite computed aggregates (statement lines, a single snapshot's check list, KPI tiles) are typed bounded arrays, not mutable resource lists; no pagination parameters unless the endpoint declares them. Drill uses Page<Voucher> (not a competing `vouchers` envelope); voucher-row drill is separately paged so a giant voucher cannot defeat the 250k-row posture.

`Idempotency-Key` (non-empty printable ASCII, max 128 characters) is required for all job-creating POSTs, import commit, export and suggestion consumption; optional on other mutations. Scope = project + method + canonical path + key. Canonical input covers selectors/query and JSON (sorted object keys, array order retained), upload byte hashes and chosen settings/profile versions; never stores secrets. Same key/same input returns the original status/body/job id and creates no new side effects, including after restart; same key/different input → ERR-005. Records are retained for the project lifetime (job list retention does not permit repeating a side effect); replay after job history expiry returns its original job receipt and the referenced job poll may be ERR-001. A new key starts a new action only if lifecycle guards permit it. Without a key the operation is not replay-safe unless its endpoint explicitly says so. Second suggestion consumption with a new key → ERR-046 `already_consumed`; repeated queued-journal export cannot re-consume a finding. Atomicity and ownership checks still apply on every replay, before returning cached data.

Editable versioned objects expose integer `version≥1`; PUT and state-changing actions on such objects require `expected_version` in their JSON body. Mismatch → ERR-003 before mutation; success increments version and writes one before/after audit event in the same transaction. Bulk actions validate **all** ids/versions before writing; no partial success. Locks are rechecked inside the write transaction, not merely at job enqueue. The identity of the local analyst is supplied by the shell context, not an untrusted request `actor` field; business attestations still carry signer labels. No financial mutation is permitted during a detected audit-chain break (ERR-090); only reads, verify, restore and diagnostics remain available.

### 1.4 Job envelopes (DEC-016)
Jobs are project-scoped and persisted; one heavy job per project runs FIFO. `202 {job_id}` is an acceptance receipt; polling GET returns 200 even when the job failed. `Job` includes `job_id, project_id, kind, status, stage, progress_pct, created_at, started_at, finished_at, cancellable, error, result`. Null fields are explicit. Queued/running jobs have null result/error; done has the exact per-kind result and null error; failed has null result and a catalogue error; cancelled has null result and ERR-004. Restarted running jobs become failed/ERR-008; queued jobs remain queued but recheck all guards before execution. Timestamps and progress are injected, never sampled in calculations. `progress_pct` is an integer 0..100 or null (indeterminate); done = 100. Connector progress also has nullable `{source,page,pages,rows,count}`; never URLs/tokens/financial rows.

Cancel: POST `/jobs/{id}/cancel`, no body, 200 `{job_id,status,cancel_requested,cancellable}`. Queued → cancelled immediately; running cancellable → request flag until the next safe boundary; during irreversible transaction/render/publish returns `cancel_requested:false,cancellable:false` without interrupting that stage; terminal job returns its state unchanged. Unknown job → ERR-001. Completion may win the cancellation race; final poll is authoritative. No success is reported until the final database/file publication is durable. The full result union and stages are owned by doc 64; `docs/api_job_schemas.json` is the normative JSON Schema attachment for this WI, indexed in doc 90. Its document-only tests are `tests/docs/test_api_job_contract.py`; no API runtime is claimed by a schema test.

## 2. Endpoints
### Health & projects
| Method & path | In | Out | Errors |
|---|---|---|---|
| GET `/health` | — | `{status:"ok", version}` | — |
| GET `/projects` | — | list of project summaries | — |
| POST `/projects` | `{name, base_currency, fy_start_month, calendar_type}` | project | ERR-010 name exists |
| GET `/projects/{id}` | — | project + period list + close progress | ERR-001 not found |
| POST `/projects/{id}/periods/{period_id}/lock` | `{note}` | period (locked) | ERR-011 open findings high-severity (returns list; override requires `{force:true, note}` audited) |
| POST `/projects/{id}/backup` / `/restore` | `{path}` | 202 job: backup → BackupManifest; restore → RestoreResult (doc 64) | ERR-012 path not writable |

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
| POST `/projects/{id}/tb-check` `{period_id, batch_id}` | compares a committed `tb_check` batch with committed GL per account → `{differences[]: {account_id, erp, app, delta} (money decimal strings)}`; zero differences flips the close item (doc 30) | ERR-030 period has no committed GL |

### Dynamics 365 connector (doc 26 §8, DEC-013; `routes_connector.py`) — read-only against the ERP; secrets never in a response body
| Endpoint | Behaviour | Errors |
|---|---|---|
| GET `/projects/{id}/connector` | `{enabled, kind: d365fo\|d365bc\|none, base_url, tenant_id, client_id, auth_mode, company, state: not_configured\|configured\|signed_in\|token_expired\|disconnected, signed_in_as?, last_pull?: {pull_id, period_id, finished_at, status, row_counts}, profile: {version, entity_check}}` — never a token or secret | |
| PUT `/projects/{id}/connector` `{kind, base_url, tenant_id, client_id, auth_mode, company?, client_secret?}` | saves non-secret fields to `connector.*` settings; `client_secret` (application mode) goes straight to the OS keyring and is never echoed; host validated against the allow-list shape | ERR-002 invalid, ERR-113 host not allowed / not https |
| POST `/projects/{id}/connector/sign-in` | delegated mode: starts auth-code+PKCE, returns `{authorize_url, port}`; the API opens the system browser; completion arrives on the callback below | ERR-110 not configured, ERR-111 sign-in failed |
| GET root `/connector/callback?code&state` (outside `/api/v1`) | loopback redirect target (`http://localhost:<port>/connector/callback`); exchanges the code, stores the MSAL cache in the keyring, returns a tiny HTML page "You can close this tab"; state mismatch → 400 and ERR-111 in the UI | ERR-111 |
| POST `/projects/{id}/connector/test` | token (silent) → companies list → entity check against the active profile → `{companies[], entity_check: {ok, checked_at, missing[]: {source, entity, field: string|null, candidates[]}}}` | ERR-110, ERR-112, ERR-113, ERR-117 (missing entities are `entity_check.ok=false`; pull refuses them with ERR-114) |
| GET `/projects/{id}/connector/companies` | cached legal entities / BC companies from the last explicit test; never starts network; `{items: Company[], next_cursor, tested_at: timestamp|null}` | ERR-112, ERR-117 |
| GET/PUT `/projects/{id}/connector/profile` | active connector profile JSON (PUT creates a new version and re-runs the entity check) | ERR-002 (invalid local profile); remote misses returned in saved profile entity_check, pull blocked ERR-114 |
| POST `/projects/{id}/connector/pull` `{period_id, sources: [gl\|ap\|tb\|budget\|masters], company?}` | → job `connector-pull` (doc 64); result `{pull_id, status: staged\|no_change, snapshot_sha256, batches[]: {batch_id, source_kind, rows_in, quarantined}, row_counts}`; batches are staged+validated, **not** committed (unless `connector.auto_commit_when_clean`) | ERR-110, ERR-112, ERR-113, ERR-114, ERR-115, ERR-116, ERR-117, ERR-118; ERR-027 period locked |
| POST `/projects/{id}/connector/check-changes` `{period_id}` | 202 job `connector-check-changes`; result (doc 64): BC: `$count` with `lastModifiedDateTime gt <last pull>` → `{changed_rows, last_pull_at}`; F&O without a watermark field → `{changed_rows: null}` (UI says "pull to check") | ERR-110, ERR-112, ERR-115 |
| GET `/projects/{id}/connector/pulls?limit&cursor` | pull history (`connector_pulls`) | |
| POST `/projects/{id}/connector/disconnect` | removes the keyring entries + MSAL cache, sets state `disconnected`, keeps settings and history, audits | |

### Statements, BvA, drill (doc 03)
| GET `/projects/{id}/statements?period_id&entity_id?&statement=pl|bs|cf` | statement lines `{line_key,label,amount,presentation_sign,drill_key}` | ERR-030 period has no committed GL |
| GET `/projects/{id}/bva?period_id&budget_version&grain` | variance rows (doc 03 §5 fields) | |
| GET `/projects/{id}/kpi?period_id` | KPI list `{key,label,value|n/a,reason?,formula}` | |
| GET `/projects/{id}/drill?drill_key&level=vouchers\|rows` | default level vouchers: Page<VoucherSummary>; level rows with row_drill_key: Page<SourceRow> (doc 90); no nested unbounded rows array | |
| GET `/projects/{id}/bridge?period_id&account_group` | components or `{available:false, reason}` | |

### Exceptions (doc 07)
| POST `/projects/{id}/exceptions/run` `{period_id}` → job; GET findings list with filters `status,severity,owner_id,rule_id,q` | |
| GET `/exceptions/{finding_id}` | finding + evidence + history | |
| POST `/exceptions/{finding_id}/transition` `{to_status, note?, waive_reason?, waive_days?}` | ERR-040 illegal transition, ERR-041 waive needs reason+expiry | |
| POST `/exceptions/bulk-assign` `{finding_ids, owner_id, due_date}` | |
| GET `/exceptions/{finding_id}` (as above) includes `suggestion` (doc 90 `Suggestion`), `suggestion_status`, `suggestion_ref` | |
| POST `/exceptions/{finding_id}/suggestion/apply` `{mode: adjustment|journal|dismiss, note?}` | `adjustment` → doc-39 group of kind `correction_view` created from the suggestion lines, finding → `corrected`, returns `{pair_group_id}`; `journal` → lines queued for the period's rectification journal (`suggestion_status = queued`); `dismiss` → `dismissed` with mandatory note | ERR-046 suggestion has no journal lines / target period locked / already consumed with a new key; ERR-005 same key with changed payload, ERR-002 dismiss without note |
| GET `/projects/{id}/rectification-journal?period_id` | the queued lines for the period with their findings, totals (must net to zero) and the formats available | |
| GET `/projects/{id}/owners` + master-data CRUD under `/projects/{id}/master/{entities|accounts|cost-centres|vendors|owners}` | ERR-050 code duplicate |

### Forecast & scenarios (doc 08)
| POST `/projects/{id}/forecast/run` `{base_period_id, method_map?}` → job → run `{accuracy per group}` |
| GET `/forecast/runs?project_id` · GET `/forecast/runs/{id}` (lines paginated) · POST `/forecast/runs/{id}/lock` |
| POST `/projects/{id}/scenarios` `{name, base_run_id, deltas}` · GET compare `?scenario_ids=a,b,c&period_id` |
| PUT `/driver-values` bulk upsert (imports also create these) |

### Exports & commentary & settings
| POST `/projects/{id}/exports` `{kind:excel|pptx|pdf|journal|all, period_id, format?: d365fo_general_journal|d365bc_general_journal|generic_csv, finding_ids?}` → job → ExportResult `{snapshot,reports[]}` (doc 64 §3; one report for a single kind, three for kind=all) | ERR-060 checks failed (tie-out details; generation blocked for pptx/pdf, excel allowed with Checks sheet flag); `journal`: ERR-046 queue empty, ERR-002 unknown format — on success the included findings move to `corrected` with `suggestion_status = exported` and `suggestion_ref = report_id` (doc 26 §7) |
| GET `/projects/{id}/reports` · GET `/reports/{id}/download` (file) |
| GET/PUT `/projects/{id}/commentary?period_id&scope` (PUT creates new version) · POST `/projects/{id}/commentary/draft` (202 job `ai-draft`; doc 11) → ERR-070 AI disabled/unconfigured, ERR-071 guardrail rejected draft (reasons) |
| GET/PUT `/projects/{id}/settings` (thresholds under `rule.*` keys) · GET `/projects/{id}/audit?limit&cursor` · POST `/projects/{id}/audit/verify` (202 job `audit-verify`) |
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

## 5. Explicit job transport endpoints (DEC-016; remaining route groups in §2/§4 still need expansion)
These three complete transport contracts use doc 64's closed result union; they are not generic-object escape hatches. Money in every reachable result/error schema is a major-unit decimal string. All require token, exact local Host/Origin and `X-FPA-Project` as in §1.2. No request starts a connector/AI call merely by reading jobs.

### 5.1 GET `/jobs/{id}`
- **Auth / scope:** local token + project header; `id` is an opaque job id in that project. Auth before ownership before state disclosure.
- **Request:** path `id` (Id); no body; no query parameters. Unknown query/body → 400/ERR-002.
- **Response:** 200 Job (`api_job_schemas.json` root / `$defs.Job`), with all required nullable fields; result is selected by kind **and** terminal status (doc 64 §1/§3). Failed/cancelled jobs are still a successful 200 poll, not HTTP 500/499.
- **Failures:** 400 ERR-002; 401 ERR-006; 403 ERR-007; 404 ERR-001 (unknown, foreign or expired job); 500 ERR-099; 503 ERR-092. Error bodies use ErrorBody from the schema attachment; lookup failures do not include foreign project identifiers.
- **Pagination:** none; large output detail is behind the result's paged resource, never embedded transactions here.
- **Idempotency:** read-only; Idempotency-Key not accepted/required. Repeated polls may show progress, never create work. Cache-Control no-store.
- **Example:** doc 63 §3 gives the complete 200 import-commit envelope; all 18 done-kind examples are in the attachment's `examples`. A failed job has `result:null`, an ErrorBody and `cancellable:false`, not a partial result.

### 5.2 GET `/projects/{id}/jobs`
- **Auth / scope:** local token + project header matching path `id`; path id is a project id, not a job id.
- **Request:** no body; optional query `limit` integer 1..1000 default 100, `cursor` opaque string, `kind` one doc-64 kind, `status` one queued/running/done/failed/cancelled. Duplicate/unknown query keys rejected. Sort `(created_at,job_id)` ascending; cursor binds filters and the list revision (§1.3). No user-defined sort expression.
- **Response:** 200 JobPage `{items:Job[],next_cursor:string|null}` (`$defs.JobPage`). Empty project → `{"items":[],"next_cursor":null}`. The page contains at most the requested limit; null cursor ends traversal. The page/list snapshot is immutable for that traversal; a poll of an individual item can be newer.
- **Failures:** 400 ERR-002 (invalid filter/limit/cursor); 401 ERR-006; 403 ERR-007; 404 ERR-001 (project); 409 ERR-003 (changed list revision); 500 ERR-099; 503 ERR-092.
- **Pagination / idempotency:** §1.3 Page protocol; read-only, no Idempotency-Key. List reads never launch/retry jobs. Cache-Control no-store.
- **Example:** GET `/projects/prj_9f2c41aa07e1/jobs?kind=connector-pull&status=running&limit=100` → 200 `{"items":[],"next_cursor":null}` when no matching pull exists; non-empty items are full typed Job envelopes, not summary objects with omitted required fields.

### 5.3 POST `/jobs/{id}/cancel`
- **Auth / scope:** local token + project header; path `id` must name a job in that project. Auth/ownership are rechecked even on an idempotency replay.
- **Request:** no body and no query; optional Idempotency-Key under §1.3, otherwise naturally repeat-safe (cannot undo completion).
- **Response:** 200 CancelResponse (`$defs.CancelResponse`), required `job_id`, `status`, `cancel_requested`, `cancellable`; six allowed variants in doc 64 §2.1. A refusal during an irreversible stage is an honest 200 response with both flags false, not a claim that cancellation happened.
- **Failures:** 400 ERR-002/ERR-005 (invalid request / optional key reused with changed input); 401 ERR-006; 403 ERR-007; 404 ERR-001; 500 ERR-099; 503 ERR-092/ERR-093. Actual terminal cancellation is ERR-004 inside the later job poll, not a failed cancel HTTP response.
- **Pagination:** none. Accepted cancellation requests audit the decision; repeated terminal requests do not create a new job. Completion/cancellation arbitration is atomic (doc 64), never inferred by the browser.
- **Example:** running non-cancellable commit → 200 `{"job_id":"job_commit_0001","status":"running","cancel_requested":false,"cancellable":false}`. Queued cancellation → 200 `{"job_id":"job_commit_0001","status":"cancelled","cancel_requested":true,"cancellable":false}`; a repeated request after that returns cancelled with both flags false.
