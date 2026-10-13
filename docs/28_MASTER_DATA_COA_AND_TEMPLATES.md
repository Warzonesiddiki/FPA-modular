# 28 — MASTER DATA, CHART-OF-ACCOUNTS & INDUSTRY TEMPLATES

## 1. Default COA template (ships with every new project; analyst edits freely)
Ranges: 1000–1499 Assets (1100 Cash, 1200 Receivables, 1300 Inventory, 1400 Fixed Assets), 1500–1999 (1999 Suspense — pre-tagged), 2000–2999 Liabilities (2100 Payables, 2200 Debt, 2300 Accruals), 3000–3999 Equity, 4000–4999 Revenue, 5000–5999 COGS, 6000–7999 Opex (6100 Personnel, 6200 Rent, 6300 SaaS/IT…), 8000 Depreciation/Interest, 9000 Tax. Each template account carries: statement_line, normal_side, tags (doc 19B) — so a new project produces statements on first import without setup archaeology. Statement line map (Revenue, COGS, Gross Profit inputs, Personnel, Rent, Other Opex, Depreciation, Interest, Tax…) is part of the template and editable in S12.

## 2. Industry starter packs (data, not code — templates = COA + KPI set + driver set + rule-threshold tweaks)
v1 ships: **General/Trading**, **Manufacturing** (inventory/production drivers), **SaaS/Services** (MRR-style revenue drivers, headcount-heavy), **Retail** (store cc preset). Phase 2: healthcare, construction (WIP), nonprofit (funds as entities), professional services. A pack is a versioned JSON in `packs/` validated by a schema; pack builder UI is Phase 2 — v1 packs are files the owner can request/customise via support. (Attempt-#2 lesson: 12 packs before one working month-end is how scope dies — 4 good packs, sequenced.)

## 3. Master-data governance
Codes immutable once used (rename = new code + mapping note); merge-duplicates tool (S12) re-points references with audit; bulk import (06 pipeline, kind `master`); quarterly hygiene prompts via DQ score deductions (doc 29 §DQ) e.g. unowned accounts, inactive vendors with balances.
