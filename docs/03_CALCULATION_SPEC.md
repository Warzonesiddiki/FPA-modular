# 03 — CALCULATION SPECIFICATION

> Owner of: every formula. Every section ends with a hand-worked oracle example; that example is a test fixture written before engine code (MASTER_PLAN §5, doc 89). All math in integer minor units / Decimal via `app/core/money.py`. Rounding: ROUND_HALF_UP to the minor unit at presentation boundaries only; internal sums are exact integers, so there is no rounding drift. Float anywhere in calc = defect. Line keys come from the registry in doc 45 §1 and nowhere else.

## 1. Sign & presentation conventions
Storage: debit +, credit − (doc 02 §1). Presentation: every statement line carries `presentation_sign ∈ {+1, −1}` from the doc 45 registry (revenue, liabilities and equity are credit-normal and presented positive; costs and assets debit-normal and presented positive). `amount_presented = presentation_sign × Σ amount_minor`. Variance favourability: for revenue-type lines `favourable = actual_presented ≥ budget_presented`; for cost-type lines `favourable = actual_presented ≤ budget_presented`; the flag is computed from the line's `favourable_direction` in the registry, never inferred from the sign of the variance. One mapping table in code (`calc/statements.py`), tested line by line.

## 2. Trial balance (gate, FR-IMP-010)
Per (project, period, entity): `Σ amount_minor` over all committed rows of the layer = 0 exactly (credit stored negative). The app reports any imbalance by entity → account → voucher (drill via `calc/drilldown`). **Oracle:** rows +100000, +50000, −150000 → balanced (0). Rows +100000, −99999 → imbalance 1 minor unit (₹0.01) reported; analysis screens show the blocking banner until resolved or owner-waived with an audited note (doc 06 §2 step 8).

## 3. Statements
Account → statement line via `accounts.statement_line` (keys and ordering: doc 45 §1; unmapped accounts: doc 45 §2).
- **P&L:** `gp = rev − cogs`; `ebitda = gp − Σ opex_*`; `ebit = ebitda − depr`; `pbt = ebit − int`; `net = pbt − tax`. Subtotals are integer sums of presented lines.
- **Balance sheet:** `Σ ast_* = Σ lia_* + Σ eq_*` must hold exactly when opening balances exist (first FY: `opening` import, doc 06; later FYs: the system-generated opening batch, doc 38). Retained earnings presented = opening `eq_re` + current-FY YTD `net` (the P&L is closed into `eq_re` only by the year-end process, doc 38 §1 — within the year the roll is computed, never posted). If no opening balances exist for the FY, the BS is presented as a **movement statement** and labelled so on screen and in every export — never a fake balanced BS.
- **Cash flow (indirect)** — classification is by line key, one table, tested:

| CF section | Lines (doc 45 keys) | Sign rule |
|---|---|---|
| Operating | `net`; add back `depr`; Δ provisions (`lia_acc`); ΔWC = −Δ`ast_ar` −Δ`ast_inv` −Δ`ast_oca` +Δ`lia_ap` +Δ`lia_ocl` | increase in an asset reduces cash; increase in a liability increases cash |
| Investing | capex = Δ`ast_fa` + `depr` (additions net of disposals at NBV; disposals proceeds from `capex_assets` when planned) ; Δ`ast_onca` | outflow negative |
| Financing | Δ`lia_debt_st` + Δ`lia_debt_lt`; Δ`eq_cap`; Δ`eq_oci`; dividends (Δ`eq_re` − `net`) | inflow positive |
| Net change | Σ sections | must equal Δ`ast_cash` when a full BS exists; mismatch → Checks item (doc 09 §4), deck blocked (doc 10 §3) |

