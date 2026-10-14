# 02 — DATA DICTIONARY

> Owner of: every table, field, type, and example. `app/store/schema.sql` must implement this 1:1 (schema-equality test, doc 14). Money is always INTEGER minor units (e.g., paise/cents); display formatting happens in calc/UI, never storage. All timestamps UTC ISO-8601. All IDs text.

## 1. Conventions
- `*_minor` INTEGER NOT NULL: money in minor units. Sign convention: debit positive, credit negative in `gl_rows.amount_minor` (doc 03 owns statement sign presentation).
- Every user-editable table carries `version INTEGER`, `created_at`, `updated_at` and writes an `audit_log` row on mutation (the actor is recorded in `audit_log.actor`; tables carry `created_by` only where listed below — `adjustments`, `report_definitions`, `close_tasks.completed_by`).
- Within an active project, soft-delete only via `is_active=0`; financial rows are never deleted — a batch is superseded (`import_batches.status='superseded'`). Explicit whole-project deletion is the separate typed-confirmation/trash/purge operation of doc 12 §2.1, not a row-deletion API (DEC-018).

## 2. Tables

### projects
| field | type | notes/example |
|---|---|---|
| project_id | TEXT PK | `prj_` + 12 hex |
| name | TEXT | "Acme India — FP&A" |
| base_currency | TEXT(3) | `INR` |
| currency_exponent | INTEGER | minor-unit digits, 2 for INR (doc 27); fixed at project creation |
| fy_start_month | INTEGER 1–12 | 4 = April |
| calendar_type | TEXT | `monthly` (v1); `445` reserved |
| created_at/updated_at | TEXT | UTC |
| is_sample | INTEGER 0/1 | sample company flagged everywhere |
| version | INTEGER ≥1 | metadata revision; required by §1 and doc 05 §6 |

### periods
| period_id TEXT (`2026-P01`) · project_id FK · fiscal_year INT · period_no INT 1–12 · start_date/end_date DATE · status TEXT `open|closing|locked` · locked_at TEXT NULL · lock_note TEXT NULL · version INTEGER ≥1 · created_at/updated_at TEXT UTC · **PK (project_id, period_id)** — period ids repeat across projects, so the key is composite; every FK to a period is logically `(project_id, period_id)` |

**Materialisation (DEC-017, doc 05 §6):** Project creation requires an explicit initial fiscal_year; it creates exactly 12 open periods atomically. Later years are explicitly ensured through POST periods (201 new / 200 unchanged); reads never create periods. Full-year creation accepts FY 1..9998; display ids zero-pad the year to four digits. Existing period status and lock history are never reset by ensuring a year.

**Period identity (normative):** `fiscal_year` = calendar year in which the fiscal year *starts*. `period_id = <fiscal_year>-P<period_no 01..12>`; with fy_start_month=4, `2026-P01` = April 2026, `2026-P12` = March 2027. PY of `2026-P01` = `2025-P01`. All docs' examples follow this.

### entities / accounts / cost_centres / vendors / owners
Master data, each: `<x>_id TEXT PK`, `project_id FK`, `code TEXT`, `name TEXT`, `is_active INT`, `version INT`, timestamps. `accounts` adds: `account_type` (`revenue|cogs|opex|asset|liability|equity|other`), `statement_line` (doc 45 §1 key), `normal_side` (`debit|credit`), `tags` TEXT (comma-separated closed list `suspense|accrual|accrual_balancing|contra|depreciation|cash|receivables|payables|inventory|debt|equity`, default `''`; doc 07/44 rules read `suspense`, `accrual`, `accrual_balancing`) and `ic_counterparty_entity_id NULL` (reserved, doc 49 §2). `cost_centres` adds `entity_id NULL` (a cost centre may be entity-scoped). `vendors` adds `linked_entity_id NULL` (reserved: vendor that is a group entity, doc 49). `owners`: `owner_id, display_name, email NULL, role_label, is_active`. `account_owners(account_id, owner_id, valid_from)` assigns accountability (doc 07).

