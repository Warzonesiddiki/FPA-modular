# 63 — API EXAMPLES & PAYLOAD COOKBOOK

> Normative examples, not a running server (M3 is not built). Doc 05 §1 owns protocol; doc 64 owns async results; doc 90 indexes schemas. Every amount is a **decimal string**. Examples use synthetic IDs. No example contains a real token or tenant credential. `X-FPA-Token` values come from the shell; never put them in URLs.

## 1. Local session and project context
All application routes are relative to `http://127.0.0.1:<port>/api/v1`; send `X-FPA-Token` for health/project operations too. Project-scoped examples additionally send `X-FPA-Project: prj_9f2c41aa07e1`. The server checks that it matches any project path and every referenced resource. POSTs creating jobs send a new `Idempotency-Key` (example `month-end-2025-P07-commit-1`). GETs send no body. OPTIONS handling and exact-origin rules are in doc 12 §1.1.

Same key/same payload returns the original receipt; changed payload with that key returns 400/FP&A-ERR-005. A new key does not bypass lifecycle guards. Missing launch token returns 401/FP&A-ERR-006, and a foreign Origin/Host is 403/FP&A-ERR-007, before project lookup.

## 2. Create a project (doc 05 §6.3)
POST `/projects` with token and required Idempotency-Key; no project selection or query. All request fields are required, including the initial FY **start year**. This is a synthetic example, not a running endpoint.
<!-- contract: ProjectCreate -->
```json
{
  "name": "Meridian FY27",
  "base_currency": "INR",
  "fy_start_month": 4,
  "calendar_type": "monthly",
  "fiscal_year": 2026
}
```
HTTP 201, complete Project metadata:
<!-- contract: Project -->
```json
{
  "project_id": "prj_9f2c41aa07e1",
  "name": "Meridian FY27",
  "base_currency": "INR",
  "currency_exponent": 2,
  "fy_start_month": 4,
  "calendar_type": "monthly",
  "is_sample": false,
  "version": 1,
  "created_at": "2026-10-14T09:00:00Z",
  "updated_at": "2026-10-14T09:00:00Z"
}
```
The server also creates FY2026's twelve periods (Apr-2026…Mar-2027); they are a separate paged resource. No client can set is_sample, exponent, timestamps, path or id. A same-key replay returns this original 201/id/body without extra rows/audit; a deleted target is ERR-001, never recreated. JPY derives exponent 0 and KWD derives 3; unknown currencies are not guessed. Only POST periods can explicitly add another year (§8).

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

## 8. Health, project reads and fiscal-year creation (doc 05 §6)
GET `/health` with the launch token → 200 (example installed version):
<!-- contract: Health -->
```json
{
  "status": "ok",
  "version": "0.1.0"
}
```
GET `/projects?is_sample=false&limit=100` → 200:
<!-- contract: ProjectPage -->
```json
{
  "items": [
    {
      "project_id": "prj_9f2c41aa07e1",
      "name": "Meridian FY27",
      "base_currency": "INR",
      "currency_exponent": 2,
      "fy_start_month": 4,
      "calendar_type": "monthly",
      "is_sample": false,
      "version": 1,
      "created_at": "2026-10-14T09:00:00Z",
      "updated_at": "2026-10-14T09:00:00Z"
    }
  ],
  "next_cursor": null
}
```
GET `/projects/prj_9f2c41aa07e1` with the matching X-FPA-Project header → 200 the exact Project in §2, **not** a periods/close-progress wrapper.

