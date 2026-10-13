# 63 — API EXAMPLES & PAYLOAD COOKBOOK

> Normative examples, not a running server (M3 is not built). Doc 05 §1 owns protocol; doc 64 owns async results; doc 90 indexes schemas. Every amount is a **decimal string**. Examples use synthetic IDs. No example contains a real token or tenant credential. `X-FPA-Token` values come from the shell; never put them in URLs.

## 1. Local session and project context
All application routes are relative to `http://127.0.0.1:<port>/api/v1`; send `X-FPA-Token` for health/project operations too. Project-scoped examples additionally send `X-FPA-Project: prj_9f2c41aa07e1`. The server checks that it matches any project path and every referenced resource. POSTs creating jobs send a new `Idempotency-Key` (example `month-end-2025-P07-commit-1`). GETs send no body. OPTIONS handling and exact-origin rules are in doc 12 §1.1.

Same key/same payload returns the original receipt; changed payload with that key returns 400/FP&A-ERR-005. A new key does not bypass lifecycle guards. Missing launch token returns 401/FP&A-ERR-006, and a foreign Origin/Host is 403/FP&A-ERR-007, before project lookup.

## 2. Create a project
POST `/projects`, JSON request (no project header on this app-scoped operation):
```json
{"name":"Meridian FY27","base_currency":"INR","fy_start_month":4,"calendar_type":"monthly"}
```
HTTP 201 response fields are Project from doc 90: project_id, name, base_currency, currency_exponent, fy_start_month, calendar_type, is_sample, periods. IDs are created by the server; no request may set is_sample to impersonate a demo project. Full per-endpoint examples are being completed in WI-0001; this section does not claim an executable endpoint.

## 3. Commit and poll a completed import
POST `/imports/bat_41c200000001/commit`, no body (guard and idempotency headers per §1). HTTP 202:
```json
{"job_id":"job_commit_0001"}
```
GET `/jobs/job_commit_0001`, HTTP 200:
```json
{
  "job_id":"job_commit_0001",
  "project_id":"prj_9f2c41aa07e1",
  "kind":"import-commit",
  "status":"done",
  "stage":"done",
  "progress_pct":100,
  "progress":null,
  "created_at":"2026-10-14T09:00:00Z",
  "started_at":"2026-10-14T09:00:01Z",
  "finished_at":"2026-10-14T09:00:03Z",
  "cancellable":false,
  "error":null,
  "result":{"batch_id":"bat_41c200000001","committed":10410,"quarantined":12,"tb_status":"balanced","superseded_batch_id":null,"enrichment":null}
}
```
A blocked commit is a failed job with null result, never a done job with `tb_status=imbalanced`. ERR-023 details use decimal-string declared/actual totals. GET poll status remains 200. Schema examples in `api_job_schemas.json` cover every job kind and state, not just this one.

## 4. Dynamics 365 — explicit foreground actions
PUT `/projects/prj_9f2c41aa07e1/connector` takes the settings fields of doc 90. `client_secret` is write-only and never in the response, job registry or diagnostics. POST `/projects/prj_9f2c41aa07e1/connector/sign-in` opens the system browser and returns `{authorize_url,port}` (200). The authorization URL is a short-lived state/PKCE initiation URL, not an access token; it must not be persisted or logged.

Microsoft redirects to **root** `http://localhost:<port>/connector/callback?code=...&state=...`. This is **not** `/api/v1/connector/callback`. The browser supplies no launch token/project header. Only an unexpired, single-use state bound to the pending project and PKCE verifier authorizes the exchange (doc 12 §1.1). Invalid/missing/replayed state gives fixed HTTP 400 HTML without an exchange; success gives fixed 200 close-tab HTML. No callback query is echoed. Polling the authenticated connector status exposes only a redacted `last_auth_error` or signed-in state.