### import_batches
| batch_id TEXT PK (`bat_`+hash12) · project_id · period_id · source_kind (`gl|budget|subledger|drivers|opening|masters|tb_check`) · subledger_kind (`bank|ar|ap|payroll`) NULL · source (`file|connector`, default `file`) · pull_id FK connector_pulls NULL (set when `source=connector`) · file_name · file_sha256 TEXT(64) · file_size INT · mapping_profile_id FK · status (`staged|validated|committed|rejected|superseded`, doc 23 §2) · row_count_in/valid/quarantined INT · control_debit_minor/control_credit_minor INT NULL (computed from staged rows) · declared_debit_minor/declared_credit_minor INT NULL · declared_row_count INT NULL · committed_at · supersedes_batch_id NULL · is_manual INT 0/1 (set when the file is a manual-journal extract or the analyst flags it; read by EXC-008) |

### import_rows_raw (staging, per batch)
| raw_id PK · batch_id FK · sheet_name TEXT · row_no INT (1-based in source incl. header offset recorded) · raw_json TEXT (original cells as strings) · parse_status (`ok|quarantined`) · quarantine_reason TEXT NULL |

### gl_rows (the fact table)
| gl_row_id TEXT PK = hash(batch_id+sheet+row_no) (deterministic, doc 06 §3) · project_id · period_id · batch_id FK · entity_id · account_id · cost_centre_id NULL · vendor_id NULL · voucher_no TEXT · document_date DATE · posting_date DATE · description TEXT (hostile data — never executed/rendered as markup) · amount_minor INT (debit +, credit −, in base currency) · quantity_decimal TEXT NULL (decimal string; floats are banned everywhere including drivers, doc 46) · fx_currency TEXT NULL · fx_amount_minor INT NULL · fx_rate TEXT NULL (transaction-currency triple, populated only when the source carries it; v1 never converts — doc 27) · layer TEXT NOT NULL (`gl`; adjustments live in `adjustments`, and the `gl_adj` view is a union — the column exists so system-generated rows such as year-end opening batches can be labelled `opening`) · posted_by TEXT NULL · posted_at TEXT NULL (poster/time columns when the extract has them; EXC-009) · posting_layer TEXT NULL (ERP posting layer as exported, e.g. D365 `Current`; rows outside `import.posting_layers` never reach this table — doc 06 §4) · source_account_ref TEXT NULL (the untouched source account string, e.g. D365 `601200-IN01-022-`, kept so a rectification journal can address the original line verbatim — doc 26 §7) · vendor_source TEXT NULL CHECK IN (`column`,`ap_match`) (how vendor_id was obtained; NULL when vendor_id is NULL — doc 06 §2 step 9) · source_file TEXT · source_row INT |

### mapping_profiles / mapping_rules
`mapping_profiles(profile_id PK, project_id, source_kind, name, version, is_default, created_at)`. `mapping_rules(profile_id FK, source_column TEXT, canonical_field TEXT, transform TEXT (`none|date:fmt|amount:debit_credit_cols|sign_flip`), constant_value TEXT NULL, PK(profile_id, canonical_field))`. Canonical fields: entity, account, cost_centre, vendor, voucher_no, document_date, posting_date, description, amount, debit, credit, quantity.

### budget_lines / budget_versions
`budget_versions(version_id PK, project_id, label (`Budget FY27 v1`), status (`draft|approved|locked`), created_at)`. `budget_lines(line_id TEXT PK, version_id FK, period_id, entity_id, account_id, cost_centre_id NULL, amount_minor INT)` + `UNIQUE INDEX ux_budget_grain ON budget_lines(version_id, period_id, entity_id, account_id, IFNULL(cost_centre_id,''))` — a composite PK over a nullable column would silently allow duplicates in SQLite, so uniqueness lives in this expression index, and a schema test inserts a duplicate grain expecting failure.

