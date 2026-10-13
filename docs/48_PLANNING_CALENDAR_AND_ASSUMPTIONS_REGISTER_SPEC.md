# 48 — PLANNING CALENDAR & ASSUMPTIONS REGISTER SPECIFICATION

## 1. Annual planning calendar (template, per project, shown S17/S16)
T-minus milestones before FY start: strategy targets (T-90d) → driver assumptions due (T-60) → department inputs (T-45) → consolidation & challenge (T-30) → budget approval + lock (T-14) → phasing + board pack (T-7). Quarterly: rolling-forecast refresh windows (first 5 business days after close). Dates computed on the close calendar (doc 30) with owner per milestone (close_tasks kind=`manual`, category=`planning`).
## 2. Assumptions register (the single home for "what we assumed")
`assumptions(assumption_id PK, project_id, scope (project|entity|account_group), key (e.g. `price_increase_pct`, `attrition_pct`, custom), value_decimal TEXT, unit, owner_id, source_note, valid_from_period, version, status draft|approved)` — every driver value (29) and scenario delta may reference an assumption_id; forecast runs record the assumption versions used (snapshot). Assumption change after budget lock → impact list (which runs/scenarios used the old version; marked stale like doc 41).
## 3. Governance
Approval of project-level assumptions = named approver + date (attest, audited); exports' Forecast sheet includes an Assumptions block (key, value, version) — a forecast without visible assumptions must not reach the board.