GET `/projects/prj_9f2c41aa07e1/periods?fiscal_year=2026&limit=1` with the same header → 200 a first page. The cursor below is a schematic opaque value; only the server issues real signed cursors and callers must not construct it:
<!-- contract: PeriodPage -->
```json
{
  "items": [
    {
      "project_id": "prj_9f2c41aa07e1",
      "period_id": "2026-P01",
      "fiscal_year": 2026,
      "period_no": 1,
      "start_date": "2026-04-01",
      "end_date": "2026-04-30",
      "status": "open",
      "locked_at": null,
      "lock_note": null,
      "version": 1,
      "created_at": "2026-10-14T09:00:00Z",
      "updated_at": "2026-10-14T09:00:00Z"
    }
  ],
  "next_cursor": "opaque-server-issued-cursor"
}
```
GET `/projects/prj_9f2c41aa07e1/periods/2026-P01` → 200:
<!-- contract: Period -->
```json
{
  "project_id": "prj_9f2c41aa07e1",
  "period_id": "2026-P01",
  "fiscal_year": 2026,
  "period_no": 1,
  "start_date": "2026-04-01",
  "end_date": "2026-04-30",
  "status": "open",
  "locked_at": null,
  "lock_note": null,
  "version": 1,
  "created_at": "2026-10-14T09:00:00Z",
  "updated_at": "2026-10-14T09:00:00Z"
}
```
An empty filtered period list is `{"items":[],"next_cursor":null}`; GET never creates missing years. A valid but absent single period instead returns 404/ERR-001. Locked periods remain readable with locked_at populated and their current version; ensuring the FY does not reopen them.

