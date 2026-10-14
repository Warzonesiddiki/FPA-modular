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
- Close readiness/sign-off/lock: §8. Version, review binding and current sign-off are mandatory; force is limited. Impact generation/approval, paged changes and retained baseline reads: §9 (docs 30/41). Snapshot persistence/ownership still requires verification.
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
| Close (30) | Task/calendar/template and history routes: §10; readiness and POST `/close/sign-off`: §8 |
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
These seven endpoint sections replace the corresponding shorthand in §2. Sample workspace/deletion/start-close/unlock are expanded in §7; backup/restore still requires expansion (lock/sign-off: §8; impact review: §9); §6 does not claim that those operations are complete. Contracts are documentation only until M3. Field names below are authoritative; doc 90 is their index. JSON Schema definitions are in the existing `api_job_schemas.json` attachment (shared primitives/errors are not copied into another registry).

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
These four endpoint contracts extend §6; they are documentation, not implemented runtime routes. Lock/sign-off are expanded in §8; impact review is expanded in §9; backup/restore remains WI-0001 work. The schema attachment owns closed DTOs; the behavioural rules below are mandatory M1/M3 tests, not something JSON Schema proves.

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

## 8. Close readiness, sign-off and lock (DEC-020)
These three contracts extend §7; product code remains frozen. Task/calendar/template editing and history are specified in §10; impact review in §9. Docs 30 §6–§7 and 41 §2 own guards. All objects are closed, all fields required (including nullable fields). No body field can set actor, server time, chosen state or a system task's completion. No money is calculated here; reachable errors retain decimal-string money.

### 8.0 Fields, review token and common sequencing
| Definition | Fields |
|---|---|
| CloseBlockerCode | Exactly the 16 codes in doc 30 §6. |
| CloseBlocker | code: CloseBlockerCode; count: integer ≥1; overridable: boolean, true **iff** code is high_findings or manual_tasks. |
| CloseReview | project_id: ProjectId; period_id: PeriodId; period_version: integer ≥1; audit_head: Sha256 or null; snapshot_id: Id or null; blocker_fingerprint: Sha256. |
| CloseSignoffEvidence | review: CloseReview with non-null snapshot_id; snapshot: SnapshotRef (doc 64, same snapshot_id as review); override_note: PeriodNote or null; overridden_blockers: sorted unique-by-code CloseBlocker array, 0..2, only overridable rows, empty without an override. |
| CloseSignoff | signoff_id: Id; project_id: ProjectId; period_id: PeriodId; signer: ProjectName syntax (label only, no uniqueness rule); attestation_text: exact server string `I confirm the pack for <period_id> is complete and reviewed`; at: Timestamp; evidence: CloseSignoffEvidence. Scope equals evidence.review. This label is not authenticated identity or statutory certification; actor comes from shell context. |
| CloseReadiness | review: CloseReview; review_token: Sha256; period_status: open/closing/locked; blockers: CloseBlocker array 0..16, unique code/sorted; current_signoff: CloseSignoff or null (null outside closing; historical lock evidence is not permission for another lock); ready_to_sign_off, ready_to_lock: boolean. ready_to_sign_off iff closing, non-null snapshot and no blockers. ready_to_lock iff closing, current_signoff valid, non-null snapshot and no remaining blocker except manual_tasks already explicitly covered by that sign-off. High findings require force, so make normal ready_to_lock false even when previously overridden. |
| CloseSignoffCreate | period_id: PeriodId; expected_version: integer ≥1; review_token: Sha256; signer: ProjectName syntax; attest: literal true; override_note: PeriodNote or null. Null means no override requested, not approval. Blank/control/wrong-type note → ERR-002; actual blocking conditions with no override → ERR-080. |
| PeriodLock | expected_version: integer ≥1; review_token: Sha256; signoff_id: Id; force: boolean; note: PeriodNote or null. force=true requires a nonblank, control-free note (missing/null/blank note → ERR-015 if all other fields are well-shaped; wrong type/length/controls → ERR-002). force=false permits null. No implicit force default. Validate the object/other fields first; then missing/null note with force=true → ERR-015; bad note type/length/controls → ERR-002; otherwise blank note with force=true → ERR-015 (force=false missing/blank note → ERR-002). |
| LockedPeriod | Period (§6) restricted to status=locked, non-null locked_at and version≥2 (response to a version-incrementing command, including a migrated closing period at version 1). lock_note equals request note. |

`blocker_fingerprint` is SHA256 of the UTF-8 canonical JSON array of pairs `[code, resource_id]` for all currently offending resources, sorted lexically by code then id, duplicates removed. For aggregate checks use the period_id as resource_id; for high_findings/custom manual tasks/jobs use their actual IDs. No resource-id list is exposed in this bounded response; resource screens retain paged drill. An empty set hashes canonical `[]`. Counts alone are not a review binding.

