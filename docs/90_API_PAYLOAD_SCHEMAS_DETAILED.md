# 90 — API PAYLOAD SCHEMAS, FIELD-LEVEL (normative companion to docs 05 + 63)

> Every field: name, type, required, constraints, example. Money = decimal string (major units), dates ISO, ids per doc 02. Unknown fields in requests are rejected (400 → FP&A-ERR-001 shape with details.unknown_fields) — silent ignoring hides UI bugs.

## Common
`Page<T>{items: T[], next_cursor: string|null}` · `Job{job_id, status, progress_pct: number|null, stage: string, error: ErrorBody|null, result?: object}` · `ErrorBody{code,message,hint,retryable,details}` (doc 22).

## Projects
`ProjectCreate{name: string 1..80, base_currency: ISO4217, fy_start_month: 1..12, calendar_type: "monthly"}` → `Project{project_id, name, base_currency, currency_exponent (derived, doc 27), fy_start_month, calendar_type, is_sample, periods: Period[]}` · `Period{period_id, fiscal_year, period_no, start_date, end_date, status}`.

## Imports
`Batch{batch_id, source_kind, period_id, file_name, file_sha256, status, row_count_in/valid/quarantined, control: {declared_debit?: string, declared_credit?: string, actual_debit: string, actual_credit: string}|null, mapping_profile_id, committed_at?}` · `QuarantineRow{row_no, sheet, reason (doc 06 §4 enum), raw: object}` · `MappingProfile{profile_id, name, version, is_default, rules: {source_column, canonical_field, transform, constant_value?}[]}` · `SuggestResponse{suggestions: {source_column, canonical_field, confidence: 0..1, basis: string}[]}`.

## Statements / BvA / drill
`Statement{statement: "pl|bs|cf", period_id, layer: "gl|gl_adj", lines: StatementLine[], checks: {tb: "balanced|imbalanced|waived"}}` · `StatementLine{line_key, label, amount: string, amount_minor: int (internal-test only, not UI), drill_key: string|null (null = calc line; drill goes via children), is_calc: bool}` · `BvaRow{grain{entity_id, account_id, cost_centre_id?}, actual, budget, forecast?, py?, var_abs, var_pct: string|null, var_pct_reason?, favourable: bool, material: bool, contribution_pct, drill_key}` · `DrillResponse{vouchers: {voucher_no, posting_date, document_date, amount, rows: {description, amount, source_file, source_row, batch_id}[]}[], next_cursor}`.

## Findings
`Finding{finding_id, finding_key, rule_id, rule_plain_name (doc 55), severity, status, amount, entity_id, account_id, period_id, owner: {owner_id, display_name}|null, due_date, evidence: {row_ids: string[], values: object, thresholds: object, grain: object}, waive?: {reason, expires}, history: FindingEvent[]}` · `TransitionRequest{to_status, note?, waive_reason?, waive_days?: 1..90, reference?}` (guards doc 23 §3 → ERR-040/041).

## Forecast / planning / scenarios
`ForecastRun{run_id, base_period_id, status, created_at, accuracy: {<group>: {method, mape: string|null, bias: string|null, hit_rate: string|null, history_months: int}}, method_map: {<group>: string}}` · `ForecastLine{period_id, entity_id, account_id, amount, method}` · `Scenario{scenario_id, name, base_run_id, deltas: Delta[], status}` `Delta{kind: "driver|pct|absolute", target: string, value: string, period_from?, period_to?}` · `GoalSeekRequest{target_kpi, target_value, driver}` → `GoalSeekResult{solved: bool, value?: string, iterations: int, reason?: string}` · Planning grids (drivers/headcount/capex/debt/wc/cash13) mirror doc 02 §5/§6 tables field-for-field with `value_decimal` strings.

## Adjustments / allocations / assumptions / year-end (doc 05 §4)
`Adjustment{adj_id, period_id, entity_id, account_id, amount, kind, label, reason, pair_group_id?, status, source, created_by}` · `AdjustmentCreate{lines: Adjustment[] (group), }` apply → ERR-042 if Σ≠0 for reclass/closing · `AllocationDef{def_id, name, method, source_scope, receivers: {cost_centre_id, pct?}[]}` · `Assumption{assumption_id, scope, scope_ref?, key, value_decimal, unit, status, version}` · `YearEndClose{fiscal_year}` → `YearEndResult{closing_adjustments: int, opening_batch_id, rollforward_delta_minor: 0}`.

## Exports / commentary / settings / dashboard
`ExportRequest{kind, period_id, layer?, scenario_ids?}` → Job → `Report{report_id, kind, path, sha256, checks: CheckResult[], snapshot: {batch_watermark, budget_version, forecast_run_id}}` · `CheckResult{name, expected: string, actual: string, delta_minor: int, pass: bool}` · `Commentary{commentary_id, period_id, scope, text, status, ai_assisted, prompt_version?, source_refs: string[], version}` · `CommentaryDraftRequest{scope, refs}` → ERR-070/071 per doc 22 · `SettingsUpdate{key, value}` (doc 62 keys only) · `Dashboard{period, kpis: KpiTile[], close_stages: {key, label, state, blocker_link?}[], top_variances: BvaRow[5], findings_by_severity: object, findings_by_owner: object, forecast_accuracy: object|null, dq_score: {score: int, deductions: {reason, points}[]}, alerts_count: int, unassigned_count: int}` · `KpiTile{key, label, value: string|null, na_reason?, delta_vs_budget?, delta_vs_py?, formula}`.

Field-level parity is enforced by the contract tests (doc 14): the OpenAPI schema generated from routes is diffed against this doc's tables in Wave 6 (script in doc 66 pipeline).