POST `/projects/prj_9f2c41aa07e1/periods` (token + matching project header; optional Idempotency-Key):
<!-- contract: FiscalYearCreate -->
```json
{
  "fiscal_year": 2027
}
```
First creation → 201, exactly twelve periods. Repeat without a key → 200 with the existing state, never reset locks/timestamps. The February below intentionally exercises the leap year 2028:
<!-- contract: FiscalYearPeriods -->
```json
{
  "project_id": "prj_9f2c41aa07e1",
  "fiscal_year": 2027,
  "periods": [
    {
      "project_id": "prj_9f2c41aa07e1",
      "period_id": "2027-P01",
      "fiscal_year": 2027,
      "period_no": 1,
      "start_date": "2027-04-01",
      "end_date": "2027-04-30",
      "status": "open",
      "locked_at": null,
      "lock_note": null,
      "version": 1,
      "created_at": "2026-10-14T09:00:00Z",
      "updated_at": "2026-10-14T09:00:00Z"
    },
    {
      "project_id": "prj_9f2c41aa07e1",
      "period_id": "2027-P02",
      "fiscal_year": 2027,
      "period_no": 2,
      "start_date": "2027-05-01",
      "end_date": "2027-05-31",
      "status": "open",
      "locked_at": null,
      "lock_note": null,
      "version": 1,
      "created_at": "2026-10-14T09:00:00Z",
      "updated_at": "2026-10-14T09:00:00Z"
    },
    {
      "project_id": "prj_9f2c41aa07e1",
      "period_id": "2027-P03",
      "fiscal_year": 2027,
      "period_no": 3,
      "start_date": "2027-06-01",
      "end_date": "2027-06-30",
      "status": "open",
      "locked_at": null,
      "lock_note": null,
      "version": 1,
      "created_at": "2026-10-14T09:00:00Z",
      "updated_at": "2026-10-14T09:00:00Z"
    },
    {
      "project_id": "prj_9f2c41aa07e1",
      "period_id": "2027-P04",
      "fiscal_year": 2027,
      "period_no": 4,
      "start_date": "2027-07-01",
      "end_date": "2027-07-31",
      "status": "open",
      "locked_at": null,
      "lock_note": null,
      "version": 1,
      "created_at": "2026-10-14T09:00:00Z",
      "updated_at": "2026-10-14T09:00:00Z"
    },
    {
      "project_id": "prj_9f2c41aa07e1",
      "period_id": "2027-P05",
      "fiscal_year": 2027,
      "period_no": 5,
      "start_date": "2027-08-01",
      "end_date": "2027-08-31",
      "status": "open",
      "locked_at": null,
      "lock_note": null,
      "version": 1,
      "created_at": "2026-10-14T09:00:00Z",
      "updated_at": "2026-10-14T09:00:00Z"
    },
    {
      "project_id": "prj_9f2c41aa07e1",
      "period_id": "2027-P06",
      "fiscal_year": 2027,
      "period_no": 6,
      "start_date": "2027-09-01",
      "end_date": "2027-09-30",
      "status": "open",
      "locked_at": null,
      "lock_note": null,
      "version": 1,
      "created_at": "2026-10-14T09:00:00Z",
      "updated_at": "2026-10-14T09:00:00Z"
    },
    {
      "project_id": "prj_9f2c41aa07e1",
      "period_id": "2027-P07",
      "fiscal_year": 2027,
      "period_no": 7,
      "start_date": "2027-10-01",
      "end_date": "2027-10-31",
      "status": "open",
      "locked_at": null,
      "lock_note": null,
      "version": 1,
      "created_at": "2026-10-14T09:00:00Z",
      "updated_at": "2026-10-14T09:00:00Z"
    },
    {
      "project_id": "prj_9f2c41aa07e1",
      "period_id": "2027-P08",
      "fiscal_year": 2027,
      "period_no": 8,
      "start_date": "2027-11-01",
      "end_date": "2027-11-30",
      "status": "open",
      "locked_at": null,
      "lock_note": null,
      "version": 1,
      "created_at": "2026-10-14T09:00:00Z",
      "updated_at": "2026-10-14T09:00:00Z"
    },
    {
      "project_id": "prj_9f2c41aa07e1",
      "period_id": "2027-P09",
      "fiscal_year": 2027,
      "period_no": 9,
      "start_date": "2027-12-01",
      "end_date": "2027-12-31",
      "status": "open",
      "locked_at": null,
      "lock_note": null,
      "version": 1,
      "created_at": "2026-10-14T09:00:00Z",
      "updated_at": "2026-10-14T09:00:00Z"
    },
    {
      "project_id": "prj_9f2c41aa07e1",
      "period_id": "2027-P10",
      "fiscal_year": 2027,
      "period_no": 10,
      "start_date": "2028-01-01",
      "end_date": "2028-01-31",
      "status": "open",
      "locked_at": null,
      "lock_note": null,
      "version": 1,
      "created_at": "2026-10-14T09:00:00Z",
      "updated_at": "2026-10-14T09:00:00Z"
    },
    {
      "project_id": "prj_9f2c41aa07e1",
      "period_id": "2027-P11",
      "fiscal_year": 2027,
      "period_no": 11,
      "start_date": "2028-02-01",
      "end_date": "2028-02-29",
      "status": "open",
      "locked_at": null,
      "lock_note": null,
      "version": 1,
      "created_at": "2026-10-14T09:00:00Z",
      "updated_at": "2026-10-14T09:00:00Z"
    },
    {
      "project_id": "prj_9f2c41aa07e1",
      "period_id": "2027-P12",
      "fiscal_year": 2027,
      "period_no": 12,
      "start_date": "2028-03-01",
      "end_date": "2028-03-31",
      "status": "open",
      "locked_at": null,
      "lock_note": null,
      "version": 1,
      "created_at": "2026-10-14T09:00:00Z",
      "updated_at": "2026-10-14T09:00:00Z"
    }
  ]
}
```
No page cursor is needed for this bounded twelve-row action result. The next GET periods still obeys limit/cursor. FY 0000 and full-year creation for 9999 are rejected before writes (ERR-002); FY0001 and FY9998 are valid creation bounds. These examples validate shapes and calendar oracles, not database atomicity or an implemented endpoint.

## 9. Sample workspace, deletion, start-close and unlock (doc 05 §7)
All examples are synthetic contract fixtures, not calls against a server. Every request carries the launch token. Project-scoped requests carry X-FPA-Project equal to their path id. Sample creation and deletion require Idempotency-Key; the period actions accept it optionally. No query parameters are accepted by these four endpoints.

### 9.1 Create a separate sample workspace
POST `/projects/sample`:
<!-- contract: SampleProjectCreate -->
```json
{
  "name": "Sample Company"
}
```
HTTP 201:
<!-- contract: CreatedSampleProject -->
```json
{
  "project_id": "prj_9f2c41aa07e2",
  "name": "Sample Company",
  "base_currency": "INR",
  "currency_exponent": 2,
  "fy_start_month": 4,
  "calendar_type": "monthly",
  "is_sample": true,
  "version": 1,
  "created_at": "2026-10-14T09:00:00Z",
  "updated_at": "2026-10-14T09:00:00Z"
}
```

