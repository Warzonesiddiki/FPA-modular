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
X-FPA-Project: prj_9f2c41aa07e1
Idempotency-Key: locked-pull-2025-P07-1

{"period_id":"2025-P07","sources":["gl"]}
```
```json
{"code":"FP&A-ERR-027","message":"Period 2025-P07 is locked, so nothing can be imported into it.","hint":"Unlock the period (with a note) or choose another period","retryable":false,"details":{"period_id":"2025-P07"}}
```
HTTP `423`; no job, pull, batch or snapshot created. A missing GL after a read request is instead `422` / ERR-030. All resource ownership checks precede business checks so a foreign id yields ERR-001, not information about another project's locks.

### 1.2 Auth, project context and paths (DEC-016)
Auth is `X-FPA-Token` on **every** `/api/v1` operation, including `/health`, job polling and download. Failure: 401/ERR-006; Origin/Host rejection: 403/ERR-007. These common failures apply to every endpoint below in addition to its domain codes. Doc 12 §1.1 defines constant-time checking, exact-origin CORS, CLI and OPTIONS. The **only** data-endpoint exception is the root OAuth callback `/connector/callback`, outside `/api/v1`, protected by single-use expiring state + S256 PKCE. It returns constant HTML, not JSON, and never accepts project selection from the browser.

Project-scoped operations require `X-FPA-Project: <project_id>`, including resource-only routes (`/imports/{batch_id}`, `/exceptions/{finding_id}`, `/mapping-profiles`, `/driver-values`, `/close/sign-off`, `/jobs/{id}` and `/diagnostics/bundle`). A project path/query/body selector must equal this header. Every nested id (batch, finding, owner, account, profile, version, run, scenario, report, job) is checked in that project before state checks; mismatch/missing/foreign → 404/ERR-001. Missing project header → 400/ERR-002. Only `/health`, `/projects` GET/POST and `/projects/sample` POST are app-scoped (no project header). No implicit last-opened/global-current-project state exists in the API.

### 1.3 Wire types, paging and idempotency (DEC-016)
Requests reject unknown fields, duplicate query parameters and unknown query keys (400/ERR-002). JSON bodies are UTF-8 objects with duplicate member names rejected before validation, never implicit form data; file upload is explicitly multipart. Required vs nullable vs optional is distinct. Unspecified request bodies are forbidden; no-body actions send no body. Dates are `YYYY-MM-DD`; timestamps are RFC3339 UTC `Z`. Period ids are `<FY-start-year>-P<01..12>` with a four-digit Gregorian start year 0001..9999 (doc 02 §2); year 0000 is invalid. Financial decimals (money, percentages, ratios, drivers) are strings: no exponent syntax, separators, leading plus or floats; money permits 0/2/3 fraction digits according to the project's fixed exponent (doc 27), never UI arithmetic. Responses format money with exactly that exponent; input with excess precision is rejected rather than silently rounded. JSON integer fields are counts/indexes/version numbers, not money. Public `amount_minor` / `delta_minor` / `erp_minor` / `app_minor` / `rollforward_delta_minor` are replaced by `amount` / `delta` / `erp` / `app` / `rollforward_delta` decimal strings; storage is unchanged. A monetary settings key ending in `_minor` retains its key but its wire `value` is a major-unit decimal string, translated through money.py. Binary content and raw source cells have their explicit formats; they are not computed money values.

A list is `Page<T> = {items: T[], next_cursor: string|null}`. Default limit 100, allowed integer 1..1000; cursor omitted on first page, null ends traversal. Default sort is resource id ascending; temporal histories use `(at,id)` ascending; financial line grids use `(period_id,entity_id,account_id,cost_centre_id,id)` ascending with null cost centre before text. No client-defined SQL sort. Opaque signed cursors bind project, operation, selectors, normalized filters, sort and the read snapshot/revision. A tampered, wrong-scope or expired cursor → ERR-002; changed snapshot/revision → ERR-003 (restart at first page), never silent duplicated/missing rows. Multi-page financial results pin their batch/version/run snapshot for the job-history retention period (7 days). Finite computed aggregates (statement lines, a single snapshot's check list, KPI tiles) are typed bounded arrays, not mutable resource lists; no pagination parameters unless the endpoint declares them. Drill uses Page<Voucher> (not a competing `vouchers` envelope); voucher-row drill is separately paged so a giant voucher cannot defeat the 250k-row posture.

`Idempotency-Key` (non-empty printable ASCII, max 128 characters) is required for all job-creating POSTs, import commit, export and suggestion consumption; optional on other mutations. Scope = project + method + canonical path + key (app-scoped project creation uses the installation scope in §6.0). Canonical input covers selectors/query and JSON (sorted object keys, array order retained), upload byte hashes and chosen settings/profile versions; never stores secrets. Same key/same input returns the original status/body/job id and creates no new side effects, including after restart; same key/different input → ERR-005. Records are retained for the project lifetime (job list retention does not permit repeating a side effect); replay after job history expiry returns its original job receipt and the referenced job poll may be ERR-001. A new key starts a new action only if lifecycle guards permit it. Without a key the operation is not replay-safe unless its endpoint explicitly says so. Second suggestion consumption with a new key → ERR-046 `already_consumed`; repeated queued-journal export cannot re-consume a finding. Atomicity and ownership checks still apply on every replay, before returning cached data.

Editable versioned objects expose integer `version≥1`; PUT and state-changing actions on such objects require `expected_version` in their JSON body. Mismatch → ERR-003 before mutation; success increments version and writes one before/after audit event in the same transaction. Bulk actions validate **all** ids/versions before writing; no partial success. Locks are rechecked inside the write transaction, not merely at job enqueue. The identity of the local analyst is supplied by the shell context, not an untrusted request `actor` field; business attestations still carry signer labels. No financial mutation is permitted during a detected audit-chain break (ERR-090); only reads, verify, restore and diagnostics remain available.

### 1.4 Job envelopes (DEC-016)
Jobs are project-scoped and persisted; one heavy job per project runs FIFO. `202 {job_id}` is an acceptance receipt; polling GET returns 200 even when the job failed. `Job` includes `job_id, project_id, kind, status, stage, progress_pct, created_at, started_at, finished_at, cancellable, error, result`. Null fields are explicit. Queued/running jobs have null result/error; done has the exact per-kind result and null error; failed has null result and a catalogue error; cancelled has null result and ERR-004. Restarted running jobs become failed/ERR-008; queued jobs remain queued but recheck all guards before execution. Timestamps and progress are injected, never sampled in calculations. `progress_pct` is an integer 0..100 or null (indeterminate); done = 100. Connector progress also has nullable `{source,page,pages,rows,count}`; never URLs/tokens/financial rows.

Cancel: POST `/jobs/{id}/cancel`, no body, 200 `{job_id,status,cancel_requested,cancellable}`. Queued → cancelled immediately; running cancellable → request flag until the next safe boundary; during irreversible transaction/render/publish returns `cancel_requested:false,cancellable:false` without interrupting that stage; terminal job returns its state unchanged. Unknown job → ERR-001. Completion may win the cancellation race; final poll is authoritative. No success is reported until the final database/file publication is durable. The full result union and stages are owned by doc 64; `docs/api_job_schemas.json` is the normative JSON Schema attachment for this WI, indexed in doc 90. Its document-only tests are `tests/docs/test_api_job_contract.py`; no API runtime is claimed by a schema test.

## 2. Endpoints
### Health & projects
Health, project list/create/detail, period list/create/detail: explicit contracts in §6. These are separate methods and paths, not CRUD shorthand.

Remaining project operations awaiting expansion in WI-0001:
- Sample workspace creation, typed-confirmation deletion and start-close/unlock: §7 (FR-PRJ-002/003/005). Financial sample loading still uses the ordinary import pipeline.
- POST `/projects/{id}/periods/{period_id}/lock`: legacy request `{note, force?}` → Period; ERR-011 for open High findings unless forced with an audited note. Lock/re-lock and impact-review guards remain to expand (FR-PRJ-003; docs 23/41).
- POST `/projects/{id}/backup` and POST `/projects/{id}/restore`: legacy request `{path}` → 202 JobReceipt; results BackupManifest / RestoreResult (doc 64), ERR-012 for unavailable paths. Full input/root-selection/integrity contracts remain to expand (FR-PRJ-004).

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

## 6. Health, project metadata and fiscal-year materialisation (DEC-017)
These seven endpoint sections replace the corresponding shorthand in §2. Sample workspace/deletion/start-close/unlock are expanded in §7; backup/restore, lock/re-lock and impact review still require expansion; §6 does not claim that those operations are complete. Contracts are documentation only until M3. Field names below are authoritative; doc 90 is their index. JSON Schema definitions are in the existing `api_job_schemas.json` attachment (shared primitives/errors are not copied into another registry).

### 6.0 Field contracts and shared behaviour
All properties are required unless explicitly optional; nullable properties must be present. All objects are closed. Dates are validated Gregorian `YYYY-MM-DD`; timestamps use §1.3 UTC Z. No money fields occur here; any reachable error money remains a decimal string. No ledger rows, filesystem paths, connection profiles or credentials are exposed by these DTOs.

| Schema | Fields, types, constraints |
|---|---|
| Health | `status` constant `ok`; `version` non-empty string ≤64 characters, no whitespace/control characters, exactly the installed `app.__version__` (not a database schema version). This is liveness, not a financial-integrity verdict. |
| ProjectName | String 1..80 Unicode code points, NFC-normalised, no leading/trailing whitespace or ASCII controls (U+0000..001F, U+007F). Reject non-canonical input with ERR-002; do not silently rename it. Active names are unique under Unicode casefold after NFC. Names are display text, never folder names or markup. |
| ProjectId | String matching `prj_` followed by exactly 12 lower-case hex characters (doc 02). Server allocates with collision retry; clients never choose it. |
| ProjectCreate | `name`: ProjectName; `base_currency`: one code from doc 27 §1's v1 table; `fy_start_month`: integer 1..12; `calendar_type`: constant `monthly`; `fiscal_year`: integer 1..9998 (initial FY start year, not current year inferred by the server). No client `project_id`, `is_sample`, exponent, path, version or timestamps. |
| Project | `project_id`: ProjectId; `name`: ProjectName; `base_currency`: as ProjectCreate; `currency_exponent`: derived from doc 27 §1, exactly 0/2/3 as appropriate to that code; `fy_start_month`: integer 1..12; `calendar_type`: `monthly`; `is_sample`: boolean, assigned only by the server; `version`: integer ≥1; `created_at`, `updated_at`: Timestamp, updated_at ≥ created_at. Metadata only: **no embedded periods or close_progress**. Read periods using §6.5/§6.7; close progress remains the separate `/projects/{id}/close?period_id` resource. |
| CreatedProject | Project restricted to `is_sample=false`, `version=1`, and equal created_at/updated_at. Used only for the successful create response, not general reads. |
| Period | `project_id`: ProjectId; `period_id`: PeriodId (doc 02, four-digit FY); `fiscal_year`: integer 1..9999; `period_no`: integer 1..12; `start_date`, `end_date`: Date; `status`: open/closing/locked; `locked_at`: Timestamp or null; `lock_note`: string 1..500 or null; `version`: integer ≥1; `created_at`, `updated_at`: Timestamp. Exact id = zero-padded fiscal_year + `-P` + two-digit period_no. Dates must be that month's first/last day under the project's FY start month. locked status requires locked_at; open/closing have locked_at and lock_note null (older locks remain in audit). A non-null note cannot be whitespace-only or contain ASCII controls. |
| ProjectPage | `items`: Project array, ≤ requested limit; `next_cursor`: non-empty opaque string ≤4096 or null. |
| PeriodPage | `items`: Period array, ≤ requested limit; `next_cursor`: same cursor type. Every item belongs to the selected project. |
| FiscalYearCreate | `fiscal_year`: integer 1..9998. This conservative full-year creation bound leaves a representable following calendar year for every FY-start month; Period's larger read bound does not authorise overflow on writes. |
| FiscalYearPeriods | `project_id`: ProjectId; `fiscal_year`: integer 1..9998; `periods`: exactly 12 Period objects ordered P01…P12 for this project/FY, with no duplicate/missing period. This bounded action result is not a Page. |
| ProjectListQuery | Optional `limit`: integer 1..1000, default 100; `cursor`: non-empty opaque string ≤4096; `is_sample`: boolean filter, omitted = both sample and real projects. |
| PeriodListQuery | Optional `limit`, `cursor` as above; `fiscal_year`: integer 1..9999; `status`: open/closing/locked. Omitted filters mean all retained years/states. |

Query integers use ASCII digits only on the wire; booleans are exactly `true`/`false`. No coercion of blank, `1.0`, `1e2`, `yes`, repeated keys or unknown keys. Query DTO schemas describe the parsed values; HTTP parsing needs its own M3 tests. Body integers are JSON integers, not numeric strings or booleans. The request parser must reject duplicate JSON object members before schema validation; it must not choose one silently.

Shared auth is §1.2: token + exact Host/Origin. App-scoped health/project listing/creation do not select a project; a supplied project header never restricts those app-wide results. Project-scoped routes require the header equal to the path ProjectId. Missing header → ERR-002; unknown/foreign/deleted project or period → ERR-001, before state disclosure. For §6 failures the complete body is the attachment's `$defs.ErrorNNN`; e.g. ERR-002 uses Error002, not an untyped details object. HTTP→code mapping is §1.1. All responses use `Cache-Control: no-store`; a read never creates periods, runs checks or opens an external socket.

App-scoped project-creation receipts are scoped to **installation + method + canonical path + key**, survive launch-token rotation/restart and atomically identify the resulting project. A retry is matched before re-deriving default settings. Project-scoped keys retain §1.3 scope. A replay must not resurrect a deleted project: retain a minimal receipt tombstone (project id + request digest, not the deleted response/name), and return 404/ERR-001. This is a necessary exception to replaying the original success body after deletion, not permission to recreate it. Filesystem publication, metadata and receipt must recover together after a crash; never return 201 for a half-created project.

### 6.1 GET `/health`
- **Auth / scope:** app-scoped; token required, no project lookup.
- **Request:** no path variables, query or body.
- **Response:** 200 Health (§6.0); `status=ok` says the process can serve requests, not that every project's audit chain is valid.
- **Failures:** 400 ERR-002 (body/query supplied); 401 ERR-006; 403 ERR-007; 500 ERR-099. No database requirement for liveness.
- **Pagination:** none.
- **Idempotency:** read-only; no Idempotency-Key; no audit mutation or background work.
- **Example:** GET `/api/v1/health` → 200 `{"status":"ok","version":"0.1.0"}` for an installation at that example version.

### 6.2 GET `/projects`
- **Auth / scope:** app-scoped; token required. List all active projects in this installation, not only a last-opened one.
- **Request:** no body/path variables; ProjectListQuery (§6.0), default limit 100 and no filters.
- **Response:** 200 ProjectPage (§6.0). Entries are full Project metadata, not a second summary shape. Trashed projects are absent; sample flags cannot be removed by a filter.
- **Failures:** 400 ERR-002; 401 ERR-006; 403 ERR-007; 409 ERR-003 (cursor revision unavailable/changed); 500 ERR-099; 503 ERR-092.
- **Pagination:** project_id ascending; cursor binds installation, filters and the project-list revision. A changed/unavailable revision returns ERR-003, not silently skipped projects. A tampered/wrong-filter/expired cursor returns ERR-002.
- **Idempotency:** read-only; no key. No DB migration, project repair, demo loading or connector action on a GET.
- **Example:** GET `/api/v1/projects?is_sample=false&limit=100` → 200 `{"items":[],"next_cursor":null}` in a fresh installation. A nonempty page is shown in doc 63 §8.

### 6.3 POST `/projects`
- **Auth / scope:** app-scoped; token required; Idempotency-Key required.
- **Request:** ProjectCreate (§6.0); no query/path variables. Initial fiscal_year is explicit. Reject unsupported currency/calendar and client-supplied server fields with ERR-002. Compare active names using §6.0's canonical casefold key; duplicate → ERR-010.
- **Response:** 201 CreatedProject (§6.0), `is_sample=false`, version 1 and equal creation/update timestamps. Also atomically initialise all 12 open periods for the requested FY, doc-62 default settings, and doc-28 COA template. No GL/budget transactions, sample corpus or imported opening balance is invented. Periods are fetched separately, not silently omitted from a promised embedded list.
- **Failures:** 400 ERR-002/ERR-005; 401 ERR-006; 403 ERR-007; 404 ERR-001 (replay target deleted); 409 ERR-010; 500 ERR-099; 503 ERR-092/ERR-093.
- **Error distinction:** ERR-012 remains backup/restore-specific, not reused for arbitrary create failures.
- **Pagination:** none.
- **Idempotency:** mandatory durable app-scoped receipt (§6.0). Same key/input → original 201/body, same timestamp/id, no duplicate files/audit/defaults. New key + duplicate active name → ERR-010. Failed creation leaves no selectable partial project; recovery finishes or removes unpublished temporary state before accepting a retry.
- **Example:** request `{"name":"Meridian FY27","base_currency":"INR","fy_start_month":4,"calendar_type":"monthly","fiscal_year":2026}` → 201 full Project in doc 63 §2. Resulting periods are April 2026…March 2027, not FY ending in 2026. Names containing literal script/formula text remain inert display data.

### 6.4 GET `/projects/{id}`
- **Auth / scope:** token + X-FPA-Project equal to path `id` (ProjectId).
- **Request:** no query or body.
- **Response:** 200 Project (§6.0). No embedded period/close arrays. Deletion makes this return ERR-001 rather than leaking a trash path. Opening/reading a project does not refresh Microsoft credentials or mutate its version.
- **Failures:** 400 ERR-002; 401 ERR-006; 403 ERR-007; 404 ERR-001; 500 ERR-099; 503 ERR-092.
- **Pagination:** none; related periods are §6.5, not an unbounded include option.
- **Idempotency:** read-only; no key; no implicit FY materialisation.
- **Example:** GET `/api/v1/projects/prj_9f2c41aa07e1` → 200 the full Project from doc 63 §2, with the same header project id.

### 6.5 GET `/projects/{id}/periods`
- **Auth / scope:** token + matching project header; path `id`: ProjectId.
- **Request:** PeriodListQuery (§6.0); no body. An absent FY in an existing project is an empty filtered list, not a reason to create it.
- **Response:** 200 PeriodPage (§6.0); exact field constraints and project ownership apply to each item, including locked periods. No monetary balances in the metadata list.
- **Failures:** 400 ERR-002; 401 ERR-006; 403 ERR-007; 404 ERR-001 (project); 409 ERR-003 (cursor revision changed/unavailable); 500 ERR-099; 503 ERR-092.
- **Pagination:** period_id ascending; cursor binds project, FY/status filters and period-list revision. A concurrent lifecycle change invalidating the read revision returns ERR-003; never splice states from different revisions.
- **Idempotency:** read-only; no key. No calendar generation or lock expiry on GET.
- **Example:** GET `/api/v1/projects/prj_9f2c41aa07e1/periods?fiscal_year=2025` → 200 `{"items":[],"next_cursor":null}` if only FY2026 exists. Nonempty example in doc 63 §8.

### 6.6 POST `/projects/{id}/periods`
- **Auth / scope:** token + matching project header; path `id`: ProjectId.
- **Request:** FiscalYearCreate (§6.0), no query. Calendar/month/currency come from the project, never a body override. This additive operation does not edit Project metadata and has no expected_version field; it cannot reset existing Period state.
- **Response:** 201 FiscalYearPeriods for a newly materialised FY; 200 FiscalYearPeriods if its complete 12-period set already exists. Newly created periods have status open, null lock metadata, version 1 and the same injected timestamp. Existing periods retain every status/version/timestamp/note; the response is their current state unless a receipt is replayed. A partially present or calendar-inconsistent FY is an integrity failure (ERR-099), not silently patched. Creation of 12 rows and one audit event is atomic. No transaction amounts or opening balances are created; no other missing years are auto-filled.
- **Failures:** 400 ERR-002/ERR-005; 401 ERR-006; 403 ERR-007; 404 ERR-001; 500 ERR-099; 503 ERR-092/ERR-093.
- **Pagination:** none; exactly 12 periods is the bounded action result, even when a read-page limit is lower.
- **Idempotency:** optional key returns original status/body on replay. Without a key, naturally repeat-safe at the FY level: first 201, subsequent 200 with no extra audit event or changed period. Concurrent requests must arbitrate uniqueness, never create 24 rows. No new project metadata version merely from adding a year.
- **Example:** POST `/api/v1/projects/prj_9f2c41aa07e1/periods` with `{"fiscal_year":2027}` → 201 full P01…P12 result in doc 63 §8; repeat without a key → 200 with the same rows, not 409 or a reset of locks.

### 6.7 GET `/projects/{id}/periods/{period_id}`
- **Auth / scope:** token + matching project header. Path `id`: ProjectId; `period_id`: PeriodId. Identical period_id in another project is not ownership.
- **Request:** no query or body. A valid but non-materialised period id is ERR-001, not a generated synthetic Period.
- **Response:** 200 Period (§6.0), including version for later guarded lifecycle actions.
- **Failures:** 400 ERR-002; 401 ERR-006; 403 ERR-007; 404 ERR-001; 500 ERR-099; 503 ERR-092.
- **Pagination:** none.
- **Idempotency:** read-only; no key; no audit mutation.
- **Example:** GET `/api/v1/projects/prj_9f2c41aa07e1/periods/2026-P01` → 200 the complete April Period in doc 63 §8. A future non-materialised FY returns 404, not zero balances.

## 7. Sample, deletion and entering/reopening close (DEC-018)
These four endpoint contracts extend §6; they are documentation, not implemented runtime routes. Lock/re-lock, sign-off, impact review and backup/restore remain WI-0001 work. The schema attachment owns closed DTOs; the behavioural rules below are mandatory M1/M3 tests, not something JSON Schema proves.

### 7.0 Fields, sequencing and lifecycle rules
All properties are required. Shared ProjectName/ProjectId/Period/PeriodNote/Timestamp types are §6.0. No financial amounts occur in these metadata DTOs; reachable error money stays decimal strings. Input objects reject unknown fields; client actor, timestamps, project paths, sample flags and server revision overrides are never accepted.

| Schema | Complete field contract |
|---|---|
| SampleProjectCreate | `name`: ProjectName. Only this field; no seed/currency/FY/calendar/path/credentials. |
| CreatedSampleProject | Project (§6.0) restricted to `is_sample=true`, `base_currency=INR`, `currency_exponent=2`, `fy_start_month=4`, `calendar_type=monthly`, `version=1`, equal created_at/updated_at. Project id is newly server-allocated, never copied from a real project. |
| ProjectDelete | `expected_version`: integer ≥1; `confirmation`: string 0..80 Unicode code points. Comparison with the stored canonical project name is **exact**, case-sensitive, no trimming/casefold/NFC correction of the confirmation. Empty/mismatched text is ERR-013; absent/non-string/oversized confirmation is ERR-002. |
| ProjectDeleted | `project_id`: ProjectId; `status`: constant `trashed`; `deleted_at`: Timestamp; `purge_after`: Timestamp, exactly deleted_at + 30×24 hours in UTC. This is the earliest eligible purge time, not a promise to run while the computer is off. No trash path or project name is returned. |
| PeriodStartClose | `expected_version`: integer ≥1. No note, force flag or chosen status. |
| PeriodUnlock | `expected_version`: integer ≥1; `note`: PeriodNote. Missing/null/blank note maps specifically to ERR-015 with action `unlock`; wrong type, >500 characters, controls or unknown fields map to ERR-002. Error-selection order: reject non-object/unknown fields or invalid expected_version as ERR-002; missing/null note → ERR-015; wrong note type/length or ASCII controls → ERR-002; otherwise whitespace-only note → ERR-015. Thus a newline-only note is ERR-002. This precedes normal DTO validation so a missing note with an otherwise valid request is not silently turned into a generic code. |
| ClosingPeriod | Period (§6.0) restricted to `status=closing`, `locked_at=null`, `lock_note=null`. Other fields retain the stored calendar/project identity. |

For mutations: local auth/origin → project/resource ownership → syntactic request validation → same-key receipt lookup/conflict → optimistic version → lifecycle/confirmation/busy guards → durable write. Ownership is checked before returning a receipt, not just on the first request. A matching receipt returns the original success without re-running version/state guards or writing another audit entry; it can be historical, so the UI reads the resource again before the next mutation. A changed payload with the same key is ERR-005. No cached success crosses projects. This ordering does not turn a missing launch token into a domain error.

`start-close`: only open→closing; version increases by exactly one, updated_at comes from an injected clock, created_at and dates stay unchanged. Instantiate the doc-30 close task template once in the same transaction as the period transition/audit. It is **not** sign-off, lock, a waiver, a rule run or permission to mark system tasks done. A second call with a new/no key while closing/locked is ERR-016, not a second template. The same key replays the original success.

`unlock`: only locked→closing; version +1, updated_at from the injected clock, clear current locked_at/lock_note (the old lock is retained in audit). Record `RESTATE_OPEN` with the note, old period version/lock metadata and the immutable pre-unlock snapshot references needed by doc 41, **before** any correction can write. Failure to retain that baseline fails atomically; never unlock first and try to capture the old numbers later. Keep prior exports, historical sign-offs and finding/audit history; previous sign-offs are no longer current for the reopened period. Existing task rows/history are not re-created or silently approved. Do not generate an impact report or post a correcting entry inside this metadata action; the full doc-41 review is still mandatory before re-lock. Missing note is ERR-015 here; ERR-083 remains the separate restatement-approval guard, not a substitute for unlock input validation.

Both period actions reject a known broken audit chain / integrity read-only state with 422/ERR-090 before any new mutation (doc 12 §3); reading historical receipts does not repair or bypass it. Both period actions arbitrate against active/queued period-affecting jobs or another write lease. Busy → ERR-092; a job checks period/version again at its eventual write boundary. Zero side effects on failed validation/version/state/lease checks. Session-derived actor, before/after and note are audited atomically; no client actor override. No new job kind or job receipt is invented for these short transactions.

### 7.1 POST `/projects/sample`
- **Auth / scope:** app-scoped, token and exact Host/Origin required; no selected project. The literal `sample` route is registered before `/{id}`. Idempotency-Key required, installation-scoped as §6.0.
- **Request:** SampleProjectCreate (§7.0), no query. The source is the shipped doc-42 seed-42 corpus/version, not caller files or another project. Active-name uniqueness is §6.0, including real projects; collision is ERR-010.
- **Response:** 201 CreatedSampleProject (§7.0). Initialise the same default settings/COA machinery as normal creation, but is_sample=true and all 36 periods for FY2024/FY2025/FY2026, each open/version 1/null lock metadata. No financial rows, completed close tasks, findings or forecasts are manufactured. This creates the **sample workspace**, not a precomputed finished month-end. The walkthrough loads the bundled master/GL/budget/driver/subledger files through the ordinary import/validation/commit endpoints (or the explicit demo connector), never by seeding ledger SQL or copying a pre-built DB. Before GL, load the bundled masters; the sample label remains on every output. No connection is enabled, and no mock server/network starts merely on creation.
- **Failures:** 400 ERR-002/ERR-005; 401 ERR-006; 403 ERR-007; 404 ERR-001 (replay target deleted); 409 ERR-010; 500 ERR-099; 503 ERR-092/ERR-093.
- **Failure details:** Missing/inconsistent installed sample assets are ERR-099, not an empty successful sample. Admission checks the shipped manifest; corpus generation/acceptance is still the M1 gate.
- **Pagination:** none; read periods via §6.5, not an embedded array.
- **Idempotency:** required receipt; one project/template/period set/audit event, including after restart. New key never overwrites another sample. Same input with a new unique name creates a separate sample workspace; it cannot adopt a real project's id or data.
- **Example:** POST `/api/v1/projects/sample` with `{"name":"Sample Company"}` → 201 the complete CreatedSampleProject in doc 63 §9. All defaults above are server-owned, not hidden client parameters.

### 7.2 DELETE `/projects/{id}`
- **Auth / scope:** token + X-FPA-Project matching path `id`: ProjectId; Idempotency-Key required. Same rules for sample and real projects; licence state does not prevent access/deletion.
- **Request:** ProjectDelete (§7.0), JSON body, no query. Read the latest Project version/name before asking for confirmation. Invalid type/missing fields → ERR-002; stale version → ERR-003 before confirmation; an exactly wrong confirmation → ERR-013 with no echoed name.
- **Response:** 200 ProjectDeleted (§7.0), only after credentials/pending auth are revoked, the directory is durably moved to private trash, the active catalogue entry is removed and the app-level receipt/audit is durable (doc 12 §2.1). This is **not** immediate permanent erasure. Other project data and externally saved exports/backups are untouched; retaining them is disclosed to the analyst. Subsequent ordinary reads and mutations for this project return ERR-001; there is no API path into trash. Purge follows doc 12 §2.1 at/after purge_after, not before it.
- **Failures:** 400 ERR-002/ERR-005/ERR-013; 401 ERR-006; 403 ERR-007; 404 ERR-001; 409 ERR-003; 500 ERR-099; 503 ERR-092/ERR-093.
- **Failure details:** Active/queued jobs, active foreground connector I/O or file read/write leases → ERR-092, without cancelling work or partially deleting anything. Integrity/read-only financial mode does not prevent an explicitly confirmed project deletion; it is recorded in the app-level audit, not a fabricated entry in a broken chain.
- **Pagination:** none.
- **Idempotency:** required, retained outside the moved/deleted folder. Same-key/body replay after deletion returns the original 200 receipt, including after purge/restart; project ownership is checked against its minimal deletion tombstone. A different key for the absent project → ERR-001. Only deletion replay has this tombstone exception; GET/job polls do not regain access. Persist only a keyed request digest + id/status/timestamps/receipt, never the typed project name or secret after purge. A digest/key conflict remains ERR-005. App-level audit/tombstone retention does not retain financial rows.
- **Example:** DELETE `/api/v1/projects/prj_9f2c41aa07e1` with `{"expected_version":1,"confirmation":"Meridian FY27"}` at 2026-10-14T09:00:00Z → 200 `{"project_id":"prj_9f2c41aa07e1","status":"trashed","deleted_at":"2026-10-14T09:00:00Z","purge_after":"2026-11-13T09:00:00Z"}`. `meridian FY27` is a mismatch, even though casefold is used for create-name uniqueness.

### 7.3 POST `/projects/{id}/periods/{period_id}/start-close`
- **Auth / scope:** token + matching project header; path `id`: ProjectId, `period_id`: PeriodId; check composite ownership.
- **Request:** PeriodStartClose (§7.0); no query. No implicit current period, forced status or client timestamp.
- **Response:** 200 ClosingPeriod; state open→closing and version +1, task initialisation/audit atomic (§7.0). Imports into closing remain permitted with the doc-23 banner. Merely opening S16/reading GET close must not start this action.
- **Failures:** 400 ERR-002/ERR-005; 401 ERR-006; 403 ERR-007; 404 ERR-001; 409 ERR-003/ERR-016; 422 ERR-090; 500 ERR-099; 503 ERR-092/ERR-093.
- **Failure details:** ERR-016 details are `{state:<actual>,action:"start_close"}`.
- **Pagination:** none.
- **Idempotency:** optional key under §1.3; successful replay returns the original ClosingPeriod, no second template or audit. Without a key this is not repeat-safe as a successful action: a fresh request must meet state/version guards.
- **Example:** open `2026-P01` at version 1; POST `{"expected_version":1}` → 200 the version-2 ClosingPeriod in doc 63 §9. The endpoint does not report any financial task complete.

### 7.4 POST `/projects/{id}/periods/{period_id}/unlock`
- **Auth / scope:** token + matching project header; `id`: ProjectId; `period_id`: PeriodId. Not a direct update to a status string.
- **Request:** PeriodUnlock (§7.0); no query; a nonblank explanatory note is mandatory even if there are no findings or the project is a sample.
- **Response:** 200 ClosingPeriod, locked→closing, version +1, baseline capture + RESTATE_OPEN audit as §7.0. Old locked_at/lock_note survive in history only, not as misleading current metadata. This response makes no claim that doc-41 impact review or re-lock is complete.
- **Failures:** 400 ERR-002/ERR-005/ERR-015; 401 ERR-006; 403 ERR-007; 404 ERR-001; 409 ERR-003/ERR-016; 422 ERR-090; 500 ERR-099; 503 ERR-092/ERR-093.
- **Failure details:** ERR-015 details `{action:"unlock"}`; ERR-016 `{state:<actual>,action:"unlock"}`. Failure to retain the immutable baseline is ERR-099 (or ERR-093 for storage failure), with the period still locked.
- **Pagination:** none.
- **Idempotency:** optional key; one transition/baseline/audit. Same-key replay precedes business state/version checks but not auth/ownership; a new/no-key request against open/closing is ERR-016 if its version is current (otherwise ERR-003).
- **Example:** locked `2026-P01`, version 3; POST `{"expected_version":3,"note":"Re-import the corrected April ledger; approved by the controller."}` → 200 the version-4 ClosingPeriod in doc 63 §9. It is not version 1 and never silently returns open.