### driver_values
| driver_row_id TEXT PK · project_id · driver_id TEXT (`volume|price|headcount|rate|growth_pct|custom:<name>`) · period_id · entity_id NULL · account_id NULL · value_decimal TEXT (decimal string, parsed via money module rules — never float storage) · source (`import|manual|scenario`) · scenario_id NULL · assumption_id NULL (doc 48 link) · version INT | This is the single driver table (doc 29 §2 "planning drivers" = this table; there is no separate `planning_drivers`).

### forecast_runs / forecast_lines / scenarios
`forecast_runs(run_id PK, project_id, base_period_id, method_map_json TEXT, status (`draft|locked`), accuracy_json TEXT (per-group MAPE/bias), created_at)`. `forecast_lines(run_id FK, period_id, entity_id, account_id, cost_centre_id, amount_minor INT, method TEXT, PK(...))`. `scenarios(scenario_id PK, project_id, name (`Base|Upside|Downside|custom`), base_run_id FK, delta_json TEXT, status)`.

### findings (exceptions)
| finding_id TEXT PK = canonical key hash (doc 07 §2) · finding_key TEXT UNIQUE (`EXC-018|ENT|ACC|PERIOD|grain`) · rule_id TEXT `EXC-###` · project_id · period_id · entity_id · account_id · severity (`high|medium|low`) · amount_minor INT · evidence_json TEXT (row ids, values, thresholds — everything needed to re-derive) · suggestion_json TEXT NOT NULL (doc 07 §7.1 shape; kinds `investigate|commentary|none` carry an empty `lines[]`) · suggestion_status TEXT NOT NULL DEFAULT `proposed` CHECK IN (`proposed`,`queued`,`applied`,`exported`,`dismissed`) · suggestion_ref TEXT NULL (adjustment pair_group id when applied; report_id when exported) · status (`new|acknowledged|explained|corrected|verified|closed|waived`) · owner_id NULL · due_date DATE · waive_reason TEXT NULL · waive_expires DATE NULL · first_seen_run TEXT · last_seen_run TEXT |

### finding_comments / finding_history
Append-only. `finding_history(history_id AUTOINCREMENT, finding_id, at, actor, action, from_status, to_status, note)` — every transition. `finding_comments(comment_id AUTOINCREMENT, finding_id, at, actor, note)` — free-text notes (FR-EXC-011); exported in the owner action list.

### commentary
| commentary_id PK · project_id · period_id · scope (`exec_summary|variance:<key>|forecast`) · text TEXT · source_refs_json (variance/finding ids the numbers came from) · ai_assisted INT 0/1 · prompt_version TEXT NULL · version INT · status (`draft|approved`) |

### reports
| report_id PK · project_id · period_id · kind (`excel|pptx|pdf`) · path TEXT · sha256 · snapshot_json (statement/BvA/forecast run ids used) · created_at |

### settings / thresholds
`settings(project_id, key, value_json, version, PK(project_id,key))`. Rule thresholds are settings keys `rule.EXC-###.<param>` (doc 07 defaults).

### audit_log
| audit_id INTEGER PK AUTOINCREMENT · project_id · at TEXT · actor TEXT · entity_type TEXT · entity_id TEXT · action TEXT · before_json NULL · after_json NULL · canonical TEXT (the exact canonical serialisation that was hashed — stored so verification never depends on re-serialisation rules) · prev_hash TEXT · hash TEXT = SHA256(prev_hash + canonical) | Hash-chain verified on demand (S14); broken chain → read-only banner + restore guidance (doc 12).

## 3. Volumes & indexes
Design point: 250k gl_rows/project/year, 5M lifetime. Indexes: gl_rows(period_id, account_id), (voucher_no), (batch_id); findings(project_id, status, severity); budget_lines(version_id, period_id). No other indexes without a measured query (doc 15).

## 4. Example row (gl_rows)
`{"gl_row_id":"9f2c…","period_id":"2026-P01","voucher_no":"VCH-2026-0001","posting_date":"2026-04-03","account_id":"ACC-5100","amount_minor":-12500050,"source_file":"gl_apr.xlsx","source_row":142}` → ₹125,000.50 credit (expense accrual reversal, sign per §1).