`review_token = SHA256(b"FPA-CLOSE-REVIEW-v1\n" + canonical(CloseReview))`. Canonical JSON here is UTF-8, object keys sorted lexically, no insignificant whitespace, no ASCII escaping of Unicode, no NaN/Infinity; arrays retain their specified ordering (Python reference: ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False). It is a concurrency digest, **not authentication**. Null audit_head means an empty chain, not successful verification of a broken one. The server recomputes from trusted data, never accepts a client-supplied review/snapshot as authoritative.

Mutations: §1.2 auth/ownership and strict syntax → same-key receipt/conflict → expected period version (ERR-003) → state/integrity/busy checks → recomputed review token (ERR-080 `blockers:["review_changed"]`) → current sign-off/impact/hard/soft guards → atomic write. All guards run again at the write boundary. Retained same-key successes replay historical results, not fresh permission to mutate. Foreign signoff_id returns ERR-001 before business checks. A sign-off record is immutable: changing signer/note requires a new explicitly reviewed sign-off, not PUT. Polling performs no writes, exports, imports, audit verification walk or network.

### 8.1 GET `/projects/{id}/periods/{period_id}/close-readiness`
- **Auth / scope:** token, exact Host/Origin, project header/path and period ownership (§1.2).
- **Request:** no body; no query parameters.
- **Response:** 200 CloseReadiness. Uses consistent committed state; no template materialisation. Known audit-integrity/busy/non-closing conditions appear as non-overridable blockers, never false ready flags. Absent usable current pack → snapshot_id=null and board_pack blocker. A current sign-off is derived per doc 30 §7, not merely the latest row in close_signoffs.
- **Failures:** 400 ERR-002; 401 ERR-006; 403 ERR-007; 404 ERR-001; 500 ERR-099; 503 ERR-093.
- **Pagination:** none; at most one row for each of 16 fixed aggregate codes. No ledger/task/finding array is embedded.
- **Idempotency:** read-only; key not required or consumed.
- **Example:** doc 63 §10.1.

### 8.2 POST `/close/sign-off`
- **Auth / scope:** token, exact Host/Origin, explicit X-FPA-Project; body period must belong to it.
- **Request:** CloseSignoffCreate; no query. The client must have displayed the attestation text and exact readiness before sending attest=true; this remains an explicit human business attestation, not AI approval.
- **Response:** 201 CloseSignoff. Creates record/audit/receipt atomically, period version unchanged, no lock. Server copies the reviewed snapshot and only actually overridden blockers. Ordinary sign-off has null override_note and empty overridden_blockers. Same-key replay does not make an old sign-off current after a later change. Read readiness again before locking: sign-off itself advances the audit head/token.
- **Failures:** 400 ERR-002/ERR-005; 401 ERR-006; 403 ERR-007; 404 ERR-001; 409 ERR-003/ERR-016; 422 ERR-080/ERR-083/ERR-090; 500 ERR-099; 503 ERR-092/ERR-093.
- **Failure details:** ERR-016 action=sign_off. Missing/stale current impact approval → ERR-083 (reason=approval_note_required); a free-text override is not impact approval. Other hard blockers or unapproved soft blockers → ERR-080 with sorted blocker codes. State/version failures precede record creation.
- **Pagination:** none; one immutable record.
- **Idempotency:** required; project + method/path + key (§1.3). A new key can create a replacement only with a fresh review, never silently reuse the last approval.
- **Example:** doc 63 §10.2.

### 8.3 POST `/projects/{id}/periods/{period_id}/lock`
- **Auth / scope:** token, exact Host/Origin, project header/path, period and signoff ownership (§1.2); signoff must belong to this period as well as this project, otherwise ERR-001.
- **Request:** PeriodLock; no query. Legacy note/force-only requests without version/review/signoff are invalid, not a bypass.
- **Response:** 200 LockedPeriod. Only closing→locked, version +1, timestamps injected; dates/created_at unchanged. Snapshot/signoff link, period change, PERIOD_LOCK audit and receipt commit together. GET and sign-off never perform this action. Force never waives audit, current sign-off, TB, forecasts, export checks or current restatement approval.
- **Failures:** 400 ERR-002/ERR-005/ERR-015; 401 ERR-006; 403 ERR-007; 404 ERR-001; 409 ERR-003/ERR-016; 422 ERR-011/ERR-080/ERR-083/ERR-090; 500 ERR-099; 503 ERR-092/ERR-093.
- **Failure details:** ERR-016 action=lock. Review changed/current sign-off missing → ERR-080 (`review_changed`/`signoff_required`). Restatement approval missing/stale → ERR-083. Other hard blockers → ERR-080. Open High without force → ERR-011; details.n is the full positive count (≥1), finding_ids carries exactly the first min(n,100) distinct sorted IDs, not the whole ledger. These guards precede every effect.
- **Pagination:** none; one period. Finding details are bounded diagnostics, not a resource-list substitute.
- **Idempotency:** required; same-key replay returns the old locked response after restart or later unlock; a fresh key against locked state fails ERR-016. Re-read current Period before another mutation.
- **Example:** doc 63 §10.3.


