# 64 — JOB & BACKGROUND PROCESS SPECIFICATION

> Normative asynchronous catalogue (DEC-016). Doc 05 §1 owns transport/auth; this document owns stages, cancellation and terminal result fields. `docs/api_job_schemas.json` is the accompanying JSON Schema 2020-12 contract, not runtime code. Doc 90 indexes its definitions. Monetary values in every result and error detail are **decimal strings in major units**, never JSON numbers or public `*_minor` fields.

## 1. Registry and lifecycle
Persist jobs and idempotency receipts in the project job registry (doc 04 module `jobs`, not an in-memory-only promise). One heavy job per project runs FIFO; reads never enter that queue. All project IDs and nested resource IDs are verified before enqueue, and permissions/lock/version guards are rechecked before transactional writes. Jobs are retained 7 days; idempotency receipts persist for project lifetime (doc 05 §1.3). Reads of another project's job return ERR-001, never its kind/status/result.

`Job`: `job_id, project_id, kind, status, stage, progress_pct, progress, created_at, started_at, finished_at, cancellable, error, result`, all required (nullable where stated). `status` is queued/running/done/failed/cancelled. `stage` is the catalogue stage key (below), not prose. `progress_pct` integer 0..100 or null; `progress` null except optional connector row/page counts `{source,page,pages,rows,count}` (source is gl/ap/tb/budget/masters; page≥0, pages nullable≥0, rows≥0, count nullable≥0). No financial rows or remote URLs in progress.

- queued: stage `queued`, null progress/start/finish/error/result; cancellable true.
- running: catalogue stage key; started_at present, finished_at/error/result null. `cancellable` reflects the stage, not a promise of immediate interruption.
- done: stage `done`, progress_pct 100, started_at/finished_at present, error null, exact result type for its kind, cancellable false.
- failed: stage `failed`, finished_at present, result null, ErrorBody present, cancellable false. started_at may be null if rejected on dequeue. Progress records the last measurable position (or null).
- cancelled: stage `cancelled`, finished_at present, result null, error code FP&A-ERR-004, cancellable false. started_at null for a queued cancellation.

Restart: running → failed/ERR-008, details `{reason:"interrupted"}`; queued remains queued and rechecks its guards. No job silently resumes a half-written transaction. A done result is published only after database/file commit; before publication, temporary outputs are deleted on cancellation/failure. Each log record includes job_id; logs are redacted (doc 65). Progress/stages/timestamps use injected clock/counters. A budget breach at >2× doc 36 logs a warning plus dataset hash, never changes calculated results.

## 2. Closed job catalogue
Stage keys are local protocol identifiers, mapped to user copy in doc 55; the UI never displays the key itself. The controller supplies the stage key; a calculation must not call a clock or network.

| Kind | Ordered running stages | Safe cancellation | Result type (§3) | Initiating operation |
|---|---|---|---|---|
| import-validate | reading, profiling, validating, summarising | between stages | ValidationResult | POST /imports/{batch_id}/validate |
| import-commit | checking_totals, writing_rows, trial_balance | before writing_rows only; once transaction starts, finish or rollback | CommitResult | POST /imports/{batch_id}/commit |
| import-enrich | loading, matching, writing | before writing only | EnrichmentResult | POST /imports/{batch_id}/enrich |
| rule-run | loading, evaluating, suggesting, verifying, assigning, publishing | between rules before publishing; publish atomic | RuleRunResult | POST /projects/{id}/exceptions/run |
| forecast-run | backtesting, fitting, writing | between groups before writing | ForecastRun | POST /projects/{id}/forecast/run |
| export-generate | snapshot, checking, rendering, stamping | before rendering only | ExportResult | POST /projects/{id}/exports |
| backup | copying, verifying | no | BackupManifest | POST /projects/{id}/backup |
| restore | copying, verifying, audit_verifying, publishing | no; prior folder stays intact on failure | RestoreResult | POST /projects/{id}/restore |
| audit-verify | walking | between rows | AuditVerifyResult | POST /projects/{id}/audit/verify |
| connector-pull | signing_in, checking_entities, counting, pulling, writing_snapshot, staging, validating | between pages/stages before publish; cleanup complete before cancelled | PullResult | POST /projects/{id}/connector/pull |
| connector-check-changes | signing_in, counting_changes | between requests | ChangeCheck | POST /projects/{id}/connector/check-changes |
| allocation-run | loading, allocating, writing | before writing | AllocationResult | POST /allocations/{id}/run |
| reconcile-run | loading, matching, summarising, writing | before writing | ReconResult | POST /projects/{id}/reconcile/run |
| year-end-close | checking, proposing, rolling_forward, publishing | before publishing; closing/opening committed together | YearEndResult | POST /projects/{id}/year-end/close |
| planning-integrate | loading, calculating, checking, writing | before writing | IntegratedResult | POST /projects/{id}/planning/integrate |
| report-render | snapshot, checking, rendering, stamping | before rendering only | Report | POST /report-definitions/{id}/render |
| diagnostics-bundle | collecting, redacting, archiving, publishing | before publishing | DiagnosticsResult | POST /diagnostics/bundle |
| ai-draft | minimising, requesting, guarding, saving | before saving; discard late provider response after cancel | Commentary | POST /projects/{id}/commentary/draft |