## 5. Expansion tables (docs 19/29/30 — same conventions §1; schema.sql must include all)
- **close_templates** (DEC-022): project_id TEXT PK/FK · version INTEGER ≥1 · calendar_json TEXT NOT NULL (CloseCalendarRules, doc 05 §10) · entries_json TEXT NOT NULL (CloseTemplateEntry array, 10..1000) · created_at/updated_at TEXT UTC. Single current template per project; prior revisions retained by CLOSE_TEMPLATE_UPDATE audit before/after. Calendar keys in doc 62 project settings are projections of this one row, not duplicate mutable settings rows.
- **close_period_configs** (DEC-022): project_id TEXT · period_id TEXT · template_version INTEGER ≥1 · calendar_json TEXT NOT NULL (exact immutable CloseCalendarRules copied at start-close) · created_at TEXT UTC; PK(project_id,period_id), composite period FK. One frozen copy per instantiated period; never updated by template edits or unlock. Task definitions are copied into close_tasks, not read from the later template.
- **close_tasks**: task_id TEXT PK · project_id TEXT NOT NULL · period_id TEXT NOT NULL · template_key TEXT NOT NULL · title TEXT · owner_id TEXT NULL · due_offset_days INTEGER -60..60 (business-day offset, wire due_offset_business_days) · depends_on TEXT NULL (task_id in same project/period) · kind TEXT `system|attest|manual` · status TEXT (stored requested status per doc 23 §7; system/outcome rows store not_started, not a fake derived result) · completed_by TEXT NULL (human signer label, NOT authenticated actor) · completed_at TEXT NULL · note TEXT NULL · statements_fingerprint TEXT(64) NULL · attestation_stale INTEGER 0/1 NOT NULL DEFAULT 0 · locked_status TEXT NULL (effective status frozen atomically by PERIOD_LOCK; cleared on unlock) · version INTEGER ≥1 · created_at/updated_at TEXT UTC. UNIQUE(project_id,period_id,template_key); composite period FK, same-period dependency and acyclicity enforced by period_repo under one transaction. Mapped public requested_status=null and no attestation for system/outcome tasks. Human terminal states reconstruct CloseTaskAttestation from completed_by/completed_at/note/statements_fingerprint; nonterminal clears these completion fields (audit retains prior evidence). T-04 statement-input mutation or unlock permanently sets attestation_stale=1 until fresh attestation; no GET writes it. Invalidation must be part of the input mutation's atomic boundary, not a background repair. Live due_date is derived by core/calendar from the frozen rules and current stored offset; no second date value to drift. locked_status projects status while locked, all other frozen task fields remain unchanged. Public review_token/evaluated_on/overdue/effective status are derived, never client-authored columns.

