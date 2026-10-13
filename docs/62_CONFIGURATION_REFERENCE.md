# 62 — CONFIGURATION REFERENCE (every setting, one table)

> Storage: project settings (doc 02 settings table) unless noted. All changes audited; UI impact text from the "Effect" column (S13).

| Key | Type/default | Effect |
|---|---|---|
| `general.currency_display_grouping` | en-IN/en-US, default en-IN | Display grouping only (27) |
| `general.scale_default` | units/thousands, default units | Default scale on S06/exports |
| `import.cutoff_window_days` | int, 5 | Posting-date tolerance around period (06) |
| `import.max_file_mb` / `max_rows` | 200 / 1,000,000 | ERR-021 caps (25 DoS) |
| `import.require_known_vendor` | bool false | off → unmapped vendor codes stored as text labels; on → `UNKNOWN_VENDOR` quarantine (06 §4; OQ-14 accepted) |
| `import.posting_layers` | list, `["Current"]` | ERP posting layers accepted into the ledger; others → `OUT_OF_SCOPE_LAYER` (06 §2.5, FR-IMP-018) |
| `import.auto_vendor_enrichment` | bool true | run AP→GL vendor enrichment after either batch commits (06 §2.9) |
| `import.ledger_account_segments` (per profile, not project) | list, e.g. `[main_account, business_unit, cost_centre, department]` | declared once per D365 F&O profile for `split:` transforms (26 §5) |
| `materiality.abs_minor` / `pct` | ₹100,000 / 5 | Doc 03 §5 + EXC-017/018/019 |
| `rule.EXC-###.*` | per doc 07 defaults (spike_abs ₹250,000, spike_pct 50, round_amount ₹10,000, approval_limit ₹500,000, one_off_abs ₹1,000,000, suspense_age_days 30, concentration_pct 40) | Rule thresholds; snapshot recorded per run |
| `rule.manual_prefixes` | list, `["JV","MJ"]` | voucher prefixes treated as manual journals in addition to `is_manual` batches (44 §0) |
| `rule.EXC-025.min_abs` / `dominance_pct` / `min_signal_tokens` / `min_token_count` / `stopwords` | ₹25,000 / 90 / 2 / 12 / list (44 §0) | Account–narration mismatch |
| `rule.EXC-026.min_abs` / `outlier_factor` / `shift_tolerance_pct` / `min_history_count` | ₹25,000 / 5 / 2 / 6 | Amount outlier / decimal shift |
| `rule.EXC-027.min_abs` / `dominant_share_pct` / `min_history_rows` | ₹25,000 / 90 / 10 | Unusual cost centre |
| `rule.EXC-028.min_abs` / `window_days` | ₹25,000 / 30 | Near-duplicate vendor charge |
| `rule.suggestions.auto_verify` | bool false | when on, a full verification match moves `corrected → verified` without a click (07 §7.4) |
| `calc.cf_interest_section` | `operating` \| `financing`, default `operating` | CF classification of interest paid (03; OQ-13 accepted) |
| `erp.journal_format` | `d365fo_general_journal` \| `d365bc_general_journal` \| `generic_csv`, default `generic_csv` (the D365 presets set it on first use) | rectification journal write-back shape (26 §7) |
| `erp.d365fo.ledger_account_format` | `{main_account}-{entity}-{cost_centre}` | how `ACCOUNTDISPLAYVALUE` is composed when no `source_account_ref` exists (26 §7) |
| `forecast.allow_negative.<group>` | bool false | Doc 08 §7 floors |
| `forecast.backtest_window` | 3 periods | 08 §3 |
| `close.target_lock_business_day` | 5 | Doc 30 calendar + KPI |
| `recon.tolerance_minor` | ₹100 default | FR-REC sign-off guard |
| `alerts.retention_days` | 90 | FR-ALR purge |
| `ai.enabled` / `ai.provider` / `ai.model` | false / — / — | Doc 11; key only in keyring, never a setting value |
| `connector.enabled` | bool false | Dynamics 365 connector on/off for the project (26 §8, DEC-013); off ⇒ zero network, file route only (FR-CON-009) |
| `connector.kind` | `none` / `d365fo` / `d365bc`, default `none` | selects the transport (OData v4 vs BC API v2.0) and the default profile |
| `connector.base_url` | string, https only | F&O environment URL or BC `https://api.businesscentral.dynamics.com/v2.0/<tenant>/<environment>`; host must match the allow-list shape (ERR-113; a customer-named host needs the explicit S13 acceptance) |
| `connector.tenant_id` / `connector.client_id` | GUIDs | Entra ID directory and app registration (26 §8.9) |
| `connector.auth_mode` | `delegated` / `client_credentials`, default `delegated` | sign-in in the browser vs service identity; the client secret/certificate is **never** a setting (keyring only, ERR-105 if a secret-shaped value is PUT here) |
| `connector.company` | string | F&O `dataAreaId` or BC company id/name; validated against `/connector/companies` (ERR-117) |
| `connector.sources_default` | list, `["gl","ap","tb"]` | pre-ticked sources on S03 step 0 / Refresh |
| `connector.page_size` | int 10,000 (BC max 20,000) | `$top` per page; lower it on throttled tenants |
| `connector.timeout_s` | int 60 | per-request timeout (connect 10 s); then retry policy below |
| `connector.retry_max_attempts` / `connector.retry_base_s` | 5 / 1 | backoff 1-2-4-8-16 s honouring `Retry-After`; exhausted ⇒ ERR-115 |
| `connector.pull_on_open` | bool false | when opening the project: BC pre-check / F&O full pull as a visible, cancellable job (never silent) |
| `connector.auto_commit_when_clean` | bool false | commit a pulled batch automatically only when zero rows are quarantined, control totals / TB tie-out pass and the TB gate is green; otherwise it stops at Validate like a file |
| `connector.allow_demo_host` | bool, true only on the sample project | lets the allow-list accept `127.0.0.1` for `tools/mock_d365.py`; cannot be turned on for other projects through the UI |
| `exports.include_drilldata` | true | DrillData sheet (09) — off reduces file size, stamped |
| `privacy.store_import_originals` | true | OQ-10; off = originals deleted post-commit (hashes retained) |
App-level (not per project): data-root default, log level, UI theme/density, last-opened project. Env overrides for dev only (`FPA_DEV_*`), ignored in release builds.
