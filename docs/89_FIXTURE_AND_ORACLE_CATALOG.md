# 89 — FIXTURE & ORACLE CATALOG (every test fixture, specified before it is built)

> Rule (docs 14 §2, 78): a fixture IS an expectation. This catalog is the complete list; the `tests/fixtures/README.md` work item must index exactly these files — a fixture not listed here may not be committed, and a file listed here must exist before the milestone that consumes it closes (doc 86). Hand-oracles are computed from the cited doc, never from running the code. Period ids use doc 02 notation (`<fy>-P<nn>`).

## 1. Statements & calc (`tests/fixtures/statements/`, consumed M2)
| Fixture | Contents | Oracle source |
|---|---|---|
| `pl_basic.json` / `.expected.json` | P&L as account-tagged GL tuples: `rev` 6,350,000 · `cogs` 3,970,000 · `gp` 2,380,000 · opex 1,240,000 = `opex_pers` 620,000 + `opex_rent` 180,000 + `opex_it` 140,000 + `opex_mkt` 120,000 + `opex_prof` 90,000 + `opex_other` 90,000 · `ebitda` 1,140,000 · `depr` 250,000 · `ebit` 890,000 · `int` 0 · `pbt` 890,000 · `tax` 195,800 · `net` 694,200 | doc 03 §3 worked example |
| `bs_basic.json` / `.expected.json` | Closing balances: `ast_cash` 1,400,000 · `ast_ar` 1,200,000 · `ast_inv` 950,000 · `ast_oca` 300,000 (current assets 3,850,000) · `ast_fa` 4,520,000 · `ast_onca` 400,000 → Assets 8,770,000; `lia_ap` 1,800,000 · `lia_debt_st` 1,500,000 · `lia_acc` 1,050,000 · `lia_ocl` 600,000 (current liabilities 4,950,000) · `lia_debt_lt` 2,000,000 → Liabilities 6,950,000; `eq_cap` 1,000,000 · `eq_re` 820,000 · `eq_oci` 0 → Equity 1,820,000; signed-sum-zero check | doc 03 §3 / doc 43 KPI inputs |
| `cf_basic.json` / `.expected.json` | OCF 1,480,000 (Net 694,200 + Depr 250,000 + WC/other 535,800 itemised per doc 03 §3 table), ICF −640,000 (capex 640,000), financing −520,000, net Δ 320,000 = BS cash Δ (opening cash 1,080,000 → closing 1,400,000). **Not** the doc 29 §7 planning world (`integrated_basic`, §5) | doc 03 §3 / doc 43 cash-conversion |
| `rounding_oracle.json` | Largest-remainder cases: ₹'000 display, negatives, zero residual, single-line | doc 03 §3 / money.py spec |
| `bva_basic.json` / `.expected.json` | Doc 03 §5 six oracles: fires (+20%), both-fail (+2.27%), **abs-only** (+150,000 / +1.5%), **pct-only** (+60,000 / +30%), zero-budget material, zero-budget small | doc 03 §5 |
| `bridge_basic.json` | Volume/price/mix oracle (1,000 + 600 + 0 = 1,600) | doc 03 §6 |
| `kpi_basic.json` / `kpis_basic.expected.json` | Every doc 43 row (2 dp) incl. every n/a case (interest cover, cash runway when CF-positive, AR overdue without due dates) | doc 43 table |

## 2. Rules (`tests/fixtures/rules/`, M2)
Per rule EXC-001…024: `exc_###_fires.json` (the doc 42 plant pattern in miniature, exact finding_key expected), `exc_###_silent.json` (the doc 42 control/boundary −1 minor unit), `exc_###_boundary.json` (threshold exact, +1). File naming and key expectations derive from doc 44 algorithms; the acceptance corpus (doc 42 §7 register) is the integration-level version of these.

## 3. Forecast (`tests/fixtures/forecast/`, M2)
`ma_basic` (doc 08 oracle: (105+115)/2 = 110; backtest APE 6.52%), `holt_basic.json` (doc 46: l₄ 122.035, b₄ 9.2485, ŷ₅ 131.2835, ŷ₆ 140.5320), `hw_flat.json` (doc 46: fixed point, ŷ₂₅ 100 / ŷ₂₆ 110 / ŷ₂₇ 100, grid tie-break (0.1, 0.1, 0.1)), `seasonal_short.json` (n = 23 → `not_run`), `seasonal_24` (24-month indices 0.9524/1.0476), `driver_basic`, `phasing_basic` (largest-remainder sums to 100.000%). The hand computation for each is committed as `<name>.calc.md` alongside, *before* the engine code.

## 4. Import (`tests/fixtures/import/`, M1–M2)
The doc 42 §5 malformed set, each `<name>.<ext>` + `<name>.expected.json` {rows_in, valid, quarantined_by_reason{}}. Plus `gl_happy.csv` (today's `sample-data/gl_sample.csv`, promoted), `gl_debit_credit.csv`, `gl_jpy_zero_exponent.csv`, `mapping_profiles/` (D365/Tally/SAP preset examples, doc 26).

## 5. Planning (`tests/fixtures/planning/`)
`alloc_basic` (doc 40: 180,000/120,000), `headcount_basic` (joiners/leavers → cost), `capex_slm`, `capex_wdv` (year-1/2 schedules hand-computed), `debt_basic` (interest on avg balance), `cash13_basic` (13 weekly buckets), `integrated_basic` (doc 29 §7 oracle: Δcash 480,000), `goal_seek_basic` (solvable + provably-unsolvable case).

## 6. Exports & cross-artifact (`tests/fixtures/golden/`)
Golden period = corpus `2025-P07` fully imported: expected API statement JSON, Excel cell map (sheet!cell → value/format/formula-presence), PPT slide-number map, PDF text extracts. The audit dataset (doc 34 stream I) is a *second* golden set generated from a different seed during the M5 audit session — never committed before that session.

## 7. Security & robustness (`tests/fixtures/hostile/`)
Zip-bomb xlsx (build-time generated), 1M-row CSV (generated), formula-injection descriptions, SQL-injection master names, prompt-injection descriptions (doc 88 G18 pattern), path-traversal file names, tampered-DB + broken-audit-chain project folders (doc 61/12 fixtures), migration DBs per released version (doc 61 §3, starts at v0.1).

## 8. Governance of this catalog
Adding a fixture = PR citing the doc section that oracles it + updating this file. Changing an expected value = treated as a spec change (doc 72): the PR must show the hand recomputation, not "code now outputs X".