DEC-022 ownership: period_repo persists templates/period copies/task rows, sign-offs and typed close-history reads from audit_log; close_service orchestrates guards, derived task evidence, token binding and atomic invalidation/lock capture using that repository; core/calendar owns business dates. PERIOD_LOCK after_json stores exactly CloseLockRecord (doc 05 §10), with no wrapper; CLOSE_SIGNOFF and RESTATE_OPEN resolve the immutable sign-off/baseline. No additional SQL table is invented for public history. Existing legacy rows/events without evidence are never promoted to fresh attestations. Migration must preserve original rows/audit and mark unbound T-04 stale; if no authentic historical calendar/baseline can be recovered, flag it for explicit migration resolution before task writes rather than fabricate a historical snapshot. The full legacy repair, statement-manifest/invalidation and impact storage contracts remain WI-0001 follow-through before M1 implementation.
- **close_signoffs**: signoff_id PK · project_id · period_id · signer · attestation_text · snapshot_json · at. Immutable. DEC-020: snapshot_json stores exactly CloseSignoffEvidence (doc 05 §8.0); public evidence decodes this JSON, not a second copy/table. Its CLOSE_SIGNOFF audit event identifies the row via entity_type=close_signoff/entity_id=signoff_id. The event hash is read from audit_log, never hashed into itself. Legacy evidence without this binding is historical only and cannot authorise lock; no fabricated approval during migration.
- **headcount_plans**: plan_id PK · project_id · period_id · cost_centre_id · opening_hc INT · joiners INT · leavers INT · avg_cost_minor INT · increment_pct TEXT · bonus_pct TEXT.
- **capex_assets**: asset_id PK · project_id · class_label · cost_minor INT · addition_period · useful_life_months INT · method (`slm|wdv`) · residual_pct TEXT · disposal_period NULL · proceeds_minor NULL.
- **debt_schedules**: facility_id PK · project_id · label · opening_minor INT · rate_pct TEXT · kind (`fixed|floating`) — movements in **debt_movements**(facility_id, period_id, kind `draw|repay`, amount_minor).
- **wc_assumptions**: project_id · entity_id · dso_days/dpo_days/dio_days TEXT · effective_period. PK(project_id, entity_id, effective_period).
- **cash13_inputs**: input_id PK · project_id · week_start DATE · kind (`ar_due|ap_due|payroll|debt|capex|tax|other_in|other_out`) · amount_minor · party_label NULL · source_ref.
- **recon_runs**: recon_id PK · project_id · period_id · kind (`bank|ar|ap|payroll`) · batch_id (the sub-ledger batch) · tolerance_minor INT · status (doc 23 §8) · signed_by/at. **recon_matches**: recon_id FK · side (`subledger|gl`) · ref_id · amount_minor · matched_group NULL · score TEXT.
- **alerts**: alert_id PK · project_id · alert_key · period_id · kind (`kpi|finding|bias|close`) · severity · message · status (doc 23 §9) · seen_count INT · created_at/last_seen.
- **report_definitions**: def_id PK · project_id · name · blocks_json (statement/bva/kpi blocks, grain, period mode) · version · created_by.
All expansion tables carry created_at/updated_at/version and audit-on-mutation per §1.

### Retained input bindings and restatement records (DEC-023, doc 24 §5)
All columns below are NOT NULL unless marked NULL. Project-scoped keys/FKs include project_id; period ownership always includes project_id. All referenced records must have matching project/period scope, validated inside the publication transaction. No cascade deletion of retained evidence. JSON payloads are canonical UTF-8 objects with the exact closed DTO named below, not client-supplied arbitrary JSON. Equality of scalar columns to decoded payload fields is a release-blocking repository test. Metadata/audit/evidence JSON may retain the **public decimal-string** financial values of ImpactChange; it is not a second arithmetic store and is never reparsed as float. Source financial tables retain INTEGER minor units per §1.