Every initiating operation returns 202 `{job_id}` and requires token, project context and Idempotency-Key (05 §1.3). Year-end **check** is a synchronous read/check, not year-end-close. Connector sign-in/start/callback, test and profile entity checks are explicit foreground user actions, not scheduled work; their synchronous response contracts are in doc 05/26 and security scope in doc 12 §1(d)/§1.1. No GET poll starts network activity; connector companies GET reads the most recent explicit connection-test result. Backup and restore are two distinct kinds, never the literal string `backup/restore`. Child auto-commit jobs use import-commit; they are not an additional kind.

### 2.1 Cancellation response
POST `/jobs/{id}/cancel` takes no body and returns 200 `{job_id,status,cancel_requested,cancellable}`. Unknown/foreign job → ERR-001. Queued is immediately cancelled, running sets a cooperative flag only when cancellable, an irreversible stage refuses with both booleans false and continues, terminal jobs return unchanged status with both booleans false. Completion can win the race; poll is authoritative. ERR-004 is a terminal job error, not a failing cancel HTTP status. All accepted cancellation requests are audited; repeated cancellation cannot undo completed effects.

## 3. Result field contracts
All object properties below are required unless marked optional; `nullable` means the property must be present with JSON null when unavailable. All strings have their semantic type in the schema attachment. Arrays are explicit, never a prose `object` placeholder. Large transaction/match/finding/forecast-line sets remain behind paged resource endpoints; job results carry IDs, bounded summaries and counts, not the whole ledger. IDs are non-empty opaque strings (doc 02); dates ISO, timestamps UTC Z. Money is a decimal string. Nullable ratios carry an explicit unavailable reason in their containing metric.

