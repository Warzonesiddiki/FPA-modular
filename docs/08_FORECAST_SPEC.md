# 08 — FORECAST & SCENARIO SPECIFICATION

> Owner of: methods, backtesting, scenarios, rolling rhythm. All methods deterministic, Decimal, pure functions over monthly series (`app/forecast/*`). No ML libraries in v1; no AI-generated numbers (doc 11 may narrate, never forecast).

## 1. Concepts
Forecast operates per **account group** (Revenue, COGS, Personnel, Other Opex, Other) × entity. History = committed actuals (monthly). A **forecast run** covers the remaining periods of the FY plus optionally +12 months rolling. Runs are immutable once `locked`; corrections create a new run. The **rolling rhythm** (P11): on new period commit, actuals replace forecast for elapsed periods and a new draft run is generated; prior runs untouched (variance forecast-vs-actual history preserved for FVA).

## 2. Methods (each: formula, minimum history, fixture)
| Method | Logic | Min history |
|---|---|---|
| `naive` | Last actual (or same-period-last-year if seasonality flag) repeated | 1 |
| `moving_average` | Mean of last n (default 3) actuals, n configurable | n |
| `exponential_smoothing` | Holt-Winters (additive trend/seasonality, α .3 β .1 γ .2 defaults, grid-searched on backtest window) | 12 for seasonal, else Holt linear ≥4 |
| `linear_trend` | Least-squares on last ≤12 points; optional CAGR variant for revenue | 4 |
| `driver_based` | From driver_values: e.g. Revenue = volume × price; Personnel = headcount × avg cost; account mapping declares driver formula id | drivers present |
| `seasonal` | Seasonal index (period_of_year mean / overall mean, ≥2 years) × trend level | 24 (else not_run, reason shown) |
| `budget_phasing` | Remaining annual budget spread by phasing curve (prior-year monthly shares or manual curve) | budget present |
| `manual` | Analyst-entered/overridden values layered on a base run; every override stored with author+reason, base preserved | base run |

## 3. Backtest & method selection (engine.py)
For each group: backtest each eligible method on the last 3 actual periods (train on prior, predict, roll). Metrics: MAPE = mean(|A−F|/|A|) (A=0 periods excluded, counted), Bias = Σ(F−A)/Σ|A|, Hit-rate = % within ±5%. Recommended method = lowest MAPE (tie → simpler method order as listed). Analyst may override per group; choice + metrics stored in run.accuracy_json and shown on S09 — a forecast without displayed backtest accuracy must not ship.
**Oracle:** history [100,110,105,115], moving_average n=2 predicts next = (105+115)/2 = 110. Backtest on last point: train [100,110,105] → predict (110+105)/2=107.5 vs actual 115 → APE = 6.52%.

## 4. Scenarios (scenarios.py)
Scenario = named delta set on a locked base run: driver deltas (volume −10%), account-group % deltas, absolute overrides — applied in that order, each step Decimal-exact. Base/Upside/Downside seeded as templates. Compare view (S10/API): periods × scenarios with Δ vs base; export includes scenario assumptions page (inputs, not just outputs). Applying deltas never mutates base (test: base hash unchanged).

## 5. Phasing & annual budgets
Annual-only budget → monthly phasing: prior-year actual shares (default), flat (explicit analyst choice), or manual curve summing to 100.000% exactly (largest-remainder). Phased provenance is stamped on every derived line (`source=phased:<curve>`).

## 6. Forecast-vs-actual (FVA) reporting
Per locked run, per period as actuals land: error, |error|, bias contribution → S09/S01 widgets and Excel Forecast sheet. Systematic bias ≥ 5% over 3 periods → advisory badge "method consistently over/under-forecasts — consider switching" (a prompt to the human; the tool never auto-switches).

## 7. Guardrails
Forecasts floor at 0 for revenue/expense groups unless `allow_negative` set per account (credit-note accounts). Locked runs are inputs to BvA (doc 03) and PPT/Excel forecast sections; exports stamp run_id + lock date.
