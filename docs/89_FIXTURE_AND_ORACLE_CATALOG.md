# 89 — FIXTURE & ORACLE CATALOG (every test fixture, specified before it is built)

> Rule (docs 14 §2, 78): a fixture IS an expectation. This catalog is the complete list; the `tests/fixtures/README.md` packet must index exactly these files — a fixture not listed here may not be committed, and a file listed here must exist before the wave that consumes it closes. Hand-oracles are computed from the cited doc, never from running the code.

## 1. Statements & calc (`tests/fixtures/statements/`, consumed Wave 2b)
| Fixture | Contents | Oracle source |
|---|---|---|
| `pl_basic.json` / `.expected.json` | 8-line P&L (Rev 6,350,000.00 … Net 694,200.00) as account-tagged GL tuples | doc 03 §3 worked example |
| `bs_basic.json` / `.expected.json` | Assets 8,770,000 = L 6,950,000 + E 1,820,000, signed-sum-zero check | doc 03 §3 / attempt-#2 fixture values retained |
| `cf_basic.json` / `.expected.json` | OCF 1,480,000 (Net 694,200 + Depr 250,000 + WC/other 535,800 itemised), ICF −640,000, FCF/FCF-fin −520,000, net Δ 320,000 = BS cash Δ | doc 43 cash-conversion provenance |
| `rounding_oracle.json` | Largest-remainder cases: ₹'000 display, negatives, zero residual, single-line | doc 03 §3 / money.py spec |
| `bva_basic.json` / `.expected.json` | Doc 03 §5 oracles: material (+20%), non-material (+2.27% AND-fail), zero-budget | doc 03 §5 |
| `bridge_basic.json` | Volume/price/mix oracle (1,000 + 600 + 0 = 1,600) | doc 03 §6 |
| `kpi_basic.json` | All doc 43 KPI fixtures incl. every n/a (zero denominator) case | doc 43 table |

## 2. Rules (`tests/fixtures/rules/`, Wave 2c)
Per rule EXC-001…024: `exc_###_fires.json` (the doc 42 plant pattern in miniature, exact finding_key expected), `exc_###_silent.json` (the doc 42 control/boundary −1 minor unit), `exc_###_boundary.json` (threshold exact, +1). File naming and key expectations derive from doc 44 algorithms; the acceptance corpus (doc 42 §7 register) is the integration-level version of these.

## 3. Forecast (`tests/fixtures/forecast/`, Wave 2d)
`ma_basic` (doc 08 oracle: (105+115)/2 = 110; backtest APE 6.52%), `holt_basic.json` and `hw_flat.json` (agents compute expected values from doc 46 equations by hand/spreadsheet *before* the fixture is accepted — the computation sheet is committed as `.calc.md` alongside), `seasonal_24` (24-month indices), `driver_basic`, `phasing_basic` (largest-remainder sums to 100.000%).

## 4. Import (`tests/fixtures/import/`, Waves 1c–2a)
The doc 42 §5 malformed set, each `<name>.<ext>` + `<name>.expected.json` {rows_in, valid, quarantined_by_reason{}}. Plus `gl_happy.csv` (the Wave-1b sample, promoted), `gl_debit_credit.csv`, `gl_jpy_zero_exponent.csv`, `mapping_profiles/` (D365/Tally/SAP preset examples, doc 26).

## 5. Planning (`tests/fixtures/planning/`)
`alloc_basic` (doc 40: 180,000/120,000), `headcount_basic` (joiners/leavers → cost), `capex_slm`, `capex_wdv` (year-1/2 schedules hand-computed), `debt_basic` (interest on avg balance), `cash13_basic` (13 weekly buckets), `integrated_basic` (doc 29 §7 oracle: Δcash 480,000), `goal_seek_basic` (solvable + provably-unsolvable case).

## 6. Exports & cross-artifact (`tests/fixtures/golden/`)
Golden period = corpus FY26-P07 fully imported: expected API statement JSON, Excel cell map (sheet!cell → value/format/formula-presence), PPT slide-number map, PDF text extracts. Auditor dataset (AUD-I) is a *second* golden set generated from a different seed at audit time — never shipped in the repo before Wave 6.

## 7. Security & robustness (`tests/fixtures/hostile/`)
Zip-bomb xlsx (build-time generated), 1M-row CSV (generated), formula-injection descriptions, SQL-injection master names, prompt-injection descriptions (doc 88 G18 pattern), path-traversal file names, tampered-DB + broken-audit-chain project folders (doc 61/12 fixtures), migration DBs per released version (doc 61 §3, starts at v0.1).

## 8. Governance of this catalog
Adding a fixture = PR citing the doc section that oracles it + updating this file. Changing an expected value = treated as a spec change (doc 72): the PR must show the hand recomputation, not "code now outputs X".
