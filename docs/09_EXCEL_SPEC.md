# 09 — EXCEL OUTPUT SPECIFICATION

> Owner of: the board Excel pack (`app/exports/excel_pack.py` + `sheet_*.py`, openpyxl). One workbook per (project, period), generated from one snapshot (doc 05 exports). Every value is either a literal from calc objects or an Excel formula over literals on the same sheet — never a re-computation in a second engine. Generated with values AND formulas policy per §3.

## 1. Workbook contract
File: `<Project>_MonthEnd_<YYYY-P##>.xlsx`. Metadata (doc properties + Cover): project, period, generated-at, app version, snapshot ids (GL batch watermark, budget version, forecast run), prepared-by label. Print setup on every sheet: landscape/portrait per sheet table, fit-to-page, repeating header rows, footer `page X of Y · <project> · <period> · Advisory — see Cover`. Freeze panes below headers. Filters on data tables. No external links, no macros, no hidden sheets (a `meta` sheet is visible and labelled).

## 2. Sheets (12, fixed order)
| # | Sheet (packet) | Content | Source |
|---|---|---|---|
| 1 | Cover | Title, period, snapshot stamps, advisory disclaimer, how-to-read, checks summary (pass/fail counts linking to Checks) | reports registry |
| 2 | Contents | Sheet index with one-line purpose + hyperlink | static |
| 3 | PL | P&L: Actual, Budget, Var₹, Var%, PY, Forecast — month + YTD blocks | calc/statements+bva |
| 4 | BS | Balance sheet or movement statement (labelled, doc 03 §3) | calc |
| 5 | CF | Cash flow indirect + tie-out line to BS cash movement | calc |
| 6 | BvA | Full variance table at export grain with favourable flags, contribution %, material highlights | calc/bva |
| 7 | Exceptions | Findings: rule, severity, owner, status, amount, age, key, suggested fix (kind label + confidence, doc 07 §7), suggestion status — potential-exception wording | findings |
| 8 | Forecast | Remaining-year forecast by group, method per group, backtest MAPE, scenario columns if selected | forecast run |
| 9 | KPIs | KPI table with formulas text and n/a reasons | calc/kpis |
| 10 | DrillData | The GL rows behind this period (voucher, dates, account, amount, source file/row) — the audit pack | gl_rows |
| 11 | Checks | Every tie-out check: name, expected, actual, Δ, PASS/FAIL (doc §4) | checks engine |
| 12 | Sources | Import batches used: file, hash, rows in/valid/quarantined, mapping profile+version, committed-at | import_batches |

## 3. Formulas vs values
Subtotal/total cells on PL/BS/CF/BvA = live Excel `SUM` formulas over the literal lines directly above (auditors can re-perform in Excel). Source data cells = literals. Cross-sheet references only from Checks to the checked cells. Number formats: `#,##0` (₹'000 view toggle writes a *separate* workbook variant, never rescales silently), `#,##0.00` detail, percentages `0.0%`, negatives in parentheses AND with minus in data exports (colour never sole signal, P19). Column widths fixed per sheet spec in code; row heights auto.

## 4. Checks (all must be evaluated; failures listed, workbook still generates with Cover flag, PPT/PDF blocked per doc 05 ERR-060)
TB balanced · BS balances (when full BS) · CF net = BS cash Δ · PL net income = BS retained-earnings movement (when mappable) · BvA Σvariance = PL variance total · Forecast sheet totals = forecast run totals · Exceptions count = findings query count · DrillData row count = committed GL count · Display-rounding (₹'000 variant): lines sum to subtotals (largest-remainder, doc 03).

## 5. Safety & fidelity
Formula-injection guard: any text cell starting with `= + - @` from imported data is prefixed `'` (DrillData especially). Descriptions truncated at 500 chars with marker. Golden-file tests assert cell values, formats, and formula presence for the golden period (doc 14); cosmetic-only changes require golden regeneration + changelog entry, never silent.
