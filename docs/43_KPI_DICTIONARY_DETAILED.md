# 43 — KPI DICTIONARY, DETAILED (extends doc 29 §8)

> Every KPI: formula (doc 03 §4 conventions — closing balances for BS inputs, `days_in_period` = calendar days, **2 dp ROUND_HALF_UP**, `n/a` + reason on zero divisor), grain, source, interpretation, default RAG vs budget/PY, fixture. Implemented only in `calc/kpis.py`; UI/Excel/PPT consume. RAG thresholds are settings (per KPI: green/amber boundaries), worded labels always accompany colour. **Fixture worlds:** every KPI example below is computed from `pl_basic` + `bs_basic` + `cf_basic` (doc 89 §1) unless marked *(integrated_basic)*; the planning oracle in doc 29 §7 is a different cash-flow world (capex 400,000, ΔWC −64,200, ΔCash 480,000) with the same P&L and must not be mixed into `cf_basic` tests. `bs_basic` closing balances used here: AR 1,200,000 · AP 1,800,000 · Inventory 950,000 · Cash 1,400,000 · ST debt 1,500,000 · LT debt 2,000,000 · current assets 3,850,000 · current liabilities 4,950,000 (full line list in `bs_basic.json`).

| KPI | Formula | Fixture |
|---|---|---|
| Revenue growth YoY | (Rev − Rev PY)/|Rev PY| | 6,350,000 vs 5,900,000 → +7.63% |
| Gross margin % | GP/Revenue | 37.48% (03 §4) |
| EBITDA margin | EBITDA/Revenue | 1,140,000/6,350,000 → 17.95% |
| Net margin | Net/Revenue | 694,200/6,350,000 → 10.93% |
| Opex ratio | Σ opex/Revenue | 1,240,000/6,350,000 → 19.53% |
| Personnel cost % | `opex_pers`/Revenue | pl_basic opex_pers 620,000 → 9.76% |
| Revenue per FTE | Revenue/closing HC (29 §3) | HC 50 → 127,000 |
| DSO | closing AR/Revenue × days_in_period | 1,200,000/6,350,000 × 30 → 5.67 d |
| DPO | closing AP/COGS × days_in_period | 1,800,000/3,970,000 × 30 → 13.60 d |
| DIO | closing inventory/COGS × days_in_period | 950,000/3,970,000 × 30 → 7.18 d |
| WC days | DSO + DIO − DPO | 5.67 + 7.18 − 13.60 → −0.75 d (negative = supplier-funded; shown, not clipped) |
| Cash conversion | Operating CF/EBITDA (OCF from the cf_basic oracle fixture: Net 694,200 + Depr 250,000 + WC/other operating adjustments 535,800 = 1,480,000 — fixture `tests/fixtures/statements/cf_basic.json`, doc 03 §3) | 1,480,000/1,140,000 → 1.30 |
| Current ratio | current assets/current liabilities | 3,850,000/4,950,000 → 0.78 |
| Quick ratio | (CA − inventory)/CL | 2,900,000/4,950,000 → 0.59 |
| Debt/EBITDA (annualised) | (ST + LT debt)/(EBITDA × 12 / periods_in_window) | 3,500,000/(1,140,000 × 12) → 0.26 (1-period window; label "annualised") |
| Interest cover | EBIT/Interest | pl_basic interest 0 → `n/a` ("no interest expense") — the n/a path is the fixture |
| ROCE (annualised) | EBIT × 12 / (Equity + debt − cash) | 890,000 × 12 / (1,820,000 + 3,500,000 − 1,400,000) → 272.45% (1-period window; label "annualised") |
| Cash runway | Cash/avg monthly net burn (3m); n/a if CF-positive | burn>0 only |
| Forecast MAPE/bias | doc 08 §3 per group | 08 oracle |
| Budget hit rate | % periods within ±5% of budget (rolling 6) | count-based |
| Suspense ageing | EXC-007 oldest bucket amount | rule evidence |
| Manual journal % | manual vouchers/total vouchers | import flags |
| Unbudgeted spend % | EXC-017 Σ/actual Σ | rule evidence |
| Exception closure rate | closed+verified/findings due in period | workflow data |
| Close cycle days | lock date − period end (business days) | doc 30 |
| DQ score | doc 29 §9 | its fixture |
| Capex/D&A | capex additions/depreciation | 640,000/250,000 → 2.56 (cf_basic); 400,000/250,000 → 1.60 *(integrated_basic)* |
| AR overdue % | AR past due date/AR (needs due dates; else n/a) | recon data |

Zero/negative denominators → `n/a` + reason (doc 03 §4), counted in tests per KPI. Every row above is a test case in `tests/fixtures/kpis/kpis_basic.expected.json`; a KPI whose fixture column still says "per fixture" is not done.
