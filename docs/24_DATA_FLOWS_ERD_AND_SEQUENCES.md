# 24 — DATA FLOWS, ERD & KEY SEQUENCES

## 1. ERD (implements doc 02; cardinalities)
```
projects 1─* periods
projects 1─* entities/accounts/cost_centres/vendors/owners
accounts *─* owners (account_owners)
projects 1─* mapping_profiles 1─* mapping_rules
projects 1─* import_batches 1─* import_rows_raw
import_batches 1─* gl_rows *─1 periods/entities/accounts
budget_versions 1─* budget_lines
forecast_runs 1─* forecast_lines ; scenarios *─1 forecast_runs(base)
findings *─1 owners ; findings 1─* finding_comments/history
commentary *─1 periods ; reports *─1 periods (snapshot_json → batch/budget/forecast ids)
planning tables (29 §9): drivers, headcount, capex_assets, debt_schedules, wc_assumptions, cash13
close_tasks *─1 periods ; recon_runs 1─* recon_matches ; alerts
settings/audit_log *─1 projects
```

## 2. Data flows (trust boundaries marked)
[ERP exports — UNTRUSTED] or [Dynamics 365 tenant — EXTERNAL, read-only, user-click only, allow-listed TLS; `app/connectors` writes a snapshot workbook = UNTRUSTED file] → staging (raw preserved) → validated staging → gl_rows (trusted core) → calc snapshots → {UI, Excel, PPT, PDF} ; gl_rows → rules → findings → owners ; actuals+drivers → forecast → scenarios ; aggregates only → [AI provider — EXTERNAL, optional] → guardrails → commentary drafts. No other outbound flow exists (doc 12 test enforces); the connector's two edges are `login.microsoftonline.com` (tokens, kept in the OS keyring) and the configured Dynamics host (reads only — no write flow exists in the code).

## 3. Key sequences
**Import commit:** UI POST file → stage+hash → profile/suggest → analyst confirms mapping → validate (quarantine report) → control totals OK → POST commit (job) → single TXN insert → TB check → batch committed → dashboard stage updates. Failure at any step leaves prior committed data untouched.
**Dynamics 365 pull (DEC-013):** UI POST /connector/pull → job: silent token (keyring) → entity check → `$count` → paged GET (retry/backoff) → count consistency → snapshot workbook to temp → rename into `imports/<sha>.xlsx` → content hash already batched? → `no_change` | stage (source=connector, pull_id) → preset auto-applies → validate → **analyst commits** (same sequence as *Import commit* from "validate" onward) → enrichment / tb_check → `connector_pulls` row + audit. Any failure before rename leaves no file and no batch.
**Rule run:** POST run → engine reads gl/budget snapshot → 28 pure rules → dedupe by finding_key (existing findings updated last_seen, new inserted, vanished-not-refired flagged for verify) → owners resolved → alerts raised → report (per-rule counts incl. not_run reasons).
**Board pack:** POST exports → snapshot frozen (batch watermark, budget version, forecast run) → checks (doc 09 §4 + integrated-forecast balance) → Excel always; PPT/PDF only if checks pass → reports row + hashes → downloads.
**Month 2 (the rhythm that must be effortless):** open project → period auto-advanced → *Refresh this month* from Dynamics 365 (or drop files) → saved mapping / preset auto-applies → commit → prior thresholds/owners/methods in force → rolling forecast draft auto-generated → analyst reviews deltas only.

## 4. Snapshot & reproducibility
Every report/commentary/forecast stores the ids+hashes of its inputs; "regenerate" on the same snapshot must produce numerically identical output (file bytes may differ only in timestamps, which are listed in the Checks/Sources stamp — acceptance stability bar applies to findings and numbers, doc 14).

DEC-020 close review: snapshot_id resolves the immutable financial input manifest, including used batch hashes, mapping/master versions, selected budget/forecast/layers/adjustments, settings affecting the output, findings and approved commentary. A batch watermark alone cannot prove the pack current after a mapping or commentary change. Close-task completion and CLOSE_SIGNOFF/PERIOD_LOCK events are not financial input changes requiring pack regeneration; their concurrency is instead fenced by the project audit head and doc-05 review token. Sign-off never hashes its own resulting audit hash into its input. The snapshot manifest must retain enough provenance to reproduce the report and the reviewed blocker identities without embedding unbounded IDs in the public readiness DTO.

DEC-021 impact generation/approval audit events also do not change financial inputs. Doc 05 §9 binds baseline/current snapshot manifests and immutable paged changes; doc 41 §6 defines comparison identities and permanent invalidation after input changes. Historical impact/approval reads never authorise current close. Full manifest/persistence schemas remain WI-0001 work before M1.

DEC-022: T-04 binds the statement-input subset of the financial manifest (doc 30 §8), not forecast/commentary/pack audit events; statement-input mutations atomically mark its attestation stale. A CloseTaskReview concurrency token includes the current audit head, but stored T-04 evidence does not. Period calendar/template copies and lock task projections are frozen by explicit commands (doc 02 §5); GET only projects. Full canonical statement-manifest/invalidation integration is still required before WI-0001 sign-off.