| Table | Columns (SQLite types) | Key / payload contract |
|---|---|---|
| input_revisions | project_id TEXT; statement_revision INTEGER; forecast_revision INTEGER; pack_revision INTEGER | PK project_id, FK projects; all counters 1..9223372036854775807, statement≤forecast≤pack. InputRevisions; created once, advanced only by db.py primitive. |
| input_revision_events | project_id TEXT; audit_id INTEGER; advance_json TEXT | PK(project_id,audit_id), same-project audit_log FK; immutable InputRevisionAdvance containing project_id, audit_id, effects, before, after. Exactly one per input-affecting committed command, none for an empty effect set. |
| snapshot_input_bindings | project_id TEXT; snapshot_id TEXT; period_id TEXT; binding_json TEXT | PK(project_id,snapshot_id), composite period FK; immutable SnapshotInputBinding. Does not itself store the full manifest/views: those tables/bytes remain mandatory WI-0001 work before runtime implementation. |
| forecast_input_bindings | project_id TEXT; run_id TEXT; forecast_revision INTEGER | PK(project_id,run_id), forecast_runs FK with same-project enforcement; immutable ForecastInputBinding, capture before computation and recheck on publication. |
| restatement_baselines | project_id TEXT; baseline_id TEXT; period_id TEXT; unlock_version INTEGER; before_snapshot_id TEXT; audit_id INTEGER; record_json TEXT | PK(project_id,baseline_id), UNIQUE(project_id,period_id,unlock_version); composite period/snapshot binding FKs and same-project audit FK; immutable RestatementBaseline (§5.1 below). |
| restatement_impacts | project_id TEXT; impact_id TEXT; period_id TEXT; period_version INTEGER; baseline_id TEXT; after_snapshot_id TEXT; audit_id INTEGER; record_json TEXT | PK(project_id,impact_id); composite baseline/after-snapshot/period FKs and same-project audit FK; immutable ImpactReport. Before snapshot/hash equals baseline; after equals snapshot binding; version matches capture. |
| restatement_changes | project_id TEXT; impact_id TEXT; ordinal INTEGER; kind TEXT; change_key TEXT; record_json TEXT | PK(project_id,impact_id,ordinal), UNIQUE(project_id,impact_id,kind,change_key), composite impact FK; ordinal starts at 0 and is contiguous in (kind,key) order; kind statement/bva/finding/forecast/report, change_key=ImpactChange.key, record_json exactly ImpactChange. Counts and canonical changes_sha256 must match the complete ordered rows, never a page hash. |
| restatement_approvals | project_id TEXT; approval_id TEXT; impact_id TEXT; audit_id INTEGER; record_json TEXT | PK(project_id,approval_id), composite impact FK and same-project audit FK; immutable ImpactApproval, exact report/snapshot/cycle/hash bindings. One impact may have multiple historical approvals; never UPDATE the old record. |
| impact_invalidations | project_id TEXT; impact_id TEXT; audit_id INTEGER; pack_revision INTEGER | PK(project_id,impact_id), composite impact FK and (project_id,audit_id) FK to input_revision_events; immutable first InputInvalidation, its pack_revision is that event's after.pack_revision and greater than the captured impact binding. |

#### 5.1 Internal record shapes and write boundary
Internal shapes in the existing schema attachment (not HTTP requests/endpoints):
- **InputRevisions**: project_id: ProjectId; statement_revision/forecast_revision/pack_revision: integer 1..9223372036854775807.
- **InputRevisionAdvance**: project_id: ProjectId; audit_id: positive integer; effects: exactly [pack_inputs], [forecast_inputs,pack_inputs] or [statement_inputs,forecast_inputs,pack_inputs]; before/after: InputRevisions, same project. Each selected counter after=before+1; others unchanged; overflow aborts. No user actor/time or mutable resource versions in this object.
- **SnapshotInputBinding**: project_id: ProjectId; snapshot_id: Id; period_id: PeriodId; revisions: InputRevisions; manifest_sha256: Sha256; statements_fingerprint: Sha256. Binding.project equals revisions.project; all scopes/hashes match retained content.
- **ForecastInputBinding**: project_id: ProjectId; run_id: Id; forecast_revision: bounded positive revision.
- **InputInvalidation**: project_id: ProjectId; impact_id: Id; audit_id: positive integer; pack_revision: bounded positive revision. First invalidating input event, never an API override.
- **RetainedBaselineRecord**: project_id: ProjectId; audit_id: positive integer; record: RestatementBaseline. record.project_id equals project_id; audit action RESTATE_OPEN, at=record.opened_at; audit/period transition/baseline/receipt atomic. Its before snapshot must resolve authentic retained content or unlock fails.
- **RetainedImpactRecord**: project_id: ProjectId; audit_id: positive integer; record: ImpactReport; after_binding: SnapshotInputBinding (joined immutable binding, not a duplicate mutable column). All scope/period/snapshot/manifest values agree; audit action IMPACT_GENERATE, at=record.created_at; metadata/changes/audit/receipt atomic.
- **RetainedImpactChange**: project_id: ProjectId; impact_id: Id; ordinal: integer ≥0; record: ImpactChange. Full sequence is contiguous starting at zero, sorted unique (kind,key), linked to its report.
- **RetainedApprovalRecord**: project_id: ProjectId; audit_id: positive integer; record: ImpactApproval. All bindings agree with the owning report, currentness rechecked before publication; audit action IMPACT_APPROVE, at=record.at; record/audit/receipt atomic. Historical replay does not create a second row or revive currentness.