The server has created FY2024–FY2026 (36 open periods), normal default settings/COA and a sample flag, not pre-committed books. Use normal import steps to load bundled masters first and then the financial files, or explicitly connect the local demo ledger. Project lists show this flag; it cannot be supplied on ordinary project creation or cleared by a client field.

### 9.2 Delete after exact confirmation
DELETE `/projects/prj_9f2c41aa07e1`, with matching project header and a fresh key:
<!-- contract: ProjectDelete -->
```json
{
  "expected_version": 1,
  "confirmation": "Meridian FY27"
}
```
HTTP 200, only after durable move/revocation/catalogue/audit/receipt:
<!-- contract: ProjectDeleted -->
```json
{
  "project_id": "prj_9f2c41aa07e1",
  "status": "trashed",
  "deleted_at": "2026-10-14T09:00:00Z",
  "purge_after": "2026-11-13T09:00:00Z"
}
```

This is private trash, not immediate erasure. UTC October 14 + 30 days is November 13, not November 14. The app may purge later if offline. A same-key replay returns the same receipt; normal GETs return 404. A different casing or trailing space in the typed confirmation gives ERR-013, even though active-name uniqueness on creation uses casefold. The app does not delete another project's files or externally saved exports/backups.

### 9.3 Enter close deliberately
For the open version-1 April Period in §8, POST `/projects/prj_9f2c41aa07e1/periods/2026-P01/start-close`:
<!-- contract: PeriodStartClose -->
```json
{
  "expected_version": 1
}
```
HTTP 200:
<!-- contract: ClosingPeriod -->
```json
{
  "project_id": "prj_9f2c41aa07e1",
  "period_id": "2026-P01",
  "fiscal_year": 2026,
  "period_no": 1,
  "start_date": "2026-04-01",
  "end_date": "2026-04-30",
  "status": "closing",
  "locked_at": null,
  "lock_note": null,
  "version": 2,
  "created_at": "2026-10-14T09:00:00Z",
  "updated_at": "2026-10-14T09:00:01Z"
}
```

The task template and audit were created in that transaction; no task was falsely marked complete. A fresh call with expected_version=2 while already closing fails ERR-016 (`action=start_close`), not a second template. Merely reading a checklist would not have produced this state.

### 9.4 Reopen a locked period with a reason
Assume April is now locked at version 3. POST `/projects/prj_9f2c41aa07e1/periods/2026-P01/unlock`:
<!-- contract: PeriodUnlock -->
```json
{
  "expected_version": 3,
  "note": "Re-import the corrected April ledger; approved by the controller."
}
```
HTTP 200:
<!-- contract: ClosingPeriod -->
```json
{
  "project_id": "prj_9f2c41aa07e1",
  "period_id": "2026-P01",
  "fiscal_year": 2026,
  "period_no": 1,
  "start_date": "2026-04-01",
  "end_date": "2026-04-30",
  "status": "closing",
  "locked_at": null,
  "lock_note": null,
  "version": 4,
  "created_at": "2026-10-14T09:00:00Z",
  "updated_at": "2026-10-14T09:00:01Z"
}
```

Old lock metadata and the immutable pre-unlock baseline are in RESTATE_OPEN history, not discarded. The current period has null lock metadata and revision 4, not open/revision 1. The previous sign-off is historical; this action does not waive impact review or approve re-lock. With a valid expected_version but missing/null/blank note, return 400 ERR-015 (`details.action=unlock`); a missing version, non-string/oversized/control-containing note or unknown field gives ERR-002. Stale version → ERR-003 before lifecycle mutation. Runtime atomicity/leases and baseline persistence remain M1/M3 verification work.

## 10. Review → sign-off → lock (doc 05 §8)
Synthetic complete fixtures, not executed HTTP calls. Every call requires X-FPA-Token, exact local authority/origin and X-FPA-Project=prj_9f2c41aa07e1. Both POSTs require distinct Idempotency-Key values. No query or client actor is accepted. The project has completed the prerequisites and has a current checked pack; the fixed hashes below stand for immutable synthetic manifests, not actual financial results.