## 9. Restatement impact review (DEC-021)
Document contracts, not runtime evidence. Doc 41 §6 owns comparison/freshness semantics; doc 24 §4 owns immutable financial manifests. **No client boolean, lock note or historical approval authorises re-lock.** All routes require the token, exact Host/Origin and X-FPA-Project; every period, baseline, snapshot, impact and approval id is checked in that project, and in the selected period where applicable, before state disclosure. No filesystem paths, external networking, AI approval or financial recomputation on GET. All fields below are required, including nulls; all objects are closed. Abbreviated project_id/period_id use ProjectId/PeriodId; all resource ids use Id. Money = Money strings via core/money, never JSON numbers.

### 9.0 Fields and ownership
| Definition | Fields / constraints |
|---|---|
| RestatementBaseline | baseline_id: Id; project_id: ProjectId; period_id: PeriodId; unlock_version: integer ≥2; before_snapshot: SnapshotRef; before_manifest_sha256: Sha256; locked_at: Timestamp; lock_note: PeriodNote or null; signoff_id: Id or null (legacy lock only); opened_at: Timestamp; reason: PeriodNote. Immutable, captured in the unlock transaction from the last lock's retained snapshot, never reconstructed from corrected current data. Missing reproducible snapshot fails unlock atomically (ERR-099). |
| RestatementState | project_id; period_id; period_version: integer ≥1; period_status: open/closing/locked; baseline: RestatementBaseline or null; current_impact_id: Id or null; current_approval_id: Id or null. Baseline is the latest retained unlock cycle, including while locked. Current ids are null outside closing or when stale; approval id requires current impact id. No baseline → both ids null. Never infer current authority from baseline/history alone. |
| ImpactCreate | expected_version: integer ≥2; baseline_id: Id; after_snapshot_id: Id. Baseline must be this cycle; after snapshot must be the current checked pack snapshot (not an arbitrary historical selector). |
| ImpactCounts | statement, bva, finding, forecast, report: integers ≥0 (exact row counts for the five change categories, not a truncated sample). |
| ImpactReport | impact_id: Id; project_id; period_id; period_version: integer ≥2; baseline_id: Id; before_snapshot, after_snapshot: SnapshotRef; before_manifest_sha256, after_manifest_sha256: Sha256; changes_sha256: Sha256; counts: ImpactCounts; created_at: Timestamp. Immutable metadata; details use the paged route below, never unbounded arrays. before snapshot/hash equals baseline, after matches checked pack. Both snapshots have the same project/period/layer. Report creation does not bump period.version. |
| ImpactValue | value: Money or null; unavailable_reason: absent/not_available or null; drill_key: Id or null. value non-null requires reason=null and non-null drill_key; null value requires non-null reason and null drill_key. absent means no row in that snapshot, not zero; not_available means a retained labelled unavailable comparator. Drill tokens bind the snapshot and owning project, not live current rows. Explicit zero is a real value with a drill to no-activity explanation. |
| ImpactMoneyChange | kind: statement/bva; key: Id; statement: pl/bs/cf or null; line_key: Id or null; entity_id, account_id, cost_centre_id: Id or null; measure: amount/actual/budget/forecast/py/var_abs; before, after: ImpactValue; delta: Money or null. statement requires statement+line_key, null grain fields and measure=amount (project total); bva requires statement=line_key=null, non-null entity/account, optional-null cost centre and non-amount measure. delta = after − before in **presented units**, null iff either side unavailable. No percentage/favourability inference from delta. |
| ImpactFindingChange | kind: literal finding; key: Id; finding_key: string 1..512, no ASCII controls; change: added/removed/changed; before_finding_id, after_finding_id: Id or null; before_sha256, after_sha256: Sha256 or null. added has only after; removed only before; changed has both and differing business-state hashes. No deletion of live/historical finding records is implied by removed. |
| ImpactForecastChange | kind: literal forecast; key: Id; run_id: Id; change: literal stale. One row per run invalidated by changed inputs since the baseline; generation itself does not stale any run. |
| ImpactReportChange | kind: literal report; key: Id; report_id: Id; change: literal superseded. One row per prior export for this period/layer whose manifest was replaced by the after snapshot; keep prior files and source refs. Current checked-pack exports are not superseded by impact creation. |
| ImpactChange | Closed union of ImpactMoneyChange, ImpactFindingChange, ImpactForecastChange, ImpactReportChange. Keys and comparison rules: doc 41 §6. |
| ImpactChangeQuery | optional kind: statement/bva/finding/forecast/report; optional limit integer 1..1000 (default 100); optional cursor: non-null PageCursor. No other parameters. |
| ImpactChangePage | items: ImpactChange array, 0..1000; next_cursor: PageCursor or null. At most requested limit, stable ordering (kind,key); cursor binds project, impact_id, changes_sha256, kind and limit. Details are immutable: later project changes do not invalidate this traversal. |
| ImpactApprovalCreate | expected_version: integer ≥2; signer: ProjectName syntax (display label, not authenticated actor); attest: literal true; note: PeriodNote (required, nonblank). |
| ImpactApproval | approval_id: Id; project_id; period_id; period_version: integer ≥2; impact_id; baseline_id; before_snapshot_id, after_snapshot_id: Id; before_manifest_sha256, after_manifest_sha256, changes_sha256: Sha256; signer: ProjectName; attestation_text: exact server string `I reviewed the restatement impact for <period_id> and approve these changes`; note: PeriodNote; at: Timestamp. All binding fields copied from the immutable report, not supplied by the client. Human attestation only; actor from local shell context in audit. Immutable and historical after staleness. |

