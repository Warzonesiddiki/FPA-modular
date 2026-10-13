-- Schema v1 — implements docs/02_DATA_DICTIONARY.md sections 2, 5, 6. Money: INTEGER minor units.
CREATE TABLE IF NOT EXISTS schema_meta (version INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS projects (
  project_id TEXT PRIMARY KEY, name TEXT NOT NULL, base_currency TEXT NOT NULL DEFAULT 'INR',
  currency_exponent INTEGER NOT NULL DEFAULT 2, fy_start_month INTEGER NOT NULL DEFAULT 4,
  calendar_type TEXT NOT NULL DEFAULT 'monthly', is_sample INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS periods (
  period_id TEXT NOT NULL, project_id TEXT NOT NULL REFERENCES projects(project_id),
  fiscal_year INTEGER NOT NULL, period_no INTEGER NOT NULL, start_date TEXT NOT NULL, end_date TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'open', locked_at TEXT, lock_note TEXT, PRIMARY KEY (project_id, period_id));
CREATE TABLE IF NOT EXISTS entities (
  entity_id TEXT PRIMARY KEY, project_id TEXT NOT NULL, code TEXT NOT NULL, name TEXT NOT NULL,
  is_active INTEGER NOT NULL DEFAULT 1, version INTEGER NOT NULL DEFAULT 1, created_at TEXT, updated_at TEXT);
CREATE TABLE IF NOT EXISTS accounts (
  account_id TEXT PRIMARY KEY, project_id TEXT NOT NULL, code TEXT NOT NULL, name TEXT NOT NULL,
  account_type TEXT NOT NULL, statement_line TEXT, normal_side TEXT NOT NULL DEFAULT 'debit',
  tags TEXT NOT NULL DEFAULT '', ic_counterparty_entity_id TEXT, is_active INTEGER NOT NULL DEFAULT 1,
  version INTEGER NOT NULL DEFAULT 1, created_at TEXT, updated_at TEXT);
CREATE TABLE IF NOT EXISTS cost_centres (
  cost_centre_id TEXT PRIMARY KEY, project_id TEXT NOT NULL, code TEXT NOT NULL, name TEXT NOT NULL,
  entity_id TEXT, is_active INTEGER NOT NULL DEFAULT 1, version INTEGER NOT NULL DEFAULT 1, created_at TEXT, updated_at TEXT);
CREATE TABLE IF NOT EXISTS vendors (
  vendor_id TEXT PRIMARY KEY, project_id TEXT NOT NULL, code TEXT NOT NULL, name TEXT NOT NULL,
  linked_entity_id TEXT, is_active INTEGER NOT NULL DEFAULT 1, version INTEGER NOT NULL DEFAULT 1, created_at TEXT, updated_at TEXT);
CREATE TABLE IF NOT EXISTS owners (
  owner_id TEXT PRIMARY KEY, project_id TEXT NOT NULL, display_name TEXT NOT NULL, email TEXT, role_label TEXT,
  is_active INTEGER NOT NULL DEFAULT 1, version INTEGER NOT NULL DEFAULT 1, created_at TEXT, updated_at TEXT);
CREATE TABLE IF NOT EXISTS account_owners (
  account_id TEXT NOT NULL, owner_id TEXT NOT NULL, valid_from TEXT, PRIMARY KEY (account_id, owner_id));
CREATE TABLE IF NOT EXISTS mapping_profiles (
  profile_id TEXT PRIMARY KEY, project_id TEXT NOT NULL, source_kind TEXT NOT NULL, name TEXT NOT NULL,
  version INTEGER NOT NULL DEFAULT 1, is_default INTEGER NOT NULL DEFAULT 0, created_at TEXT);
CREATE TABLE IF NOT EXISTS mapping_rules (
  profile_id TEXT NOT NULL, source_column TEXT NOT NULL, canonical_field TEXT NOT NULL,
  transform TEXT NOT NULL DEFAULT 'none', constant_value TEXT, PRIMARY KEY (profile_id, canonical_field));
CREATE TABLE IF NOT EXISTS import_batches (
  batch_id TEXT PRIMARY KEY, project_id TEXT NOT NULL, period_id TEXT, source_kind TEXT NOT NULL,
  file_name TEXT, file_sha256 TEXT NOT NULL, file_size INTEGER, mapping_profile_id TEXT,
  status TEXT NOT NULL DEFAULT 'staged', row_count_in INTEGER DEFAULT 0, row_count_valid INTEGER DEFAULT 0,
  row_count_quarantined INTEGER DEFAULT 0, control_debit_minor INTEGER, control_credit_minor INTEGER,
  declared_debit_minor INTEGER, declared_credit_minor INTEGER, committed_at TEXT, supersedes_batch_id TEXT);
CREATE TABLE IF NOT EXISTS import_rows_raw (
  raw_id TEXT PRIMARY KEY, batch_id TEXT NOT NULL, sheet_name TEXT, row_no INTEGER NOT NULL,
  raw_json TEXT NOT NULL, parse_status TEXT NOT NULL DEFAULT 'ok', quarantine_reason TEXT);
CREATE TABLE IF NOT EXISTS gl_rows (
  gl_row_id TEXT PRIMARY KEY, project_id TEXT NOT NULL, period_id TEXT NOT NULL, batch_id TEXT NOT NULL,
  entity_id TEXT, account_id TEXT, cost_centre_id TEXT, vendor_id TEXT, voucher_no TEXT,
  document_date TEXT, posting_date TEXT, description TEXT, amount_minor INTEGER NOT NULL,
  quantity_decimal TEXT, fx_currency TEXT, fx_amount_minor INTEGER, fx_rate TEXT,
  layer TEXT NOT NULL DEFAULT 'gl', source_file TEXT, source_row INTEGER);
CREATE INDEX IF NOT EXISTS ix_gl_period_account ON gl_rows(period_id, account_id);
CREATE INDEX IF NOT EXISTS ix_gl_voucher ON gl_rows(voucher_no);
CREATE INDEX IF NOT EXISTS ix_gl_batch ON gl_rows(batch_id);
CREATE TABLE IF NOT EXISTS budget_versions (
  version_id TEXT PRIMARY KEY, project_id TEXT NOT NULL, label TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'draft', created_at TEXT);
CREATE TABLE IF NOT EXISTS budget_lines (
  line_id TEXT PRIMARY KEY, version_id TEXT NOT NULL, period_id TEXT NOT NULL, entity_id TEXT,
  account_id TEXT, cost_centre_id TEXT, amount_minor INTEGER NOT NULL);
CREATE UNIQUE INDEX IF NOT EXISTS ux_budget_grain ON budget_lines(version_id, period_id, entity_id, account_id, IFNULL(cost_centre_id,''));
CREATE TABLE IF NOT EXISTS driver_values (
  driver_row_id TEXT PRIMARY KEY, project_id TEXT NOT NULL, driver_id TEXT NOT NULL, period_id TEXT NOT NULL,
  entity_id TEXT, account_id TEXT, value_decimal TEXT NOT NULL, source TEXT NOT NULL DEFAULT 'manual',
  scenario_id TEXT, assumption_id TEXT, version INTEGER NOT NULL DEFAULT 1);
CREATE TABLE IF NOT EXISTS forecast_runs (
  run_id TEXT PRIMARY KEY, project_id TEXT NOT NULL, base_period_id TEXT, method_map_json TEXT,
  status TEXT NOT NULL DEFAULT 'draft', accuracy_json TEXT, created_at TEXT);
CREATE TABLE IF NOT EXISTS forecast_lines (
  run_id TEXT NOT NULL, period_id TEXT NOT NULL, entity_id TEXT, account_id TEXT, cost_centre_id TEXT,
  amount_minor INTEGER NOT NULL, method TEXT, PRIMARY KEY (run_id, period_id, entity_id, account_id, cost_centre_id));
CREATE TABLE IF NOT EXISTS scenarios (
  scenario_id TEXT PRIMARY KEY, project_id TEXT NOT NULL, name TEXT NOT NULL, base_run_id TEXT,
  delta_json TEXT, status TEXT NOT NULL DEFAULT 'draft');
CREATE TABLE IF NOT EXISTS findings (
  finding_id TEXT PRIMARY KEY, finding_key TEXT NOT NULL UNIQUE, rule_id TEXT NOT NULL, project_id TEXT NOT NULL,
  period_id TEXT, entity_id TEXT, account_id TEXT, severity TEXT NOT NULL, amount_minor INTEGER DEFAULT 0,
  evidence_json TEXT, status TEXT NOT NULL DEFAULT 'new', owner_id TEXT, due_date TEXT,
  waive_reason TEXT, waive_expires TEXT, first_seen_run TEXT, last_seen_run TEXT);
CREATE INDEX IF NOT EXISTS ix_findings_project_status ON findings(project_id, status, severity);
CREATE TABLE IF NOT EXISTS finding_comments (
  comment_id INTEGER PRIMARY KEY AUTOINCREMENT, finding_id TEXT NOT NULL, at TEXT, actor TEXT, note TEXT);
CREATE TABLE IF NOT EXISTS finding_history (
  history_id INTEGER PRIMARY KEY AUTOINCREMENT, finding_id TEXT NOT NULL, at TEXT, actor TEXT, action TEXT,
  from_status TEXT, to_status TEXT, note TEXT);
CREATE TABLE IF NOT EXISTS commentary (
  commentary_id TEXT PRIMARY KEY, project_id TEXT NOT NULL, period_id TEXT, scope TEXT NOT NULL, text TEXT,
  source_refs_json TEXT, ai_assisted INTEGER NOT NULL DEFAULT 0, prompt_version TEXT,
  version INTEGER NOT NULL DEFAULT 1, status TEXT NOT NULL DEFAULT 'draft');
CREATE TABLE IF NOT EXISTS reports (
  report_id TEXT PRIMARY KEY, project_id TEXT NOT NULL, period_id TEXT, kind TEXT NOT NULL, path TEXT,
  sha256 TEXT, snapshot_json TEXT, created_at TEXT);
CREATE TABLE IF NOT EXISTS settings (
  project_id TEXT NOT NULL, key TEXT NOT NULL, value_json TEXT, version INTEGER NOT NULL DEFAULT 1,
  PRIMARY KEY (project_id, key));
CREATE TABLE IF NOT EXISTS audit_log (
  audit_id INTEGER PRIMARY KEY AUTOINCREMENT, project_id TEXT, at TEXT, actor TEXT, entity_type TEXT,
  entity_id TEXT, action TEXT, before_json TEXT, after_json TEXT, canonical TEXT, prev_hash TEXT, hash TEXT);
-- doc 02 section 5/6 expansion
CREATE TABLE IF NOT EXISTS close_tasks (
  task_id TEXT PRIMARY KEY, project_id TEXT NOT NULL, period_id TEXT, template_key TEXT, title TEXT,
  owner_id TEXT, due_offset_days INTEGER, depends_on TEXT, kind TEXT, status TEXT NOT NULL DEFAULT 'not_started',
  completed_by TEXT, completed_at TEXT, note TEXT);
CREATE TABLE IF NOT EXISTS close_signoffs (
  signoff_id TEXT PRIMARY KEY, project_id TEXT NOT NULL, period_id TEXT, signer TEXT, attestation_text TEXT,
  snapshot_json TEXT, at TEXT);
CREATE TABLE IF NOT EXISTS headcount_plans (
  plan_id TEXT PRIMARY KEY, project_id TEXT NOT NULL, period_id TEXT, cost_centre_id TEXT, opening_hc INTEGER,
  joiners INTEGER DEFAULT 0, leavers INTEGER DEFAULT 0, avg_cost_minor INTEGER, increment_pct TEXT, bonus_pct TEXT);
CREATE TABLE IF NOT EXISTS capex_assets (
  asset_id TEXT PRIMARY KEY, project_id TEXT NOT NULL, class_label TEXT, cost_minor INTEGER, addition_period TEXT,
  useful_life_months INTEGER, method TEXT DEFAULT 'slm', residual_pct TEXT, disposal_period TEXT, proceeds_minor INTEGER);
CREATE TABLE IF NOT EXISTS debt_schedules (
  facility_id TEXT PRIMARY KEY, project_id TEXT NOT NULL, label TEXT, opening_minor INTEGER, rate_pct TEXT, kind TEXT DEFAULT 'fixed');
CREATE TABLE IF NOT EXISTS debt_movements (
  facility_id TEXT NOT NULL, period_id TEXT, kind TEXT, amount_minor INTEGER, PRIMARY KEY (facility_id, period_id, kind));
CREATE TABLE IF NOT EXISTS wc_assumptions (
  project_id TEXT NOT NULL, entity_id TEXT NOT NULL, dso_days TEXT, dpo_days TEXT, dio_days TEXT,
  effective_period TEXT, PRIMARY KEY (project_id, entity_id, effective_period));
CREATE TABLE IF NOT EXISTS cash13_inputs (
  input_id TEXT PRIMARY KEY, project_id TEXT NOT NULL, week_start TEXT, kind TEXT, amount_minor INTEGER,
  party_label TEXT, source_ref TEXT);
CREATE TABLE IF NOT EXISTS recon_runs (
  recon_id TEXT PRIMARY KEY, project_id TEXT NOT NULL, period_id TEXT, kind TEXT, tolerance_minor INTEGER,
  status TEXT NOT NULL DEFAULT 'open', signed_by TEXT, signed_at TEXT);
CREATE TABLE IF NOT EXISTS recon_matches (
  recon_id TEXT NOT NULL, side TEXT NOT NULL, ref_id TEXT, amount_minor INTEGER, matched_group TEXT, score TEXT);
CREATE TABLE IF NOT EXISTS alerts (
  alert_id TEXT PRIMARY KEY, project_id TEXT NOT NULL, alert_key TEXT, period_id TEXT, kind TEXT, severity TEXT,
  message TEXT, status TEXT NOT NULL DEFAULT 'active', seen_count INTEGER DEFAULT 1, created_at TEXT, last_seen TEXT);
CREATE TABLE IF NOT EXISTS report_definitions (
  def_id TEXT PRIMARY KEY, project_id TEXT NOT NULL, name TEXT, blocks_json TEXT, version INTEGER DEFAULT 1, created_by TEXT);
CREATE TABLE IF NOT EXISTS adjustments (
  adj_id TEXT PRIMARY KEY, project_id TEXT NOT NULL, period_id TEXT, entity_id TEXT, account_id TEXT,
  cost_centre_id TEXT, amount_minor INTEGER NOT NULL, kind TEXT NOT NULL, label TEXT, reason TEXT NOT NULL,
  pair_group_id TEXT, contra_account_id TEXT, status TEXT NOT NULL DEFAULT 'draft', reverses_adj_id TEXT,
  source TEXT NOT NULL DEFAULT 'manual', created_by TEXT, created_at TEXT, version INTEGER NOT NULL DEFAULT 1);
CREATE TABLE IF NOT EXISTS allocation_definitions (
  def_id TEXT PRIMARY KEY, project_id TEXT NOT NULL, name TEXT, method TEXT, source_scope_json TEXT,
  driver_id TEXT, step_order_json TEXT, version INTEGER DEFAULT 1, is_active INTEGER DEFAULT 1);
CREATE TABLE IF NOT EXISTS allocation_receivers (
  def_id TEXT NOT NULL, cost_centre_id TEXT NOT NULL, pct TEXT, PRIMARY KEY (def_id, cost_centre_id));
CREATE TABLE IF NOT EXISTS allocation_runs (
  run_id TEXT PRIMARY KEY, def_id TEXT NOT NULL, period_id TEXT, status TEXT NOT NULL DEFAULT 'draft', created_at TEXT);
CREATE TABLE IF NOT EXISTS assumptions (
  assumption_id TEXT PRIMARY KEY, project_id TEXT NOT NULL, scope TEXT, scope_ref TEXT, key TEXT NOT NULL,
  value_decimal TEXT, unit TEXT, owner_id TEXT, source_note TEXT, valid_from_period TEXT,
  version INTEGER DEFAULT 1, status TEXT NOT NULL DEFAULT 'draft');
CREATE TABLE IF NOT EXISTS year_end_runs (
  ye_id TEXT PRIMARY KEY, project_id TEXT NOT NULL, fiscal_year INTEGER, status TEXT NOT NULL DEFAULT 'checks',
  closing_batch_ref TEXT, rollforward_check_json TEXT, created_at TEXT);
