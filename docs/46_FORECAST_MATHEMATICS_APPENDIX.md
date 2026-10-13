# 46 — FORECAST MATHEMATICS APPENDIX (exact math for doc 08)

Notation: history `y[1..n]` monthly Decimal; forecasts `ŷ`. All fitting on Decimal via normal equations / iterative updates in `forecast/*` (no float; where a method is classically float (grid search), compute in Decimal with 6dp internal scale).
- **Moving average(n):** ŷ = mean(y[n-k+1..n]). **Naive seasonal:** ŷ[t] = y[t−12] if exists else y[n].
- **Linear trend:** least squares on last ≤12 points, x=1..m: b = Σ(x−x̄)(y−ȳ)/Σ(x−x̄)², a = ȳ − b·x̄; ŷ = a + b·(m+h). CAGR variant (revenue only): (y[n]/y[n−11])^(1/11) − 1 over 12 points, requires all >0 else not_run.
- **Holt (linear):** l_t = α·y_t + (1−α)(l_{t−1}+b_{t−1}); b_t = β(l_t − l_{t−1}) + (1−β)b_{t−1}; ŷ = l_n + h·b_n. Init l_1=y_1, b_1=y_2−y_1.
- **Holt-Winters (additive, m=12):** l_t = α(y_t − s_{t−m}) + (1−α)(l_{t−1}+b_{t−1}); b as Holt; s_t = γ(y_t − l_{t−1} − b_{t−1}) + (1−γ)s_{t−m}; ŷ = l_n + h·b_n + s_{n+h−m}. Init: l = mean(first 12), b = (mean(next 6 if avail) − l)/6 else 0, s_i = y_i − l. Requires n ≥ 14 (else Holt). Grid search α,β,γ ∈ {0.1,…,0.9} minimising backtest MAPE (doc 08 §3 window) — deterministic tie-break smallest (α,β,γ) lexicographic.
- **Seasonal index:** index[p] = mean(y at period-of-year p)/overall mean (needs ≥24; with 12–23: falls back to naive-seasonal and says so), ŷ = index[p] × trend level (Holt level at horizon).
- **Metrics:** MAPE = mean(|A−F|/|A|) over A≠0 (report excluded count), Bias = Σ(F−A)/Σ|A|, Hit = share |err|≤5%.
- **Floors/negatives:** doc 08 §7 applied after method output, recorded per line.
**Numerical oracles (must match in tests):** HW example: y = [100,110]*6 (n=12, flat seasonal) → indices 0.952/1.048 (4dp), level 105 → next ŷ = 100.0 (period-1 index) — computed fixture in `tests/fixtures/forecast/hw_flat.json`. Holt on [100,110,105,115] α=.3 β=.1: l4, b4 recorded in fixture `holt_basic.json` (agents compute the fixture from these equations by hand/spreadsheet, then code must match — fixture-first per doc 14 §2).