Changes hash = SHA256 of the UTF-8 canonical JSON array of all ImpactChange rows sorted by (kind,key), using §8.0 canonical encoding. Empty array uses the same hash as empty blockers. Compute incrementally; do not load an entire ledger merely to return a page. Counts exactly partition that array. Server-assigned key = SHA256 of the canonical JSON identity tuple in doc 41 §6 (64 lowercase hex, a subset of Id); unique within a report. Hashes are integrity/concurrency evidence, not authentication. Arithmetic, cross-field equality, ownership, counts, sorting, hashing, currency exponent, and actual currentness are runtime checks beyond JSON Schema.

Write sequence: auth/ownership and strict syntax → durable same-key receipt/conflict → expected period version (ERR-003) → closing state (ERR-016), known integrity failure (ERR-090), incompatible job/write/lifecycle lease (ERR-092, excluding own lease) → cycle/pack/manifest checks → atomic publish with audit and receipt. No partial report/pages/approval survives failure. Period-affecting jobs cannot race publication; all input checks repeat inside the project write boundary. Frozen inputs may be compared outside that boundary, but a changed context fails before publication. Period version alone is insufficient for this fence. No forecast/export job starts implicitly.

Current impact requires **all**: closing period, same project/period and unlock cycle, same period revision, before snapshot/hash equals baseline, after snapshot/hash equals current financial manifest and current checked pack. Of qualifying reports choose the latest IMPACT_GENERATE event in durable project audit append order, never wall-clock order or random-id lexical order. Current approval requires that exact current report, identical bindings and a nonblank note; choose the latest IMPACT_APPROVE event in that same durable append order. Publishing another impact replaces the current choice even for identical inputs; previous approvals remain history. A new approval or sign-off audit event is NOT a financial input change. Financial changes invalidate current impact/approval even if batch_watermark is unchanged. Conservative v1: once an input-affecting mutation occurs after report creation, that report never becomes current again even if values later revert; regeneration and approval are required. Persist this invalidation; do not rely only on a hash equality after rollback. Locked approvals remain readable, never permission for another cycle.

### 9.1 GET `/projects/{id}/periods/{period_id}/restatement`
- **Request:** no body/query. **Response:** 200 RestatementState; null baseline for a never-reopened period. GET creates nothing and projects currentness from trusted retained state.
- **Failures:** 400 ERR-002; 401 ERR-006; 403 ERR-007; 404 ERR-001; 500 ERR-099; 503 ERR-093.
- **Pagination:** none, one bounded context. **Idempotency:** read-only, no key. **Example:** doc 63 §11.1.

### 9.2 POST `/projects/{id}/periods/{period_id}/impacts`
- **Request:** ImpactCreate, no query. **Response:** 201 ImpactReport. Synchronously compares already-retained before/current pack snapshots, streaming pages internally; it does not recalculate financial engines or render files. Publish report, immutable changes, IMPACT_GENERATE audit and durable receipt atomically. This is not a job acceptance or a new doc-64 job kind.
- **Failures:** 400 ERR-002/ERR-005; 401 ERR-006; 403 ERR-007; 404 ERR-001; 409 ERR-003/ERR-016; 422 ERR-080/ERR-090; 500 ERR-099; 503 ERR-092/ERR-093.
- **Failure details:** ERR-016 action=generate_impact; no active baseline/old same-period baseline → ERR-080 blockers=[restatement_review]; stale supplied snapshot → ERR-080 blockers=[review_changed]; absent/stale/unchecked pack → ERR-080 blockers=[board_pack]; obsolete forecast → ERR-080 blockers=[forecast]. Check in that order after common guards. No sign-off/lock/impact-approval prerequisite: those are downstream. Missing retained baseline content → ERR-099, or ERR-093 on storage failure; it is never an empty successful comparison.
- **Pagination:** metadata only; changes via §9.4. **Idempotency:** required §1.3; same key returns historical response without recomputing; fresh key creates a new immutable report. **Example:** doc 63 §11.2.