| Type | Fields and invariants |
|---|---|
| ValidationResult | batch_id; status staged/validated; rows_in, valid, quarantined (integers≥0, rows_in=valid+quarantined); reasons: list of ReasonCount; issues: list of ErrorBody; control: nullable ControlComparison. validated iff issues empty; quarantine alone does not block. Counts include empty rows even though empty raw cells are not persisted. |
| ReasonCount | reason from doc 06 §4 closed enum; count integer≥1. One row per reason, sorted by reason; sum=count quarantined. |
| ControlComparison | declared_rows nullable integer≥0; actual_rows integer≥0; declared_debit/declared_credit nullable Money; actual_debit/actual_credit Money; differences: list of AccountDifference. Missing declarations are null, not fabricated zero. |
| AccountDifference | account_id; erp, app, delta Money (delta=app−erp); zero differences list is empty. |
| CommitResult | batch_id; committed/quarantined integers≥0; tb_status balanced/waived/not_applicable; superseded_batch_id nullable ID; enrichment nullable EnrichmentResult. Failed totals/TB never produce done. not_applicable is restricted to non-GL kinds. A waiver must already have audited evidence, not a new boolean that bypasses the gate. |
| EnrichmentResult | matched, ambiguous, unmatched, already_had_vendor integers≥0, counting disjoint GL rows in the scoped batch. Never count ambiguous as matched. |
| RuleRunResult | run_id; findings_new/findings_reopened/findings_total integers≥0; not_run list of {rule_id,reason}; rules_executed list of EXC-001…028. Lists unique; every rule belongs to exactly one list; result does not inline findings. |
| ForecastRun | run_id; base_period_id; status draft/locked; created_at; method_map dictionary of group→method; accuracy dictionary of group→Accuracy. Methods are doc 08's eight names. Keys are the same in both dictionaries. Forecast lines are separately paged; no money numbers inside method metadata. |
| Accuracy | method; mape/bias/hit_rate nullable DecimalString; history_months integer≥0; excluded_zero_periods integer≥0; na_reason nullable string (required non-empty if any metric is null). No numeric JSON ratio. |
| CheckResult | name; expected/actual/delta Money; pass boolean. Comparison logic is owned by the calculation spec, not the UI. |
| Report | report_id; kind excel/pptx/pdf/journal; period_id; path (project/chosen-export-root relative, not an arbitrary URL); sha256 64 lowercase hex; checks list of CheckResult; snapshot: SnapshotRef. Journal reports also use this registry shape; CSV file format is not a separate report kind. |
| SnapshotRef | snapshot_id; batch_watermark (64 hex); budget_version nullable ID; forecast_run_id nullable ID; layer gl/gl_adj. Stored report snapshot stays immutable. |
| ExportResult | snapshot: SnapshotRef; reports list of Report, 1..3. For kind=all it contains exactly excel,pptx,pdf in that order and all share snapshot/period. A single-kind export has exactly one report. Publish the board pack only if all required outputs pass; Excel-alone may include failed Checks as documented in doc 09; PPT/PDF never do. |
| BackupManifest | path; sha256; files integer≥1; created_at; project_id; audit_head (64 hex or null for an empty chain). Manifest signature/hash checks and archive-entry detail live inside the backup manifest file; the job returns its verified summary, not a second manifest format. |
| RestoreResult | project_id; manifest: BackupManifest; verified boolean always true. False verification is failed/ERR-014, never done. Restored keyring credentials are absent by design. |
| AuditVerifyResult | ok boolean always true; rows_verified integer≥0; head_hash nullable SHA256. Chain break is failed/ERR-090 with first bad row details; no success-shaped false verdict. |
| PullResult | pull_id; status staged/no_change; snapshot_sha256 nullable SHA256; batches list of PulledBatch; row_counts dictionary keyed only by gl/ap/tb/budget/masters → SourceCount; auto_commit_job_ids list of ID. no_change has no batches or auto-commit jobs; sha is last known successful hash or null for a watermark-only first check. staged requires a hash and ≥1 batch; each source is accounted for or explicitly skipped. Auto-commit is enqueued as separate import-commit jobs **after** successful staging/validation only when every selected batch is clean and controls/TB pass. Those jobs have their own terminal results; a commit failure never retroactively turns a successful staged pull into a failed pull with surviving batches. |
| PulledBatch | batch_id; source_kind gl/subledger/tb_check/budget/masters; rows_in, quarantined integers≥0; status staged/validated. Counts refer to the snapshot result, not later current batch status. Rows skipped by posting-layer scope are quarantined and counted. |
| SourceCount | status pulled/skipped; expected, received, pages, retries integers≥0; note nullable string. pulled requires expected=received and note=null; skipped requires zero counts plus non-empty reason (e.g. no standard F&O TB entity). Requested unavailable optional source never disappears silently; required GL missing is failed/ERR-114. |
| ChangeCheck | changed_rows nullable integer≥0; last_pull_at nullable timestamp. Null count means watermark unavailable: UI must say “pull to check”, not “nothing changed”. |
| AllocationResult | run_id; def_id; period_id; status applied; pair_group_ids list of ID; total_allocated Money. Adjustments are balanced and applied atomically, source allocation; failure leaves no applied group. |
| ReconResult | recon_id; period_id; kind bank/ar/ap/payroll; status open/in_review; matched_groups, unmatched_gl, unmatched_subledger integers≥0; gl_total/subledger_total/unmatched_net/tolerance Money. Matches and both unmatched sides are paged under the recon resource, not embedded here. Completion is not sign-off. |
| YearEndResult | ye_id; fiscal_year integer 1..9998; closing_adjustments integer≥0; opening_batch_id; rollforward_delta Money exactly zero at project exponent; status confirmed. Difference is failed/ERR-082; no implicit plug. |
| IntegratedResult | run: ForecastRun; checks: list of CheckResult (all pass). Articulation failure is failed/ERR-102, no published run. |
| DiagnosticsResult | path; sha256; files integer≥1; created_at; redacted boolean always true. No secrets, financial values, snapshot rows, OAuth state or raw request bodies in the archive. |
| Commentary | commentary_id; period_id; scope exec_summary/forecast/variance:<key>; text; status draft; ai_assisted true; prompt_version; source_refs list of ID; version integer≥1. This job only drafts; approval is a human action. Guardrail rejection is failed/ERR-071 and persists no commentary. |

## 4. Failure envelope
`ErrorBody`: required `code` (FP&A-ERR-nnn from doc 22), `message`, `hint`, `retryable` boolean and `details`. Messages/hints/flags are doc-22-owned; schema validates shape, not a substitute wording catalogue. `details` is a closed, per-code object in the attachment, not arbitrary JSON. Row-level import failures remain quarantine reasons. Error text is escaped/redacted; untrusted provider strings are length-limited and credential-filtered before persistence. Details may contain monetary **decimal strings**, never raw minor-unit integers. ERR-004 details `{reason:"user_cancelled"}`; ERR-008 `{reason:"interrupted"}`; ERR-099 `{diagnostics_id}`. An unexpected exception must not expose its traceback in the API.

## 5. Verification requirement
`tests/docs/test_api_job_contract.py` validates every state/kind fixture against the JSON Schema and semantic invariants (counts, not-run partition, skipped sources, shared export snapshots), rejects numeric money, missing/unknown fields, invalid lifecycle combinations, out-of-range progress, cross-kind results and invalid error codes; ≥3 isolated schema mutations must be caught. It must fail on a missing/empty schema **as a contract assertion**, not an import error. M3 separately tests the real registry, HTTP endpoints, crash/cancellation races, money conversion and no-partial-artifact behaviour. Document-schema tests do not close that runtime gate.