POST `/projects/prj_9f2c41aa07e1/connector/test` is an explicit foreground action. A completed entity check returns 200 even if `entity_check.ok=false`; the missing list supplies repair candidates. Pulling with a missing required entity then fails ERR-114. GET companies uses the last explicit test's cache; it never refreshes over the network by itself. A profile PUT returns its saved version and check result, not a job result or an invented list of top-level candidates.

## 5. Pull and no-change result
POST `/projects/prj_9f2c41aa07e1/connector/pull`, JSON (with headers §1):
```json
{"period_id":"2025-P07","sources":["gl","ap","tb"]}
```
HTTP 202 `{job_id}`. A locked target is rejected **before** creating a job or opening a socket with 423/FP&A-ERR-027, not ERR-030.

A done `connector-pull` job uses the same full envelope as §3 and this exact `result`:
```json
{
  "pull_id":"pul_7c0d12e4aa91",
  "status":"staged",
  "snapshot_sha256":"5e1c000000000000000000000000000000000000000000000000000000000000",
  "batches":[
    {"batch_id":"bat_a91f00000001","source_kind":"gl","rows_in":48213,"quarantined":3,"status":"validated"},
    {"batch_id":"bat_b02000000001","source_kind":"subledger","rows_in":1120,"quarantined":0,"status":"validated"}
  ],
  "row_counts":{
    "gl":{"status":"pulled","expected":48213,"received":48213,"pages":5,"retries":1,"note":null},
    "ap":{"status":"pulled","expected":1120,"received":1120,"pages":1,"retries":0,"note":null},
    "tb":{"status":"skipped","expected":0,"received":0,"pages":0,"retries":0,"note":"No standard F&O trial-balance entity; import the Trial balance file."}
  },
  "auto_commit_job_ids":[]
}
```
The three Tax-layer rows are quarantined as OUT_OF_SCOPE_LAYER. Auto-commit is not enqueued because quarantine is nonzero. Review and commit via the same file pipeline. An enabled, all-clean auto-commit instead supplies separate commit job ids; their errors never corrupt the successful staged-pull record.

An unchanged ledger's result is:
```json
{"pull_id":"pul_7c0d12e4aa92","status":"no_change","snapshot_sha256":"5e1c000000000000000000000000000000000000000000000000000000000000","batches":[],"row_counts":{},"auto_commit_job_ids":[]}
```
POST check-changes is also a job (`connector-check-changes`): result `{changed_rows:null,last_pull_at:null}` means no watermark available, **not** zero changes. Its API result must not be interpreted as permission to skip a full pull.

## 6. Cancellation and failures
POST `/jobs/job_commit_0001/cancel`, no body: terminal job returns 200 `{job_id:"job_commit_0001",status:"done",cancel_requested:false,cancellable:false}`. During a commit transaction, cancellation is refused with both flags false; the transaction finishes or rolls back. A queued cancellation ends in cancelled/ERR-004. App restart interrupts running jobs with failed/ERR-008. Neither is a local HTTP 499.

A connector retry exhaustion error (inside failed job envelope):
```json
{"code":"FP&A-ERR-115","message":"Dynamics 365 is busy and kept asking us to wait.","hint":"Try again in a few minutes; pulling outside business hours is faster","retryable":true,"details":{"source":"gl","page":4,"attempts":5,"last_status":429}}
```
Do not forward upstream 429 as the local endpoint status. Asynchronous results/errors have schemas in doc 64's attachment; synchronous errors use doc 05's status table. Tokens, authorization codes and raw URLs must not appear in either.

## 7. Finance boundaries and pagination
A BvA amount is `"125000.50"`, not `125000.50`; zero-budget variance percent is null with `var_pct_reason:"zero_budget"`. Money strings adapt to the project currency's 0/2/3 exponent (doc 27); the UI formats, never computes. Drill list uses `{items:[Voucher],next_cursor:null}`. Rows within one large voucher are separately paged; do not embed 250k rows in a single voucher item. All list cursors bind the project, request filters and snapshot. Changed snapshot produces ERR-003; wrong/tampered cursor ERR-002. Statement aggregates and job summaries are not an alternate path for dumping the transaction table.