### 9.3 GET `/impacts/{id}`
- **Request:** no body/query. **Response:** 200 ImpactReport (historical even if no longer current). Missing/foreign impact is ERR-001.
- **Failures:** 400 ERR-002; 401 ERR-006; 403 ERR-007; 404 ERR-001; 500 ERR-099; 503 ERR-093.
- **Pagination:** none. **Idempotency:** read-only, no key. **Example:** doc 63 §11.2's response, unchanged after approval/lock.

### 9.4 GET `/impacts/{id}/changes`
- **Request:** no body, ImpactChangeQuery. **Response:** 200 ImpactChangePage. Filter kind before paging, never omit changes because a threshold was not met. Empty diff returns empty page, not no report. Cursor/project/report/filter/limit mismatch → ERR-002; no revision conflict for immutable rows. Historical source drill must use the row's frozen snapshot token.
- **Failures:** 400 ERR-002; 401 ERR-006; 403 ERR-007; 404 ERR-001; 500 ERR-099; 503 ERR-093.
- **Pagination:** §9.0; no unbounded nested findings/transactions. **Idempotency:** read-only, no key. **Example:** doc 63 §11.3.

### 9.5 POST `/impacts/{id}/approve`
- **Request:** ImpactApprovalCreate, no query. UI must display the report and attestation before explicit human approval. A caller-supplied actor, snapshot, impact_approved or force field is ERR-002.
- **Response:** 201 ImpactApproval; record + IMPACT_APPROVE audit + durable receipt in one transaction; no period version increment, sign-off, lock, financial invalidation or automatic pack generation. Re-read close readiness after approval before signing.
- **Failures:** 400 ERR-002/ERR-005; 401 ERR-006; 403 ERR-007; 404 ERR-001; 409 ERR-003/ERR-016; 422 ERR-083/ERR-090; 500 ERR-099; 503 ERR-092/ERR-093.
- **Failure details:** ERR-016 action=approve_impact; missing/null/blank/wrong-type note or attest!=true → ERR-002 (not unlock's ERR-015). Well-shaped approval of a stale/not-current report or cycle → ERR-083 reason=approval_note_required. A retained report id is not enough. Same-key historical replay remains success but does not restore current authorisation.
- **Pagination:** none. **Idempotency:** required §1.3; a new key may record another reviewed attestation for the still-current report, preserving earlier rows. **Example:** doc 63 §11.4.

### 9.6 GET `/impact-approvals/{id}`
- **Request:** no body/query. **Response:** 200 ImpactApproval; readable history, never an implicit current=true assertion. Use §9.1 for currentness.
- **Failures:** 400 ERR-002; 401 ERR-006; 403 ERR-007; 404 ERR-001; 500 ERR-099; 503 ERR-093.
- **Pagination:** none. **Idempotency:** read-only, no key. **Example:** doc 63 §11.4's immutable response.


### 9.7 GET `/restatement-baselines/{id}`
- **Request:** no body/query. **Response:** 200 RestatementBaseline, including old cycles. Project ownership applies before lookup disclosure; retained baseline is not an assertion of currentness. Use §9.1 for the current cycle.
- **Failures:** 400 ERR-002; 401 ERR-006; 403 ERR-007; 404 ERR-001; 500 ERR-099; 503 ERR-093.
- **Pagination:** none. **Idempotency:** read-only, no key. **Example:** doc 63 §11.1 baseline object, unchanged after another unlock.


## 10. Close tasks, calendar, template and history (DEC-022)
Doc 30 §§8–9 owns semantics; doc 02 §5 owns storage. These are document contracts, not implemented HTTP. All eight endpoints require X-FPA-Token, exact Host/Origin and matching X-FPA-Project (§1.2). All task/period/dependency/owner references are checked within the project and selected period before state disclosure. Foreign/missing resource → ERR-001. No GET mutates, materialises templates, completes tasks or runs financial work. No money is computed/exposed here except existing decimal-string errors.

### 10.0 Field definitions and shared rules
All fields required including nullable fields unless explicitly marked optional. Objects are closed. ProjectId, PeriodId, Id, Sha256, CalendarDate, Timestamp, PeriodNote and ProjectName retain their shared definitions. ProjectName is display text, not identity or uniqueness for a signer/title.

| Definition | Fields / constraints |
|---|---|
| CloseTaskKey | T-01…T-10 or C- followed by 1..24 lowercase letters/digits/underscore, first a letter. Project-template key, not a task resource id. |
| CloseTaskStatus | not_started/in_progress/blocked/done/waived. |
| CloseCalendarRules | start_business_day: integer 1..60; target_lock_business_day: integer 1..60, ≥start; holidays: sorted unique CalendarDate array 0..1000. |
| CloseTemplateEntry | key: CloseTaskKey; title: ProjectName; kind: system/attest/manual; owner_id: Id or null; due_offset_business_days: integer -60..60; depends_on: CloseTaskKey or null. Built-ins have exact doc-30 title/kind and null dependency; custom kind=manual. T-09/T-10 cannot be dependencies. |
| CloseTemplatePut | expected_version: integer ≥1; calendar: CloseCalendarRules; entries: CloseTemplateEntry array 10..1000. Complete replacement for future periods, not a patch. Exactly one of each built-in; unique sorted keys; all referenced custom keys included; no cycles. |
| CloseTemplate | project_id: ProjectId; version: integer ≥1; calendar; entries (same rules); created_at, updated_at: Timestamp. At creation defaults doc 30 §8, no period task rows yet. |
| CloseCalendar | project_id; period_id; template_version: integer ≥1; instantiated: boolean; rules: CloseCalendarRules; period_end, close_start_date, target_lock_date: CalendarDate. Preview from current template when not instantiated, otherwise from immutable period copy. No task array. |
| CloseTaskAttestation | signer: ProjectName; at: Timestamp; note: PeriodNote or null; statements_fingerprint: Sha256 or null (non-null only for T-04 done). It is retained evidence, not current=true. |
| CloseTask | task_id: Id; project_id; period_id; template_key: CloseTaskKey; kind: system/attest/manual; title: ProjectName; owner_id: Id or null; due_offset_business_days: integer -60..60; due_date: CalendarDate; depends_on: Id or null (task resource id, not template key); version: integer ≥1; created_at, updated_at: Timestamp; requested_status: CloseTaskStatus or null; status: CloseTaskStatus (effective); note: PeriodNote or null; attestation: CloseTaskAttestation or null; review: CloseTaskReview; review_token: Sha256; evaluated_on: CalendarDate; overdue: boolean. System/outcome requested_status, note and attestation are null. Human done/waived requested status requires attestation; nonterminal human requested status has null attestation. T-04 cannot be waived. Unknown/missing template is a hard failure, not a completed empty list. |
| CloseTaskDetails | action: literal details; expected_version, expected_period_version: integer ≥1; review_token: Sha256; title: ProjectName; owner_id: Id or null; due_offset_business_days: integer -60..60; depends_on: Id or null. Built-in title/dependency must be unchanged; custom graph revalidated atomically. |
| CloseTaskTransition | action: literal transition; expected_version, expected_period_version: integer ≥1; review_token: Sha256; to_status: CloseTaskStatus; signer: ProjectName or null; attest: boolean; note: PeriodNote or null. done/waived require signer and attest=true; other states require signer=null/attest=false. blocked/waived require note. Reversal note rule is contextual (doc 30 §8). |
| CloseTaskUpdate | Closed union CloseTaskDetails / CloseTaskTransition. No force, actor, server times, evidence or completed_by accepted. |
| ClosePeriodQuery | period_id: PeriodId (required); no other keys. |
| CloseTaskListQuery | period_id required; limit integer 1..1000 default 100 and non-null cursor string 1..4096 optional. No status filters or arbitrary sort. |
| CloseTaskPage | items: CloseTask array 0..1000; next_cursor: PageCursor. Stable sort (template_key,task_id), at most requested limit. |
| CloseTaskCounts | not_started, in_progress, blocked, done, waived: integers ≥0, sum = instantiated task count. Outcome tasks counted for display only, not prerequisites. |
| CloseOverview | project_id; period_id; period_version: integer ≥1; period_status: open/closing/locked; instantiated: boolean; template_version: integer ≥1 or null; counts: CloseTaskCounts; evaluated_on: CalendarDate; readiness: CloseReadiness (§8). Not instantiated → template_version=null and all counts zero, with hard statements_review blocker in readiness. No embedded task list or fake completed percentage. |
| CloseLockRecord | project_id; period_id; before_version: integer ≥1; after_version: integer ≥2 (before+1); signoff_id: Id; snapshot: SnapshotRef; force: boolean; note: PeriodNote or null (non-null if force); locked_at: Timestamp. Immutable projection from a complete PERIOD_LOCK event and retained lock evidence, not current Period metadata. |
| CloseHistoryItem | audit_id: integer ≥1; action: CLOSE_SIGNOFF/PERIOD_LOCK/RESTATE_OPEN; at: Timestamp; evidence_state: complete/legacy; record: CloseSignoff/CloseLockRecord/RestatementBaseline according to action, or null iff legacy. Scope equals requested project/period; record timestamp equals at (signoff.at / lock.locked_at / baseline.opened_at). |
| CloseHistoryQuery | optional action from those three audit actions; optional limit integer 1..1000 default 100; optional non-null cursor string 1..4096. |
| CloseHistoryPage | items: CloseHistoryItem array 0..1000; next_cursor: PageCursor. Sorted unique audit_id ascending; high-water mark pinned by cursor, append-only new events do not duplicate/shift prior pages. Never infer currentness from latest history row. |

Task review token = SHA256(b"FPA-CLOSE-TASK-v1\n" + canonical({project_id,period_id,period_version,task_id,task_version,audit_head,statements_fingerprint,dependency_status})), canonical encoding as §8.0. Values: owning ids; current revisions; audit_head Sha256 or null; statements_fingerprint current statements Sha256 for T-04 only (null if no current statements and for all other tasks); dependency_status effective CloseTaskStatus or null if no dependency. This named **CloseTaskReview** is exposed as CloseTask.review and is also in the schema attachment. Its ids/revisions equal the containing task and owning period; review_token hashes this exact object. Before T-04 done, the client must have displayed statements whose fingerprint equals review.statements_fingerprint; a newly fetched token is not permission to claim older displayed statements were reviewed. The statement-viewer transport must carry this fingerprint when that endpoint family is expanded in WI-0001. Computing dependency status must detect cycles, not recurse indefinitely. Server recomputes all values under the write boundary, never trusts client facts. Tokens are concurrency digests, not authority. Completion of T-04 stores ONLY its statement binding, not an audit-head binding that downstream forecast/pack work would stale.

All PUT: strict syntax/auth/ownership → same-key receipt/conflict → versions → closing state for task edits → integrity/busy checks → task token → allowed edit/transition, owner, graph, dependency and statement guards → one atomic write/audit/receipt. Task version checked first (ERR-003 expected/actual task version), then period version (same shape for period); template PUT compares its own version. Token changed → ERR-080 blockers=[review_changed]. Period state failures → ERR-016 action=edit_close_task. System/outcome transition → ERR-080 blockers=[task_read_only]; T-04 waived → ERR-080 blockers=[task_not_waivable]. Invalid built-in title/dependency or malformed graph → ERR-002 (details.field=entries or depends_on). Missing/cross-period task dependency → ERR-001; same-period forbidden T-09/T-10 dependency → ERR-002. Unmet dependency at done/waived → ERR-084 details={task:<task_id>,dependency:<task_id>}. Missing reversal note → ERR-002 field=note. T-04 without current statements → ERR-080 blockers=[statements_review]. No error partially applies owner, status or calendar changes.

Live task pages bind project, period, limit, ordering, project audit head and evaluated_on in the signed cursor. Re-evaluate effective guards using that bound civil date; changed project audit head → ERR-003, tampered/expired/wrong-scope cursor → ERR-002. For audit-head conflicts, ERR-003 details.expected_version/actual_version are the bound/current project audit_id + 1 (empty head uses audit_id=0), not invented task revisions. Effective waivers are still evaluated at the real injected instant. The signed task cursor expires at the earlier of §1.3 retention expiry or the next relevant effective waiver expiry; reaching that boundary is an expired cursor (ERR-002), not a fabricated row-version change. Re-start traversal after expiry. A read must never pin a valid waiver beyond its actual expiry. No GET writes a snapshot just to paginate. History cursors instead pin immutable audit_id high-water mark; they bind action/limit/scope and use §1.3 expiry. Reads may expose historical evidence while locked but grant no edit or re-lock permission.

### 10.1 GET `/projects/{id}/close`
- **Request:** no body; ClosePeriodQuery. **Response:** 200 CloseOverview; counts/readiness from one consistent snapshot, with no task materialisation. Use separate pages for tasks and §8 for readiness-only polling.
- **Failures:** 400 ERR-002; 401 ERR-006; 403 ERR-007; 404 ERR-001; 500 ERR-099; 503 ERR-093.
- **Pagination:** none (bounded aggregate). **Idempotency:** read-only, no key. **Example:** doc 63 §12.1.

### 10.2 GET `/projects/{id}/close/tasks`
- **Request:** no body; CloseTaskListQuery. **Response:** 200 CloseTaskPage; never-started period has empty items, not a synthetic completed checklist. In locked periods use retained lock evidence; reads never complete system tasks in storage.
- **Failures:** 400 ERR-002; 401 ERR-006; 403 ERR-007; 404 ERR-001; 409 ERR-003; 500 ERR-099; 503 ERR-093.
- **Pagination:** §10.0 live projection. **Idempotency:** read-only, no key. **Example:** doc 63 §12.2.

### 10.3 GET `/close/tasks/{id}`
- **Request:** no body/query. **Response:** 200 CloseTask. Ownership includes the task's period; current review token for this one task.
- **Failures:** 400 ERR-002; 401 ERR-006; 403 ERR-007; 404 ERR-001; 500 ERR-099; 503 ERR-093.
- **Pagination:** none. **Idempotency:** read-only, no key. **Example:** doc 63 §12.2 task object.

### 10.4 PUT `/close/tasks/{id}`
- **Request:** CloseTaskUpdate, no query. **Response:** 200 CloseTask with task revision +1 and freshly recomputed review_token; period revision unchanged. No financial calculation, sign-off or lock occurs. All doc 30 §8 edit rules apply, including dependency cycles, human reversal and outcome protections.
- **Failures:** 400 ERR-002/ERR-005; 401 ERR-006; 403 ERR-007; 404 ERR-001; 409 ERR-003/ERR-016; 422 ERR-044/ERR-080/ERR-084/ERR-090; 500 ERR-099; 503 ERR-092/ERR-093.
- **Pagination:** none. **Idempotency:** required; durable §1.3 receipt. Same-key replay is the original result, not new attestation/currentness; fresh key requires current versions/token even if payload otherwise unchanged. **Example:** doc 63 §12.3.

### 10.5 GET `/projects/{id}/close/template`
- **Request:** no body/query. **Response:** 200 CloseTemplate, current project template. Exactly ten required built-ins plus declared customs; no live-period status rows.
- **Failures:** 400 ERR-002; 401 ERR-006; 403 ERR-007; 404 ERR-001; 500 ERR-099; 503 ERR-093.
- **Pagination:** none, one bounded configuration object, not a resource collection. **Idempotency:** read-only, no key. **Example:** doc 63 §12.4.

### 10.6 PUT `/projects/{id}/close/template`
- **Request:** CloseTemplatePut, no query. **Response:** 200 CloseTemplate, version +1. Entries and close calendar settings update atomically with one CLOSE_TEMPLATE_UPDATE audit + receipt; existing period copies/tasks untouched. May edit future template while periods are locked; never changes those locked periods or bypasses their guards. Missing/foreign owner → ERR-001; newly assigned inactive owner → ERR-044. Reject missing/duplicate built-ins, cycles, dangling keys, bounds or dates with ERR-002 before any write. No DELETE shortcut for removing mandatory tasks.
- **Failures:** 400 ERR-002/ERR-005; 401 ERR-006; 403 ERR-007; 404 ERR-001; 409 ERR-003; 422 ERR-044/ERR-090; 500 ERR-099; 503 ERR-092/ERR-093.
- **Pagination:** none. **Idempotency:** required; historical response replay does not reapply a template or rewrite a live period. **Example:** doc 63 §12.4 (body uses expected_version instead of server metadata).

### 10.7 GET `/projects/{id}/close/calendar`
- **Request:** no body; ClosePeriodQuery. **Response:** 200 CloseCalendar; computed preview for open never-started period, otherwise immutable period calendar. Task dates/overdue status are in paged task reads. On preview date overflow return ERR-002 field=period_id; no partial/clipped dates.
- **Failures:** 400 ERR-002; 401 ERR-006; 403 ERR-007; 404 ERR-001; 500 ERR-099; 503 ERR-093.
- **Pagination:** none (two dates/rules, not annual milestones). **Idempotency:** read-only, no key. **Example:** doc 63 §12.5. Annual planning calendar is a separate unfinished WI-0001 family (doc 48), not mixed with close prerequisites.

### 10.8 GET `/projects/{id}/periods/{period_id}/close-history`
- **Request:** no body; CloseHistoryQuery. **Response:** 200 CloseHistoryPage. Each complete record retains original data; legacy events explicitly labelled. No current=true/approved boolean, live Period substitution, raw audit JSON or implicit mutation.
- **Failures:** 400 ERR-002; 401 ERR-006; 403 ERR-007; 404 ERR-001; 500 ERR-099; 503 ERR-093.
- **Pagination:** §10.0 immutable audit high-water traversal. **Idempotency:** read-only, no key. **Example:** doc 63 §12.6; use readiness/restatement endpoints for current permissions.


## 11. Persistence fence obligations behind §§7–10 (DEC-023)
No new endpoint or caller field is introduced here. Docs 02 §5 and 24 §5 define server-only InputRevisions/InputRevisionAdvance, SnapshotInputBinding, ForecastInputBinding, InputInvalidation and retained baseline/impact/change/approval record layouts. Runtime routes must not accept these as arbitrary requests. Existing error codes and DTO fields are unchanged.

A newly generated forecast is published only against the captured forecast_revision (ERR-003 with captured/current revisions on mismatch); publishing its result advances pack_revision, **not** forecast_revision. Pack/impact publication similarly fences the captured pack_revision under the project write boundary, in addition to all existing ownership/state/manifest/content guards. Input writes advance normalised counters once, append permanent impact invalidation and mark statement attestations stale in the same transaction; no post-commit repair. Integrity, busy, note/attestation and scope failures retain their earlier precedence and codes. Counter overflow or unknown internal mutation category is ERR-099 with no surviving effects, never a new public error code.

Same-key replay does not advance counters or create another baseline/impact/approval; it can return historical data but cannot reauthorise it. Reads/pack generation/impact approval/sign-off do not themselves stale the financial state being reviewed. A counter match is necessary, not sufficient: full manifests, cycle/version, current checked outputs, time-dependent blockers and current human attestations still apply. Restore must have an external stale-write fence; replacing a database containing these counters does not prove rollback safety. Complete manifest/view encoding and lifecycle/control-plane receipt storage remain unfinished WI-0001 requirements.
