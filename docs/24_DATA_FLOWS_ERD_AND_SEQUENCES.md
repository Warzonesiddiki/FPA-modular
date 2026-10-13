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
