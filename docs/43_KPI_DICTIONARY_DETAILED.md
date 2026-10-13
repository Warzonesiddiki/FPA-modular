# 43 — KPI DICTIONARY, DETAILED (extends doc 29 §8)

> Every KPI: formula (doc 03 conventions), grain, source, interpretation, default RAG vs budget/PY, fixture. Implemented only in `calc/kpis.py`; UI/Excel/PPT consume. RAG thresholds are settings (per KPI: green/amber boundaries), worded labels always accompany colour.

| KPI | Formula | Fixture |
|---|---|---|
| Revenue growth YoY | (Rev − Rev PY)/|Rev PY| | 6.35M vs 5.9M → +7.6% |
| Gross margin % | GP/Revenue | 37.48% (03 §4) |
| EBITDA margin | EBITDA/Revenue | 1.14/6.35 → 18.0% |
| Net margin | Net/Revenue | 694,200/6,350,000 → 10.9% |
| Opex ratio | Opex/Revenue | 19.5% |
| Personnel cost % | Personnel/Revenue | per fixture data |
| Revenue per FTE | Revenue/closing HC (29 §3) | HC 50 → 127,000 |
| DSO | AR/Revenue × days in period | AR 1.2M, Rev 6.35M, 30d → 5.7d |
| DPO | AP/COGS × days | per fixture |
| DIO | Inventory/COGS × days | per fixture |
| WC days | DSO+DIO−DPO | sum of above |
| Cash conversion | Operating CF/EBITDA (OCF from the cf_basic oracle fixture: Net 694,200 + Depr 250,000 + WC/other operating adjustments 535,800 = 1,480,000 — fixture `tests/fixtures/statements/cf_basic.json`, doc 03 §3) | 1,480,000/1,140,000 → 1.30 |
| Current ratio | Current Assets/Current Liabilities | per BS fixture |
| Quick ratio | (CA−Inventory)/CL | per fixture |
| Debt/EBITDA | Total debt/(EBITDA×12/periods) annualised | labelled annualised |
| Interest cover | EBIT/Interest | per fixture |
| ROCE | EBIT/(Equity+Net Debt) | per fixture |
| Cash runway | Cash/avg monthly net burn (3m); n/a if CF-positive | burn>0 only |
| Forecast MAPE/bias | doc 08 §3 per group | 08 oracle |
| Budget hit rate | % periods within ±5% of budget (rolling 6) | count-based |
| Suspense ageing | EXC-007 oldest bucket amount | rule evidence |
| Manual journal % | manual vouchers/total vouchers | import flags |
| Unbudgeted spend % | EXC-017 Σ/actual Σ | rule evidence |
| Exception closure rate | closed+verified/findings due in period | workflow data |
| Close cycle days | lock date − period end (business days) | doc 30 |
| DQ score | doc 29 §9 | its fixture |
| Capex/D&A | Capex additions/Depreciation | 400/250 → 1.60 |
| AR overdue % | AR past due date/AR (needs due dates; else n/a) | recon data |

Zero/negative denominators → `n/a` + reason (doc 03 §4), counted in tests per KPI.