These JSON shapes verify record layout only. store/db.py owns revision counters/events and first invalidation markers plus input-driven T-04 stale flag updates; report_repo owns immutable binding/baseline/impact/change/approval rows; forecast_repo owns forecast bindings. All use the **caller's** connection/transaction. No repository-local commit. Complete manifest/view row storage, release codec identities, canonical finding-state serialization and project lifecycle/receipt control-plane schema remain open before WI-0001 sign-off; this table is not a claim of a complete storage design or applied SQL.

## 6. Tables required by docs 38–48 (normative — schema.sql is incomplete without these)
- **adjustments** (doc 39): adj_id TEXT PK · project_id · period_id · entity_id · account_id · cost_centre_id NULL · amount_minor INT · kind (`reclass|provision|closing|correction_view|other`) · label · reason TEXT NOT NULL · pair_group_id TEXT NULL · contra_account_id NULL · status (`draft|applied|reversed`) · reverses_adj_id NULL · source (`manual|system_closing|allocation`) · created_by/at · version. Rule runs record their layer; statement queries take layer as a parameter.
- **allocation_definitions**: def_id PK · project_id · name · method (`pct|driver|step_down`) · source_scope_json · driver_id NULL · step_order_json NULL · version · is_active. **allocation_receivers**: def_id FK · cost_centre_id · pct TEXT NULL (driver method computes shares). **allocation_runs**: run_id PK · def_id FK · period_id · status (`draft|applied`) · created_at (output = adjustments rows with source=`allocation`, label `ALLOC:<name>`).
- **assumptions** (doc 48): assumption_id PK · project_id · scope (`project|entity|account_group`) · scope_ref · key · value_decimal TEXT · unit · owner_id NULL · source_note · valid_from_period · version · status (`draft|approved`). Forecast runs store assumption versions in accuracy/snapshot JSON.
- **year_end_runs**: ye_id PK · project_id · fiscal_year INT · status (`checks|closing_proposed|confirmed`) · closing_batch_ref NULL · rollforward_check_json · created_at. (Closing journal itself is stored as adjustments kind=`closing` + a generated `opening` import batch, doc 38.)
- **connector_profiles** (doc 26 §8.3, DEC-013): connector_profile_id TEXT PK (`cpf_`+hash12) · project_id · kind (`d365fo|d365bc`) · version INT · profile_json TEXT (sources → entity, filter template, sort key, field→preset-header map, watermark field) · entity_check_json TEXT NULL (last entity-check result: checked_at, missing[]) · is_active INT 0/1 · created_at. One active row per project; a profile edit creates a new version (like `mapping_profiles`). Connection *settings* (host, tenant id, client id, company) live in `settings` under `connector.*` (doc 62); tokens and secrets live only in the OS keyring — **no column anywhere may hold them**.
- **connector_pulls** (doc 26 §8.4): pull_id TEXT PK (`pul_`+hash12) · project_id · period_id · kind (`d365fo|d365bc`) · company TEXT · sources_json TEXT (requested sources, e.g. `["gl","ap","tb"]`) · status (`running|snapshot_written|staged|no_change|failed`, doc 23 §11) · started_at · finished_at NULL · row_counts_json TEXT NULL (per source: expected count, received, pages, retries) · snapshot_sha256 TEXT(64) NULL · batch_ids_json TEXT NULL · error_code TEXT NULL (ERR-11x) · error_detail TEXT NULL (redacted; never a token or URL with a token) · actor_id. Index `(project_id, period_id, started_at)`; the latest `status IN ('staged','no_change')` row per period drives "last pulled on <date>" (S01) and the BC `lastModifiedDateTime` pre-check watermark (doc 26 §8.5).
Schema-equality test (doc 14) compares this doc's full table list (sections 2, 5, 6) against sqlite_master — any table here missing from schema.sql fails CI.