### 10.1 Inspect without side effects
GET `/projects/prj_9f2c41aa07e1/periods/2026-P01/close-readiness` → 200:
<!-- contract: CloseReadiness -->
```json
{
  "review": {
    "project_id": "prj_9f2c41aa07e1",
    "period_id": "2026-P01",
    "period_version": 2,
    "audit_head": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "snapshot_id": "snapshot_close_1",
    "blocker_fingerprint": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945"
  },
  "review_token": "4dae58139f4db3910d02eec2df87b14fab580f74a6a7df512b13fee454c6a0eb",
  "period_status": "closing",
  "blockers": [],
  "current_signoff": null,
  "ready_to_sign_off": true,
  "ready_to_lock": false
}
```

The empty blocker fingerprint is SHA256 of the two UTF-8 bytes `[]`. The review token uses the exact domain prefix and canonical CloseReview bytes in doc 05. T-09/T-10 do not appear as impossible prerequisites. ready_to_lock is false because there is not yet a current sign-off.

### 10.2 Attest explicitly
POST `/close/sign-off`:
<!-- contract: CloseSignoffCreate -->
```json
{
  "period_id": "2026-P01",
  "expected_version": 2,
  "review_token": "4dae58139f4db3910d02eec2df87b14fab580f74a6a7df512b13fee454c6a0eb",
  "signer": "Controller",
  "attest": true,
  "override_note": null
}
```
201:
<!-- contract: CloseSignoff -->
```json
{
  "signoff_id": "signoff_1",
  "project_id": "prj_9f2c41aa07e1",
  "period_id": "2026-P01",
  "signer": "Controller",
  "attestation_text": "I confirm the pack for 2026-P01 is complete and reviewed",
  "at": "2026-10-14T09:00:00Z",
  "evidence": {
    "review": {
      "project_id": "prj_9f2c41aa07e1",
      "period_id": "2026-P01",
      "period_version": 2,
      "audit_head": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
      "snapshot_id": "snapshot_close_1",
      "blocker_fingerprint": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945"
    },
    "snapshot": {
      "snapshot_id": "snapshot_close_1",
      "batch_watermark": "dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd",
      "budget_version": "budget_1",
      "forecast_run_id": "forecast_1",
      "layer": "gl"
    },
    "override_note": null,
    "overridden_blockers": []
  }
}
```

The Period stays closing/version 2. This event advances the audit chain; the old review token must NOT be reused for lock. GET readiness again (the synthetic CLOSE_SIGNOFF event hash is c repeated 64 times) → 200:
<!-- contract: CloseReadiness -->
```json
{
  "review": {
    "project_id": "prj_9f2c41aa07e1",
    "period_id": "2026-P01",
    "period_version": 2,
    "audit_head": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
    "snapshot_id": "snapshot_close_1",
    "blocker_fingerprint": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945"
  },
  "review_token": "03b75d6416cd895a4dcd3a50cab9dd50af6373ca24789b43c73d4aa00ea93f5c",
  "period_status": "closing",
  "blockers": [],
  "current_signoff": {
    "signoff_id": "signoff_1",
    "project_id": "prj_9f2c41aa07e1",
    "period_id": "2026-P01",
    "signer": "Controller",
    "attestation_text": "I confirm the pack for 2026-P01 is complete and reviewed",
    "at": "2026-10-14T09:00:00Z",
    "evidence": {
      "review": {
        "project_id": "prj_9f2c41aa07e1",
        "period_id": "2026-P01",
        "period_version": 2,
        "audit_head": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "snapshot_id": "snapshot_close_1",
        "blocker_fingerprint": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945"
      },
      "snapshot": {
        "snapshot_id": "snapshot_close_1",
        "batch_watermark": "dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd",
        "budget_version": "budget_1",
        "forecast_run_id": "forecast_1",
        "layer": "gl"
      },
      "override_note": null,
      "overridden_blockers": []
    }
  },
  "ready_to_sign_off": true,
  "ready_to_lock": true
}
```