## 5. Durable input revisions and publication fences (DEC-023)
This specifies the **revision/invalidation** part of the retention contract, not the still-open complete manifest/view encoding. A batch watermark is not a version of mappings, opening balances, adjustments or settings. Every project has InputRevisions, initial statement_revision=forecast_revision=pack_revision=1. All are positive SQLite signed 64-bit integers (maximum 9223372036854775807); overflow aborts the entire command with ERR-099, never wraps or resets. Revisions are metadata, not money. They are separate from editable project/period/task versions and audit_id. Server-trusted mutators declare a union of effects; clients cannot set counters or effects.

The closed effect classes are statement_inputs, forecast_inputs, pack_inputs. Canonical order is that order. statement_inputs implies both other effects; forecast_inputs implies pack_inputs. Normalise the union once per committed command, then increment each selected counter **exactly once**, not once per row, entity, period or nested repository call. An input-affecting command in another period conservatively invalidates current project-wide bindings; immutable locked history is still readable. False-positive refresh work is preferred to stale approvals in v1. Reverting values is another increment (ABA never resurrects old evidence). A durable replay, rejected/rolled-back request, cancelled unpublished job or GET does not advance a counter. Successfully published financial changes and later cancellation cannot be combined into a false cancelled/no-effect outcome (doc 64).

| Mutation category | Normalised effects | Scope / exclusions |
|---|---|---|
| committed_source | statement_inputs, forecast_inputs, pack_inputs | Commit/supersede GL or opening data, source enrichment changing retained GL provenance; not staging or quarantine previews. |
| adjustment_change | statement_inputs, forecast_inputs, pack_inputs | Apply/reverse/change an included adjustment or year-end/opening state; financial effect, not merely a proposal preview. |
| statement_mapping | statement_inputs, forecast_inputs, pack_inputs | Account/entity/cost-centre mappings, master or presentation versions used by statements, including changes to prior-period inputs. |
| statement_settings | statement_inputs, forecast_inputs, pack_inputs | Calculation settings affecting statement values/classification (calc.*); selectors/registry versions used for calculation. |
| forecast_assumptions | forecast_inputs, pack_inputs | Budgets, drivers, planning inputs, assumption versions, forecast method/parameters and manual forecast inputs; include drafts conservatively when persisted. |
| forecast_publication | pack_inputs | A new forecast run/result, its lock/selection or scenario output. Does NOT advance forecast_revision: the run cannot stale itself. |
| finding_change | pack_inputs | Finding state/evidence/owner/waiver/correction/suggestion changes, comments, and completion of a rules run including explicit not_run coverage. |
| commentary_change | pack_inputs | Persisted draft or approved commentary and sources. Forecast/statement inputs are unaffected. |
| pack_configuration | pack_inputs | Report definitions, display settings/general.*, report labels, owner labels and rule thresholds; rule freshness still independently checked. |
| project_display | pack_inputs | Project display metadata used in packs; not immutable currency/calendar identity changes. |
| pack_publication | none | Materialise retained snapshots and checked render outputs only; no source/finding mutation hidden here. |
| impact_publication | none | Immutable impact metadata/changes or approval; no source edits or automatic forecasting. |
| close_metadata | none | Task/template/attestation/sign-off/lock/unlock audit; unlock separately revokes T-04 for that period and advances period.version. |
| staging_only | none | Upload/stage/validate/discard without committing financial input. |
| job_control | none | Queuing/progress/cancel acknowledgement; no completed financial result publication. |
| read_only | none | All GETs, including freshness/expiry projection; no hidden repair or revision row writes. |

This is an **effect** register, not a URL whitelist. A compound command takes the union: a journal export that changes suggestion/finding state is finding_change, not just pack_publication; allocation output creating adjustments includes adjustment_change; connector auto-commit is a separate committed_source (or forecast_assumptions for budget) command. A command spanning several rows/periods increments once. Unknown categories fail closed before any write (internal ERR-099); a new input-affecting feature must extend this owner table and its tests before implementation. None of AI/connector credentials, tokens or launch state belongs in a snapshot or this register.

### 5.1 Single transaction and owners
store/db.py owns the caller-held project write transaction and the mechanical input revision advance/invalidation primitive. Trusted repository/engine mutators declare categories from §5; the primitive performs no financial classification/calculation. Store repositories never commit independently or swallow rollback. In the SAME SQLite transaction: domain writes → one owning audit event → normalised counter advance + input_revision_events row referencing that audit → mark T-04 attestations stale when statement_inputs changed → append the first invalidation for every previously uninvalidated impact with an older pack revision → command receipt/publication. If any step fails, ALL steps roll back. No after-commit invalidation, background fixup or GET repair is acceptable. The close service clears T-04's stale flag only after a fresh guarded attestation; an input mutation can only set it. Locked_status retains the original locked projection; changing a currentness flag never rewrites historical DTOs.

