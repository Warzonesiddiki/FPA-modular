# 29 — BUDGETING, PLANNING & KPI LIBRARY SPECIFICATION

> Extends doc 08 (forecast methods). Planning turns forecasts into an integrated 3-statement plan. Screens S17/S09/S10; APIs §10 addendum.

## 1. Budgeting
Budget versions: import (doc 06) or grid-author on top of import (every edit audited w/ before/after), copy-version, approve/lock workflow (23 §5), phasing (08 §5). Budget-vs-forecast-vs-actual three-way compare in BvA (budget_version + forecast_run selectors; columns labelled with version names in every export).

## 2. Driver planning (S17 Drivers)
Drivers: volume, price, headcount, rate, %growth, custom(decimal). Driver → account-group formula registry: `revenue = volume × price`, `personnel = headcount × avg_cost`, `rent = sites × rent_per_site` etc.; formula shown beside every computed line; overrides flagged. Driver import kind `drivers`; manual edits versioned.

## 3. Headcount plan
Per cost-centre: opening HC, joiners, leavers by month, avg monthly cost, increment % + effective month, bonus % — computes personnel cost series + HC closing (joiners−leavers; negative HC impossible → validation). Feeds driver_based forecast + scenario deltas (HC freeze = joiners 0 preset).

## 4. Capex & depreciation
Asset classes w/ useful life + method (SLM/WDV) + residual %; capex additions by month → depreciation schedule (pro-rata month of addition) → PL depreciation + BS NBV + CF capex lines. Disposals: month + NBV removal + gain/loss line (analyst-entered proceeds).

## 5. Debt schedule
Facilities: opening balance, drawdowns/repayments by month, rate % (fixed or base+spread), interest = average balance × rate/12 (Decimal, fixture-tested), covenant fields (informational). Outputs interest + closing debt for integrated forecast.

## 6. Working capital & 13-week cash
WC assumptions DSO/DPO/DIO targets by entity → forecast receivables/payables/inventory from revenue/COGS forecast. **13-week cash:** weekly buckets; inflows from receivables ageing (opening AR by due week + forecast sales × collection curve), outflows AP ageing, payroll dates, debt service, capex, tax dates (analyst calendar); opening bank input/recon (FR-REC); minimum-balance alert (FR-ALR). Weekly ≠ monthly/4 — calendar weeks Mon–Sun from a start date.

## 7. Integrated forecast integrity
Forecast PL + BS movements + CF must articulate: ΔCash(CF) = ΔCash(BS); retained earnings roll = prior + Net Income − distributions(driver); imbalance → checks failure (doc 09 §4 extension) with the broken link named; never an auto-plug account. **Oracle:** Net Income 694,200 (doc 03) + Depr 250,000 − Capex 400,000 − ΔWC 64,200 → Net Cash Δ 480,000 == BS cash movement in fixture.

## 8. KPI catalogue (≥30, each: formula ref doc 03 §4 style + fixture in calc/kpis)
Revenue growth (MoM/YoY), GM%, EBITDA%, EBIT%, Net margin, Opex%, Personnel cost%, Revenue/FTE, DSO, DPO, DIO, WC days, Cash conversion, Current ratio, Quick ratio, Debt/EBITDA, Interest cover, ROCE (EBIT/CE), Cash runway (cash ÷ avg monthly net burn, n/a if cash-generative), Budget accuracy (FVA MAPE by group), Forecast bias, Suspense ageing balance, Manual-journal %, Unbudgeted spend %, Exception closure rate, Close cycle days, DQ score (§9), Capex/D&A ratio, AR overdue %.

## 9. Data-quality (DQ) score (calc/quality_score)
100 − deductions: TB imbalance (blocks, score shown 0-category), unmapped/quarantined % (>2% → −10…−30 scaled), accounts without owner (−1 ea, cap −10), stale suspense >30d (−10), manual journals >20% (−5), missing budget (−10), forecast stale >1 period (−5). Deductions table is the UI — the score never appears without its reasons.

## 10. API addendum (extends doc 05; same conventions/errors)
`/projects/{id}/planning/{drivers|headcount|capex|debt|wc|cash13}` GET/PUT (bulk, versioned) · POST `/projects/{id}/planning/integrate` → forecast run from planning inputs · GET `/projects/{id}/sensitivity` (params: driver, range, steps, target output) · POST `/projects/{id}/goal-seek` {target_kpi, target_value, driver} → {solved_value|no_solution, iterations} · `/projects/{id}/close/{tasks,sign-off,calendar}` · `/projects/{id}/reconcile/*` · `/projects/{id}/alerts` · report-builder: `/projects/{id}/report-definitions` CRUD + POST render. All paginated/versioned/audited per doc 05 conventions. Packets for planning modules: planning/drivers.py, headcount.py, capex.py, debt.py, working_capital.py, cash13.py, sensitivity.py, goal_seek.py (+tests) — added to the regenerated manifest.