### 10.3 Lock the exact approved state
POST `/projects/prj_9f2c41aa07e1/periods/2026-P01/lock`:
<!-- contract: PeriodLock -->
```json
{
  "expected_version": 2,
  "review_token": "03b75d6416cd895a4dcd3a50cab9dd50af6373ca24789b43c73d4aa00ea93f5c",
  "signoff_id": "signoff_1",
  "force": false,
  "note": null
}
```
200:
<!-- contract: LockedPeriod -->
```json
{
  "project_id": "prj_9f2c41aa07e1",
  "period_id": "2026-P01",
  "fiscal_year": 2026,
  "period_no": 1,
  "start_date": "2026-04-01",
  "end_date": "2026-04-30",
  "status": "locked",
  "locked_at": "2026-10-14T09:00:00Z",
  "lock_note": null,
  "version": 3,
  "created_at": "2026-10-14T09:00:00Z",
  "updated_at": "2026-10-14T09:00:00Z"
}
```

Period is now locked/version 3, dates/created_at preserved, lock_note null because no override was requested. A same-key replay is historical; a fresh key against locked state fails ERR-016. A project mutation between review/sign-off/lock makes the review stale (ERR-080), even if counts happen to remain equal. A lock note alone cannot satisfy a reopened period's current impact approval (ERR-083). Missing force note → ERR-015; force+note still cannot override TB, audit, missing/current sign-off, stale forecast or impact review.


## 11. Restatement impact (DEC-021, doc 05 §9)
Synthetic illustrative values, not sample-corpus expectations. All calls use X-FPA-Token, X-FPA-Project: prj_000000000001 and the permitted Host/Origin. Both POSTs require distinct Idempotency-Key values. No caller-supplied actor/time or arbitrary path. Snapshot hashes illustrate immutable references, not files proved present.

### 11.1 Read context — GET /projects/prj_000000000001/periods/2026-P01/restatement
<!-- schema: RestatementState -->
```json
{
  "project_id": "prj_000000000001",
  "period_id": "2026-P01",
  "period_version": 4,
  "period_status": "closing",
  "baseline": {
    "baseline_id": "baseline_1",
    "project_id": "prj_000000000001",
    "period_id": "2026-P01",
    "unlock_version": 4,
    "before_snapshot": {
      "snapshot_id": "snapshot_old",
      "batch_watermark": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
      "budget_version": "budget_1",
      "forecast_run_id": "forecast_old",
      "layer": "gl"
    },
    "before_manifest_sha256": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
    "locked_at": "2026-10-13T10:00:00Z",
    "lock_note": null,
    "signoff_id": "signoff_old",
    "opened_at": "2026-10-14T10:00:00Z",
    "reason": "Correct April source data."
  },
  "current_impact_id": "impact_1",
  "current_approval_id": "approval_1"
}
```

### 11.2 Generate — POST /projects/prj_000000000001/periods/2026-P01/impacts
<!-- schema: ImpactCreate -->
```json
{
  "expected_version": 4,
  "baseline_id": "baseline_1",
  "after_snapshot_id": "snapshot_new"
}
```
<!-- schema: ImpactReport -->
```json
{
  "impact_id": "impact_1",
  "project_id": "prj_000000000001",
  "period_id": "2026-P01",
  "period_version": 4,
  "baseline_id": "baseline_1",
  "before_snapshot": {
    "snapshot_id": "snapshot_old",
    "batch_watermark": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "budget_version": "budget_1",
    "forecast_run_id": "forecast_old",
    "layer": "gl"
  },
  "after_snapshot": {
    "snapshot_id": "snapshot_new",
    "batch_watermark": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
    "budget_version": "budget_1",
    "forecast_run_id": "forecast_new",
    "layer": "gl"
  },
  "before_manifest_sha256": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
  "after_manifest_sha256": "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
  "changes_sha256": "33c44dcb8e226601ae3e97038099c0c7449f444f2f766dc6808dea82a1d92788",
  "counts": {
    "statement": 1,
    "bva": 1,
    "finding": 1,
    "forecast": 1,
    "report": 1
  },
  "created_at": "2026-10-14T10:00:00Z"
}
```