Interest: shown within operating by default; setting `calc.cf_interest_section = operating|financing` (doc 62) moves `int`, labelled in exports.
- **Display rounding (₹'000 view):** presented lines are rounded to thousands with the **largest-remainder method** (`money.largest_remainder_allocate`: floors, then distribute the residual to the lines with the largest fractional remainders, ties by line order) so displayed lines sum exactly to the displayed subtotal. This is the single rounding algorithm for display; "residual to the largest line" is **not** used.

**Oracle (pl_basic):** Revenue 6,350,000.00; COGS 3,970,000.00; GP 2,380,000.00; Opex 1,240,000.00; EBITDA 1,140,000.00; Depr 250,000.00; EBIT 890,000.00; Interest 0; PBT 890,000.00; Tax 195,800.00 (22%); Net 694,200.00.
**Oracle (bs_basic):** Assets 8,770,000 = Liabilities 6,950,000 + Equity 1,820,000 (doc 89 §1).
**Oracle (cf_basic):** OCF 1,480,000 (Net 694,200 + Depr 250,000 + WC/other +535,800) · ICF −640,000 · FCF −520,000 · Net Δ 320,000 = Δ`ast_cash` (doc 89 §1). The *planning* oracle in doc 29 §7 is a different fixture (`integrated_basic`: Capex 400,000, ΔWC −64,200, Net Δ 480,000) — the two must never be mixed within one fixture file.

## 4. KPIs (each: formula + fixture in `calc/kpis.py`; the complete list is doc 43)
Basis rules (apply to every KPI unless doc 43 says otherwise): **balance-sheet inputs use the period-end closing balance**; flow inputs use the period (month) or YTD as the KPI's grain states; `days_in_period` = calendar days of the period; annualisation = `× 12 / periods_in_window` and is always labelled "annualised". Precision: ratios and percentages are computed in Decimal and presented at **2 dp, ROUND_HALF_UP** (settings may reduce display precision; stored value stays 2 dp). Division by zero → KPI value `n/a` with a reason string, never 0 or a crash.
Core set: Gross margin % = GP / Revenue; EBITDA margin = EBITDA / Revenue; Opex ratio = Σ opex / Revenue; DSO = closing `ast_ar` / Revenue × days_in_period; DPO = closing `lia_ap` / COGS × days; DIO = closing `ast_inv` / COGS × days; Working-capital days = DSO + DIO − DPO; Cash conversion = OCF / EBITDA; Revenue growth YoY = (Rev − Rev_PY) / |Rev_PY|.
**Oracle:** GM% = 2,380,000 / 6,350,000 = 37.48%; EBITDA margin = 17.95%; Net margin = 10.93%; Opex ratio = 19.53%; DSO with closing AR 1,200,000 and 30 days = 5.67 days.

## 5. Budget-vs-Actual (BvA)
At the lowest shared grain: if budget is entity×account and actuals entity×cc×account, BvA grain = entity×account (cc collapsed, disclosed in UI/export footnote). Per row: Actual, Budget, Forecast (latest locked run), PY actual, `var_abs = Actual − Budget` (signed, presented units), `var_pct = var_abs / |Budget|` (Budget = 0 → `var_pct = n/a`, materiality by the absolute leg only, reason recorded), Favourable (per §1), Contribution = var_abs / Σ|var_abs| of the parent group.
**Materiality is an AND-test:** `material = |var_abs| ≥ materiality.abs_minor AND |var_pct| ≥ materiality.pct` (keys per doc 62; defaults ₹100,000 and 5%). The absence of the AND is the attempt-#4 control failure; therefore the oracle set below must contain **both one-leg cases**, because a case where both legs fail cannot distinguish AND from OR.
**Oracles (bva_basic):**
| Case | Budget | Actual | var_abs | var_pct | abs leg | pct leg | material |
|---|---|---|---|---|---|---|---|
| fires | 1,000,000 | 1,200,000 | +200,000 | +20.00% | pass | pass | **yes** |
| both fail | 880,000 | 900,000 | +20,000 | +2.27% | fail | fail | no |
| abs only | 10,000,000 | 10,150,000 | +150,000 | +1.50% | pass | fail | **no** |
| pct only | 200,000 | 260,000 | +60,000 | +30.00% | fail | pass | **no** |
| zero budget | 0 | 150,000 | +150,000 | n/a | pass | n/a | yes (abs only, reason "budget is zero") |
| zero budget small | 0 | 40,000 | +40,000 | n/a | fail | n/a | no |

## 6. Variance bridge (attribution)
Only when `driver_values` exist for the account group: Total Var = Volume + Price + Mix + Other (residual, labelled). Volume = (Qa − Qb) × Pb; Price = (Pa − Pb) × Qa; Mix = residual after volume/price at sub-group grain; Other absorbs any rounding so the components sum to the total exactly. Without drivers the bridge is not rendered and the UI states "Driver data not imported for this line" — fabrication is a defect. **Oracle:** Budget 100 u × ₹50 = 5,000; Actual 120 u × ₹55 = 6,600; Var = 1,600 = Volume 1,000 + Price 600 + Mix 0 + Other 0.

## 7. Period comparisons & phasing
YoY = same `period_no` in the prior fiscal year (`calendar.prior_year`). QoQ/MoM are sequential. YTD = Σ P01..current of the same fiscal year. PY-YTD likewise. Budget phasing for YTD comparisons uses the budget at the same periods — never annual/12 unless the budget itself is annual-only, in which case doc 08 §5's phasing curve applies and the derived lines are stamped `source=phased:<curve>`. **Oracle:** FY `2025` P01..P03 actuals 100, 120, 110 → YTD at P03 = 330; PY P03 YTD (90, 100, 100) = 290; YoY-YTD growth = 40 / 290 = 13.79%.

## 8. Drilldown contract
Every aggregate cell exposes `drill_key = {statement|bva|kpi, entity, account?, cc?, period, layer, version refs}` → voucher groups → gl_rows (voucher, dates, description, amount, source_file, source_row) and, when the layer includes adjustments, a second section of adjustment lines (reason, author). A rendered cell with zero rows must not exist (statements render only lines with activity, plus explicit zero lines from the template, which drill to "no activity").