store/report_repo.py owns immutable snapshot bindings and restatement baseline/impact/change/approval storage and reads. store/forecast_repo.py owns forecast input bindings. store/period_repo.py owns task/period records. services/close_service.py coordinates unlock/impact generation/approval with these repositories and the DB boundary. These are assignments to existing planned modules, not implementations. The separate missing project creation/deletion/backup/restore/installation receipt coordinator is NOT assigned to close_service by implication and remains a WI-0001 gap.

### 5.2 Captured bindings and currentness
SnapshotInputBinding is stored only when a retained snapshot and its complete content have been published: project_id, snapshot_id, period_id, revisions: InputRevisions, manifest_sha256, statements_fingerprint. The revisions.project_id equals project_id. All three counters capture the same read transaction that supplied the snapshot. A binding alone is not the snapshot: storage must also retain and verify the manifest, referenced row versions, computed views and drill provenance; those encodings are the next open part of WI-0001. No empty object/current-data fallback can stand in for missing historical content.

ForecastInputBinding contains project_id, run_id and captured forecast_revision. While computing outside the write boundary, hold frozen input references; at publication recheck forecast_revision and all original domain guards under the write transaction, then publish the run and its binding together. Increment pack_revision for forecast_publication only; the new run remains current against the unchanged forecast_revision. A source or assumption mutation during computation rejects publication (ERR-003 with the captured/current forecast revisions), not a partially successful stale run. Run generation must never observe its own output as an input.

For pack/impact publication, compare captured pack_revision with the current counter before any publication; mismatch → ERR-003 with these revisions. For T-04, compare captured statement_revision AND current statement manifest/fingerprint; downstream forecast/commentary/pack/impact/close events do not advance statement_revision. Bindings, layer/scope, full manifests, checked outputs and time-dependent guards remain conjunctive requirements: equality of revision numbers alone is **not** current approval. Expired waivers are still evaluated at the injected real instant per docs 05/30; reads do not increment revisions on expiry. Rollback/restore can replace project counters, so these counters are **not** a substitute for an external restore generation/epoch; backup/restore fencing remains explicitly open.

Current impact requires its after-snapshot binding to match current pack_revision, no impact_invalidations row, same cycle/period revision and the existing doc-41 manifest/pack/approval guards. Every approval is linked to exactly that immutable impact; the approval itself never overwrites approved=true on a mutable report. Prefer the latest qualifying audit event as already specified, not wall-clock order. An invalidation marker is permanent and points to the first invalidating command; subsequent mutations do not rewrite it. An old approval remains readable after invalidation but can never authorise sign-off or re-lock.

The ERR-003 detail object remains exactly `{expected_version,actual_version}`: expected_version is the captured relevant counter and actual_version is its value re-read under the publication transaction. Forecast uses forecast_revision; pack/impact use pack_revision. Do not invent captured_revision/current_revision wire fields. No mutation survives a failed recheck. For a synchronous route this is HTTP 409; an already accepted job records the same error in its failed envelope.

The attachment's internal `x-revision-effects` maps the §5 category names to their normalised arrays (none = []); `x-revision-storage` maps the nine doc-02 table names to exact ordered `columns` and single `owner` module paths. `x-revision-policy.required_revision_facts` records these conjuncts for document model checks: same_project, same_pack_revision, no_invalidation, content_verified, current_cycle, current_period_version, current_checked_pack, time_guards. They are server-derived facts, NOT booleans accepted from callers and NOT replacements for doc 41's full currentness/approval guards. Document models only interpret supplied synthetic facts; runtime must derive and verify them from retained content and current state.

### 5.3 Cache keys and migration
Statement memoisation must include project_id, period_id, layer, statement_revision and calculation/presentation selector identity; within a revision it must still use the exact statement manifest/registry version. Watermark-only caching is prohibited. A cache hit is never evidence of freshness; guards compare the current revision first. Budget/forecast/finding/commentary changes do not invalidate statement-only cached numbers, but do invalidate relevant forecast/pack bindings. Different projects sharing a period id cannot share a cache entry.

Migration creates initial counters at 1 but does **not** backfill historical snapshot/forecast/approval bindings from today's state. Legacy objects with missing bindings remain historical/stale; regenerate current forecasts/packs and explicitly re-attest/re-approve. Mark unbound legacy T-04 attestations stale while preserving their original fields/audit. Missing authentic historical baselines/calendars still need a specific repair contract; do not infer them from current configuration. Migration is not an input event approving old data.

Hand-worked counter oracle, one project: initial (1,1,1); committed source → (2,2,2); forecast assumptions → (2,3,3); forecast result published against f=3 → (2,3,4), that run remains current; approved commentary → (2,3,5); pack + impact + approval + sign-off + lock → unchanged (2,3,5). Source correction and then reversal → (4,5,7), never back to (2,3,5). A failed correction or same-key replay leaves the starting triple exactly unchanged. A multi-entity command with source plus finding effects still advances only one step to (3,4,6).