### 11.3 Read all changes — GET /impacts/impact_1/changes?limit=100
<!-- schema: ImpactChangePage -->
```json
{
  "items": [
    {
      "kind": "bva",
      "key": "9ef09f801c999309e27505529401bb4b4fa9b8cf1664356368546201cbd06b56",
      "statement": null,
      "line_key": null,
      "entity_id": "entity_1",
      "account_id": "account_rev",
      "cost_centre_id": null,
      "measure": "var_abs",
      "before": {
        "value": "20.00",
        "unavailable_reason": null,
        "drill_key": "drill_before_var"
      },
      "after": {
        "value": "45.00",
        "unavailable_reason": null,
        "drill_key": "drill_after_var"
      },
      "delta": "25.00"
    },
    {
      "kind": "finding",
      "key": "0a465cecc4adc7c0a5b06d355ba5d040b8f4ef9c2b67f4685450719e9c04b646",
      "finding_key": "EXC-001|2026-P01|entity_1|account_rev",
      "change": "added",
      "before_finding_id": null,
      "after_finding_id": "finding_1",
      "before_sha256": null,
      "after_sha256": "dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"
    },
    {
      "kind": "forecast",
      "key": "097b0ad9859571649cfb6e4a5d0bc23c922d93ea9059e45891706ea9053be259",
      "run_id": "forecast_old",
      "change": "stale"
    },
    {
      "kind": "report",
      "key": "6192b8cfd7fb481ba1bdf852902fa823c254169cf71cbb729fc460d6e1c996ab",
      "report_id": "report_old",
      "change": "superseded"
    },
    {
      "kind": "statement",
      "key": "8bf8c7b69568387a8f45109eff5238dd65bfd78c1a030fef29578794d0841fdc",
      "statement": "pl",
      "line_key": "rev",
      "entity_id": null,
      "account_id": null,
      "cost_centre_id": null,
      "measure": "amount",
      "before": {
        "value": "100.00",
        "unavailable_reason": null,
        "drill_key": "drill_before_rev"
      },
      "after": {
        "value": "125.00",
        "unavailable_reason": null,
        "drill_key": "drill_after_rev"
      },
      "delta": "25.00"
    }
  ],
  "next_cursor": null
}
```

### 11.4 Approve — POST /impacts/impact_1/approve
<!-- schema: ImpactApprovalCreate -->
```json
{
  "expected_version": 4,
  "signer": "Controller",
  "attest": true,
  "note": "Reviewed correction against the original pack."
}
```
<!-- schema: ImpactApproval -->
```json
{
  "approval_id": "approval_1",
  "project_id": "prj_000000000001",
  "period_id": "2026-P01",
  "period_version": 4,
  "impact_id": "impact_1",
  "baseline_id": "baseline_1",
  "before_snapshot_id": "snapshot_old",
  "after_snapshot_id": "snapshot_new",
  "before_manifest_sha256": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
  "after_manifest_sha256": "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
  "changes_sha256": "33c44dcb8e226601ae3e97038099c0c7449f444f2f766dc6808dea82a1d92788",
  "signer": "Controller",
  "attestation_text": "I reviewed the restatement impact for 2026-P01 and approve these changes",
  "note": "Reviewed correction against the original pack.",
  "at": "2026-10-14T10:00:00Z"
}
```

POST responses are 201; GET responses 200. §11.1 illustrates the state after §11.4, not permission to skip generation. GET /impacts/impact_1 and GET /impact-approvals/approval_1 return exactly these historical objects even after lock. Re-read readiness after approval, sign off, then re-read readiness again before lock. A second unlock/version change or changed financial manifest makes current ids null; the immutable history is unchanged. A well-shaped attempt to approve an old report fails 422 ERR-083 with {"reason":"approval_note_required"}; a null/blank note fails 400 ERR-002. Same-key replay can return an old success without restoring authority. Empty impact is counts all zero, changes_sha256=SHA256([]), and an empty page; it still needs explicit approval.
