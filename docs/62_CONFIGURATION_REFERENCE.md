# 62 — CONFIGURATION REFERENCE (every setting, one table)

> Storage: project settings (doc 02 settings table) unless noted. All changes audited; UI impact text from the "Effect" column (S13).

| Key | Type/default | Effect |
|---|---|---|
| `general.currency_display_grouping` | en-IN/en-US, default en-IN | Display grouping only (27) |
| `general.scale_default` | units/thousands, default units | Default scale on S06/exports |
| `import.cutoff_window_days` | int, 5 | Posting-date tolerance around period (06) |
| `import.max_file_mb` / `max_rows` | 200 / 1,000,000 | ERR-021 caps (25 DoS) |
| `materiality.abs_minor` / `pct` | ₹100,000 / 5 | Doc 03 §5 + EXC-017/018/019 |
| `rule.EXC-###.*` | per doc 07 defaults (spike_abs ₹250,000, spike_pct 50, round_amount ₹10,000, approval_limit ₹500,000, one_off_abs ₹1,000,000, suspense_age_days 30, concentration_pct 40) | Rule thresholds; snapshot recorded per run |
| `forecast.allow_negative.<group>` | bool false | Doc 08 §7 floors |
| `forecast.backtest_window` | 3 periods | 08 §3 |
| `close.target_lock_business_day` | 5 | Doc 30 calendar + KPI |
| `recon.tolerance_minor` | ₹100 default | FR-REC sign-off guard |
| `alerts.retention_days` | 90 | FR-ALR purge |
| `ai.enabled` / `ai.provider` / `ai.model` | false / — / — | Doc 11; key only in keyring, never a setting value |
| `exports.include_drilldata` | true | DrillData sheet (09) — off reduces file size, stamped |
| `privacy.store_import_originals` | true | OQ-10; off = originals deleted post-commit (hashes retained) |
App-level (not per project): data-root default, log level, UI theme/density, last-opened project. Env overrides for dev only (`FPA_DEV_*`), ignored in release builds.
