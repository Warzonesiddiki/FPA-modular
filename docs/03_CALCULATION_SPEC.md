# 03 — CALCULATION SPECIFICATION

> Owner of: every formula. Every section ends with a hand-worked oracle example; that example is a test fixture written before engine code (MASTER_PLAN §5). All math in integer minor units / Decimal via `app/core/money.py`. Rounding: ROUND_HALF_UP to minor unit at presentation boundaries only; internal sums are exact integers, so no rounding drift. Float anywhere in calc = defect.

## 1. Sign & presentation conventions
Storage: debit +, credit − (doc 02). Presentation: revenue/credit-normal lines shown positive when favourable per statement template; every presented line carries `presentation_sign ∈ {+1,−1}` from `accounts.normal_side` and the statement template — one mapping table in code (`calc/statements.py`), tested line-by-line. Variance favourability: revenue ↑ favourable, cost ↑ unfavourable; the favourable flag is computed, never inferred from sign alone.

## 2. Trial balance (gate, FR-IMP-09)
Per (project, period, entity): `Σ debit = −Σ credit` exactly in minor units; app reports imbalance by entity → account → voucher (drill via `calc/drilldown`). **Oracle:** rows +100000, +50000, −150000 → balanced 0. Rows +100000, −99999 → imbalance 1 (₹0.01) reported, analysis locked until resolved or owner-waived with audit note.

## 3. Statements
Account → statement line via `accounts.statement_line`. 
- **P&L:** Revenue − COGS = Gross Profit; − Opex = EBITDA (memo: depreciation line flagged by account_type mapping); − Depreciation = EBIT; − Interest − Tax = Net Income. Subtotals are integer sums of mapped lines.
- **Balance Sheet:** Assets = Liabilities + Equity must hold exactly; if opening balances absent, BS is presented as *movement* statement and labelled as such — never a fake balanced BS.
- **Cash Flow (indirect):** Net Income + non-cash (depreciation, ΔWC from BS movement accounts) − capex = Net Cash Change; must equal BS cash-account movement when both available; mismatch → check item on Exports S11, deck generation blocked (doc 10).
- **Largest-remainder presentation rounding** (to ₹'000 display): allocate rounding residual to the largest line so displayed lines sum to displayed subtotal (fixtures in tests; algorithm in money.py).
**Oracle (pl_basic):** Revenue 6,350,000.00; COGS 3,970,000.00; GP 2,380,000.00; Opex 1,240,000.00; EBITDA 1,140,000.00; Depr 250,000.00; EBIT 890,000.00; Tax 195,800.00 (22%); Net 694,200.00.

## 4. KPIs (each: formula + fixture in `calc/kpis.py`)
Gross margin % = GP/Revenue; EBITDA margin; Opex ratio; DSO = Receivables/Revenue × days-in-period; DPO, DIO analogously; Working-capital days = DSO+DIO−DPO; Cash conversion = Operating CF/EBITDA; Revenue growth % YoY. Division by zero → KPI shown "n/a" with reason, never 0 or crash. **Oracle:** GM% above = 2,380,000/6,350,000 = 37.48% (2dp, half-up).

## 5. Budget-vs-Actual (BvA)
At lowest shared grain: if budget is entity×account and actuals entity×cc×account, BvA grain = entity×account (cc collapsed, disclosed in UI/export footnote). Per row: Actual, Budget, Forecast(latest locked), PY-actual, Var₹ = Actual−Budget (signed), Var% = Var₹/|Budget| (Budget=0 → Var% = `n/a`, materiality by absolute threshold only), Favourable bool, Contribution = Var₹ / Σ|Var₹| of parent group. Materiality: `material_abs_minor` AND `material_pct` from settings (defaults ₹100,000 and 5%; both must trip — the AND-test whose absence caused attempt #4's control failure). **Oracle:** Actual 900,000 vs Budget 880,000 on expense: Var +20,000 (+2.27%) → not material (pct fails AND) → no EXC-018. Actual 1,200,000 vs 1,000,000: +200,000 (+20%) → material.

## 6. Variance bridge (attribution)
Only when driver_values exist for the account group: Total Var = Volume + Price + Mix + Other(residual, labelled). Volume=(Qa−Qb)×Pb; Price=(Pa−Pb)×Qa; Mix=residual after volume/price at subgroup grain. Components must sum to total exactly (residual absorbs rounding). Without drivers: bridge not rendered; UI states "Driver data not imported for this line" — fabrication is a defect. **Oracle:** Budget 100u×₹50=5,000; Actual 120u×₹55=6,600; Var=1,600 = Volume 1,000 + Price 600 + Mix 0.

## 7. Period comparisons & phasing
YoY = same period_no prior FY. QoQ/MoM sequential. YTD = Σ P01..current. Budget phasing for YTD comparisons uses budget at same periods (never annual/12 unless budget itself is annual-only, in which case doc 08 §5 phasing curve applies and is disclosed).

## 8. Drilldown contract
Every aggregate cell exposes `{entity, account, cc?, period, version refs}` → gl_row list (voucher, dates, description, amount, source_file, source_row). A cell with zero rows must not exist (statements only render lines with activity or explicit zero-lines from template).