## 7. Schema-vs-dictionary status (normative until closed; owner: WORK_PLAN item for `app/store/schema.sql`)
`app/store/schema.sql` v1 (frozen at the build pause) implements §2/§5/§6 **except** the deltas below. Each delta is either applied to `schema.sql` (migration v2) or removed from this doc **before M1's gate closes**; the schema-equality test (doc 14 §4) then compares tables **and columns**, not table names only.

| # | Delta | Resolution |
|---|---|---|
| 1 | `import_batches` lacks `subledger_kind`, `declared_row_count`, `is_manual`; status CHECK lacks `validated` | add columns + CHECK in v2 |
| 2 | `gl_rows` lacks `posted_by`, `posted_at` (EXC-009 inputs) | add in v2 |
| 3 | `accounts.tags` closed list not CHECK-enforced | enforce in `master_repo` (SQLite CHECK on a CSV column is impractical) + test |
| 4 | `periods` FK from child tables is single-column `period_id` | keep (project scoping is enforced by `project_id` on every row); document, test cross-project isolation in `period_repo` |
| 5 | Few FKs/CHECKs overall (schema relies on repositories) | add `CHECK` on every enumerated status/kind column in v2; FKs for master references with `PRAGMA foreign_keys=ON` in `db.py` |
| 6 | `recon_runs` lacks `batch_id` | add in v2 |
| 7 | `created_by` absent on most tables | **dictionary corrected** (§1): actor lives in `audit_log` |
| 8 | `driver_values` carries `assumption_id`, `version` not previously documented | **dictionary corrected** (§2) |
| 9 | `audit_log.canonical`, `projects.currency_exponent`, `accounts.tags/ic_counterparty_entity_id`, `cost_centres.entity_id`, `vendors.linked_entity_id`, `gl_rows.fx_*/layer`, `finding_comments` | **dictionary corrected** (§2) — all now documented |
| 10 | `gl_rows` lacks `posting_layer`, `source_account_ref`, `vendor_source` (DEC-012: D365 shapes, vendor enrichment, verbatim write-back) | add in v2 |
| 11 | `findings` lacks `suggestion_json`, `suggestion_status`, `suggestion_ref` (DEC-011: rectification suggestions, doc 07 §7) | add in v2 (NOT NULL with default `{}`/`proposed` for the migration of any pre-existing rows) |
| 12 | `import_batches.source_kind` CHECK lacks `tb_check`; `subledger_kind` values must include `ap|ar|bank|payroll`; new nullable `enrichment_json` (vendor-enrichment counts, doc 06 §2 step 9) | add in v2 |
| 13 | `import_batches` lacks `source` (`file|connector`) and `pull_id`; tables `connector_profiles`, `connector_pulls` absent (DEC-013, doc 26 §8) | add in v2 (`source` NOT NULL DEFAULT `file` so existing rows migrate unchanged) |
| 14 | `projects.version`; `periods.version/created_at/updated_at` are required by §1 but missing from the frozen schema/explicit field lists | add in M1 schema migration; existing rows version 1 with migration-clock timestamps, preserve existing locked_at/lock_note (DEC-017) |

| 15 | `close_templates`, `close_period_configs`; close_tasks version/timestamps/statements_fingerprint/attestation_stale/locked_status and typed dependency/status constraints are absent (DEC-022) | add in M1 schema/migration; preserve legacy evidence, never infer fresh approval; full columns/FKs/JSON shapes checked against §5; task dates frozen by period calendar copy |

| 16 | Input revisions/events, snapshot/forecast input bindings and immutable baseline/impact/change/approval/invalidation tables in §5 (DEC-023) are absent | add in M1 schema/migration; exact columns, composite ownership/FKs, first-marker immutability and canonical typed payload equality; do not backfill legacy approval from current data |
